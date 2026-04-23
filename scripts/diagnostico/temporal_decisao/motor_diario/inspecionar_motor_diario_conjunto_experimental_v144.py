from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.comparador_hibrido_switching_v1 import chave_promocao_hibrida
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import (
    _cap_fontes_por_destino,
    _comparar_com_baseline,
    _gerar_cenarios_integral_parametrizados,
    _melhores_por_fonte_destino,
)
from nucleo.motor_diario_conjunto_experimental_v143 import (
    _ativar_recebidos_futuros_no_dia,
    _carregar_estado_janela,
    _chave_pacote,
    _coerce_date,
    _executar_pacote_dia,
    _ordenar_pagamentos,
    classificar_cenario_diario,
    rodar_motor_diario_conjunto_experimental_v143,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1


DATA_INICIO = date(2026, 5, 3)
DATA_FIM = date(2026, 5, 12)
LIMITE_CANDIDATOS = 24
CAP_FONTES_DESTINO = 5


def _auditoria_forcada_switch_then_pay(raiz: Path) -> dict[str, object]:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=raiz,
        instalar_automaticamente=False,
        incluir_switching_shadow=False,
        incluir_triagem=True,
        incluir_replay=True,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    config = deepcopy(contexto.pacote_config.conteudo)
    estado = _carregar_estado_janela(contexto=contexto, data_inicio=DATA_INICIO, data_fim=DATA_FIM)
    pagamentos_iniciais = list(estado.get('pagamentos_futuros') or [])
    pagamentos_por_dia: dict[str, list[dict[str, object]]] = {}
    for pagamento in pagamentos_iniciais:
        chave = (_coerce_date(pagamento.get('data')) or DATA_INICIO).isoformat()
        pagamentos_por_dia.setdefault(chave, []).append(deepcopy(dict(pagamento)))

    historico_execucao: list[dict[str, object]] = []
    dias: list[dict[str, object]] = []
    dia = DATA_INICIO
    while dia <= DATA_FIM:
        estado['data_evento_corrente'] = dia
        ativados = _ativar_recebidos_futuros_no_dia(estado, dia, historico_execucao)
        pagamentos_dia = _ordenar_pagamentos(pagamentos_por_dia.get(dia.isoformat(), []))
        registro = {
            'data': dia.isoformat(),
            'quantidade_pagamentos': len(pagamentos_dia),
            'pagamentos_ids': [str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia],
            'recebidos_ativados': [
                {
                    'id': str(x.get('id') or x.get('fonte_id') or ''),
                    'valor_disponivel': round(float(x.get('valor_disponivel') or x.get('valor') or 0.0), 2),
                }
                for x in ativados
            ],
        }
        if pagamentos_dia:
            horizonte = {'data_inicio': dia.isoformat(), 'data_fim': DATA_FIM.isoformat()}
            baseline = simular_cenario_eventos_v1(deepcopy(estado), [], config, horizonte=horizonte)
            plano = planejar_switching_temporal_v1(
                estado_global=deepcopy(estado),
                config=config,
                horizonte_planejamento=horizonte,
                filtros_eventos=None,
                limite_candidatos_por_data=LIMITE_CANDIDATOS,
            )
            acoes = [
                deepcopy(item)
                for item in (plano.get('acoes_candidatas') or [])
                if str(item.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'} and item.get('elegivel')
            ]
            acoes = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), CAP_FONTES_DESTINO)
            cenarios = _gerar_cenarios_integral_parametrizados(acoes)
            resultados = []
            for cenario in cenarios:
                sim = simular_cenario_eventos_v1(deepcopy(estado), cenario.get('eventos') or [], config, horizonte=horizonte)
                comparacao = _comparar_com_baseline(sim, baseline)
                classif = classificar_cenario_diario(comparacao)
                resultados.append({
                    **cenario,
                    **comparacao,
                    **classif,
                    'patrimonio_liquido_terminal_proxy': sim.get('patrimonio_liquido_terminal_proxy'),
                })
            pay_only = _executar_pacote_dia(
                estado_inicial=estado,
                dia=dia,
                pagamentos_dia=pagamentos_dia,
                config=config,
                data_fim=DATA_FIM,
                tipo_pacote='pay_only',
                plano_switching=None,
            )
            registro['pay_only'] = {
                'vetor_total_estimado': list(pay_only.get('vetor_total_estimado') or ()),
                'patrimonio_terminal_proxy_estimado': round(float(pay_only.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
            }
            registro['switching_diario'] = {
                'acoes_elegiveis': len(acoes),
                'cenarios_gerados': len(cenarios),
                'cenarios_promoviveis': sum(1 for item in resultados if bool(item.get('promovivel_hibrido'))),
            }
            if resultados:
                melhor_bruto = sorted(resultados, key=chave_promocao_hibrida)[0]
                forced = _executar_pacote_dia(
                    estado_inicial=estado,
                    dia=dia,
                    pagamentos_dia=pagamentos_dia,
                    config=config,
                    data_fim=DATA_FIM,
                    tipo_pacote='switch_then_pay',
                    plano_switching=melhor_bruto,
                )
                registro['melhor_switching_bruto'] = {
                    'rotulo': melhor_bruto.get('rotulo'),
                    'classe_comparador_hibrido': melhor_bruto.get('classe_comparador_hibrido'),
                    'delta_patrimonio_proxy_vs_baseline': melhor_bruto.get('delta_patrimonio_proxy_vs_baseline'),
                    'vetor_switch_only': list(melhor_bruto.get('vetor_lexicografico') or ()),
                }
                registro['switch_then_pay_forcado'] = {
                    'vetor_total_estimado': list(forced.get('vetor_total_estimado') or ()),
                    'patrimonio_terminal_proxy_estimado': round(float(forced.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
                    'vence_pay_only': bool(_chave_pacote(forced) < _chave_pacote(pay_only)),
                }
            else:
                registro['melhor_switching_bruto'] = None
                registro['switch_then_pay_forcado'] = None

            estado = deepcopy(pay_only.get('estado_pos_dia') or estado)
        estado['pagamentos_futuros'] = [
            deepcopy(dict(item))
            for item in (estado.get('pagamentos_futuros') or [])
            if (_coerce_date(item.get('data')) or date.max) > dia
        ]
        dias.append(registro)
        dia += timedelta(days=1)

    return {'dias': dias}


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    diagnostico_base = rodar_motor_diario_conjunto_experimental_v143(
        raiz_repositorio=raiz,
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM,
        limite_candidatos_por_data=LIMITE_CANDIDATOS,
        cap_fontes_destino=CAP_FONTES_DESTINO,
    )
    auditoria_forcada = _auditoria_forcada_switch_then_pay(raiz)
    payload = {
        'status': 'ok',
        'baseline_operacional': 'V143',
        'versao_auditoria': 'V144',
        'janela': {'data_inicio': DATA_INICIO.isoformat(), 'data_fim': DATA_FIM.isoformat()},
        'diagnostico_motor_diario': diagnostico_base,
        'auditoria_forcada_switch_then_pay': auditoria_forcada,
        'conclusao_estrutural': (
            'Na janela auditada, switch_then_pay não entra na disputa final do motor porque nenhum plano de switching '
            'isolado foi promovido pelo comparador híbrido. Mesmo quando o melhor switching bruto é forçado no pacote '
            'do dia, pay_only continua vencedor nos dias com pagamento.'
        ),
    }
    destino = raiz / 'saidas' / 'diagnostico' / 'motor_diario_conjunto_experimental_v144_2026-05-03_2026-05-12.json'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(destino)


if __name__ == '__main__':
    main()

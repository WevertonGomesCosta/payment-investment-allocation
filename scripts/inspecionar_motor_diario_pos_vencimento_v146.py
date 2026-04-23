from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.comparador_hibrido_switching_v1 import chave_promocao_hibrida, classificar_cenario_diario
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
    _normalizar_lote_pos_vencimento_no_dia,
    _ordenar_pagamentos,
    rodar_motor_diario_conjunto_experimental_v143,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1

DATA_INICIO = date(2026, 5, 3)
DATA_FIM = date(2026, 5, 6)
LIMITE_CANDIDATOS = 24
CAP_FONTES_DESTINO = 5


def executar_auditoria() -> dict[str, object]:
    resultado_motor = rodar_motor_diario_conjunto_experimental_v143(
        raiz_repositorio=RAIZ,
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM,
        limite_candidatos_por_data=LIMITE_CANDIDATOS,
        cap_fontes_destino=CAP_FONTES_DESTINO,
    )

    contexto = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
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
        pagamentos_por_dia.setdefault((_coerce_date(pagamento.get('data')) or DATA_INICIO).isoformat(), []).append(deepcopy(dict(pagamento)))

    dias: list[dict[str, object]] = []
    historico: list[dict[str, object]] = []
    dia = DATA_INICIO
    while dia <= DATA_FIM:
        estado['data_evento_corrente'] = dia
        convertidos = _normalizar_lote_pos_vencimento_no_dia(estado, dia, config, historico)
        ativados = _ativar_recebidos_futuros_no_dia(estado, dia, historico)
        pagamentos_dia = _ordenar_pagamentos(pagamentos_por_dia.get(dia.isoformat(), []))
        registro = {
            'data': dia.isoformat(),
            'pagamentos_ids': [str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia],
            'lotes_normalizados_pos_vencimento': [
                {
                    'id': str(x.get('id') or ''),
                    'produto_origem': str(x.get('produto_origem') or ''),
                    'valor_disponivel': round(float(x.get('valor_disponivel') or x.get('valor') or 0.0), 2),
                }
                for x in convertidos
            ],
            'recebidos_ativados': [
                {
                    'id': str(x.get('id') or ''),
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
                'fontes': [str(x.get('fonte_principal_tipo') or '') for x in (pay_only.get('resultados_pagamento') or [])],
            }
            registro['switching_diario'] = {
                'acoes_elegiveis': len(acoes),
                'cenarios_gerados': len(cenarios),
                'cenarios_promoviveis': sum(1 for x in resultados if bool(x.get('promovivel_hibrido'))),
            }
            if resultados:
                melhor = sorted(resultados, key=chave_promocao_hibrida)[0]
                forced = _executar_pacote_dia(
                    estado_inicial=estado,
                    dia=dia,
                    pagamentos_dia=pagamentos_dia,
                    config=config,
                    data_fim=DATA_FIM,
                    tipo_pacote='switch_then_pay',
                    plano_switching=melhor,
                )
                registro['melhor_switching_bruto'] = {
                    'rotulo': melhor.get('rotulo'),
                    'classe_comparador_hibrido': melhor.get('classe_comparador_hibrido'),
                    'patrimonio_liquido_terminal_proxy': round(float(melhor.get('patrimonio_liquido_terminal_proxy') or 0.0), 2),
                }
                registro['switch_then_pay_forcado'] = {
                    'vetor_total_estimado': list(forced.get('vetor_total_estimado') or ()),
                    'patrimonio_terminal_proxy_estimado': round(float(forced.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
                    'vence_pay_only': _chave_pacote(forced) < _chave_pacote(pay_only),
                }
        dias.append(registro)
        dia += timedelta(days=1)

    return {
        'status': 'ok',
        'versao': 'V146',
        'janela': {'data_inicio': DATA_INICIO.isoformat(), 'data_fim': DATA_FIM.isoformat()},
        'resultado_motor': resultado_motor,
        'auditoria_forcada': {'dias': dias, 'historico_execucao': historico},
    }


def main() -> int:
    consolidado = executar_auditoria()
    saida_json = RAIZ / 'saidas' / 'motor_diario_conjunto_pos_vencimento_v146_2026-05-03_2026-05-06.json'
    saida_md = RAIZ / 'relatorios' / 'atuais' / 'MOTOR_DIARIO_CONJUNTO_POS_VENCIMENTO_V146_2026-05-03_2026-05-06.md'
    saida_json.write_text(json.dumps(consolidado, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    resumo = consolidado['resultado_motor']['resumo']
    linhas = [
        '# Auditoria do motor diário com normalização pós-vencimento — V146',
        '',
        f"Janela: **{DATA_INICIO.isoformat()}** a **{DATA_FIM.isoformat()}**.",
        '',
        '## Resumo do motor corrigido',
        '',
        f"- decisões `pay_only`: **{resumo.get('decisoes_pay_only', 0)}**",
        f"- decisões `switch_then_pay`: **{resumo.get('decisoes_switch_then_pay', 0)}**",
        f"- decisões `switch_only`: **{resumo.get('decisoes_switch_only', 0)}**",
        f"- decisões `no_action`: **{resumo.get('decisoes_no_action', 0)}**",
        f"- patrimônio líquido terminal proxy final: **R$ {float(resumo.get('patrimonio_liquido_terminal_proxy_final') or 0.0):.2f}**",
        '',
        '## Auditoria forçada `pay_only` vs `switch_then_pay`',
        '',
    ]
    for dia in consolidado['auditoria_forcada']['dias']:
        linhas.append(f"### {dia['data']}")
        if dia['lotes_normalizados_pos_vencimento']:
            linhas.append('- lotes normalizados no dia:')
            for item in dia['lotes_normalizados_pos_vencimento']:
                linhas.append(f"  - {item['id']} | {item['produto_origem']} | R$ {float(item['valor_disponivel']):.2f}")
        if dia['recebidos_ativados']:
            linhas.append('- recebidos ativados no dia:')
            for item in dia['recebidos_ativados']:
                linhas.append(f"  - {item['id']} | R$ {float(item['valor_disponivel']):.2f}")
        linhas.append(f"- pagamentos do dia: **{len(dia['pagamentos_ids'])}**")
        if 'pay_only' in dia:
            linhas.append(f"- `pay_only`: vetor {tuple(dia['pay_only']['vetor_total_estimado'])} | patrimônio proxy R$ {float(dia['pay_only']['patrimonio_terminal_proxy_estimado']):.2f}")
            linhas.append(f"- fontes `pay_only`: {dia['pay_only']['fontes']}")
            linhas.append(f"- switching diário: {dia['switching_diario']['acoes_elegiveis']} ações elegíveis, {dia['switching_diario']['cenarios_gerados']} cenários, {dia['switching_diario']['cenarios_promoviveis']} promovíveis")
        if 'melhor_switching_bruto' in dia:
            linhas.append(f"- melhor switching bruto: {dia['melhor_switching_bruto']['rotulo']} | classe {dia['melhor_switching_bruto']['classe_comparador_hibrido']}")
            linhas.append(f"- `switch_then_pay` forçado vence `pay_only`? **{dia['switch_then_pay_forcado']['vence_pay_only']}**")
            linhas.append(f"- `switch_then_pay` forçado: vetor {tuple(dia['switch_then_pay_forcado']['vetor_total_estimado'])} | patrimônio proxy R$ {float(dia['switch_then_pay_forcado']['patrimonio_terminal_proxy_estimado']):.2f}")
        linhas.append('')
    saida_md.write_text('\n'.join(linhas), encoding='utf-8')
    print(saida_json)
    print(saida_md)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

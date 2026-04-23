
from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

from collections import defaultdict
from copy import deepcopy
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path
import json
import os

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.benchmark_runner_futuro_shadow import _pagamentos_futuros
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _ativar_recebidos_futuros_no_dia,
    _consumir_componentes,
    _coerce_date,
    construir_estado_global_recorte_curto_v117,
    simular_cenario_eventos_v1,
)

BASE_OPERACIONAL = Path(RAIZ) / 'saidas' / 'operacional'
BASE_OPERACIONAL.mkdir(parents=True, exist_ok=True)

def _parse_date_env(var: str, default: str) -> date:
    valor = os.getenv(var, default) or default
    return date.fromisoformat(valor)

JANELA_INICIO = _parse_date_env('V136_JANELA_INICIO', '2026-05-21')
JANELA_FIM = _parse_date_env('V136_JANELA_FIM', '2027-03-31')
START_OFFSET = int(os.getenv('V136_START_OFFSET', '0') or 0)
MAX_DIAS = int(os.getenv('V136_MAX_DIAS', '0') or 0)
CHUNK_JSON = BASE_OPERACIONAL / f'grade_diaria_hibrida_v136_{JANELA_INICIO.isoformat()}_{JANELA_FIM.isoformat()}_offset_{START_OFFSET:03d}.json'


MAX_FONTES_POR_DESTINO = int(os.getenv('V136_MAX_FONTES_POR_DESTINO', '6') or 6)


def _cap_fontes_por_destino(acoes, max_fontes: int):
    if max_fontes <= 0:
        return list(acoes)
    por_destino = defaultdict(list)
    for acao in acoes:
        destino = str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')
        por_destino[destino].append(deepcopy(acao))
    saida = []
    for _, grupo in por_destino.items():
        grupo = sorted(grupo, key=lambda a: float(a.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)
        saida.extend(grupo[:max_fontes])
    return saida


def _carregar_estado_completo(contexto):
    pagamentos = _pagamentos_futuros(contexto.dados_operacionais, data_referencia=contexto.execucao.data_referencia)
    data_fim = max(pagamentos['data']) if len(pagamentos) else contexto.execucao.data_referencia
    estado = construir_estado_global_recorte_curto_v117(
        contexto,
        data_inicio=contexto.execucao.data_referencia,
        data_fim=data_fim,
        limite_pagamentos=max(len(pagamentos), 1),
    )
    return estado, data_fim, len(pagamentos)


def _gerar_snapshots_baseline(estado_inicial, config):
    estado = deepcopy(estado_inicial)
    pagamentos = sorted(
        [deepcopy(dict(item)) for item in estado.get('pagamentos_futuros', [])],
        key=lambda item: (
            _coerce_date(item.get('data')),
            int(item.get('prioridade_classe') or 99),
            int(item.get('prioridade_intraclasse') or 99),
            str(item.get('pagamento_id') or item.get('despesa_id') or ''),
        ),
    )
    inicio = _coerce_date(estado.get('data_referencia'))
    fim = _coerce_date(estado.get('data_fim_recorte'))
    pagamentos_por_data = defaultdict(list)
    for pagamento in pagamentos:
        pagamentos_por_data[_coerce_date(pagamento.get('data'))].append(pagamento)
    snapshots = {}
    dia = inicio
    while dia <= fim:
        estado['data_evento_corrente'] = dia
        _ativar_recebidos_futuros_no_dia(estado, dia)
        snapshots[dia.isoformat()] = deepcopy(estado)
        for pagamento in pagamentos_por_data.get(dia, []):
            estado_para_pagamento = deepcopy(estado)
            estado_para_pagamento['dias_horizonte_terminal'] = max((fim - dia).days, 0)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_pagamento,
                config=config,
                plano_switching_candidato=None,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            _consumir_componentes(estado, alocacao.get('componentes_escolhidos') or [])
        dia += timedelta(days=1)
    return snapshots


def _ticket_ok(valor_total: float, acao: dict, *, individual: bool) -> tuple[bool, str]:
    minimo = float(acao.get('aplicacao_minima_destino') or 0.0)
    maximo = float(acao.get('aplicacao_maxima_destino') or 0.0)
    somente_combo = bool(acao.get('somente_combo_destino') or False)
    if individual:
        if not bool(acao.get('atende_ticket_individual', True)):
            return False, str(acao.get('motivo_bloqueio_ticket_individual') or '')
        if somente_combo:
            return False, 'somente_combo'
    else:
        if minimo > 0.0 and valor_total + 1e-9 < minimo:
            return False, 'abaixo_da_aplicacao_minima_agrupada'
        if maximo > 0.0 and valor_total - 1e-9 > maximo:
            return False, 'acima_da_aplicacao_maxima_agrupada'
    return True, ''


def _melhores_por_fonte_destino(acoes):
    melhores = {}
    for acao in acoes:
        if str(acao.get('tipo_acao') or '') not in {'switching_simples', 'aporte_nao_aportado'}:
            continue
        if not acao.get('elegivel'):
            continue
        fonte = str(acao.get('lote_origem_id') or '')
        destino = str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')
        if not fonte or not destino:
            continue
        chave = (fonte, destino)
        atual = melhores.get(chave)
        score = float(acao.get('ganho_terminal_economico_minimo_estimado') or 0.0)
        if atual is None or score > float(atual.get('ganho_terminal_economico_minimo_estimado') or 0.0):
            melhores[chave] = deepcopy(acao)
    return list(melhores.values())


def _gerar_cenarios_parametrizados(acoes):
    cenarios = []
    for acao in acoes:
        valor_total = round(float(acao.get('valor_migrado_estimado') or acao.get('valor_liquido_resgatavel') or 0.0), 2)
        ok, motivo = _ticket_ok(valor_total, acao, individual=True)
        if not ok:
            continue
        evento = deepcopy(acao)
        evento['fracao_lote'] = 1.0
        cenarios.append({
            'familia': 'individual_integral_parametrizado',
            'rotulo': f"{acao.get('lote_origem_id')} -> {acao.get('produto_destino')}",
            'produto_destino': acao.get('produto_destino'),
            'valor_total_alocado': valor_total,
            'validacao_ticket': {'ok': True, 'motivo': motivo},
            'eventos': [evento],
        })

    por_destino = defaultdict(list)
    for acao in acoes:
        por_destino[str(acao.get('produto_destino_key') or acao.get('produto_destino') or '')].append(deepcopy(acao))
    for _, grupo in por_destino.items():
        grupo = sorted(grupo, key=lambda a: float(a.get('ganho_terminal_economico_minimo_estimado') or 0.0), reverse=True)
        if len(grupo) < 2:
            continue
        for tamanho in range(2, len(grupo) + 1):
            for combo in combinations(grupo, tamanho):
                fontes = [str(acao.get('lote_origem_id') or '') for acao in combo]
                if len(set(fontes)) < len(fontes):
                    continue
                valor_total = round(sum(float(acao.get('valor_migrado_estimado') or acao.get('valor_liquido_resgatavel') or 0.0) for acao in combo), 2)
                ok, motivo = _ticket_ok(valor_total, combo[0], individual=False)
                if not ok:
                    continue
                eventos = []
                for acao in combo:
                    evento = deepcopy(acao)
                    evento['fracao_lote'] = 1.0
                    eventos.append(evento)
                cenarios.append({
                    'familia': 'agrupado_integral_parametrizado',
                    'rotulo': f"{' + '.join(fontes)} -> {combo[0].get('produto_destino')}",
                    'produto_destino': combo[0].get('produto_destino'),
                    'valor_total_alocado': valor_total,
                    'validacao_ticket': {'ok': True, 'motivo': motivo},
                    'eventos': eventos,
                })
    return cenarios


def _comparar_com_baseline(sim: dict, baseline: dict) -> dict:
    metrica = sim.get('metrica_central') or {}
    base = baseline.get('metrica_central') or {}
    vetor = vetor_lexicografico_central(metrica)
    vetor_base = vetor_lexicografico_central(base)
    delta_perda = round(float(metrica.get('perda_patrimonio_liquido_terminal') or 0.0) - float(base.get('perda_patrimonio_liquido_terminal') or 0.0), 2)
    delta_deficit = round(float(metrica.get('deficit_liquido_total') or 0.0) - float(base.get('deficit_liquido_total') or 0.0), 2)
    delta_protegida = round(float(metrica.get('violacoes_protegida') or 0.0) - float(base.get('violacoes_protegida') or 0.0), 2)
    delta_pat = round(float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0) - float(baseline.get('patrimonio_liquido_terminal_proxy') or 0.0), 2)
    vencedor = vetor < vetor_base
    material = vencedor and (abs(delta_perda) >= 1.0 or abs(delta_deficit) >= 1.0 or abs(delta_protegida) >= 1.0 or abs(delta_pat) >= 1.0)
    return {
        'vetor_lexicografico': vetor,
        'vetor_baseline': vetor_base,
        'continua_vencedor_central': vencedor,
        'vitoria_material': material,
        'delta_perda_terminal_vs_baseline': delta_perda,
        'delta_deficit_vs_baseline': delta_deficit,
        'delta_violacoes_protegida_vs_baseline': delta_protegida,
        'delta_patrimonio_proxy_vs_baseline': delta_pat,
    }


def executar() -> dict:
    contexto = carregar_contexto_baseline(
        raiz_repositorio=Path(RAIZ),
        instalar_automaticamente=False,
        incluir_switching_shadow=False,
        incluir_triagem=True,
        incluir_switching_economico_shadow=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    config = contexto.pacote_config.conteudo
    estado_base, data_fim, qtd_pagamentos = _carregar_estado_completo(contexto)
    horizonte = {'data_inicio': contexto.execucao.data_referencia.isoformat(), 'data_fim': data_fim.isoformat()}
    snapshots = _gerar_snapshots_baseline(estado_base, config)

    resultados = []
    dias_auditados = []
    dia = JANELA_INICIO + timedelta(days=max(START_OFFSET, 0))
    limite_data = JANELA_FIM if MAX_DIAS <= 0 else min(JANELA_FIM, dia + timedelta(days=MAX_DIAS - 1))
    while dia <= limite_data:
        estado_dia = deepcopy(snapshots[dia.isoformat()])
        estado_dia['data_evento_corrente'] = dia
        baseline_dia = simular_cenario_eventos_v1(estado_inicial=estado_dia, eventos_candidatos=[], config=config, horizonte=horizonte)
        plano = planejar_switching_temporal_v1(
            estado_global=estado_dia,
            config=config,
            horizonte_planejamento=horizonte,
            filtros_eventos=None,
            limite_candidatos_por_data=500,
        )
        acoes = _melhores_por_fonte_destino(plano.get('acoes_candidatas', []))
        acoes = _cap_fontes_por_destino(acoes, MAX_FONTES_POR_DESTINO)
        cenarios = _gerar_cenarios_parametrizados(acoes)
        dias_auditados.append({
            'data': dia.isoformat(),
            'quantidade_acoes_elegiveis_planejador': len(acoes),
            'quantidade_cenarios_parametrizados': len(cenarios),
        })
        for cenario in cenarios:
            sim = simular_cenario_eventos_v1(
                estado_inicial=estado_dia,
                eventos_candidatos=cenario['eventos'],
                config=config,
                horizonte=horizonte,
            )
            comp = _comparar_com_baseline(sim, baseline_dia)
            registro = {
                'data_solicitada': dia.isoformat(),
                'familia': cenario['familia'],
                'rotulo': cenario['rotulo'],
                'produto_destino': cenario['produto_destino'],
                'valor_total_alocado': cenario['valor_total_alocado'],
                'validacao_ticket': cenario['validacao_ticket'],
                'eventos': [
                    {
                        'lote_origem_id': e.get('lote_origem_id'),
                        'produto_destino': e.get('produto_destino'),
                        'rank_destino_sugerido': e.get('rank_destino_sugerido'),
                        'valor_migrado_estimado': e.get('valor_migrado_estimado'),
                        'aplicacao_minima_destino': e.get('aplicacao_minima_destino'),
                        'aplicacao_maxima_destino': e.get('aplicacao_maxima_destino'),
                        'somente_combo_destino': bool(e.get('somente_combo_destino') or False),
                    }
                    for e in cenario['eventos']
                ],
                'patrimonio_liquido_terminal_proxy': float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0),
                **comp,
            }
            registro.update(classificar_cenario_diario(registro))
            resultados.append(registro)
        dia += timedelta(days=1)

    payload = {
        'janela_inicio': JANELA_INICIO.isoformat(),
        'janela_fim': JANELA_FIM.isoformat(),
        'start_offset': START_OFFSET,
        'max_dias': MAX_DIAS,
        'max_fontes_por_destino': MAX_FONTES_POR_DESTINO,
        'quantidade_pagamentos_horizonte_total': qtd_pagamentos,
        'dias_auditados': dias_auditados,
        'resultados': resultados,
    }
    CHUNK_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(CHUNK_JSON))
    return payload


def main() -> int:
    if JANELA_FIM < JANELA_INICIO:
        raise ValueError('JANELA_FIM deve ser maior ou igual a JANELA_INICIO.')
    executar()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

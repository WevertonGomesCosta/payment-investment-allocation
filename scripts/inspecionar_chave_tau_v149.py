from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.avaliador_cenarios_conjuntos_v1 import ORDEM_METRICA_CANONICA
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
    _chave_pacote_tau,
    _coerce_date,
    _executar_pacote_dia,
    _normalizar_lote_pos_vencimento_no_dia,
    _ordenar_pagamentos,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, chave_promocao_hibrida

DATA_INICIO = date(2026, 4, 22)
DATA_ALVO = date(2026, 5, 4)
DATA_FIM = date(2026, 5, 12)
LIMITE_CANDIDATOS = 60
CAP_FONTES_DESTINO = 8
LOTES_3K = {"Lote 3000 mar. V", "Lote 3000 mar. B"}
TAUS = (9.5, 10.0)


def _fmt_br(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _cenario_key(cenario: dict[str, Any]) -> tuple[Any, ...]:
    eventos = cenario.get('eventos') or []
    fontes = tuple(sorted(str(e.get('lote_origem_id') or e.get('fonte_origem_id') or '') for e in eventos))
    destinos = tuple(sorted(str(e.get('produto_destino_key') or e.get('produto_destino') or '') for e in eventos))
    return (fontes, destinos, len(eventos), str(cenario.get('familia') or ''))


def _vetor_dict(vetor: list[float] | tuple[float, ...] | None) -> dict[str, float]:
    dados = list(vetor or [])
    return {
        chave: round(float(dados[idx] if idx < len(dados) else 0.0), 6)
        for idx, chave in enumerate(ORDEM_METRICA_CANONICA)
    }


def _fontes_3k_only(cenario: dict[str, Any]) -> bool:
    fontes = [str(e.get('lote_origem_id') or '') for e in (cenario.get('eventos') or [])]
    return bool(fontes) and all(f in LOTES_3K for f in fontes)


def _is_case_7000_mp(item: dict[str, Any]) -> bool:
    fontes = set(item.get('fontes_switch') or [])
    destinos = [str(x).lower() for x in (item.get('destinos_switch') or [])]
    return fontes == {'Lote 7000 mai.'} and any('mercado pago cofrinho 120% cdi meli+' in d for d in destinos)


def _is_case_3k_only(item: dict[str, Any]) -> bool:
    fontes = set(item.get('fontes_switch') or [])
    return bool(fontes) and fontes.issubset(LOTES_3K)


def _gerar_cenarios_sem_gate(*, estado: dict[str, Any], config: dict[str, Any], dia: date, data_fim: date) -> dict[str, Any]:
    horizonte = {'data_inicio': dia.isoformat(), 'data_fim': data_fim.isoformat()}
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
    acoes_cap = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), CAP_FONTES_DESTINO)
    cenarios = _gerar_cenarios_integral_parametrizados(acoes_cap)
    resultados: list[dict[str, Any]] = []
    for cenario in cenarios:
        sim = simular_cenario_eventos_v1(deepcopy(estado), cenario.get('eventos') or [], config, horizonte=horizonte)
        comparacao = _comparar_com_baseline(sim, baseline)
        classif = classificar_cenario_diario(comparacao)
        item = {
            **deepcopy(cenario),
            **comparacao,
            **classif,
            'patrimonio_liquido_terminal_proxy': round(float(sim.get('patrimonio_liquido_terminal_proxy') or 0.0), 2),
        }
        item['_fontes'] = [str(e.get('lote_origem_id') or '') for e in (cenario.get('eventos') or [])]
        item['_destinos'] = [str(e.get('produto_destino_key') or e.get('produto_destino') or '') for e in (cenario.get('eventos') or [])]
        resultados.append(item)
    dedup: dict[tuple[Any, ...], dict[str, Any]] = {}
    for item in resultados:
        dedup[_cenario_key(item)] = item
    resultados = list(dedup.values())
    cenarios_3k = [x for x in resultados if _fontes_3k_only(x)]
    return {
        'acoes_elegiveis': acoes,
        'acoes_cap': acoes_cap,
        'cenarios': resultados,
        'best_hibrido': min(resultados, key=chave_promocao_hibrida) if resultados else None,
        'best_3k_only': min(cenarios_3k, key=chave_promocao_hibrida) if cenarios_3k else None,
        'baseline_terminal': round(float(baseline.get('patrimonio_liquido_terminal_proxy') or 0.0), 2),
    }


def _resumo_pacote(*, estado: dict[str, Any], dia: date, data_fim: date, config: dict[str, Any], pagamentos: list[dict[str, Any]], tipo: str, plano: dict[str, Any] | None) -> dict[str, Any]:
    pacote = _executar_pacote_dia(
        estado_inicial=estado,
        dia=dia,
        pagamentos_dia=pagamentos,
        config=config,
        data_fim=data_fim,
        tipo_pacote=tipo,
        plano_switching=plano,
    )
    vetor = [round(float(x), 6) for x in (pacote.get('vetor_total_estimado') or [])]
    patrimonio = round(float(pacote.get('patrimonio_terminal_proxy_estimado') or 0.0), 2)
    vetor_dict = _vetor_dict(vetor)
    return {
        'tipo_pacote': tipo,
        'rotulo_switching': str((plano or {}).get('rotulo') or ''),
        'classe_switching': str((plano or {}).get('classe_comparador_hibrido') or ''),
        'fontes_switch': [str(e.get('lote_origem_id') or '') for e in ((plano or {}).get('eventos') or [])],
        'destinos_switch': [str(e.get('produto_destino_key') or e.get('produto_destino') or '') for e in ((plano or {}).get('eventos') or [])],
        'vetor_total_estimado': vetor,
        'vetor_total_estimado_dict': vetor_dict,
        'patrimonio_terminal_proxy_estimado': patrimonio,
        'custo_operacional': round(float(vetor_dict.get('custo_operacional') or 0.0), 6),
        'switching_executado': bool(pacote.get('switching_executado')),
    }


def _delta_vs_base(item: dict[str, Any], base: dict[str, Any]) -> dict[str, float]:
    delta_pat = float(item['patrimonio_terminal_proxy_estimado']) - float(base['patrimonio_terminal_proxy_estimado'])
    delta_custo = float(item['custo_operacional']) - float(base['custo_operacional'])
    ganho_por_operacao = 0.0
    if delta_custo > 0:
        ganho_por_operacao = delta_pat / delta_custo
    return {
        'delta_patrimonio_terminal_proxy': round(delta_pat, 2),
        'delta_custo_operacional': round(delta_custo, 6),
        'ganho_por_operacao_extra': round(ganho_por_operacao, 6),
    }


def executar() -> dict[str, Any]:
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
    pagamentos_mapa: dict[str, list[dict[str, Any]]] = {}
    for pagamento in list(estado.get('pagamentos_futuros') or []):
        pagamentos_mapa.setdefault((_coerce_date(pagamento.get('data')) or DATA_INICIO).isoformat(), []).append(deepcopy(dict(pagamento)))

    historico: list[dict[str, Any]] = []
    dia = DATA_INICIO
    while dia < DATA_ALVO:
        estado['data_evento_corrente'] = dia
        _normalizar_lote_pos_vencimento_no_dia(estado, dia, config, historico)
        _ativar_recebidos_futuros_no_dia(estado, dia, historico)
        pagamentos_dia = _ordenar_pagamentos(pagamentos_mapa.get(dia.isoformat(), []))
        if pagamentos_dia:
            pacote = _executar_pacote_dia(
                estado_inicial=estado,
                dia=dia,
                pagamentos_dia=pagamentos_dia,
                config=config,
                data_fim=DATA_FIM,
                tipo_pacote='pay_only',
                plano_switching=None,
            )
            estado = deepcopy(pacote.get('estado_pos_dia') or estado)
        dia += timedelta(days=1)

    estado['data_evento_corrente'] = DATA_ALVO
    lotes_normalizados = _normalizar_lote_pos_vencimento_no_dia(estado, DATA_ALVO, config, historico)
    _ativar_recebidos_futuros_no_dia(estado, DATA_ALVO, historico)
    pagamentos_dia = _ordenar_pagamentos(pagamentos_mapa.get(DATA_ALVO.isoformat(), []))

    base = _resumo_pacote(estado=estado, dia=DATA_ALVO, data_fim=DATA_FIM, config=config, pagamentos=pagamentos_dia, tipo='pay_only', plano=None)
    cenarios = _gerar_cenarios_sem_gate(estado=estado, config=config, dia=DATA_ALVO, data_fim=DATA_FIM)

    pacotes = [base]
    for cenario in cenarios['cenarios']:
        plano = {**deepcopy(cenario), 'classe_comparador_hibrido': 'auditoria_tau_sem_gate', 'promovivel_hibrido': True}
        pacote = _resumo_pacote(estado=estado, dia=DATA_ALVO, data_fim=DATA_FIM, config=config, pagamentos=pagamentos_dia, tipo='switch_then_pay', plano=plano)
        pacote['delta_vs_base'] = _delta_vs_base(pacote, base)
        pacote['usa_3k_only'] = _is_case_3k_only(pacote)
        pacote['usa_7000_mp'] = _is_case_7000_mp(pacote)
        pacotes.append(pacote)

    vencedor_atual = min(pacotes, key=_chave_pacote)
    resultados_tau: dict[str, Any] = {}
    for tau in TAUS:
        vencedor = min(pacotes, key=lambda item: _chave_pacote_tau(item, tau))
        promovidos = [item for item in pacotes if item is not base and _chave_pacote_tau(item, tau) < _chave_pacote_tau(base, tau)]
        promovidos_ordenados = sorted(promovidos, key=lambda item: _chave_pacote_tau(item, tau))
        resultados_tau[str(tau).replace('.', '_')] = {
            'tau': tau,
            'vencedor': vencedor,
            'quantidade_promovidos_vs_base': len(promovidos_ordenados),
            'top5_promovidos_vs_base': promovidos_ordenados[:5],
            'melhor_3k_only': next((item for item in promovidos_ordenados if item.get('usa_3k_only')), None),
            'melhor_7000_mp': next((item for item in promovidos_ordenados if item.get('usa_7000_mp')), None),
        }

    payload = {
        'status': 'ok',
        'baseline': 'V148',
        'versao_experimental': 'V149',
        'descricao_regra_tau': 'Mantém os 7 primeiros critérios canônicos intactos e, no empate, compara patrimônio_terminal_proxy - tau * custo_operacional.',
        'data_alvo': DATA_ALVO.isoformat(),
        'data_fim': DATA_FIM.isoformat(),
        'taus_testados': list(TAUS),
        'lotes_normalizados_no_dia': [{'id': str(x.get('id') or ''), 'valor_disponivel': round(float(x.get('valor_disponivel') or x.get('valor') or 0.0), 2)} for x in lotes_normalizados],
        'resumo_cenarios': {'acoes_elegiveis_total': len(cenarios['acoes_elegiveis']), 'cenarios_total': len(cenarios['cenarios']), 'base': base, 'vencedor_regra_atual': vencedor_atual},
        'resultado_tau': resultados_tau,
    }
    return payload

if __name__ == '__main__':
    resultado = executar()
    saida_json = RAIZ / 'saidas' / 'auditoria_chave_tau_v149_2026-05-04.json'
    saida_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    base = resultado['resumo_cenarios']['base']
    atual = resultado['resumo_cenarios']['vencedor_regra_atual']
    linhas = [
        '# Auditoria da chave experimental com tau em 2026-05-04',
        '',
        'Baseline: V148',
        'Versão experimental: V149',
        '',
        '## Contrato experimental',
        resultado['descricao_regra_tau'],
        '',
        '## Base',
        f"- Patrimônio terminal proxy do `pay_only`: **{_fmt_br(base['patrimonio_terminal_proxy_estimado'])}**",
        f"- Custo operacional do `pay_only`: **{base['custo_operacional']}**",
        '',
        '## Regra atual',
        f"- Vencedor: **{atual['tipo_pacote']}** | rotulo `{atual['rotulo_switching']}` | fontes {', '.join(atual['fontes_switch']) or '—'} | patrimônio **{_fmt_br(atual['patrimonio_terminal_proxy_estimado'])}** | custo operacional **{atual['custo_operacional']}**",
        '',
    ]
    for bloco in resultado['resultado_tau'].values():
        tau = bloco['tau']
        vencedor = bloco['vencedor']
        linhas.extend([
            f"## Tau = {str(tau).replace('.', ',')}",
            f"- Vencedor: **{vencedor['tipo_pacote']}** | rotulo `{vencedor['rotulo_switching']}` | fontes {', '.join(vencedor['fontes_switch']) or '—'} | patrimônio **{_fmt_br(vencedor['patrimonio_terminal_proxy_estimado'])}** | custo operacional **{vencedor['custo_operacional']}**",
            f"- Quantidade de switching promovidos vs base: **{bloco['quantidade_promovidos_vs_base']}**",
        ])
        melhor_3k = bloco['melhor_3k_only']
        if melhor_3k is not None:
            linhas.append(f"- Melhor 3k-only promovido: `{melhor_3k['rotulo_switching']}` | fontes {', '.join(melhor_3k['fontes_switch'])} | delta patrimônio **{_fmt_br(melhor_3k['delta_vs_base']['delta_patrimonio_terminal_proxy'])}** | delta custo operacional **{melhor_3k['delta_vs_base']['delta_custo_operacional']}** | ganho/op **{melhor_3k['delta_vs_base']['ganho_por_operacao_extra']:.6f}**")
        else:
            linhas.append('- Melhor 3k-only promovido: nenhum')
        melhor_7000 = bloco['melhor_7000_mp']
        if melhor_7000 is not None:
            linhas.append(f"- Caso `Lote 7000 mai. -> MP 120%` promovido: sim | delta patrimônio **{_fmt_br(melhor_7000['delta_vs_base']['delta_patrimonio_terminal_proxy'])}** | delta custo operacional **{melhor_7000['delta_vs_base']['delta_custo_operacional']}** | ganho/op **{melhor_7000['delta_vs_base']['ganho_por_operacao_extra']:.6f}**")
        else:
            linhas.append('- Caso `Lote 7000 mai. -> MP 120%` promovido: não')
        linhas.append('')
    saida_md = RAIZ / 'relatorios' / 'AUDITORIA_CHAVE_TAU_V149_2026-05-04.md'
    saida_md.write_text('\n'.join(linhas), encoding='utf-8')
    print(str(saida_json))
    print(str(saida_md))

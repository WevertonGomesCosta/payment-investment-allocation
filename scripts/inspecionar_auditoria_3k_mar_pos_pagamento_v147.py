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

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.motor_diario_conjunto_experimental_v143 import (
    _ativar_recebidos_futuros_no_dia,
    _carregar_estado_janela,
    _chave_pacote,
    _coerce_date,
    _executar_pacote_dia,
    _normalizar_lote_pos_vencimento_no_dia,
    _ordenar_pagamentos,
)
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import (
    _cap_fontes_por_destino,
    _comparar_com_baseline,
    _gerar_cenarios_integral_parametrizados,
    _melhores_por_fonte_destino,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import simular_cenario_eventos_v1
from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, chave_promocao_hibrida
from nucleo.avaliador_cenarios_conjuntos_v1 import ORDEM_METRICA_CANONICA

DATA_ATUAL = date(2026, 4, 22)
DATA_NU = date(2026, 5, 4)
DATA_FIM = date(2026, 5, 12)
LIMITE_CANDIDATOS = 60
CAP_FONTES_DESTINO = 8
LOTES_3K = {"Lote 3000 mar. V", "Lote 3000 mar. B"}


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


def _fontes_3k_included(cenario: dict[str, Any]) -> bool:
    fontes = [str(e.get('lote_origem_id') or '') for e in (cenario.get('eventos') or [])]
    return any(f in LOTES_3K for f in fontes)


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
    return {
        'acoes_elegiveis': acoes,
        'acoes_cap': acoes_cap,
        'cenarios': resultados,
        'best_hibrido': min(resultados, key=chave_promocao_hibrida) if resultados else None,
        'best_3k_only': min([x for x in resultados if _fontes_3k_only(x)], key=chave_promocao_hibrida) if any(_fontes_3k_only(x) for x in resultados) else None,
        'best_3k_included': min([x for x in resultados if _fontes_3k_included(x)], key=chave_promocao_hibrida) if any(_fontes_3k_included(x) for x in resultados) else None,
    }


def _resumo_switch_package(*, estado: dict[str, Any], dia: date, data_fim: date, config: dict[str, Any], plano: dict[str, Any] | None, tipo: str, pagamentos: list[dict[str, Any]]) -> dict[str, Any] | None:
    if plano is None:
        return None
    pacote = _executar_pacote_dia(
        estado_inicial=estado,
        dia=dia,
        pagamentos_dia=pagamentos,
        config=config,
        data_fim=data_fim,
        tipo_pacote=tipo,
        plano_switching=plano,
    )
    return {
        'tipo_pacote': tipo,
        'rotulo': str(plano.get('rotulo') or ''),
        'fontes': [str(e.get('lote_origem_id') or '') for e in (plano.get('eventos') or [])],
        'destinos': [str(e.get('produto_destino_key') or e.get('produto_destino') or '') for e in (plano.get('eventos') or [])],
        'classe_comparador_hibrido': str(plano.get('classe_comparador_hibrido') or ''),
        'vetor_total_estimado': [round(float(x), 6) for x in (pacote.get('vetor_total_estimado') or [])],
        'vetor_total_estimado_dict': _vetor_dict(pacote.get('vetor_total_estimado') or []),
        'patrimonio_terminal_proxy_estimado': round(float(pacote.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
        'switching_executado': bool(pacote.get('switching_executado')),
        'resultados_pagamento': deepcopy(pacote.get('resultados_pagamento') or []),
        'estado_pos_dia': deepcopy(pacote.get('estado_pos_dia') or {}),
    }


def _resumo_base_package(*, estado: dict[str, Any], dia: date, data_fim: date, config: dict[str, Any], pagamentos: list[dict[str, Any]], tipo: str) -> dict[str, Any]:
    pacote = _executar_pacote_dia(
        estado_inicial=estado,
        dia=dia,
        pagamentos_dia=pagamentos,
        config=config,
        data_fim=data_fim,
        tipo_pacote=tipo,
        plano_switching=None,
    )
    return {
        'tipo_pacote': tipo,
        'vetor_total_estimado': [round(float(x), 6) for x in (pacote.get('vetor_total_estimado') or [])],
        'vetor_total_estimado_dict': _vetor_dict(pacote.get('vetor_total_estimado') or []),
        'patrimonio_terminal_proxy_estimado': round(float(pacote.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
        'resultados_pagamento': deepcopy(pacote.get('resultados_pagamento') or []),
        'estado_pos_dia': deepcopy(pacote.get('estado_pos_dia') or {}),
    }


def _serializar_estado_3k(estado: dict[str, Any]) -> list[dict[str, Any]]:
    itens = []
    for item in (estado.get('recebidos_nao_aportados_disponiveis') or []):
        ident = str(item.get('id') or item.get('fonte_id') or '')
        if ident in LOTES_3K:
            itens.append({
                'id': ident,
                'valor_disponivel': round(float(item.get('valor_disponivel') or item.get('valor') or 0.0), 2),
                'origem_pos_vencimento': bool(item.get('origem_pos_vencimento')),
                'data_recebimento': (_coerce_date(item.get('data_recebimento')) or DATA_NU).isoformat(),
            })
    itens.sort(key=lambda x: x['id'])
    return itens


def _pagamentos_por_dia(estado: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    m: dict[str, list[dict[str, Any]]] = {}
    for pagamento in list(estado.get('pagamentos_futuros') or []):
        chave = (_coerce_date(pagamento.get('data')) or DATA_ATUAL).isoformat()
        m.setdefault(chave, []).append(deepcopy(dict(pagamento)))
    return m


def _comparar(base: dict[str, Any], alt: dict[str, Any] | None) -> dict[str, Any] | None:
    if alt is None:
        return None
    return {
        'vence_base': _chave_pacote(alt) < _chave_pacote(base),
        'delta_patrimonio_proxy': round(float(alt['patrimonio_terminal_proxy_estimado']) - float(base['patrimonio_terminal_proxy_estimado']), 2),
        'delta_vetor': {
            chave: round(float(alt['vetor_total_estimado_dict'][chave]) - float(base['vetor_total_estimado_dict'][chave]), 6)
            for chave in ORDEM_METRICA_CANONICA
        },
    }


def executar_auditoria() -> dict[str, Any]:
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
    estado = _carregar_estado_janela(contexto=contexto, data_inicio=DATA_ATUAL, data_fim=DATA_FIM)
    pagamentos_mapa = _pagamentos_por_dia(estado)

    historico: list[dict[str, Any]] = []
    trilha: list[dict[str, Any]] = []
    estado_pos_pagamento_nu: dict[str, Any] | None = None
    detalhe_pagamento_nu: list[dict[str, Any]] | None = None

    dia = DATA_ATUAL
    while dia <= DATA_NU:
        estado['data_evento_corrente'] = dia
        convertidos = _normalizar_lote_pos_vencimento_no_dia(estado, dia, config, historico)
        ativados = _ativar_recebidos_futuros_no_dia(estado, dia, config, historico) if False else _ativar_recebidos_futuros_no_dia(estado, dia, historico)
        pagamentos_dia = _ordenar_pagamentos(pagamentos_mapa.get(dia.isoformat(), []))
        base_tipo = 'pay_only' if pagamentos_dia else 'no_action'
        pacote_base = _resumo_base_package(estado=estado, dia=dia, data_fim=DATA_FIM, config=config, pagamentos=pagamentos_dia, tipo=base_tipo)

        cenarios = _gerar_cenarios_sem_gate(estado=estado, config=config, dia=dia, data_fim=DATA_FIM)
        switch_tipo = 'switch_then_pay' if pagamentos_dia else 'switch_only'
        best_overall = _resumo_switch_package(estado=estado, dia=dia, data_fim=DATA_FIM, config=config, plano=cenarios['best_hibrido'], tipo=switch_tipo, pagamentos=pagamentos_dia)
        best_3k_only = _resumo_switch_package(estado=estado, dia=dia, data_fim=DATA_FIM, config=config, plano=cenarios['best_3k_only'], tipo=switch_tipo, pagamentos=pagamentos_dia)
        best_3k_included = _resumo_switch_package(estado=estado, dia=dia, data_fim=DATA_FIM, config=config, plano=cenarios['best_3k_included'], tipo=switch_tipo, pagamentos=pagamentos_dia)

        candidatos = [('base', pacote_base)]
        if best_overall is not None:
            candidatos.append(('best_overall', best_overall))
        vencedor_tag, vencedor = min(candidatos, key=lambda item: tuple(item[1].get('vetor_total_estimado') or []) + (-float(item[1].get('patrimonio_terminal_proxy_estimado') or 0.0),))
        trilha.append({
            'data': dia.isoformat(),
            'pagamentos_dia': [
                {
                    'id': str(p.get('pagamento_id') or p.get('despesa_id') or ''),
                    'descricao': str(p.get('descricao') or ''),
                    'valor': round(float(p.get('valor') or 0.0), 2),
                }
                for p in pagamentos_dia
            ],
            'lotes_normalizados_pos_vencimento': [
                {
                    'id': str(x.get('id') or ''),
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
            'base': {k: v for k, v in pacote_base.items() if k != 'estado_pos_dia'},
            'switching_sem_gate': {
                'acoes_elegiveis': len(cenarios['acoes_elegiveis']),
                'cenarios_total': len(cenarios['cenarios']),
                'cenarios_3k_only': sum(1 for x in cenarios['cenarios'] if _fontes_3k_only(x)),
                'cenarios_3k_included': sum(1 for x in cenarios['cenarios'] if _fontes_3k_included(x)),
            },
            'best_overall': None if best_overall is None else {**{k: v for k, v in best_overall.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(pacote_base, best_overall)},
            'best_3k_only': None if best_3k_only is None else {**{k: v for k, v in best_3k_only.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(pacote_base, best_3k_only)},
            'best_3k_included': None if best_3k_included is None else {**{k: v for k, v in best_3k_included.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(pacote_base, best_3k_included)},
            'vencedor': vencedor_tag,
        })
        estado = deepcopy(vencedor['estado_pos_dia'])
        if dia == DATA_NU:
            estado_pos_pagamento_nu = deepcopy(pacote_base['estado_pos_dia'])
            detalhe_pagamento_nu = deepcopy(pacote_base['resultados_pagamento'])
        dia += timedelta(days=1)

    assert estado_pos_pagamento_nu is not None

    base_idle = _resumo_base_package(estado=estado_pos_pagamento_nu, dia=DATA_NU, data_fim=DATA_FIM, config=config, pagamentos=[], tipo='no_action')
    cenarios_pos = _gerar_cenarios_sem_gate(estado=estado_pos_pagamento_nu, config=config, dia=DATA_NU, data_fim=DATA_FIM)
    best_overall_pos = _resumo_switch_package(estado=estado_pos_pagamento_nu, dia=DATA_NU, data_fim=DATA_FIM, config=config, plano=cenarios_pos['best_hibrido'], tipo='switch_only', pagamentos=[])
    best_3k_only_pos = _resumo_switch_package(estado=estado_pos_pagamento_nu, dia=DATA_NU, data_fim=DATA_FIM, config=config, plano=cenarios_pos['best_3k_only'], tipo='switch_only', pagamentos=[])
    best_3k_included_pos = _resumo_switch_package(estado=estado_pos_pagamento_nu, dia=DATA_NU, data_fim=DATA_FIM, config=config, plano=cenarios_pos['best_3k_included'], tipo='switch_only', pagamentos=[])

    return {
        'status': 'ok',
        'baseline': 'V146',
        'versao_auditoria': 'V147',
        'janela_planejamento': {'data_inicio': DATA_ATUAL.isoformat(), 'data_fim': DATA_NU.isoformat(), 'horizonte_terminal_avaliado': DATA_FIM.isoformat()},
        'trilha_diaria_ate_nu': trilha,
        'pagamento_nu': detalhe_pagamento_nu,
        'estado_pos_pagamento_nu': {
            'saldo_3k_remanescente': _serializar_estado_3k(estado_pos_pagamento_nu),
            'base_caixa_ocioso': {k: v for k, v in base_idle.items() if k != 'estado_pos_dia'},
            'best_switch_overall': None if best_overall_pos is None else {**{k: v for k, v in best_overall_pos.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(base_idle, best_overall_pos)},
            'best_switch_3k_only': None if best_3k_only_pos is None else {**{k: v for k, v in best_3k_only_pos.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(base_idle, best_3k_only_pos)},
            'best_switch_3k_included': None if best_3k_included_pos is None else {**{k: v for k, v in best_3k_included_pos.items() if k != 'estado_pos_dia'}, 'comparacao_com_base': _comparar(base_idle, best_3k_included_pos)},
            'switching_sem_gate': {
                'acoes_elegiveis': len(cenarios_pos['acoes_elegiveis']),
                'cenarios_total': len(cenarios_pos['cenarios']),
                'cenarios_3k_only': sum(1 for x in cenarios_pos['cenarios'] if _fontes_3k_only(x)),
                'cenarios_3k_included': sum(1 for x in cenarios_pos['cenarios'] if _fontes_3k_included(x)),
            },
        },
    }


def main() -> int:
    auditoria = executar_auditoria()
    saida_json = Path('/mnt/data/auditoria_3k_mar_pos_pagamento_v147.json')
    saida_md = Path('/mnt/data/AUDITORIA_3K_MAR_POS_PAGAMENTO_V147.md')
    saida_json.write_text(json.dumps(auditoria, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    trilha = auditoria['trilha_diaria_ate_nu']
    pos = auditoria['estado_pos_pagamento_nu']
    linhas = [
        '# Auditoria dos 3k mar no pós-pagamento do Cartão NU — V147',
        '',
        f"Janela de planejamento auditada: **{DATA_ATUAL.isoformat()}** a **{DATA_NU.isoformat()}**, com horizonte terminal de avaliação em **{DATA_FIM.isoformat()}**.",
        '',
        '## Perguntas auditadas',
        '',
        '1. Após o pagamento do Cartão NU em 2026-05-04, o comparador diário prefere manter o saldo remanescente dos 3k mar em caixa ocioso ou reinvesti-lo?',
        '2. Entre a data atual e 2026-05-04, existe algum dia em que já deveríamos planejar switching envolvendo os 3k mar?',
        '',
        '## Trilha diária até 2026-05-04',
        '',
    ]
    for dia in trilha:
        linhas.append(f"### {dia['data']}")
        linhas.append(f"- pagamentos do dia: **{len(dia['pagamentos_dia'])}**")
        if dia['pagamentos_dia']:
            for p in dia['pagamentos_dia']:
                linhas.append(f"  - {p['id']} | {p['descricao']} | {_fmt_br(float(p['valor']))}")
        if dia['lotes_normalizados_pos_vencimento']:
            linhas.append('- lotes normalizados no dia:')
            for item in dia['lotes_normalizados_pos_vencimento']:
                linhas.append(f"  - {item['id']} | {_fmt_br(float(item['valor_disponivel']))}")
        linhas.append(f"- pacote base `{dia['base']['tipo_pacote']}`: patrimônio proxy **{_fmt_br(float(dia['base']['patrimonio_terminal_proxy_estimado']))}** | vetor {tuple(dia['base']['vetor_total_estimado'])}")
        if dia['best_overall'] is not None:
            comp = dia['best_overall']['comparacao_com_base']
            linhas.append(f"- melhor switching sem gate: `{dia['best_overall']['rotulo']}` | patrimônio proxy **{_fmt_br(float(dia['best_overall']['patrimonio_terminal_proxy_estimado']))}** | delta vs base **{_fmt_br(float(comp['delta_patrimonio_proxy']))}** | vence base = **{comp['vence_base']}**")
        if dia['best_3k_only'] is not None:
            comp = dia['best_3k_only']['comparacao_com_base']
            linhas.append(f"- melhor switching 3k-only: `{dia['best_3k_only']['rotulo']}` | fontes {', '.join(dia['best_3k_only']['fontes'])} | patrimônio proxy **{_fmt_br(float(dia['best_3k_only']['patrimonio_terminal_proxy_estimado']))}** | delta vs base **{_fmt_br(float(comp['delta_patrimonio_proxy']))}** | vence base = **{comp['vence_base']}**")
            linhas.append(f"  - delta vetor: {comp['delta_vetor']}")
        linhas.append(f"- vencedor do dia: **{dia['vencedor']}**")
        linhas.append('')
    total_3k = sum(float(x['valor_disponivel']) for x in pos['saldo_3k_remanescente'])
    linhas.extend([
        '## Estado após o pagamento do Cartão NU em 2026-05-04',
        '',
        f"Saldo remanescente dos 3k mar após o pagamento: **{_fmt_br(total_3k)}**.",
    ])
    for item in pos['saldo_3k_remanescente']:
        linhas.append(f"- {item['id']}: {_fmt_br(float(item['valor_disponivel']))}")
    linhas.append(f"- base `caixa ocioso`: patrimônio proxy **{_fmt_br(float(pos['base_caixa_ocioso']['patrimonio_terminal_proxy_estimado']))}** | vetor {tuple(pos['base_caixa_ocioso']['vetor_total_estimado'])}")
    for chave in ('best_switch_overall', 'best_switch_3k_only', 'best_switch_3k_included'):
        item = pos[chave]
        if item is None:
            continue
        comp = item['comparacao_com_base']
        linhas.append(f"- {chave}: `{item['rotulo']}` | fontes {', '.join(item['fontes']) or '—'} | destinos {', '.join(item['destinos']) or '—'} | patrimônio proxy **{_fmt_br(float(item['patrimonio_terminal_proxy_estimado']))}** | delta vs caixa **{_fmt_br(float(comp['delta_patrimonio_proxy']))}** | vence base = **{comp['vence_base']}**")
        linhas.append(f"  - vetor: {tuple(item['vetor_total_estimado'])}")
        linhas.append(f"  - delta vetor: {comp['delta_vetor']}")
    linhas.extend([
        '',
        '## Leitura técnica',
        '',
        '- Se o patrimônio proxy do melhor reinvestimento subir, mas o pacote ainda perder, então a causa está no vetor lexicográfico anterior ao patrimônio.',
        '- Se nenhum dia até 2026-05-04 promover switching com 3k mar, então não há evidência operacional de que o planejamento devesse ser antecipado antes do vencimento dentro deste horizonte curto.',
    ])
    saida_md.write_text('\n'.join(linhas), encoding='utf-8')
    print(json.dumps({
        'json': str(saida_json),
        'md': str(saida_md),
        'summary': {
            'post_payment_remanescente_3k': total_3k,
            'base_idle': pos['base_caixa_ocioso']['patrimonio_terminal_proxy_estimado'],
            'best_switch_3k_only': None if pos['best_switch_3k_only'] is None else pos['best_switch_3k_only']['patrimonio_terminal_proxy_estimado'],
            'best_switch_3k_only_delta': None if pos['best_switch_3k_only'] is None else pos['best_switch_3k_only']['comparacao_com_base']['delta_patrimonio_proxy'],
            'days_switching_wins_until_nu': [d['data'] for d in trilha if d['best_3k_only'] and d['best_3k_only']['comparacao_com_base']['vence_base']],
            'day_0504_switching_wins': next((d['best_3k_only']['comparacao_com_base']['vence_base'] for d in trilha if d['data']=='2026-05-04' and d['best_3k_only']), None),
        }
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())

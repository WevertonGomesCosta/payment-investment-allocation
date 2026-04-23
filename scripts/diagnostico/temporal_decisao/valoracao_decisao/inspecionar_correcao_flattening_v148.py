from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
from typing import Any

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ

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

DATA_INICIO = date(2026, 4, 22)
DATA_ALVO = date(2026, 5, 4)
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
    return {
        'tipo_pacote': tipo,
        'rotulo_switching': str((plano or {}).get('rotulo') or ''),
        'fontes_switch': [str(e.get('lote_origem_id') or '') for e in ((plano or {}).get('eventos') or [])],
        'destinos_switch': [str(e.get('produto_destino_key') or e.get('produto_destino') or '') for e in ((plano or {}).get('eventos') or [])],
        'vetor_total_estimado': [round(float(x), 6) for x in (pacote.get('vetor_total_estimado') or [])],
        'vetor_total_estimado_dict': _vetor_dict(pacote.get('vetor_total_estimado') or []),
        'patrimonio_terminal_proxy_estimado': round(float(pacote.get('patrimonio_terminal_proxy_estimado') or 0.0), 2),
        'switching_executado': bool(pacote.get('switching_executado')),
        'resultados_pagamento': deepcopy(pacote.get('resultados_pagamento') or []),
        'estado_pos_dia': deepcopy(pacote.get('estado_pos_dia') or {}),
        'metrica_dia': deepcopy(pacote.get('metrica_dia') or {}),
        'metrica_total_estimada': deepcopy(pacote.get('metrica_total_estimada') or {}),
        'eventos_switching': deepcopy(pacote.get('eventos_switching') or []),
    }


def _serializar_lotes_switching(estado: dict[str, Any]) -> list[dict[str, Any]]:
    itens = []
    for lote in (estado.get('lotes_aportados') or []):
        if not lote.get('origem_switching_evento'):
            continue
        itens.append({
            'id': str(lote.get('id') or ''),
            'investimento': str(lote.get('investimento') or ''),
            'valor_liquido_resgatavel': round(float(lote.get('valor_liquido_resgatavel') or 0.0), 2),
            'valor_terminal_estimado': round(float(lote.get('valor_terminal_estimado') or 0.0), 2),
            'valor_liquido_base_terminal_estimado': round(float(lote.get('valor_liquido_base_terminal_estimado') or 0.0), 2),
            'data_final_valor_terminal_estimado': (_coerce_date(lote.get('data_final_valor_terminal_estimado')) or DATA_FIM).isoformat() if lote.get('data_final_valor_terminal_estimado') else None,
            'origem_tipo_evento': str(lote.get('origem_tipo_evento') or ''),
        })
    itens.sort(key=lambda x: x['id'])
    return itens


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
        else:
            _ativar_recebidos_futuros_no_dia(estado, dia, historico)
        dia += timedelta(days=1)

    estado['data_evento_corrente'] = DATA_ALVO
    lotes_normalizados = _normalizar_lote_pos_vencimento_no_dia(estado, DATA_ALVO, config, historico)
    _ativar_recebidos_futuros_no_dia(estado, DATA_ALVO, historico)
    pagamentos_dia = _ordenar_pagamentos(pagamentos_mapa.get(DATA_ALVO.isoformat(), []))

    base = _resumo_pacote(estado=estado, dia=DATA_ALVO, data_fim=DATA_FIM, config=config, pagamentos=pagamentos_dia, tipo='pay_only', plano=None)
    cenarios = _gerar_cenarios_sem_gate(estado=estado, config=config, dia=DATA_ALVO, data_fim=DATA_FIM)
    plano_3k = cenarios['best_3k_only']
    if plano_3k is not None:
        plano_3k = {**deepcopy(plano_3k), 'classe_comparador_hibrido': 'auditoria_3k_only_sem_gate', 'promovivel_hibrido': True}
    pacote_3k = _resumo_pacote(estado=estado, dia=DATA_ALVO, data_fim=DATA_FIM, config=config, pagamentos=pagamentos_dia, tipo='switch_then_pay', plano=plano_3k) if plano_3k else None

    comparacao = None
    if pacote_3k is not None:
        comparacao = {
            'switch_3k_vence_base': _chave_pacote(pacote_3k) < _chave_pacote(base),
            'delta_patrimonio_terminal_proxy': round(float(pacote_3k['patrimonio_terminal_proxy_estimado']) - float(base['patrimonio_terminal_proxy_estimado']), 2),
            'delta_vetor': {
                chave: round(float(pacote_3k['vetor_total_estimado_dict'][chave]) - float(base['vetor_total_estimado_dict'][chave]), 6)
                for chave in ORDEM_METRICA_CANONICA
            },
        }

    payload = {
        'status': 'ok',
        'baseline': 'V147',
        'versao_experimental': 'V148',
        'data_alvo': DATA_ALVO.isoformat(),
        'data_fim': DATA_FIM.isoformat(),
        'lotes_normalizados_no_dia': [
            {
                'id': str(x.get('id') or ''),
                'valor_disponivel': round(float(x.get('valor_disponivel') or x.get('valor') or 0.0), 2),
            }
            for x in lotes_normalizados
        ],
        'cenario_sem_gate': {
            'baseline_terminal': cenarios['baseline_terminal'],
            'acoes_elegiveis_total': len(cenarios['acoes_elegiveis']),
            'cenarios_total': len(cenarios['cenarios']),
            'melhor_3k_only': None if cenarios['best_3k_only'] is None else {
                'rotulo': str(cenarios['best_3k_only'].get('rotulo') or ''),
                'fontes': list(cenarios['best_3k_only'].get('_fontes') or []),
                'destinos': list(cenarios['best_3k_only'].get('_destinos') or []),
                'patrimonio_liquido_terminal_proxy': round(float(cenarios['best_3k_only'].get('patrimonio_liquido_terminal_proxy') or 0.0), 2),
                'ganho_terminal_vs_baseline': round(float(cenarios['best_3k_only'].get('ganho_patrimonio_terminal_proxy') or 0.0), 2),
            },
        },
        'pacote_base_pay_only': base,
        'pacote_switch_then_pay_3k_only': pacote_3k,
        'comparacao': comparacao,
        'lotes_switching_pos_dia': _serializar_lotes_switching((pacote_3k or {}).get('estado_pos_dia') or {}),
    }
    return payload


if __name__ == '__main__':
    resultado = executar()
    saida_json = RAIZ / 'saidas' / 'auditoria_correcao_flattening_v148_2026-05-04.json'
    saida_json.write_text(json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

    base = resultado['pacote_base_pay_only']
    alt = resultado['pacote_switch_then_pay_3k_only']
    comp = resultado['comparacao'] or {}
    lotes_str = ', '.join([f"{x['id']}={_fmt_br(x['valor_disponivel'])}" for x in resultado['lotes_normalizados_no_dia']]) or 'nenhum'
    linhas = [
        '# Auditoria experimental da correção de flattening em 2026-05-04',
        '',
        'Baseline: V147',
        'Versão experimental: V148',
        '',
        '## Resumo',
        f"- Lotes normalizados no dia: {lotes_str}",
        f"- Patrimônio terminal proxy do pacote base (`pay_only`): **{_fmt_br(base['patrimonio_terminal_proxy_estimado'])}**",
    ]
    if alt is not None:
        linhas.extend([
            f"- Patrimônio terminal proxy do pacote `switch_then_pay` 3k-only: **{_fmt_br(alt['patrimonio_terminal_proxy_estimado'])}**",
            f"- Delta de patrimônio terminal proxy: **{_fmt_br(comp.get('delta_patrimonio_terminal_proxy', 0.0))}**",
            f"- `switch_then_pay` 3k-only vence o base: **{comp.get('switch_3k_vence_base')}**",
            f"- Fontes do switching: {', '.join(alt['fontes_switch']) or 'nenhuma'}",
            f"- Destinos do switching: {', '.join(alt['destinos_switch']) or 'nenhum'}",
        ])
    else:
        linhas.append('- Nenhum pacote `switch_then_pay` 3k-only foi construído.')
    linhas.extend([
        '',
        '## Melhor cenário 3k-only sem gate',
        json.dumps(resultado['cenario_sem_gate']['melhor_3k_only'], ensure_ascii=False, indent=2),
        '',
        '## Lotes de switching no estado pós-dia',
        json.dumps(resultado['lotes_switching_pos_dia'], ensure_ascii=False, indent=2),
        '',
        '## Comparação vetorial',
        json.dumps(comp.get('delta_vetor', {}), ensure_ascii=False, indent=2),
    ])
    saida_md = RAIZ / 'relatorios' / 'AUDITORIA_CORRECAO_FLATTENING_V148_2026-05-04.md'
    saida_md.write_text('\n'.join(linhas), encoding='utf-8')
    print(str(saida_json))
    print(str(saida_md))

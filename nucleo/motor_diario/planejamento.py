from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

from nucleo.comparador_hibrido_switching_v1 import classificar_cenario_diario, escolher_melhor_cenario_promovivel
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import (
    _cap_fontes_por_destino,
    _comparar_com_baseline,
    _gerar_cenarios_integral_parametrizados,
    _melhores_por_fonte_destino,
)
from nucleo.planejador_switching_temporal_v1 import planejar_switching_temporal_v1
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _normalizar_lote_pos_vencimento_no_dia,
    simular_cenario_eventos_v1,
)


def _cenarios_switching_diario_v143(
    *,
    estado: dict[str, Any],
    config: dict[str, Any],
    data_atual: date,
    data_fim: date,
    limite_candidatos_por_data: int = 24,
    cap_fontes_destino: int = 5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    estado_local = deepcopy(estado)
    estado_local['data_evento_corrente'] = data_atual
    _normalizar_lote_pos_vencimento_no_dia(estado_local, data_atual, config, None)
    horizonte = {'data_inicio': data_atual.isoformat(), 'data_fim': data_fim.isoformat()}
    baseline = simular_cenario_eventos_v1(deepcopy(estado_local), [], config, horizonte=horizonte)
    plano = planejar_switching_temporal_v1(
        estado_global=estado_local,
        config=config,
        horizonte_planejamento=horizonte,
        filtros_eventos=None,
        limite_candidatos_por_data=limite_candidatos_por_data,
    )
    acoes = [
        deepcopy(item)
        for item in (plano.get('acoes_candidatas') or [])
        if str(item.get('tipo_acao') or '') in {'switching_simples', 'aporte_nao_aportado'} and item.get('elegivel')
    ]
    acoes = _cap_fontes_por_destino(_melhores_por_fonte_destino(acoes), cap_fontes_destino)
    cenarios = _gerar_cenarios_integral_parametrizados(acoes)
    resultados: list[dict[str, Any]] = []
    for cenario in cenarios:
        sim = simular_cenario_eventos_v1(deepcopy(estado_local), cenario.get('eventos') or [], config, horizonte=horizonte)
        comparacao = _comparar_com_baseline(sim, baseline)
        classif = classificar_cenario_diario(comparacao)
        estado_pos = deepcopy(estado_local)
        _aplicar_switching_eventos(estado_pos, cenario.get('eventos') or [], data_atual, [])
        resultados.append({
            **cenario,
            **comparacao,
            **classif,
            'estado_pos_switching': estado_pos,
            'custo_fiscal_switching_total': sim.get('custo_fiscal_switching_total'),
            'perda_liquidez_switching_total': sim.get('perda_liquidez_switching_total'),
            'patrimonio_liquido_terminal_proxy': sim.get('patrimonio_liquido_terminal_proxy'),
            'metrica_central': sim.get('metrica_central'),
        })
    return plano, resultados


def _melhor_plano_switching_diario_v143(
    *,
    estado: dict[str, Any],
    config: dict[str, Any],
    data_atual: date,
    data_fim: date,
    limite_candidatos_por_data: int = 24,
    cap_fontes_destino: int = 5,
) -> dict[str, Any] | None:
    _, resultados = _cenarios_switching_diario_v143(
        estado=estado,
        config=config,
        data_atual=data_atual,
        data_fim=data_fim,
        limite_candidatos_por_data=limite_candidatos_por_data,
        cap_fontes_destino=cap_fontes_destino,
    )
    return escolher_melhor_cenario_promovivel(resultados)

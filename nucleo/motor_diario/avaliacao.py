from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from typing import Any

from nucleo.alocador_pagamentos_terminal_v1 import alocar_pagamento_terminal_v1
from nucleo.avaliador_cenarios_conjuntos_v1 import vetor_lexicografico_central
from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import _safe_float
from nucleo.motor_diario.estado import _ordenar_pagamentos, _remover_pagamentos_ate_dia
from nucleo.motor_diario.metricas import _combinar_metricas
from nucleo.simulador_central_eventos_v1 import (
    _aplicar_switching_eventos,
    _calcular_metrica,
    _consumir_componentes,
    _coerce_date,
    _normalizar_lote_pos_vencimento_no_dia,
    _patrimonio_terminal_proxy,
    simular_cenario_eventos_v1,
)


def _avaliar_continuacao_neutra(
    *,
    estado_pos_dia: dict[str, Any],
    dia_atual: date,
    data_fim: date,
    config: dict[str, Any],
) -> tuple[dict[str, float], float]:
    if dia_atual >= data_fim:
        metrica = {
            'violacoes_protegida': 0.0,
            'deficit_liquido_total': 0.0,
            'pagamentos_sem_cobertura_integral': 0.0,
            'perda_patrimonio_liquido_terminal': 0.0,
            'destruicao_estrategica_lotes': 0.0,
            'deterioracao_liquidez_futura': 0.0,
            'custo_fiscal_imediato': 0.0,
            'custo_operacional': 0.0,
        }
        patrimonio = _patrimonio_terminal_proxy(estado_pos_dia, metrica, 0.0)
        return metrica, round(patrimonio, 2)

    estado_futuro = deepcopy(estado_pos_dia)
    _remover_pagamentos_ate_dia(estado_futuro, dia_atual)
    proximo_dia = dia_atual + timedelta(days=1)
    if not (estado_futuro.get('pagamentos_futuros') or []):
        estado_futuro['data_evento_corrente'] = dia_atual
        metrica = {
            'violacoes_protegida': 0.0,
            'deficit_liquido_total': 0.0,
            'pagamentos_sem_cobertura_integral': 0.0,
            'perda_patrimonio_liquido_terminal': 0.0,
            'destruicao_estrategica_lotes': 0.0,
            'deterioracao_liquidez_futura': 0.0,
            'custo_fiscal_imediato': 0.0,
            'custo_operacional': 0.0,
        }
        patrimonio = _patrimonio_terminal_proxy(estado_futuro, metrica, 0.0)
        return metrica, round(patrimonio, 2)

    horizonte = {'data_inicio': proximo_dia.isoformat(), 'data_fim': data_fim.isoformat()}
    sim = simular_cenario_eventos_v1(deepcopy(estado_futuro), [], config, horizonte=horizonte)
    return dict(sim.get('metrica_central') or {}), round(_safe_float(sim.get('patrimonio_liquido_terminal_proxy')), 2)


def _executar_pacote_dia(
    *,
    estado_inicial: dict[str, Any],
    dia: date,
    pagamentos_dia: list[dict[str, Any]],
    config: dict[str, Any],
    data_fim: date,
    tipo_pacote: str,
    plano_switching: dict[str, Any] | None,
) -> dict[str, Any]:
    estado = deepcopy(estado_inicial)
    historico_local: list[dict[str, Any]] = []
    _normalizar_lote_pos_vencimento_no_dia(estado, dia, config, historico_local)
    eventos_executados: list[dict[str, Any]] = []
    ganho_switching = 0.0
    perda_liquidez_switching = 0.0
    custo_fiscal_switching = 0.0
    rotulo_switching = None
    classe_switching = None
    switching_executado = False

    if tipo_pacote in {'switch_only', 'switch_then_pay'} and plano_switching is not None:
        eventos = [deepcopy(dict(x)) for x in (plano_switching.get('eventos') or [])]
        novos_eventos, ganho_switching, perda_liquidez_switching, custo_fiscal_switching = _aplicar_switching_eventos(estado, eventos, dia, historico_local)
        eventos_executados.extend(novos_eventos)
        switching_executado = len(novos_eventos) > 0
        rotulo_switching = str(plano_switching.get('rotulo') or '') or None
        classe_switching = str(plano_switching.get('classe_comparador_hibrido') or '') or None

    resultados_pagamento: list[dict[str, Any]] = []
    pagamentos_ids = [str(x.get('pagamento_id') or x.get('despesa_id') or '') for x in pagamentos_dia]
    if tipo_pacote in {'pay_only', 'switch_then_pay'}:
        for pagamento in _ordenar_pagamentos(pagamentos_dia):
            estado_para_pagamento = deepcopy(estado)
            estado_para_pagamento['dias_horizonte_terminal'] = max(((_coerce_date(estado.get('data_fim_recorte')) or dia) - dia).days, 0)
            alocacao = alocar_pagamento_terminal_v1(
                pagamento=pagamento,
                estado_global=estado_para_pagamento,
                config=config,
                plano_switching_candidato=None,
                permitir_combinacao_minima=True,
                limite_fontes_candidatas=None,
            )
            resultados_pagamento.append(alocacao)
            _consumir_componentes(estado, alocacao.get('componentes_escolhidos') or [])

    metrica_dia = _calcular_metrica(
        resultados_pagamento,
        ganho_switching=ganho_switching,
        perda_liquidez_switching=perda_liquidez_switching,
        custo_fiscal_switching=custo_fiscal_switching,
        eventos_executados=eventos_executados,
    )
    estado['data_evento_corrente'] = dia
    _remover_pagamentos_ate_dia(estado, dia)
    metrica_futura, patrimonio_futuro = _avaliar_continuacao_neutra(
        estado_pos_dia=estado,
        dia_atual=dia,
        data_fim=data_fim,
        config=config,
    )
    metrica_total = _combinar_metricas(metrica_dia, metrica_futura)
    patrimonio_total = round(patrimonio_futuro - _safe_float(metrica_dia.get('perda_patrimonio_liquido_terminal')), 2)
    return {
        'tipo_pacote': tipo_pacote,
        'estado_pos_dia': estado,
        'eventos_switching': eventos_executados,
        'switching_executado': switching_executado,
        'rotulo_switching': rotulo_switching,
        'classe_switching': classe_switching,
        'resultados_pagamento': resultados_pagamento,
        'metrica_dia': metrica_dia,
        'metrica_total_estimada': metrica_total,
        'vetor_total_estimado': vetor_lexicografico_central(metrica_total),
        'patrimonio_terminal_proxy_estimado': patrimonio_total,
        'pagamentos_ids': pagamentos_ids,
    }

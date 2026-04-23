from __future__ import annotations

from typing import Any

from nucleo.fluxo_pagamentos_terminal_recorte_amplo_v142 import _safe_float


def _combinar_metricas(m1: dict[str, Any] | None, m2: dict[str, Any] | None) -> dict[str, float]:
    a = dict(m1 or {})
    b = dict(m2 or {})
    return {
        'violacoes_protegida': round(_safe_float(a.get('violacoes_protegida')) + _safe_float(b.get('violacoes_protegida')), 2),
        'deficit_liquido_total': round(_safe_float(a.get('deficit_liquido_total')) + _safe_float(b.get('deficit_liquido_total')), 2),
        'pagamentos_sem_cobertura_integral': round(_safe_float(a.get('pagamentos_sem_cobertura_integral')) + _safe_float(b.get('pagamentos_sem_cobertura_integral')), 2),
        'perda_patrimonio_liquido_terminal': round(_safe_float(a.get('perda_patrimonio_liquido_terminal')) + _safe_float(b.get('perda_patrimonio_liquido_terminal')), 2),
        'destruicao_estrategica_lotes': round(_safe_float(a.get('destruicao_estrategica_lotes')) + _safe_float(b.get('destruicao_estrategica_lotes')), 2),
        'deterioracao_liquidez_futura': round(_safe_float(a.get('deterioracao_liquidez_futura')) + _safe_float(b.get('deterioracao_liquidez_futura')), 2),
        'custo_fiscal_imediato': round(_safe_float(a.get('custo_fiscal_imediato')) + _safe_float(b.get('custo_fiscal_imediato')), 2),
        'custo_operacional': round(_safe_float(a.get('custo_operacional')) + _safe_float(b.get('custo_operacional')), 2),
    }


def _chave_pacote(resultado: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(resultado.get('vetor_total_estimado') or ()) + (-_safe_float(resultado.get('patrimonio_terminal_proxy_estimado')),)


def _chave_pacote_tau(resultado: dict[str, Any], tau: float) -> tuple[Any, ...]:
    vetor = list(resultado.get('vetor_total_estimado') or ())
    if len(vetor) < 8:
        vetor = vetor + [0.0] * (8 - len(vetor))
    primeiros_sete = tuple(float(x) for x in vetor[:7])
    custo_operacional = float(vetor[7] or 0.0)
    patrimonio = _safe_float(resultado.get('patrimonio_terminal_proxy_estimado'))
    patrimonio_ajustado = patrimonio - float(tau or 0.0) * custo_operacional
    return primeiros_sete + (-patrimonio_ajustado, custo_operacional, -patrimonio)


def _selecionar_vencedor_pacote(candidatos: list[dict[str, Any]], tau: float | None = None) -> dict[str, Any]:
    if tau is None:
        return min(candidatos, key=_chave_pacote)
    return min(candidatos, key=lambda item: _chave_pacote_tau(item, tau))

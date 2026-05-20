"""Integração shadow temporal opcional para a auditoria da saída canônica.

V17-F0-V.4K acrescenta um bloco de auditoria temporal shadow a uma cópia do
PacoteSaidaCanonica, preservando integralmente os blocos observáveis e sem
alterar o construtor operacional efetivo de saida_canonica.py.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from nucleo.pacotes_temporais_agregados_saida import construir_pacotes_temporais_agregados_saida_shadow
from nucleo.saida_canonica import PacoteSaidaCanonica, construir_saida_canonica


CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K = "temporal_shadow_v4k"


def _qtd(valor: Any) -> int:
    try:
        if valor is None:
            return 0
        if hasattr(valor, "__len__"):
            return int(len(valor))
    except Exception:
        return 0
    return 0


def _lotes_saida(saida: PacoteSaidaCanonica) -> set[str]:
    lotes: set[str] = set()
    for row in list(saida.lotes_ativos or []) + list(saida.lotes_exauridos or []):
        lote = str(row.get("Lote") or row.get("lote_id") or "").strip()
        if lote:
            lotes.add(lote)
    return lotes


def _estado_normalizado_base_observavel(saida: PacoteSaidaCanonica, estado_final: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lotes_obs = _lotes_saida(saida)
    return [
        dict(row)
        for row in list(estado_final or [])
        if str(row.get("lote_id") or row.get("Lote") or "").strip() in lotes_obs
    ]


def construir_bloco_temporal_shadow_v4k(contexto: Any, saida_base: PacoteSaidaCanonica) -> dict[str, Any]:
    """Constrói bloco compacto de auditoria temporal shadow para a saída."""
    agregados = construir_pacotes_temporais_agregados_saida_shadow(contexto)

    replay = agregados.pacote_replay_passado
    ledger = agregados.pacote_ledger_temporal_operacional
    estado = agregados.pacote_estado_temporal
    auditoria_temporal = agregados.pacote_auditoria_temporal

    auditoria_agregador = dict(agregados.auditoria_agregador_temporal or {})
    validacao_agregador = dict(agregados.validacao_agregador_temporal or {})
    auditoria_residuos = dict(getattr(auditoria_temporal, "auditoria_residuos_legados", {}) or {})

    estado_final = list(getattr(estado, "estado_lotes_final", []) or [])
    estado_normalizado = _estado_normalizado_base_observavel(saida_base, estado_final)

    extrato_passado_identico = _qtd(saida_base.extrato_passado) == _qtd(getattr(replay, "log_movimentos_passados", []))
    extrato_futuro_identico = _qtd(saida_base.extrato_futuro) == _qtd(getattr(ledger, "eventos_temporais", []))
    lotes_identicos = (_qtd(saida_base.lotes_ativos) + _qtd(saida_base.lotes_exauridos)) == _qtd(estado_normalizado)

    return {
        "ok": bool(validacao_agregador.get("ok")),
        "versao_microetapa": "V17-F0-V.4K",
        "versao_agregador": getattr(agregados, "versao", None),
        "modo_shadow": True,
        "data_referencia": getattr(agregados, "data_referencia", None),
        "pacote_replay_passado_presente": replay is not None,
        "pacote_ledger_temporal_operacional_presente": ledger is not None,
        "pacote_estado_temporal_presente": estado is not None,
        "pacote_auditoria_temporal_presente": auditoria_temporal is not None,
        "validacao_agregador_ok": bool(validacao_agregador.get("ok")),
        "erros_bloqueantes_agregador_total": _qtd(validacao_agregador.get("erros_bloqueantes", [])),
        "extrato_passado_qtd_saida": _qtd(saida_base.extrato_passado),
        "extrato_passado_qtd_pacote": _qtd(getattr(replay, "log_movimentos_passados", [])),
        "extrato_passado_identico": extrato_passado_identico,
        "extrato_futuro_qtd_saida": _qtd(saida_base.extrato_futuro),
        "extrato_futuro_qtd_pacote": _qtd(getattr(ledger, "eventos_temporais", [])),
        "extrato_futuro_identico": extrato_futuro_identico,
        "lotes_ativos_qtd_saida": _qtd(saida_base.lotes_ativos),
        "lotes_exauridos_qtd_saida": _qtd(saida_base.lotes_exauridos),
        "lotes_saida_total": _qtd(saida_base.lotes_ativos) + _qtd(saida_base.lotes_exauridos),
        "estado_lotes_final_qtd_original": _qtd(estado_final),
        "estado_lotes_final_qtd_normalizado_base_observavel": _qtd(estado_normalizado),
        "lotes_normalizados_identicos": lotes_identicos,
        "fechamento_atual_qtd_saida": _qtd(saida_base.fechamento_atual),
        "auditoria_temporal_global_ok": bool(getattr(auditoria_temporal, "validacao_temporal_global", {}).get("ok")),
        "fonte_primaria_switching_ledger": auditoria_agregador.get("fonte_primaria_switching_ledger"),
        "usa_planilha_bruta_como_fonte_primaria": auditoria_agregador.get("usa_planilha_bruta_como_fonte_primaria"),
        "usa_retorno_ledger_dict_legado": auditoria_agregador.get("usa_retorno_ledger_dict_legado") if auditoria_agregador else auditoria_residuos.get("usa_retorno_ledger_dict_legado"),
        "saida_chama_ledger_diretamente_fluxo_atual": auditoria_agregador.get("saida_chama_ledger_diretamente_fluxo_atual") if auditoria_agregador else auditoria_residuos.get("saida_chama_ledger_diretamente"),
        "auditoria_existente_preservada": True,
        "auditoria_acrescida_apenas_bloco_temporal_shadow": True,
        "sem_alteracao_observavel": True,
    }


def construir_saida_canonica_com_temporal_shadow_v4k(
    contexto: Any,
    *,
    versao: str = "V203",
) -> PacoteSaidaCanonica:
    """Retorna PacoteSaidaCanonica com bloco temporal shadow na auditoria.

    O pacote operacional de saída não é alterado in-place. A função constrói a
    saída atual, copia a auditoria existente e acrescenta apenas
    `temporal_shadow_v4k`.
    """
    saida_base = construir_saida_canonica(contexto, versao=versao)
    auditoria_base = dict(saida_base.auditoria or {})
    bloco = construir_bloco_temporal_shadow_v4k(contexto, saida_base)
    auditoria_shadow = dict(auditoria_base)
    auditoria_shadow[CHAVE_AUDITORIA_TEMPORAL_SHADOW_V4K] = bloco
    return replace(saida_base, auditoria=auditoria_shadow)

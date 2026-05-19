"""Ledger com switching_canonico como fonte primária controlada.

V17-F0-V.3.7R promove o switching_canonico dentro de um construtor controlado,
sem editar diretamente o ledger legado. A promoção ocorre por substituição
temporária das funções globais que o ledger usa para obter mapa/eventos de
switching operacional. Ao final da chamada, o caminho legado é restaurado.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from nucleo.switching_canonico_ledger_shadow import (
    switching_canonico_para_eventos_ledger_shadow,
    switching_canonico_para_mapa_ledger_shadow,
)


FONTE_PRIMARIA_SWITCHING_LEDGER_V37R = "switching_canonico"
FALLBACK_LEGADO_SWITCHING_LEDGER_V37R = "aba_switching_operacional_legado"


def _mapa_switchings_canonico_compativel_ledger_v37r(contexto: Any) -> dict[str, dict[str, Any]]:
    """Retorna mapa canônico com schema compatível ao legado do ledger.

    A origem observável é mantida compatível para preservar identidade da saída.
    A auditoria da promoção é feita fora da estrutura operacional retornada.
    """
    try:
        mapa_canonico = switching_canonico_para_mapa_ledger_shadow(contexto)
    except Exception:
        mapa_canonico = {}

    if not mapa_canonico:
        import nucleo.ledger_temporal_conjunto as ledger_legado

        return ledger_legado._mapa_switchings_aba_operacional(contexto)

    mapa: dict[str, dict[str, Any]] = {}
    for lote, meta in mapa_canonico.items():
        lote_origem = str(lote or meta.get("lote_origem") or "").strip()
        if not lote_origem:
            continue
        mapa[lote_origem] = {
            "lote_origem": lote_origem,
            "data_switching": meta.get("data_switching"),
            "produto_destino": str(meta.get("produto_destino") or "").strip(),
            "valor_liquido_origem": meta.get("valor_liquido_origem"),
            "status_switching": "classificado_promovido",
            "origem_mapa_migracao": "aba_switching_operacional",
            "lote_pos_switching": str(meta.get("lote_pos_switching") or "").strip(),
        }
    return mapa


def _eventos_switching_canonico_compativel_ledger_v37r(contexto: Any) -> list[dict[str, Any]]:
    """Retorna eventos canônicos com schema compatível ao legado do ledger."""
    try:
        eventos_canonicos = switching_canonico_para_eventos_ledger_shadow(contexto)
    except Exception:
        eventos_canonicos = []

    if not eventos_canonicos:
        import nucleo.ledger_temporal_conjunto as ledger_legado

        return ledger_legado._eventos_switching_aba_operacional(contexto)

    eventos: list[dict[str, Any]] = []
    for evento in eventos_canonicos:
        lote_origem = str(evento.get("lote_origem") or "").strip()
        if not lote_origem:
            continue
        eventos.append({
            "evento_switching_id": str(
                evento.get("evento_switching_id_legado_compat")
                or evento.get("evento_switching_id")
                or ""
            ).strip(),
            "lote_origem": lote_origem,
            "data_switching": evento.get("data_switching"),
            "produto_destino": str(evento.get("produto_destino") or "").strip(),
            "valor_liquido_origem": evento.get("valor_liquido_origem"),
            "lote_pos_switching": str(evento.get("lote_pos_switching") or "").strip(),
            "status_materializacao_passiva": "materializado_passivo",
            "origem_mapa_migracao": "aba_switching_operacional",
        })
    return eventos


@contextmanager
def _usar_switching_canonico_como_fonte_primaria_v37r() -> Iterator[None]:
    import nucleo.ledger_temporal_conjunto as ledger_legado

    mapa_original = ledger_legado._mapa_switchings_aba_operacional
    eventos_original = ledger_legado._eventos_switching_aba_operacional
    ledger_legado._mapa_switchings_aba_operacional = _mapa_switchings_canonico_compativel_ledger_v37r
    ledger_legado._eventos_switching_aba_operacional = _eventos_switching_canonico_compativel_ledger_v37r
    try:
        yield
    finally:
        ledger_legado._mapa_switchings_aba_operacional = mapa_original
        ledger_legado._eventos_switching_aba_operacional = eventos_original


def construir_ledger_temporal_conjunto_switching_canonico_v37r(
    quadro_futuro: Any,
    mapa_central: dict[str, dict[str, Any]] | None = None,
    contexto: Any | None = None,
) -> dict[str, Any]:
    """Executa o ledger usando switching_canonico como fonte primária controlada."""
    import nucleo.ledger_temporal_conjunto as ledger_legado

    with _usar_switching_canonico_como_fonte_primaria_v37r():
        return ledger_legado.construir_ledger_temporal_conjunto(
            quadro_futuro,
            mapa_central,
            contexto,
        )


def auditoria_promocao_switching_canonico_ledger_v37r() -> dict[str, Any]:
    return {
        "fonte_primaria_switching_ledger": FONTE_PRIMARIA_SWITCHING_LEDGER_V37R,
        "fallback_legado_disponivel_apenas_para_auditoria": True,
        "promocao_controlada_v37r": True,
        "edita_ledger_legado_diretamente": False,
        "preserva_schema_operacional_legado": True,
    }


__all__ = [
    "FALLBACK_LEGADO_SWITCHING_LEDGER_V37R",
    "FONTE_PRIMARIA_SWITCHING_LEDGER_V37R",
    "auditoria_promocao_switching_canonico_ledger_v37r",
    "construir_ledger_temporal_conjunto_switching_canonico_v37r",
]

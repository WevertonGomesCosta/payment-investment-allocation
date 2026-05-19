"""Conexão opcional shadow entre PacoteLedgerTemporal e saída canônica.

V17-F0-V.3.7M não substitui o ledger operacional usado por
``nucleo.saida_canonica.construir_saida_canonica``. Este módulo apenas constrói
um PacoteLedgerTemporal em modo shadow e devolve um PacoteSaidaCanonica com a
mesma saída observável, acrescida de um bloco de auditoria shadow.
"""

from __future__ import annotations

from typing import Any

from nucleo.pacote_ledger_temporal import PacoteLedgerTemporal, construir_pacote_ledger_temporal_shadow
from nucleo.saida_canonica import (
    PacoteSaidaCanonica,
    _mapa_pagamentos_central,
    _quadro_futuro_preferencial,
    construir_saida_canonica,
)


BLOCO_AUDITORIA_LEDGER_SHADOW_V37M = "ledger_shadow_v37m"


def _montar_bloco_auditoria_ledger_shadow_v37m(
    saida_base: PacoteSaidaCanonica,
    pacote_ledger_shadow: PacoteLedgerTemporal,
) -> dict[str, Any]:
    auditoria_pacote = dict(pacote_ledger_shadow.auditoria_ledger_temporal or {})
    validacao_pacote = dict(pacote_ledger_shadow.validacao_ledger_temporal or {})
    auditoria_saida = dict(saida_base.auditoria or {})
    fifo_saida = list(auditoria_saida.get("fifo_candidatos_avaliados", []) or [])
    qtd_eventos_saida = int(auditoria_saida.get("qtd_eventos_ledger", 0) or 0)

    return {
        "modo_shadow": True,
        "origem": "nucleo.saida_canonica_ledger_shadow.construir_saida_canonica_com_ledger_shadow_opcional",
        "pacote_ledger_temporal_classe": type(pacote_ledger_shadow).__name__,
        "pacote_ledger_temporal_entrada_obrigatoria_saida": False,
        "saida_operacional_preservada": True,
        "ponte_legada_removida": False,
        "fonte_operacional_saida": "construir_saida_canonica_legado",
        "validacao_ok": bool(validacao_pacote.get("ok")),
        "qtd_eventos_temporais_shadow": len(pacote_ledger_shadow.eventos_temporais),
        "qtd_fifo_candidatos_shadow": len(pacote_ledger_shadow.fifo_candidatos_avaliados),
        "qtd_eventos_ledger_auditoria_saida": qtd_eventos_saida,
        "qtd_fifo_auditoria_saida": len(fifo_saida),
        "equivalente_qtd_eventos_saida_vs_shadow": qtd_eventos_saida == len(pacote_ledger_shadow.eventos_temporais),
        "equivalente_qtd_fifo_saida_vs_shadow": len(fifo_saida) == len(pacote_ledger_shadow.fifo_candidatos_avaliados),
        "usa_contexto_amplo": auditoria_pacote.get("usa_contexto_amplo"),
        "usa_planilha_bruta": auditoria_pacote.get("usa_planilha_bruta"),
        "usa_switching_shadow": auditoria_pacote.get("usa_switching_shadow"),
        "usa_pos_injetado": auditoria_pacote.get("usa_pos_injetado"),
        "erros_bloqueantes": list(validacao_pacote.get("erros_bloqueantes", []) or []),
        "avisos": list(validacao_pacote.get("avisos", []) or []),
    }


def _copiar_saida_com_auditoria(
    saida_base: PacoteSaidaCanonica,
    auditoria_nova: dict[str, Any],
) -> PacoteSaidaCanonica:
    return PacoteSaidaCanonica(
        versao=saida_base.versao,
        data_referencia=saida_base.data_referencia,
        extrato_passado=list(saida_base.extrato_passado),
        extrato_futuro=list(saida_base.extrato_futuro),
        switchings=list(saida_base.switchings),
        ranking_amostra=list(saida_base.ranking_amostra),
        lotes_ativos=list(saida_base.lotes_ativos),
        lotes_exauridos=list(saida_base.lotes_exauridos),
        recebidos_atuais=list(saida_base.recebidos_atuais),
        fechamento_atual=list(saida_base.fechamento_atual),
        resumo_recebidos=list(saida_base.resumo_recebidos),
        auditoria=auditoria_nova,
    )


def construir_saida_canonica_com_ledger_shadow_opcional(
    contexto: Any,
    *,
    versao: str = "V203",
    ativar_ledger_shadow: bool = False,
) -> PacoteSaidaCanonica:
    """Constrói saída canônica com bloco shadow opcional de ledger.

    Com ``ativar_ledger_shadow=False``, retorna exatamente a saída canônica
    operacional atual.

    Com ``ativar_ledger_shadow=True``, preserva todas as tabelas da saída
    operacional e acrescenta apenas ``auditoria['ledger_shadow_v37m']``.
    """
    saida_base = construir_saida_canonica(contexto, versao=versao)
    if not ativar_ledger_shadow:
        return saida_base

    quadro_futuro = _quadro_futuro_preferencial(contexto)
    mapa_central = _mapa_pagamentos_central(contexto)
    pacote_ledger_shadow = construir_pacote_ledger_temporal_shadow(
        quadro_futuro,
        mapa_central,
        contexto,
    )

    auditoria_nova = dict(saida_base.auditoria or {})
    auditoria_nova[BLOCO_AUDITORIA_LEDGER_SHADOW_V37M] = _montar_bloco_auditoria_ledger_shadow_v37m(
        saida_base,
        pacote_ledger_shadow,
    )

    return _copiar_saida_com_auditoria(saida_base, auditoria_nova)

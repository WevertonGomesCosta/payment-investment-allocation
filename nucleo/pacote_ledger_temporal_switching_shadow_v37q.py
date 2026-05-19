"""Conexão opcional do switching_canonico ao PacoteLedgerTemporal em modo shadow.

A V17-F0-V.3.7Q preserva o ledger operacional. O construtor legado continua
sendo a fonte efetiva dos eventos e do FIFO; o switching_canonico entra apenas
como bloco adicional de auditoria dentro do PacoteLedgerTemporal shadow.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Mapping

from nucleo.ledger_switching_canonico_shadow_v37q import (
    BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q,
    auditar_switching_canonico_ledger_shadow_v37q,
)
from nucleo.pacote_ledger_temporal import (
    PacoteLedgerTemporal,
    construir_pacote_ledger_temporal_shadow,
)


def construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q(
    quadro_futuro: Any,
    mapa_central: Any,
    contexto: Any,
    *,
    ativar_switching_canonico_shadow: bool = False,
    retorno_legado: Mapping[str, Any] | None = None,
) -> PacoteLedgerTemporal:
    """Constrói PacoteLedgerTemporal e, opcionalmente, anexa auditoria V3.7Q.

    Mesmo com ``ativar_switching_canonico_shadow=True``, os eventos temporais e
    o FIFO continuam vindo do retorno legado. O adaptador canônico não é usado
    como fonte operacional.
    """
    pacote = construir_pacote_ledger_temporal_shadow(
        quadro_futuro,
        mapa_central,
        contexto,
        modo_shadow=True,
        retorno_legado=retorno_legado,
    )

    if not ativar_switching_canonico_shadow:
        return pacote

    auditoria_nova = dict(pacote.auditoria_ledger_temporal or {})
    auditoria_nova[BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q] = (
        auditar_switching_canonico_ledger_shadow_v37q(contexto)
    )
    auditoria_nova["switching_canonico_shadow_v37q_ativado"] = True
    auditoria_nova["ledger_operacional_preservado_v37q"] = True
    auditoria_nova["fonte_operacional_ledger_v37q"] = "construir_ledger_temporal_conjunto_legado"
    auditoria_nova["promove_switching_canonico_para_ledger_v37q"] = False

    metadados_novos = dict(pacote.metadados_origem or {})
    metadados_novos["versao_microetapa_switching_canonico_shadow"] = "V17-F0-V.3.7Q"
    metadados_novos["switching_canonico_shadow_ativado"] = True
    metadados_novos["nao_promove_switching_canonico_para_ledger"] = True

    return replace(
        pacote,
        auditoria_ledger_temporal=auditoria_nova,
        metadados_origem=metadados_novos,
    )


__all__ = [
    "construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q",
]

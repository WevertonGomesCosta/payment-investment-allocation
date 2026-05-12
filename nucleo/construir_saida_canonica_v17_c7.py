from __future__ import annotations

from typing import Any

from nucleo.saida_canonica import PacoteSaidaCanonica, construir_saida_canonica
from nucleo.saida_canonica_switching_v17_c7 import integrar_switchings_materializados_saida_canonica_v17_f0_p1


def construir_saida_canonica_com_switching_v17_c7(contexto: Any, versao: str) -> PacoteSaidaCanonica:
    """Constrói saída canônica e integra switchings materializados da V17-F0-O.2."""
    saida_base = construir_saida_canonica(contexto, versao=versao)
    return integrar_switchings_materializados_saida_canonica_v17_f0_p1(saida_base, contexto)

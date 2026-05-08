from __future__ import annotations

from typing import Any

from nucleo.saida_canonica import PacoteSaidaCanonica, construir_saida_canonica
from nucleo.saida_canonica_switching_v17_c7 import integrar_switchings_ponte_saida_canonica


def construir_saida_canonica_com_switching_v17_c7(contexto: Any, versao: str) -> PacoteSaidaCanonica:
    """Constrói saída canônica e integra exclusivamente switchings via ponte V17-C7.

    Este construtor mantém a saída canônica original como base e aplica apenas
    a substituição controlada do atributo `switchings`. Pagamentos, valores,
    ranking, lotes, recebidos e fechamento são preservados da saída base.
    """
    saida_base = construir_saida_canonica(contexto, versao=versao)
    return integrar_switchings_ponte_saida_canonica(saida_base, contexto)

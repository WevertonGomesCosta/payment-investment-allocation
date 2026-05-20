"""Caminho opcional controlado da saída canônica com bloco temporal shadow.

V17-F0-V.4L promove a rota V4K para uma interface controlada por parâmetro,
mantendo o comportamento padrão sem bloco temporal shadow.
"""

from __future__ import annotations

from typing import Any

from nucleo.saida_canonica import PacoteSaidaCanonica, construir_saida_canonica
from nucleo.saida_canonica_temporal_shadow_v4k import construir_saida_canonica_com_temporal_shadow_v4k


def construir_saida_canonica_controlada_v4l(
    contexto: Any,
    *,
    versao: str = "V203",
    incluir_temporal_shadow: bool = False,
) -> PacoteSaidaCanonica:
    """Constrói a saída canônica por caminho controlado.

    Parâmetros
    ----------
    contexto:
        Contexto operacional já carregado.
    versao:
        Versão informada ao pacote de saída.
    incluir_temporal_shadow:
        Quando ``False`` preserva exatamente o construtor padrão atual.
        Quando ``True`` usa a rota opcional V4K e acrescenta apenas o bloco
        ``temporal_shadow_v4k`` à auditoria.
    """
    if incluir_temporal_shadow:
        return construir_saida_canonica_com_temporal_shadow_v4k(contexto, versao=versao)
    return construir_saida_canonica(contexto, versao=versao)

from __future__ import annotations

from dataclasses import replace
from typing import Any

from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida
from nucleo.ponte_renderizacao_switching_v17_c6 import renderizar_switchings_compativeis_saida
from nucleo.saida_canonica import PacoteSaidaCanonica


def integrar_switchings_ponte_saida_canonica(
    saida: PacoteSaidaCanonica,
    contexto: Any,
) -> PacoteSaidaCanonica:
    """Retorna uma cópia da saída canônica com apenas switchings preenchidos.

    Escopo V17-C7:
    - não altera pagamentos;
    - não altera bruto/imposto/líquido;
    - não altera ranking;
    - não altera motor;
    - não altera switching funcional;
    - usa somente a ponte V17-C6 para renderização observável.
    """
    pacote_pre_saida = montar_pacote_orquestrado_pre_saida(contexto)
    ponte = renderizar_switchings_compativeis_saida(pacote_pre_saida)
    switchings = list(ponte.switchings_compativeis_saida or [])

    auditoria = dict(saida.auditoria or {})
    auditoria["v17_c7_switching_ponte"] = {
        "status": "aplicada" if switchings else "sem_switchings_renderizados",
        "switchings_antes": len(saida.switchings or []),
        "switchings_depois": len(switchings),
        "origem": "pacote_orquestrado_pre_saida.estado_temporal_switching via ponte_renderizacao_switching_v17_c6",
        "altera_pagamentos": False,
        "altera_valores_bruto_imposto_liquido": False,
        "altera_ranking": False,
        "altera_motor": False,
    }

    return replace(
        saida,
        switchings=switchings,
        auditoria=auditoria,
    )

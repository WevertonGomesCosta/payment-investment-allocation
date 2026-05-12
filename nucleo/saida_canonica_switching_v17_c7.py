from __future__ import annotations

from dataclasses import replace
from typing import Any

from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2
from nucleo.saida_canonica import PacoteSaidaCanonica


def integrar_switchings_materializados_saida_canonica_v17_f0_p1(
    saida: PacoteSaidaCanonica,
    contexto: Any,
) -> PacoteSaidaCanonica:
    """Integra switchings observáveis na saída via materialização V17-F0-O.2."""
    eventos = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)
    switchings = [dict(evento) for evento in eventos if isinstance(evento, dict)]

    auditoria = dict(saida.auditoria or {})
    auditoria["v17_f0_p1_switching_oficial"] = {
        "status": "materializado_via_ledger_estado_temporal_v17_f0_o2" if switchings else "sem_switchings_materializados",
        "switchings_antes": len(saida.switchings or []),
        "switchings_depois": len(switchings),
        "origem": "materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)",
        "altera_pagamentos": False,
        "altera_valores_bruto_imposto_liquido": False,
        "altera_ranking": False,
        "altera_motor": False,
    }
    auditoria["v17_c7_switching_ponte"] = {
        "status": "nao_aplicada_v17_f0_p1",
        "switchings_antes": len(saida.switchings or []),
        "switchings_depois": len(switchings),
        "origem": "ponte_desativada_na_rota_oficial_v17_f0_p1",
        "altera_pagamentos": False,
        "altera_valores_bruto_imposto_liquido": False,
        "altera_ranking": False,
        "altera_motor": False,
    }

    return replace(saida, switchings=switchings, auditoria=auditoria)

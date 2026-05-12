from __future__ import annotations

from dataclasses import replace
from typing import Any

from nucleo.ledger_switching_estado_temporal_v17_f0_o2 import materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2
from nucleo.saida_canonica import PacoteSaidaCanonica


def _texto(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _numero(v: Any) -> float | None:
    t=_texto(v)
    if not t:
        return None
    try:
        return round(float(v),2)
    except Exception:
        pass
    try:
        t=t.replace("R$","").strip()
        if "," in t:
            t=t.replace(".","").replace(",", ".")
        return round(float(t),2)
    except Exception:
        return None


def _converter_evento_para_schema_renderizavel(evento: dict[str, Any]) -> dict[str, Any]:
    data_switching = _texto(evento.get("data_switching"))
    lote_origem = _texto(evento.get("lote_origem"))
    lote_destino = _texto(evento.get("lote_destino")) or _texto(evento.get("lote_pos_switching"))
    produto_destino = _texto(evento.get("produto_destino"))
    valor_liquido_origem = _numero(evento.get("valor_liquido_origem"))
    if valor_liquido_origem is None:
        valor_liquido_origem = _numero(evento.get("valor_liquido_migrado"))
    status_materializacao = _texto(evento.get("status_materializacao")) or "materializado_estado_temporal_v17_f0_p1_1"

    renderizado = dict(evento)
    renderizado.update(
        {
            "Data": data_switching,
            "Data sugerida": data_switching,
            "Lote origem": lote_origem,
            "Lote destino": lote_destino,
            "Destino": produto_destino,
            "Produto destino": produto_destino,
            "Produto destino switching": produto_destino,
            "Valor líquido origem": valor_liquido_origem,
            "Status": status_materializacao,
        }
    )
    return renderizado


def integrar_switchings_materializados_saida_canonica_v17_f0_p1(
    saida: PacoteSaidaCanonica,
    contexto: Any,
) -> PacoteSaidaCanonica:
    """Integra switchings observáveis na saída via materialização V17-F0-O.2."""
    eventos = materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)
    switchings = [_converter_evento_para_schema_renderizavel(dict(evento)) for evento in eventos if isinstance(evento, dict)]

    auditoria = dict(saida.auditoria or {})
    auditoria["v17_f0_p1_switching_oficial"] = {
        "status": "materializado_via_ledger_estado_temporal_v17_f0_o2" if switchings else "sem_switchings_materializados",
        "switchings_antes": len(saida.switchings or []),
        "switchings_depois": len(switchings),
        "origem": "materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)",
        "schema_renderizavel_preservado": True,
        "campos_renderizaveis_obrigatorios": [
            "Data",
            "Data sugerida",
            "Lote origem",
            "Lote destino",
            "Produto destino switching",
            "Valor líquido origem",
            "Status",
        ],
        "altera_pagamentos": False,
        "altera_valores_bruto_imposto_liquido": False,
        "altera_ranking": False,
        "altera_motor": False,
    }
    auditoria["v17_c7_switching_ponte"] = {
        "status": "nao_aplicada_v17_f0_p1_1",
        "switchings_antes": len(saida.switchings or []),
        "switchings_depois": len(switchings),
        "origem": "ponte_desativada_na_rota_oficial_v17_f0_p1_1",
        "altera_pagamentos": False,
        "altera_valores_bruto_imposto_liquido": False,
        "altera_ranking": False,
        "altera_motor": False,
    }

    return replace(saida, switchings=switchings, auditoria=auditoria)

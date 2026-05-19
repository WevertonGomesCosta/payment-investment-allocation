"""Auditoria shadow de switching_canonico conectado ao envelope do ledger.

V17-F0-V.3.7Q não promove o switching canônico como fonte operacional. Este
módulo apenas compara, dentro do fluxo shadow do ledger, as estruturas legadas
extraídas da aba bruta Switching com as estruturas canônicas da Etapa 3.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from nucleo.ledger_temporal_conjunto import (
    _eventos_switching_aba_operacional,
    _mapa_switchings_aba_operacional,
)
from nucleo.switching_canonico_ledger_shadow import (
    ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW,
    auditar_adaptador_switching_canonico_ledger_shadow,
    switching_canonico_para_eventos_ledger_shadow,
    switching_canonico_para_mapa_ledger_shadow,
)


BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q = "switching_canonico_ledger_shadow_v37q"


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _norm_data(valor: Any) -> str:
    if valor in (None, ""):
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    try:
        dt = pd.to_datetime(valor, errors="coerce")
        if pd.isna(dt):
            return _txt(valor)
        return dt.date().isoformat()
    except Exception:
        return _txt(valor)


def _norm_valor(valor: Any) -> str:
    if valor in (None, ""):
        return ""
    try:
        return f"{round(float(valor), 2):.2f}"
    except Exception:
        return _txt(valor)


def _normalizar_mapa(mapa: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalizado: dict[str, dict[str, Any]] = {}
    for lote, meta in (mapa or {}).items():
        normalizado[_txt(lote)] = {
            "lote_origem": _txt(meta.get("lote_origem")),
            "lote_pos_switching": _txt(meta.get("lote_pos_switching")),
            "data_switching": _norm_data(meta.get("data_switching")),
            "produto_destino": _txt(meta.get("produto_destino")),
            "valor_liquido_origem": _norm_valor(meta.get("valor_liquido_origem")),
            "status_switching": _txt(meta.get("status_switching")),
        }
    return normalizado


def _normalizar_eventos(eventos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalizados: list[dict[str, Any]] = []
    for evento in list(eventos or []):
        normalizados.append({
            "evento_switching_id": _txt(evento.get("evento_switching_id")),
            "evento_switching_id_legado_compat": _txt(evento.get("evento_switching_id_legado_compat")),
            "lote_origem": _txt(evento.get("lote_origem")),
            "lote_pos_switching": _txt(evento.get("lote_pos_switching")),
            "data_switching": _norm_data(evento.get("data_switching")),
            "produto_destino": _txt(evento.get("produto_destino")),
            "valor_liquido_origem": _norm_valor(evento.get("valor_liquido_origem")),
            "status_materializacao_passiva": _txt(evento.get("status_materializacao_passiva")),
        })
    return sorted(
        normalizados,
        key=lambda r: (
            r.get("data_switching", ""),
            r.get("lote_origem", ""),
            r.get("lote_pos_switching", ""),
            r.get("evento_switching_id_legado_compat") or r.get("evento_switching_id", ""),
        ),
    )


def _comparar_mapas(mapa_legado: dict[str, dict[str, Any]], mapa_shadow: dict[str, dict[str, Any]]) -> dict[str, Any]:
    legado = _normalizar_mapa(mapa_legado)
    shadow = _normalizar_mapa(mapa_shadow)
    lotes_legado = set(legado)
    lotes_shadow = set(shadow)

    divergencias: list[dict[str, Any]] = []
    for lote in sorted(lotes_legado & lotes_shadow):
        for campo in ["lote_pos_switching", "data_switching", "produto_destino", "valor_liquido_origem"]:
            if legado[lote].get(campo) != shadow[lote].get(campo):
                divergencias.append({
                    "lote_origem": lote,
                    "campo": campo,
                    "legado": legado[lote].get(campo),
                    "shadow": shadow[lote].get(campo),
                })

    return {
        "qtd_mapa_legado": len(legado),
        "qtd_mapa_shadow": len(shadow),
        "lotes_origem_apenas_legado": sorted(lotes_legado - lotes_shadow),
        "lotes_origem_apenas_shadow": sorted(lotes_shadow - lotes_legado),
        "divergencias_mapa": divergencias,
        "mapa_qtd_identica": len(legado) == len(shadow),
        "mapa_lotes_origem_identicos": lotes_legado == lotes_shadow,
        "mapa_campos_criticos_identicos": len(divergencias) == 0,
    }


def _comparar_eventos(eventos_legado: list[dict[str, Any]], eventos_shadow: list[dict[str, Any]]) -> dict[str, Any]:
    legado = _normalizar_eventos(eventos_legado)
    shadow = _normalizar_eventos(eventos_shadow)

    def chave(evento: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            evento.get("data_switching", ""),
            evento.get("lote_origem", ""),
            evento.get("lote_pos_switching", ""),
            evento.get("evento_switching_id_legado_compat") or evento.get("evento_switching_id", ""),
        )

    mapa_legado = {chave(evento): evento for evento in legado}
    mapa_shadow = {chave(evento): evento for evento in shadow}
    chaves_legado = set(mapa_legado)
    chaves_shadow = set(mapa_shadow)

    divergencias: list[dict[str, Any]] = []
    for ch in sorted(chaves_legado & chaves_shadow):
        ev_legado = mapa_legado[ch]
        ev_shadow = mapa_shadow[ch]
        for campo in ["produto_destino", "valor_liquido_origem", "status_materializacao_passiva"]:
            if ev_legado.get(campo) != ev_shadow.get(campo):
                divergencias.append({
                    "chave": "|".join(ch),
                    "campo": campo,
                    "legado": ev_legado.get(campo),
                    "shadow": ev_shadow.get(campo),
                })

    return {
        "qtd_eventos_legado": len(legado),
        "qtd_eventos_shadow": len(shadow),
        "eventos_apenas_legado": ["|".join(ch) for ch in sorted(chaves_legado - chaves_shadow)],
        "eventos_apenas_shadow": ["|".join(ch) for ch in sorted(chaves_shadow - chaves_legado)],
        "divergencias_eventos": divergencias,
        "eventos_qtd_identica": len(legado) == len(shadow),
        "eventos_chaves_equivalentes": chaves_legado == chaves_shadow,
        "eventos_campos_criticos_identicos": len(divergencias) == 0,
    }


def auditar_switching_canonico_ledger_shadow_v37q(contexto: Any) -> dict[str, Any]:
    """Compara switching legado e canônico dentro do fluxo shadow do ledger."""
    mapa_legado = _mapa_switchings_aba_operacional(contexto)
    eventos_legado = _eventos_switching_aba_operacional(contexto)
    mapa_shadow = switching_canonico_para_mapa_ledger_shadow(contexto)
    eventos_shadow = switching_canonico_para_eventos_ledger_shadow(contexto)

    auditoria_adaptador = auditar_adaptador_switching_canonico_ledger_shadow(contexto)
    comparacao_mapa = _comparar_mapas(mapa_legado, mapa_shadow)
    comparacao_eventos = _comparar_eventos(eventos_legado, eventos_shadow)

    comparacao_mapa_ok = bool(
        comparacao_mapa["mapa_qtd_identica"]
        and comparacao_mapa["mapa_lotes_origem_identicos"]
        and comparacao_mapa["mapa_campos_criticos_identicos"]
    )
    comparacao_eventos_ok = bool(
        comparacao_eventos["eventos_qtd_identica"]
        and comparacao_eventos["eventos_chaves_equivalentes"]
        and comparacao_eventos["eventos_campos_criticos_identicos"]
    )
    isolamento_ok = bool(
        auditoria_adaptador.get("nao_le_pacote_planilha")
        and auditoria_adaptador.get("nao_le_quadros_brutos")
        and auditoria_adaptador.get("nao_reabre_excel")
        and auditoria_adaptador.get("nao_altera_ledger_operacional")
        and auditoria_adaptador.get("nao_altera_saida_canonica")
    )

    validacao_ok = bool(comparacao_mapa_ok and comparacao_eventos_ok and isolamento_ok)

    return {
        "modo_shadow": True,
        "origem": "nucleo.ledger_switching_canonico_shadow_v37q",
        "fonte_operacional_ledger": "aba_switching_operacional_legado",
        "fonte_shadow": ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW,
        "validacao_ok": validacao_ok,
        "comparacao_mapa_legado_vs_canonico": comparacao_mapa_ok,
        "comparacao_eventos_legado_vs_canonico": comparacao_eventos_ok,
        "isolamento_shadow_ok": isolamento_ok,
        "ledger_operacional_preservado": True,
        "ledger_operacional_ainda_usa_caminho_legado": True,
        "promove_switching_canonico_para_ledger": False,
        "saida_canonica_preservada": True,
        **auditoria_adaptador,
        **comparacao_mapa,
        **comparacao_eventos,
    }


__all__ = [
    "BLOCO_AUDITORIA_SWITCHING_CANONICO_LEDGER_SHADOW_V37Q",
    "auditar_switching_canonico_ledger_shadow_v37q",
]

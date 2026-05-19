"""Adaptador shadow entre switching_canonico da Etapa 3 e o ledger legado.

V17-F0-V.3.7P não altera o ledger operacional. Este módulo apenas materializa,
em modo shadow, as mesmas estruturas auxiliares que o ledger hoje extrai da aba
bruta ``Switching``.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW = "switching_canonico_etapa3"


def _txt(valor: Any) -> str:
    return str(valor or "").strip()


def _norm(valor: Any) -> str:
    return _txt(valor).lower()


def _round(valor: Any) -> Any:
    try:
        return round(float(valor), 2)
    except Exception:
        return ""


def _normalizar_data_comparavel(valor: Any) -> Any:
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass
    if hasattr(valor, "date") and not isinstance(valor, str):
        try:
            if hasattr(valor, "hour"):
                return valor.date()
        except Exception:
            pass
    if isinstance(valor, str):
        texto = valor.strip()
        if _norm(texto) in {"", "n/d", "nd", "não determinado", "nao determinado", "none"}:
            return None
        for dayfirst in (False, True):
            try:
                dt = pd.to_datetime(texto, errors="raise", dayfirst=dayfirst)
                if pd.isna(dt):
                    continue
                return dt.date()
            except Exception:
                continue
        return None
    try:
        dt = pd.to_datetime(valor, errors="raise")
        if pd.isna(dt):
            return None
        return dt.date()
    except Exception:
        return None


def _primeira_data_valida(row: dict[str, Any], colunas: list[str]) -> Any:
    for coluna in colunas:
        valor = row.get(coluna)
        if _normalizar_data_comparavel(valor) is not None:
            return valor
    return None


def _switching_canonico_do_contexto(contexto: Any) -> pd.DataFrame:
    dados_operacionais = getattr(contexto, "dados_operacionais", None) if contexto is not None else None
    switching_canonico = getattr(dados_operacionais, "switching_canonico", None) if dados_operacionais is not None else None
    if isinstance(switching_canonico, pd.DataFrame):
        return switching_canonico
    return pd.DataFrame()


def _ordem_compat(row: dict[str, Any], indice: Any) -> int:
    ordem = row.get("ordem_planilha_switching")
    try:
        if ordem not in (None, "") and not pd.isna(ordem):
            return max(int(ordem) - 1, 0)
    except Exception:
        pass
    try:
        return int(indice)
    except Exception:
        return 0


def _id_evento_legado_compat(row: dict[str, Any], indice: Any, lote_origem: str, lote_destino: str, data_switching_norm: Any) -> str:
    evento_informado = _txt(row.get("evento_switching_id"))
    if evento_informado:
        return evento_informado
    ordem = _ordem_compat(row, indice)
    return f"swop::{data_switching_norm}::{lote_origem}::{lote_destino or ordem}"


def _id_evento_canonico(row: dict[str, Any], indice: Any, lote_origem: str, lote_destino: str, data_switching_norm: Any) -> str:
    switching_id = _txt(row.get("switching_id"))
    if switching_id:
        return switching_id
    return _id_evento_legado_compat(row, indice, lote_origem, lote_destino, data_switching_norm)


def _lote_pos_switching(row: dict[str, Any], indice: Any, lote_origem: str) -> str:
    lote_destino = _txt(row.get("lote_destino") or row.get("lote_pos_switching"))
    if lote_destino:
        return lote_destino
    ordem = _ordem_compat(row, indice)
    return f"lote_pos_switching_audit::{lote_origem}::{ordem}"


def _data_switching_canonica(row: dict[str, Any]) -> Any:
    return _primeira_data_valida(
        row,
        ["data_switching", "data_aplicacao", "data_recebimento"],
    )


def switching_canonico_para_mapa_ledger_shadow(contexto: Any) -> dict[str, dict[str, Any]]:
    """Converte switching_canonico em mapa por lote de origem para auditoria shadow.

    Não lê ``pacote_planilha``, não acessa ``quadros_brutos`` e não reabre Excel.
    """
    df = _switching_canonico_do_contexto(contexto)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return {}

    mapa: dict[str, dict[str, Any]] = {}
    for indice, row in df.iterrows():
        registro = row.to_dict()
        lote_origem = _txt(registro.get("lote_origem"))
        if not lote_origem:
            continue

        data_switching = _data_switching_canonica(registro)
        data_switching_norm = _normalizar_data_comparavel(data_switching)
        if data_switching_norm is None:
            continue

        lote_destino = _txt(registro.get("lote_destino") or registro.get("lote_pos_switching"))
        meta = {
            "lote_origem": lote_origem,
            "data_switching": data_switching,
            "produto_destino": _txt(registro.get("produto_destino")),
            "valor_liquido_origem": _round(registro.get("valor_liquido_origem")),
            "status_switching": _txt(registro.get("status")) or "classificado_promovido",
            "origem_mapa_migracao": ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW,
            "lote_pos_switching": lote_destino,
            "switching_id_canonico": _txt(registro.get("switching_id")),
            "ordem_planilha_switching": registro.get("ordem_planilha_switching"),
        }

        atual = mapa.get(lote_origem)
        if atual is None:
            mapa[lote_origem] = meta
            continue

        data_atual_norm = _normalizar_data_comparavel(atual.get("data_switching"))
        if data_atual_norm is None or data_switching_norm > data_atual_norm:
            mapa[lote_origem] = meta

    return mapa


def switching_canonico_para_eventos_ledger_shadow(contexto: Any) -> list[dict[str, Any]]:
    """Converte switching_canonico em eventos POS compatíveis com auditoria do ledger.

    Não lê ``pacote_planilha``, não acessa ``quadros_brutos`` e não reabre Excel.
    """
    df = _switching_canonico_do_contexto(contexto)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []

    eventos: list[dict[str, Any]] = []
    for indice, row in df.iterrows():
        registro = row.to_dict()
        lote_origem = _txt(registro.get("lote_origem"))
        if not lote_origem:
            continue

        data_switching = _data_switching_canonica(registro)
        data_switching_norm = _normalizar_data_comparavel(data_switching)
        if data_switching_norm is None:
            continue

        lote_destino = _txt(registro.get("lote_destino") or registro.get("lote_pos_switching"))
        lote_pos = _lote_pos_switching(registro, indice, lote_origem)
        eventos.append({
            "evento_switching_id": _id_evento_canonico(registro, indice, lote_origem, lote_destino, data_switching_norm),
            "evento_switching_id_legado_compat": _id_evento_legado_compat(registro, indice, lote_origem, lote_destino, data_switching_norm),
            "switching_id_canonico": _txt(registro.get("switching_id")),
            "lote_origem": lote_origem,
            "data_switching": data_switching_norm,
            "produto_destino": _txt(registro.get("produto_destino")),
            "valor_liquido_origem": _round(registro.get("valor_liquido_origem")),
            "lote_pos_switching": lote_pos,
            "status_materializacao_passiva": "materializado_passivo",
            "origem_mapa_migracao": ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW,
            "ordem_planilha_switching": registro.get("ordem_planilha_switching"),
        })

    return eventos


def auditar_adaptador_switching_canonico_ledger_shadow(contexto: Any) -> dict[str, Any]:
    df = _switching_canonico_do_contexto(contexto)
    mapa = switching_canonico_para_mapa_ledger_shadow(contexto)
    eventos = switching_canonico_para_eventos_ledger_shadow(contexto)
    return {
        "adaptador": "switching_canonico_ledger_shadow",
        "origem": ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW,
        "switching_canonico_presente": isinstance(df, pd.DataFrame),
        "switching_canonico_linhas": int(len(df)) if isinstance(df, pd.DataFrame) else 0,
        "qtd_mapa_switchings": int(len(mapa)),
        "qtd_eventos_switching": int(len(eventos)),
        "nao_le_pacote_planilha": True,
        "nao_le_quadros_brutos": True,
        "nao_reabre_excel": True,
        "nao_altera_ledger_operacional": True,
        "nao_altera_saida_canonica": True,
    }


__all__ = [
    "ORIGEM_SWITCHING_CANONICO_LEDGER_SHADOW",
    "auditar_adaptador_switching_canonico_ledger_shadow",
    "switching_canonico_para_eventos_ledger_shadow",
    "switching_canonico_para_mapa_ledger_shadow",
]

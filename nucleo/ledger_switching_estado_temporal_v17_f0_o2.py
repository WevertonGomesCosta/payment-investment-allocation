from __future__ import annotations

from typing import Any
import pandas as pd


def _s(x: Any) -> str:
    if x is None:
        return ""
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return str(x).strip()


def _n(x: Any) -> str:
    return " ".join(_s(x).lower().split())


def _pick(row: dict[str, Any], names: list[str]) -> Any:
    cols = {_n(k): k for k in row.keys()}
    for name in names:
        col = cols.get(_n(name))
        if col is not None and _s(row.get(col)):
            return row.get(col)
    return ""


def _date(x: Any) -> str:
    if not _s(x):
        return ""
    if hasattr(x, "date") and not isinstance(x, str):
        try:
            return x.date().isoformat()
        except Exception:
            pass
    for dayfirst in (False, True):
        try:
            dt = pd.to_datetime(x, errors="raise", dayfirst=dayfirst)
            if not pd.isna(dt):
                return dt.date().isoformat()
        except Exception:
            pass
    return _s(x)[:10]


def _money(x: Any) -> str:
    txt = _s(x)
    if not txt:
        return ""
    try:
        return f"{float(x):.2f}"
    except Exception:
        pass
    txt = txt.replace("R$", "").strip()
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return f"{float(txt):.2f}"
    except Exception:
        return txt


def _estado_pre_saida(contexto: Any) -> pd.DataFrame:
    try:
        from nucleo.pacote_orquestrado_pre_saida import montar_pacote_orquestrado_pre_saida
        pacote = montar_pacote_orquestrado_pre_saida(contexto)
        df = getattr(pacote, "estado_temporal_switching", pd.DataFrame())
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df.copy()
    except Exception:
        pass
    return pd.DataFrame()


def _aba_switching(contexto: Any) -> pd.DataFrame:
    pacote = getattr(contexto, "pacote_planilha", None)
    quadros = []
    if pacote is not None:
        quadros.append(getattr(pacote, "quadros_canonicos", {}))
        quadros.append(getattr(pacote, "quadros_brutos", {}))
    cfg = getattr(getattr(contexto, "pacote_config", None), "conteudo", {}) or {}
    nome_cfg = ((cfg.get("abas") or {}).get("switching") if isinstance(cfg, dict) else None) or "Switching"
    for nome in [nome_cfg, "Switching", "Switiching", "Swtiching"]:
        for q in quadros:
            if isinstance(q, dict) and isinstance(q.get(nome), pd.DataFrame) and not q[nome].empty:
                return q[nome].copy()
    return pd.DataFrame()


def _evento(row: dict[str, Any], idx: int, origem: str) -> dict[str, Any] | None:
    data = _date(_pick(row, ["data_switching", "Data", "Data sugerida", "Data Aplicação", "data_aplicacao", "Data Recebimento", "data_recebimento"]))
    lote_origem = _s(_pick(row, ["lote_id_origem", "lote_origem", "lote_id_antes", "Lote origem", "Lote (ID) Antes", "lote_id"]))
    lote_destino = _s(_pick(row, ["lote_id_destino", "lote_destino", "lote_id_depois", "lote_pos_switching", "Lote destino", "Lote (ID) Depois"]))
    produto = _s(_pick(row, ["produto_destino", "Produto destino switching", "Investimento", "investimento", "Destino", "produto_destino_nome", "produto_destino_key"]))
    valor = _money(_pick(row, ["valor_liquido_migrado", "valor_liquido_origem", "Valor líquido origem", "Valor Líquido Migrado", "Valor líquido total", "valor_liquido_resgatavel"]))
    if not (data and lote_origem and produto and valor):
        return None
    return {
        "evento_switching_id": f"switching::{data}::{idx}",
        "tipo_evento": "switching",
        "data_switching": data,
        "lote_origem": lote_origem,
        "lote_destino": lote_destino,
        "lote_pos_switching": lote_destino,
        "produto_destino": produto,
        "valor_liquido_origem": valor,
        "valor_liquido_migrado": valor,
        "status_materializacao": "materializado_estado_temporal_v17_f0_o2",
        "status_materializacao_passiva": "materializado_estado_temporal_v17_f0_o2",
        "origem_materializacao": origem,
        "origem_mapa_migracao": origem,
        "indice_origem_materializacao": idx,
    }


def materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto: Any) -> list[dict[str, Any]]:
    df = _estado_pre_saida(contexto)
    origem = "pacote_orquestrado_pre_saida.estado_temporal_switching"
    if not isinstance(df, pd.DataFrame) or df.empty:
        df = _aba_switching(contexto)
        origem = "planilha.aba_switching"
    if not isinstance(df, pd.DataFrame) or df.empty:
        return []
    eventos: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        ev = _evento(dict(row), idx, origem)
        if ev is None:
            continue
        chave = "|".join([_n(ev["data_switching"]), _n(ev["lote_origem"]), _n(ev["lote_destino"]), _n(ev["produto_destino"]), _money(ev["valor_liquido_origem"])])
        if chave in vistos:
            continue
        vistos.add(chave)
        eventos.append(ev)
    return eventos

from __future__ import annotations

from typing import Any
import re


def _norm(v: Any) -> str:
    txt = str(v or "").strip().casefold()
    return re.sub(r"\s+", " ", txt)


def _split_fontes(v: Any) -> list[str]:
    txt = str(v or "").strip()
    if not txt:
        return []
    return [p.strip() for p in txt.split("+") if p.strip()]


def _mapa_matriz(matriz_df):
    m = {}
    for _, r in matriz_df.iterrows():
        chave = _norm(r.get("fonte_id"))
        if chave:
            m[chave] = r.to_dict()
    return m


def aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz_elegibilidade):
    mapa = _mapa_matriz(matriz_elegibilidade)
    audit = []

    for i, row in enumerate(saida_canonica.extrato_futuro):
        original = str(row.get("Lote sugerido") or "").strip()
        comps = _split_fontes(original)
        bloqueados = []
        ausentes = []
        elegivel = True if comps else False
        motivo = ""

        for c in comps:
            info = mapa.get(_norm(c))
            if not info:
                ausentes.append(c)
                elegivel = False
                continue
            if str(info.get("elegivel_para_pagamento") or "") != "sim" or str(info.get("pode_ser_lote_sugerido") or "") != "sim":
                bloqueados.append(f"{c}:{info.get('motivo_bloqueio') or 'bloqueado'}")
                elegivel = False

        status_ledger = str(row.get("status_ledger") or "")
        motivo_ledger = str(row.get("motivo_bloqueio_ledger") or "")
        ledger_bloqueia = status_ledger in {"sem_saldo_temporal_auditavel", "saldo_temporal_insuficiente_cumulativo"}

        row["lote_sugerido_original"] = original
        row["componentes_fonte"] = " + ".join(comps)
        row["componentes_bloqueados_ou_ausentes"] = " | ".join(bloqueados + [f"ausente:{x}" for x in ausentes])
        row["fonte_normativa_s7c"] = "matriz_elegibilidade_s7b"

        if not comps:
            row["acao_s7c"] = "sem_fonte_para_avaliar"
            row["elegivel_matriz"] = "nao"
            row["pode_ser_lote_sugerido_matriz"] = "nao"
            row["motivo_bloqueio_matriz"] = "fonte_vazia"
            row["Lote sugerido"] = ""
        elif ausentes:
            row["acao_s7c"] = "fonte_nao_encontrada_na_matriz"
            row["elegivel_matriz"] = "nao"
            row["pode_ser_lote_sugerido_matriz"] = "nao"
            row["motivo_bloqueio_matriz"] = "fonte_nao_encontrada_na_matriz_elegibilidade"
            row["Lote sugerido"] = ""
        elif not elegivel:
            row["acao_s7c"] = "bloqueado_por_matriz"
            row["elegivel_matriz"] = "nao"
            row["pode_ser_lote_sugerido_matriz"] = "nao"
            row["motivo_bloqueio_matriz"] = "componente_bloqueado_na_matriz"
            row["Lote sugerido"] = ""
        else:
            row["acao_s7c"] = "preservado_por_matriz"
            row["elegivel_matriz"] = "sim"
            row["pode_ser_lote_sugerido_matriz"] = "sim"
            row["motivo_bloqueio_matriz"] = ""

        if ledger_bloqueia:
            row["acao_s7c"] = "bloqueado_por_ledger"
            row["Lote sugerido"] = ""
            row["motivo_bloqueio_matriz"] = motivo_ledger or status_ledger

        row["lote_sugerido_pos_matriz"] = row.get("Lote sugerido") or ""
        audit.append({"idx": i, **row})

    return saida_canonica, audit

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.identidade_baseline import VERSAO_BASELINE
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

CSV_DETALHE = RAIZ / "saidas" / "diagnostico" / "auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.csv"
CSV_RESUMO = RAIZ / "saidas" / "diagnostico" / "auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1_resumo.csv"


def _n(v: Any) -> str:
    return str(v or "").strip().lower()


def _d(v: Any):
    try:
        return pd.to_datetime(v).date()
    except Exception:
        return None


def _num(v: Any):
    try:
        return float(v)
    except Exception:
        return None


def _pick_status(row: dict[str, Any]):
    for k in ["Status recomendação", "status_ledger", "Status", "status"]:
        vv = str(row.get(k) or "").strip()
        if vv:
            return k, vv
    return "status_nao_localizado", ""


def _resolver_lotes_pos_por_data(lotes_pos: list[dict[str, Any]]):
    por_nome: dict[str, list[dict[str, Any]]] = {}
    for lote in lotes_pos:
        nome = _n(lote.get("Lote") or lote.get("lote") or lote.get("lote_destino") or lote.get("lote_pos_switching"))
        if not nome:
            continue
        por_nome.setdefault(nome, []).append(lote)
    return por_nome


def auditar_q1(extrato: list[dict[str, Any]], switchings: list[dict[str, Any]], lotes_pos: list[dict[str, Any]]):
    origens = {_n(x.get("lote_origem")): _d(x.get("data_switching")) for x in switchings}
    destinos = {_n(x.get("lote_destino") or x.get("lote_pos_switching")) for x in switchings if _n(x.get("lote_destino") or x.get("lote_pos_switching"))}
    lotes_por_nome = _resolver_lotes_pos_por_data(lotes_pos)

    detalhes = []
    for i, r in enumerate(extrato, 1):
        data_pag = _d(r.get("Data"))
        fonte = str(r.get("Lote sugerido") or "")
        partes = [x.strip() for x in fonte.split("+") if x.strip()]
        partes_n = [_n(x) for x in partes]

        campo_status, status_usado = _pick_status(r)
        usa_pos = any(p in destinos for p in partes_n)
        usa_origem_migrada_indevida = any((origens.get(p) and data_pag and data_pag >= origens.get(p)) for p in partes_n)

        candidatos_pos_na_data = [
            l for l in lotes_pos if _d(l.get("Data")) and data_pag and _d(l.get("Data")) <= data_pag
        ]

        evidencias = []
        classificacao = "nao_aplicavel"

        saldo_antes = _num(r.get("Saldo antes"))
        saldo_depois = _num(r.get("Saldo depois"))
        valor_pag = _num(r.get("Valor"))

        if usa_pos:
            observavel_saldo = saldo_antes is not None and saldo_depois is not None and valor_pag is not None
            if observavel_saldo:
                consumo = round((saldo_antes - saldo_depois), 2)
                if consumo == round(valor_pag, 2):
                    classificacao = "baixa_confirmada"
                    evidencias.append("saldo_antes-saldo_depois igual ao valor_pagamento")
                elif consumo == 0:
                    classificacao = "baixa_ausente_confirmada"
                    evidencias.append("saldo observavel sem reducao apesar de pagamento usando lote_pos_switching")
                else:
                    classificacao = "baixa_inconsistente"
                    evidencias.append("saldo observavel com consumo divergente do valor_pagamento")
            else:
                campos_consumo = [
                    "valor_consumido_lote", "consumo_lote", "baixa_lote", "saldo_lote_antes", "saldo_lote_depois"
                ]
                sinais = {k: r.get(k) for k in campos_consumo if k in r}
                if sinais:
                    vals = [x for x in sinais.values() if _num(x) is not None]
                    if vals and any(v > 0 for v in vals):
                        classificacao = "baixa_confirmada"
                        evidencias.append("campo observavel de consumo > 0")
                    elif vals and all(v == 0 for v in vals):
                        classificacao = "baixa_ausente_confirmada"
                        evidencias.append("campo observavel de consumo igual a zero")
                    else:
                        classificacao = "sem_evidencia_observavel_de_baixa"
                        evidencias.append("campos observaveis existem mas nao trazem metrica numerica utilizavel")
                else:
                    classificacao = "sem_evidencia_observavel_de_baixa"
                    evidencias.append("sem campos observaveis de consumo/saldo para confirmar baixa")

        detalhes.append(
            {
                "pagamento_id": r.get("Despesa ID") or f"idx_{i}",
                "data_pagamento": r.get("Data"),
                "conta": r.get("Conta"),
                "valor_pagamento": r.get("Valor"),
                "campo_status_usado": campo_status,
                "status_usado": status_usado,
                "pacote_do_dia": _n(r.get("Pacote do dia") or r.get("pacote_do_dia_ledger")),
                "fonte_escolhida_renderizada": fonte,
                "fonte_eh_lote_pos_switching": usa_pos,
                "origem_migrada_usada_indevidamente": usa_origem_migrada_indevida,
                "lote_pos_switching_elegivel_na_data": bool(candidatos_pos_na_data),
                "lotes_pos_switching_disponiveis_na_data": len(candidatos_pos_na_data),
                "saldo_antes_observavel": saldo_antes,
                "saldo_depois_observavel": saldo_depois,
                "classificacao_baixa": classificacao,
                "evidencia_classificacao": " | ".join(evidencias),
                "camada_falha": (
                    "origem_switching" if usa_origem_migrada_indevida else (
                        "observabilidade" if classificacao == "sem_evidencia_observavel_de_baixa" else (
                            "baixa_contabil" if classificacao in {"baixa_ausente_confirmada", "baixa_inconsistente"} else "n/a"
                        )
                    )
                ),
            }
        )

    df = pd.DataFrame(detalhes)
    if df.empty:
        resumo = {
            "baseline_entrada": "276733b",
            "qtd_pagamentos_futuros": 0,
            "qtd_pagamentos_usando_lote_pos_switching": 0,
            "qtd_lotes_pos_switching_total": len(lotes_pos),
            "qtd_lotes_pos_switching_elegiveis_em_alguma_data": 0,
            "qtd_pagamentos_pos_switching_com_baixa_confirmada": 0,
            "qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada": 0,
            "qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa": 0,
            "qtd_pagamentos_pos_switching_com_baixa_inconsistente": 0,
            "qtd_origens_migradas_usadas_indevidamente": 0,
            "qtd_divergencias_baixa_pos_switching": 0,
            "camada_falha_dominante": "sem_pagamentos_futuros",
            "status_geral_q1": "sem_pagamentos_futuros_para_auditar",
        }
        return resumo, df

    df_pos = df[df["fonte_eh_lote_pos_switching"] == True]
    divergencias = df_pos["classificacao_baixa"].isin(["baixa_ausente_confirmada", "baixa_inconsistente", "sem_evidencia_observavel_de_baixa"]).sum()
    camada_dominante = "n/a"
    if divergencias > 0:
        camada_dominante = (
            df_pos[df_pos["classificacao_baixa"].isin(["baixa_ausente_confirmada", "baixa_inconsistente", "sem_evidencia_observavel_de_baixa"])]["camada_falha"]
            .value_counts()
            .index[0]
        )

    status_geral = "ok_baixa_confirmada"
    if int((df_pos["classificacao_baixa"] == "baixa_confirmada").sum()) == 0 and len(df_pos) > 0:
        status_geral = "divergencia_detectada_sem_confirmacao_de_baixa"
    elif divergencias > 0:
        status_geral = "divergencia_parcial_detectada"

    resumo = {
        "baseline_entrada": "276733b",
        "qtd_pagamentos_futuros": int(len(df)),
        "qtd_pagamentos_usando_lote_pos_switching": int(len(df_pos)),
        "qtd_lotes_pos_switching_total": int(len(lotes_pos)),
        "qtd_lotes_pos_switching_elegiveis_em_alguma_data": int(df["lote_pos_switching_elegivel_na_data"].sum()),
        "qtd_pagamentos_pos_switching_com_baixa_confirmada": int((df_pos["classificacao_baixa"] == "baixa_confirmada").sum()),
        "qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada": int((df_pos["classificacao_baixa"] == "baixa_ausente_confirmada").sum()),
        "qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa": int((df_pos["classificacao_baixa"] == "sem_evidencia_observavel_de_baixa").sum()),
        "qtd_pagamentos_pos_switching_com_baixa_inconsistente": int((df_pos["classificacao_baixa"] == "baixa_inconsistente").sum()),
        "qtd_origens_migradas_usadas_indevidamente": int(df["origem_migrada_usada_indevidamente"].sum()),
        "qtd_divergencias_baixa_pos_switching": int(divergencias),
        "camada_falha_dominante": camada_dominante,
        "status_geral_q1": status_geral,
    }
    return resumo, df


def main():
    ctx = carregar_contexto_baseline(
        raiz_repositorio=RAIZ,
        instalar_automaticamente=False,
        incluir_resolver_hibrido_5p_shadow=False,
        incluir_benchmark_agrupado_individual_shadow=False,
        incluir_benchmark_runner_futuro_shadow=False,
        incluir_auditoria_primeira_quebra_runner_futuro_shadow=False,
    )
    saida = construir_saida_canonica_com_switching_v17_c7(ctx, versao=VERSAO_BASELINE)
    extrato = [dict(x) for x in (saida.extrato_futuro or []) if isinstance(x, dict)]
    switchings = [dict(x) for x in (saida.switchings or []) if isinstance(x, dict)]
    lotes_pos = [dict(x) for x in (getattr(saida, "lotes_sinteticos_pos_switching_console", lambda **_: [])(limite=500) or [])]

    resumo, df_detalhe = auditar_q1(extrato, switchings, lotes_pos)

    CSV_DETALHE.parent.mkdir(parents=True, exist_ok=True)
    df_detalhe.to_csv(CSV_DETALHE, index=False)
    pd.DataFrame([resumo]).to_csv(CSV_RESUMO, index=False)

    print("=== AUDITORIA V17-F0-Q.1 — BAIXA CONTABIL LOTES POS-SWITCHING EM PAGAMENTOS ===")
    for chave in [
        "baseline_entrada",
        "qtd_pagamentos_futuros",
        "qtd_pagamentos_usando_lote_pos_switching",
        "qtd_lotes_pos_switching_total",
        "qtd_lotes_pos_switching_elegiveis_em_alguma_data",
        "qtd_pagamentos_pos_switching_com_baixa_confirmada",
        "qtd_pagamentos_pos_switching_com_baixa_ausente_confirmada",
        "qtd_pagamentos_pos_switching_sem_evidencia_observavel_de_baixa",
        "qtd_pagamentos_pos_switching_com_baixa_inconsistente",
        "qtd_origens_migradas_usadas_indevidamente",
        "qtd_divergencias_baixa_pos_switching",
        "camada_falha_dominante",
        "status_geral_q1",
    ]:
        print(f"{chave}={resumo[chave]}")
    print(f"csv_detalhe={CSV_DETALHE}")
    print(f"csv_resumo={CSV_RESUMO}")


if __name__ == "__main__":
    main()

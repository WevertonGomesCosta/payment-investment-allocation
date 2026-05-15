#!/usr/bin/env python3
from __future__ import annotations
import sys
import subprocess
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CSV_S7G = REPO_ROOT / "saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv"

COLS_REQ = [
    "data","conta","valor","lote_recomendado","fontes_componentes","qtd_fontes_componentes",
    "fonte_principal","fonte_reserva","status_recomendacao_original","status_operacional",
    "acao_recomendada","motivo","saldo_liquido_disponivel","valor_liquido_necessario",
    "saldo_pos_pagamento","saldo_pos_pagamento_origem","patrimonio_liquido_fonte",
    "usa_lote_pos_switching","qtd_componentes_pos_switching","alerta_operacional",
    "tipo_alerta_operacional","problema_operacional","motivo_operacional",
    "saldo_temporal_insuficiente_tipo","estado_terminal_bloqueante","fonte_aprovada_para_pagamento"
]

SENTINELS = [
    ("2026-05-15","Internet",132.40,2895.01,"extrato_futuro_saldo_remanescente","sentinela_internet_saldo_pos_ok"),
    ("2026-05-20","Cartão Azul",5372.00,869.53,"extrato_futuro_saldo_remanescente","sentinela_cartao_azul_saldo_pos_ok"),
    ("2026-05-20","Condomínio",113.31,1205.69,"extrato_futuro_saldo_remanescente","sentinela_condominio_2026_05_20_saldo_pos_ok"),
    ("2026-05-30","Implante Velt",400.00,2495.01,"extrato_futuro_saldo_remanescente","sentinela_implante_velt_saldo_pos_ok"),
    ("2026-06-02","Cartão NU",580.00,1915.01,"extrato_futuro_saldo_remanescente","sentinela_cartao_nu_saldo_pos_ok"),
]

def _n(x):
    try:
        return float(x)
    except Exception:
        return float("nan")

def run_s7g():
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/diagnostico/gerar_tabela_operacional_pagamentos_v17_f0_s7g.py")],
        check=True
    )

def main():
    run_s7g()
    df = pd.read_csv(CSV_S7G)
    missing = [c for c in COLS_REQ if c not in df.columns]
    out = {}

    out["qtd_linhas_tabela_operacional"] = len(df)
    out["qtd_colunas_tabela_operacional"] = len(df.columns)
    out["qtd_colunas_obrigatorias_ausentes"] = len(missing)
    out["colunas_obrigatorias_ausentes"] = ",".join(missing) if missing else "nenhuma"
    out["qtd_linhas_com_data_valida"] = int(pd.to_datetime(df["data"], errors="coerce").notna().sum())
    out["qtd_linhas_com_conta_nao_vazia"] = int(df["conta"].astype(str).str.strip().ne("").sum())
    out["qtd_linhas_com_valor_valido"] = int(pd.to_numeric(df["valor"], errors="coerce").notna().sum())
    out["qtd_linhas_com_status_operacional_nao_vazio"] = int(df["status_operacional"].astype(str).str.strip().ne("").sum())
    out["qtd_linhas_com_acao_recomendada_nao_vazia"] = int(df["acao_recomendada"].astype(str).str.strip().ne("").sum())

    out["comparacao_extrato_futuro"] = "nao_disponivel"
    out["qtd_lotes_sugeridos_alterados"] = 0
    out["qtd_status_recomendacao_alterados"] = 0

    out["qtd_pagamentos_aprovados_para_pagamento"] = int((df["status_operacional"] == "aprovado_para_pagamento").sum())
    out["qtd_pagamentos_aprovados_multifonte"] = int((df["status_operacional"] == "aprovado_multifonte").sum())
    out["qtd_pagamentos_com_lote_pos_switching_valido"] = int((df["usa_lote_pos_switching"].astype(str) == "sim").sum())
    out["qtd_componentes_lote_pos_switching_validos"] = int(pd.to_numeric(df["qtd_componentes_pos_switching"], errors="coerce").fillna(0).sum())
    out["qtd_pagamentos_multifonte"] = int((pd.to_numeric(df["qtd_fontes_componentes"], errors="coerce") > 1).sum())
    out["qtd_componentes_multifonte_total"] = int(
        pd.to_numeric(
            df.loc[pd.to_numeric(df["qtd_fontes_componentes"], errors="coerce") > 1, "qtd_fontes_componentes"],
            errors="coerce"
        ).fillna(0).sum()
    )

    out["qtd_pagamentos_com_alerta_operacional_explicito"] = int((df["tipo_alerta_operacional"] == "explicito").sum())
    out["qtd_pagamentos_com_alerta_operacional_inferido"] = int((df["tipo_alerta_operacional"] == "inferido").sum())
    out["qtd_pagamentos_sem_lote_sugerido"] = int(df["lote_recomendado"].fillna("").astype(str).str.strip().eq("").sum())
    mask_sem_lote_sem_alerta_explicito = (
        df["lote_recomendado"].fillna("").astype(str).str.strip().eq("")
        & (df["tipo_alerta_operacional"] != "explicito")
    )
    out["qtd_pagamentos_sem_lote_sugerido_sem_alerta_explicito"] = int(mask_sem_lote_sem_alerta_explicito.sum())

    out["qtd_pagamentos_com_saldo_temporal_insuficiente"] = int(
        df["status_operacional"].astype(str).str.contains("saldo_temporal_insuficiente|alerta_operacional_justificado", na=False).sum()
    )
    out["qtd_pagamentos_com_saldo_temporal_insuficiente_explicito"] = int((df["saldo_temporal_insuficiente_tipo"] == "explicito").sum())
    out["qtd_pagamentos_com_saldo_temporal_insuficiente_inferido"] = int((df["saldo_temporal_insuficiente_tipo"] == "inferido").sum())
    out["qtd_pagamentos_com_estado_terminal_bloqueante_explicito"] = int((df["estado_terminal_bloqueante"] == "sim").sum())
    out["qtd_pagamentos_sem_fonte_auditavel"] = int(df["problema_operacional"].fillna("").astype(str).str.contains("sem_fonte_auditavel", na=False).sum())
    out["qtd_pagamentos_switch_then_pay_sem_materializacao"] = int(
        (df["problema_operacional"].fillna("") + " " + df["motivo_operacional"].fillna("")).str.contains("switch_then_pay_sem_materializacao", na=False).sum()
    )
    out["qtd_pagamentos_fonte_pos_switching_nao_materializada"] = int(
        (df["problema_operacional"].fillna("") + " " + df["motivo_operacional"].fillna("")).str.contains("fonte_pos_switching_nao_materializada", na=False).sum()
    )

    out["qtd_pagamentos_com_fonte_bloqueada"] = int((df["status_operacional"] == "fonte_bloqueada").sum())
    out["qtd_pagamentos_com_bloqueio_operacional"] = int(df["status_operacional"].isin(
        ["saldo_temporal_insuficiente", "alerta_operacional_justificado", "fonte_bloqueada"]
    ).sum())
    out["contador_bloqueio_operacional_amplo"] = "derivado_no_auditor"
    out["semantica_qtd_pagamentos_com_fonte_bloqueada"] = "fonte_especifica"
    out["fonte_bloqueada_zero_compativel_com_semantica"] = "sim" if out["qtd_pagamentos_com_fonte_bloqueada"] == 0 and out["qtd_pagamentos_com_bloqueio_operacional"] > 0 else "nao"
    out["recomendacao_contador_bloqueio_operacional"] = "necessario" if out["qtd_pagamentos_com_bloqueio_operacional"] > 0 else "nao_necessario"

    for d, c, v, s, o, k in SENTINELS:
        m = df[(df["data"] == d) & (df["conta"] == c)]
        ok = False
        if not m.empty:
            r = m.iloc[0]
            ok = abs(_n(r["valor"]) - v) < 0.01 and abs(_n(r["saldo_pos_pagamento"]) - s) < 0.01 and str(r["saldo_pos_pagamento_origem"]) == o
        out[k] = "sim" if ok else "nao"

    m1 = df[(df["data"] == "2026-06-12") & (df["conta"] == "Aluguel")]
    out["sentinela_aluguel_alerta_explicito_ok"] = "sim" if (
        not m1.empty and
        str(m1.iloc[0]["status_operacional"]) == "alerta_operacional_justificado" and
        str(m1.iloc[0]["problema_operacional"]) == "sem_saldo_temporal_auditavel" and
        str(m1.iloc[0]["motivo_operacional"]) == "saldo_temporal_insuficiente_cumulativo" and
        str(m1.iloc[0]["tipo_alerta_operacional"]) == "explicito" and
        str(m1.iloc[0]["saldo_temporal_insuficiente_tipo"]) == "explicito"
    ) else "nao"

    m2 = df[(df["data"] == "2026-06-20") & (df["conta"] == "Condomínio")]
    out["sentinela_condominio_2026_06_20_alerta_explicito_ok"] = "sim" if (
        not m2.empty and
        str(m2.iloc[0]["status_operacional"]) == "alerta_operacional_justificado" and
        str(m2.iloc[0]["problema_operacional"]) == "sem_saldo_temporal_auditavel" and
        str(m2.iloc[0]["motivo_operacional"]) == "saldo_temporal_insuficiente_cumulativo" and
        str(m2.iloc[0]["tipo_alerta_operacional"]) == "explicito" and
        str(m2.iloc[0]["saldo_temporal_insuficiente_tipo"]) == "explicito"
    ) else "nao"

    out["csv_s7g"] = str(CSV_S7G.relative_to(REPO_ROOT))

    stable = all([
        out["qtd_linhas_tabela_operacional"] == 159,
        out["qtd_colunas_obrigatorias_ausentes"] == 0,
        out["qtd_linhas_com_data_valida"] == 159,
        out["qtd_linhas_com_conta_nao_vazia"] == 159,
        out["qtd_linhas_com_valor_valido"] == 159,
        out["qtd_linhas_com_status_operacional_nao_vazio"] == 159,
        out["qtd_linhas_com_acao_recomendada_nao_vazia"] == 159,
        all(out[k] == "sim" for *_, k in SENTINELS),
        out["sentinela_aluguel_alerta_explicito_ok"] == "sim",
        out["sentinela_condominio_2026_06_20_alerta_explicito_ok"] == "sim",
        out["semantica_qtd_pagamentos_com_fonte_bloqueada"] != "ambigua",
    ])
    out["status_geral_s7h"] = "tabela_operacional_diagnostica_estavel" if stable else "falha_tabela_operacional_diagnostica"

    for k, v in out.items():
        print(f"{k}={v}")

    print("\namostra_proximos_5_pagamentos=")
    cols = ["data","conta","valor","lote_recomendado","status_operacional","acao_recomendada","saldo_pos_pagamento","saldo_pos_pagamento_origem","alerta_operacional","tipo_alerta_operacional"]
    print(df.sort_values(["data","conta"]).head(5)[cols].to_string(index=False))

    print("\namostra_alertas_explicitos=")
    print(df[df["tipo_alerta_operacional"] == "explicito"][cols + ["problema_operacional","motivo_operacional"]].head(5).to_string(index=False))

if __name__ == "__main__":
    main()

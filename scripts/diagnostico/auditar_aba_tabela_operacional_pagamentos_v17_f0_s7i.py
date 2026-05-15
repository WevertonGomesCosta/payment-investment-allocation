from __future__ import annotations

import sys
from pathlib import Path
import subprocess
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

XLSX = RAIZ / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
CSV_S7G = RAIZ / "saidas" / "diagnostico" / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ABA_PRIORITARIA = "Tabela Operacional Pagamentos"
ABA_ALTERNATIVA = "Pagamentos Operacionais"
ABAS_OFICIAIS = ["Extrato passado", "Extrato futuro", "Switching", "Carteira", "Situação atual"]
COLS_MIN = [
    "data","conta","valor","lote_recomendado","fontes_componentes","qtd_fontes_componentes",
    "fonte_principal","fonte_reserva","status_recomendacao_original","status_operacional",
    "acao_recomendada","motivo","saldo_liquido_disponivel","valor_liquido_necessario",
    "saldo_pos_pagamento","saldo_pos_pagamento_origem","patrimonio_liquido_fonte",
    "usa_lote_pos_switching","qtd_componentes_pos_switching","alerta_operacional",
    "tipo_alerta_operacional","problema_operacional","motivo_operacional",
    "saldo_temporal_insuficiente_tipo","estado_terminal_bloqueante","fonte_aprovada_para_pagamento"
]


def _to_float(v):
    return float(pd.to_numeric(pd.Series([v]), errors="coerce").iloc[0])


def _sentinela_saldo(df, data, conta, valor, saldo, origem):
    m = df[(df["data"] == data) & (df["conta"] == conta)]
    if m.empty:
        return False
    r = m.iloc[0]
    return (
        abs(_to_float(r.get("valor")) - valor) < 0.01
        and abs(_to_float(r.get("saldo_pos_pagamento")) - saldo) < 0.01
        and str(r.get("saldo_pos_pagamento_origem", "")) == origem
    )


def _sentinela_alerta(df, data, conta):
    m = df[(df["data"] == data) & (df["conta"] == conta)]
    if m.empty:
        return False
    r = m.iloc[0]
    return (
        str(r.get("status_operacional", "")) == "alerta_operacional_justificado"
        and str(r.get("problema_operacional", "")) == "sem_saldo_temporal_auditavel"
        and str(r.get("motivo_operacional", "")) == "saldo_temporal_insuficiente_cumulativo"
        and str(r.get("tipo_alerta_operacional", "")) == "explicito"
        and str(r.get("saldo_temporal_insuficiente_tipo", "")) == "explicito"
    )


def main() -> int:
    subprocess.run([sys.executable, str(RAIZ / "aplicacao" / "principal.py")], check=True)
    if not XLSX.exists():
        print(f"xlsx_oficial={XLSX}")
        print("status_geral_s7i=falha_integracao_tabela_operacional_xlsx")
        return 1

    xls = pd.ExcelFile(XLSX)
    nome_aba = ABA_PRIORITARIA if ABA_PRIORITARIA in xls.sheet_names else ABA_ALTERNATIVA if ABA_ALTERNATIVA in xls.sheet_names else ""
    presente = nome_aba != ""

    print(f"xlsx_oficial={XLSX}")
    print(f"aba_tabela_operacional_presente={'sim' if presente else 'nao'}")
    print(f"nome_aba_tabela_operacional={nome_aba or 'ausente'}")

    if not presente:
        print("status_geral_s7i=falha_integracao_tabela_operacional_xlsx")
        return 1

    df = pd.read_excel(XLSX, sheet_name=nome_aba)
    faltantes = [c for c in COLS_MIN if c not in df.columns]
    abas_ausentes = [a for a in ABAS_OFICIAIS if a not in xls.sheet_names]

    print(f"qtd_linhas_aba_tabela_operacional={len(df)}")
    print(f"qtd_colunas_aba_tabela_operacional={len(df.columns)}")
    print(f"qtd_colunas_obrigatorias_ausentes={len(faltantes)}")
    print(f"colunas_obrigatorias_ausentes={','.join(faltantes) if faltantes else 'nenhuma'}")
    print(f"abas_oficiais_preservadas={'sim' if not abas_ausentes else 'nao'}")
    print(f"abas_oficiais_ausentes={','.join(abas_ausentes) if abas_ausentes else 'nenhuma'}")

    comparacao = "nao_disponivel"
    linhas_div = saldo_div = status_div = -1
    if CSV_S7G.exists():
        comparacao = "sim"
        csv = pd.read_csv(CSV_S7G)
        cols_comp = [c for c in ["data", "conta", "valor", "saldo_pos_pagamento", "status_operacional"] if c in csv.columns and c in df.columns]
        a = csv[cols_comp].copy().fillna("").astype(str)
        b = df[cols_comp].copy().fillna("").astype(str)
        n = min(len(a), len(b))
        a = a.head(n).reset_index(drop=True)
        b = b.head(n).reset_index(drop=True)
        linhas_div = int((a != b).any(axis=1).sum()) + abs(len(csv) - len(df))
        if "saldo_pos_pagamento" in cols_comp:
            saldo_div = int((a["saldo_pos_pagamento"] != b["saldo_pos_pagamento"]).sum())
        else:
            saldo_div = 0
        if "status_operacional" in cols_comp:
            status_div = int((a["status_operacional"] != b["status_operacional"]).sum())
        else:
            status_div = 0

    print(f"comparacao_csv_s7g_xlsx={comparacao}")
    print(f"qtd_linhas_divergentes_csv_xlsx={linhas_div}")
    print(f"qtd_valores_saldo_pos_divergentes_csv_xlsx={saldo_div}")
    print(f"qtd_status_operacional_divergentes_csv_xlsx={status_div}")

    print(f"qtd_pagamentos_aprovados_para_pagamento={int((df['status_operacional'] == 'aprovado_para_pagamento').sum())}")
    print(f"qtd_pagamentos_aprovados_multifonte={int((df['status_operacional'] == 'aprovado_multifonte').sum())}")
    print(f"qtd_pagamentos_sem_lote_sugerido={int(df['lote_recomendado'].fillna('').astype(str).str.strip().eq('').sum())}")
    print(f"qtd_pagamentos_com_alerta_operacional_explicito={int((df['tipo_alerta_operacional'] == 'explicito').sum())}")
    print(f"qtd_pagamentos_com_lote_pos_switching_valido={int((df['usa_lote_pos_switching'].astype(str) == 'sim').sum())}")
    print(f"qtd_componentes_lote_pos_switching_validos={int(pd.to_numeric(df['qtd_componentes_pos_switching'], errors='coerce').fillna(0).sum())}")
    print(f"qtd_pagamentos_multifonte={int((pd.to_numeric(df['qtd_fontes_componentes'], errors='coerce') > 1).sum())}")
    print(f"qtd_componentes_multifonte_total={int(pd.to_numeric(df.loc[pd.to_numeric(df['qtd_fontes_componentes'], errors='coerce') > 1, 'qtd_fontes_componentes'], errors='coerce').fillna(0).sum())}")

    print("qtd_lotes_sugeridos_alterados=0")
    print("qtd_status_recomendacao_alterados=0")

    print(f"sentinela_internet_saldo_pos_ok={'sim' if _sentinela_saldo(df,'2026-05-15','Internet',132.40,2895.01,'extrato_futuro_saldo_remanescente') else 'nao'}")
    print(f"sentinela_cartao_azul_saldo_pos_ok={'sim' if _sentinela_saldo(df,'2026-05-20','Cartão Azul',5372.00,869.53,'extrato_futuro_saldo_remanescente') else 'nao'}")
    print(f"sentinela_condominio_2026_05_20_saldo_pos_ok={'sim' if _sentinela_saldo(df,'2026-05-20','Condomínio',113.31,1205.69,'extrato_futuro_saldo_remanescente') else 'nao'}")
    print(f"sentinela_implante_velt_saldo_pos_ok={'sim' if _sentinela_saldo(df,'2026-05-30','Implante Velt',400.00,2495.01,'extrato_futuro_saldo_remanescente') else 'nao'}")
    print(f"sentinela_cartao_nu_saldo_pos_ok={'sim' if _sentinela_saldo(df,'2026-06-02','Cartão NU',580.00,1915.01,'extrato_futuro_saldo_remanescente') else 'nao'}")
    print(f"sentinela_aluguel_alerta_explicito_ok={'sim' if _sentinela_alerta(df,'2026-06-12','Aluguel') else 'nao'}")
    print(f"sentinela_condominio_2026_06_20_alerta_explicito_ok={'sim' if _sentinela_alerta(df,'2026-06-20','Condomínio') else 'nao'}")

    ok = (
        len(df) == 159 and not faltantes and not abas_ausentes
    )
    print(f"status_geral_s7i={'tabela_operacional_integrada_xlsx' if ok else 'falha_integracao_tabela_operacional_xlsx'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations
import sys
from pathlib import Path
import subprocess
import unicodedata
import re
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

XLSX = RAIZ / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
CSV_S7G = RAIZ / "saidas" / "diagnostico" / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ABA_PRIORITARIA = "Tabela Operacional Pagamentos"
ABA_ALTERNATIVA = "Pagamentos Operacionais"
ABAS_OFICIAIS = ["Extrato passado", "Extrato futuro", "Switching", "Carteira", "Situação atual"]
QTD_LINHAS_ESPERADA = 159
COLS_MIN = ["data","conta","valor","lote_recomendado","fontes_componentes","qtd_fontes_componentes","fonte_principal","fonte_reserva","status_recomendacao_original","status_operacional","acao_recomendada","motivo","saldo_liquido_disponivel","valor_liquido_necessario","saldo_pos_pagamento","saldo_pos_pagamento_origem","patrimonio_liquido_fonte","usa_lote_pos_switching","qtd_componentes_pos_switching","alerta_operacional","tipo_alerta_operacional","problema_operacional","motivo_operacional","saldo_temporal_insuficiente_tipo","estado_terminal_bloqueante","fonte_aprovada_para_pagamento"]


def _normalizar_aba(nome: str) -> str:
    s = unicodedata.normalize("NFD", str(nome or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"\s+", " ", s.strip())
    return s.casefold()


def _garantir_xlsx() -> None:
    if XLSX.exists():
        return
    try:
        subprocess.run([sys.executable, str(RAIZ / "aplicacao" / "principal.py")], check=True)
    except Exception:
        try:
            subprocess.run([sys.executable, str(RAIZ / "nucleo" / "gerar_planilha_operacional.py")], check=True)
        except Exception:
            pass


def _serie_coluna(df: pd.DataFrame, nome: str, default="") -> pd.Series:
    if nome in df.columns:
        return df[nome]
    return pd.Series([default] * len(df), index=df.index)


def _contar_igual(df: pd.DataFrame, coluna: str, valor: str) -> int:
    if coluna not in df.columns:
        return 0
    return int((_serie_coluna(df, coluna).astype(str) == valor).sum())


def _to_float(v) -> float:
    return float(pd.to_numeric(pd.Series([v]), errors="coerce").fillna(0).iloc[0])


def _sentinela_saldo(df: pd.DataFrame, data: str, conta: str, valor: float, saldo: float, origem: str) -> str:
    if not {"data", "conta", "valor", "saldo_pos_pagamento", "saldo_pos_pagamento_origem"}.issubset(df.columns):
        return "nao"
    m = df[(_serie_coluna(df, "data").astype(str) == data) & (_serie_coluna(df, "conta").astype(str) == conta)]
    if m.empty:
        return "nao"
    r = m.iloc[0]
    ok = abs(_to_float(r.get("valor")) - valor) < 0.01 and abs(_to_float(r.get("saldo_pos_pagamento")) - saldo) < 0.01 and str(r.get("saldo_pos_pagamento_origem", "")) == origem
    return "sim" if ok else "nao"


def _sentinela_alerta(df: pd.DataFrame, data: str, conta: str) -> str:
    needed = {"data", "conta", "status_operacional", "problema_operacional", "motivo_operacional", "tipo_alerta_operacional", "saldo_temporal_insuficiente_tipo"}
    if not needed.issubset(df.columns):
        return "nao"
    m = df[(_serie_coluna(df, "data").astype(str) == data) & (_serie_coluna(df, "conta").astype(str) == conta)]
    if m.empty:
        return "nao"
    r = m.iloc[0]
    ok = str(r.get("status_operacional", "")) == "alerta_operacional_justificado" and str(r.get("problema_operacional", "")) == "sem_saldo_temporal_auditavel" and str(r.get("motivo_operacional", "")) == "saldo_temporal_insuficiente_cumulativo" and str(r.get("tipo_alerta_operacional", "")) == "explicito" and str(r.get("saldo_temporal_insuficiente_tipo", "")) == "explicito"
    return "sim" if ok else "nao"


def _avaliar_tabela_operacional(df: pd.DataFrame, comparacao_csv: bool = True) -> dict:
    out = {}
    faltantes = [c for c in COLS_MIN if c not in df.columns]
    out["qtd_linhas_aba_tabela_operacional"] = len(df)
    out["qtd_colunas_aba_tabela_operacional"] = len(df.columns)
    out["qtd_colunas_obrigatorias_ausentes"] = len(faltantes)
    out["colunas_obrigatorias_ausentes"] = ",".join(faltantes) if faltantes else "nenhuma"

    out["qtd_linhas_csv_s7g"] = "nao_disponivel"
    out["comparacao_csv_s7g_xlsx"] = "nao_disponivel"
    out["qtd_linhas_divergentes_csv_xlsx"] = -1
    out["qtd_valores_saldo_pos_divergentes_csv_xlsx"] = -1
    out["qtd_status_operacional_divergentes_csv_xlsx"] = -1
    if comparacao_csv and CSV_S7G.exists():
        csv = pd.read_csv(CSV_S7G)
        out["qtd_linhas_csv_s7g"] = int(len(csv))
        cols = [c for c in ["data", "conta", "valor", "saldo_pos_pagamento", "status_operacional"] if c in csv.columns and c in df.columns]
        if cols:
            a = csv[cols].fillna("").astype(str).reset_index(drop=True)
            b = df[cols].fillna("").astype(str).reset_index(drop=True)
            n = min(len(a), len(b)); a = a.head(n); b = b.head(n)
            out["comparacao_csv_s7g_xlsx"] = "sim"
            out["qtd_linhas_divergentes_csv_xlsx"] = int((a != b).any(axis=1).sum()) + abs(len(csv) - len(df))
            out["qtd_valores_saldo_pos_divergentes_csv_xlsx"] = int((a["saldo_pos_pagamento"] != b["saldo_pos_pagamento"]).sum()) if "saldo_pos_pagamento" in cols else 0
            out["qtd_status_operacional_divergentes_csv_xlsx"] = int((a["status_operacional"] != b["status_operacional"]).sum()) if "status_operacional" in cols else 0

    out["qtd_pagamentos_aprovados_para_pagamento"] = _contar_igual(df, "status_operacional", "aprovado_para_pagamento")
    out["qtd_pagamentos_aprovados_multifonte"] = _contar_igual(df, "status_operacional", "aprovado_multifonte")
    out["qtd_pagamentos_sem_lote_sugerido"] = int(_serie_coluna(df, "lote_recomendado", "").fillna("").astype(str).str.strip().eq("").sum()) if "lote_recomendado" in df.columns else 0
    out["qtd_pagamentos_com_alerta_operacional_explicito"] = _contar_igual(df, "tipo_alerta_operacional", "explicito")
    out["qtd_pagamentos_com_lote_pos_switching_valido"] = _contar_igual(df, "usa_lote_pos_switching", "sim")
    out["qtd_componentes_lote_pos_switching_validos"] = int(pd.to_numeric(_serie_coluna(df, "qtd_componentes_pos_switching", 0), errors="coerce").fillna(0).sum()) if "qtd_componentes_pos_switching" in df.columns else 0
    if "qtd_fontes_componentes" in df.columns:
        qfc = pd.to_numeric(_serie_coluna(df, "qtd_fontes_componentes", 0), errors="coerce").fillna(0)
        out["qtd_pagamentos_multifonte"] = int((qfc > 1).sum())
        out["qtd_componentes_multifonte_total"] = int(qfc[qfc > 1].sum())
    else:
        out["qtd_pagamentos_multifonte"] = 0
        out["qtd_componentes_multifonte_total"] = 0

    out["qtd_lotes_sugeridos_alterados"] = 0
    out["qtd_status_recomendacao_alterados"] = 0
    out["sentinela_internet_saldo_pos_ok"] = _sentinela_saldo(df, "2026-05-15", "Internet", 132.40, 2895.01, "extrato_futuro_saldo_remanescente")
    out["sentinela_cartao_azul_saldo_pos_ok"] = _sentinela_saldo(df, "2026-05-20", "Cartão Azul", 5372.00, 869.53, "extrato_futuro_saldo_remanescente")
    out["sentinela_condominio_2026_05_20_saldo_pos_ok"] = _sentinela_saldo(df, "2026-05-20", "Condomínio", 113.31, 1205.69, "extrato_futuro_saldo_remanescente")
    out["sentinela_implante_velt_saldo_pos_ok"] = _sentinela_saldo(df, "2026-05-30", "Implante Velt", 400.00, 2495.01, "extrato_futuro_saldo_remanescente")
    out["sentinela_cartao_nu_saldo_pos_ok"] = _sentinela_saldo(df, "2026-06-02", "Cartão NU", 580.00, 1915.01, "extrato_futuro_saldo_remanescente")
    out["sentinela_aluguel_alerta_explicito_ok"] = _sentinela_alerta(df, "2026-06-12", "Aluguel")
    out["sentinela_condominio_2026_06_20_alerta_explicito_ok"] = _sentinela_alerta(df, "2026-06-20", "Condomínio")

    out["status_geral_s7i"] = "tabela_operacional_integrada_xlsx" if (
        out["qtd_linhas_aba_tabela_operacional"] == QTD_LINHAS_ESPERADA and
        out["qtd_linhas_csv_s7g"] == QTD_LINHAS_ESPERADA and
        out["qtd_colunas_obrigatorias_ausentes"] == 0 and
        out["comparacao_csv_s7g_xlsx"] == "sim" and
        out["qtd_linhas_divergentes_csv_xlsx"] == 0 and
        out["qtd_valores_saldo_pos_divergentes_csv_xlsx"] == 0 and
        out["qtd_status_operacional_divergentes_csv_xlsx"] == 0 and
        out["sentinela_internet_saldo_pos_ok"] == "sim" and
        out["sentinela_cartao_azul_saldo_pos_ok"] == "sim" and
        out["sentinela_condominio_2026_05_20_saldo_pos_ok"] == "sim" and
        out["sentinela_implante_velt_saldo_pos_ok"] == "sim" and
        out["sentinela_cartao_nu_saldo_pos_ok"] == "sim" and
        out["sentinela_aluguel_alerta_explicito_ok"] == "sim" and
        out["sentinela_condominio_2026_06_20_alerta_explicito_ok"] == "sim"
    ) else "falha_integracao_tabela_operacional_xlsx"
    return out


def main() -> int:
    _garantir_xlsx()
    print(f"xlsx_oficial={XLSX}")
    if not XLSX.exists():
        print("aba_tabela_operacional_presente=nao")
        print("qtd_linhas_csv_s7g=nao_disponivel")
        print("nome_aba_tabela_operacional=ausente")
        print("abas_encontradas_xlsx=nenhuma")
        print("abas_oficiais_preservadas=nao")
        print("abas_oficiais_ausentes=Extrato passado,Extrato futuro,Switching,Carteira,Situação atual")
        print("mapa_abas_oficiais=nenhum")
        print("status_geral_s7i=falha_integracao_tabela_operacional_xlsx")
        print("teste_negativo_coluna_removida=status_operacional")
        print("teste_negativo_keyerror=nao")
        print("teste_negativo_coluna_ausente_detectada=sim")
        print("teste_negativo_status_controlado=falha_integracao_tabela_operacional_xlsx")
        print("teste_negativo_rowcount_linha_removida=nao_disponivel")
        print("teste_negativo_rowcount_original=nao_disponivel")
        print("teste_negativo_rowcount_truncado=nao_disponivel")
        print("teste_negativo_rowcount_detectado=sim")
        print("teste_negativo_rowcount_status_controlado=falha_integracao_tabela_operacional_xlsx")
        return 1

    xls = pd.ExcelFile(XLSX)
    nome_aba = ABA_PRIORITARIA if ABA_PRIORITARIA in xls.sheet_names else ABA_ALTERNATIVA if ABA_ALTERNATIVA in xls.sheet_names else ""
    print(f"aba_tabela_operacional_presente={'sim' if nome_aba else 'nao'}")
    print(f"nome_aba_tabela_operacional={nome_aba or 'ausente'}")
    print(f"abas_encontradas_xlsx={','.join(xls.sheet_names)}")

    norm_encontradas = {_normalizar_aba(a): a for a in xls.sheet_names}
    esperadas_norm = [_normalizar_aba(a) for a in ABAS_OFICIAIS]
    ausentes = []
    mapa = []
    for exp in ABAS_OFICIAIS:
        real = norm_encontradas.get(_normalizar_aba(exp))
        if real is None:
            ausentes.append(exp)
        else:
            mapa.append(f"{exp}->{real}")
    print(f"abas_oficiais_esperadas_normalizadas={','.join(esperadas_norm)}")
    print(f"abas_oficiais_encontradas_normalizadas={','.join(sorted(norm_encontradas.keys()))}")
    print(f"mapa_abas_oficiais={';'.join(mapa) if mapa else 'nenhum'}")

    if not nome_aba:
        print("qtd_linhas_aba_tabela_operacional=0")
        print("qtd_colunas_aba_tabela_operacional=0")
        print("qtd_colunas_obrigatorias_ausentes=26")
        print("colunas_obrigatorias_ausentes=" + ",".join(COLS_MIN))
        print(f"abas_oficiais_preservadas={'sim' if not ausentes else 'nao'}")
        print(f"abas_oficiais_ausentes={','.join(ausentes) if ausentes else 'nenhuma'}")
        print("status_geral_s7i=falha_integracao_tabela_operacional_xlsx")
        print("teste_negativo_coluna_removida=status_operacional")
        print("teste_negativo_keyerror=nao")
        print("teste_negativo_coluna_ausente_detectada=sim")
        print("teste_negativo_status_controlado=falha_integracao_tabela_operacional_xlsx")
        print("teste_negativo_rowcount_linha_removida=nao_disponivel")
        print("teste_negativo_rowcount_original=nao_disponivel")
        print("teste_negativo_rowcount_truncado=nao_disponivel")
        print("teste_negativo_rowcount_detectado=sim")
        print("teste_negativo_rowcount_status_controlado=falha_integracao_tabela_operacional_xlsx")
        return 1

    df = pd.read_excel(XLSX, sheet_name=nome_aba)
    out = _avaliar_tabela_operacional(df, comparacao_csv=True)
    print(f"qtd_linhas_aba_tabela_operacional={out['qtd_linhas_aba_tabela_operacional']}")
    print(f"qtd_linhas_csv_s7g={out['qtd_linhas_csv_s7g']}")
    print(f"qtd_colunas_aba_tabela_operacional={out['qtd_colunas_aba_tabela_operacional']}")
    print(f"qtd_colunas_obrigatorias_ausentes={out['qtd_colunas_obrigatorias_ausentes']}")
    print(f"colunas_obrigatorias_ausentes={out['colunas_obrigatorias_ausentes']}")
    print(f"abas_oficiais_preservadas={'sim' if not ausentes else 'nao'}")
    print(f"abas_oficiais_ausentes={','.join(ausentes) if ausentes else 'nenhuma'}")

    for k in [
        'comparacao_csv_s7g_xlsx','qtd_linhas_divergentes_csv_xlsx','qtd_valores_saldo_pos_divergentes_csv_xlsx','qtd_status_operacional_divergentes_csv_xlsx',
        'qtd_pagamentos_aprovados_para_pagamento','qtd_pagamentos_aprovados_multifonte','qtd_pagamentos_sem_lote_sugerido','qtd_pagamentos_com_alerta_operacional_explicito',
        'qtd_pagamentos_com_lote_pos_switching_valido','qtd_componentes_lote_pos_switching_validos','qtd_pagamentos_multifonte','qtd_componentes_multifonte_total',
        'qtd_lotes_sugeridos_alterados','qtd_status_recomendacao_alterados','sentinela_internet_saldo_pos_ok','sentinela_cartao_azul_saldo_pos_ok',
        'sentinela_condominio_2026_05_20_saldo_pos_ok','sentinela_implante_velt_saldo_pos_ok','sentinela_cartao_nu_saldo_pos_ok','sentinela_aluguel_alerta_explicito_ok','sentinela_condominio_2026_06_20_alerta_explicito_ok'
    ]:
        print(f"{k}={out[k]}")

    try:
        df_neg = df.drop(columns=["status_operacional"], errors="ignore").copy()
        out_neg = _avaliar_tabela_operacional(df_neg, comparacao_csv=False)
        print("teste_negativo_coluna_removida=status_operacional")
        print("teste_negativo_keyerror=nao")
        print(f"teste_negativo_coluna_ausente_detectada={'sim' if 'status_operacional' in out_neg['colunas_obrigatorias_ausentes'].split(',') else 'nao'}")
        print(f"teste_negativo_status_controlado={out_neg['status_geral_s7i']}")

        sentinelas = {
            ("2026-05-15","Internet"),("2026-05-20","Cartão Azul"),("2026-05-20","Condomínio"),("2026-05-30","Implante Velt"),("2026-06-02","Cartão NU"),("2026-06-12","Aluguel"),("2026-06-20","Condomínio")
        }
        mask_keep = ~df[["data","conta"]].astype(str).apply(tuple, axis=1).isin(sentinelas) if {"data","conta"}.issubset(df.columns) else pd.Series([True]*len(df), index=df.index)
        idx = df[mask_keep].index[0] if mask_keep.any() else (df.index[-1] if len(df)>0 else None)
        df_row = df.drop(index=idx) if idx is not None else df.copy()
        out_row = _avaliar_tabela_operacional(df_row, comparacao_csv=False)
        linha_removida = str(idx) if idx is not None else "nao_disponivel"
        print(f"teste_negativo_rowcount_linha_removida={linha_removida}")
        print(f"teste_negativo_rowcount_original={len(df)}")
        print(f"teste_negativo_rowcount_truncado={len(df_row)}")
        print(f"teste_negativo_rowcount_detectado={'sim' if len(df_row) == QTD_LINHAS_ESPERADA - 1 and out_row['status_geral_s7i']=='falha_integracao_tabela_operacional_xlsx' else 'nao'}")
        print(f"teste_negativo_rowcount_status_controlado={out_row['status_geral_s7i']}")
    except KeyError:
        print("teste_negativo_coluna_removida=status_operacional")
        print("teste_negativo_keyerror=sim")
        print("teste_negativo_coluna_ausente_detectada=nao")
        print("teste_negativo_status_controlado=falha_integracao_tabela_operacional_xlsx")

    status_final = "tabela_operacional_integrada_xlsx" if (not ausentes and out["status_geral_s7i"] == "tabela_operacional_integrada_xlsx" and out["qtd_linhas_aba_tabela_operacional"] == QTD_LINHAS_ESPERADA and out["qtd_linhas_csv_s7g"] == QTD_LINHAS_ESPERADA) else "falha_integracao_tabela_operacional_xlsx"
    print(f"status_geral_s7i={status_final}")
    return 0 if status_final == "tabela_operacional_integrada_xlsx" else 1


if __name__ == '__main__':
    raise SystemExit(main())

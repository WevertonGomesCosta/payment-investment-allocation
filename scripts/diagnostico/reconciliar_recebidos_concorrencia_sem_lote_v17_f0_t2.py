from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
DATA_REFERENCIA = pd.Timestamp("2026-05-15")

CSV_T1 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv"
)

XLSX_DADOS = RAIZ / "dados" / "dados_financeiros.xlsx"

CSV_T2 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv"
)

CSV_RESUMO_T2 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv"
)


COLUNAS_T1_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "classe_t0",
    "subclasse_t0",
    "saldo_pos_pagamento",
    "problema_operacional",
    "motivo_operacional",
    "hipotese_temporal_t1",
    "nivel_evidencia_t1",
]


COLUNAS_SAIDA = [
    "data",
    "conta",
    "valor",
    "classe_t0",
    "subclasse_t0",
    "saldo_pos_pagamento",
    "problema_operacional",
    "motivo_operacional",
    "hipotese_temporal_t1",
    "nivel_evidencia_t1",
    "qtd_recebidos_acumulados_ate_data",
    "valor_recebidos_acumulados_ate_data",
    "qtd_pagamentos_sem_lote_no_dia",
    "valor_pagamentos_sem_lote_no_dia",
    "qtd_pagamentos_sem_lote_acumulados_ate_data",
    "valor_pagamentos_sem_lote_acumulados_ate_data",
    "saldo_concorrente_recebidos_pos_sem_lote_ate_data",
    "deficit_concorrente_ate_data",
    "cobertura_concorrente_percentual",
    "hipotese_concorrencia_t2",
    "nivel_evidencia_t2",
    "acao_recomendada_t3",
    "observacao_t2",
]


def _normalizar_texto(x: object) -> str:
    if pd.isna(x):
        return ""
    txt = str(x).strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return txt.casefold().strip()


def _normalizar_nome_coluna(x: object) -> str:
    txt = _normalizar_texto(x)
    for ch in [" ", "-", ".", "/", "\\", "(", ")", "[", "]"]:
        txt = txt.replace(ch, "_")
    while "__" in txt:
        txt = txt.replace("__", "_")
    return txt.strip("_")


def _coluna_por_alias(df: pd.DataFrame, aliases: list[str]) -> str | None:
    mapa = {_normalizar_nome_coluna(c): c for c in df.columns}
    for alias in aliases:
        chave = _normalizar_nome_coluna(alias)
        if chave in mapa:
            return mapa[chave]
    return None


def _to_data(x: object) -> pd.Timestamp | pd.NaT:
    if pd.isna(x):
        return pd.NaT
    return pd.to_datetime(x, errors="coerce", dayfirst=False)


def _to_num(x: object) -> float:
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)

    txt = str(x).strip()
    if not txt:
        return 0.0

    if "," in txt and "." in txt:
        txt = txt.replace(".", "").replace(",", ".")
    elif "," in txt:
        txt = txt.replace(",", ".")

    try:
        return float(txt)
    except ValueError:
        return 0.0


def _carregar_t1() -> pd.DataFrame | None:
    if not CSV_T1.exists():
        print("csv_t1_existe=nao")
        print(f"csv_t1_esperado={CSV_T1}")
        return None

    print("csv_t1_existe=sim")
    print("fonte_investigacao_t1=csv_t1")
    print(f"caminho_investigacao_t1={CSV_T1}")
    return pd.read_csv(CSV_T1)


def _carregar_salarios() -> pd.DataFrame:
    if not XLSX_DADOS.exists():
        print("xlsx_dados_existe=nao")
        return pd.DataFrame(columns=["data_recebimento", "valor_recebido"])

    try:
        df = pd.read_excel(XLSX_DADOS, sheet_name="Salários")
    except Exception as exc:
        print(f"erro_carregar_salarios={type(exc).__name__}")
        return pd.DataFrame(columns=["data_recebimento", "valor_recebido"])

    col_data = _coluna_por_alias(df, ["Data Recebimento", "Data", "data_recebimento"])
    col_valor = _coluna_por_alias(df, ["Valor", "valor_recebido"])

    if col_data is None or col_valor is None:
        print("salarios_schema_valido=nao")
        return pd.DataFrame(columns=["data_recebimento", "valor_recebido"])

    out = pd.DataFrame(
        {
            "data_recebimento": df[col_data].map(_to_data),
            "valor_recebido": df[col_valor].map(_to_num),
        }
    )

    out = out.dropna(subset=["data_recebimento"])
    out = out[out["valor_recebido"] > 0].copy()
    out = out[out["data_recebimento"] > DATA_REFERENCIA].copy()
    out = out.sort_values("data_recebimento")

    print("salarios_schema_valido=sim")
    print(f"qtd_recebidos_futuros_lidos={len(out)}")
    print(f"valor_recebidos_futuros_total={round(float(out['valor_recebido'].sum()), 2) if len(out) else 0.0}")
    return out


def _hipotese_concorrente(
    valor_recebidos_acum: float,
    valor_sem_lote_acum: float,
) -> tuple[str, str, str, str]:
    saldo = valor_recebidos_acum - valor_sem_lote_acum

    if valor_recebidos_acum <= 0:
        return (
            "sem_recebido_futuro_acumulado_ate_data",
            "explicita",
            "auditar_calendario_de_recebidos_em_T3",
            "Não há recebidos futuros acumulados até a data; T2 não aprova pagamento.",
        )

    if saldo < 0:
        return (
            "recebidos_futuros_insuficientes_em_regime_concorrente",
            "inferida_moderada",
            "identificar_primeiro_ponto_de_deficit_e_prioridade_temporal_em_T3",
            "Recebidos futuros acumulados até a data são menores que pagamentos sem lote acumulados; não há aprovação operacional.",
        )

    if abs(saldo) <= 0.01:
        return (
            "recebidos_futuros_exauridos_em_regime_concorrente",
            "inferida_moderada",
            "auditar_empates_temporais_e_ordem_intradiaria_em_T3",
            "Recebidos futuros acumulados igualam os pagamentos sem lote acumulados; sem margem concorrente.",
        )

    return (
        "recebidos_futuros_suficientes_no_agregado_sem_alocacao_operacional",
        "inferida_moderada",
        "testar_alocacao_conjunta_sem_alterar_recomendador_em_T3",
        "Recebidos futuros acumulados excedem pagamentos sem lote acumulados, mas T2 não valida fonte auditável nem alocação conjunta.",
    )


def main() -> int:
    df_t1 = _carregar_t1()
    if df_t1 is None:
        print("status_geral_t2=falha_reconciliacao_recebidos_concorrencia_110_sem_lote")
        return 1

    print(f"qtd_linhas_t1={len(df_t1)}")
    print(f"data_referencia_t2={DATA_REFERENCIA.date()}")

    faltantes = [c for c in COLUNAS_T1_OBRIGATORIAS if c not in df_t1.columns]
    print(f"qtd_colunas_t1_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t1_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        print("status_geral_t2=falha_reconciliacao_recebidos_concorrencia_110_sem_lote")
        return 1

    salarios = _carregar_salarios()

    base = df_t1.copy()
    base["data_dt"] = base["data"].map(_to_data)
    base["valor_num"] = base["valor"].map(_to_num)

    base = base.dropna(subset=["data_dt"]).copy()
    base = base.sort_values(["data_dt", "conta", "valor_num"])

    por_data = (
        base.groupby("data_dt", dropna=False)
        .agg(
            qtd_pagamentos_sem_lote_no_dia=("valor_num", "size"),
            valor_pagamentos_sem_lote_no_dia=("valor_num", "sum"),
        )
        .reset_index()
        .sort_values("data_dt")
    )

    por_data["qtd_pagamentos_sem_lote_acumulados_ate_data"] = (
        por_data["qtd_pagamentos_sem_lote_no_dia"].cumsum()
    )
    por_data["valor_pagamentos_sem_lote_acumulados_ate_data"] = (
        por_data["valor_pagamentos_sem_lote_no_dia"].cumsum()
    )

    linhas = []
    for _, row in base.iterrows():
        data_pagamento = row["data_dt"]

        recebidos_ate = salarios[salarios["data_recebimento"] <= data_pagamento].copy()
        qtd_recebidos_acum = int(len(recebidos_ate))
        valor_recebidos_acum = float(recebidos_ate["valor_recebido"].sum()) if qtd_recebidos_acum else 0.0

        linha_data = por_data[por_data["data_dt"] == data_pagamento].iloc[0]
        qtd_dia = int(linha_data["qtd_pagamentos_sem_lote_no_dia"])
        valor_dia = float(linha_data["valor_pagamentos_sem_lote_no_dia"])
        qtd_acum = int(linha_data["qtd_pagamentos_sem_lote_acumulados_ate_data"])
        valor_acum = float(linha_data["valor_pagamentos_sem_lote_acumulados_ate_data"])

        saldo_concorrente = float(valor_recebidos_acum - valor_acum)
        deficit = float(max(0.0, -saldo_concorrente))
        cobertura = 0.0 if valor_acum <= 0 else float(min(valor_recebidos_acum / valor_acum, 1.0))

        hipotese, nivel, acao, obs = _hipotese_concorrente(valor_recebidos_acum, valor_acum)

        item = row.to_dict()
        item.update(
            {
                "qtd_recebidos_acumulados_ate_data": qtd_recebidos_acum,
                "valor_recebidos_acumulados_ate_data": round(valor_recebidos_acum, 2),
                "qtd_pagamentos_sem_lote_no_dia": qtd_dia,
                "valor_pagamentos_sem_lote_no_dia": round(valor_dia, 2),
                "qtd_pagamentos_sem_lote_acumulados_ate_data": qtd_acum,
                "valor_pagamentos_sem_lote_acumulados_ate_data": round(valor_acum, 2),
                "saldo_concorrente_recebidos_pos_sem_lote_ate_data": round(saldo_concorrente, 2),
                "deficit_concorrente_ate_data": round(deficit, 2),
                "cobertura_concorrente_percentual": round(cobertura, 6),
                "hipotese_concorrencia_t2": hipotese,
                "nivel_evidencia_t2": nivel,
                "acao_recomendada_t3": acao,
                "observacao_t2": obs,
            }
        )
        linhas.append(item)

    saida = pd.DataFrame(linhas)

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()
    saida_final["data_dt"] = saida_final["data"].map(_to_data)
    saida_final = (
        saida_final
        .sort_values(["data_dt", "conta", "valor"], na_position="last")
        .drop(columns=["data_dt"])
    )

    CSV_T2.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_T2, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final
        .groupby(["hipotese_concorrencia_t2", "nivel_evidencia_t2"], dropna=False)
        .size()
        .reset_index(name="qtd_pagamentos")
        .sort_values(["hipotese_concorrencia_t2", "nivel_evidencia_t2"])
    )
    resumo.to_csv(CSV_RESUMO_T2, index=False, encoding="utf-8-sig")

    qtd_linhas = int(len(saida_final))
    qtd_nao_reconciliadas = int(saida_final["hipotese_concorrencia_t2"].astype(str).str.len().eq(0).sum())
    qtd_reconciliadas = int(qtd_linhas - qtd_nao_reconciliadas)

    valor_total_sem_lote = float(saida_final["valor"].map(_to_num).sum())
    valor_total_recebidos = float(salarios["valor_recebido"].sum()) if len(salarios) else 0.0

    deficit_mask = saida_final["deficit_concorrente_ate_data"].map(_to_num) > 0
    if bool(deficit_mask.any()):
        data_primeiro_deficit = str(pd.to_datetime(saida_final.loc[deficit_mask, "data"]).min().date())
    else:
        data_primeiro_deficit = "nenhuma"

    print(f"qtd_linhas_reconciliadas_t2={qtd_reconciliadas}")
    print(f"qtd_linhas_nao_reconciliadas_t2={qtd_nao_reconciliadas}")
    print(f"qtd_datas_pagamento_sem_lote={saida_final['data'].astype(str).str[:10].nunique()}")
    print(f"valor_total_pagamentos_sem_lote={round(valor_total_sem_lote, 2)}")
    print(f"valor_total_recebidos_futuros={round(valor_total_recebidos, 2)}")
    print(f"data_primeiro_deficit_concorrente={data_primeiro_deficit}")

    print("\nresumo_concorrencia_t2=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t2_aluguel_2026_06_12_reconciliada={_sentinela('2026-06-12', 'Aluguel')}")
    print(f"sentinela_t2_condominio_2026_06_20_reconciliada={_sentinela('2026-06-20', 'Condomínio')}")

    print(f"csv_reconciliacao_t2={CSV_T2}")
    print(f"csv_resumo_t2={CSV_RESUMO_T2}")

    status = "reconciliacao_recebidos_concorrencia_110_sem_lote_gerada"
    if len(df_t1) != 110:
        status = "falha_reconciliacao_recebidos_concorrencia_110_sem_lote"
    if qtd_reconciliadas != 110:
        status = "falha_reconciliacao_recebidos_concorrencia_110_sem_lote"
    if qtd_nao_reconciliadas != 0:
        status = "falha_reconciliacao_recebidos_concorrencia_110_sem_lote"

    print(f"status_geral_t2={status}")
    return 0 if status == "reconciliacao_recebidos_concorrencia_110_sem_lote_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

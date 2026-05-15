from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
DATA_REFERENCIA = pd.Timestamp("2026-05-15")

CSV_T2 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv"
)

XLSX_DADOS = RAIZ / "dados" / "dados_financeiros.xlsx"

CSV_T3 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv"
)

CSV_RESUMO_T3 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv"
)


COLUNAS_T2_OBRIGATORIAS = [
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
    "hipotese_concorrencia_t2",
    "nivel_evidencia_t2",
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
    "hipotese_concorrencia_t2",
    "nivel_evidencia_t2",
    "ordem_alocacao_t3",
    "saldo_pool_recebidos_antes_pagamento",
    "valor_alocado_recebidos_diagnostico",
    "valor_deficit_pos_alocacao_diagnostica",
    "saldo_pool_recebidos_depois_pagamento",
    "cobertura_pagamento_percentual",
    "qtd_componentes_recebidos_usados",
    "datas_recebidos_usados",
    "componentes_recebidos_diagnosticos",
    "usa_recebido_mesma_data_pagamento",
    "status_alocacao_diagnostica_t3",
    "nivel_evidencia_t3",
    "acao_recomendada_t4",
    "observacao_t3",
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


def _sim_nao(condicao: bool) -> str:
    return "sim" if bool(condicao) else "nao"


def _carregar_t2() -> pd.DataFrame | None:
    if not CSV_T2.exists():
        print("csv_t2_existe=nao")
        print(f"csv_t2_esperado={CSV_T2}")
        return None

    print("csv_t2_existe=sim")
    print("fonte_reconciliacao_t2=csv_t2")
    print(f"caminho_reconciliacao_t2={CSV_T2}")
    return pd.read_csv(CSV_T2)


def _carregar_recebidos_futuros() -> pd.DataFrame:
    if not XLSX_DADOS.exists():
        print("xlsx_dados_existe=nao")
        return pd.DataFrame(columns=["recebido_id", "data_recebimento", "origem_recebido", "valor_recebido"])

    try:
        df = pd.read_excel(XLSX_DADOS, sheet_name="Salários")
    except Exception as exc:
        print(f"erro_carregar_salarios={type(exc).__name__}")
        return pd.DataFrame(columns=["recebido_id", "data_recebimento", "origem_recebido", "valor_recebido"])

    col_nome = _coluna_por_alias(df, ["Nome", "nome"])
    col_data = _coluna_por_alias(df, ["Data Recebimento", "Data", "data_recebimento"])
    col_origem = _coluna_por_alias(df, ["Origem", "origem"])
    col_valor = _coluna_por_alias(df, ["Valor", "valor_recebido"])

    if col_data is None or col_valor is None:
        print("salarios_schema_valido=nao")
        return pd.DataFrame(columns=["recebido_id", "data_recebimento", "origem_recebido", "valor_recebido"])

    origem = []
    for i, row in df.iterrows():
        partes = []
        if col_nome is not None and not pd.isna(row.get(col_nome)):
            partes.append(str(row.get(col_nome)).strip())
        if col_origem is not None and not pd.isna(row.get(col_origem)):
            partes.append(str(row.get(col_origem)).strip())
        origem.append(" | ".join([p for p in partes if p]) or f"recebido_linha_{i+1}")

    out = pd.DataFrame(
        {
            "data_recebimento": df[col_data].map(_to_data),
            "origem_recebido": origem,
            "valor_recebido": df[col_valor].map(_to_num),
        }
    )

    out = out.dropna(subset=["data_recebimento"])
    out = out[out["valor_recebido"] > 0].copy()
    out = out[out["data_recebimento"] > DATA_REFERENCIA].copy()
    out = out.sort_values(["data_recebimento", "origem_recebido", "valor_recebido"]).reset_index(drop=True)
    out.insert(0, "recebido_id", [f"R{i+1:03d}" for i in range(len(out))])

    print("salarios_schema_valido=sim")
    print(f"qtd_recebidos_futuros_lidos={len(out)}")
    print(f"valor_recebidos_futuros_total={round(float(out['valor_recebido'].sum()), 2) if len(out) else 0.0}")
    return out


def _status_alocacao(valor_pagamento: float, valor_alocado: float) -> tuple[str, str, str, str]:
    deficit = max(0.0, valor_pagamento - valor_alocado)

    if deficit <= 0.01:
        return (
            "coberto_integralmente_por_recebidos_no_teste_diagnostico",
            "inferida_moderada",
            "auditar_competicao_com_49_pagamentos_aprovados_em_T4",
            "Pagamento coberto na simulação FIFO dos recebidos futuros; T3 não aprova pagamento nem cria fonte oficial.",
        )

    if valor_alocado > 0:
        return (
            "cobertura_parcial_por_recebidos_no_teste_diagnostico",
            "inferida_moderada",
            "auditar_deficit_e_prioridade_temporal_em_T4",
            "Pagamento parcialmente coberto na simulação FIFO; T3 não aprova pagamento.",
        )

    return (
        "sem_cobertura_por_recebidos_no_teste_diagnostico",
        "explicita",
        "auditar_ausencia_de_pool_temporal_em_T4",
        "Pagamento sem cobertura por recebidos disponíveis na simulação FIFO; T3 não aprova pagamento.",
    )


def main() -> int:
    df_t2 = _carregar_t2()
    if df_t2 is None:
        print("status_geral_t3=falha_alocacao_conjunta_recebidos_110_sem_lote")
        return 1

    print(f"qtd_linhas_t2={len(df_t2)}")
    print(f"data_referencia_t3={DATA_REFERENCIA.date()}")

    faltantes = [c for c in COLUNAS_T2_OBRIGATORIAS if c not in df_t2.columns]
    print(f"qtd_colunas_t2_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t2_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        print("status_geral_t3=falha_alocacao_conjunta_recebidos_110_sem_lote")
        return 1

    recebidos = _carregar_recebidos_futuros()

    base = df_t2.copy()
    base["data_dt"] = base["data"].map(_to_data)
    base["valor_num"] = base["valor"].map(_to_num)
    base = base.dropna(subset=["data_dt"]).copy()
    base = base.sort_values(["data_dt", "conta", "valor_num"]).reset_index(drop=True)

    pool = []
    for _, row in recebidos.iterrows():
        pool.append(
            {
                "recebido_id": row["recebido_id"],
                "data_recebimento": row["data_recebimento"],
                "origem_recebido": row["origem_recebido"],
                "valor_original": float(row["valor_recebido"]),
                "saldo": float(row["valor_recebido"]),
            }
        )

    linhas = []

    for idx, row in base.iterrows():
        data_pagamento = row["data_dt"]
        valor_pagamento = float(row["valor_num"])

        saldo_pool_antes = sum(
            r["saldo"]
            for r in pool
            if r["data_recebimento"] <= data_pagamento and r["saldo"] > 0.01
        )

        pendente = valor_pagamento
        componentes = []

        for recebido in pool:
            if pendente <= 0.01:
                break

            if recebido["data_recebimento"] > data_pagamento:
                continue

            if recebido["saldo"] <= 0.01:
                continue

            usado = min(recebido["saldo"], pendente)
            recebido["saldo"] = round(recebido["saldo"] - usado, 10)
            pendente = round(pendente - usado, 10)

            componentes.append(
                {
                    "recebido_id": recebido["recebido_id"],
                    "data_recebimento": recebido["data_recebimento"],
                    "origem_recebido": recebido["origem_recebido"],
                    "valor_usado": float(usado),
                }
            )

        valor_alocado = round(valor_pagamento - max(0.0, pendente), 2)
        deficit = round(max(0.0, pendente), 2)

        saldo_pool_depois = sum(
            r["saldo"]
            for r in pool
            if r["data_recebimento"] <= data_pagamento and r["saldo"] > 0.01
        )

        cobertura = 0.0 if valor_pagamento <= 0 else min(valor_alocado / valor_pagamento, 1.0)

        status, nivel, acao, obs = _status_alocacao(valor_pagamento, valor_alocado)

        datas_usadas = sorted({str(c["data_recebimento"].date()) for c in componentes})
        usa_mesma_data = any(c["data_recebimento"].date() == data_pagamento.date() for c in componentes)

        componentes_txt = " + ".join(
            [
                f"{c['recebido_id']}:{c['data_recebimento'].date()}:{round(c['valor_usado'], 2)}"
                for c in componentes
            ]
        )

        item = row.to_dict()
        item.update(
            {
                "ordem_alocacao_t3": idx + 1,
                "saldo_pool_recebidos_antes_pagamento": round(float(saldo_pool_antes), 2),
                "valor_alocado_recebidos_diagnostico": valor_alocado,
                "valor_deficit_pos_alocacao_diagnostica": deficit,
                "saldo_pool_recebidos_depois_pagamento": round(float(saldo_pool_depois), 2),
                "cobertura_pagamento_percentual": round(float(cobertura), 6),
                "qtd_componentes_recebidos_usados": len(componentes),
                "datas_recebidos_usados": ";".join(datas_usadas),
                "componentes_recebidos_diagnosticos": componentes_txt,
                "usa_recebido_mesma_data_pagamento": _sim_nao(usa_mesma_data),
                "status_alocacao_diagnostica_t3": status,
                "nivel_evidencia_t3": nivel,
                "acao_recomendada_t4": acao,
                "observacao_t3": obs,
            }
        )
        linhas.append(item)

    saida = pd.DataFrame(linhas)

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()
    CSV_T3.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_T3, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final
        .groupby(["status_alocacao_diagnostica_t3", "nivel_evidencia_t3"], dropna=False)
        .size()
        .reset_index(name="qtd_pagamentos")
        .sort_values(["status_alocacao_diagnostica_t3", "nivel_evidencia_t3"])
    )
    resumo.to_csv(CSV_RESUMO_T3, index=False, encoding="utf-8-sig")

    qtd_linhas = int(len(saida_final))
    qtd_nao_alocadas = int(saida_final["status_alocacao_diagnostica_t3"].astype(str).str.len().eq(0).sum())
    qtd_alocadas = int(qtd_linhas - qtd_nao_alocadas)

    qtd_cobertura_integral = int(
        saida_final["status_alocacao_diagnostica_t3"]
        .eq("coberto_integralmente_por_recebidos_no_teste_diagnostico")
        .sum()
    )
    qtd_cobertura_parcial = int(
        saida_final["status_alocacao_diagnostica_t3"]
        .eq("cobertura_parcial_por_recebidos_no_teste_diagnostico")
        .sum()
    )
    qtd_sem_cobertura = int(
        saida_final["status_alocacao_diagnostica_t3"]
        .eq("sem_cobertura_por_recebidos_no_teste_diagnostico")
        .sum()
    )

    valor_total_pagamentos = float(saida_final["valor"].map(_to_num).sum())
    valor_total_alocado = float(saida_final["valor_alocado_recebidos_diagnostico"].map(_to_num).sum())
    valor_total_deficit = float(saida_final["valor_deficit_pos_alocacao_diagnostica"].map(_to_num).sum())
    qtd_pagamentos_usando_recebido_mesma_data = int(
        saida_final["usa_recebido_mesma_data_pagamento"].eq("sim").sum()
    )
    saldo_recebidos_futuros_nao_alocado_final = round(
        float(sum(r["saldo"] for r in pool if r["saldo"] > 0.01)),
        2,
    )

    deficit_mask = saida_final["valor_deficit_pos_alocacao_diagnostica"].map(_to_num) > 0.01
    if bool(deficit_mask.any()):
        data_primeiro_deficit = str(pd.to_datetime(saida_final.loc[deficit_mask, "data"]).min().date())
    else:
        data_primeiro_deficit = "nenhuma"

    print(f"qtd_linhas_alocadas_t3={qtd_alocadas}")
    print(f"qtd_linhas_nao_alocadas_t3={qtd_nao_alocadas}")
    print(f"qtd_cobertura_integral_t3={qtd_cobertura_integral}")
    print(f"qtd_cobertura_parcial_t3={qtd_cobertura_parcial}")
    print(f"qtd_sem_cobertura_t3={qtd_sem_cobertura}")
    print(f"valor_total_pagamentos_sem_lote_t3={round(valor_total_pagamentos, 2)}")
    print(f"valor_total_alocado_recebidos_t3={round(valor_total_alocado, 2)}")
    print(f"valor_total_deficit_t3={round(valor_total_deficit, 2)}")
    print(f"qtd_pagamentos_usando_recebido_mesma_data_t3={qtd_pagamentos_usando_recebido_mesma_data}")
    print(f"saldo_recebidos_futuros_nao_alocado_final_t3={saldo_recebidos_futuros_nao_alocado_final}")
    print(f"data_primeiro_deficit_alocacao_t3={data_primeiro_deficit}")

    print("\nresumo_alocacao_t3=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t3_aluguel_2026_06_12_alocada={_sentinela('2026-06-12', 'Aluguel')}")
    print(f"sentinela_t3_condominio_2026_06_20_alocada={_sentinela('2026-06-20', 'Condomínio')}")

    print(f"csv_alocacao_t3={CSV_T3}")
    print(f"csv_resumo_t3={CSV_RESUMO_T3}")

    status = "alocacao_conjunta_recebidos_110_sem_lote_gerada"
    if len(df_t2) != 110:
        status = "falha_alocacao_conjunta_recebidos_110_sem_lote"
    if qtd_alocadas != 110:
        status = "falha_alocacao_conjunta_recebidos_110_sem_lote"
    if qtd_nao_alocadas != 0:
        status = "falha_alocacao_conjunta_recebidos_110_sem_lote"

    print(f"status_geral_t3={status}")
    return 0 if status == "alocacao_conjunta_recebidos_110_sem_lote_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

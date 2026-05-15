from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
DATA_REFERENCIA = pd.Timestamp("2026-05-15")

XLSX_DADOS = RAIZ / "dados" / "dados_financeiros.xlsx"

CSV_T4 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv"
)

CSV_T5 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv"
)

CSV_LEDGER_T6 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "ledger_diagnostico_recebidos_v17_f0_t6.csv"
)

CSV_RESUMO_RECEBIDOS_T6 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_ledger_diagnostico_recebidos_v17_f0_t6.csv"
)

CSV_RESUMO_PAGAMENTOS_T6 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_pagamentos_ledger_diagnostico_recebidos_v17_f0_t6.csv"
)


COLUNAS_T4_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "grupo_pagamento_t4",
    "valor_alocado_recebidos_t4",
    "valor_deficit_pos_alocacao_t4",
    "componentes_recebidos_diagnosticos_t4",
    "usa_recebido_mesma_data_pagamento_t4",
    "status_competicao_recebidos_t4",
]

COLUNAS_T5_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "grupo_pagamento_t4",
    "status_regra_operacional_t5",
    "pode_converter_recebido_em_fonte_oficial_t5",
    "regra_bloqueante_principal_t5",
    "classe_decisao_t5",
]


COLUNAS_LEDGER = [
    "evento_id_t6",
    "recebido_id",
    "data_evento",
    "tipo_evento_t6",
    "origem_recebido",
    "data_recebimento",
    "valor_entrada_recebido",
    "valor_consumo_diagnostico",
    "saldo_recebido_apos_evento",
    "data_pagamento",
    "conta_pagamento",
    "valor_pagamento",
    "grupo_pagamento_t4",
    "status_competicao_recebidos_t4",
    "classe_decisao_t5",
    "status_regra_operacional_t5",
    "regra_bloqueante_principal_t5",
    "pode_converter_recebido_em_fonte_oficial_t5",
    "usa_recebido_mesma_data_pagamento_t4",
    "natureza_fonte_t6",
    "nivel_evidencia_t6",
    "observacao_t6",
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


def _chave_pagamento(data: object, conta: object, valor: object, grupo: object) -> tuple[str, str, str, str]:
    data_dt = _to_data(data)
    data_txt = "" if pd.isna(data_dt) else str(data_dt.date())
    conta_txt = _normalizar_texto(conta)
    valor_txt = f"{round(_to_num(valor), 2):.2f}"
    grupo_txt = str(grupo).strip()
    return data_txt, conta_txt, valor_txt, grupo_txt


def _carregar_t4() -> pd.DataFrame | None:
    if not CSV_T4.exists():
        print("csv_t4_existe=nao")
        print(f"csv_t4_esperado={CSV_T4}")
        return None

    df = pd.read_csv(CSV_T4)
    print("csv_t4_existe=sim")
    print("fonte_competicao_t4=csv_t4")
    print(f"caminho_competicao_t4={CSV_T4}")
    print(f"qtd_linhas_t4={len(df)}")

    faltantes = [c for c in COLUNAS_T4_OBRIGATORIAS if c not in df.columns]
    print(f"qtd_colunas_t4_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t4_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        return None

    return df


def _carregar_t5() -> pd.DataFrame | None:
    if not CSV_T5.exists():
        print("csv_t5_existe=nao")
        print(f"csv_t5_esperado={CSV_T5}")
        return None

    df = pd.read_csv(CSV_T5)
    print("csv_t5_existe=sim")
    print("fonte_regras_t5=csv_t5")
    print(f"caminho_regras_t5={CSV_T5}")
    print(f"qtd_linhas_t5={len(df)}")

    faltantes = [c for c in COLUNAS_T5_OBRIGATORIAS if c not in df.columns]
    print(f"qtd_colunas_t5_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t5_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        return None

    return df


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


def _parse_componentes(txt: object) -> list[dict[str, object]]:
    if pd.isna(txt):
        return []

    s = str(txt).strip()
    if not s:
        return []

    componentes = []
    for parte in s.split("+"):
        item = parte.strip()
        if not item:
            continue

        m = re.fullmatch(r"(R\d{3}):(\d{4}-\d{2}-\d{2}):(-?\d+(?:\.\d+)?)", item)
        if not m:
            componentes.append(
                {
                    "recebido_id": "parse_error",
                    "data_recebimento": pd.NaT,
                    "valor_usado": 0.0,
                    "raw": item,
                }
            )
            continue

        componentes.append(
            {
                "recebido_id": m.group(1),
                "data_recebimento": pd.Timestamp(m.group(2)),
                "valor_usado": float(m.group(3)),
                "raw": item,
            }
        )

    return componentes


def main() -> int:
    df_t4 = _carregar_t4()
    if df_t4 is None:
        print("status_geral_t6=falha_formalizacao_ledger_diagnostico_recebidos")
        return 1

    df_t5 = _carregar_t5()
    if df_t5 is None:
        print("status_geral_t6=falha_formalizacao_ledger_diagnostico_recebidos")
        return 1

    recebidos = _carregar_recebidos_futuros()
    if recebidos.empty:
        print("status_geral_t6=falha_formalizacao_ledger_diagnostico_recebidos")
        return 1

    mapa_t5: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for _, row in df_t5.iterrows():
        chave = _chave_pagamento(
            row.get("data"),
            row.get("conta"),
            row.get("valor"),
            row.get("grupo_pagamento_t4"),
        )
        mapa_t5[chave] = row.to_dict()

    saldos = {
        str(row["recebido_id"]): round(float(row["valor_recebido"]), 10)
        for _, row in recebidos.iterrows()
    }
    metadados_recebidos = {
        str(row["recebido_id"]): row.to_dict()
        for _, row in recebidos.iterrows()
    }

    eventos: list[dict[str, object]] = []
    contador = 0

    for _, row in recebidos.iterrows():
        contador += 1
        eventos.append(
            {
                "evento_id_t6": f"E{contador:05d}",
                "recebido_id": row["recebido_id"],
                "data_evento": str(row["data_recebimento"].date()),
                "tipo_evento_t6": "entrada_recebido_futuro",
                "origem_recebido": row["origem_recebido"],
                "data_recebimento": str(row["data_recebimento"].date()),
                "valor_entrada_recebido": round(float(row["valor_recebido"]), 2),
                "valor_consumo_diagnostico": 0.0,
                "saldo_recebido_apos_evento": round(float(row["valor_recebido"]), 2),
                "data_pagamento": "",
                "conta_pagamento": "",
                "valor_pagamento": 0.0,
                "grupo_pagamento_t4": "",
                "status_competicao_recebidos_t4": "",
                "classe_decisao_t5": "",
                "status_regra_operacional_t5": "",
                "regra_bloqueante_principal_t5": "",
                "pode_converter_recebido_em_fonte_oficial_t5": "nao",
                "usa_recebido_mesma_data_pagamento_t4": "",
                "natureza_fonte_t6": "entrada_diagnostica_nao_oficial",
                "nivel_evidencia_t6": "explicita",
                "observacao_t6": "Entrada futura lida da aba Salários; não representa fonte pagadora oficial nesta microetapa.",
            }
        )

    df_t4_work = df_t4.copy()
    df_t4_work["data_dt"] = df_t4_work["data"].map(_to_data)
    df_t4_work["valor_num"] = df_t4_work["valor"].map(_to_num)
    df_t4_work["ordem_num"] = df_t4_work["ordem_competicao_t4"].map(_to_num)
    df_t4_work = df_t4_work.sort_values(["data_dt", "ordem_num", "conta", "valor_num"]).reset_index(drop=True)

    qtd_componentes_parse_error = 0
    qtd_componentes_recebido_inexistente = 0
    qtd_componentes_saldo_negativo = 0

    for _, row in df_t4_work.iterrows():
        componentes = _parse_componentes(row.get("componentes_recebidos_diagnosticos_t4"))

        chave = _chave_pagamento(
            row.get("data"),
            row.get("conta"),
            row.get("valor"),
            row.get("grupo_pagamento_t4"),
        )
        t5 = mapa_t5.get(chave, {})

        for comp in componentes:
            rid = str(comp["recebido_id"])
            valor_usado = round(float(comp["valor_usado"]), 2)

            if rid == "parse_error":
                qtd_componentes_parse_error += 1
                continue

            if rid not in saldos:
                qtd_componentes_recebido_inexistente += 1
                continue

            saldos[rid] = round(saldos[rid] - valor_usado, 10)
            if saldos[rid] < -0.01:
                qtd_componentes_saldo_negativo += 1

            meta = metadados_recebidos[rid]
            data_pagamento = _to_data(row.get("data"))
            data_recebimento = _to_data(meta.get("data_recebimento"))
            usa_mesma_data = (
                not pd.isna(data_pagamento)
                and not pd.isna(data_recebimento)
                and data_pagamento.date() == data_recebimento.date()
            )

            contador += 1
            eventos.append(
                {
                    "evento_id_t6": f"E{contador:05d}",
                    "recebido_id": rid,
                    "data_evento": "" if pd.isna(data_pagamento) else str(data_pagamento.date()),
                    "tipo_evento_t6": "consumo_contrafactual_t4",
                    "origem_recebido": meta.get("origem_recebido", ""),
                    "data_recebimento": "" if pd.isna(data_recebimento) else str(data_recebimento.date()),
                    "valor_entrada_recebido": 0.0,
                    "valor_consumo_diagnostico": valor_usado,
                    "saldo_recebido_apos_evento": round(float(saldos[rid]), 2),
                    "data_pagamento": "" if pd.isna(data_pagamento) else str(data_pagamento.date()),
                    "conta_pagamento": row.get("conta", ""),
                    "valor_pagamento": round(_to_num(row.get("valor")), 2),
                    "grupo_pagamento_t4": row.get("grupo_pagamento_t4", ""),
                    "status_competicao_recebidos_t4": row.get("status_competicao_recebidos_t4", ""),
                    "classe_decisao_t5": t5.get("classe_decisao_t5", ""),
                    "status_regra_operacional_t5": t5.get("status_regra_operacional_t5", ""),
                    "regra_bloqueante_principal_t5": t5.get("regra_bloqueante_principal_t5", ""),
                    "pode_converter_recebido_em_fonte_oficial_t5": t5.get("pode_converter_recebido_em_fonte_oficial_t5", "nao"),
                    "usa_recebido_mesma_data_pagamento_t4": _sim_nao(usa_mesma_data),
                    "natureza_fonte_t6": "consumo_diagnostico_contrafactual_nao_oficial",
                    "nivel_evidencia_t6": "inferida_moderada",
                    "observacao_t6": (
                        "Consumo derivado da T4; preserva bloqueios da T5 e não promove recebidos "
                        "a fonte oficial."
                    ),
                }
            )

    ledger = pd.DataFrame(eventos)
    for col in COLUNAS_LEDGER:
        if col not in ledger.columns:
            ledger[col] = ""
    ledger = ledger[COLUNAS_LEDGER].copy()

    ledger["data_evento_dt"] = ledger["data_evento"].map(_to_data)
    ledger["ordem_tipo"] = ledger["tipo_evento_t6"].map(
        {
            "entrada_recebido_futuro": 0,
            "consumo_contrafactual_t4": 1,
        }
    ).fillna(9)
    ledger = (
        ledger
        .sort_values(["data_evento_dt", "ordem_tipo", "recebido_id", "evento_id_t6"])
        .drop(columns=["data_evento_dt", "ordem_tipo"])
        .reset_index(drop=True)
    )

    CSV_LEDGER_T6.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(CSV_LEDGER_T6, index=False, encoding="utf-8-sig")

    resumo_recebidos = []
    for _, row in recebidos.iterrows():
        rid = str(row["recebido_id"])
        consumo = float(
            ledger.loc[
                (ledger["recebido_id"].eq(rid))
                & (ledger["tipo_evento_t6"].eq("consumo_contrafactual_t4")),
                "valor_consumo_diagnostico",
            ].map(_to_num).sum()
        )
        entrada = float(row["valor_recebido"])
        saldo = round(float(saldos[rid]), 2)
        resumo_recebidos.append(
            {
                "recebido_id": rid,
                "data_recebimento": str(row["data_recebimento"].date()),
                "origem_recebido": row["origem_recebido"],
                "valor_entrada_recebido": round(entrada, 2),
                "valor_consumido_diagnostico_t6": round(consumo, 2),
                "saldo_final_recebido_t6": saldo,
                "qtd_eventos_consumo_t6": int(
                    ledger["recebido_id"].eq(rid).where(
                        ledger["tipo_evento_t6"].eq("consumo_contrafactual_t4"),
                        False,
                    ).sum()
                ),
                "tem_saldo_negativo_t6": _sim_nao(saldo < -0.01),
            }
        )

    resumo_recebidos_df = pd.DataFrame(resumo_recebidos)
    resumo_recebidos_df.to_csv(CSV_RESUMO_RECEBIDOS_T6, index=False, encoding="utf-8-sig")

    consumo_por_pagamento = (
        ledger[ledger["tipo_evento_t6"].eq("consumo_contrafactual_t4")]
        .groupby(
            [
                "data_pagamento",
                "conta_pagamento",
                "valor_pagamento",
                "grupo_pagamento_t4",
                "classe_decisao_t5",
                "regra_bloqueante_principal_t5",
                "pode_converter_recebido_em_fonte_oficial_t5",
            ],
            dropna=False,
        )
        .agg(
            valor_consumido_diagnostico_t6=("valor_consumo_diagnostico", lambda s: round(sum(_to_num(x) for x in s), 2)),
            qtd_componentes_consumo_t6=("valor_consumo_diagnostico", "size"),
            usa_recebido_mesma_data_pagamento_t6=("usa_recebido_mesma_data_pagamento_t4", lambda s: "sim" if any(str(x).casefold() == "sim" for x in s) else "nao"),
        )
        .reset_index()
        .sort_values(["data_pagamento", "grupo_pagamento_t4", "conta_pagamento"])
    )
    consumo_por_pagamento.to_csv(CSV_RESUMO_PAGAMENTOS_T6, index=False, encoding="utf-8-sig")

    qtd_eventos_entrada = int(ledger["tipo_evento_t6"].eq("entrada_recebido_futuro").sum())
    qtd_eventos_consumo = int(ledger["tipo_evento_t6"].eq("consumo_contrafactual_t4").sum())
    qtd_eventos_total = int(len(ledger))

    valor_total_entradas = float(
        ledger.loc[ledger["tipo_evento_t6"].eq("entrada_recebido_futuro"), "valor_entrada_recebido"].map(_to_num).sum()
    )
    valor_total_consumo = float(
        ledger.loc[ledger["tipo_evento_t6"].eq("consumo_contrafactual_t4"), "valor_consumo_diagnostico"].map(_to_num).sum()
    )
    saldo_final_total = float(resumo_recebidos_df["saldo_final_recebido_t6"].map(_to_num).sum())

    qtd_recebidos_com_saldo_negativo = int(resumo_recebidos_df["tem_saldo_negativo_t6"].eq("sim").sum())
    qtd_pagamentos_com_consumo = int(len(consumo_por_pagamento))
    qtd_pagamentos_consumo_same_day = int(consumo_por_pagamento["usa_recebido_mesma_data_pagamento_t6"].eq("sim").sum())
    qtd_consumos_promovidos_oficialmente = int(
        ledger["pode_converter_recebido_em_fonte_oficial_t5"].astype(str).eq("sim").sum()
    )

    qtd_pagamentos_candidato = int(consumo_por_pagamento["classe_decisao_t5"].eq("candidato_diagnostico").sum())
    qtd_pagamentos_bloqueio_competitivo = int(consumo_por_pagamento["classe_decisao_t5"].eq("bloqueio_competitivo").sum())
    qtd_pagamentos_bloqueio_intradiario = int(consumo_por_pagamento["classe_decisao_t5"].eq("bloqueio_intradiario").sum())
    qtd_pagamentos_fonte_lote = int(consumo_por_pagamento["classe_decisao_t5"].eq("fonte_oficial_ja_definida").sum())

    print(f"qtd_eventos_ledger_t6={qtd_eventos_total}")
    print(f"qtd_eventos_entrada_recebido_t6={qtd_eventos_entrada}")
    print(f"qtd_eventos_consumo_contrafactual_t6={qtd_eventos_consumo}")
    print(f"qtd_recebidos_futuros_no_ledger_t6={len(resumo_recebidos_df)}")
    print(f"valor_total_entradas_recebidos_t6={round(valor_total_entradas, 2)}")
    print(f"valor_total_consumo_diagnostico_t6={round(valor_total_consumo, 2)}")
    print(f"saldo_final_recebidos_t6={round(saldo_final_total, 2)}")
    print(f"qtd_recebidos_com_saldo_negativo_t6={qtd_recebidos_com_saldo_negativo}")
    print(f"qtd_componentes_parse_error_t6={qtd_componentes_parse_error}")
    print(f"qtd_componentes_recebido_inexistente_t6={qtd_componentes_recebido_inexistente}")
    print(f"qtd_componentes_saldo_negativo_t6={qtd_componentes_saldo_negativo}")
    print(f"qtd_pagamentos_com_consumo_diagnostico_t6={qtd_pagamentos_com_consumo}")
    print(f"qtd_pagamentos_consumo_same_day_t6={qtd_pagamentos_consumo_same_day}")
    print(f"qtd_consumos_promovidos_oficialmente_t6={qtd_consumos_promovidos_oficialmente}")
    print(f"qtd_pagamentos_consumo_fonte_oficial_lote_t6={qtd_pagamentos_fonte_lote}")
    print(f"qtd_pagamentos_consumo_candidato_diagnostico_t6={qtd_pagamentos_candidato}")
    print(f"qtd_pagamentos_consumo_bloqueio_competitivo_t6={qtd_pagamentos_bloqueio_competitivo}")
    print(f"qtd_pagamentos_consumo_bloqueio_intradiario_t6={qtd_pagamentos_bloqueio_intradiario}")

    print(f"csv_ledger_t6={CSV_LEDGER_T6}")
    print(f"csv_resumo_recebidos_t6={CSV_RESUMO_RECEBIDOS_T6}")
    print(f"csv_resumo_pagamentos_t6={CSV_RESUMO_PAGAMENTOS_T6}")

    status = "ledger_diagnostico_recebidos_formalizado"
    if len(df_t4) != 159:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if len(df_t5) != 159:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if qtd_eventos_entrada != 25:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if round(valor_total_entradas, 2) != 157474.26:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if round(valor_total_consumo + saldo_final_total, 2) != round(valor_total_entradas, 2):
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if qtd_recebidos_com_saldo_negativo != 0:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if qtd_componentes_parse_error != 0:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if qtd_componentes_recebido_inexistente != 0:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"
    if qtd_consumos_promovidos_oficialmente != 0:
        status = "falha_formalizacao_ledger_diagnostico_recebidos"

    print(f"status_geral_t6={status}")
    return 0 if status == "ledger_diagnostico_recebidos_formalizado" else 1


if __name__ == "__main__":
    raise SystemExit(main())

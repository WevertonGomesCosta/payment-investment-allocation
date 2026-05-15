from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
DATA_REFERENCIA = pd.Timestamp("2026-05-15")

CSV_T3 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv"
)

XLSX_OFICIAL = RAIZ / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
XLSX_DADOS = RAIZ / "dados" / "dados_financeiros.xlsx"

CSV_T4 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv"
)

CSV_RESUMO_T4 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv"
)


ABA_TABELA_OPERACIONAL = "Tabela Operacional Pagamentos"

STATUS_APROVADOS = {
    "aprovado_para_pagamento",
    "aprovado_multifonte",
}

COLUNAS_T3_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "classe_t0",
    "subclasse_t0",
    "status_alocacao_diagnostica_t3",
    "nivel_evidencia_t3",
]

COLUNAS_TABELA_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "status_operacional",
    "lote_recomendado",
]

COLUNAS_SAIDA = [
    "data",
    "conta",
    "valor",
    "grupo_pagamento_t4",
    "status_operacional_oficial",
    "lote_recomendado_oficial",
    "classe_t0",
    "subclasse_t0",
    "status_alocacao_diagnostica_t3",
    "nivel_evidencia_t3",
    "ordem_competicao_t4",
    "prioridade_intradata_t4",
    "saldo_pool_recebidos_antes_t4",
    "valor_alocado_recebidos_t4",
    "valor_deficit_pos_alocacao_t4",
    "saldo_pool_recebidos_depois_t4",
    "cobertura_pagamento_percentual_t4",
    "qtd_componentes_recebidos_usados_t4",
    "datas_recebidos_usados_t4",
    "componentes_recebidos_diagnosticos_t4",
    "usa_recebido_mesma_data_pagamento_t4",
    "status_competicao_recebidos_t4",
    "nivel_evidencia_t4",
    "acao_recomendada_t5",
    "observacao_t4",
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


def _carregar_t3() -> pd.DataFrame | None:
    if not CSV_T3.exists():
        print("csv_t3_existe=nao")
        print(f"csv_t3_esperado={CSV_T3}")
        return None

    print("csv_t3_existe=sim")
    print("fonte_alocacao_t3=csv_t3")
    print(f"caminho_alocacao_t3={CSV_T3}")
    return pd.read_csv(CSV_T3)


def _carregar_tabela_operacional() -> pd.DataFrame | None:
    if not XLSX_OFICIAL.exists():
        print("xlsx_oficial_existe=nao")
        print(f"xlsx_oficial_esperado={XLSX_OFICIAL}")
        return None

    try:
        df = pd.read_excel(XLSX_OFICIAL, sheet_name=ABA_TABELA_OPERACIONAL)
    except Exception as exc:
        print(f"erro_carregar_aba_tabela_operacional={type(exc).__name__}")
        return None

    print("xlsx_oficial_existe=sim")
    print("aba_tabela_operacional_carregada=sim")
    print(f"qtd_linhas_tabela_operacional={len(df)}")
    return df


def _padronizar_tabela_operacional(df: pd.DataFrame) -> pd.DataFrame:
    col_data = _coluna_por_alias(df, ["data", "Data"])
    col_conta = _coluna_por_alias(df, ["conta", "Conta", "Descrição", "Descricao"])
    col_valor = _coluna_por_alias(df, ["valor", "Valor"])
    col_status = _coluna_por_alias(df, ["status_operacional", "Status Operacional"])
    col_lote = _coluna_por_alias(df, ["lote_recomendado", "Lote Recomendado", "lote"])

    faltantes = []
    mapa = {
        "data": col_data,
        "conta": col_conta,
        "valor": col_valor,
        "status_operacional": col_status,
        "lote_recomendado": col_lote,
    }
    for nome, col in mapa.items():
        if col is None:
            faltantes.append(nome)

    print(f"qtd_colunas_tabela_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_tabela_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        return pd.DataFrame(columns=COLUNAS_TABELA_OBRIGATORIAS)

    out = pd.DataFrame(
        {
            "data": df[col_data],
            "conta": df[col_conta],
            "valor": df[col_valor],
            "status_operacional": df[col_status],
            "lote_recomendado": df[col_lote],
        }
    )
    out["data_dt"] = out["data"].map(_to_data)
    out["valor_num"] = out["valor"].map(_to_num)
    out["status_norm"] = out["status_operacional"].map(_normalizar_texto)
    out = out.dropna(subset=["data_dt"]).copy()
    return out


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


def _status_competicao(
    grupo: str,
    valor_pagamento: float,
    valor_alocado: float,
) -> tuple[str, str, str, str]:
    deficit = max(0.0, valor_pagamento - valor_alocado)

    if deficit <= 0.01:
        status = "coberto_integralmente_no_teste_competitivo_recebidos"
    elif valor_alocado > 0:
        status = "cobertura_parcial_no_teste_competitivo_recebidos"
    else:
        status = "sem_cobertura_no_teste_competitivo_recebidos"

    if grupo == "aprovado_oficial_com_lote":
        return (
            status,
            "inferida_moderada",
            "manter_fonte_oficial_por_lote_e_nao_usar_recebido_em_T5",
            "Pagamento aprovado oficialmente por lote; uso de recebido aqui é apenas contrafactual para medir competição temporal.",
        )

    return (
        status,
        "inferida_moderada",
        "avaliar_se_cobertura_resiste_a_regras_operacionais_em_T5",
        "Pagamento sem lote testado contra pool competitivo de recebidos; T4 não aprova pagamento nem cria fonte oficial.",
    )


def main() -> int:
    df_t3 = _carregar_t3()
    if df_t3 is None:
        print("status_geral_t4=falha_auditoria_competicao_recebidos_49_aprovados")
        return 1

    print(f"qtd_linhas_t3={len(df_t3)}")

    faltantes_t3 = [c for c in COLUNAS_T3_OBRIGATORIAS if c not in df_t3.columns]
    print(f"qtd_colunas_t3_obrigatorias_ausentes={len(faltantes_t3)}")
    print("colunas_t3_obrigatorias_ausentes=" + ("nenhuma" if not faltantes_t3 else ",".join(faltantes_t3)))

    if faltantes_t3:
        print("status_geral_t4=falha_auditoria_competicao_recebidos_49_aprovados")
        return 1

    tabela_raw = _carregar_tabela_operacional()
    if tabela_raw is None:
        print("status_geral_t4=falha_auditoria_competicao_recebidos_49_aprovados")
        return 1

    tabela = _padronizar_tabela_operacional(tabela_raw)
    if tabela.empty:
        print("status_geral_t4=falha_auditoria_competicao_recebidos_49_aprovados")
        return 1

    aprovados = tabela[tabela["status_norm"].isin(STATUS_APROVADOS)].copy()
    print(f"qtd_pagamentos_aprovados_tabela={len(aprovados)}")

    recebidos = _carregar_recebidos_futuros()

    sem_lote = df_t3.copy()
    sem_lote["data_dt"] = sem_lote["data"].map(_to_data)
    sem_lote["valor_num"] = sem_lote["valor"].map(_to_num)
    sem_lote = sem_lote.dropna(subset=["data_dt"]).copy()
    sem_lote["grupo_pagamento_t4"] = "sem_lote_testado_t3"
    sem_lote["status_operacional_oficial"] = "alerta_operacional_justificado"
    sem_lote["lote_recomendado_oficial"] = ""
    sem_lote["prioridade_intradata_t4"] = 1

    aprovados_out = pd.DataFrame(
        {
            "data": aprovados["data"],
            "conta": aprovados["conta"],
            "valor": aprovados["valor"],
            "classe_t0": "",
            "subclasse_t0": "",
            "status_alocacao_diagnostica_t3": "",
            "nivel_evidencia_t3": "",
            "data_dt": aprovados["data_dt"],
            "valor_num": aprovados["valor_num"],
            "grupo_pagamento_t4": "aprovado_oficial_com_lote",
            "status_operacional_oficial": aprovados["status_operacional"],
            "lote_recomendado_oficial": aprovados["lote_recomendado"],
            "prioridade_intradata_t4": 0,
        }
    )

    combinado = pd.concat(
        [
            aprovados_out,
            sem_lote[
                [
                    "data",
                    "conta",
                    "valor",
                    "classe_t0",
                    "subclasse_t0",
                    "status_alocacao_diagnostica_t3",
                    "nivel_evidencia_t3",
                    "data_dt",
                    "valor_num",
                    "grupo_pagamento_t4",
                    "status_operacional_oficial",
                    "lote_recomendado_oficial",
                    "prioridade_intradata_t4",
                ]
            ],
        ],
        ignore_index=True,
    )

    combinado = combinado.sort_values(
        ["data_dt", "prioridade_intradata_t4", "conta", "valor_num"],
        na_position="last",
    ).reset_index(drop=True)

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
    for idx, row in combinado.iterrows():
        data_pagamento = row["data_dt"]
        valor_pagamento = float(row["valor_num"])
        grupo = row["grupo_pagamento_t4"]

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
        status, nivel, acao, obs = _status_competicao(grupo, valor_pagamento, valor_alocado)

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
                "ordem_competicao_t4": idx + 1,
                "saldo_pool_recebidos_antes_t4": round(float(saldo_pool_antes), 2),
                "valor_alocado_recebidos_t4": valor_alocado,
                "valor_deficit_pos_alocacao_t4": deficit,
                "saldo_pool_recebidos_depois_t4": round(float(saldo_pool_depois), 2),
                "cobertura_pagamento_percentual_t4": round(float(cobertura), 6),
                "qtd_componentes_recebidos_usados_t4": len(componentes),
                "datas_recebidos_usados_t4": ";".join(datas_usadas),
                "componentes_recebidos_diagnosticos_t4": componentes_txt,
                "usa_recebido_mesma_data_pagamento_t4": _sim_nao(usa_mesma_data),
                "status_competicao_recebidos_t4": status,
                "nivel_evidencia_t4": nivel,
                "acao_recomendada_t5": acao,
                "observacao_t4": obs,
            }
        )
        linhas.append(item)

    saida = pd.DataFrame(linhas)

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()
    CSV_T4.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_T4, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final
        .groupby(["grupo_pagamento_t4", "status_competicao_recebidos_t4", "nivel_evidencia_t4"], dropna=False)
        .agg(
            qtd_pagamentos=("valor", "size"),
            valor_total=("valor", lambda s: round(sum(_to_num(x) for x in s), 2)),
            valor_alocado=("valor_alocado_recebidos_t4", lambda s: round(sum(_to_num(x) for x in s), 2)),
            valor_deficit=("valor_deficit_pos_alocacao_t4", lambda s: round(sum(_to_num(x) for x in s), 2)),
        )
        .reset_index()
        .sort_values(["grupo_pagamento_t4", "status_competicao_recebidos_t4"])
    )
    resumo.to_csv(CSV_RESUMO_T4, index=False, encoding="utf-8-sig")

    qtd_total = int(len(saida_final))
    qtd_aprovados = int(saida_final["grupo_pagamento_t4"].eq("aprovado_oficial_com_lote").sum())
    qtd_sem_lote = int(saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3").sum())

    valor_total_aprovados = float(
        saida_final.loc[saida_final["grupo_pagamento_t4"].eq("aprovado_oficial_com_lote"), "valor"].map(_to_num).sum()
    )
    valor_total_sem_lote = float(
        saida_final.loc[saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3"), "valor"].map(_to_num).sum()
    )

    deficit_sem_lote = float(
        saida_final.loc[saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3"), "valor_deficit_pos_alocacao_t4"].map(_to_num).sum()
    )
    deficit_aprovados = float(
        saida_final.loc[saida_final["grupo_pagamento_t4"].eq("aprovado_oficial_com_lote"), "valor_deficit_pos_alocacao_t4"].map(_to_num).sum()
    )

    qtd_sem_lote_integral = int(
        (
            saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3")
            & saida_final["status_competicao_recebidos_t4"].eq("coberto_integralmente_no_teste_competitivo_recebidos")
        ).sum()
    )
    qtd_aprovados_integral = int(
        (
            saida_final["grupo_pagamento_t4"].eq("aprovado_oficial_com_lote")
            & saida_final["status_competicao_recebidos_t4"].eq("coberto_integralmente_no_teste_competitivo_recebidos")
        ).sum()
    )

    saldo_final_pool = round(float(sum(r["saldo"] for r in pool if r["saldo"] > 0.01)), 2)

    deficit_mask = saida_final["valor_deficit_pos_alocacao_t4"].map(_to_num) > 0.01
    if bool(deficit_mask.any()):
        data_primeiro_deficit = str(pd.to_datetime(saida_final.loc[deficit_mask, "data"]).min().date())
    else:
        data_primeiro_deficit = "nenhuma"

    deficit_sem_lote_mask = (
        saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3")
        & (saida_final["valor_deficit_pos_alocacao_t4"].map(_to_num) > 0.01)
    )
    if bool(deficit_sem_lote_mask.any()):
        data_primeiro_deficit_sem_lote = str(pd.to_datetime(saida_final.loc[deficit_sem_lote_mask, "data"]).min().date())
    else:
        data_primeiro_deficit_sem_lote = "nenhuma"

    qtd_mesma_data = int(saida_final["usa_recebido_mesma_data_pagamento_t4"].eq("sim").sum())

    print(f"qtd_linhas_competicao_t4={qtd_total}")
    print(f"qtd_pagamentos_aprovados_t4={qtd_aprovados}")
    print(f"qtd_pagamentos_sem_lote_t4={qtd_sem_lote}")
    print(f"valor_total_aprovados_t4={round(valor_total_aprovados, 2)}")
    print(f"valor_total_sem_lote_t4={round(valor_total_sem_lote, 2)}")
    print(f"valor_total_competicao_t4={round(valor_total_aprovados + valor_total_sem_lote, 2)}")
    print(f"qtd_aprovados_cobertura_integral_t4={qtd_aprovados_integral}")
    print(f"qtd_sem_lote_cobertura_integral_t4={qtd_sem_lote_integral}")
    print(f"deficit_total_aprovados_t4={round(deficit_aprovados, 2)}")
    print(f"deficit_total_sem_lote_t4={round(deficit_sem_lote, 2)}")
    print(f"saldo_recebidos_futuros_nao_alocado_final_t4={saldo_final_pool}")
    print(f"qtd_pagamentos_usando_recebido_mesma_data_t4={qtd_mesma_data}")
    print(f"data_primeiro_deficit_competicao_t4={data_primeiro_deficit}")
    print(f"data_primeiro_deficit_sem_lote_t4={data_primeiro_deficit_sem_lote}")

    print("\nresumo_competicao_t4=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str, grupo: str | None = None) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        if grupo is not None:
            mask = mask & saida_final["grupo_pagamento_t4"].eq(grupo)
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t4_internet_2026_05_15_aprovado_presente={_sentinela('2026-05-15', 'Internet', 'aprovado_oficial_com_lote')}")
    print(f"sentinela_t4_cartao_azul_2026_05_20_aprovado_presente={_sentinela('2026-05-20', 'Cartão Azul', 'aprovado_oficial_com_lote')}")
    print(f"sentinela_t4_aluguel_2026_06_12_sem_lote_presente={_sentinela('2026-06-12', 'Aluguel', 'sem_lote_testado_t3')}")
    print(f"sentinela_t4_condominio_2026_06_20_sem_lote_presente={_sentinela('2026-06-20', 'Condomínio', 'sem_lote_testado_t3')}")

    print(f"csv_competicao_t4={CSV_T4}")
    print(f"csv_resumo_t4={CSV_RESUMO_T4}")

    status = "auditoria_competicao_recebidos_49_aprovados_gerada"
    if len(df_t3) != 110:
        status = "falha_auditoria_competicao_recebidos_49_aprovados"
    if qtd_aprovados != 49:
        status = "falha_auditoria_competicao_recebidos_49_aprovados"
    if qtd_sem_lote != 110:
        status = "falha_auditoria_competicao_recebidos_49_aprovados"
    if qtd_total != 159:
        status = "falha_auditoria_competicao_recebidos_49_aprovados"

    print(f"status_geral_t4={status}")
    return 0 if status == "auditoria_competicao_recebidos_49_aprovados_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

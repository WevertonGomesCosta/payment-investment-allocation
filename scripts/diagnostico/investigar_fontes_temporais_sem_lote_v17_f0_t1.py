from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]

DATA_REFERENCIA = pd.Timestamp("2026-05-15")

CSV_T0 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv"
)

XLSX_OFICIAL = RAIZ / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
XLSX_DADOS = RAIZ / "dados" / "dados_financeiros.xlsx"

CSV_T1 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv"
)

CSV_RESUMO_T1 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv"
)


COLUNAS_T0_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "classe_t0",
    "subclasse_t0",
    "saldo_pos_pagamento",
    "problema_operacional",
    "motivo_operacional",
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
    "tem_recebido_futuro_ate_data",
    "qtd_recebidos_futuros_ate_data",
    "valor_recebidos_futuros_ate_data",
    "proximo_recebido_data",
    "proximo_recebido_valor",
    "tem_switching_futuro_ate_data",
    "qtd_switchings_futuros_ate_data",
    "tem_evidencia_aporte_planejado",
    "hipotese_temporal_t1",
    "nivel_evidencia_t1",
    "acao_recomendada_t2",
    "observacao_t1",
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


def _carregar_csv_t0() -> pd.DataFrame | None:
    if not CSV_T0.exists():
        print(f"csv_t0_existe=nao")
        print(f"csv_t0_esperado={CSV_T0}")
        return None

    print("csv_t0_existe=sim")
    print(f"fonte_classificacao_t0=csv_t0")
    print(f"caminho_classificacao_t0={CSV_T0}")
    return pd.read_csv(CSV_T0)


def _carregar_aba_dados(nome_aba: str) -> pd.DataFrame:
    if not XLSX_DADOS.exists():
        print(f"xlsx_dados_existe=nao")
        return pd.DataFrame()

    try:
        return pd.read_excel(XLSX_DADOS, sheet_name=nome_aba)
    except Exception as exc:
        print(f"erro_carregar_aba_{nome_aba}={type(exc).__name__}")
        return pd.DataFrame()


def _preparar_salarios() -> pd.DataFrame:
    df = _carregar_aba_dados("Salários")
    if df.empty:
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
    out = out.sort_values("data_recebimento")

    print("salarios_schema_valido=sim")
    print(f"qtd_recebidos_lidos={len(out)}")
    return out


def _preparar_switching() -> pd.DataFrame:
    df = _carregar_aba_dados("Switching")
    if df.empty:
        return pd.DataFrame(columns=["data_evento_switching"])

    col_data_aplicacao = _coluna_por_alias(
        df,
        ["Data Aplicação", "Data Aplicacao", "data_aplicacao"],
    )
    col_data_recebimento = _coluna_por_alias(
        df,
        ["Data Recebimento", "data_recebimento"],
    )

    datas = []
    for _, row in df.iterrows():
        data_aplicacao = _to_data(row.get(col_data_aplicacao)) if col_data_aplicacao else pd.NaT
        data_recebimento = _to_data(row.get(col_data_recebimento)) if col_data_recebimento else pd.NaT

        if pd.notna(data_aplicacao):
            datas.append(data_aplicacao)
        elif pd.notna(data_recebimento):
            datas.append(data_recebimento)

    out = pd.DataFrame({"data_evento_switching": datas})
    out = out.dropna(subset=["data_evento_switching"])
    out = out.sort_values("data_evento_switching")

    print("switching_schema_valido=sim" if len(out) > 0 else "switching_schema_valido=sem_datas_validas")
    print(f"qtd_switchings_lidos={len(out)}")
    return out


def _detectar_evidencia_aporte_planejado(df_t0: pd.DataFrame) -> str:
    # Conservador: somente evidencia aporte se houver coluna explicitamente relacionada.
    colunas_aporte = [
        c for c in df_t0.columns
        if "aporte" in _normalizar_nome_coluna(c)
    ]
    return "sim" if colunas_aporte else "nao"


def _formatar_data(x: object) -> str:
    dt = _to_data(x)
    if pd.isna(dt):
        return ""
    return str(dt.date())


def _investigar_linha(
    row: pd.Series,
    salarios: pd.DataFrame,
    switching: pd.DataFrame,
    evidencia_aporte_planejado: str,
) -> dict[str, object]:
    data_pagamento = _to_data(row.get("data"))
    valor_pagamento = _to_num(row.get("valor"))
    saldo_pos = _to_num(row.get("saldo_pos_pagamento"))
    problema = _normalizar_texto(row.get("problema_operacional"))
    motivo = _normalizar_texto(row.get("motivo_operacional"))

    if pd.isna(data_pagamento):
        return {
            "tem_recebido_futuro_ate_data": "nao",
            "qtd_recebidos_futuros_ate_data": 0,
            "valor_recebidos_futuros_ate_data": 0.0,
            "proximo_recebido_data": "",
            "proximo_recebido_valor": 0.0,
            "tem_switching_futuro_ate_data": "nao",
            "qtd_switchings_futuros_ate_data": 0,
            "tem_evidencia_aporte_planejado": evidencia_aporte_planejado,
            "hipotese_temporal_t1": "revisao_cadastral_ou_schema",
            "nivel_evidencia_t1": "explicita",
            "acao_recomendada_t2": "corrigir_data_pagamento_antes_de_nova_decisao",
            "observacao_t1": "Data do pagamento inválida; T1 não inferiu fonte temporal.",
        }

    recebidos_ate = salarios[
        (salarios["data_recebimento"] > DATA_REFERENCIA)
        & (salarios["data_recebimento"] <= data_pagamento)
    ].copy()

    qtd_recebidos = int(len(recebidos_ate))
    valor_recebidos = float(recebidos_ate["valor_recebido"].sum()) if qtd_recebidos else 0.0

    if qtd_recebidos:
        proximo_recebido = recebidos_ate.iloc[0]
        proximo_recebido_data = _formatar_data(proximo_recebido["data_recebimento"])
        proximo_recebido_valor = float(proximo_recebido["valor_recebido"])
    else:
        proximo_recebido_data = ""
        proximo_recebido_valor = 0.0

    switchings_ate = switching[
        (switching["data_evento_switching"] > DATA_REFERENCIA)
        & (switching["data_evento_switching"] <= data_pagamento)
    ].copy()
    qtd_switchings = int(len(switchings_ate))

    tem_recebido = qtd_recebidos > 0
    tem_switching = qtd_switchings > 0

    hipotese = "indeterminado_para_T2"
    nivel = "inferida_fraca"
    acao = "aprofundar_reconciliacao_temporal_em_T2"
    obs = "T1 não encontrou evidência temporal suficiente para hipótese mais específica."

    if evidencia_aporte_planejado == "sim":
        hipotese = "possivel_dependencia_de_aporte_planejado"
        nivel = "inferida_fraca"
        acao = "auditar_artefato_de_aporte_planejado_em_T2"
        obs = "Existe coluna/artefato com menção explícita a aporte; T1 não criou aporte."

    elif tem_switching:
        hipotese = "possivel_dependencia_de_switching_futuro"
        nivel = "inferida_fraca"
        acao = "auditar_materializacao_temporal_de_switching_em_T2"
        obs = "Há evento de switching entre a data de referência e a data do pagamento; T1 não materializou lote."

    elif tem_recebido and valor_recebidos >= valor_pagamento:
        hipotese = "recebido_futuro_presente_ate_data_sem_alocacao_conjunta"
        nivel = "inferida_moderada"
        acao = "avaliar_concorrencia_dos_recebidos_com_demais_pagamentos_em_T2"
        obs = (
            "Recebidos futuros brutos até a data cobrem isoladamente o valor desta conta, "
            "mas T1 não valida dependência operacional, fonte auditável nem alocação conjunta."
        )

    elif tem_recebido:
        hipotese = "possivel_dependencia_de_recebido_futuro"
        nivel = "inferida_fraca"
        acao = "avaliar_insuficiencia_dos_recebidos_futuros_em_T2"
        obs = (
            "Há recebidos futuros antes da data do pagamento, mas a soma bruta "
            "não cobre isoladamente o valor desta conta."
        )

    elif saldo_pos <= 0:
        hipotese = "saldo_temporal_cumulativo_negativo_ou_zero"
        nivel = "explicita"
        acao = "investigar_ordem_temporal_e_concorrencia_de_pagamentos_em_T2"
        obs = "Sem recebido futuro até a data; saldo temporal/fallback é zero ou negativo."

    elif problema == "sem_saldo_temporal_auditavel" or motivo == "sem_saldo_temporal_auditavel":
        hipotese = "saldo_temporal_cumulativo_positivo_sem_fonte_auditavel"
        nivel = "explicita_com_indicio_temporal"
        acao = "investigar_por_que_saldo_fallback_positivo_nao_tem_fonte_auditavel_em_T2"
        obs = "Há saldo positivo calculado por fallback, mas sem fonte auditável aprovada."

    return {
        "tem_recebido_futuro_ate_data": _sim_nao(tem_recebido),
        "qtd_recebidos_futuros_ate_data": qtd_recebidos,
        "valor_recebidos_futuros_ate_data": round(valor_recebidos, 2),
        "proximo_recebido_data": proximo_recebido_data,
        "proximo_recebido_valor": round(proximo_recebido_valor, 2),
        "tem_switching_futuro_ate_data": _sim_nao(tem_switching),
        "qtd_switchings_futuros_ate_data": qtd_switchings,
        "tem_evidencia_aporte_planejado": evidencia_aporte_planejado,
        "hipotese_temporal_t1": hipotese,
        "nivel_evidencia_t1": nivel,
        "acao_recomendada_t2": acao,
        "observacao_t1": obs,
    }


def main() -> int:
    df_t0 = _carregar_csv_t0()

    if df_t0 is None:
        print("status_geral_t1=falha_investigacao_fontes_temporais_110_sem_lote")
        return 1

    print(f"qtd_linhas_t0={len(df_t0)}")
    print(f"data_referencia_t1={DATA_REFERENCIA.date()}")

    faltantes = [c for c in COLUNAS_T0_OBRIGATORIAS if c not in df_t0.columns]
    print(f"qtd_colunas_t0_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t0_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        print("status_geral_t1=falha_investigacao_fontes_temporais_110_sem_lote")
        return 1

    salarios = _preparar_salarios()
    switching = _preparar_switching()
    evidencia_aporte = _detectar_evidencia_aporte_planejado(df_t0)

    print(f"tem_evidencia_aporte_planejado_global={evidencia_aporte}")

    investigacoes = df_t0.apply(
        lambda row: _investigar_linha(row, salarios, switching, evidencia_aporte),
        axis=1,
        result_type="expand",
    )

    saida = pd.concat(
        [df_t0.reset_index(drop=True), investigacoes.reset_index(drop=True)],
        axis=1,
    )

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()
    saida_final["_data_ordem"] = pd.to_datetime(saida_final["data"], errors="coerce")
    saida_final = (
        saida_final
        .sort_values(["_data_ordem", "conta", "valor"], na_position="last")
        .drop(columns=["_data_ordem"])
    )

    CSV_T1.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_T1, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final
        .groupby(
            ["classe_t0", "subclasse_t0", "hipotese_temporal_t1", "nivel_evidencia_t1"],
            dropna=False,
        )
        .size()
        .reset_index(name="qtd_pagamentos")
        .sort_values(["classe_t0", "subclasse_t0", "hipotese_temporal_t1", "nivel_evidencia_t1"])
    )
    resumo.to_csv(CSV_RESUMO_T1, index=False, encoding="utf-8-sig")

    qtd_linhas = int(len(saida_final))
    qtd_nao_investigadas = int(saida_final["hipotese_temporal_t1"].astype(str).str.len().eq(0).sum())
    qtd_investigadas = int(qtd_linhas - qtd_nao_investigadas)

    qtd_com_recebido = int(saida_final["tem_recebido_futuro_ate_data"].eq("sim").sum())
    qtd_sem_recebido = int(saida_final["tem_recebido_futuro_ate_data"].eq("nao").sum())
    qtd_com_switching = int(saida_final["tem_switching_futuro_ate_data"].eq("sim").sum())
    qtd_com_aporte = int(saida_final["tem_evidencia_aporte_planejado"].eq("sim").sum())

    print(f"qtd_linhas_investigadas_t1={qtd_investigadas}")
    print(f"qtd_linhas_nao_investigadas_t1={qtd_nao_investigadas}")
    print(f"qtd_com_recebido_futuro_ate_data={qtd_com_recebido}")
    print(f"qtd_sem_recebido_futuro_ate_data={qtd_sem_recebido}")
    print(f"qtd_com_switching_futuro_ate_data={qtd_com_switching}")
    print(f"qtd_com_evidencia_aporte_planejado={qtd_com_aporte}")

    print("\nresumo_hipoteses_t1=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t1_aluguel_2026_06_12_investigada={_sentinela('2026-06-12', 'Aluguel')}")
    print(f"sentinela_t1_condominio_2026_06_20_investigada={_sentinela('2026-06-20', 'Condomínio')}")

    print(f"csv_investigacao_t1={CSV_T1}")
    print(f"csv_resumo_t1={CSV_RESUMO_T1}")

    status = "investigacao_fontes_temporais_110_sem_lote_gerada"
    if len(df_t0) != 110:
        status = "falha_investigacao_fontes_temporais_110_sem_lote"
    if qtd_investigadas != 110:
        status = "falha_investigacao_fontes_temporais_110_sem_lote"
    if qtd_nao_investigadas != 0:
        status = "falha_investigacao_fontes_temporais_110_sem_lote"

    print(f"status_geral_t1={status}")
    return 0 if status == "investigacao_fontes_temporais_110_sem_lote_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

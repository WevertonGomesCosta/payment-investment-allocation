from __future__ import annotations

import math
from typing import Any

import pandas as pd

from tipos import (
    ClasseBrutaLote,
    ConfigProjeto,
    FaseTemporal,
    StatusGastoModelo,
    StatusLote,
)


GASTOS_NORM_COLUMNS = [
    "id_gasto",
    "data_gasto",
    "descricao_gasto",
    "valor_gasto_centavos",
    "flag_pago_historico",
    "lote_usado_1_raw",
    "lote_usado_2_raw",
    "fase_temporal",
    "status_modelo",
    "valor_em_aberto_centavos",
]

LOTES_NORM_COLUMNS = [
    "id_lote",
    "data_entrada_lote",
    "valor_original_centavos",
    "valor_saldo_centavos",
    "valor_principal_remanescente_centavos",
    "valor_bruto_remanescente_centavos",
    "valor_consumido_historico_centavos",
    "quantidade_consumos_historicos",
    "data_ultima_atualizacao",
    "data_ultimo_consumo_historico",
    "flag_usado_historico",
    "investimento_raw",
    "classe_bruta_lote",
    "status_lote",
    "carteira_atual",
    "id_carteira_atual",
    "flag_carteira_encontrada",
    "flag_historico",
    "flag_futuro",
    "flag_pode_pagar",
    "flag_pode_aportar",
    "flag_pode_switchar",
    "data_elegivel_resgate",
    "data_elegivel_switching",
    "valor_economico_centavos",
    "valor_liquido_resgatavel_centavos",
]

CARTEIRAS_NORM_COLUMNS = [
    "id_carteira",
    "nome_carteira",
    "tipo_produto",
    "indexador",
    "flag_ativa",
    "flag_isento_ir",
    "flag_somente_combo",
    "taxa_base",
    "taxa_bonus",
    "dias_bonus",
    "prazo_dias",
    "carencia_dias",
    "aplicacao_minima_centavos",
    "aplicacao_maxima_centavos",
    "produto_base",
    "produto_bonus",
    "ratio_base",
    "ratio_bonus",
    "banco_emissor",
    "score_banco",
    "risco_real",
    "max_usos",
]


def _normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value).strip()



def normalize_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.normalize()



def money_to_cents(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce").fillna(0.0)
    return (numeric * 100).round().astype("int64")



def to_bool(series: pd.Series, true_values: set[str] | None = None) -> pd.Series:
    true_values = true_values or {"sim", "s", "true", "1", "x", "yes"}

    def convert(value: Any) -> bool:
        if pd.isna(value):
            return False
        text = _normalize_text(value).lower()
        return text in true_values

    return series.apply(convert).astype(bool)



def normalize_rate_fraction(series: pd.Series) -> pd.Series:
    def convert(value: Any) -> float:
        if pd.isna(value):
            return 0.0
        text = _normalize_text(value).replace("%", "").replace(",", ".")
        if text == "":
            return 0.0
        numeric = float(text)
        if numeric > 10:
            return numeric / 100.0
        return numeric

    return series.apply(convert).astype("float64")



def classify_lote_from_investimento(value: Any) -> ClasseBrutaLote:
    text = _normalize_text(value)
    if text == "-":
        return ClasseBrutaLote.BLOQUEADO
    if text == "":
        return ClasseBrutaLote.LIVRE
    return ClasseBrutaLote.INVESTIDO



def normalize_gastos(df_raw: pd.DataFrame, config: ConfigProjeto) -> pd.DataFrame:
    cols = config.colunas_gastos
    out = pd.DataFrame()
    out["id_gasto"] = [f"GASTO_{i + 1:05d}" for i in range(len(df_raw))]
    out["data_gasto"] = normalize_dates(df_raw[cols.data])
    out["descricao_gasto"] = df_raw[cols.descricao].fillna("").astype(str).str.strip()
    out["valor_gasto_centavos"] = money_to_cents(df_raw[cols.valor])
    pago_raw = df_raw[cols.pago]
    out["flag_pago_historico"] = (~pago_raw.isna()) if config.politicas_modelo.tratar_pago_nulo_como_nao else to_bool(pago_raw)
    out["lote_usado_1_raw"] = df_raw[cols.lote_usado_1].fillna("").astype(str).str.strip()
    out["lote_usado_2_raw"] = df_raw[cols.lote_usado_2].fillna("").astype(str).str.strip()
    out["fase_temporal"] = out["flag_pago_historico"].map(
        {True: FaseTemporal.HISTORICO.value, False: FaseTemporal.FUTURO.value}
    )
    out["status_modelo"] = out["flag_pago_historico"].map(
        {True: StatusGastoModelo.EXECUTADO.value, False: StatusGastoModelo.PENDENTE.value}
    )
    out["valor_em_aberto_centavos"] = out["valor_gasto_centavos"]
    out.loc[out["flag_pago_historico"], "valor_em_aberto_centavos"] = 0
    return out[GASTOS_NORM_COLUMNS]



def normalize_lotes(df_raw: pd.DataFrame, config: ConfigProjeto) -> pd.DataFrame:
    cols = config.colunas_lotes
    out = pd.DataFrame()
    out["id_lote"] = df_raw[cols.id_lote].fillna("").astype(str).str.strip()
    out["data_entrada_lote"] = normalize_dates(df_raw[cols.data_entrada])
    out["valor_original_centavos"] = money_to_cents(df_raw[cols.valor_original])
    out["valor_saldo_centavos"] = out["valor_original_centavos"]
    out["valor_principal_remanescente_centavos"] = out["valor_original_centavos"]
    out["valor_bruto_remanescente_centavos"] = out["valor_original_centavos"]
    out["valor_consumido_historico_centavos"] = 0
    out["quantidade_consumos_historicos"] = 0
    out["data_ultima_atualizacao"] = out["data_entrada_lote"]
    out["data_ultimo_consumo_historico"] = pd.NaT
    out["flag_usado_historico"] = False
    out["investimento_raw"] = df_raw[cols.investimento].fillna("").astype(str).str.strip()
    out["classe_bruta_lote"] = out["investimento_raw"].apply(lambda x: classify_lote_from_investimento(x).value)

    out["status_lote"] = StatusLote.LIVRE_FUTURO.value
    out.loc[out["classe_bruta_lote"] == ClasseBrutaLote.INVESTIDO.value, "status_lote"] = StatusLote.INVESTIDO_ATUAL.value
    out.loc[out["classe_bruta_lote"] == ClasseBrutaLote.BLOQUEADO.value, "status_lote"] = StatusLote.BLOQUEADO_MODELO.value

    out["carteira_atual"] = out["investimento_raw"].where(
        out["classe_bruta_lote"] == ClasseBrutaLote.INVESTIDO.value,
        "",
    )
    out["id_carteira_atual"] = ""
    out["flag_carteira_encontrada"] = False
    out["flag_historico"] = False
    out["flag_futuro"] = True
    out["flag_pode_pagar"] = out["classe_bruta_lote"] == ClasseBrutaLote.LIVRE.value
    out["flag_pode_aportar"] = out["classe_bruta_lote"] == ClasseBrutaLote.LIVRE.value
    out["flag_pode_switchar"] = out["classe_bruta_lote"] == ClasseBrutaLote.INVESTIDO.value
    out["data_elegivel_resgate"] = pd.NaT
    out["data_elegivel_switching"] = pd.NaT
    out["valor_economico_centavos"] = out["valor_original_centavos"]
    out["valor_liquido_resgatavel_centavos"] = out["valor_original_centavos"]
    out["quantidade_consumos_historicos"] = out["quantidade_consumos_historicos"].astype("int32")
    return out[LOTES_NORM_COLUMNS]



def normalize_carteiras(df_raw: pd.DataFrame, config: ConfigProjeto) -> pd.DataFrame:
    cols = config.colunas_carteiras
    out = pd.DataFrame()
    out["id_carteira"] = [f"CARTEIRA_{i + 1:04d}" for i in range(len(df_raw))]
    out["nome_carteira"] = df_raw[cols.nome].fillna("").astype(str).str.strip()
    out["tipo_produto"] = df_raw[cols.tipo].fillna("").astype(str).str.strip()
    out["indexador"] = df_raw[cols.indexador].fillna("").astype(str).str.strip()
    out["flag_ativa"] = to_bool(df_raw[cols.ativo])
    out["flag_isento_ir"] = to_bool(df_raw[cols.isento_ir])
    out["flag_somente_combo"] = to_bool(df_raw[cols.somente_combo])
    out["taxa_base"] = normalize_rate_fraction(df_raw[cols.taxa_base])
    out["taxa_bonus"] = normalize_rate_fraction(df_raw[cols.taxa_bonus])
    out["dias_bonus"] = pd.to_numeric(df_raw[cols.dias_bonus], errors="coerce").fillna(0).astype("int32")
    out["prazo_dias"] = pd.to_numeric(df_raw[cols.prazo_dias], errors="coerce").fillna(0).astype("int32")
    out["carencia_dias"] = pd.to_numeric(df_raw[cols.carencia_dias], errors="coerce").fillna(0).astype("int32")
    out["aplicacao_minima_centavos"] = money_to_cents(df_raw[cols.aplicacao_minima])
    out["aplicacao_maxima_centavos"] = money_to_cents(df_raw[cols.aplicacao_maxima])
    out["produto_base"] = df_raw[cols.produto_base].fillna("").astype(str).str.strip()
    out["produto_bonus"] = df_raw[cols.produto_bonus].fillna("").astype(str).str.strip()
    out["ratio_base"] = pd.to_numeric(df_raw[cols.ratio_base], errors="coerce").fillna(0.0).astype("float64")
    out["ratio_bonus"] = pd.to_numeric(df_raw[cols.ratio_bonus], errors="coerce").fillna(0.0).astype("float64")
    out["banco_emissor"] = df_raw[cols.banco_emissor].fillna("").astype(str).str.strip()
    out["score_banco"] = pd.to_numeric(df_raw[cols.score_banco], errors="coerce").fillna(0.0).astype("float64")
    out["risco_real"] = df_raw[cols.risco_real].fillna("").astype(str).str.strip()
    out["max_usos"] = pd.to_numeric(df_raw[cols.max_usos], errors="coerce").fillna(0).astype("int32")
    return out[CARTEIRAS_NORM_COLUMNS]



def vincular_lotes_investidos_a_carteiras(
    lotes: pd.DataFrame,
    carteiras: pd.DataFrame,
) -> pd.DataFrame:
    """
    Vincula lotes investidos à carteira normalizada pelo nome da carteira atual.
    Mantém nomes não encontrados vazios para auditoria posterior.
    """
    out = lotes.copy()
    mapa_nome_para_id = dict(zip(carteiras["nome_carteira"].astype(str), carteiras["id_carteira"].astype(str)))

    investidos = out["classe_bruta_lote"] == ClasseBrutaLote.INVESTIDO.value
    nomes = out.loc[investidos, "carteira_atual"].astype(str)
    out.loc[investidos, "id_carteira_atual"] = nomes.map(mapa_nome_para_id).fillna("")
    out.loc[investidos, "flag_carteira_encontrada"] = out.loc[investidos, "id_carteira_atual"].ne("")
    return out

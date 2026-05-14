from __future__ import annotations

from pathlib import Path
from typing import Any
import subprocess

import pandas as pd

from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

VERSAO_BASELINE = "V225"
CSV_S6 = Path("saidas/diagnostico/auditoria_separacao_previsao_materializacao_v17_f0_s6.csv")
SCRIPT_S6 = Path("scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py")
SCRIPT_S2 = Path("scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py")
SCRIPT_S4 = Path("scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py")


def _norm_txt(v: Any) -> str:
    return str(v or "").strip().lower()


def _bool_sn(v: bool) -> str:
    return "sim" if bool(v) else "nao"


def _classificar_regra_base(reg: dict[str, Any]) -> dict[str, Any]:
    classe = _norm_txt(reg.get("classe_temporal_s6"))
    status_ciclo = _norm_txt(reg.get("status_ciclo"))
    fonte_futura = _norm_txt(reg.get("fonte_futura")) == "sim"
    materializada = _norm_txt(reg.get("materializada")) == "sim"
    saldo = float(reg.get("saldo_observado") or 0.0)

    elegivel_temporal = materializada and not fonte_futura
    elegivel_liquidez = saldo > 0
    motivo = ""

    if classe == "salario_previsto_futuro_nao_materializado":
        elegivel_temporal = False
        reg["materializada"] = "nao"
        motivo = "previsao_futura_nao_materializada"
    elif classe == "lacuna_real_de_integracao":
        elegivel_temporal = False
        motivo = "lacuna_real_de_integracao"
    elif classe == "uso_pre_aplicacao_no_mes_sem_vinculo_linha":
        elegivel_temporal = False
        motivo = "uso_pre_aplicacao_sem_vinculo_temporal"
    elif fonte_futura:
        elegivel_temporal = False
        motivo = "fonte_futura_nao_materializada"

    if status_ciclo == "exaurido":
        elegivel_temporal = False
        elegivel_liquidez = False
        motivo = "lote_exaurido"
    elif status_ciclo == "migrado_por_switching":
        elegivel_temporal = False
        motivo = "lote_migrado_por_switching"
    elif status_ciclo == "ativo_pos_switching" and not materializada:
        elegivel_temporal = False
        motivo = "lote_pos_switching_nao_materializado"

    elegivel = bool(elegivel_temporal and elegivel_liquidez)
    reg["elegivel_temporalmente"] = _bool_sn(elegivel_temporal)
    reg["elegivel_liquidez_carencia"] = _bool_sn(elegivel_liquidez)
    reg["elegivel_para_pagamento"] = _bool_sn(elegivel)
    reg["pode_ser_lote_sugerido"] = _bool_sn(elegivel)
    reg["motivo_bloqueio"] = motivo
    reg["elegibilidade_cumulativa"] = "nao_determinado"
    reg["motivo_bloqueio_cumulativo"] = "nao_disponivel_sem_motor"
    return reg


def _carregar_s6_df() -> pd.DataFrame:
    s6_origem = "csv_existente"
    if not CSV_S6.exists():
        scripts = [SCRIPT_S2, SCRIPT_S4, SCRIPT_S6]
        if any(not p.exists() for p in scripts):
            raise RuntimeError("erro_recomposicao_cadeia_s6_indisponivel")
        s6_origem = "recomposta"
        try:
            for p in scripts:
                subprocess.run(["python", str(p)], check=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError("erro_recomposicao_cadeia_s6_falhou") from exc
    if not CSV_S6.exists():
        raise RuntimeError("erro_s6_csv_nao_produzido")
    df = pd.read_csv(CSV_S6)
    if df.empty:
        raise RuntimeError("erro_csv_s6_vazio_para_matriz_elegibilidade")
    col = _resolver_coluna_classe_s6(df)
    if not col:
        raise RuntimeError("erro_coluna_classe_s6_nao_encontrada")
    serie = df[col].astype(str).str.strip().str.lower()
    if serie.eq("").all():
        raise RuntimeError("erro_csv_s6_vazio_para_matriz_elegibilidade")
    df["_s6_origem"] = s6_origem
    df["_coluna_classe_s6_usada"] = col
    return df


def _resolver_coluna_classe_s6(s6_df: pd.DataFrame) -> str:
    for col in ("classe_s6", "classe_temporal_s6", "classe_politica_s6"):
        if col in s6_df.columns:
            return col
    return ""


def construir_matriz_elegibilidade_fontes_s7b(contexto, *, data_referencia=None):
    saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
    data_ref = str(data_referencia or saida.data_referencia)

    s6_df = _carregar_s6_df()
    classe_counts = {}
    coluna_classe_s6_usada = "nao_aplicavel_sem_csv_s6"
    col = _resolver_coluna_classe_s6(s6_df)
    if not col:
        raise ValueError("erro_coluna_classe_s6_nao_encontrada")
    coluna_classe_s6_usada = col
    serie = s6_df[col].astype(str).str.strip().str.lower()
    classe_counts = serie.value_counts().to_dict()

    registros: list[dict[str, Any]] = []

    for lote in saida.lotes_ativos:
        valor = float(lote.get("Saldo rem") or lote.get("Líquido") or lote.get("Valor original") or 0.0)
        lote_nome = str(lote.get("Lote") or lote.get("nome") or lote.get("id") or "lote_ativo")
        status_field = _norm_txt(lote.get("Status"))
        status_sw = "pos_switching" if "switching" in status_field else "nao"
        classe = "salario_materializado_em_aporte"
        if status_sw == "pos_switching":
            classe = "salario_materializado_em_aporte"
        registros.append(
            {
                "data_referencia": data_ref,
                "fonte_id": lote_nome,
                "tipo_fonte": "lote",
                "classe_temporal_s6": classe,
                "origem_materializacao": "aporte",
                "materializada": "sim",
                "fonte_futura": "nao",
                "saldo_observado": valor,
                "status_ciclo": "ativo_pos_switching" if "ativo_pos_switching" in status_field else "ativo",
                "status_switching": status_sw,
                "fonte_normativa": "S.6+Q.FINAL",
                "coluna_classe_s6_usada": coluna_classe_s6_usada,
            }
        )

    for lote in saida.lotes_exauridos:
        registros.append(
            {
                "data_referencia": data_ref,
                "fonte_id": str(lote.get("Lote") or lote.get("nome") or lote.get("id") or "lote_exaurido"),
                "tipo_fonte": "lote",
                "classe_temporal_s6": "salario_materializado_em_aporte",
                "origem_materializacao": "aporte",
                "materializada": "sim",
                "fonte_futura": "nao",
                "saldo_observado": float(lote.get("Saldo rem") or lote.get("Líquido") or 0.0),
                "status_ciclo": "migrado_por_switching" if "migrado" in _norm_txt(lote.get("Status")) else "exaurido",
                "status_switching": "pos_switching"
                if any(
                    "switching" in _norm_txt(lote.get(chave))
                    for chave in ("Status", "fonte_detalhada", "Origem migrada", "Evento switching ID")
                )
                else "nao",
                "fonte_normativa": "S.6+Q.FINAL",
                "coluna_classe_s6_usada": coluna_classe_s6_usada,
            }
        )

    for classe in [
        "salario_previsto_futuro_nao_materializado",
        "lacuna_real_de_integracao",
        "uso_pre_aplicacao_no_mes_sem_vinculo_linha",
    ]:
        qtd = int(classe_counts.get(classe, 0))
        subset = s6_df[serie == classe].copy()
        for i, (_, row_s6) in enumerate(subset.iterrows(), start=1):
            fonte_id_real = str(row_s6.get("salario_id") or row_s6.get("descricao_salario") or "").strip()
            data_s6 = str(row_s6.get("data_recebimento_salario") or "").strip()
            valor_s6 = row_s6.get("valor_liquido_salario")
            chave_op = "|".join([fonte_id_real, data_s6, str(valor_s6)])
            linkavel = "sim" if fonte_id_real else "nao"
            registros.append(
                {
                    "data_referencia": data_ref,
                    "registro_s6_id": f"{classe}_{i}",
                    "fonte_id": chave_op if chave_op.strip("|") else f"s6_diag::{classe}::{i}",
                    "fonte_id_real": fonte_id_real,
                    "chave_operacional_s6": chave_op,
                    "tipo_fonte": "classe_s6",
                    "classe_temporal_s6": classe,
                    "classe_politica_s6": str(row_s6.get("classe_politica_s6") or classe),
                    "data_recebimento_s6": data_s6,
                    "origem_s6": str(row_s6.get("camada_temporal_s6") or ""),
                    "valor_s6": valor_s6,
                    "linkavel_ao_fluxo": linkavel,
                    "motivo_nao_linkavel": "" if linkavel == "sim" else "sem_chave_operacional_s6",
                    "origem_materializacao": "nao_materializada" if "materializado" in classe else "diagnostico",
                    "materializada": "nao",
                    "fonte_futura": "sim" if classe == "salario_previsto_futuro_nao_materializado" else "nao",
                    "saldo_observado": 0.0,
                    "status_ciclo": "nao_lote",
                    "status_switching": "nao",
                    "fonte_normativa": "S.6",
                    "s6_origem": str(row_s6.get("_s6_origem") or "csv_existente"),
                    "coluna_classe_s6_usada": coluna_classe_s6_usada,
                    "fonte_id_sintetico_s6": "nao" if linkavel == "sim" else "sim",
                }
            )

    classificados = [_classificar_regra_base(r) for r in registros]
    return pd.DataFrame(classificados)

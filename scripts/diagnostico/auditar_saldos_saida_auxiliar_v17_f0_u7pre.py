from __future__ import annotations

import math
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DIR_DIAG = BASE_DIR / "saidas/diagnostico"

ARQ_U4_XLSX = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u4.xlsx"

ARQ_U6_RESUMO = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_resumo.csv"
ARQ_U6_ABAS = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_abas.csv"
ARQ_U6_CAMPOS = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_campos.csv"
ARQ_U6_GATES = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_gates.csv"
ARQ_U6_BLOQUEIOS = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_bloqueios.csv"
ARQ_LOG_U6 = BASE_DIR / "logs/iteracoes/ME-V17-F0-U6_GOVERNANCA_PROMOCAO_SAIDA_AUXILIAR.md"

ARQ_DADOS_FINANCEIROS = BASE_DIR / "dados/dados_financeiros.xlsx"

ARQ_RESUMO_U7PRE = DIR_DIAG / "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_resumo.csv"
ARQ_LINHAS_U7PRE = DIR_DIAG / "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_linhas.csv"
ARQ_MULTIFONTE_U7PRE = DIR_DIAG / "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_multifonte.csv"
ARQ_REFERENCIAS_U7PRE = DIR_DIAG / "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_referencias.csv"
ARQ_BLOQUEIOS_U7PRE = DIR_DIAG / "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_bloqueios.csv"

ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U7PRE_AUDITORIA_SALDOS_SAIDA_AUXILIAR.md"

STATUS_GERAL = "auditoria_saldos_saida_auxiliar_v17_f0_u7pre_gerada"

DECISAO_APROVADOS = "saldos_aprovados_para_promocao_futura"
DECISAO_RESTRICOES = "saldos_aprovados_apenas_com_restricoes"
DECISAO_NAO_APROVADOS = "saldos_nao_aprovados_para_promocao"

COL_SALDO_FONTE = "saldo_fonte_considerado"
COL_SALDO_REMANESCENTE = "saldo_remanescente_diagnostico"
COL_FONTE = "fonte"
COL_CHAVE = "chave_pagamento"

TOL = 0.01


def normalizar_texto(x: Any) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if s.endswith(".0"):
        try:
            f = float(s)
            if f.is_integer():
                return str(int(f))
        except ValueError:
            pass
    return s


def normalizar_comp(x: Any) -> str:
    s = normalizar_texto(x)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def normalizar_chave(x: Any) -> str:
    s = normalizar_comp(x)
    s = s.replace("r$", "")
    s = s.replace("  ", " ")
    return s


def to_float(x: Any) -> float | None:
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        f = float(x)
        if math.isnan(f):
            return None
        return f

    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "n/d", "na", "-", "null"}:
        return None

    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")

    try:
        f = float(s)
    except ValueError:
        return None

    if math.isnan(f):
        return None
    return f


def round2(x: Any) -> float | None:
    f = to_float(x)
    if f is None:
        return None
    return round(f + 1e-12, 2)


def carregar_csv(path: Path, nome: str, instrucao: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo obrigatório ausente para U.7-PRE ({nome}): {path}\n{instrucao}")
    return pd.read_csv(path)


def carregar_xlsx_u4(path: Path) -> dict[str, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(
            f"XLSX auxiliar U.4 ausente: {path}\n"
            "Execute antes: python -B scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py"
        )

    abas_necessarias = ["Linhas_Operacionais", "Multifonte", "Pagamentos", "Pendencias", "Metadados"]
    xls = pd.ExcelFile(path)
    faltantes = [aba for aba in abas_necessarias if aba not in xls.sheet_names]
    if faltantes:
        raise ValueError(f"Abas obrigatórias ausentes no XLSX U.4: {faltantes}")

    return {aba: pd.read_excel(path, sheet_name=aba) for aba in abas_necessarias}


def validar_colunas(df: pd.DataFrame, aba: str, colunas: list[str]) -> None:
    faltantes = [c for c in colunas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes na aba {aba}: {faltantes}")


def confirmar_classificacao_u6(campos_u6: pd.DataFrame) -> tuple[int, int, pd.DataFrame]:
    esperado = {COL_SALDO_FONTE, COL_SALDO_REMANESCENTE}
    linhas = campos_u6.loc[campos_u6["campo"].astype(str).isin(esperado)].copy()

    linhas["classificacao_esperada"] = "exige_precondicao"
    linhas["governanca_ok"] = linhas["classificacao_governanca"].astype(str).eq("exige_precondicao")

    qtd_ok = int(linhas["governanca_ok"].sum())
    qtd_div = int((~linhas["governanca_ok"]).sum())

    return qtd_ok, qtd_div, linhas


def detectar_colunas_referencia(df: pd.DataFrame) -> dict[str, Any]:
    colunas = list(df.columns)
    norm = {c: normalizar_comp(c) for c in colunas}

    candidatas_chave = [
        c for c, n in norm.items()
        if (
            n in {"lote", "fonte", "nome_lote", "id_lote", "descricao_lote", "lote_informado"}
            or ("lote" in n and not any(t in n for t in ["valor", "saldo", "bruto", "liquido", "data"]))
        )
    ]

    candidatas_saldo_liquido = [
        c for c, n in norm.items()
        if (
            ("saldo" in n and "liquido" in n)
            or ("valor" in n and "liquido" in n and "saldo" in n)
            or ("saldo" in n and "remanescente" in n and "diagnostico" not in n)
        )
    ]

    candidatas_data_status = [
        c for c, n in norm.items()
        if ("data" in n or "status" in n or "referencia" in n or "posicao" in n)
    ]

    return {
        "candidatas_chave": candidatas_chave,
        "candidatas_saldo_liquido": candidatas_saldo_liquido,
        "candidatas_data_status": candidatas_data_status,
    }


def avaliar_referencia_df(origem: str, detalhe: str, df: pd.DataFrame) -> tuple[pd.DataFrame | None, dict[str, Any]]:
    det = detectar_colunas_referencia(df)

    candidatas_chave = det["candidatas_chave"]
    candidatas_saldo = det["candidatas_saldo_liquido"]
    candidatas_data_status = det["candidatas_data_status"]

    aceita = (
        len(candidatas_chave) == 1
        and len(candidatas_saldo) == 1
        and len(candidatas_data_status) >= 1
    )

    info = {
        "origem": origem,
        "detalhe": detalhe,
        "qtd_linhas": len(df),
        "qtd_colunas": len(df.columns),
        "candidatas_chave": ";".join(map(str, candidatas_chave)),
        "candidatas_saldo_liquido": ";".join(map(str, candidatas_saldo)),
        "candidatas_data_status": ";".join(map(str, candidatas_data_status)),
        "referencia_aceita": "sim" if aceita else "nao",
        "motivo_rejeicao": "",
    }

    if not aceita:
        motivos = []
        if len(candidatas_chave) != 1:
            motivos.append(f"qtd_colunas_chave={len(candidatas_chave)}")
        if len(candidatas_saldo) != 1:
            motivos.append(f"qtd_colunas_saldo_liquido={len(candidatas_saldo)}")
        if len(candidatas_data_status) < 1:
            motivos.append("sem_coluna_data_status_referencia")
        info["motivo_rejeicao"] = "|".join(motivos)
        return None, info

    col_chave = candidatas_chave[0]
    col_saldo = candidatas_saldo[0]
    col_data_status = candidatas_data_status[0]

    ref = df[[col_chave, col_saldo, col_data_status]].copy()
    ref.columns = ["fonte_referencia", "saldo_liquido_real_referencia", "data_status_referencia"]
    ref["fonte_referencia_norm"] = ref["fonte_referencia"].map(normalizar_chave)
    ref["saldo_liquido_real_referencia_num"] = ref["saldo_liquido_real_referencia"].map(round2)
    ref = ref.loc[
        (ref["fonte_referencia_norm"] != "")
        & ref["saldo_liquido_real_referencia_num"].notna()
    ].copy()

    if ref.empty:
        info["referencia_aceita"] = "nao"
        info["motivo_rejeicao"] = "referencia_sem_linhas_validas"
        return None, info

    duplicadas = int(ref["fonte_referencia_norm"].duplicated(keep=False).sum())
    if duplicadas > 0:
        info["referencia_aceita"] = "nao"
        info["motivo_rejeicao"] = f"chaves_de_referencia_duplicadas={duplicadas}"
        return None, info

    info["qtd_linhas_validas_referencia"] = len(ref)
    return ref, info


def buscar_referencias_saldo_liquido() -> tuple[pd.DataFrame | None, pd.DataFrame]:
    referencias_info: list[dict[str, Any]] = []
    referencias_aceitas: list[pd.DataFrame] = []

    if ARQ_DADOS_FINANCEIROS.exists():
        try:
            xls = pd.ExcelFile(ARQ_DADOS_FINANCEIROS)
            if "Inventário de Lotes" in xls.sheet_names:
                inv = pd.read_excel(ARQ_DADOS_FINANCEIROS, sheet_name="Inventário de Lotes")
                ref, info = avaliar_referencia_df(
                    "dados/dados_financeiros.xlsx",
                    "aba=Inventário de Lotes",
                    inv,
                )
                referencias_info.append(info)
                if ref is not None:
                    ref["origem_referencia"] = "dados/dados_financeiros.xlsx::Inventário de Lotes"
                    referencias_aceitas.append(ref)
            else:
                referencias_info.append({
                    "origem": "dados/dados_financeiros.xlsx",
                    "detalhe": "aba=Inventário de Lotes",
                    "qtd_linhas": 0,
                    "qtd_colunas": 0,
                    "candidatas_chave": "",
                    "candidatas_saldo_liquido": "",
                    "candidatas_data_status": "",
                    "referencia_aceita": "nao",
                    "motivo_rejeicao": "aba_inventario_de_lotes_ausente",
                })
        except Exception as exc:
            referencias_info.append({
                "origem": "dados/dados_financeiros.xlsx",
                "detalhe": "aba=Inventário de Lotes",
                "qtd_linhas": 0,
                "qtd_colunas": 0,
                "candidatas_chave": "",
                "candidatas_saldo_liquido": "",
                "candidatas_data_status": "",
                "referencia_aceita": "nao",
                "motivo_rejeicao": f"erro_leitura:{type(exc).__name__}:{exc}",
            })
    else:
        referencias_info.append({
            "origem": "dados/dados_financeiros.xlsx",
            "detalhe": "aba=Inventário de Lotes",
            "qtd_linhas": 0,
            "qtd_colunas": 0,
            "candidatas_chave": "",
            "candidatas_saldo_liquido": "",
            "candidatas_data_status": "",
            "referencia_aceita": "nao",
            "motivo_rejeicao": "arquivo_ausente",
        })

    # Busca conservadora em artefatos diagnósticos já existentes.
    # Exclui explicitamente os próprios artefatos de saída auxiliar/governança/auditoria de saldos,
    # para evitar usar o objeto auditado como fonte de verdade.
    padroes_excluir = [
        "saida_operacional_pagamentos_v17_f0_u3",
        "saida_operacional_pagamentos_v17_f0_u4",
        "auditoria_consistencia_exportacao_auxiliar",
        "governanca_promocao_saida_auxiliar",
        "auditoria_saldos_saida_auxiliar",
    ]

    for csv_path in sorted(DIR_DIAG.glob("*.csv")):
        nome = csv_path.name
        if any(p in nome for p in padroes_excluir):
            continue
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:
            referencias_info.append({
                "origem": str(csv_path.relative_to(BASE_DIR)),
                "detalhe": "csv_diagnostico",
                "qtd_linhas": 0,
                "qtd_colunas": 0,
                "candidatas_chave": "",
                "candidatas_saldo_liquido": "",
                "candidatas_data_status": "",
                "referencia_aceita": "nao",
                "motivo_rejeicao": f"erro_leitura:{type(exc).__name__}:{exc}",
            })
            continue

        ref, info = avaliar_referencia_df(str(csv_path.relative_to(BASE_DIR)), "csv_diagnostico", df)
        referencias_info.append(info)
        if ref is not None:
            ref["origem_referencia"] = str(csv_path.relative_to(BASE_DIR))
            referencias_aceitas.append(ref)

    referencias_df = pd.DataFrame(referencias_info)

    if not referencias_aceitas:
        return None, referencias_df

    ref_total = pd.concat(referencias_aceitas, ignore_index=True)
    duplicadas = ref_total["fonte_referencia_norm"].duplicated(keep=False)

    if duplicadas.any():
        referencias_df.loc[len(referencias_df)] = {
            "origem": "referencias_consolidadas",
            "detalhe": "validacao_final",
            "qtd_linhas": len(ref_total),
            "qtd_colunas": len(ref_total.columns),
            "candidatas_chave": "fonte_referencia_norm",
            "candidatas_saldo_liquido": "saldo_liquido_real_referencia_num",
            "candidatas_data_status": "data_status_referencia",
            "referencia_aceita": "nao",
            "motivo_rejeicao": "chaves_duplicadas_entre_referencias",
        }
        return None, referencias_df

    referencias_df.loc[len(referencias_df)] = {
        "origem": "referencias_consolidadas",
        "detalhe": "validacao_final",
        "qtd_linhas": len(ref_total),
        "qtd_colunas": len(ref_total.columns),
        "candidatas_chave": "fonte_referencia_norm",
        "candidatas_saldo_liquido": "saldo_liquido_real_referencia_num",
        "candidatas_data_status": "data_status_referencia",
        "referencia_aceita": "sim",
        "motivo_rejeicao": "",
    }

    return ref_total, referencias_df


def classificar_linha_saldo(row: pd.Series, ref_map: dict[str, dict[str, Any]] | None) -> dict[str, Any]:
    fonte = normalizar_texto(row.get(COL_FONTE))
    fonte_norm = normalizar_chave(fonte)

    saldo_fonte = round2(row.get(COL_SALDO_FONTE))
    saldo_rem = round2(row.get(COL_SALDO_REMANESCENTE))

    candidato_fifo = normalizar_comp(row.get("candidato_fifo_detectado")) == "sim"
    pendencia_sem_lote = normalizar_comp(row.get("pendencia_sem_lote_sugerido")) == "sim"
    origem = normalizar_comp(row.get("origem_linha_u3"))

    if candidato_fifo or "candidato_fifo" in origem:
        categoria = "linha_fifo_diagnostica_nao_promovivel"
        saldo_ref = None
        diferenca_saldo_fonte = None
        diferenca_saldo_rem = None
        origem_ref = ""
        tem_ref = "nao"
    elif pendencia_sem_lote:
        categoria = "linha_pendencia_nao_promovivel"
        saldo_ref = None
        diferenca_saldo_fonte = None
        diferenca_saldo_rem = None
        origem_ref = ""
        tem_ref = "nao"
    elif not fonte_norm:
        categoria = "fonte_sem_chave_de_lote"
        saldo_ref = None
        diferenca_saldo_fonte = None
        diferenca_saldo_rem = None
        origem_ref = ""
        tem_ref = "nao"
    elif saldo_fonte is None or saldo_rem is None:
        categoria = "campo_saldo_vazio_ou_nao_numerico"
        saldo_ref = None
        diferenca_saldo_fonte = None
        diferenca_saldo_rem = None
        origem_ref = ""
        tem_ref = "nao"
    elif ref_map is None or fonte_norm not in ref_map:
        categoria = "sem_referencia_liquida_real_auditavel"
        saldo_ref = None
        diferenca_saldo_fonte = None
        diferenca_saldo_rem = None
        origem_ref = ""
        tem_ref = "nao"
    else:
        ref = ref_map[fonte_norm]
        saldo_ref = ref["saldo_liquido_real_referencia_num"]
        origem_ref = ref["origem_referencia"]
        tem_ref = "sim"

        diferenca_saldo_fonte = round(saldo_fonte - saldo_ref, 6)
        diferenca_saldo_rem = round(saldo_rem - saldo_ref, 6)

        if abs(diferenca_saldo_fonte) <= TOL or abs(diferenca_saldo_rem) <= TOL:
            categoria = "saldo_compativel_com_referencia"
        else:
            categoria = "saldo_divergente_da_referencia"

    return {
        "pagamento_idx": row.get("pagamento_idx", ""),
        "chave_pagamento": row.get(COL_CHAVE, ""),
        "data": row.get("data", ""),
        "conta": row.get("conta", ""),
        "origem_linha_u3": row.get("origem_linha_u3", ""),
        "fonte": fonte,
        "fonte_norm": fonte_norm,
        "saldo_fonte_considerado": saldo_fonte,
        "saldo_remanescente_diagnostico": saldo_rem,
        "tem_referencia_liquida_real": tem_ref,
        "saldo_liquido_real_referencia": saldo_ref,
        "origem_referencia": origem_ref,
        "diferenca_saldo_fonte_vs_referencia": diferenca_saldo_fonte,
        "diferenca_saldo_remanescente_vs_referencia": diferenca_saldo_rem,
        "categoria_saldo_u7pre": categoria,
        "promovivel_como_saldo_oficial": "nao" if categoria != "saldo_compativel_com_referencia" else "somente_com_gate",
    }


def auditar_multifonte(multifonte: pd.DataFrame, ref_map: dict[str, dict[str, Any]] | None) -> tuple[pd.DataFrame, dict[str, Any]]:
    audit = pd.DataFrame([classificar_linha_saldo(r, ref_map) for _, r in multifonte.iterrows()])

    valores = multifonte.copy()
    valores["valor_pagamento_num"] = valores["valor_pagamento"].map(round2)
    valores["valor_resgate_num"] = valores["valor_resgate_operacional_u3"].map(round2)

    por_pag = valores.groupby("chave_pagamento", dropna=False).agg(
        valor_pagamento=("valor_pagamento_num", "max"),
        soma_resgate=("valor_resgate_num", "sum"),
        qtd_linhas=("valor_resgate_num", "size"),
    ).reset_index()
    por_pag["diferenca_cobertura"] = por_pag["soma_resgate"] - por_pag["valor_pagamento"]
    por_pag["cobertura_ok"] = por_pag["diferenca_cobertura"].abs() <= TOL

    resumo_multifonte = {
        "qtd_linhas_multifonte": int(len(multifonte)),
        "qtd_pagamentos_multifonte": int(multifonte["chave_pagamento"].nunique()),
        "qtd_pagamentos_multifonte_cobertura_ok": int(por_pag["cobertura_ok"].sum()),
        "qtd_pagamentos_multifonte_cobertura_divergente": int((~por_pag["cobertura_ok"]).sum()),
        "maior_diferenca_cobertura_multifonte": round(float(por_pag["diferenca_cobertura"].abs().max()), 6) if not por_pag.empty else 0.0,
    }

    return audit, resumo_multifonte


def decidir_saldos(
    qtd_saldos_divergentes: int,
    qtd_linhas_sem_referencia: int,
    qtd_linhas_fifo: int,
    qtd_linhas_pendencia: int,
    qtd_divergencias_governanca_u6: int,
    qtd_linhas_com_referencia: int,
) -> str:
    if (
        qtd_saldos_divergentes > 0
        or qtd_divergencias_governanca_u6 > 0
        or qtd_linhas_sem_referencia > 0
        or qtd_linhas_fifo > 0
        or qtd_linhas_pendencia > 0
        or qtd_linhas_com_referencia == 0
    ):
        return DECISAO_NAO_APROVADOS

    return DECISAO_APROVADOS


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    instr_u6 = "Execute antes: python -B scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py"

    abas = carregar_xlsx_u4(ARQ_U4_XLSX)
    linhas = abas["Linhas_Operacionais"]
    multifonte = abas["Multifonte"]

    validar_colunas(linhas, "Linhas_Operacionais", [COL_CHAVE, COL_FONTE, COL_SALDO_FONTE, COL_SALDO_REMANESCENTE])
    validar_colunas(multifonte, "Multifonte", [COL_CHAVE, COL_FONTE, COL_SALDO_FONTE, COL_SALDO_REMANESCENTE, "valor_pagamento", "valor_resgate_operacional_u3"])

    u6_resumo = carregar_csv(ARQ_U6_RESUMO, "U6 resumo", instr_u6)
    u6_abas = carregar_csv(ARQ_U6_ABAS, "U6 abas", instr_u6)
    u6_campos = carregar_csv(ARQ_U6_CAMPOS, "U6 campos", instr_u6)
    u6_gates = carregar_csv(ARQ_U6_GATES, "U6 gates", instr_u6)
    u6_bloqueios = carregar_csv(ARQ_U6_BLOQUEIOS, "U6 bloqueios", instr_u6)

    if not ARQ_LOG_U6.exists():
        raise FileNotFoundError(f"Log U.6 versionado ausente: {ARQ_LOG_U6}")

    qtd_campos_saldo_exigem_precondicao_u6, qtd_divergencias_governanca_u6, governanca_saldos = confirmar_classificacao_u6(u6_campos)

    ref_total, referencias_df = buscar_referencias_saldo_liquido()
    ref_map = None
    if ref_total is not None:
        ref_map = {
            str(r["fonte_referencia_norm"]): r.to_dict()
            for _, r in ref_total.iterrows()
        }

    auditoria_linhas = pd.DataFrame([classificar_linha_saldo(r, ref_map) for _, r in linhas.iterrows()])
    auditoria_multifonte, resumo_multifonte = auditar_multifonte(multifonte, ref_map)

    categorias_linhas = auditoria_linhas["categoria_saldo_u7pre"].value_counts().to_dict()
    categorias_multi = auditoria_multifonte["categoria_saldo_u7pre"].value_counts().to_dict()

    qtd_linhas_com_referencia = int((auditoria_linhas["tem_referencia_liquida_real"] == "sim").sum())
    qtd_linhas_sem_referencia = int((auditoria_linhas["tem_referencia_liquida_real"] == "nao").sum())
    qtd_saldos_compativeis = int((auditoria_linhas["categoria_saldo_u7pre"] == "saldo_compativel_com_referencia").sum())
    qtd_saldos_divergentes = int((auditoria_linhas["categoria_saldo_u7pre"] == "saldo_divergente_da_referencia").sum())
    qtd_linhas_fifo = int((auditoria_linhas["categoria_saldo_u7pre"] == "linha_fifo_diagnostica_nao_promovivel").sum())
    qtd_linhas_pendencia = int((auditoria_linhas["categoria_saldo_u7pre"] == "linha_pendencia_nao_promovivel").sum())

    bloqueios = []

    if qtd_divergencias_governanca_u6 > 0:
        bloqueios.append({
            "bloqueio": "divergencia_governanca_u6",
            "escopo": "campos_saldo",
            "qtd_ocorrencias": qtd_divergencias_governanca_u6,
            "classificacao": "bloqueante",
            "detalhe": "Campos de saldo não estão todos classificados como exige_precondicao na U.6.",
        })

    if ref_total is None:
        bloqueios.append({
            "bloqueio": "sem_referencia_liquida_real_consolidada",
            "escopo": "referencias_saldo",
            "qtd_ocorrencias": 1,
            "classificacao": "bloqueante",
            "detalhe": "Não foi encontrada referência inequívoca de saldo líquido real por fonte/lote.",
        })

    if qtd_linhas_sem_referencia > 0:
        bloqueios.append({
            "bloqueio": "linhas_sem_referencia_liquida_real",
            "escopo": "Linhas_Operacionais",
            "qtd_ocorrencias": qtd_linhas_sem_referencia,
            "classificacao": "bloqueante",
            "detalhe": "Há linhas sem referência líquida real auditável.",
        })

    if qtd_saldos_divergentes > 0:
        bloqueios.append({
            "bloqueio": "saldos_divergentes",
            "escopo": "Linhas_Operacionais",
            "qtd_ocorrencias": qtd_saldos_divergentes,
            "classificacao": "bloqueante",
            "detalhe": "Há saldos divergentes da referência líquida real.",
        })

    if qtd_linhas_fifo > 0:
        bloqueios.append({
            "bloqueio": "fifo_diagnostico_nao_promovivel",
            "escopo": "Linhas_Operacionais",
            "qtd_ocorrencias": qtd_linhas_fifo,
            "classificacao": "bloqueante",
            "detalhe": "Linhas FIFO diagnósticas não podem ser promovidas como saldo oficial.",
        })

    if qtd_linhas_pendencia > 0:
        bloqueios.append({
            "bloqueio": "pendencia_nao_promovivel",
            "escopo": "Linhas_Operacionais",
            "qtd_ocorrencias": qtd_linhas_pendencia,
            "classificacao": "bloqueante",
            "detalhe": "Pendências não podem ser promovidas como saldo oficial.",
        })

    if resumo_multifonte["qtd_pagamentos_multifonte_cobertura_divergente"] > 0:
        bloqueios.append({
            "bloqueio": "multifonte_cobertura_divergente",
            "escopo": "Multifonte",
            "qtd_ocorrencias": resumo_multifonte["qtd_pagamentos_multifonte_cobertura_divergente"],
            "classificacao": "bloqueante",
            "detalhe": "Há pagamento multifonte cuja soma de resgates difere do valor do pagamento.",
        })

    decisao = decidir_saldos(
        qtd_saldos_divergentes=qtd_saldos_divergentes,
        qtd_linhas_sem_referencia=qtd_linhas_sem_referencia,
        qtd_linhas_fifo=qtd_linhas_fifo,
        qtd_linhas_pendencia=qtd_linhas_pendencia,
        qtd_divergencias_governanca_u6=qtd_divergencias_governanca_u6,
        qtd_linhas_com_referencia=qtd_linhas_com_referencia,
    )

    bloqueios_df = pd.DataFrame(
        bloqueios,
        columns=["bloqueio", "escopo", "qtd_ocorrencias", "classificacao", "detalhe"],
    )

    resumo = {
        "qtd_linhas_operacionais_auditadas_u7pre": int(len(linhas)),
        "qtd_linhas_multifonte_auditadas_u7pre": int(len(multifonte)),
        "qtd_pagamentos_multifonte_u7pre": int(multifonte["chave_pagamento"].nunique()),
        "qtd_campos_saldo_auditados_u7pre": 4,
        "qtd_linhas_com_referencia_liquida_real": qtd_linhas_com_referencia,
        "qtd_linhas_sem_referencia_liquida_real": qtd_linhas_sem_referencia,
        "qtd_saldos_compativeis": qtd_saldos_compativeis,
        "qtd_saldos_divergentes": qtd_saldos_divergentes,
        "qtd_linhas_fifo_diagnosticas": qtd_linhas_fifo,
        "qtd_linhas_pendencia_nao_promovivel": qtd_linhas_pendencia,
        "qtd_campos_saldo_exigem_precondicao_u6": qtd_campos_saldo_exigem_precondicao_u6,
        "qtd_divergencias_governanca_u6": qtd_divergencias_governanca_u6,
        "qtd_bloqueios_saldo": int(len(bloqueios_df)),
        "qtd_referencias_aceitas": int((referencias_df["referencia_aceita"] == "sim").sum()) if not referencias_df.empty else 0,
        "qtd_referencias_rejeitadas": int((referencias_df["referencia_aceita"] == "nao").sum()) if not referencias_df.empty else 0,
        "qtd_multifonte_cobertura_divergente": resumo_multifonte["qtd_pagamentos_multifonte_cobertura_divergente"],
        "maior_diferenca_cobertura_multifonte": resumo_multifonte["maior_diferenca_cobertura_multifonte"],
        "decisao_saldos_u7pre": decisao,
        "status_geral_u7pre": STATUS_GERAL,
    }

    resumo_df = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    resumo_df.to_csv(ARQ_RESUMO_U7PRE, index=False)
    auditoria_linhas.to_csv(ARQ_LINHAS_U7PRE, index=False)
    auditoria_multifonte.to_csv(ARQ_MULTIFONTE_U7PRE, index=False)
    referencias_df.to_csv(ARQ_REFERENCIAS_U7PRE, index=False)
    bloqueios_df.to_csv(ARQ_BLOQUEIOS_U7PRE, index=False)

    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())
    linhas_bloqueios = "\n".join(
        f"- `{r['bloqueio']}`: qtd=`{r['qtd_ocorrencias']}`, classificacao=`{r['classificacao']}`"
        for _, r in bloqueios_df.iterrows()
    ) if not bloqueios_df.empty else "- nenhum bloqueio registrado"

    linhas_referencias = "\n".join(
        f"- `{r['origem']}` / `{r['detalhe']}`: aceita=`{r['referencia_aceita']}`, motivo=`{r.get('motivo_rejeicao', '')}`"
        for _, r in referencias_df.iterrows()
    ) if not referencias_df.empty else "- nenhuma referência avaliada"

    linhas_categorias = "\n".join(
        f"- `{k}`: `{v}`"
        for k, v in sorted(categorias_linhas.items())
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U7-PRE — Auditoria de saldos da saída auxiliar

- MICROETAPA: V17-F0-U.7-PRE
- CLASSE: DIAGNÓSTICO / READ-ONLY / AUDITORIA DE SALDOS
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #336
- MICROETAPA_ANTERIOR: V17-F0-U.6
- STATUS_GERAL_U7PRE: `{STATUS_GERAL}`
- DECISAO_SALDOS_U7PRE: `{decisao}`

## Objetivo

Auditar se os campos `saldo_fonte_considerado` e `saldo_remanescente_diagnostico` da saída auxiliar U.4/U.5/U.6 podem ser usados futuramente como saldo oficial por fonte.

A U.7-PRE não corrige saldos, não altera recomendador oficial, não altera motor econômico, não altera exportador oficial, não altera XLSX oficial, não altera dados/cache, não altera contrato/modelo e não implementa U.7 oficial.

## Fontes lidas

- `{ARQ_U4_XLSX.relative_to(BASE_DIR)}`
- `{ARQ_U6_RESUMO.relative_to(BASE_DIR)}`
- `{ARQ_U6_ABAS.relative_to(BASE_DIR)}`
- `{ARQ_U6_CAMPOS.relative_to(BASE_DIR)}`
- `{ARQ_U6_GATES.relative_to(BASE_DIR)}`
- `{ARQ_U6_BLOQUEIOS.relative_to(BASE_DIR)}`
- `{ARQ_LOG_U6.relative_to(BASE_DIR)}`
- `{ARQ_DADOS_FINANCEIROS.relative_to(BASE_DIR)}`

## Artefatos diagnósticos locais gerados

- `{ARQ_RESUMO_U7PRE.relative_to(BASE_DIR)}`
- `{ARQ_LINHAS_U7PRE.relative_to(BASE_DIR)}`
- `{ARQ_MULTIFONTE_U7PRE.relative_to(BASE_DIR)}`
- `{ARQ_REFERENCIAS_U7PRE.relative_to(BASE_DIR)}`
- `{ARQ_BLOQUEIOS_U7PRE.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Categorias de saldo em Linhas_Operacionais

{linhas_categorias}

## Referências de saldo líquido real avaliadas

{linhas_referencias}

## Bloqueios e pré-condições

{linhas_bloqueios}

## Interpretação

A decisão `{decisao}` é conservadora. A ausência de referência líquida real inequívoca, a presença de linhas FIFO diagnósticas, a existência de pendências ou qualquer divergência de saldo bloqueiam promoção oficial dos campos de saldo.

## Decisão normativa preservada

- XLSX auxiliar permanece diagnóstico.
- XLSX oficial não é alterado.
- Exportador oficial não é alterado.
- Motor econômico não é alterado.
- Recomendador oficial não é alterado.
- Nenhum saldo é corrigido.
- Nenhum campo de saldo é promovido automaticamente.
- Os 110 pagamentos sem lote sugerido permanecem bloqueados/pendentes.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte FIFO é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- S.7 e T.0–T.8 não são reabertos.

## Restrições preservadas

- `aplicacao/principal.py` não alterado.
- Motor econômico não alterado.
- Recomendador oficial não alterado.
- Exportador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.

## Status

`{STATUS_GERAL}`
"""
    ARQ_LOG.write_text(log, encoding="utf-8")

    print("=== U7-PRE GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")

    print("\nCategorias Linhas_Operacionais:")
    print(pd.Series(categorias_linhas).sort_index().to_string())

    print("\nCategorias Multifonte:")
    print(pd.Series(categorias_multi).sort_index().to_string())

    print("\nReferencias:")
    print(referencias_df.to_string(index=False))

    print("\nBloqueios:")
    print(bloqueios_df.to_string(index=False) if not bloqueios_df.empty else "sem bloqueios")

    print("\nCSVs:")
    print(ARQ_RESUMO_U7PRE.relative_to(BASE_DIR))
    print(ARQ_LINHAS_U7PRE.relative_to(BASE_DIR))
    print(ARQ_MULTIFONTE_U7PRE.relative_to(BASE_DIR))
    print(ARQ_REFERENCIAS_U7PRE.relative_to(BASE_DIR))
    print(ARQ_BLOQUEIOS_U7PRE.relative_to(BASE_DIR))

    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import math
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DIR_DIAG = BASE_DIR / "saidas/diagnostico"

ARQ_U3_LINHAS = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_linhas.csv"
ARQ_U3_PAGAMENTOS = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_pagamentos.csv"
ARQ_U3_RESUMO = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_resumo.csv"

ARQ_U4_XLSX = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u4.xlsx"
ARQ_U4_RESUMO = DIR_DIAG / "exportacao_auxiliar_pagamentos_v17_f0_u4_resumo.csv"

ARQ_RESUMO_U5 = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_resumo.csv"
ARQ_ABAS_U5 = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_abas.csv"
ARQ_DIVERGENCIAS_U5 = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_divergencias.csv"
ARQ_CHAVES_U5 = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_chaves.csv"

ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U5_AUDITORIA_CONSISTENCIA_EXPORTACAO_AUXILIAR_U4.md"

STATUS_SEM_DIVERGENCIAS = "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_sem_divergencias"
STATUS_COM_DIVERGENCIAS = "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_com_divergencias"
TOL = 0.01

COLUNAS_DIVERGENCIA = [
    "categoria",
    "escopo",
    "tabela",
    "chave",
    "coluna",
    "valor_csv",
    "valor_xlsx",
    "diferenca",
    "detalhe",
]


def carregar_csv(path: Path, nome: str, instrucao: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo obrigatório ausente para U.5 ({nome}): {path}\n{instrucao}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Arquivo obrigatório vazio para U.5 ({nome}): {path}")
    return df


def carregar_xlsx(path: Path) -> dict[str, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(
            f"XLSX obrigatório ausente para U.5: {path}\n"
            "Execute antes: python -B scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py"
        )
    abas_necessarias = ["Resumo_U4", "Pagamentos", "Linhas_Operacionais", "Multifonte", "Pendencias", "Metadados"]
    xls = pd.ExcelFile(path)
    faltantes = [aba for aba in abas_necessarias if aba not in xls.sheet_names]
    if faltantes:
        raise ValueError(f"Abas ausentes no XLSX U.4: {faltantes}")
    return {aba: pd.read_excel(path, sheet_name=aba) for aba in abas_necessarias}


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


def normalizar_texto_comp(x: Any) -> str:
    s = normalizar_texto(x)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def to_float(x: Any) -> float:
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        f = float(x)
        return 0.0 if math.isnan(f) else f
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "n/d", "na", "-"}:
        return 0.0
    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def round2(x: Any) -> float:
    return round(to_float(x) + 1e-12, 2)


def chave_pagamento(row: pd.Series) -> str:
    return normalizar_texto(row.get("chave_pagamento"))


def chave_linha(row: pd.Series) -> str:
    ordem = int(round2(row.get("ordem_fonte_no_pagamento")))
    return "|".join([
        normalizar_texto(row.get("chave_pagamento")),
        str(ordem),
        normalizar_texto(row.get("fonte")),
        normalizar_texto(row.get("origem_linha_u3")),
    ])


def registrar_divergencia(
    divergencias: list[dict[str, Any]],
    categoria: str,
    escopo: str,
    tabela: str,
    chave: str,
    coluna: str,
    valor_csv: Any,
    valor_xlsx: Any,
    diferenca: Any,
    detalhe: str,
) -> None:
    divergencias.append({
        "categoria": categoria,
        "escopo": escopo,
        "tabela": tabela,
        "chave": chave,
        "coluna": coluna,
        "valor_csv": valor_csv,
        "valor_xlsx": valor_xlsx,
        "diferenca": diferenca,
        "detalhe": detalhe,
    })


def preparar_por_chave(df: pd.DataFrame, func_chave) -> tuple[pd.DataFrame, dict[str, pd.Series], list[str]]:
    out = df.copy()
    out["_chave_auditoria"] = out.apply(func_chave, axis=1)
    duplicadas = sorted(out.loc[out["_chave_auditoria"].duplicated(keep=False), "_chave_auditoria"].unique())
    mapa = {str(r["_chave_auditoria"]): r for _, r in out.iterrows()}
    return out, mapa, duplicadas


def comparar_tabela(
    nome: str,
    csv_df: pd.DataFrame,
    xlsx_df: pd.DataFrame,
    func_chave,
    colunas_valor: list[str],
    colunas_classe: list[str],
    colunas_flags: list[str],
    divergencias: list[dict[str, Any]],
) -> dict[str, Any]:
    csv_prep, mapa_csv, dup_csv = preparar_por_chave(csv_df, func_chave)
    xlsx_prep, mapa_xlsx, dup_xlsx = preparar_por_chave(xlsx_df, func_chave)

    if len(csv_df) != len(xlsx_df):
        registrar_divergencia(
            divergencias, "shape", nome, nome, "__shape__", "linhas",
            len(csv_df), len(xlsx_df), len(csv_df) - len(xlsx_df), "Quantidade de linhas divergente."
        )

    for chave in dup_csv:
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "duplicada_csv", "", "", "Chave duplicada no CSV.")
    for chave in dup_xlsx:
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "", "duplicada_xlsx", "", "Chave duplicada no XLSX.")

    chaves_csv = set(mapa_csv)
    chaves_xlsx = set(mapa_xlsx)

    for chave in sorted(chaves_csv - chaves_xlsx):
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "presente", "ausente", "", "Chave presente no CSV e ausente no XLSX.")
    for chave in sorted(chaves_xlsx - chaves_csv):
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "ausente", "presente", "", "Chave presente no XLSX e ausente no CSV.")

    for chave in sorted(chaves_csv & chaves_xlsx):
        row_csv = mapa_csv[chave]
        row_xlsx = mapa_xlsx[chave]

        for coluna in colunas_valor:
            if coluna not in row_csv.index or coluna not in row_xlsx.index:
                registrar_divergencia(divergencias, "shape", nome, nome, chave, coluna, coluna in row_csv.index, coluna in row_xlsx.index, "", "Coluna ausente.")
                continue
            v_csv = round2(row_csv[coluna])
            v_xlsx = round2(row_xlsx[coluna])
            diff = round(v_csv - v_xlsx, 6)
            if abs(diff) > TOL:
                registrar_divergencia(divergencias, "valor", nome, nome, chave, coluna, v_csv, v_xlsx, diff, "Valor divergente acima da tolerância 0.01.")

        for coluna in colunas_classe:
            if coluna not in row_csv.index or coluna not in row_xlsx.index:
                registrar_divergencia(divergencias, "shape", nome, nome, chave, coluna, coluna in row_csv.index, coluna in row_xlsx.index, "", "Coluna ausente.")
                continue
            v_csv = normalizar_texto(row_csv[coluna])
            v_xlsx = normalizar_texto(row_xlsx[coluna])
            if v_csv != v_xlsx:
                registrar_divergencia(divergencias, "classe", nome, nome, chave, coluna, v_csv, v_xlsx, "", "Classe/texto divergente.")

        for coluna in colunas_flags:
            if coluna not in row_csv.index or coluna not in row_xlsx.index:
                registrar_divergencia(divergencias, "shape", nome, nome, chave, coluna, coluna in row_csv.index, coluna in row_xlsx.index, "", "Coluna ausente.")
                continue
            v_csv = normalizar_texto_comp(row_csv[coluna])
            v_xlsx = normalizar_texto_comp(row_xlsx[coluna])
            if v_csv != v_xlsx:
                registrar_divergencia(divergencias, "flags", nome, nome, chave, coluna, v_csv, v_xlsx, "", "Flag divergente.")

    return {
        "tabela": nome,
        "qtd_linhas_csv": len(csv_df),
        "qtd_linhas_xlsx": len(xlsx_df),
        "qtd_chaves_csv": len(chaves_csv),
        "qtd_chaves_xlsx": len(chaves_xlsx),
        "qtd_duplicadas_csv": len(dup_csv),
        "qtd_duplicadas_xlsx": len(dup_xlsx),
        "qtd_chaves_faltantes_no_xlsx": len(chaves_csv - chaves_xlsx),
        "qtd_chaves_extras_no_xlsx": len(chaves_xlsx - chaves_csv),
    }


def comparar_subconjunto(
    nome: str,
    esperado: pd.DataFrame,
    observado: pd.DataFrame,
    func_chave,
    divergencias: list[dict[str, Any]],
) -> dict[str, Any]:
    esp, _, dup_esp = preparar_por_chave(esperado, func_chave)
    obs, _, dup_obs = preparar_por_chave(observado, func_chave)
    chaves_esp = set(esp["_chave_auditoria"])
    chaves_obs = set(obs["_chave_auditoria"])

    if len(esperado) != len(observado):
        registrar_divergencia(
            divergencias, "shape", nome, nome, "__shape__", "linhas",
            len(esperado), len(observado), len(esperado) - len(observado), "Quantidade de linhas do subconjunto divergente."
        )

    for chave in sorted(chaves_esp - chaves_obs):
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "esperado", "ausente", "", "Chave esperada ausente no subconjunto.")
    for chave in sorted(chaves_obs - chaves_esp):
        registrar_divergencia(divergencias, "chave", nome, nome, chave, "_chave_auditoria", "ausente", "observado", "", "Chave extra no subconjunto.")

    return {
        "tabela": nome,
        "qtd_linhas_esperadas": len(esperado),
        "qtd_linhas_observadas": len(observado),
        "qtd_chaves_esperadas": len(chaves_esp),
        "qtd_chaves_observadas": len(chaves_obs),
        "qtd_duplicadas_esperadas": len(dup_esp),
        "qtd_duplicadas_observadas": len(dup_obs),
        "qtd_chaves_faltantes": len(chaves_esp - chaves_obs),
        "qtd_chaves_extras": len(chaves_obs - chaves_esp),
    }


def comparar_resumo(csv_resumo: pd.DataFrame, xlsx_resumo: pd.DataFrame, divergencias: list[dict[str, Any]]) -> None:
    mapa_csv = {normalizar_texto(r["metrica"]): r["valor"] for _, r in csv_resumo.iterrows()}
    mapa_xlsx = {normalizar_texto(r["metrica"]): r["valor"] for _, r in xlsx_resumo.iterrows()}

    for metrica in sorted(set(mapa_csv) - set(mapa_xlsx)):
        registrar_divergencia(divergencias, "resumo", "Resumo_U4", "Resumo_U4", metrica, "valor", mapa_csv[metrica], "ausente", "", "Métrica ausente no XLSX.")
    for metrica in sorted(set(mapa_xlsx) - set(mapa_csv)):
        registrar_divergencia(divergencias, "resumo", "Resumo_U4", "Resumo_U4", metrica, "valor", "ausente", mapa_xlsx[metrica], "", "Métrica extra no XLSX.")

    for metrica in sorted(set(mapa_csv) & set(mapa_xlsx)):
        v_csv = mapa_csv[metrica]
        v_xlsx = mapa_xlsx[metrica]

        n_csv = round2(v_csv)
        n_xlsx = round2(v_xlsx)
        csv_numeric = normalizar_texto(v_csv).replace(".", "", 1).replace("-", "", 1).isdigit()
        xlsx_numeric = normalizar_texto(v_xlsx).replace(".", "", 1).replace("-", "", 1).isdigit()

        if csv_numeric or xlsx_numeric:
            diff = round(n_csv - n_xlsx, 6)
            if abs(diff) > TOL:
                registrar_divergencia(divergencias, "resumo", "Resumo_U4", "Resumo_U4", metrica, "valor", n_csv, n_xlsx, diff, "Valor de resumo divergente.")
        else:
            if normalizar_texto(v_csv) != normalizar_texto(v_xlsx):
                registrar_divergencia(divergencias, "resumo", "Resumo_U4", "Resumo_U4", metrica, "valor", v_csv, v_xlsx, "", "Texto de resumo divergente.")


def auditar_metadados(metadados: pd.DataFrame, divergencias: list[dict[str, Any]]) -> None:
    texto_total = " ".join(
        f"{normalizar_texto_comp(r.get('campo'))} {normalizar_texto_comp(r.get('valor'))}"
        for _, r in metadados.iterrows()
    )

    requisitos = {
        "microetapa_v17_f0_u4": ["microetapa", "v17-f0-u.4"],
        "xlsx_auxiliar_diagnostico": ["xlsx auxiliar", "diagnostico"],
        "nao_saida_oficial": ["nao e saida oficial"],
        "motor_nao_alterado": ["motor economico nao alterado"],
        "recomendador_nao_alterado": ["recomendador oficial nao alterado"],
        "exportador_nao_alterado": ["exportador oficial nao alterado"],
        "xlsx_oficial_nao_alterado": ["xlsx oficial nao alterado"],
    }

    for requisito, termos in requisitos.items():
        if not all(t in texto_total for t in termos):
            registrar_divergencia(
                divergencias,
                "metadados",
                "Metadados",
                "Metadados",
                requisito,
                "valor",
                "presente_esperado",
                "ausente_ou_incompleto",
                "",
                f"Requisito de metadados não localizado: {requisito}",
            )


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    instr_u3 = "Execute antes: python -B scripts/diagnostico/integrar_saida_operacional_pagamentos_multifonte_v17_f0_u3.py"
    instr_u4 = "Execute antes: python -B scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py"

    u3_linhas = carregar_csv(ARQ_U3_LINHAS, "U3 linhas", instr_u3)
    u3_pagamentos = carregar_csv(ARQ_U3_PAGAMENTOS, "U3 pagamentos", instr_u3)
    u3_resumo = carregar_csv(ARQ_U3_RESUMO, "U3 resumo", instr_u3)

    u4_resumo_csv = carregar_csv(ARQ_U4_RESUMO, "U4 resumo csv", instr_u4)
    abas = carregar_xlsx(ARQ_U4_XLSX)

    xlsx_resumo = abas["Resumo_U4"]
    xlsx_pagamentos = abas["Pagamentos"]
    xlsx_linhas = abas["Linhas_Operacionais"]
    xlsx_multifonte = abas["Multifonte"]
    xlsx_pendencias = abas["Pendencias"]
    xlsx_metadados = abas["Metadados"]

    divergencias: list[dict[str, Any]] = []

    info_chaves = []
    info_chaves.append(comparar_tabela(
        "Pagamentos",
        u3_pagamentos,
        xlsx_pagamentos,
        chave_pagamento,
        colunas_valor=[
            "pagamento_idx",
            "valor_pagamento",
            "qtd_linhas_operacionais",
            "soma_resgates_pagamento_u3",
            "diferenca_cobertura_u3",
        ],
        colunas_classe=["tipo_pagamento_operacional_u3", "motivo_bloqueio_u3"],
        colunas_flags=["executavel_operacionalmente_u3", "bloqueio_u3", "nao_auditavel_u3"],
        divergencias=divergencias,
    ))

    info_chaves.append(comparar_tabela(
        "Linhas_Operacionais",
        u3_linhas,
        xlsx_linhas,
        chave_linha,
        colunas_valor=[
            "pagamento_idx",
            "valor_pagamento",
            "ordem_fonte_no_pagamento",
            "valor_resgate_operacional_u3",
            "saldo_fonte_considerado",
            "saldo_remanescente_diagnostico",
            "soma_resgates_pagamento_u3",
            "diferenca_cobertura_u3",
        ],
        colunas_classe=[
            "origem_linha_u3",
            "classe_operacional_u1",
            "classe_linha_u2",
            "classe_pagamento_u2",
            "cobertura_pagamento_u3",
        ],
        colunas_flags=[
            "executavel_operacionalmente_u3",
            "bloqueio_u3",
            "fonte_aprovada_para_pagamento",
            "candidato_fifo_detectado",
            "pendencia_sem_lote_sugerido",
        ],
        divergencias=divergencias,
    ))

    esperado_multifonte = xlsx_linhas.loc[
        xlsx_linhas["origem_linha_u3"].astype(str) == "fonte_multifonte_decomposta_u2"
    ].copy()
    info_multifonte = comparar_subconjunto("Multifonte", esperado_multifonte, xlsx_multifonte, chave_linha, divergencias)

    esperado_pendencias = xlsx_pagamentos.loc[
        (xlsx_pagamentos["bloqueio_u3"].astype(str) == "sim")
        | (xlsx_pagamentos["tipo_pagamento_operacional_u3"].astype(str).str.contains("sem_lote", na=False))
    ].copy()
    info_pendencias = comparar_subconjunto("Pendencias", esperado_pendencias, xlsx_pendencias, chave_pagamento, divergencias)

    comparar_resumo(u4_resumo_csv, xlsx_resumo, divergencias)
    auditar_metadados(xlsx_metadados, divergencias)

    qtd_divergencias_chave = sum(1 for d in divergencias if d["categoria"] == "chave")
    qtd_divergencias_shape = sum(1 for d in divergencias if d["categoria"] == "shape")
    qtd_divergencias_valor = sum(1 for d in divergencias if d["categoria"] == "valor")
    qtd_divergencias_classe = sum(1 for d in divergencias if d["categoria"] == "classe")
    qtd_divergencias_flags = sum(1 for d in divergencias if d["categoria"] == "flags")
    qtd_divergencias_resumo = sum(1 for d in divergencias if d["categoria"] == "resumo")
    qtd_divergencias_metadados = sum(1 for d in divergencias if d["categoria"] == "metadados")
    qtd_divergencias_total = len(divergencias)

    status_geral = STATUS_SEM_DIVERGENCIAS if qtd_divergencias_total == 0 else STATUS_COM_DIVERGENCIAS

    resumo = {
        "qtd_pagamentos_csv_u3": int(u3_pagamentos["chave_pagamento"].nunique()),
        "qtd_pagamentos_xlsx_u4": int(xlsx_pagamentos["chave_pagamento"].nunique()),
        "qtd_linhas_csv_u3": int(len(u3_linhas)),
        "qtd_linhas_xlsx_u4": int(len(xlsx_linhas)),
        "qtd_linhas_multifonte_xlsx_u4": int(len(xlsx_multifonte)),
        "qtd_pagamentos_multifonte_xlsx_u4": int(xlsx_multifonte["chave_pagamento"].nunique()),
        "qtd_pendencias_xlsx_u4": int(len(xlsx_pendencias)),
        "qtd_candidatos_fifo_diagnosticos_xlsx_u4": int(
            (xlsx_linhas["origem_linha_u3"].astype(str) == "candidato_fifo_apenas_diagnostico").sum()
        ),
        "qtd_metricas_resumo_u4_csv": int(len(u4_resumo_csv)),
        "qtd_metricas_resumo_u4_xlsx": int(len(xlsx_resumo)),
        "qtd_divergencias_chave": qtd_divergencias_chave,
        "qtd_divergencias_shape": qtd_divergencias_shape,
        "qtd_divergencias_valor": qtd_divergencias_valor,
        "qtd_divergencias_classe": qtd_divergencias_classe,
        "qtd_divergencias_flags": qtd_divergencias_flags,
        "qtd_divergencias_resumo": qtd_divergencias_resumo,
        "qtd_divergencias_metadados": qtd_divergencias_metadados,
        "qtd_divergencias_total": qtd_divergencias_total,
        "status_geral_u5": status_geral,
    }

    abas_auditadas = pd.DataFrame([
        {
            "aba": "Pagamentos",
            "qtd_linhas_obtida": len(xlsx_pagamentos),
            "qtd_linhas_esperada": len(u3_pagamentos),
            "qtd_chaves_unicas": int(xlsx_pagamentos["chave_pagamento"].nunique()),
            "status": "ok" if len(xlsx_pagamentos) == len(u3_pagamentos) else "divergente",
        },
        {
            "aba": "Linhas_Operacionais",
            "qtd_linhas_obtida": len(xlsx_linhas),
            "qtd_linhas_esperada": len(u3_linhas),
            "qtd_chaves_unicas": len(set(xlsx_linhas.apply(chave_linha, axis=1))),
            "status": "ok" if len(xlsx_linhas) == len(u3_linhas) else "divergente",
        },
        {
            "aba": "Multifonte",
            "qtd_linhas_obtida": len(xlsx_multifonte),
            "qtd_linhas_esperada": len(esperado_multifonte),
            "qtd_chaves_unicas": len(set(xlsx_multifonte.apply(chave_linha, axis=1))),
            "status": "ok" if info_multifonte["qtd_chaves_faltantes"] == 0 and info_multifonte["qtd_chaves_extras"] == 0 else "divergente",
        },
        {
            "aba": "Pendencias",
            "qtd_linhas_obtida": len(xlsx_pendencias),
            "qtd_linhas_esperada": len(esperado_pendencias),
            "qtd_chaves_unicas": int(xlsx_pendencias["chave_pagamento"].nunique()),
            "status": "ok" if info_pendencias["qtd_chaves_faltantes"] == 0 and info_pendencias["qtd_chaves_extras"] == 0 else "divergente",
        },
        {
            "aba": "Resumo_U4",
            "qtd_linhas_obtida": len(xlsx_resumo),
            "qtd_linhas_esperada": len(u4_resumo_csv),
            "qtd_chaves_unicas": int(xlsx_resumo["metrica"].nunique()),
            "status": "ok" if len(xlsx_resumo) == len(u4_resumo_csv) else "divergente",
        },
        {
            "aba": "Metadados",
            "qtd_linhas_obtida": len(xlsx_metadados),
            "qtd_linhas_esperada": "n/d",
            "qtd_chaves_unicas": int(xlsx_metadados["campo"].nunique()),
            "status": "ok" if qtd_divergencias_metadados == 0 else "divergente",
        },
    ])

    chaves = pd.DataFrame(info_chaves + [info_multifonte, info_pendencias])
    divergencias_df = pd.DataFrame(divergencias, columns=COLUNAS_DIVERGENCIA)
    resumo_df = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    resumo_df.to_csv(ARQ_RESUMO_U5, index=False)
    abas_auditadas.to_csv(ARQ_ABAS_U5, index=False)
    divergencias_df.to_csv(ARQ_DIVERGENCIAS_U5, index=False)
    chaves.to_csv(ARQ_CHAVES_U5, index=False)

    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())
    linhas_abas = "\n".join(
        f"- `{r['aba']}`: obtida=`{r['qtd_linhas_obtida']}`, esperada=`{r['qtd_linhas_esperada']}`, status=`{r['status']}`"
        for _, r in abas_auditadas.iterrows()
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U5 — Auditoria de consistência da exportação auxiliar U.4 contra CSVs U.3

- MICROETAPA: V17-F0-U.5
- CLASSE: DIAGNÓSTICO / READ-ONLY / AUDITORIA CRUZADA
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #334
- MICROETAPA_ANTERIOR: V17-F0-U.4
- STATUS_GERAL_U5: `{status_geral}`

## Objetivo

Auditar se o XLSX auxiliar gerado na U.4 preserva exatamente o conteúdo dos CSVs diagnósticos da U.3, sem perda de linhas, duplicação indevida, alteração de valores, alteração de classes, alteração de flags operacionais ou mudança de chaves.

A U.5 não altera recomendador oficial, motor econômico, exportador oficial, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `{ARQ_U3_LINHAS.relative_to(BASE_DIR)}`
- `{ARQ_U3_PAGAMENTOS.relative_to(BASE_DIR)}`
- `{ARQ_U3_RESUMO.relative_to(BASE_DIR)}`
- `{ARQ_U4_XLSX.relative_to(BASE_DIR)}`
- `{ARQ_U4_RESUMO.relative_to(BASE_DIR)}`

## Artefatos diagnósticos locais gerados

- `{ARQ_RESUMO_U5.relative_to(BASE_DIR)}`
- `{ARQ_ABAS_U5.relative_to(BASE_DIR)}`
- `{ARQ_DIVERGENCIAS_U5.relative_to(BASE_DIR)}`
- `{ARQ_CHAVES_U5.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Auditoria por aba

{linhas_abas}

## Interpretação

A U.5 compara CSVs U.3, XLSX auxiliar U.4 e resumo U.4. O status `sem_divergencias` só é emitido quando não há divergências de chaves, shapes, valores, classes, flags, resumo ou metadados.

## Decisão normativa preservada

- XLSX auxiliar permanece diagnóstico.
- XLSX oficial não é alterado.
- Exportador oficial não é alterado.
- Motor econômico não é alterado.
- Recomendador oficial não é alterado.
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

`{status_geral}`
"""
    ARQ_LOG.write_text(log, encoding="utf-8")

    print("=== U5 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")

    print("\nAuditoria por aba:")
    print(abas_auditadas.to_string(index=False))

    print("\nCSVs:")
    print(ARQ_RESUMO_U5.relative_to(BASE_DIR))
    print(ARQ_ABAS_U5.relative_to(BASE_DIR))
    print(ARQ_DIVERGENCIAS_U5.relative_to(BASE_DIR))
    print(ARQ_CHAVES_U5.relative_to(BASE_DIR))

    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

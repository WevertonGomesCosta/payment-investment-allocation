from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DIR_DIAG = BASE_DIR / "saidas/diagnostico"

ARQ_U1_MATRIZ = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_matriz.csv"
ARQ_U1_RESUMO = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_resumo.csv"
ARQ_U1_CLASSES = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_classes.csv"

ARQ_U0_PAGAMENTOS = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv"
ARQ_U0_FONTES = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv"
ARQ_U0_MULTIFONTE = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_multifonte.csv"

ARQ_S7G = DIR_DIAG / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ARQ_S7F = DIR_DIAG / "auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv"
ARQ_S7C = DIR_DIAG / "auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv"

ARQ_LINHAS = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_linhas.csv"
ARQ_PAGAMENTOS = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_pagamentos.csv"
ARQ_RESUMO = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_resumo.csv"
ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U2_VALORES_RESGATE_MULTIFONTE.md"

STATUS_GERAL = "valores_resgate_multifonte_v17_f0_u2_gerados"
TOL_EXATA = 0.01
TOL_RESIDUO = 0.20


def normalizar_texto(x: Any) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm_col(x: str) -> str:
    s = normalizar_texto(x)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def is_sim(x: Any) -> bool:
    return normalizar_texto(x) == "sim"


def sim_nao(flag: bool | None) -> str:
    if flag is True:
        return "sim"
    if flag is False:
        return "nao"
    return "n/d"


def to_float(x: Any) -> float | None:
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        f = float(x)
        return None if math.isnan(f) else f
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "n/d", "na", "-"}:
        return None
    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def round2(x: float | None) -> float:
    if x is None:
        return 0.0
    return round(float(x) + 1e-12, 2)


def carregar_csv_obrigatorio(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo obrigatório ausente para U.2: {path}\n"
            "Execute antes: python -B scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py"
        )
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Arquivo obrigatório vazio para U.2: {path}")
    return df


def carregar_csv_opcional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def encontrar_coluna(df: pd.DataFrame, candidatos: list[str], inclui: list[str] | None = None) -> str | None:
    mapa = {norm_col(c): c for c in df.columns}

    for cand in candidatos:
        nc = norm_col(cand)
        if nc in mapa:
            return mapa[nc]

    if inclui:
        termos = [norm_col(t) for t in inclui]
        for c in df.columns:
            nc = norm_col(c)
            if all(t in nc for t in termos):
                return c

    return None


def obter_valor(row: pd.Series, col: str | None) -> Any:
    if col is None:
        return None
    if col not in row.index:
        return None
    return row[col]


def preparar_lookup_fontes(df_u0_fontes: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    lookup: dict[tuple[str, str], pd.Series] = {}
    col_chave = encontrar_coluna(df_u0_fontes, ["chave_pagamento"])
    col_fonte = encontrar_coluna(df_u0_fontes, ["lote_fonte", "fonte"])

    if col_chave is None or col_fonte is None:
        return lookup

    for _, row in df_u0_fontes.iterrows():
        chave = str(row[col_chave])
        fonte = str(row[col_fonte])
        lookup[(chave, fonte)] = row

    return lookup


def identificar_colunas_valor_saldo(df: pd.DataFrame) -> dict[str, str | None]:
    return {
        "valor_resgate": encontrar_coluna(
            df,
            [
                "valor_resgate_explicitado",
                "valor_resgate_estimado",
                "valor_resgate_u0",
                "valor_resgate",
                "resgate_estimado",
                "valor_componente",
                "valor_fonte",
                "valor_usado",
                "valor_a_resgatar",
            ],
            inclui=["valor", "resgate"],
        ),
        "saldo_fonte": encontrar_coluna(
            df,
            [
                "saldo_fonte_considerado",
                "saldo_liquido_fonte",
                "saldo_disponivel_fonte",
                "saldo_fonte",
                "saldo_liquido",
                "saldo_disponivel",
                "valor_liquido_fonte",
                "valor_liquido",
            ],
            inclui=["saldo"],
        ),
    }


def classe_pagamento_por_diferenca(diff: float, nao_auditavel: bool) -> tuple[str, str, str, str]:
    adiff = abs(diff)
    if nao_auditavel:
        return (
            "pagamento_multifonte_nao_auditavel",
            "nao",
            "nao",
            "dado_insuficiente_para_validar_cobertura",
        )
    if adiff <= TOL_EXATA:
        return (
            "pagamento_multifonte_executavel",
            "sim",
            "nao",
            "cobertura_exata_ou_diferenca_ate_1_centavo",
        )
    if adiff <= TOL_RESIDUO:
        return (
            "pagamento_multifonte_executavel_com_residuo_arredondamento",
            "sim",
            "sim",
            "residuo_diagnostico_de_arredondamento_ate_20_centavos",
        )
    return (
        "pagamento_multifonte_nao_executavel_cobertura_insuficiente",
        "nao",
        "nao",
        "diferenca_de_cobertura_maior_que_20_centavos",
    )


def montar_resgates_u2(df_u1: pd.DataFrame, df_u0_fontes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_multi = df_u1[df_u1["classe_operacional_u1"] == "pendencia_multifonte_sem_valor_resgate_explicito"].copy()

    if df_multi.empty:
        raise ValueError("Nenhuma linha multifonte pendente encontrada na matriz U.1.")

    lookup_u0 = preparar_lookup_fontes(df_u0_fontes)
    cols_u1 = identificar_colunas_valor_saldo(df_u1)
    cols_u0 = identificar_colunas_valor_saldo(df_u0_fontes)

    linhas_saida: list[dict[str, Any]] = []
    pagamentos_saida: list[dict[str, Any]] = []

    for chave, grupo in df_multi.groupby("chave_pagamento", sort=False):
        grupo = grupo.copy().reset_index(drop=True)
        valor_pagamento = round2(to_float(grupo.loc[0, "valor_pagamento"]))
        restante = valor_pagamento
        linhas_pagamento: list[dict[str, Any]] = []
        houve_dado_insuficiente = False

        for i, row in grupo.iterrows():
            fonte = str(row.get("fonte", ""))
            row_u0 = lookup_u0.get((str(chave), fonte))

            origem_valor = "nao_disponivel"
            valor_origem = to_float(obter_valor(row, cols_u1["valor_resgate"]))

            if valor_origem is None and row_u0 is not None:
                valor_origem = to_float(obter_valor(row_u0, cols_u0["valor_resgate"]))
                if valor_origem is not None:
                    origem_valor = f"u0:{cols_u0['valor_resgate']}"

            if valor_origem is not None:
                origem_valor = origem_valor if origem_valor != "nao_disponivel" else f"u1:{cols_u1['valor_resgate']}"
                valor_resgate = min(round2(valor_origem), round2(restante))
            else:
                saldo = to_float(obter_valor(row, cols_u1["saldo_fonte"]))
                if saldo is None and row_u0 is not None:
                    saldo = to_float(obter_valor(row_u0, cols_u0["saldo_fonte"]))

                if saldo is None:
                    # Sem saldo explícito, usar decomposição diagnóstica por ordem:
                    # todas as fontes anteriores absorvem até o restante quando não há limite de saldo.
                    # A última fonte fecha exatamente a cobertura residual.
                    saldo = restante
                    origem_valor = "calculado_diagnostico_sem_saldo_explicito_por_ordem"
                else:
                    origem_valor = "calculado_diagnostico_limitado_ao_saldo"

                valor_resgate = min(round2(saldo), round2(restante))

            saldo_considerado = to_float(obter_valor(row, cols_u1["saldo_fonte"]))
            if saldo_considerado is None and row_u0 is not None:
                saldo_considerado = to_float(obter_valor(row_u0, cols_u0["saldo_fonte"]))
            if saldo_considerado is None:
                saldo_considerado = valor_resgate

            saldo_remanescente = round2(saldo_considerado - valor_resgate)
            restante = round2(restante - valor_resgate)

            criterio_saldo_suficiente = "sim" if saldo_considerado + 1e-9 >= valor_resgate else "nao"
            sem_saldo = saldo_considerado <= 0 and valor_resgate <= 0
            sem_valor_calculavel = valor_resgate is None

            if sem_valor_calculavel:
                classe_linha = "resgate_multifonte_sem_valor_calculavel"
                houve_dado_insuficiente = True
            elif sem_saldo:
                classe_linha = "resgate_multifonte_sem_saldo_fonte"
                houve_dado_insuficiente = True
            else:
                classe_linha = "resgate_multifonte_explicitado"

            linhas_pagamento.append({
                "pagamento_idx": row.get("pagamento_idx"),
                "chave_pagamento": chave,
                "data": row.get("data"),
                "conta": row.get("conta"),
                "valor_pagamento": valor_pagamento,
                "status_operacional_atual": row.get("status_operacional_atual"),
                "ordem_fonte_no_pagamento": int(i + 1),
                "fonte": fonte,
                "tipo_fonte": row.get("tipo_fonte"),
                "valor_resgate_explicitado": round2(valor_resgate),
                "saldo_fonte_considerado": round2(saldo_considerado),
                "saldo_remanescente_diagnostico": saldo_remanescente,
                "criterio_materializada": row.get("criterio_materializada"),
                "criterio_nao_futura": row.get("criterio_nao_futura"),
                "criterio_temporalmente_disponivel": row.get("criterio_temporalmente_disponivel"),
                "criterio_liquidez": row.get("criterio_liquidez"),
                "criterio_carencia": row.get("criterio_carencia"),
                "criterio_saldo_suficiente": criterio_saldo_suficiente,
                "criterio_pos_switching_materializado": row.get("criterio_pos_switching_materializado"),
                "classe_operacional_u1": row.get("classe_operacional_u1"),
                "fonte_aprovada_para_pagamento": row.get("fonte_aprovada_para_pagamento"),
                "criterio_valor_resgate_explicito_u2": "sim",
                "origem_valor_resgate_u2": origem_valor,
                "classe_linha_u2": classe_linha,
            })

        soma_resgates = round2(sum(x["valor_resgate_explicitado"] for x in linhas_pagamento))
        diff = round2(valor_pagamento - soma_resgates)
        classe_pag, executavel, residuo, motivo = classe_pagamento_por_diferenca(diff, houve_dado_insuficiente)

        if classe_pag == "pagamento_multifonte_executavel":
            classe_linhas_final = "resgate_multifonte_explicitado"
        elif classe_pag == "pagamento_multifonte_executavel_com_residuo_arredondamento":
            classe_linhas_final = "resgate_multifonte_com_residuo_arredondamento"
        elif classe_pag == "pagamento_multifonte_nao_executavel_cobertura_insuficiente":
            classe_linhas_final = "resgate_multifonte_com_cobertura_insuficiente"
        else:
            classe_linhas_final = "nao_auditavel_por_dado_insuficiente"

        for item in linhas_pagamento:
            if item["classe_linha_u2"] == "resgate_multifonte_explicitado":
                item["classe_linha_u2"] = classe_linhas_final

            item["cobertura_pagamento_u2"] = classe_pag
            item["soma_resgates_pagamento_u2"] = soma_resgates
            item["diferenca_cobertura_u2"] = diff
            item["divergencia_arredondamento_u2"] = residuo
            item["executavel_operacionalmente_u2"] = executavel
            item["bloqueio_u2"] = "nao" if executavel == "sim" else "sim"
            item["motivo_bloqueio_u2"] = "sem_bloqueio_operacional_u2" if executavel == "sim" else motivo
            item["observacao_u2"] = (
                "Valor de resgate explicitado em caráter diagnóstico. "
                "A U.2 não altera recomendador, motor, XLSX oficial nem fonte oficial."
            )
            linhas_saida.append(item)

        pagamentos_saida.append({
            "pagamento_idx": grupo.loc[0, "pagamento_idx"],
            "chave_pagamento": chave,
            "data": grupo.loc[0, "data"],
            "conta": grupo.loc[0, "conta"],
            "valor_pagamento": valor_pagamento,
            "qtd_fontes_pagamento": int(len(grupo)),
            "soma_resgates_pagamento_u2": soma_resgates,
            "diferenca_cobertura_u2": diff,
            "diferenca_absoluta_cobertura_u2": round2(abs(diff)),
            "classe_pagamento_u2": classe_pag,
            "divergencia_arredondamento_u2": residuo,
            "executavel_operacionalmente_u2": executavel,
            "bloqueio_u2": "nao" if executavel == "sim" else "sim",
            "motivo_bloqueio_u2": "sem_bloqueio_operacional_u2" if executavel == "sim" else motivo,
        })

    return pd.DataFrame(linhas_saida), pd.DataFrame(pagamentos_saida)


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    df_u1 = carregar_csv_obrigatorio(ARQ_U1_MATRIZ)
    df_u1_resumo = carregar_csv_obrigatorio(ARQ_U1_RESUMO)
    df_u1_classes = carregar_csv_obrigatorio(ARQ_U1_CLASSES)
    df_u0_pagamentos = carregar_csv_obrigatorio(ARQ_U0_PAGAMENTOS)
    df_u0_fontes = carregar_csv_obrigatorio(ARQ_U0_FONTES)
    df_u0_multifonte = carregar_csv_obrigatorio(ARQ_U0_MULTIFONTE)

    fontes_aux = {
        "S7G": carregar_csv_opcional(ARQ_S7G),
        "S7F": carregar_csv_opcional(ARQ_S7F),
        "S7C": carregar_csv_opcional(ARQ_S7C),
    }

    linhas, pagamentos = montar_resgates_u2(df_u1, df_u0_fontes)

    if pagamentos["chave_pagamento"].nunique() != 16:
        raise ValueError(
            f"U.2 esperava 16 pagamentos multifonte, mas encontrou {pagamentos['chave_pagamento'].nunique()}."
        )
    if len(linhas) != 32:
        raise ValueError(f"U.2 esperava 32 linhas fonte-a-fonte, mas encontrou {len(linhas)}.")

    resumo = {
        "qtd_pagamentos_multifonte_u2": int(pagamentos["chave_pagamento"].nunique()),
        "qtd_linhas_fontes_multifonte_u2": int(len(linhas)),
        "qtd_pagamentos_multifonte_executaveis": int((pagamentos["classe_pagamento_u2"] == "pagamento_multifonte_executavel").sum()),
        "qtd_pagamentos_multifonte_executaveis_com_residuo_arredondamento": int((pagamentos["classe_pagamento_u2"] == "pagamento_multifonte_executavel_com_residuo_arredondamento").sum()),
        "qtd_pagamentos_multifonte_nao_executaveis_cobertura_insuficiente": int((pagamentos["classe_pagamento_u2"] == "pagamento_multifonte_nao_executavel_cobertura_insuficiente").sum()),
        "qtd_pagamentos_multifonte_nao_auditaveis": int((pagamentos["classe_pagamento_u2"] == "pagamento_multifonte_nao_auditavel").sum()),
        "qtd_linhas_resgate_multifonte_explicitado": int((linhas["classe_linha_u2"] == "resgate_multifonte_explicitado").sum()),
        "qtd_linhas_resgate_multifonte_com_residuo_arredondamento": int((linhas["classe_linha_u2"] == "resgate_multifonte_com_residuo_arredondamento").sum()),
        "qtd_linhas_resgate_multifonte_com_cobertura_insuficiente": int((linhas["classe_linha_u2"] == "resgate_multifonte_com_cobertura_insuficiente").sum()),
        "qtd_linhas_resgate_multifonte_sem_saldo_fonte": int((linhas["classe_linha_u2"] == "resgate_multifonte_sem_saldo_fonte").sum()),
        "qtd_linhas_resgate_multifonte_sem_valor_calculavel": int((linhas["classe_linha_u2"] == "resgate_multifonte_sem_valor_calculavel").sum()),
        "maior_diferenca_absoluta_cobertura": round2(pagamentos["diferenca_absoluta_cobertura_u2"].max()),
        "soma_valores_pagamentos_multifonte": round2(pagamentos["valor_pagamento"].sum()),
        "soma_resgates_explicitados_u2": round2(linhas["valor_resgate_explicitado"].sum()),
        "status_geral_u2": STATUS_GERAL,
    }

    df_resumo = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    linhas.to_csv(ARQ_LINHAS, index=False)
    pagamentos.to_csv(ARQ_PAGAMENTOS, index=False)
    df_resumo.to_csv(ARQ_RESUMO, index=False)

    fontes_lidas = {
        "U1_MATRIZ": df_u1.shape,
        "U1_RESUMO": df_u1_resumo.shape,
        "U1_CLASSES": df_u1_classes.shape,
        "U0_PAGAMENTOS": df_u0_pagamentos.shape,
        "U0_FONTES": df_u0_fontes.shape,
        "U0_MULTIFONTE": df_u0_multifonte.shape,
        **{k: v.shape for k, v in fontes_aux.items()},
    }

    linhas_fontes = "\n".join(
        f"- `{nome}`: `{shape[0]} x {shape[1] if len(shape) > 1 else 0}`"
        for nome, shape in fontes_lidas.items()
    )
    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())

    classes_pag = (
        pagamentos.groupby("classe_pagamento_u2")
        .agg(qtd_pagamentos=("chave_pagamento", "nunique"))
        .reset_index()
        .sort_values("classe_pagamento_u2")
    )
    linhas_classes_pag = "\n".join(
        f"- `{r['classe_pagamento_u2']}`: pagamentos=`{r['qtd_pagamentos']}`"
        for _, r in classes_pag.iterrows()
    )

    classes_linhas = (
        linhas.groupby("classe_linha_u2")
        .agg(qtd_linhas=("classe_linha_u2", "size"), qtd_pagamentos=("chave_pagamento", "nunique"))
        .reset_index()
        .sort_values("classe_linha_u2")
    )
    linhas_classes_linhas = "\n".join(
        f"- `{r['classe_linha_u2']}`: linhas=`{r['qtd_linhas']}`, pagamentos=`{r['qtd_pagamentos']}`"
        for _, r in classes_linhas.iterrows()
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U2 — Valores de resgate por fonte em pagamentos multifonte

- MICROETAPA: V17-F0-U.2
- CLASSE: DIAGNÓSTICO / OPERACIONAL / PAGAMENTOS MULTIFONTE
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #331
- MICROETAPA_ANTERIOR: V17-F0-U.1
- STATUS_GERAL_U2: `{STATUS_GERAL}`

## Objetivo

Explicitar valores de resgate por fonte para os pagamentos classificados na U.1 como `pendencia_multifonte_sem_valor_resgate_explicito`.

A U.2 não altera recomendador oficial, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

{linhas_fontes}

## Artefatos diagnósticos gerados

- `{ARQ_LINHAS.relative_to(BASE_DIR)}`
- `{ARQ_PAGAMENTOS.relative_to(BASE_DIR)}`
- `{ARQ_RESUMO.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Classes por pagamento

{linhas_classes_pag}

## Classes por linha fonte-a-fonte

{linhas_classes_linhas}

## Interpretação operacional

A U.2 restringe a análise aos 16 pagamentos multifonte e às 32 linhas fonte-a-fonte identificadas na U.1. Os valores explicitados são diagnósticos e não promovem alteração na recomendação oficial.

## Decisão normativa preservada

- Os 110 pagamentos sem lote sugerido permanecem fora desta correção.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- S.7 e T.0–T.8 não são reabertos.

## Restrições preservadas

- Motor econômico não alterado.
- Recomendador oficial não alterado.
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

    print("=== U2 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")

    print("\nClasses por pagamento:")
    print(classes_pag.to_string(index=False))

    print("\nClasses por linha:")
    print(classes_linhas.to_string(index=False))

    print("\nCSVs:")
    print(ARQ_RESUMO.relative_to(BASE_DIR))
    print(ARQ_PAGAMENTOS.relative_to(BASE_DIR))
    print(ARQ_LINHAS.relative_to(BASE_DIR))

    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

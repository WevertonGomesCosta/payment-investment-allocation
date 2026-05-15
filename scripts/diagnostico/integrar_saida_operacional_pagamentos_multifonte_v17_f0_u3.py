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

ARQ_S7G = DIR_DIAG / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ARQ_U0_PAGAMENTOS = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv"
ARQ_U0_FONTES = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv"

ARQ_U1_MATRIZ = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_matriz.csv"

ARQ_U2_LINHAS = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_linhas.csv"
ARQ_U2_PAGAMENTOS = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_pagamentos.csv"
ARQ_U2_RESUMO = DIR_DIAG / "valores_resgate_multifonte_v17_f0_u2_resumo.csv"

ARQ_LINHAS = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_linhas.csv"
ARQ_PAGAMENTOS = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_pagamentos.csv"
ARQ_RESUMO = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u3_resumo.csv"
ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U3_SAIDA_OPERACIONAL_PAGAMENTOS_MULTIFONTE.md"

STATUS_GERAL = "saida_operacional_pagamentos_multifonte_v17_f0_u3_gerada"


def normalizar_texto(x: Any) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


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


def is_sim(x: Any) -> bool:
    return normalizar_texto(x) == "sim"


def carregar_csv_obrigatorio(path: Path, nome: str) -> pd.DataFrame:
    if not path.exists():
        if "u2" in nome.lower():
            raise FileNotFoundError(
                f"Arquivo obrigatório ausente para U.3: {path}\n"
                "Execute antes: python -B scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py"
            )
        raise FileNotFoundError(f"Arquivo obrigatório ausente para U.3: {path}")
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Arquivo obrigatório vazio para U.3: {path}")
    return df


def preparar_lookup_u2(df_u2_linhas: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    lookup: dict[str, list[dict[str, Any]]] = {}
    for _, row in df_u2_linhas.iterrows():
        r = row.to_dict()
        lookup.setdefault(str(r["chave_pagamento"]), []).append(r)

    for chave in lookup:
        lookup[chave] = sorted(
            lookup[chave],
            key=lambda r: int(to_float(r.get("ordem_fonte_no_pagamento", 0))),
        )

    return lookup


def linha_base(
    row: dict[str, Any],
    *,
    tipo_pagamento: str,
    origem_linha: str,
    ordem_fonte: int,
    fonte: str,
    tipo_fonte: str,
    valor_resgate: float,
    saldo_fonte: float,
    saldo_remanescente: float,
    soma_resgates: float,
    diferenca: float,
    cobertura: str,
    executavel: str,
    bloqueio: str,
    motivo: str,
    classe_linha_u2: str,
    classe_pagamento_u2: str,
    observacao: str,
) -> dict[str, Any]:
    return {
        "pagamento_idx": row.get("pagamento_idx"),
        "chave_pagamento": row.get("chave_pagamento"),
        "data": row.get("data"),
        "conta": row.get("conta"),
        "valor_pagamento": round2(row.get("valor_pagamento")),
        "status_operacional_original": row.get("status_operacional_atual"),
        "tipo_pagamento_operacional_u3": tipo_pagamento,
        "origem_linha_u3": origem_linha,
        "ordem_fonte_no_pagamento": ordem_fonte,
        "fonte": fonte,
        "tipo_fonte": tipo_fonte,
        "valor_resgate_operacional_u3": round2(valor_resgate),
        "saldo_fonte_considerado": round2(saldo_fonte),
        "saldo_remanescente_diagnostico": round2(saldo_remanescente),
        "soma_resgates_pagamento_u3": round2(soma_resgates),
        "diferenca_cobertura_u3": round2(diferenca),
        "cobertura_pagamento_u3": cobertura,
        "executavel_operacionalmente_u3": executavel,
        "bloqueio_u3": bloqueio,
        "motivo_bloqueio_u3": motivo,
        "classe_operacional_u1": row.get("classe_operacional_u1"),
        "classe_linha_u2": classe_linha_u2,
        "classe_pagamento_u2": classe_pagamento_u2,
        "fonte_aprovada_para_pagamento": row.get("fonte_aprovada_para_pagamento"),
        "candidato_fifo_detectado": row.get("candidato_fifo_detectado"),
        "pendencia_sem_lote_sugerido": "sim" if row.get("classe_operacional_u1") in {
            "candidato_fifo_apenas_diagnostico",
            "pendencia_sem_lote_sugerido",
        } else "nao",
        "observacao_u3": observacao,
    }


def montar_saida_u3(df_u1: pd.DataFrame, df_u2_linhas: pd.DataFrame) -> pd.DataFrame:
    lookup_u2 = preparar_lookup_u2(df_u2_linhas)
    linhas: list[dict[str, Any]] = []

    chaves_multifonte_processadas: set[str] = set()

    for _, row_pd in df_u1.iterrows():
        row = row_pd.to_dict()
        classe = str(row.get("classe_operacional_u1"))
        chave = str(row.get("chave_pagamento"))
        valor_pagamento = round2(row.get("valor_pagamento"))

        if classe == "fonte_aprovada_sem_violacao_dura":
            linhas.append(linha_base(
                row,
                tipo_pagamento="monofonte_aprovado",
                origem_linha="fonte_monofonte_aprovada_u0_u1",
                ordem_fonte=1,
                fonte=str(row.get("fonte")),
                tipo_fonte=str(row.get("tipo_fonte")),
                valor_resgate=valor_pagamento,
                saldo_fonte=valor_pagamento,
                saldo_remanescente=0.0,
                soma_resgates=valor_pagamento,
                diferenca=0.0,
                cobertura="pagamento_monofonte_coberto_por_fonte_aprovada",
                executavel="sim",
                bloqueio="nao",
                motivo="sem_bloqueio_operacional_u3",
                classe_linha_u2="n/d",
                classe_pagamento_u2="n/d",
                observacao="Linha monofonte aprovada herdada de U.0/U.1. A U.3 não altera recomendador nem motor.",
            ))
            continue

        if classe == "pendencia_multifonte_sem_valor_resgate_explicito":
            if chave in chaves_multifonte_processadas:
                continue
            chaves_multifonte_processadas.add(chave)

            partes = lookup_u2.get(chave)
            if not partes:
                linhas.append(linha_base(
                    row,
                    tipo_pagamento="nao_auditavel",
                    origem_linha="nao_auditavel",
                    ordem_fonte=1,
                    fonte=str(row.get("fonte")),
                    tipo_fonte=str(row.get("tipo_fonte")),
                    valor_resgate=0.0,
                    saldo_fonte=0.0,
                    saldo_remanescente=0.0,
                    soma_resgates=0.0,
                    diferenca=valor_pagamento,
                    cobertura="u2_ausente_para_multifonte",
                    executavel="nao",
                    bloqueio="sim",
                    motivo="decomposicao_u2_ausente",
                    classe_linha_u2="n/d",
                    classe_pagamento_u2="n/d",
                    observacao="Pagamento multifonte sem decomposição U.2 localizada. Não promover.",
                ))
                continue

            for parte in partes:
                linhas.append(linha_base(
                    row,
                    tipo_pagamento="multifonte_decomposto_diagnostico",
                    origem_linha="fonte_multifonte_decomposta_u2",
                    ordem_fonte=int(to_float(parte.get("ordem_fonte_no_pagamento"))),
                    fonte=str(parte.get("fonte")),
                    tipo_fonte=str(parte.get("tipo_fonte")),
                    valor_resgate=round2(parte.get("valor_resgate_explicitado")),
                    saldo_fonte=round2(parte.get("saldo_fonte_considerado")),
                    saldo_remanescente=round2(parte.get("saldo_remanescente_diagnostico")),
                    soma_resgates=round2(parte.get("soma_resgates_pagamento_u2")),
                    diferenca=round2(parte.get("diferenca_cobertura_u2")),
                    cobertura=str(parte.get("cobertura_pagamento_u2")),
                    executavel=str(parte.get("executavel_operacionalmente_u2")),
                    bloqueio=str(parte.get("bloqueio_u2")),
                    motivo=str(parte.get("motivo_bloqueio_u2")),
                    classe_linha_u2=str(parte.get("classe_linha_u2")),
                    classe_pagamento_u2=str(parte.get("cobertura_pagamento_u2")),
                    observacao="Linha multifonte decomposta pela U.2 em caráter diagnóstico. Não altera recomendador oficial.",
                ))
            continue

        if classe == "candidato_fifo_apenas_diagnostico":
            linhas.append(linha_base(
                row,
                tipo_pagamento="sem_lote_com_candidato_fifo_diagnostico",
                origem_linha="candidato_fifo_apenas_diagnostico",
                ordem_fonte=1,
                fonte="sem_fonte_recomendada",
                tipo_fonte="n/d",
                valor_resgate=0.0,
                saldo_fonte=0.0,
                saldo_remanescente=0.0,
                soma_resgates=0.0,
                diferenca=valor_pagamento,
                cobertura="sem_cobertura_por_fonte_aprovada",
                executavel="nao",
                bloqueio="sim",
                motivo="candidato_fifo_nao_promovido",
                classe_linha_u2="n/d",
                classe_pagamento_u2="n/d",
                observacao="Candidato FIFO preservado como diagnóstico. A U.3 não escolhe fonte nem promove recomendação.",
            ))
            continue

        if classe == "pendencia_sem_lote_sugerido":
            linhas.append(linha_base(
                row,
                tipo_pagamento="sem_lote_sugerido",
                origem_linha="pagamento_sem_lote_sugerido",
                ordem_fonte=1,
                fonte="sem_fonte_recomendada",
                tipo_fonte="n/d",
                valor_resgate=0.0,
                saldo_fonte=0.0,
                saldo_remanescente=0.0,
                soma_resgates=0.0,
                diferenca=valor_pagamento,
                cobertura="sem_cobertura_por_fonte_aprovada",
                executavel="nao",
                bloqueio="sim",
                motivo="sem_lote_sugerido",
                classe_linha_u2="n/d",
                classe_pagamento_u2="n/d",
                observacao="Pagamento sem lote sugerido preservado como pendência. A U.3 não refactibiliza.",
            ))
            continue

        linhas.append(linha_base(
            row,
            tipo_pagamento="nao_auditavel",
            origem_linha="nao_auditavel",
            ordem_fonte=1,
            fonte=str(row.get("fonte", "n/d")),
            tipo_fonte=str(row.get("tipo_fonte", "n/d")),
            valor_resgate=0.0,
            saldo_fonte=0.0,
            saldo_remanescente=0.0,
            soma_resgates=0.0,
            diferenca=valor_pagamento,
            cobertura="nao_auditavel",
            executavel="nao",
            bloqueio="sim",
            motivo="classe_u1_nao_mapeada_para_u3",
            classe_linha_u2="n/d",
            classe_pagamento_u2="n/d",
            observacao=f"Classe U.1 não mapeada na U.3: {classe}.",
        ))

    return pd.DataFrame(linhas)


def montar_pagamentos(df_linhas: pd.DataFrame) -> pd.DataFrame:
    registros: list[dict[str, Any]] = []

    for chave, grupo in df_linhas.groupby("chave_pagamento", sort=False):
        g0 = grupo.iloc[0]
        valor_pagamento = round2(g0["valor_pagamento"])
        soma_resgates = round2(grupo["valor_resgate_operacional_u3"].sum())
        diferenca = round2(valor_pagamento - soma_resgates)

        bloqueado = (grupo["bloqueio_u3"] == "sim").any()
        nao_auditavel = (grupo["tipo_pagamento_operacional_u3"] == "nao_auditavel").any()
        executavel = "nao" if bloqueado or nao_auditavel else "sim"

        registros.append({
            "pagamento_idx": g0["pagamento_idx"],
            "chave_pagamento": chave,
            "data": g0["data"],
            "conta": g0["conta"],
            "valor_pagamento": valor_pagamento,
            "qtd_linhas_operacionais": int(len(grupo)),
            "tipo_pagamento_operacional_u3": g0["tipo_pagamento_operacional_u3"],
            "soma_resgates_pagamento_u3": soma_resgates,
            "diferenca_cobertura_u3": diferenca,
            "executavel_operacionalmente_u3": executavel,
            "bloqueio_u3": "sim" if bloqueado else "nao",
            "nao_auditavel_u3": "sim" if nao_auditavel else "nao",
            "motivo_bloqueio_u3": ";".join(sorted(set(str(x) for x in grupo["motivo_bloqueio_u3"]))),
        })

    return pd.DataFrame(registros)


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    df_s7g = carregar_csv_obrigatorio(ARQ_S7G, "S7G")
    df_u0_pagamentos = carregar_csv_obrigatorio(ARQ_U0_PAGAMENTOS, "U0 pagamentos")
    df_u0_fontes = carregar_csv_obrigatorio(ARQ_U0_FONTES, "U0 fontes")
    df_u1 = carregar_csv_obrigatorio(ARQ_U1_MATRIZ, "U1 matriz")
    df_u2_linhas = carregar_csv_obrigatorio(ARQ_U2_LINHAS, "U2 linhas")
    df_u2_pagamentos = carregar_csv_obrigatorio(ARQ_U2_PAGAMENTOS, "U2 pagamentos")
    df_u2_resumo = carregar_csv_obrigatorio(ARQ_U2_RESUMO, "U2 resumo")

    linhas = montar_saida_u3(df_u1, df_u2_linhas)
    pagamentos = montar_pagamentos(linhas)

    qtd_pagamentos_u3 = int(pagamentos["chave_pagamento"].nunique())
    qtd_linhas_operacionais_u3 = int(len(linhas))
    qtd_linhas_monofonte_aprovadas = int((linhas["origem_linha_u3"] == "fonte_monofonte_aprovada_u0_u1").sum())
    qtd_linhas_multifonte_decompostas = int((linhas["origem_linha_u3"] == "fonte_multifonte_decomposta_u2").sum())
    qtd_pagamentos_multifonte_decompostos = int(
        linhas.loc[linhas["origem_linha_u3"] == "fonte_multifonte_decomposta_u2", "chave_pagamento"].nunique()
    )
    qtd_candidatos_fifo_apenas_diagnosticos = int(
        (linhas["origem_linha_u3"] == "candidato_fifo_apenas_diagnostico").sum()
    )
    qtd_sem_lote_sem_candidato_fifo = int(
        (linhas["origem_linha_u3"] == "pagamento_sem_lote_sugerido").sum()
    )
    qtd_pagamentos_sem_lote_sugerido = qtd_candidatos_fifo_apenas_diagnosticos + qtd_sem_lote_sem_candidato_fifo
    qtd_pagamentos_executaveis_operacionalmente_u3 = int(
        (pagamentos["executavel_operacionalmente_u3"] == "sim").sum()
    )
    qtd_pagamentos_bloqueados_u3 = int((pagamentos["bloqueio_u3"] == "sim").sum())
    qtd_pagamentos_nao_auditaveis_u3 = int((pagamentos["nao_auditavel_u3"] == "sim").sum())

    pagamentos_unicos = pagamentos.drop_duplicates("chave_pagamento")
    soma_valores_pagamentos_unicos_u3 = round2(pagamentos_unicos["valor_pagamento"].sum())
    soma_resgates_operacionais_u3 = round2(linhas["valor_resgate_operacional_u3"].sum())
    soma_resgates_multifonte_u3 = round2(
        linhas.loc[
            linhas["origem_linha_u3"] == "fonte_multifonte_decomposta_u2",
            "valor_resgate_operacional_u3",
        ].sum()
    )
    maior_diferenca_cobertura_multifonte_u3 = round2(
        abs(
            linhas.loc[
                linhas["origem_linha_u3"] == "fonte_multifonte_decomposta_u2",
                "diferenca_cobertura_u3",
            ]
        ).max()
    )

    resumo = {
        "qtd_pagamentos_u3": qtd_pagamentos_u3,
        "qtd_linhas_operacionais_u3": qtd_linhas_operacionais_u3,
        "qtd_linhas_monofonte_aprovadas": qtd_linhas_monofonte_aprovadas,
        "qtd_linhas_multifonte_decompostas": qtd_linhas_multifonte_decompostas,
        "qtd_pagamentos_multifonte_decompostos": qtd_pagamentos_multifonte_decompostos,
        "qtd_pagamentos_sem_lote_sugerido": qtd_pagamentos_sem_lote_sugerido,
        "qtd_candidatos_fifo_apenas_diagnosticos": qtd_candidatos_fifo_apenas_diagnosticos,
        "qtd_sem_lote_sem_candidato_fifo": qtd_sem_lote_sem_candidato_fifo,
        "qtd_pagamentos_executaveis_operacionalmente_u3": qtd_pagamentos_executaveis_operacionalmente_u3,
        "qtd_pagamentos_bloqueados_u3": qtd_pagamentos_bloqueados_u3,
        "qtd_pagamentos_nao_auditaveis_u3": qtd_pagamentos_nao_auditaveis_u3,
        "soma_valores_pagamentos_unicos_u3": soma_valores_pagamentos_unicos_u3,
        "soma_resgates_operacionais_u3": soma_resgates_operacionais_u3,
        "soma_resgates_multifonte_u3": soma_resgates_multifonte_u3,
        "maior_diferenca_cobertura_multifonte_u3": maior_diferenca_cobertura_multifonte_u3,
        "status_geral_u3": STATUS_GERAL,
    }

    assert qtd_pagamentos_u3 == 159, f"Esperado 159 pagamentos únicos, obtido {qtd_pagamentos_u3}"
    assert qtd_linhas_operacionais_u3 == 175, f"Esperado 175 linhas, obtido {qtd_linhas_operacionais_u3}"
    assert qtd_linhas_monofonte_aprovadas == 33, f"Esperado 33 monofonte, obtido {qtd_linhas_monofonte_aprovadas}"
    assert qtd_linhas_multifonte_decompostas == 32, f"Esperado 32 multifonte, obtido {qtd_linhas_multifonte_decompostas}"
    assert qtd_pagamentos_multifonte_decompostos == 16, f"Esperado 16 multifonte, obtido {qtd_pagamentos_multifonte_decompostos}"
    assert qtd_pagamentos_sem_lote_sugerido == 110, f"Esperado 110 sem lote, obtido {qtd_pagamentos_sem_lote_sugerido}"
    assert qtd_candidatos_fifo_apenas_diagnosticos == 109, f"Esperado 109 FIFO, obtido {qtd_candidatos_fifo_apenas_diagnosticos}"
    assert qtd_sem_lote_sem_candidato_fifo == 1, f"Esperado 1 sem lote sem FIFO, obtido {qtd_sem_lote_sem_candidato_fifo}"
    assert maior_diferenca_cobertura_multifonte_u3 <= 0.01, (
        f"Divergência multifonte acima de 0.01: {maior_diferenca_cobertura_multifonte_u3}"
    )

    linhas.to_csv(ARQ_LINHAS, index=False)
    pagamentos.to_csv(ARQ_PAGAMENTOS, index=False)
    pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()]).to_csv(ARQ_RESUMO, index=False)

    fontes_lidas = {
        "S7G": df_s7g.shape,
        "U0_PAGAMENTOS": df_u0_pagamentos.shape,
        "U0_FONTES": df_u0_fontes.shape,
        "U1_MATRIZ": df_u1.shape,
        "U2_LINHAS": df_u2_linhas.shape,
        "U2_PAGAMENTOS": df_u2_pagamentos.shape,
        "U2_RESUMO": df_u2_resumo.shape,
    }

    linhas_fontes = "\n".join(
        f"- `{nome}`: `{shape[0]} x {shape[1] if len(shape) > 1 else 0}`"
        for nome, shape in fontes_lidas.items()
    )
    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())

    classes_linhas = (
        linhas.groupby("origem_linha_u3")
        .agg(qtd_linhas=("origem_linha_u3", "size"), qtd_pagamentos=("chave_pagamento", "nunique"))
        .reset_index()
        .sort_values("origem_linha_u3")
    )
    texto_classes_linhas = "\n".join(
        f"- `{r['origem_linha_u3']}`: linhas=`{r['qtd_linhas']}`, pagamentos=`{r['qtd_pagamentos']}`"
        for _, r in classes_linhas.iterrows()
    )

    classes_pagamentos = (
        pagamentos.groupby("tipo_pagamento_operacional_u3")
        .agg(qtd_pagamentos=("chave_pagamento", "nunique"))
        .reset_index()
        .sort_values("tipo_pagamento_operacional_u3")
    )
    texto_classes_pagamentos = "\n".join(
        f"- `{r['tipo_pagamento_operacional_u3']}`: pagamentos=`{r['qtd_pagamentos']}`"
        for _, r in classes_pagamentos.iterrows()
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U3 — Saída operacional diagnóstica de pagamentos com multifonte

- MICROETAPA: V17-F0-U.3
- CLASSE: DIAGNÓSTICO / EXPORTÁVEL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #332
- MICROETAPA_ANTERIOR: V17-F0-U.2
- STATUS_GERAL_U3: `{STATUS_GERAL}`

## Objetivo

Integrar a decomposição multifonte da U.2 a uma saída diagnóstica operacional consolidada de pagamentos.

A U.3 não altera recomendador oficial, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

{linhas_fontes}

## Artefatos diagnósticos gerados

- `{ARQ_LINHAS.relative_to(BASE_DIR)}`
- `{ARQ_PAGAMENTOS.relative_to(BASE_DIR)}`
- `{ARQ_RESUMO.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Classes por origem de linha

{texto_classes_linhas}

## Classes por pagamento

{texto_classes_pagamentos}

## Interpretação operacional

A U.3 consolida os 159 pagamentos originais em 175 linhas operacionais diagnósticas. Os pagamentos multifonte deixam de aparecer apenas como agregados e passam a ter linhas fonte-a-fonte com valor de resgate consumível, herdado da U.2.

A soma dos pagamentos é calculada por pagamento único, não por linha, para evitar dupla contagem dos multifontes.

## Decisão normativa preservada

- Os 110 pagamentos sem lote sugerido permanecem bloqueados/pendentes.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte FIFO é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- A decomposição multifonte permanece diagnóstica.
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
- Exportador oficial não alterado.

## Status

`{STATUS_GERAL}`
"""
    ARQ_LOG.write_text(log, encoding="utf-8")

    print("=== U3 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")

    print("\nClasses por origem de linha:")
    print(classes_linhas.to_string(index=False))

    print("\nClasses por pagamento:")
    print(classes_pagamentos.to_string(index=False))

    print("\nCSVs:")
    print(ARQ_RESUMO.relative_to(BASE_DIR))
    print(ARQ_PAGAMENTOS.relative_to(BASE_DIR))
    print(ARQ_LINHAS.relative_to(BASE_DIR))

    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

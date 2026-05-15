from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DIR_DIAG = BASE_DIR / "saidas/diagnostico"

ARQ_U0_PAGAMENTOS = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv"
ARQ_U0_FONTES = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv"
ARQ_U0_MULTIFONTE = DIR_DIAG / "auditoria_recomendacoes_pagamento_v17_f0_u0_multifonte.csv"
ARQ_U0_CANDIDATOS = DIR_DIAG / "candidatos_correcao_recomendador_pagamentos_v17_f0_u0.csv"

ARQ_S7G = DIR_DIAG / "tabela_operacional_pagamentos_v17_f0_s7g.csv"
ARQ_S7C = DIR_DIAG / "auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv"
ARQ_S7F = DIR_DIAG / "auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv"
ARQ_S7B = DIR_DIAG / "auditoria_matriz_elegibilidade_fontes_v17_f0_s7b.csv"
ARQ_S7J = DIR_DIAG / "auditoria_uso_operacional_tabela_pagamentos_v17_f0_s7j.csv"

ARQ_MATRIZ = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_matriz.csv"
ARQ_RESUMO = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_resumo.csv"
ARQ_CLASSES = DIR_DIAG / "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_classes.csv"
ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U1_CRITERIOS_ELEGIBILIDADE_OPERACIONAL_PAGAMENTOS.md"

STATUS_GERAL = "criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_gerados"


def normalizar_texto(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def to_float(x) -> float:
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        f = float(x)
        return 0.0 if math.isnan(f) else f
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "n/d"}:
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


def is_sim(x) -> bool:
    return normalizar_texto(x) == "sim"


def sim_nao(flag: bool | None) -> str:
    if flag is True:
        return "sim"
    if flag is False:
        return "nao"
    return "n/d"


def carregar_csv_obrigatorio(path: Path, nome: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo obrigatório ausente para U.1: {path}\n"
            f"Execute antes: python -B scripts/diagnostico/auditar_recomendacoes_pagamento_v17_f0_u0.py"
        )
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"Arquivo obrigatório vazio para U.1: {path}")
    return df


def carregar_csv_opcional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def contar_pagamentos_unicos(df: pd.DataFrame, coluna_flag: str) -> int:
    if coluna_flag not in df.columns:
        return 0
    return int(df.loc[df[coluna_flag].map(is_sim), "chave_pagamento"].nunique())


def classe_bloqueio_fonte(row: dict) -> tuple[str | None, str | None]:
    if is_sim(row.get("fonte_em_carencia")):
        return "fonte_bloqueada_por_carencia", "fonte_em_carencia"
    if is_sim(row.get("fonte_sem_liquidez")):
        return "fonte_bloqueada_por_liquidez", "fonte_sem_liquidez"
    if is_sim(row.get("fonte_futura_indevida")):
        return "fonte_bloqueada_por_materializacao", "fonte_futura_indevida_ou_nao_materializada"
    if is_sim(row.get("fonte_pos_switching_nao_materializada")):
        return "fonte_bloqueada_por_pos_switching_nao_materializado", "fonte_pos_switching_nao_materializada"
    if is_sim(row.get("valor_resgate_maior_que_saldo")):
        return "fonte_bloqueada_por_saldo_insuficiente", "valor_resgate_maior_que_saldo"
    return None, None


def montar_linhas_u1(df_pag: pd.DataFrame, df_fontes: pd.DataFrame) -> list[dict]:
    linhas = []

    fontes_por_chave: dict[str, list[dict]] = {}
    if not df_fontes.empty and "chave_pagamento" in df_fontes.columns:
        for _, r in df_fontes.iterrows():
            fontes_por_chave.setdefault(str(r["chave_pagamento"]), []).append(r.to_dict())

    for _, pag in df_pag.iterrows():
        p = pag.to_dict()
        chave = str(p.get("chave_pagamento"))
        fontes = fontes_por_chave.get(chave, [])

        pagamento_sem_lote = is_sim(p.get("pendencia_sem_lote_sugerido")) or not is_sim(p.get("tem_fonte_recomendada"))
        candidato_fifo = is_sim(p.get("candidato_fifo_detectado"))
        multifonte_pendente = is_sim(p.get("pendencia_multifonte_sem_valor_resgate_explicito"))
        multifonte_decomposta = is_sim(p.get("multifonte_decomposta_u0"))
        violacao_dura = is_sim(p.get("violacao_dura_fonte_aprovada"))
        valor_pagamento = to_float(p.get("valor"))

        # Caso sem fonte recomendada: manter uma linha diagnóstica sem promover FIFO.
        if pagamento_sem_lote or not fontes:
            classe = "candidato_fifo_apenas_diagnostico" if candidato_fifo else "pendencia_sem_lote_sugerido"
            motivo = "candidato_fifo_nao_aprovado_normativamente" if candidato_fifo else "sem_lote_sugerido"
            linhas.append({
                "pagamento_idx": p.get("pagamento_idx"),
                "chave_pagamento": chave,
                "data": p.get("data"),
                "conta": p.get("conta"),
                "valor_pagamento": round(valor_pagamento, 2),
                "fonte": "sem_fonte_recomendada",
                "tipo_fonte": "n/d",
                "status_operacional_atual": p.get("status_operacional"),
                "fonte_aprovada_para_pagamento": "nao",
                "fonte_recomendada_atual": "nao",
                "candidato_fifo_detectado": sim_nao(candidato_fifo),
                "criterio_materializada": "n/d",
                "criterio_nao_futura": "n/d",
                "criterio_temporalmente_disponivel": "n/d",
                "criterio_liquidez": "n/d",
                "criterio_carencia": "n/d",
                "criterio_saldo_suficiente": "n/d",
                "criterio_pos_switching_materializado": "n/d",
                "criterio_nao_competicao_diaria": "n/d",
                "criterio_precedencia_intradiaria": "n/d",
                "criterio_valor_resgate_explicito": "n/d",
                "criterio_multifonte_decomposta": "n/d",
                "classe_operacional_u1": classe,
                "bloqueio_operacional_u1": "sim",
                "motivo_bloqueio_u1": motivo,
                "pode_virar_recomendacao_em_etapa_futura": "nao",
                "precisa_u2_multifonte": "nao",
                "precisa_u3_refactibilizacao": "sim",
                "observacao_normativa": "Pagamento sem fonte aprovada. Candidato FIFO, quando presente, permanece diagnóstico e não substitui elegibilidade normativa.",
            })
            continue

        # Casos com fonte recomendada: avaliar fonte-a-fonte sem alterar recomendação.
        for fonte in fontes:
            bloqueio_classe, bloqueio_motivo = classe_bloqueio_fonte(fonte)

            fonte_nome = fonte.get("lote_fonte")
            fonte_aprovada = is_sim(p.get("tem_fonte_recomendada"))
            criterio_saldo = not is_sim(fonte.get("valor_resgate_maior_que_saldo"))
            criterio_pos_sw = True
            if is_sim(fonte.get("usa_lote_pos_switching_s7g")):
                if is_sim(fonte.get("fonte_pos_switching_nao_materializada")):
                    criterio_pos_sw = False
                elif is_sim(fonte.get("lote_pos_switching_materializado_s7c")):
                    criterio_pos_sw = True
                else:
                    criterio_pos_sw = None

            if bloqueio_classe:
                classe = bloqueio_classe
                motivo = bloqueio_motivo
                bloqueio = "sim"
                pode_futuro = "nao"
                precisa_u2 = "nao"
                precisa_u3 = "sim"
            elif multifonte_pendente:
                classe = "pendencia_multifonte_sem_valor_resgate_explicito"
                motivo = "multifonte_sem_valor_resgate_explicito_por_fonte_na_origem"
                bloqueio = "sim"
                pode_futuro = "nao"
                precisa_u2 = "sim"
                precisa_u3 = "nao"
            elif fonte_aprovada and not violacao_dura:
                classe = "fonte_aprovada_sem_violacao_dura"
                motivo = "sem_bloqueio_operacional_detectado"
                bloqueio = "nao"
                pode_futuro = "sim"
                precisa_u2 = "nao"
                precisa_u3 = "nao"
            else:
                classe = "nao_auditavel_por_dado_insuficiente"
                motivo = "criterios_insuficientes_para_aprovacao_conservadora"
                bloqueio = "sim"
                pode_futuro = "nao"
                precisa_u2 = "nao"
                precisa_u3 = "sim"

            linhas.append({
                "pagamento_idx": p.get("pagamento_idx"),
                "chave_pagamento": chave,
                "data": p.get("data"),
                "conta": p.get("conta"),
                "valor_pagamento": round(valor_pagamento, 2),
                "fonte": fonte_nome,
                "tipo_fonte": fonte.get("tipo_fonte", "n/d"),
                "status_operacional_atual": p.get("status_operacional"),
                "fonte_aprovada_para_pagamento": sim_nao(fonte_aprovada),
                "fonte_recomendada_atual": "sim",
                "candidato_fifo_detectado": "nao",
                "criterio_materializada": fonte.get("materializada_s7b", "n/d"),
                "criterio_nao_futura": sim_nao(not is_sim(fonte.get("fonte_futura_s7b")) if fonte.get("fonte_futura_s7b") != "n/d" else None),
                "criterio_temporalmente_disponivel": fonte.get("elegivel_temporalmente_s7b", "n/d"),
                "criterio_liquidez": sim_nao(not is_sim(fonte.get("fonte_sem_liquidez"))),
                "criterio_carencia": sim_nao(not is_sim(fonte.get("fonte_em_carencia"))),
                "criterio_saldo_suficiente": sim_nao(criterio_saldo),
                "criterio_pos_switching_materializado": sim_nao(criterio_pos_sw),
                "criterio_nao_competicao_diaria": "sim" if fonte_aprovada else "n/d",
                "criterio_precedencia_intradiaria": "sim" if fonte_aprovada else "n/d",
                "criterio_valor_resgate_explicito": "nao" if multifonte_pendente else "sim",
                "criterio_multifonte_decomposta": sim_nao(multifonte_decomposta) if is_sim(p.get("multifonte")) else "n/d",
                "classe_operacional_u1": classe,
                "bloqueio_operacional_u1": bloqueio,
                "motivo_bloqueio_u1": motivo,
                "pode_virar_recomendacao_em_etapa_futura": pode_futuro,
                "precisa_u2_multifonte": precisa_u2,
                "precisa_u3_refactibilizacao": precisa_u3,
                "observacao_normativa": "Fonte já aprovada na U.0 não é alterada. Multifonte segue pendente até valor explícito por fonte.",
            })

    return linhas


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    df_pag = carregar_csv_obrigatorio(ARQ_U0_PAGAMENTOS, "U0 pagamentos")
    df_fontes = carregar_csv_obrigatorio(ARQ_U0_FONTES, "U0 fontes")
    df_multi = carregar_csv_obrigatorio(ARQ_U0_MULTIFONTE, "U0 multifonte")
    df_cand = carregar_csv_obrigatorio(ARQ_U0_CANDIDATOS, "U0 candidatos")

    # Fontes auxiliares lidas para registrar disponibilidade e preservar trilha, sem promover candidatos.
    fontes_aux = {
        "S7G": carregar_csv_opcional(ARQ_S7G),
        "S7C": carregar_csv_opcional(ARQ_S7C),
        "S7F": carregar_csv_opcional(ARQ_S7F),
        "S7B": carregar_csv_opcional(ARQ_S7B),
        "S7J": carregar_csv_opcional(ARQ_S7J),
    }

    linhas = montar_linhas_u1(df_pag, df_fontes)
    df_matriz = pd.DataFrame(linhas)

    classes = (
        df_matriz.groupby("classe_operacional_u1", dropna=False)
        .agg(
            qtd_linhas=("classe_operacional_u1", "size"),
            qtd_pagamentos=("chave_pagamento", "nunique"),
        )
        .reset_index()
        .sort_values(["classe_operacional_u1"])
    )

    def count_rows_class(nome: str) -> int:
        return int((df_matriz["classe_operacional_u1"] == nome).sum())

    def count_pag_class(nome: str) -> int:
        return int(df_matriz.loc[df_matriz["classe_operacional_u1"] == nome, "chave_pagamento"].nunique())

    qtd_pagamentos_u1 = int(df_matriz["chave_pagamento"].nunique())
    qtd_fontes_u1 = int(len(df_matriz))
    qtd_fontes_aprovadas_sem_violacao_dura = count_rows_class("fonte_aprovada_sem_violacao_dura")
    qtd_linhas_fontes_multifonte_pendentes_u2 = count_rows_class("pendencia_multifonte_sem_valor_resgate_explicito")
    qtd_pagamentos_aprovados_sem_bloqueio_duro_inclui_multifonte_pendente = int(
        df_matriz.loc[
            df_matriz["classe_operacional_u1"].isin([
                "fonte_aprovada_sem_violacao_dura",
                "pendencia_multifonte_sem_valor_resgate_explicito",
            ]),
            "chave_pagamento",
        ].nunique()
    )

    resumo = {
        "qtd_pagamentos_u1": qtd_pagamentos_u1,
        "qtd_fontes_u1": qtd_fontes_u1,
        "qtd_fontes_aprovadas_sem_violacao_dura": qtd_fontes_aprovadas_sem_violacao_dura,
        "qtd_linhas_fontes_multifonte_pendentes_u2": qtd_linhas_fontes_multifonte_pendentes_u2,
        "qtd_pagamentos_aprovados_sem_bloqueio_duro_inclui_multifonte_pendente": qtd_pagamentos_aprovados_sem_bloqueio_duro_inclui_multifonte_pendente,
        "qtd_pendencias_sem_lote_sugerido": int(df_pag["pendencia_sem_lote_sugerido"].map(is_sim).sum()),
        "qtd_candidatos_fifo_apenas_diagnosticos": int(df_pag["candidato_fifo_detectado"].map(is_sim).sum()),
        "qtd_multifonte_sem_valor_resgate_explicito": int(df_pag["pendencia_multifonte_sem_valor_resgate_explicito"].map(is_sim).sum()),
        "qtd_bloqueios_por_carencia": count_pag_class("fonte_bloqueada_por_carencia"),
        "qtd_bloqueios_por_liquidez": count_pag_class("fonte_bloqueada_por_liquidez"),
        "qtd_bloqueios_por_materializacao": count_pag_class("fonte_bloqueada_por_materializacao"),
        "qtd_bloqueios_por_pos_switching_nao_materializado": count_pag_class("fonte_bloqueada_por_pos_switching_nao_materializado"),
        "qtd_bloqueios_por_saldo_insuficiente": count_pag_class("fonte_bloqueada_por_saldo_insuficiente"),
        "qtd_bloqueios_por_precedencia_intradiaria": count_pag_class("fonte_bloqueada_por_precedencia_intradiaria"),
        "qtd_bloqueios_por_competicao_diaria": count_pag_class("fonte_bloqueada_por_competicao_diaria"),
        "qtd_nao_auditaveis": count_pag_class("nao_auditavel_por_dado_insuficiente"),
        "qtd_casos_prontos_para_u2_multifonte": int(df_matriz.loc[df_matriz["precisa_u2_multifonte"] == "sim", "chave_pagamento"].nunique()),
        "qtd_casos_prontos_para_u3_refactibilizacao": int(df_matriz.loc[df_matriz["precisa_u3_refactibilizacao"] == "sim", "chave_pagamento"].nunique()),
        "qtd_linhas_classe_fonte_aprovada_sem_violacao_dura": count_rows_class("fonte_aprovada_sem_violacao_dura"),
        "qtd_linhas_classe_pendencia_multifonte": count_rows_class("pendencia_multifonte_sem_valor_resgate_explicito"),
        "qtd_linhas_classe_candidato_fifo": count_rows_class("candidato_fifo_apenas_diagnostico"),
        "qtd_linhas_classe_pendencia_sem_lote": count_rows_class("pendencia_sem_lote_sugerido"),
        "status_geral_u1": STATUS_GERAL,
    }

    df_resumo = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    df_matriz.to_csv(ARQ_MATRIZ, index=False)
    df_resumo.to_csv(ARQ_RESUMO, index=False)
    classes.to_csv(ARQ_CLASSES, index=False)

    fontes_lidas = {
        "U0_PAGAMENTOS": df_pag.shape,
        "U0_FONTES": df_fontes.shape,
        "U0_MULTIFONTE": df_multi.shape,
        "U0_CANDIDATOS": df_cand.shape,
        **{k: v.shape for k, v in fontes_aux.items()},
    }

    linhas_fontes = "\n".join(
        f"- `{nome}`: `{shape[0]} x {shape[1] if len(shape) > 1 else 0}`"
        for nome, shape in fontes_lidas.items()
    )
    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())
    linhas_classes = "\n".join(
        f"- `{r['classe_operacional_u1']}`: linhas=`{r['qtd_linhas']}`, pagamentos=`{r['qtd_pagamentos']}`"
        for _, r in classes.iterrows()
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U1 — Critérios de elegibilidade operacional para recomendações de pagamento

- MICROETAPA: V17-F0-U.1
- CLASSE: DIAGNÓSTICO / NORMATIVA OPERACIONAL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #330
- MICROETAPA_ANTERIOR: V17-F0-U.0
- STATUS_GERAL_U1: `{STATUS_GERAL}`

## Objetivo

Formalizar critérios operacionais para distinguir fonte aprovada, fonte inelegível, fonte em carência, fonte sem liquidez, fonte futura, fonte pós-switching não materializada, candidato FIFO apenas diagnóstico, pagamento sem lote sugerido e pagamento multifonte sem valor explícito por fonte.

A U.1 não altera recomendador, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

{linhas_fontes}

## Artefatos diagnósticos gerados

- `{ARQ_MATRIZ.relative_to(BASE_DIR)}`
- `{ARQ_RESUMO.relative_to(BASE_DIR)}`
- `{ARQ_CLASSES.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Classes operacionais

{linhas_classes}

## Decisão normativa preservada

Os casos com `candidato_fifo_detectado = sim` permanecem diagnósticos. Eles não são promovidos automaticamente a fonte elegível, fonte aprovada, lote sugerido ou recomendação operacional.

A U.1 preserva a distinção entre:

- fonte aprovada;
- candidato FIFO apenas diagnóstico;
- pendência sem lote sugerido;
- pendência multifonte sem valor explícito por fonte.

## Restrições preservadas

- Motor econômico não alterado.
- Recomendador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.
- T.0–T.8 não reabertos.
- S.7 não reaberta.

## Status

`{STATUS_GERAL}`
"""
    ARQ_LOG.write_text(log, encoding="utf-8")

    print("=== U1 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")
    print("\nClasses:")
    print(classes.to_string(index=False))
    print("\nCSVs:")
    print(ARQ_MATRIZ.relative_to(BASE_DIR))
    print(ARQ_RESUMO.relative_to(BASE_DIR))
    print(ARQ_CLASSES.relative_to(BASE_DIR))
    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]

XLSX_OFICIAL = RAIZ / "saidas" / "oficial" / "relatorio_operacional_v225.xlsx"
ABA_TABELA = "Tabela Operacional Pagamentos"

CSV_S7G = RAIZ / "saidas" / "diagnostico" / "tabela_operacional_pagamentos_v17_f0_s7g.csv"

CSV_CLASSIFICACAO = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv"
)
CSV_RESUMO = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv"
)


COLUNAS_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "lote_recomendado",
    "status_operacional",
    "acao_recomendada",
    "problema_operacional",
    "motivo_operacional",
    "saldo_pos_pagamento",
    "saldo_pos_pagamento_origem",
    "alerta_operacional",
    "tipo_alerta_operacional",
]


COLUNAS_SAIDA = [
    "data",
    "conta",
    "valor",
    "status_operacional",
    "acao_recomendada",
    "problema_operacional",
    "motivo_operacional",
    "saldo_pos_pagamento",
    "saldo_pos_pagamento_origem",
    "alerta_operacional",
    "tipo_alerta_operacional",
    "classe_t0",
    "subclasse_t0",
    "nivel_evidencia",
    "acao_recomendada_t1",
    "observacao_t0",
]


def _normalizar_texto(x: object) -> str:
    if pd.isna(x):
        return ""
    txt = str(x).strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return txt.casefold().strip()


def _eh_vazio(x: object) -> bool:
    if pd.isna(x):
        return True
    txt = str(x).strip()
    return txt == "" or txt.casefold() in {"nan", "none", "null", "na"}


def _to_num(x: object) -> float:
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)

    txt = str(x).strip()
    if not txt:
        return 0.0

    # Suporta tanto "1.234,56" quanto "1234.56".
    if "," in txt and "." in txt:
        txt = txt.replace(".", "").replace(",", ".")
    elif "," in txt:
        txt = txt.replace(",", ".")

    try:
        return float(txt)
    except ValueError:
        return 0.0


def _carregar_tabela() -> tuple[pd.DataFrame | None, str, str]:
    if XLSX_OFICIAL.exists():
        try:
            df = pd.read_excel(XLSX_OFICIAL, sheet_name=ABA_TABELA)
            return df, "xlsx", str(XLSX_OFICIAL)
        except Exception as exc:
            print(f"erro_carregar_xlsx={type(exc).__name__}")

    if CSV_S7G.exists():
        try:
            df = pd.read_csv(CSV_S7G)
            return df, "csv_s7g", str(CSV_S7G)
        except Exception as exc:
            print(f"erro_carregar_csv_s7g={type(exc).__name__}")

    return None, "indisponivel", ""


def _classificar_linha(row: pd.Series) -> dict[str, str]:
    problema = _normalizar_texto(row.get("problema_operacional"))
    motivo = _normalizar_texto(row.get("motivo_operacional"))
    alerta = _normalizar_texto(row.get("alerta_operacional"))
    tipo_alerta = _normalizar_texto(row.get("tipo_alerta_operacional"))
    origem_saldo = _normalizar_texto(row.get("saldo_pos_pagamento_origem"))
    saldo = _to_num(row.get("saldo_pos_pagamento"))

    classe = "classe_indeterminada_requer_T1"
    subclasse = "sem_regra_conclusiva_t0"
    nivel = "inferida_fraca"
    acao_t1 = "revisar_fontes_temporais_em_T1"
    observacao = "T0 classificou de forma conservadora; não altera recomendação."

    if (
        problema == "sem_saldo_temporal_auditavel"
        and motivo == "saldo_temporal_insuficiente_cumulativo"
    ):
        classe = "insuficiencia_temporal_explicita"

        if saldo <= 0:
            subclasse = "saldo_temporal_insuficiente_cumulativo__saldo_fallback_zero_ou_negativo"
            nivel = "explicita"
            observacao = (
                "Alerta explícito de insuficiência temporal cumulativa; "
                "saldo fallback zero ou negativo."
            )
        else:
            subclasse = "saldo_temporal_insuficiente_cumulativo__saldo_fallback_positivo_mas_sem_fonte_auditavel"
            nivel = "explicita_com_indicio_temporal"
            observacao = (
                "Alerta explícito de insuficiência temporal cumulativa; "
                "há saldo fallback positivo, mas sem fonte auditável aprovada."
            )

        acao_t1 = "investigar_fontes_temporais_recebidos_aportes_switching"

    elif problema == "sem_saldo_temporal_auditavel":
        classe = "sem_saldo_temporal_auditavel"
        subclasse = motivo if motivo else "motivo_operacional_nao_informado"
        nivel = "explicita"
        acao_t1 = "investigar_origem_do_alerta_sem_saldo_temporal"
        observacao = "Problema operacional explícito sem fonte temporal auditável."

    elif alerta == "sim" and tipo_alerta == "explicito":
        classe = "alerta_operacional_explicito_sem_lote"
        subclasse = problema if problema else "problema_operacional_nao_informado"
        nivel = "explicita"
        acao_t1 = "investigar_alerta_operacional_sem_lote"
        observacao = "Linha sem lote com alerta explícito, mas sem regra T0 mais específica."

    elif origem_saldo == "calculado_fallback":
        classe = "saldo_fallback_sem_lote"
        subclasse = "saldo_fallback_sem_fonte_auditavel_aprovada"
        nivel = "inferida_fraca"
        acao_t1 = "investigar_fonte_temporal_do_saldo_fallback"
        observacao = "Há saldo calculado por fallback, mas não há lote sugerido."

    return {
        "classe_t0": classe,
        "subclasse_t0": subclasse,
        "nivel_evidencia": nivel,
        "acao_recomendada_t1": acao_t1,
        "observacao_t0": observacao,
    }


def main() -> int:
    df, fonte, caminho = _carregar_tabela()

    print(f"fonte_tabela_operacional={fonte}")
    if caminho:
        print(f"caminho_tabela_operacional={caminho}")

    if df is None:
        print("tabela_operacional_carregada=nao")
        print("status_geral_t0=falha_classificacao_110_sem_lote")
        return 1

    print("tabela_operacional_carregada=sim")
    print(f"qtd_linhas_tabela_operacional={len(df)}")
    print(f"qtd_colunas_tabela_operacional={len(df.columns)}")

    faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    print(f"qtd_colunas_obrigatorias_ausentes={len(faltantes)}")
    print(
        "colunas_obrigatorias_ausentes="
        + ("nenhuma" if not faltantes else ",".join(faltantes))
    )

    if faltantes:
        print("status_geral_t0=falha_classificacao_110_sem_lote")
        return 1

    sem_lote_mask = df["lote_recomendado"].map(_eh_vazio)
    sem_lote = df.loc[sem_lote_mask].copy()

    print(f"qtd_pagamentos_sem_lote_sugerido={len(sem_lote)}")

    sem_lote["alerta_norm"] = sem_lote["alerta_operacional"].map(_normalizar_texto)
    sem_lote["tipo_alerta_norm"] = sem_lote["tipo_alerta_operacional"].map(_normalizar_texto)

    qtd_alerta_explicito = int(
        ((sem_lote["alerta_norm"] == "sim") & (sem_lote["tipo_alerta_norm"] == "explicito")).sum()
    )
    qtd_sem_alerta_explicito = int(len(sem_lote) - qtd_alerta_explicito)

    print(f"qtd_sem_lote_com_alerta_explicito={qtd_alerta_explicito}")
    print(f"qtd_sem_lote_sem_alerta_explicito={qtd_sem_alerta_explicito}")

    classificacoes = sem_lote.apply(_classificar_linha, axis=1, result_type="expand")
    saida = pd.concat([sem_lote.reset_index(drop=True), classificacoes.reset_index(drop=True)], axis=1)

    # Normaliza data apenas para ordenação e exportação legível.
    saida["_data_ordem"] = pd.to_datetime(saida["data"], errors="coerce")
    saida = saida.sort_values(["_data_ordem", "conta", "valor"], na_position="last").drop(columns=["_data_ordem"])

    # Garante colunas finais mesmo que alguma esteja ausente por alteração futura.
    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()

    CSV_CLASSIFICACAO.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_CLASSIFICACAO, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final.groupby(["classe_t0", "subclasse_t0", "nivel_evidencia"], dropna=False)
        .size()
        .reset_index(name="qtd_pagamentos")
        .sort_values(["classe_t0", "subclasse_t0", "nivel_evidencia"])
    )
    resumo.to_csv(CSV_RESUMO, index=False, encoding="utf-8-sig")

    qtd_classificados = int(saida_final["classe_t0"].astype(str).str.len().gt(0).sum())
    qtd_nao_classificados = int(len(saida_final) - qtd_classificados)

    print(f"qtd_sem_lote_classificados={qtd_classificados}")
    print(f"qtd_sem_lote_nao_classificados={qtd_nao_classificados}")
    print(f"qtd_classes_t0={saida_final['classe_t0'].nunique()}")

    print("\nresumo_classes_t0=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t0_aluguel_2026_06_12_classificada={_sentinela('2026-06-12', 'Aluguel')}")
    print(f"sentinela_t0_condominio_2026_06_20_classificada={_sentinela('2026-06-20', 'Condomínio')}")

    print(f"csv_classificacao_t0={CSV_CLASSIFICACAO}")
    print(f"csv_resumo_t0={CSV_RESUMO}")

    status = "classificacao_110_sem_lote_gerada"
    if len(df) != 159:
        status = "falha_classificacao_110_sem_lote"
    if len(sem_lote) != 110:
        status = "falha_classificacao_110_sem_lote"
    if qtd_classificados != 110:
        status = "falha_classificacao_110_sem_lote"

    print(f"status_geral_t0={status}")
    return 0 if status == "classificacao_110_sem_lote_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

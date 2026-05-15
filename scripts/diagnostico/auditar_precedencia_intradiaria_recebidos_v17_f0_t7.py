from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]

CSV_LEDGER_T6 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "ledger_diagnostico_recebidos_v17_f0_t6.csv"
)

CSV_T7 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_precedencia_intradiaria_recebidos_v17_f0_t7.csv"
)

CSV_RESUMO_T7 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_precedencia_intradiaria_recebidos_v17_f0_t7.csv"
)


COLUNAS_LEDGER_OBRIGATORIAS = [
    "evento_id_t6",
    "recebido_id",
    "data_evento",
    "tipo_evento_t6",
    "data_recebimento",
    "valor_consumo_diagnostico",
    "saldo_recebido_apos_evento",
    "data_pagamento",
    "conta_pagamento",
    "valor_pagamento",
    "grupo_pagamento_t4",
    "status_competicao_recebidos_t4",
    "classe_decisao_t5",
    "status_regra_operacional_t5",
    "regra_bloqueante_principal_t5",
    "pode_converter_recebido_em_fonte_oficial_t5",
    "usa_recebido_mesma_data_pagamento_t4",
    "natureza_fonte_t6",
]


COLUNAS_SAIDA = [
    "data_pagamento",
    "conta_pagamento",
    "valor_pagamento",
    "grupo_pagamento_t4",
    "classe_decisao_t5",
    "status_regra_operacional_t5",
    "regra_bloqueante_principal_t5",
    "pode_converter_recebido_em_fonte_oficial_t5",
    "status_competicao_recebidos_t4",
    "qtd_componentes_same_day_t7",
    "recebidos_ids_same_day_t7",
    "datas_recebimento_same_day_t7",
    "valor_consumo_same_day_t7",
    "status_precedencia_intradiaria_t7",
    "regra_intradiaria_requerida_t7",
    "pode_promover_recebido_pos_t7",
    "classe_bloqueio_t7",
    "acao_recomendada_t8",
    "nivel_evidencia_t7",
    "observacao_t7",
]


def _normalizar_texto(x: object) -> str:
    if pd.isna(x):
        return ""
    txt = str(x).strip()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return txt.casefold().strip()


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


def _carregar_ledger() -> pd.DataFrame | None:
    if not CSV_LEDGER_T6.exists():
        print("csv_ledger_t6_existe=nao")
        print(f"csv_ledger_t6_esperado={CSV_LEDGER_T6}")
        return None

    df = pd.read_csv(CSV_LEDGER_T6)
    print("csv_ledger_t6_existe=sim")
    print("fonte_ledger_t6=csv_ledger_t6")
    print(f"caminho_ledger_t6={CSV_LEDGER_T6}")
    print(f"qtd_linhas_ledger_t6={len(df)}")

    faltantes = [c for c in COLUNAS_LEDGER_OBRIGATORIAS if c not in df.columns]
    print(f"qtd_colunas_ledger_t6_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_ledger_t6_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        return None

    return df


def _classificar(row: pd.Series) -> dict[str, str]:
    classe_t5 = str(row.get("classe_decisao_t5", "")).strip()
    pode_converter = str(row.get("pode_converter_recebido_em_fonte_oficial_t5", "")).strip()

    if pode_converter == "sim":
        return {
            "status_precedencia_intradiaria_t7": "falha_promocao_indevida_detectada",
            "regra_intradiaria_requerida_t7": "bloqueio_total",
            "pode_promover_recebido_pos_t7": "nao",
            "classe_bloqueio_t7": "inconsistencia_critica_promocao_indevida",
            "acao_recomendada_t8": "interromper_e_auditar_t5_t6",
            "nivel_evidencia_t7": "explicita",
            "observacao_t7": "Foi detectada conversão para fonte oficial, o que viola T5/T6.",
        }

    if classe_t5 == "fonte_oficial_ja_definida":
        return {
            "status_precedencia_intradiaria_t7": "bloqueado_por_fonte_oficial_lote_e_mesma_data",
            "regra_intradiaria_requerida_t7": "R0_preservar_fonte_lote;R1_definir_precedencia_intradiaria",
            "pode_promover_recebido_pos_t7": "nao",
            "classe_bloqueio_t7": "fonte_lote_prevalece",
            "acao_recomendada_t8": "manter_fonte_oficial_por_lote_e_nao_promover_recebido",
            "nivel_evidencia_t7": "explicita",
            "observacao_t7": (
                "Pagamento já possui fonte oficial por lote. O consumo same-day do recebido é apenas "
                "contrafactual e não deve trocar a fonte oficial."
            ),
        }

    if classe_t5 == "bloqueio_intradiario":
        return {
            "status_precedencia_intradiaria_t7": "bloqueado_ate_definir_precedencia_intradiaria",
            "regra_intradiaria_requerida_t7": "R1_definir_precedencia_intradiaria_e_materializacao_antes_do_pagamento",
            "pode_promover_recebido_pos_t7": "nao",
            "classe_bloqueio_t7": "dependencia_intradiaria",
            "acao_recomendada_t8": "formalizar_contrato_intradiario_antes_de_qualquer_promocao",
            "nivel_evidencia_t7": "explicita",
            "observacao_t7": (
                "Pagamento sem lote depende de recebido materializado na mesma data. Sem regra intradiária, "
                "deve permanecer bloqueado."
            ),
        }

    if classe_t5 == "bloqueio_competitivo":
        return {
            "status_precedencia_intradiaria_t7": "bloqueado_por_competicao_e_intradiario",
            "regra_intradiaria_requerida_t7": "R1_definir_precedencia_intradiaria;R2_exigir_suficiencia_competitiva",
            "pode_promover_recebido_pos_t7": "nao",
            "classe_bloqueio_t7": "bloqueio_composto",
            "acao_recomendada_t8": "manter_bloqueio_e_reconciliar_competicao_antes_de_intradiario",
            "nivel_evidencia_t7": "explicita",
            "observacao_t7": (
                "Pagamento combina dependência intradiária com bloqueio competitivo; não é candidato "
                "a promoção por recebido."
            ),
        }

    if classe_t5 == "candidato_diagnostico":
        return {
            "status_precedencia_intradiaria_t7": "inconsistencia_candidato_com_uso_same_day",
            "regra_intradiaria_requerida_t7": "R1_deveria_ter_bloqueado_na_t5",
            "pode_promover_recebido_pos_t7": "nao",
            "classe_bloqueio_t7": "inconsistencia_taxonomica",
            "acao_recomendada_t8": "auditar_t5_classificacao_same_day",
            "nivel_evidencia_t7": "explicita",
            "observacao_t7": (
                "Um candidato diagnóstico não deveria depender de recebido na mesma data; isso indicaria "
                "inconsistência entre T5 e T6."
            ),
        }

    return {
        "status_precedencia_intradiaria_t7": "classe_t5_nao_reconhecida",
        "regra_intradiaria_requerida_t7": "auditoria_manual",
        "pode_promover_recebido_pos_t7": "nao",
        "classe_bloqueio_t7": "classe_desconhecida",
        "acao_recomendada_t8": "auditar_schema_t5_t6",
        "nivel_evidencia_t7": "explicita",
        "observacao_t7": "Classe T5 não reconhecida na auditoria intradiária.",
    }


def main() -> int:
    ledger = _carregar_ledger()
    if ledger is None:
        print("status_geral_t7=falha_auditoria_precedencia_intradiaria_recebidos")
        return 1

    consumos = ledger[ledger["tipo_evento_t6"].astype(str).eq("consumo_contrafactual_t4")].copy()
    consumos_same_day = consumos[
        consumos["usa_recebido_mesma_data_pagamento_t4"].astype(str).str.casefold().eq("sim")
    ].copy()

    print(f"qtd_eventos_consumo_t6={len(consumos)}")
    print(f"qtd_eventos_consumo_same_day_t7={len(consumos_same_day)}")

    if consumos_same_day.empty:
        print("qtd_pagamentos_same_day_t7=0")
        print("status_geral_t7=falha_auditoria_precedencia_intradiaria_recebidos")
        return 1

    agrupado = (
        consumos_same_day
        .groupby(
            [
                "data_pagamento",
                "conta_pagamento",
                "valor_pagamento",
                "grupo_pagamento_t4",
                "classe_decisao_t5",
                "status_regra_operacional_t5",
                "regra_bloqueante_principal_t5",
                "pode_converter_recebido_em_fonte_oficial_t5",
                "status_competicao_recebidos_t4",
            ],
            dropna=False,
        )
        .agg(
            qtd_componentes_same_day_t7=("evento_id_t6", "size"),
            recebidos_ids_same_day_t7=("recebido_id", lambda s: " + ".join(sorted(set(map(str, s))))),
            datas_recebimento_same_day_t7=("data_recebimento", lambda s: " + ".join(sorted(set(map(str, s))))),
            valor_consumo_same_day_t7=("valor_consumo_diagnostico", lambda s: round(sum(_to_num(x) for x in s), 2)),
        )
        .reset_index()
        .sort_values(["data_pagamento", "grupo_pagamento_t4", "conta_pagamento"])
    )

    linhas = []
    for _, row in agrupado.iterrows():
        item = row.to_dict()
        item.update(_classificar(row))
        linhas.append(item)

    saida = pd.DataFrame(linhas)

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida = saida[COLUNAS_SAIDA].copy()

    CSV_T7.parent.mkdir(parents=True, exist_ok=True)
    saida.to_csv(CSV_T7, index=False, encoding="utf-8-sig")

    resumo = (
        saida
        .groupby(
            [
                "classe_decisao_t5",
                "classe_bloqueio_t7",
                "status_precedencia_intradiaria_t7",
                "pode_promover_recebido_pos_t7",
                "nivel_evidencia_t7",
            ],
            dropna=False,
        )
        .agg(
            qtd_pagamentos=("valor_pagamento", "size"),
            valor_pagamentos=("valor_pagamento", lambda s: round(sum(_to_num(x) for x in s), 2)),
            valor_consumo_same_day=("valor_consumo_same_day_t7", lambda s: round(sum(_to_num(x) for x in s), 2)),
            qtd_componentes_same_day=("qtd_componentes_same_day_t7", lambda s: int(sum(_to_num(x) for x in s))),
        )
        .reset_index()
        .sort_values(["classe_decisao_t5", "classe_bloqueio_t7"])
    )
    resumo.to_csv(CSV_RESUMO_T7, index=False, encoding="utf-8-sig")

    qtd_pagamentos_same_day = int(len(saida))
    qtd_componentes_same_day = int(saida["qtd_componentes_same_day_t7"].map(_to_num).sum())
    valor_consumo_same_day = float(saida["valor_consumo_same_day_t7"].map(_to_num).sum())

    qtd_fonte_lote = int(saida["classe_decisao_t5"].eq("fonte_oficial_ja_definida").sum())
    qtd_bloqueio_intradiario = int(saida["classe_decisao_t5"].eq("bloqueio_intradiario").sum())
    qtd_bloqueio_competitivo = int(saida["classe_decisao_t5"].eq("bloqueio_competitivo").sum())
    qtd_candidato = int(saida["classe_decisao_t5"].eq("candidato_diagnostico").sum())
    qtd_classe_desconhecida = int(saida["classe_bloqueio_t7"].eq("classe_desconhecida").sum())
    qtd_inconsistencia_taxonomica = int(saida["classe_bloqueio_t7"].eq("inconsistencia_taxonomica").sum())
    qtd_pode_promover_sim = int(saida["pode_promover_recebido_pos_t7"].eq("sim").sum())
    qtd_pode_converter_t5_sim = int(saida["pode_converter_recebido_em_fonte_oficial_t5"].astype(str).eq("sim").sum())

    print(f"qtd_pagamentos_same_day_t7={qtd_pagamentos_same_day}")
    print(f"qtd_componentes_same_day_t7={qtd_componentes_same_day}")
    print(f"valor_consumo_same_day_t7={round(valor_consumo_same_day, 2)}")
    print(f"qtd_pagamentos_same_day_fonte_oficial_lote_t7={qtd_fonte_lote}")
    print(f"qtd_pagamentos_same_day_bloqueio_intradiario_t7={qtd_bloqueio_intradiario}")
    print(f"qtd_pagamentos_same_day_bloqueio_competitivo_t7={qtd_bloqueio_competitivo}")
    print(f"qtd_pagamentos_same_day_candidato_diagnostico_t7={qtd_candidato}")
    print(f"qtd_pagamentos_same_day_classe_desconhecida_t7={qtd_classe_desconhecida}")
    print(f"qtd_inconsistencia_taxonomica_t7={qtd_inconsistencia_taxonomica}")
    print(f"qtd_pode_promover_recebido_pos_t7_sim={qtd_pode_promover_sim}")
    print(f"qtd_pode_converter_recebido_t5_sim_em_same_day_t7={qtd_pode_converter_t5_sim}")

    print("\nresumo_precedencia_intradiaria_t7=")
    print(resumo.to_string(index=False))

    print(f"csv_auditoria_t7={CSV_T7}")
    print(f"csv_resumo_t7={CSV_RESUMO_T7}")

    status = "auditoria_precedencia_intradiaria_recebidos_gerada"
    if qtd_pagamentos_same_day != 5:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"
    if qtd_pode_promover_sim != 0:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"
    if qtd_pode_converter_t5_sim != 0:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"
    if qtd_candidato != 0:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"
    if qtd_classe_desconhecida != 0:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"
    if qtd_inconsistencia_taxonomica != 0:
        status = "falha_auditoria_precedencia_intradiaria_recebidos"

    print(f"status_geral_t7={status}")
    return 0 if status == "auditoria_precedencia_intradiaria_recebidos_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

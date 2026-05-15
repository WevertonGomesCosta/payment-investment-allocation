from __future__ import annotations

from pathlib import Path
import unicodedata

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]

CSV_T4 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv"
)

CSV_T5 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv"
)

CSV_RESUMO_T5 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "resumo_auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv"
)

CSV_REGRAS_T5 = (
    RAIZ
    / "saidas"
    / "diagnostico"
    / "matriz_regras_operacionais_uso_recebidos_v17_f0_t5.csv"
)


COLUNAS_T4_OBRIGATORIAS = [
    "data",
    "conta",
    "valor",
    "grupo_pagamento_t4",
    "status_operacional_oficial",
    "lote_recomendado_oficial",
    "ordem_competicao_t4",
    "prioridade_intradata_t4",
    "saldo_pool_recebidos_antes_t4",
    "valor_alocado_recebidos_t4",
    "valor_deficit_pos_alocacao_t4",
    "saldo_pool_recebidos_depois_t4",
    "usa_recebido_mesma_data_pagamento_t4",
    "status_competicao_recebidos_t4",
    "nivel_evidencia_t4",
]


COLUNAS_SAIDA = [
    "data",
    "conta",
    "valor",
    "grupo_pagamento_t4",
    "status_operacional_oficial",
    "lote_recomendado_oficial",
    "status_competicao_recebidos_t4",
    "valor_alocado_recebidos_t4",
    "valor_deficit_pos_alocacao_t4",
    "usa_recebido_mesma_data_pagamento_t4",
    "status_regra_operacional_t5",
    "pode_converter_recebido_em_fonte_oficial_t5",
    "regra_bloqueante_principal_t5",
    "regras_pendentes_t5",
    "nivel_evidencia_t5",
    "classe_decisao_t5",
    "acao_recomendada_t6",
    "observacao_t5",
]


REGRAS_T5 = [
    {
        "codigo_regra_t5": "R0",
        "nome_regra_t5": "Preservar fonte oficial já recomendada por lote",
        "descricao_regra_t5": (
            "Pagamentos aprovados oficialmente com lote sugerido não devem ser convertidos "
            "para recebidos apenas porque a simulação contrafactual alocou recebidos."
        ),
        "bloqueante_para_promocao": "sim",
    },
    {
        "codigo_regra_t5": "R1",
        "nome_regra_t5": "Definir precedência intradiária de recebidos",
        "descricao_regra_t5": (
            "Recebido na mesma data do pagamento só pode ser usado oficialmente se houver "
            "regra explícita de precedência intradiária e materialização antes do pagamento."
        ),
        "bloqueante_para_promocao": "sim",
    },
    {
        "codigo_regra_t5": "R2",
        "nome_regra_t5": "Exigir suficiência temporal competitiva",
        "descricao_regra_t5": (
            "Recebidos só podem ser fonte oficial se o pagamento estiver integralmente coberto "
            "no cenário competitivo, considerando pagamentos anteriores e prioridades do dia."
        ),
        "bloqueante_para_promocao": "sim",
    },
    {
        "codigo_regra_t5": "R3",
        "nome_regra_t5": "Separar fonte diagnóstica de fonte oficial",
        "descricao_regra_t5": (
            "Cobertura diagnóstica por recebidos não altera status_operacional, lote_recomendado, "
            "XLSX oficial ou recomendador."
        ),
        "bloqueante_para_promocao": "sim",
    },
    {
        "codigo_regra_t5": "R4",
        "nome_regra_t5": "Criar ledger oficial de recebidos antes de promoção",
        "descricao_regra_t5": (
            "Antes de usar recebidos como fonte oficial, é necessário ledger temporal auditável "
            "com entrada, consumo, saldo remanescente e concorrência por data."
        ),
        "bloqueante_para_promocao": "sim",
    },
    {
        "codigo_regra_t5": "R5",
        "nome_regra_t5": "Definir prioridade entre lotes, recebidos e aportes",
        "descricao_regra_t5": (
            "A escolha entre lote, recebido e eventual aporte planejado precisa ser decidida "
            "pelo objetivo econômico conjunto, não por disponibilidade isolada."
        ),
        "bloqueante_para_promocao": "sim",
    },
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


def _carregar_t4() -> pd.DataFrame | None:
    if not CSV_T4.exists():
        print("csv_t4_existe=nao")
        print(f"csv_t4_esperado={CSV_T4}")
        return None

    print("csv_t4_existe=sim")
    print("fonte_competicao_t4=csv_t4")
    print(f"caminho_competicao_t4={CSV_T4}")
    return pd.read_csv(CSV_T4)


def _classificar_linha(row: pd.Series) -> dict[str, str]:
    grupo = str(row.get("grupo_pagamento_t4", ""))
    status_competicao = str(row.get("status_competicao_recebidos_t4", ""))
    usa_mesma_data = _normalizar_texto(row.get("usa_recebido_mesma_data_pagamento_t4", "")) == "sim"
    deficit = _to_num(row.get("valor_deficit_pos_alocacao_t4", 0.0))

    if grupo == "aprovado_oficial_com_lote":
        return {
            "status_regra_operacional_t5": "manter_fonte_oficial_por_lote",
            "pode_converter_recebido_em_fonte_oficial_t5": "nao",
            "regra_bloqueante_principal_t5": "R0_preservar_fonte_oficial_por_lote",
            "regras_pendentes_t5": "R0;R3;R5",
            "nivel_evidencia_t5": "explicita",
            "classe_decisao_t5": "fonte_oficial_ja_definida",
            "acao_recomendada_t6": "manter_pagamento_fora_da_promocao_por_recebido",
            "observacao_t5": (
                "Pagamento já aprovado oficialmente por lote. A alocação por recebidos em T4 é apenas "
                "contrafactual e não deve trocar a fonte oficial."
            ),
        }

    if deficit > 0.01:
        regras = ["R2", "R3", "R4", "R5"]
        if usa_mesma_data:
            regras.insert(0, "R1")

        return {
            "status_regra_operacional_t5": "bloqueado_por_insuficiencia_temporal_competitiva",
            "pode_converter_recebido_em_fonte_oficial_t5": "nao",
            "regra_bloqueante_principal_t5": "R2_exigir_suficiencia_temporal_competitiva",
            "regras_pendentes_t5": ";".join(regras),
            "nivel_evidencia_t5": "explicita",
            "classe_decisao_t5": "bloqueio_competitivo",
            "acao_recomendada_t6": "nao_promover_para_fonte_recebido_sem_novo_motor_temporal",
            "observacao_t5": (
                "Pagamento sem lote não ficou integralmente coberto em T4 quando os 49 aprovados entraram "
                "na competição contrafactual pelo pool de recebidos."
            ),
        }

    if "coberto_integralmente" not in status_competicao:
        return {
            "status_regra_operacional_t5": "bloqueado_por_status_competitivo_nao_integral",
            "pode_converter_recebido_em_fonte_oficial_t5": "nao",
            "regra_bloqueante_principal_t5": "R2_exigir_cobertura_integral_no_cenario_competitivo",
            "regras_pendentes_t5": "R2;R3;R4;R5",
            "nivel_evidencia_t5": "explicita",
            "classe_decisao_t5": "bloqueio_competitivo",
            "acao_recomendada_t6": "nao_promover_para_fonte_recebido_sem_cobertura_integral",
            "observacao_t5": (
                "Pagamento sem lote não possui status competitivo integral em T4."
            ),
        }

    if usa_mesma_data:
        return {
            "status_regra_operacional_t5": "bloqueado_ate_definir_precedencia_intradiaria",
            "pode_converter_recebido_em_fonte_oficial_t5": "nao",
            "regra_bloqueante_principal_t5": "R1_definir_precedencia_intradiaria_de_recebidos",
            "regras_pendentes_t5": "R1;R3;R4;R5",
            "nivel_evidencia_t5": "explicita",
            "classe_decisao_t5": "bloqueio_intradiario",
            "acao_recomendada_t6": "auditar_precedencia_intradiaria_antes_de_promover",
            "observacao_t5": (
                "Pagamento ficou coberto em T4, mas usa recebido na mesma data; falta regra explícita "
                "de materialização intradiária."
            ),
        }

    return {
        "status_regra_operacional_t5": "candidato_diagnostico_resistente_sem_promocao",
        "pode_converter_recebido_em_fonte_oficial_t5": "nao_sem_motor_oficial_de_recebidos",
        "regra_bloqueante_principal_t5": "R4_criar_ledger_oficial_de_recebidos",
        "regras_pendentes_t5": "R3;R4;R5",
        "nivel_evidencia_t5": "inferida_moderada",
        "classe_decisao_t5": "candidato_diagnostico",
        "acao_recomendada_t6": "planejar_motor_oficial_de_recebidos_sem_alterar_recomendador",
        "observacao_t5": (
            "Pagamento sem lote resistiu à competição temporal em T4 sem usar recebido na mesma data. "
            "Ainda assim, permanece apenas candidato diagnóstico, pois falta ledger e regra oficial de prioridade."
        ),
    }


def main() -> int:
    df_t4 = _carregar_t4()
    if df_t4 is None:
        print("status_geral_t5=falha_auditoria_regras_operacionais_uso_recebidos")
        return 1

    print(f"qtd_linhas_t4={len(df_t4)}")

    faltantes = [c for c in COLUNAS_T4_OBRIGATORIAS if c not in df_t4.columns]
    print(f"qtd_colunas_t4_obrigatorias_ausentes={len(faltantes)}")
    print("colunas_t4_obrigatorias_ausentes=" + ("nenhuma" if not faltantes else ",".join(faltantes)))

    if faltantes:
        print("status_geral_t5=falha_auditoria_regras_operacionais_uso_recebidos")
        return 1

    linhas = []
    for _, row in df_t4.iterrows():
        item = row.to_dict()
        item.update(_classificar_linha(row))
        linhas.append(item)

    saida = pd.DataFrame(linhas)

    for col in COLUNAS_SAIDA:
        if col not in saida.columns:
            saida[col] = ""

    saida_final = saida[COLUNAS_SAIDA].copy()

    CSV_T5.parent.mkdir(parents=True, exist_ok=True)
    saida_final.to_csv(CSV_T5, index=False, encoding="utf-8-sig")

    regras = pd.DataFrame(REGRAS_T5)
    regras.to_csv(CSV_REGRAS_T5, index=False, encoding="utf-8-sig")

    resumo = (
        saida_final
        .groupby(
            [
                "grupo_pagamento_t4",
                "classe_decisao_t5",
                "status_regra_operacional_t5",
                "regra_bloqueante_principal_t5",
                "nivel_evidencia_t5",
            ],
            dropna=False,
        )
        .agg(
            qtd_pagamentos=("valor", "size"),
            valor_total=("valor", lambda s: round(sum(_to_num(x) for x in s), 2)),
            valor_deficit_t4=("valor_deficit_pos_alocacao_t4", lambda s: round(sum(_to_num(x) for x in s), 2)),
        )
        .reset_index()
        .sort_values(["grupo_pagamento_t4", "classe_decisao_t5", "status_regra_operacional_t5"])
    )
    resumo.to_csv(CSV_RESUMO_T5, index=False, encoding="utf-8-sig")

    qtd_total = int(len(saida_final))
    qtd_aprovados = int(saida_final["grupo_pagamento_t4"].eq("aprovado_oficial_com_lote").sum())
    qtd_sem_lote = int(saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3").sum())

    qtd_mantidos_lote = int(saida_final["classe_decisao_t5"].eq("fonte_oficial_ja_definida").sum())
    qtd_bloqueio_competitivo = int(saida_final["classe_decisao_t5"].eq("bloqueio_competitivo").sum())
    qtd_bloqueio_intradiario = int(saida_final["classe_decisao_t5"].eq("bloqueio_intradiario").sum())
    qtd_candidato = int(saida_final["classe_decisao_t5"].eq("candidato_diagnostico").sum())

    qtd_pode_converter_sim = int(saida_final["pode_converter_recebido_em_fonte_oficial_t5"].eq("sim").sum())
    qtd_pode_converter_nao = int(
        saida_final["pode_converter_recebido_em_fonte_oficial_t5"]
        .astype(str)
        .str.startswith("nao")
        .sum()
    )

    sem_lote_mask = saida_final["grupo_pagamento_t4"].eq("sem_lote_testado_t3")
    qtd_sem_lote_candidato = int((sem_lote_mask & saida_final["classe_decisao_t5"].eq("candidato_diagnostico")).sum())
    qtd_sem_lote_bloqueado = int((sem_lote_mask & ~saida_final["classe_decisao_t5"].eq("candidato_diagnostico")).sum())

    qtd_mesma_data = int(saida_final["usa_recebido_mesma_data_pagamento_t4"].astype(str).str.casefold().eq("sim").sum())
    qtd_regras_formalizadas = int(len(regras))

    valor_candidato = float(
        saida_final.loc[saida_final["classe_decisao_t5"].eq("candidato_diagnostico"), "valor"].map(_to_num).sum()
    )
    valor_bloqueio_competitivo = float(
        saida_final.loc[saida_final["classe_decisao_t5"].eq("bloqueio_competitivo"), "valor"].map(_to_num).sum()
    )

    print(f"qtd_linhas_auditoria_t5={qtd_total}")
    print(f"qtd_pagamentos_aprovados_t5={qtd_aprovados}")
    print(f"qtd_pagamentos_sem_lote_t5={qtd_sem_lote}")
    print(f"qtd_mantidos_com_fonte_oficial_lote_t5={qtd_mantidos_lote}")
    print(f"qtd_bloqueados_por_competicao_t5={qtd_bloqueio_competitivo}")
    print(f"qtd_bloqueados_por_intradiario_t5={qtd_bloqueio_intradiario}")
    print(f"qtd_candidatos_diagnosticos_resistentes_t5={qtd_candidato}")
    print(f"qtd_sem_lote_candidatos_diagnosticos_t5={qtd_sem_lote_candidato}")
    print(f"qtd_sem_lote_bloqueados_t5={qtd_sem_lote_bloqueado}")
    print(f"qtd_pode_converter_recebido_em_fonte_oficial_sim_t5={qtd_pode_converter_sim}")
    print(f"qtd_pode_converter_recebido_em_fonte_oficial_nao_t5={qtd_pode_converter_nao}")
    print(f"qtd_pagamentos_usando_recebido_mesma_data_t5={qtd_mesma_data}")
    print(f"qtd_regras_operacionais_formalizadas_t5={qtd_regras_formalizadas}")
    print(f"valor_candidatos_diagnosticos_t5={round(valor_candidato, 2)}")
    print(f"valor_bloqueio_competitivo_t5={round(valor_bloqueio_competitivo, 2)}")

    print("\nresumo_regras_operacionais_t5=")
    print(resumo.to_string(index=False))

    def _sentinela(data: str, conta: str) -> str:
        mask = (
            saida_final["data"].astype(str).str[:10].eq(data)
            & saida_final["conta"].astype(str).str.casefold().eq(conta.casefold())
        )
        return "sim" if bool(mask.any()) else "nao"

    print(f"sentinela_t5_internet_2026_05_15_presente={_sentinela('2026-05-15', 'Internet')}")
    print(f"sentinela_t5_cartao_azul_2026_05_20_presente={_sentinela('2026-05-20', 'Cartão Azul')}")
    print(f"sentinela_t5_aluguel_2026_06_12_presente={_sentinela('2026-06-12', 'Aluguel')}")
    print(f"sentinela_t5_condominio_2026_06_20_presente={_sentinela('2026-06-20', 'Condomínio')}")

    print(f"csv_auditoria_t5={CSV_T5}")
    print(f"csv_resumo_t5={CSV_RESUMO_T5}")
    print(f"csv_regras_t5={CSV_REGRAS_T5}")

    status = "auditoria_regras_operacionais_uso_recebidos_gerada"
    if qtd_total != 159:
        status = "falha_auditoria_regras_operacionais_uso_recebidos"
    if qtd_aprovados != 49:
        status = "falha_auditoria_regras_operacionais_uso_recebidos"
    if qtd_sem_lote != 110:
        status = "falha_auditoria_regras_operacionais_uso_recebidos"
    if qtd_pode_converter_sim != 0:
        status = "falha_auditoria_regras_operacionais_uso_recebidos"
    if qtd_regras_formalizadas < 6:
        status = "falha_auditoria_regras_operacionais_uso_recebidos"

    print(f"status_geral_t5={status}")
    return 0 if status == "auditoria_regras_operacionais_uso_recebidos_gerada" else 1


if __name__ == "__main__":
    raise SystemExit(main())

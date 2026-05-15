from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DIR_DIAG = BASE_DIR / "saidas/diagnostico"

ARQ_U4_XLSX = DIR_DIAG / "saida_operacional_pagamentos_v17_f0_u4.xlsx"

ARQ_U5_RESUMO = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_resumo.csv"
ARQ_U5_ABAS = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_abas.csv"
ARQ_U5_DIVERGENCIAS = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_divergencias.csv"
ARQ_U5_CHAVES = DIR_DIAG / "auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_chaves.csv"
ARQ_LOG_U5 = BASE_DIR / "logs/iteracoes/ME-V17-F0-U5_AUDITORIA_CONSISTENCIA_EXPORTACAO_AUXILIAR_U4.md"

ARQ_RESUMO_U6 = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_resumo.csv"
ARQ_ABAS_U6 = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_abas.csv"
ARQ_CAMPOS_U6 = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_campos.csv"
ARQ_GATES_U6 = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_gates.csv"
ARQ_BLOQUEIOS_U6 = DIR_DIAG / "governanca_promocao_saida_auxiliar_v17_f0_u6_bloqueios.csv"

ARQ_LOG = BASE_DIR / "logs/iteracoes/ME-V17-F0-U6_GOVERNANCA_PROMOCAO_SAIDA_AUXILIAR.md"

STATUS_GERAL = "governanca_promocao_saida_auxiliar_v17_f0_u6_gerada"
RECOMENDACAO = "promover_apenas_apos_gates"

ABAS_ESPERADAS = [
    "Resumo_U4",
    "Pagamentos",
    "Linhas_Operacionais",
    "Multifonte",
    "Pendencias",
    "Metadados",
]


def carregar_csv(path: Path, nome: str, instrucao: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo obrigatório ausente para U.6 ({nome}): {path}\n{instrucao}")
    return pd.read_csv(path)


def carregar_xlsx(path: Path) -> dict[str, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(
            f"XLSX U.4 ausente para U.6: {path}\n"
            "Execute antes: python -B scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py"
        )

    xls = pd.ExcelFile(path)
    faltantes = [aba for aba in ABAS_ESPERADAS if aba not in xls.sheet_names]
    if faltantes:
        raise ValueError(f"Abas obrigatórias ausentes no XLSX U.4: {faltantes}")

    return {aba: pd.read_excel(path, sheet_name=aba) for aba in ABAS_ESPERADAS}


def valor_resumo(resumo: pd.DataFrame, metrica: str, default: Any = None) -> Any:
    if "metrica" not in resumo.columns or "valor" not in resumo.columns:
        return default
    filtro = resumo.loc[resumo["metrica"].astype(str) == metrica, "valor"]
    if filtro.empty:
        return default
    return filtro.iloc[0]


def confirmar_u5_sem_divergencias(resumo: pd.DataFrame, divergencias: pd.DataFrame) -> bool:
    total = str(valor_resumo(resumo, "qtd_divergencias_total", "")).strip()
    status = str(valor_resumo(resumo, "status_geral_u5", "")).strip()
    return total in {"0", "0.0"} and "sem_divergencias" in status and len(divergencias) == 0


def classificar_aba(aba: str, df: pd.DataFrame) -> dict[str, Any]:
    regras = {
        "Resumo_U4": {
            "classificacao_governanca": "promovivel_como_auxiliar",
            "uso_futuro_permitido": "referencia_diagnostica_sumario",
            "risco_promocao": "substituir_resumo_oficial_sem_gate",
            "precondicao": "u5_sem_divergencias_e_metadados_preservados",
            "proibicao": "nao_substituir_resumo_oficial_sem_etapa_propria",
        },
        "Pagamentos": {
            "classificacao_governanca": "promovivel_com_gate",
            "uso_futuro_permitido": "aba_auxiliar_operacional_controlada",
            "risco_promocao": "converter_pendencias_em_recomendacoes_executaveis",
            "precondicao": "preservar_159_pagamentos_e_bloqueios_explicitos",
            "proibicao": "nao_transformar_pendencias_em_recomendacoes",
        },
        "Linhas_Operacionais": {
            "classificacao_governanca": "promovivel_com_gate",
            "uso_futuro_permitido": "aba_auxiliar_detalhada_fonte_a_fonte",
            "risco_promocao": "dupla_contagem_multifonte_ou_uso_de_saldo_nao_oficial",
            "precondicao": "preservar_175_linhas_e_gate_de_saldo",
            "proibicao": "nao_usar_saldos_como_oficiais_sem_auditoria_propria",
        },
        "Multifonte": {
            "classificacao_governanca": "promovivel_com_gate",
            "uso_futuro_permitido": "aba_auxiliar_detalhada_multifonte",
            "risco_promocao": "alterar_recomendador_ou_somar_resgates_em_duplicidade",
            "precondicao": "preservar_32_linhas_16_pagamentos_e_somas_por_pagamento",
            "proibicao": "nao_alterar_recomendador_sem_microetapa_propria",
        },
        "Pendencias": {
            "classificacao_governanca": "manter_diagnostico",
            "uso_futuro_permitido": "aba_auxiliar_de_bloqueios",
            "risco_promocao": "promover_fifo_ou_pendencias_como_recomendacao",
            "precondicao": "preservar_110_pendencias_e_109_fifo_diagnosticos",
            "proibicao": "nao_promover_fifo_e_nao_converter_bloqueio_em_recomendacao",
        },
        "Metadados": {
            "classificacao_governanca": "promovivel_como_auxiliar",
            "uso_futuro_permitido": "aba_auxiliar_obrigatoria_de_rastreabilidade",
            "risco_promocao": "perder_baseline_fontes_restricoes_ou_status",
            "precondicao": "preservar_baseline_fontes_restricoes_data_e_status",
            "proibicao": "nao_gerar_saida_oficial_sem_metadados",
        },
    }

    r = regras[aba]
    return {
        "aba": aba,
        "qtd_linhas": len(df),
        "qtd_campos": len(df.columns),
        **r,
        "promocao_permitida_agora": "nao",
        "promocao_futura": "somente_com_gates",
    }


def classificar_campo(aba: str, campo: str) -> dict[str, Any]:
    c = campo.lower()

    campos_chave = {
        "chave_pagamento", "pagamento_idx", "data", "conta",
        "fonte", "tipo_fonte", "ordem_fonte_no_pagamento",
        "metrica", "campo",
    }

    if campo in campos_chave:
        classificacao = "promovivel_como_auxiliar"
        justificativa = "Campo de chave, identificação ou estrutura auxiliar."
        precondicao = "preservar_chaves_e_shapes"
        risco = "baixo"

    elif "saldo" in c:
        classificacao = "exige_precondicao"
        justificativa = "Campo de saldo não deve ser tratado como saldo oficial sem auditoria contra saldo líquido real por fonte."
        precondicao = "auditoria_especifica_de_saldo_liquido_real"
        risco = "alto"

    elif any(t in c for t in ["valor", "resgate", "soma", "diferenca", "maior"]):
        classificacao = "promovivel_com_gate"
        justificativa = "Campo monetário; exige tolerância <= 0.01 e ausência de divergências U.5."
        precondicao = "u5_sem_divergencias_e_tolerancia_0_01"
        risco = "medio"

    elif any(t in c for t in ["tipo_pagamento", "origem_linha", "classe", "cobertura", "motivo_bloqueio", "status_operacional"]):
        classificacao = "promovivel_com_gate"
        justificativa = "Campo de classe operacional; deve preservar caráter diagnóstico quando aplicável."
        precondicao = "classes_preservadas_e_sem_promocao_de_pendencias"
        risco = "medio"

    elif campo in {"candidato_fifo_detectado", "pendencia_sem_lote_sugerido"}:
        classificacao = "manter_diagnostico"
        justificativa = "Campo relacionado a FIFO ou pendência; não pode promover candidato diagnóstico como fonte oficial."
        precondicao = "manter_fifo_e_pendencias_como_diagnostico"
        risco = "alto"

    elif any(t in c for t in ["executavel", "bloqueio", "nao_auditavel", "fonte_aprovada"]):
        classificacao = "promovivel_com_gate"
        justificativa = "Flag operacional; pode ir como auxiliar desde que não altere recomendação oficial."
        precondicao = "preservar_flags_e_bloqueios"
        risco = "medio"

    elif "observacao" in c:
        classificacao = "manter_diagnostico"
        justificativa = "Campo textual interpretativo; deve permanecer como observação diagnóstica."
        precondicao = "nao_usar_como_regra_de_decisao"
        risco = "medio"

    elif aba == "Metadados":
        classificacao = "promovivel_como_auxiliar"
        justificativa = "Campo de rastreabilidade da saída auxiliar."
        precondicao = "preservar_restricoes_baseline_fontes_e_status"
        risco = "baixo"

    else:
        classificacao = "manter_diagnostico"
        justificativa = "Campo sem regra de promoção automática definida; manter diagnóstico por governança conservadora."
        precondicao = "avaliacao_em_etapa_propria_antes_de_promocao"
        risco = "medio"

    bloqueio_promocao_automatica = "sim" if classificacao in {"manter_diagnostico", "bloqueado_para_promocao", "exige_precondicao"} else "nao"

    return {
        "aba": aba,
        "campo": campo,
        "classificacao_governanca": classificacao,
        "risco_promocao": risco,
        "precondicao": precondicao,
        "bloqueio_promocao_automatica": bloqueio_promocao_automatica,
        "justificativa": justificativa,
    }


def montar_gates() -> pd.DataFrame:
    gates = [
        ("gate_u5_sem_divergencias", "qtd_divergencias_total = 0", "bloqueante", "U.5 deve permanecer sem divergências de chaves, shapes, valores, classes, flags, resumo e metadados."),
        ("gate_shape_pagamentos", "Pagamentos = 159", "bloqueante", "Aba Pagamentos deve preservar uma linha por pagamento único."),
        ("gate_shape_linhas", "Linhas_Operacionais = 175", "bloqueante", "Aba Linhas_Operacionais deve preservar granularidade fonte-a-fonte."),
        ("gate_shape_multifonte", "Multifonte = 32 linhas e 16 pagamentos", "bloqueante", "Aba Multifonte deve preservar decomposição U.2/U.3."),
        ("gate_shape_pendencias", "Pendencias = 110", "bloqueante", "Pendências devem permanecer separadas de recomendações executáveis."),
        ("gate_multifonte_soma", "soma_resgates_por_pagamento = valor_pagamento com tolerancia <= 0.01", "bloqueante", "Evitar cobertura parcial e dupla contagem."),
        ("gate_fifo", "109 FIFO continuam diagnosticos", "bloqueante", "Nenhum candidato FIFO pode ser promovido automaticamente."),
        ("gate_saldo", "saldo oficial apenas com auditoria contra saldo liquido real", "bloqueante", "Campos de saldo permanecem diagnósticos ou exigem pré-condição."),
        ("gate_metadados", "baseline, fontes, status, restricoes e data preservados", "bloqueante", "Qualquer integração futura deve manter rastreabilidade."),
        ("gate_nao_regressao", "motor/recomendador/exportador_oficial/contrato/modelo inalterados", "bloqueante", "Etapa de governança não pode alterar decisão econômica."),
    ]

    return pd.DataFrame(gates, columns=["gate", "condicao", "tipo", "justificativa"])


def montar_bloqueios() -> pd.DataFrame:
    bloqueios = [
        ("fifo_diagnostico", "109 candidatos FIFO", "bloqueado_para_promocao_automatica", "FIFO permanece diagnóstico; não pode virar fonte oficial sem etapa própria."),
        ("pendencias", "110 pagamentos bloqueados/pendentes", "bloqueado_para_recomendacao", "Pendências não podem ser convertidas em recomendações executáveis."),
        ("saldo_fonte_considerado", "campos de saldo", "exige_precondicao", "Saldo só pode ser oficial após auditoria contra saldo líquido real por fonte."),
        ("saldo_remanescente_diagnostico", "campos de saldo", "exige_precondicao", "Saldo remanescente diagnóstico não substitui saldo oficial."),
        ("multifonte_recomendador", "aba Multifonte", "bloqueado_para_alterar_recomendador", "A aba multifonte não pode alterar recomendador sem microetapa própria."),
        ("resumo_u4", "Resumo_U4", "nao_substitui_resumo_oficial", "Resumo U.4 não substitui resumo oficial sem gate e etapa específica."),
        ("metadados", "Metadados", "obrigatorio_para_promocao_futura", "Integração futura deve preservar baseline, fontes, restrições e status."),
        ("integracao_oficial", "XLSX oficial", "bloqueado_na_u6", "U.6 não pode integrar ao XLSX oficial."),
    ]

    return pd.DataFrame(bloqueios, columns=["bloqueio", "escopo", "classificacao", "justificativa"])


def main() -> int:
    DIR_DIAG.mkdir(parents=True, exist_ok=True)
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)

    instr_u5 = "Execute antes: python -B scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py"

    abas = carregar_xlsx(ARQ_U4_XLSX)
    u5_resumo = carregar_csv(ARQ_U5_RESUMO, "U5 resumo", instr_u5)
    u5_abas = carregar_csv(ARQ_U5_ABAS, "U5 abas", instr_u5)
    u5_divergencias = carregar_csv(ARQ_U5_DIVERGENCIAS, "U5 divergencias", instr_u5)
    u5_chaves = carregar_csv(ARQ_U5_CHAVES, "U5 chaves", instr_u5)

    if not ARQ_LOG_U5.exists():
        raise FileNotFoundError(f"Log U.5 versionado ausente: {ARQ_LOG_U5}")

    u5_sem_divergencias = confirmar_u5_sem_divergencias(u5_resumo, u5_divergencias)

    linhas_abas = [classificar_aba(aba, abas[aba]) for aba in ABAS_ESPERADAS]
    abas_df = pd.DataFrame(linhas_abas)

    linhas_campos = []
    for aba in ABAS_ESPERADAS:
        for campo in abas[aba].columns:
            linhas_campos.append(classificar_campo(aba, str(campo)))
    campos_df = pd.DataFrame(linhas_campos)

    gates_df = montar_gates()
    bloqueios_df = montar_bloqueios()

    qtd_abas_avaliadas = int(len(abas_df))
    qtd_campos_avaliados = int(len(campos_df))

    resumo = {
        "qtd_abas_avaliadas_u6": qtd_abas_avaliadas,
        "qtd_campos_avaliados_u6": qtd_campos_avaliados,
        "qtd_abas_promoviveis_como_auxiliar": int((abas_df["classificacao_governanca"] == "promovivel_como_auxiliar").sum()),
        "qtd_abas_promoviveis_com_gate": int((abas_df["classificacao_governanca"] == "promovivel_com_gate").sum()),
        "qtd_abas_manter_diagnostico": int((abas_df["classificacao_governanca"] == "manter_diagnostico").sum()),
        "qtd_abas_bloqueadas_para_promocao": int((abas_df["classificacao_governanca"] == "bloqueado_para_promocao").sum()),
        "qtd_campos_promoviveis_como_auxiliar": int((campos_df["classificacao_governanca"] == "promovivel_como_auxiliar").sum()),
        "qtd_campos_promoviveis_com_gate": int((campos_df["classificacao_governanca"] == "promovivel_com_gate").sum()),
        "qtd_campos_manter_diagnostico": int((campos_df["classificacao_governanca"] == "manter_diagnostico").sum()),
        "qtd_campos_bloqueados_para_promocao": int((campos_df["classificacao_governanca"] == "bloqueado_para_promocao").sum()),
        "qtd_campos_exigem_precondicao": int((campos_df["classificacao_governanca"] == "exige_precondicao").sum()),
        "qtd_gates_futura_u7": int(len(gates_df)),
        "qtd_bloqueios_precondicoes": int(len(bloqueios_df)),
        "u5_sem_divergencias_confirmado": "sim" if u5_sem_divergencias else "nao",
        "recomendacao_promocao_u6": RECOMENDACAO,
        "status_geral_u6": STATUS_GERAL,
    }

    if not u5_sem_divergencias:
        resumo["recomendacao_promocao_u6"] = "nao_promover_ainda"

    resumo_df = pd.DataFrame([{"metrica": k, "valor": v} for k, v in resumo.items()])

    resumo_df.to_csv(ARQ_RESUMO_U6, index=False)
    abas_df.to_csv(ARQ_ABAS_U6, index=False)
    campos_df.to_csv(ARQ_CAMPOS_U6, index=False)
    gates_df.to_csv(ARQ_GATES_U6, index=False)
    bloqueios_df.to_csv(ARQ_BLOQUEIOS_U6, index=False)

    linhas_resumo = "\n".join(f"- `{k}`: `{v}`" for k, v in resumo.items())
    linhas_abas_log = "\n".join(
        f"- `{r['aba']}`: classificacao=`{r['classificacao_governanca']}`, linhas=`{r['qtd_linhas']}`, campos=`{r['qtd_campos']}`"
        for _, r in abas_df.iterrows()
    )
    linhas_gates_log = "\n".join(
        f"- `{r['gate']}`: `{r['condicao']}`"
        for _, r in gates_df.iterrows()
    )
    linhas_bloqueios_log = "\n".join(
        f"- `{r['bloqueio']}`: classificacao=`{r['classificacao']}`"
        for _, r in bloqueios_df.iterrows()
    )

    data_exec = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"""# ME-V17-F0-U6 — Governança de promoção da saída auxiliar U.4/U.5

- MICROETAPA: V17-F0-U.6
- CLASSE: DIAGNÓSTICO / DOCUMENTAL / GOVERNANÇA
- DATA_EXECUCAO_LOCAL: {data_exec}
- BASELINE: main pós-merge da PR #335
- MICROETAPA_ANTERIOR: V17-F0-U.5
- STATUS_GERAL_U6: `{STATUS_GERAL}`

## Objetivo

Definir a governança para eventual promoção futura da saída auxiliar U.4/U.5 para integração oficial controlada, sem implementar a integração.

A U.6 classifica abas, campos, gates, bloqueios e pré-condições. A U.6 não altera recomendador oficial, motor econômico, exportador oficial, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `{ARQ_U4_XLSX.relative_to(BASE_DIR)}`
- `{ARQ_U5_RESUMO.relative_to(BASE_DIR)}`
- `{ARQ_U5_ABAS.relative_to(BASE_DIR)}`
- `{ARQ_U5_DIVERGENCIAS.relative_to(BASE_DIR)}`
- `{ARQ_U5_CHAVES.relative_to(BASE_DIR)}`
- `{ARQ_LOG_U5.relative_to(BASE_DIR)}`

## Artefatos diagnósticos locais gerados

- `{ARQ_RESUMO_U6.relative_to(BASE_DIR)}`
- `{ARQ_ABAS_U6.relative_to(BASE_DIR)}`
- `{ARQ_CAMPOS_U6.relative_to(BASE_DIR)}`
- `{ARQ_GATES_U6.relative_to(BASE_DIR)}`
- `{ARQ_BLOQUEIOS_U6.relative_to(BASE_DIR)}`

## Contadores principais

{linhas_resumo}

## Governança por aba

{linhas_abas_log}

## Gates obrigatórios para futura U.7

{linhas_gates_log}

## Bloqueios e pré-condições

{linhas_bloqueios_log}

## Interpretação

A U.6 confirma que a saída auxiliar U.4/U.5 pode ser considerada candidata a promoção futura apenas de forma controlada e condicionada a gates. A recomendação desta microetapa é `{resumo['recomendacao_promocao_u6']}`.

A U.6 não promove a saída auxiliar ao XLSX oficial. A integração oficial, se aprovada, deve ser tratada em uma U.7 separada.

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
- Campos de saldo exigem pré-condição antes de qualquer uso oficial.
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

    print("=== U6 GERADA ===")
    for k, v in resumo.items():
        print(f"{k}: {v}")

    print("\nGovernanca por aba:")
    print(abas_df.to_string(index=False))

    print("\nCSVs:")
    print(ARQ_RESUMO_U6.relative_to(BASE_DIR))
    print(ARQ_ABAS_U6.relative_to(BASE_DIR))
    print(ARQ_CAMPOS_U6.relative_to(BASE_DIR))
    print(ARQ_GATES_U6.relative_to(BASE_DIR))
    print(ARQ_BLOQUEIOS_U6.relative_to(BASE_DIR))

    print("\nLog:")
    print(ARQ_LOG.relative_to(BASE_DIR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

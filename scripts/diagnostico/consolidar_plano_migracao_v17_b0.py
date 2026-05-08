from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

ARQ_SAIDA_CANONICA = RAIZ / "nucleo" / "saida_canonica.py"
IN_DIR_A4 = RAIZ / "saidas" / "diagnostico" / "v17_a4"
ARQ_IN_PONTOS_A4 = IN_DIR_A4 / "v17_a4_pontos_suspeitos_saida_canonica.csv"
ARQ_IN_PRIORIDADE_A4 = IN_DIR_A4 / "v17_a4_priorizacao_migracao_saida_canonica.csv"

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_b0"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_OUT_PONTOS = OUT_DIR / "v17_b0_pontos_p0_p1_por_funcao.csv"
ARQ_OUT_FUNCOES = OUT_DIR / "v17_b0_funcoes_blocos_responsaveis.csv"
ARQ_OUT_PLANO = OUT_DIR / "v17_b0_plano_migracao_minima.csv"
ARQ_OUT_GUARDRAILS = OUT_DIR / "v17_b0_guardrails_migracao_minima.csv"
ARQ_OUT_RESUMO = OUT_DIR / "v17_b0_resumo.csv"

CLASSES_ALVO = {
    "correcao_funcional_proibida",
    "migrar_para_estado_temporal",
    "inferencia_operacional_indevida",
}

PRIORIDADE_CLASSE = {
    "correcao_funcional_proibida": "P0",
    "migrar_para_estado_temporal": "P0",
    "inferencia_operacional_indevida": "P1",
}

ORDEM_PRIORIDADE = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

PADROES_BLOCO = [
    {
        "bloco_responsavel": "normalizacao_sem_fonte_valida_extrato_futuro",
        "regex": r"_normalizar_sem_fonte_valida|_linha_extrato_futuro_sem_saldo_temporal|sem_saldo_temporal|saldo_temporal_insuficiente",
        "familia_migracao": "estado_temporal_fonte_pagamento",
        "acao_minima": "mover limpeza/ocultacao de fonte invalida para estado temporal de pagamento sem saldo auditavel",
    },
    {
        "bloco_responsavel": "fallback_recebido_disponivel_fontes_elegiveis",
        "regex": r"fallback|recebido_disponivel|fontes_elegiveis|_mapa_fontes_elegiveis|_pagamentos_decisao_recebido",
        "familia_migracao": "adapter_temporal_fontes_v17",
        "acao_minima": "substituir fallback na saida por campo vindo de adapter/estado temporal ja decidido",
    },
    {
        "bloco_responsavel": "lotes_sinteticos_pos_switching",
        "regex": r"lotes_sinteticos_pos_switching|Novo lote|valor_total|Lotes origem|pos_switch|pós-switching|pos-switching",
        "familia_migracao": "estado_temporal_switching",
        "acao_minima": "materializar lote destino de switching antes da saida, com ID e valor auditaveis",
    },
    {
        "bloco_responsavel": "estado_pos_switching_lotes",
        "regex": r"estado_pos_switching|ativo_pos_switching|migrado_por_switching|Status novo|Status origem|Produto destino",
        "familia_migracao": "estado_temporal_switching",
        "acao_minima": "mover estado pos-switching para ledger/estado temporal canonico",
    },
    {
        "bloco_responsavel": "limpeza_lotes_migrados_intradia",
        "regex": r"_limpar_lotes_migrados|partes_validas|conflito_intradia|mapa_migrados|data_sw|novo_lote",
        "familia_migracao": "precedencia_intradiaria_estado_temporal",
        "acao_minima": "resolver exclusao de lote migrado e conflito intradia antes da camada de saida",
    },
    {
        "bloco_responsavel": "calculo_saldos_correntes_lotes",
        "regex": r"_mapa_saldos_correntes|valor_bruto_em_data|valor_liquido_em_data|valor_liquido_hoje|principal_remanescente|saldo_bruto|tabela_iof|faixas_ir",
        "familia_migracao": "estado_financeiro_lotes",
        "acao_minima": "usar saldos brutos/liquidos ja calculados pelo estado temporal; nao recalcular na saida",
    },
    {
        "bloco_responsavel": "avanco_lote_para_data",
        "regex": r"_avancar_lote_para_data|atualizar_juros|taxa_diaria|data_cursor|fator_dia|serie_cdi",
        "familia_migracao": "motor_rendimento_estado_temporal",
        "acao_minima": "mover capitalizacao/avanco de lote para nucleo economico ou estado temporal",
    },
    {
        "bloco_responsavel": "selecao_quadro_futuro_preferencial",
        "regex": r"_quadro_futuro_preferencial|motor_recomendacao|decisao_local_v1|quadro_recomendacoes|quadro_decisao_local_v1",
        "familia_migracao": "orquestracao_fonte_de_verdade",
        "acao_minima": "definir fonte de verdade antes da saida; saida nao deve escolher entre quadros funcionais",
    },
    {
        "bloco_responsavel": "outro_ponto_saida_canonica",
        "regex": r".*",
        "familia_migracao": "triagem_manual",
        "acao_minima": "revisar trecho e decidir se migra para estado temporal, orquestracao ou permanece como guardrail transitorio",
    },
]

SEQUENCIA_MIGRACAO = [
    {
        "ordem": 1,
        "microetapa_futura": "V17-B1",
        "familia_migracao": "orquestracao_fonte_de_verdade",
        "objetivo": "definir quadro/estado de entrada unico da saida sem que saida escolha entre motor e decisao_local",
        "escopo_permitido": "diagnostico/desenho de contrato interno da fonte de verdade",
        "escopo_proibido": "alterar motor, saida_canonica ou decisao economica",
        "criterio_saida": "todo ponto de selecao de quadro tem destino arquitetural antes da saida",
    },
    {
        "ordem": 2,
        "microetapa_futura": "V17-B2",
        "familia_migracao": "estado_temporal_switching",
        "objetivo": "migrar materializacao e estado pos-switching para estado temporal diagnostico",
        "escopo_permitido": "criar estrutura diagnostica de estado pos-switching sem consumo funcional",
        "escopo_proibido": "trocar switching funcional ou alterar recomendacoes",
        "criterio_saida": "lote destino, valor e status pos-switching deixam de ser construidos na saida",
    },
    {
        "ordem": 3,
        "microetapa_futura": "V17-B3",
        "familia_migracao": "precedencia_intradiaria_estado_temporal",
        "objetivo": "mover limpeza de lotes migrados e conflito intradia para estado temporal",
        "escopo_permitido": "diagnostico de precedencia e exclusao antes da renderizacao",
        "escopo_proibido": "remover fonte em saida_canonica como regra funcional",
        "criterio_saida": "saida apenas renderiza fontes ja filtradas pelo estado temporal",
    },
    {
        "ordem": 4,
        "microetapa_futura": "V17-B4",
        "familia_migracao": "estado_temporal_fonte_pagamento|adapter_temporal_fontes_v17",
        "objetivo": "substituir fallback de recebido_disponivel e limpeza de sem_saldo por estado/fonte V17 ja decidida",
        "escopo_permitido": "adapter diagnostico e matriz de equivalencia",
        "escopo_proibido": "saida escolher fonte ou completar recebido_disponivel",
        "criterio_saida": "fallback funcional deixa de ser necessario na saida",
    },
    {
        "ordem": 5,
        "microetapa_futura": "V17-B5",
        "familia_migracao": "estado_financeiro_lotes|motor_rendimento_estado_temporal",
        "objetivo": "remover recalculo financeiro da saida e usar valores auditaveis do estado temporal",
        "escopo_permitido": "diagnostico de equivalencia entre valores atuais da saida e estado temporal",
        "escopo_proibido": "alterar calculo de rendimento/imposto na saida",
        "criterio_saida": "saida nao chama valor_bruto_em_data, valor_liquido_em_data, atualizar_juros ou equivalentes",
    },
    {
        "ordem": 6,
        "microetapa_futura": "V17-C0",
        "familia_migracao": "ponte_para_primeira_integracao_funcional",
        "objetivo": "decidir se os P0/P1 foram migrados ou controlados para abrir integracao funcional minima",
        "escopo_permitido": "planejamento de integracao funcional controlada com rollback",
        "escopo_proibido": "abrir V17 funcional com P0/P1 ativos na saida",
        "criterio_saida": "P0 zerados e P1 justificados por guardrail ou migrados",
    },
]


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _ler_csv(caminho: Path, colunas: list[str]) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame(columns=colunas)
    try:
        df = pd.read_csv(caminho)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df


def _mapear_funcoes_saida() -> pd.DataFrame:
    if not ARQ_SAIDA_CANONICA.exists():
        return pd.DataFrame(columns=["linha_inicio", "linha_fim", "funcao_bloco", "tipo_bloco"])

    linhas = ARQ_SAIDA_CANONICA.read_text(encoding="utf-8").splitlines()
    blocos: list[dict[str, Any]] = []
    atual: dict[str, Any] | None = None

    padrao_def = re.compile(r"^(?P<indent>\s*)(def|class)\s+(?P<nome>[A-Za-z_][A-Za-z0-9_]*)")
    for idx, linha in enumerate(linhas, start=1):
        m = padrao_def.match(linha)
        if not m:
            continue
        indent = len(m.group("indent"))
        if indent > 4:
            continue
        if atual is not None:
            atual["linha_fim"] = idx - 1
            blocos.append(atual)
        tipo = "classe" if linha.lstrip().startswith("class ") else "funcao"
        atual = {
            "linha_inicio": idx,
            "linha_fim": len(linhas),
            "funcao_bloco": m.group("nome"),
            "tipo_bloco": tipo,
        }

    if atual is not None:
        atual["linha_fim"] = len(linhas)
        blocos.append(atual)

    return pd.DataFrame(blocos)


def _atribuir_funcao(linha: int, df_blocos: pd.DataFrame) -> tuple[str, str]:
    if df_blocos.empty:
        return "arquivo_sem_mapa", "desconhecido"
    cand = df_blocos[(df_blocos["linha_inicio"] <= linha) & (df_blocos["linha_fim"] >= linha)]
    if cand.empty:
        return "top_level", "top_level"
    row = cand.sort_values("linha_inicio", ascending=False).iloc[0]
    return str(row.get("funcao_bloco") or "top_level"), str(row.get("tipo_bloco") or "desconhecido")


def _atribuir_bloco_responsavel(trecho: str, nome_padrao: str) -> tuple[str, str, str]:
    alvo = f"{trecho}\n{nome_padrao}"
    for spec in PADROES_BLOCO:
        if re.search(spec["regex"], alvo, flags=re.IGNORECASE):
            return spec["bloco_responsavel"], spec["familia_migracao"], spec["acao_minima"]
    spec = PADROES_BLOCO[-1]
    return spec["bloco_responsavel"], spec["familia_migracao"], spec["acao_minima"]


def _preparar_pontos_p0_p1(df_a4: pd.DataFrame, df_blocos: pd.DataFrame) -> pd.DataFrame:
    if df_a4.empty:
        return pd.DataFrame()
    df = df_a4[df_a4["classe_v17_a4"].astype(str).isin(CLASSES_ALVO)].copy()
    if df.empty:
        return df

    funcoes = []
    tipos_blocos = []
    blocos_resp = []
    familias = []
    acoes = []
    prioridades = []
    for _, row in df.iterrows():
        linha = int(row.get("linha") or 0)
        funcao, tipo_bloco = _atribuir_funcao(linha, df_blocos)
        bloco, familia, acao = _atribuir_bloco_responsavel(str(row.get("trecho") or ""), str(row.get("nome_padrao") or ""))
        classe = str(row.get("classe_v17_a4") or "")
        funcoes.append(funcao)
        tipos_blocos.append(tipo_bloco)
        blocos_resp.append(bloco)
        familias.append(familia)
        acoes.append(acao)
        prioridades.append(PRIORIDADE_CLASSE.get(classe, "P2"))

    df["funcao_bloco"] = funcoes
    df["tipo_bloco"] = tipos_blocos
    df["bloco_responsavel"] = blocos_resp
    df["familia_migracao"] = familias
    df["prioridade"] = prioridades
    df["acao_minima_migracao"] = acoes
    df["altera_codigo_v17_b0"] = False
    return df.sort_values(["prioridade", "familia_migracao", "funcao_bloco", "linha"], kind="stable")


def _consolidar_funcoes(df_pontos: pd.DataFrame) -> pd.DataFrame:
    if df_pontos.empty:
        return pd.DataFrame()

    linhas: list[dict[str, Any]] = []
    grupos = df_pontos.groupby(["funcao_bloco", "tipo_bloco", "bloco_responsavel", "familia_migracao"], dropna=False)
    for (funcao, tipo_bloco, bloco_resp, familia), sub in grupos:
        classes = sub["classe_v17_a4"].astype(str).value_counts().to_dict()
        prioridades = sorted(set(sub["prioridade"].astype(str)), key=lambda x: ORDEM_PRIORIDADE.get(x, 9))
        prioridade_max = prioridades[0] if prioridades else "P3"
        linhas.append({
            "funcao_bloco": funcao,
            "tipo_bloco": tipo_bloco,
            "bloco_responsavel": bloco_resp,
            "familia_migracao": familia,
            "prioridade_maxima": prioridade_max,
            "qtd_pontos": int(len(sub)),
            "qtd_correcao_funcional_proibida": int(classes.get("correcao_funcional_proibida", 0)),
            "qtd_migrar_para_estado_temporal": int(classes.get("migrar_para_estado_temporal", 0)),
            "qtd_inferencia_operacional_indevida": int(classes.get("inferencia_operacional_indevida", 0)),
            "linhas_min_max": f"{int(sub['linha'].min())}-{int(sub['linha'].max())}",
            "acao_minima_migracao": str(sub["acao_minima_migracao"].dropna().iloc[0]) if len(sub["acao_minima_migracao"].dropna()) else "triagem manual",
            "decisao_v17_b0": "migrar_antes_de_v17_funcional" if prioridade_max == "P0" else "auditar_antes_de_v17_funcional",
        })
    df = pd.DataFrame(linhas)
    return df.sort_values(["prioridade_maxima", "familia_migracao", "qtd_pontos"], ascending=[True, True, False], kind="stable")


def _gerar_plano(df_funcoes: pd.DataFrame) -> pd.DataFrame:
    plano = pd.DataFrame(SEQUENCIA_MIGRACAO)
    if df_funcoes.empty:
        plano["qtd_funcoes_blocos_afetados"] = 0
        plano["qtd_pontos_relacionados"] = 0
        return plano

    qtd_funcoes = []
    qtd_pontos = []
    for _, etapa in plano.iterrows():
        familias = str(etapa.get("familia_migracao") or "").split("|")
        sub = df_funcoes[df_funcoes["familia_migracao"].astype(str).isin(familias)]
        qtd_funcoes.append(int(len(sub)))
        qtd_pontos.append(int(sub["qtd_pontos"].sum()) if not sub.empty else 0)
    plano["qtd_funcoes_blocos_afetados"] = qtd_funcoes
    plano["qtd_pontos_relacionados"] = qtd_pontos
    return plano


def _gerar_guardrails() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "guardrail": "v17_b0_nao_altera_saida_canonica",
            "regra": "V17-B0 apenas consolida plano; nenhuma linha de nucleo/saida_canonica.py deve ser alterada.",
        },
        {
            "guardrail": "migracao_p0_antes_de_v17_funcional",
            "regra": "correcao_funcional_proibida e migrar_para_estado_temporal sao P0 e bloqueiam abertura funcional sem migracao ou rollback explicito.",
        },
        {
            "guardrail": "inferencia_operacional_p1",
            "regra": "inferencia_operacional_indevida deve ser substituida por estado decidido ou justificada por guardrail antes de integracao funcional.",
        },
        {
            "guardrail": "saida_renderiza_estado",
            "regra": "saida_canonica deve renderizar estado decidido; nao pode escolher fonte, recalcular financeiro, materializar switching ou resolver precedencia intradiaria.",
        },
        {
            "guardrail": "sem_mudanca_de_motor_na_v17_b0",
            "regra": "motor, ranking, switching funcional, contrato, modelo e saida canonica permanecem inalterados nesta etapa.",
        },
    ])


def main() -> int:
    df_a4 = _ler_csv(ARQ_IN_PONTOS_A4, [
        "arquivo", "linha", "trecho", "nome_padrao", "classe_v17_a4", "severidade",
        "acao_recomendada", "criterio_classificacao", "altera_codigo",
    ])
    df_blocos = _mapear_funcoes_saida()
    df_pontos = _preparar_pontos_p0_p1(df_a4, df_blocos)
    df_funcoes = _consolidar_funcoes(df_pontos)
    df_plano = _gerar_plano(df_funcoes)
    df_guardrails = _gerar_guardrails()

    total_p0 = int((df_pontos["prioridade"] == "P0").sum()) if not df_pontos.empty else 0
    total_p1 = int((df_pontos["prioridade"] == "P1").sum()) if not df_pontos.empty else 0
    total_funcoes_p0 = int((df_funcoes["prioridade_maxima"] == "P0").sum()) if not df_funcoes.empty else 0
    total_funcoes_p1 = int((df_funcoes["prioridade_maxima"] == "P1").sum()) if not df_funcoes.empty else 0

    status_global = "ok_diagnostico"
    decisao = "manter_bloqueio_v17_funcional_ate_plano_p0_p1"
    if total_p0 == 0 and total_p1 == 0:
        decisao = "sem_bloqueio_p0_p1_detectado"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_b0", "valor": status_global, "status": "ok", "observacao": "plano diagnostico consolidado"},
        {"metrica": "decisao_v17_funcional", "valor": decisao, "status": "bloqueio_preventivo" if decisao.startswith("manter") else "ok", "observacao": "V17-B0 nao altera codigo funcional"},
        {"metrica": "pontos_p0_p1_consolidados", "valor": int(len(df_pontos)), "status": "info", "observacao": "correcao_funcional_proibida + migrar_para_estado_temporal + inferencia_operacional_indevida"},
        {"metrica": "pontos_p0", "valor": total_p0, "status": "bloqueio_preventivo" if total_p0 else "ok", "observacao": "migrar antes de V17 funcional"},
        {"metrica": "pontos_p1", "valor": total_p1, "status": "bloqueio_preventivo" if total_p1 else "ok", "observacao": "auditar/substituir por estado decidido"},
        {"metrica": "funcoes_blocos_com_p0", "valor": total_funcoes_p0, "status": "bloqueio_preventivo" if total_funcoes_p0 else "ok", "observacao": "blocos com prioridade maxima P0"},
        {"metrica": "funcoes_blocos_com_p1", "valor": total_funcoes_p1, "status": "bloqueio_preventivo" if total_funcoes_p1 else "ok", "observacao": "blocos com prioridade maxima P1"},
        {"metrica": "etapas_plano_migracao", "valor": int(len(df_plano)), "status": "ok", "observacao": "sequencia minima proposta"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/switching"},
        {"metrica": "confirmacao_sem_alterar_saida_canonica", "valor": True, "status": "ok", "observacao": "saida_canonica.py apenas lido estaticamente"},
    ])

    _gravar_csv(df_pontos, ARQ_OUT_PONTOS, [
        "arquivo", "linha", "funcao_bloco", "tipo_bloco", "bloco_responsavel", "familia_migracao",
        "classe_v17_a4", "prioridade", "severidade", "nome_padrao", "trecho",
        "acao_minima_migracao", "acao_recomendada", "criterio_classificacao", "altera_codigo_v17_b0",
    ])
    _gravar_csv(df_funcoes, ARQ_OUT_FUNCOES, [
        "funcao_bloco", "tipo_bloco", "bloco_responsavel", "familia_migracao", "prioridade_maxima",
        "qtd_pontos", "qtd_correcao_funcional_proibida", "qtd_migrar_para_estado_temporal",
        "qtd_inferencia_operacional_indevida", "linhas_min_max", "acao_minima_migracao", "decisao_v17_b0",
    ])
    _gravar_csv(df_plano, ARQ_OUT_PLANO, [
        "ordem", "microetapa_futura", "familia_migracao", "objetivo", "escopo_permitido",
        "escopo_proibido", "criterio_saida", "qtd_funcoes_blocos_afetados", "qtd_pontos_relacionados",
    ])
    _gravar_csv(df_guardrails, ARQ_OUT_GUARDRAILS, ["guardrail", "regra"])
    _gravar_csv(resumo, ARQ_OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-B0 — PLANO DIAGNOSTICO DE MIGRACAO MINIMA DA SAIDA ===")
    print(f"status_global_v17_b0={status_global}")
    print(f"decisao_v17_funcional={decisao}")
    print(f"pontos_p0_p1_consolidados={len(df_pontos)}")
    print(f"pontos_p0={total_p0}")
    print(f"pontos_p1={total_p1}")
    print(f"funcoes_blocos_com_p0={total_funcoes_p0}")
    print(f"funcoes_blocos_com_p1={total_funcoes_p1}")
    print(f"etapas_plano_migracao={len(df_plano)}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

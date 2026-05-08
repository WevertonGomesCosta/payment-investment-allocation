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
IN_DIR_B0 = RAIZ / "saidas" / "diagnostico" / "v17_b0"
ARQ_IN_B0_PONTOS = IN_DIR_B0 / "v17_b0_pontos_p0_p1_por_funcao.csv"
ARQ_IN_B0_FUNCOES = IN_DIR_B0 / "v17_b0_funcoes_blocos_responsaveis.csv"

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_b1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_OUT_PONTOS = OUT_DIR / "v17_b1_pontos_escolha_fonte_saida.csv"
ARQ_OUT_MATRIZ = OUT_DIR / "v17_b1_matriz_orquestracao_fonte_verdade.csv"
ARQ_OUT_CONTRATO = OUT_DIR / "v17_b1_contrato_diagnostico_fonte_verdade.csv"
ARQ_OUT_GUARDRAILS = OUT_DIR / "v17_b1_guardrails_fonte_verdade.csv"
ARQ_OUT_RESUMO = OUT_DIR / "v17_b1_resumo.csv"

PADROES_FONTE = [
    {
        "fonte_detectada": "motor_recomendacao_pagamentos_switching_v1",
        "regex": r"motor_recomendacao_pagamentos_switching_v1|motor_recomendacao|quadro_recomendacoes",
        "classe_risco": "saida_escolhe_motor_ou_quadro_funcional",
        "prioridade": "P0",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.recomendacoes_futuras",
        "acao_orquestracao": "orquestrador anterior a saida deve escolher o quadro final de recomendacoes; saida apenas renderiza",
    },
    {
        "fonte_detectada": "decisao_local_v1",
        "regex": r"decisao_local_v1|quadro_decisao_local_v1|quadro_decisoes",
        "classe_risco": "saida_escolhe_decisao_local_ou_fallback_de_decisao",
        "prioridade": "P0",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.decisoes_pagamento",
        "acao_orquestracao": "orquestrador deve receber decisao local ja validada ou substituida pelo motor final antes da saida",
    },
    {
        "fonte_detectada": "fallback_recebido_disponivel",
        "regex": r"fallback|recebido_disponivel|fontes_elegiveis|quadro_fontes_elegiveis|valor_liquido_disponivel|_mapa_fontes_elegiveis",
        "classe_risco": "saida_aplica_fallback_de_fonte",
        "prioridade": "P0",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.fontes_pagamento_v17",
        "acao_orquestracao": "adapter temporal deve classificar fonte V17 antes da saida; saida nao pode completar recebido_disponivel",
    },
    {
        "fonte_detectada": "saldo_disponivel_geral",
        "regex": r"saldo_disponivel_geral|quadro_saldo_disponivel|_mapa_saldo_disponivel",
        "classe_risco": "saida_consulta_saldo_operacional_auxiliar",
        "prioridade": "P1",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.estado_caixa_pagamentos",
        "acao_orquestracao": "estado temporal deve fornecer caixa/fonte ja classificada; saida nao deve consultar saldo auxiliar para decidir fonte",
    },
    {
        "fonte_detectada": "recomputacao_sequencial_central_v1",
        "regex": r"recomputacao_sequencial_central_v1|quadro_recomputacao_sequencial_central|_mapa_pagamentos_central",
        "classe_risco": "saida_consulta_recomputacao_como_fonte_alternativa",
        "prioridade": "P1",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.replay_pagamentos_consolidado",
        "acao_orquestracao": "orquestrador deve consolidar recomputacao/replay antes da saida",
    },
    {
        "fonte_detectada": "switching_quadro_saida",
        "regex": r"self\.switchings|switchings|quadro_switching|Produto destino switching|destino_switching_janela|lote_origem_switching",
        "classe_risco": "saida_constroi_estado_switching_a_partir_de_quadro",
        "prioridade": "P0",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.estado_temporal_switching",
        "acao_orquestracao": "estado temporal de switching deve materializar origem/destino antes da saida",
    },
    {
        "fonte_detectada": "ranking_amostra",
        "regex": r"ranking_amostra|ranking_destino|Top1|produto_nome_canonico",
        "classe_risco": "saida_usa_ranking_para_completar_destino_ou_carteira",
        "prioridade": "P1",
        "fonte_verdade_proposta": "pacote_orquestrado_pre_saida.destinos_switching_reconciliados",
        "acao_orquestracao": "ranking pode ser referencia informativa, mas destino operacional deve vir reconciliado antes da saida",
    },
]

ORDEM_PRIORIDADE = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


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
        atual = {
            "linha_inicio": idx,
            "linha_fim": len(linhas),
            "funcao_bloco": m.group("nome"),
            "tipo_bloco": "classe" if linha.lstrip().startswith("class ") else "funcao",
        }

    if atual is not None:
        atual["linha_fim"] = len(linhas)
        blocos.append(atual)
    return pd.DataFrame(blocos)


def _atribuir_funcao(linha: int, df_blocos: pd.DataFrame) -> tuple[str, str]:
    cand = df_blocos[(df_blocos["linha_inicio"] <= linha) & (df_blocos["linha_fim"] >= linha)] if not df_blocos.empty else pd.DataFrame()
    if cand.empty:
        return "top_level", "top_level"
    row = cand.sort_values("linha_inicio", ascending=False).iloc[0]
    return str(row.get("funcao_bloco") or "top_level"), str(row.get("tipo_bloco") or "desconhecido")


def _detectar_pontos_saida(df_blocos: pd.DataFrame) -> pd.DataFrame:
    linhas_arquivo = ARQ_SAIDA_CANONICA.read_text(encoding="utf-8").splitlines()
    achados: list[dict[str, Any]] = []

    for n, linha in enumerate(linhas_arquivo, start=1):
        trecho = linha.rstrip("\n")
        if not trecho.strip():
            continue
        for spec in PADROES_FONTE:
            if not re.search(spec["regex"], trecho, flags=re.IGNORECASE):
                continue
            funcao, tipo_bloco = _atribuir_funcao(n, df_blocos)
            achados.append({
                "arquivo": str(ARQ_SAIDA_CANONICA.relative_to(RAIZ)),
                "linha": n,
                "funcao_bloco": funcao,
                "tipo_bloco": tipo_bloco,
                "trecho": trecho.strip()[:500],
                "fonte_detectada": spec["fonte_detectada"],
                "classe_risco": spec["classe_risco"],
                "prioridade": spec["prioridade"],
                "fonte_verdade_proposta": spec["fonte_verdade_proposta"],
                "acao_orquestracao": spec["acao_orquestracao"],
                "altera_codigo_v17_b1": False,
            })
    df = pd.DataFrame(achados)
    if df.empty:
        return df
    df["_ordem"] = df["prioridade"].map(ORDEM_PRIORIDADE).fillna(9).astype(int)
    df = df.sort_values(["_ordem", "funcao_bloco", "linha", "fonte_detectada"], kind="stable")
    df = df.drop(columns=["_ordem"])
    return df


def _consolidar_matriz(df_pontos: pd.DataFrame, df_b0_funcoes: pd.DataFrame) -> pd.DataFrame:
    if df_pontos.empty:
        return pd.DataFrame()

    linhas: list[dict[str, Any]] = []
    grupos = df_pontos.groupby(["funcao_bloco", "tipo_bloco", "fonte_detectada", "classe_risco", "fonte_verdade_proposta"], dropna=False)
    for (funcao, tipo_bloco, fonte, classe, fonte_verdade), sub in grupos:
        prioridades = sorted(set(sub["prioridade"].astype(str)), key=lambda x: ORDEM_PRIORIDADE.get(x, 9))
        prioridade = prioridades[0] if prioridades else "P3"
        acao = str(sub["acao_orquestracao"].dropna().iloc[0]) if len(sub["acao_orquestracao"].dropna()) else "auditar manualmente"
        b0_match = pd.DataFrame()
        if not df_b0_funcoes.empty and "funcao_bloco" in df_b0_funcoes.columns:
            b0_match = df_b0_funcoes[df_b0_funcoes["funcao_bloco"].astype(str) == str(funcao)]
        linhas.append({
            "funcao_bloco": funcao,
            "tipo_bloco": tipo_bloco,
            "fonte_detectada": fonte,
            "classe_risco": classe,
            "prioridade": prioridade,
            "qtd_ocorrencias": int(len(sub)),
            "linhas_min_max": f"{int(sub['linha'].min())}-{int(sub['linha'].max())}",
            "fonte_verdade_unica_proposta": fonte_verdade,
            "acao_orquestracao_anterior_saida": acao,
            "aparece_no_plano_v17_b0": not b0_match.empty,
            "qtd_pontos_b0_na_funcao": int(b0_match["qtd_pontos"].sum()) if not b0_match.empty and "qtd_pontos" in b0_match.columns else 0,
            "decisao_v17_b1": "definir_fonte_verdade_antes_de_v17_funcional" if prioridade in {"P0", "P1"} else "monitorar",
        })
    df = pd.DataFrame(linhas)
    df["_ordem"] = df["prioridade"].map(ORDEM_PRIORIDADE).fillna(9).astype(int)
    df = df.sort_values(["_ordem", "fonte_verdade_unica_proposta", "qtd_ocorrencias"], ascending=[True, True, False], kind="stable")
    return df.drop(columns=["_ordem"])


def _gerar_contrato_diagnostico(df_matriz: pd.DataFrame) -> pd.DataFrame:
    linhas_base = [
        {
            "item_contrato_diagnostico": "entrada_unica_saida_canonica",
            "regra": "saida_canonica deve receber um pacote orquestrado unico, nao escolher entre motor_recomendacao, decisao_local, recomputacao ou fallback.",
            "fonte_verdade_unica_proposta": "pacote_orquestrado_pre_saida",
            "obrigatorio_antes_v17_funcional": True,
        },
        {
            "item_contrato_diagnostico": "recomendacoes_futuras",
            "regra": "quadro de recomendacoes futuras deve ser escolhido antes da saida por orquestrador/estado temporal.",
            "fonte_verdade_unica_proposta": "pacote_orquestrado_pre_saida.recomendacoes_futuras",
            "obrigatorio_antes_v17_funcional": True,
        },
        {
            "item_contrato_diagnostico": "decisoes_pagamento",
            "regra": "decisoes de fonte de pagamento devem chegar consolidadas e auditaveis; saida nao pode promover fallback.",
            "fonte_verdade_unica_proposta": "pacote_orquestrado_pre_saida.decisoes_pagamento",
            "obrigatorio_antes_v17_funcional": True,
        },
        {
            "item_contrato_diagnostico": "fontes_pagamento_v17",
            "regra": "fontes devem estar classificadas na taxonomia V17 antes da renderizacao.",
            "fonte_verdade_unica_proposta": "pacote_orquestrado_pre_saida.fontes_pagamento_v17",
            "obrigatorio_antes_v17_funcional": True,
        },
        {
            "item_contrato_diagnostico": "estado_temporal_switching",
            "regra": "origem/destino de switching e lote materializado devem vir do estado temporal, nao da saida.",
            "fonte_verdade_unica_proposta": "pacote_orquestrado_pre_saida.estado_temporal_switching",
            "obrigatorio_antes_v17_funcional": True,
        },
    ]
    df = pd.DataFrame(linhas_base)
    if not df_matriz.empty:
        usados = set(df_matriz["fonte_verdade_unica_proposta"].astype(str))
        df["detectada_na_saida_atual"] = df["fonte_verdade_unica_proposta"].astype(str).isin(usados)
    else:
        df["detectada_na_saida_atual"] = False
    return df


def _gerar_guardrails() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "guardrail": "b1_nao_altera_saida_canonica",
            "regra": "V17-B1 apenas define matriz diagnostica; nucleo/saida_canonica.py permanece inalterado.",
        },
        {
            "guardrail": "saida_nao_escolhe_quadro",
            "regra": "saida nao pode escolher entre motor_recomendacao, decisao_local_v1, recomputacao ou quadros alternativos.",
        },
        {
            "guardrail": "saida_nao_aplica_fallback_fonte",
            "regra": "fallback de recebido_disponivel/fontes_elegiveis deve ser resolvido antes da saida.",
        },
        {
            "guardrail": "pacote_orquestrado_pre_saida",
            "regra": "a futura integracao funcional deve introduzir uma fonte unica de verdade antes de remover logica da saida.",
        },
        {
            "guardrail": "sem_mudanca_motor_ranking_switching",
            "regra": "motor, ranking, switching funcional, contrato e modelo permanecem inalterados nesta etapa.",
        },
    ])


def main() -> int:
    if not ARQ_SAIDA_CANONICA.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {ARQ_SAIDA_CANONICA}")

    df_b0_funcoes = _ler_csv(ARQ_IN_B0_FUNCOES, [
        "funcao_bloco", "tipo_bloco", "bloco_responsavel", "familia_migracao", "prioridade_maxima",
        "qtd_pontos", "qtd_correcao_funcional_proibida", "qtd_migrar_para_estado_temporal",
        "qtd_inferencia_operacional_indevida", "linhas_min_max", "acao_minima_migracao", "decisao_v17_b0",
    ])
    df_blocos = _mapear_funcoes_saida()
    df_pontos = _detectar_pontos_saida(df_blocos)
    df_matriz = _consolidar_matriz(df_pontos, df_b0_funcoes)
    df_contrato = _gerar_contrato_diagnostico(df_matriz)
    df_guardrails = _gerar_guardrails()

    total_pontos = int(len(df_pontos))
    total_p0 = int((df_pontos["prioridade"] == "P0").sum()) if not df_pontos.empty else 0
    total_p1 = int((df_pontos["prioridade"] == "P1").sum()) if not df_pontos.empty else 0
    total_funcoes = int(df_matriz["funcao_bloco"].nunique()) if not df_matriz.empty else 0
    total_fontes = int(df_matriz["fonte_detectada"].nunique()) if not df_matriz.empty else 0
    total_fontes_verdade = int(df_matriz["fonte_verdade_unica_proposta"].nunique()) if not df_matriz.empty else 0

    status_global = "ok_diagnostico"
    decisao = "manter_bloqueio_v17_funcional_ate_fonte_verdade_pre_saida"
    if total_p0 == 0 and total_p1 == 0:
        decisao = "sem_escolha_fonte_detectada_na_saida"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_b1", "valor": status_global, "status": "ok", "observacao": "matriz diagnostica de fonte de verdade gerada"},
        {"metrica": "decisao_v17_funcional", "valor": decisao, "status": "bloqueio_preventivo" if decisao.startswith("manter") else "ok", "observacao": "saida ainda nao deve ser integrada funcionalmente"},
        {"metrica": "pontos_escolha_fonte_detectados", "valor": total_pontos, "status": "info", "observacao": "ocorrencias estaticas"},
        {"metrica": "pontos_p0", "valor": total_p0, "status": "bloqueio_preventivo" if total_p0 else "ok", "observacao": "exige orquestracao antes da saida"},
        {"metrica": "pontos_p1", "valor": total_p1, "status": "bloqueio_preventivo" if total_p1 else "ok", "observacao": "exige auditoria/estado decidido"},
        {"metrica": "funcoes_blocos_afetados", "valor": total_funcoes, "status": "info", "observacao": "funcoes/blocos com escolha ou consulta de fonte"},
        {"metrica": "fontes_detectadas", "valor": total_fontes, "status": "info", "observacao": "fontes funcionais/auxiliares detectadas na saida"},
        {"metrica": "fontes_verdade_unicas_propostas", "valor": total_fontes_verdade, "status": "ok", "observacao": "componentes do pacote orquestrado pre-saida"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/switching"},
        {"metrica": "confirmacao_sem_alterar_saida_canonica", "valor": True, "status": "ok", "observacao": "saida_canonica.py apenas lido estaticamente"},
    ])

    _gravar_csv(df_pontos, ARQ_OUT_PONTOS, [
        "arquivo", "linha", "funcao_bloco", "tipo_bloco", "trecho", "fonte_detectada", "classe_risco",
        "prioridade", "fonte_verdade_proposta", "acao_orquestracao", "altera_codigo_v17_b1",
    ])
    _gravar_csv(df_matriz, ARQ_OUT_MATRIZ, [
        "funcao_bloco", "tipo_bloco", "fonte_detectada", "classe_risco", "prioridade", "qtd_ocorrencias",
        "linhas_min_max", "fonte_verdade_unica_proposta", "acao_orquestracao_anterior_saida",
        "aparece_no_plano_v17_b0", "qtd_pontos_b0_na_funcao", "decisao_v17_b1",
    ])
    _gravar_csv(df_contrato, ARQ_OUT_CONTRATO, [
        "item_contrato_diagnostico", "regra", "fonte_verdade_unica_proposta", "obrigatorio_antes_v17_funcional", "detectada_na_saida_atual",
    ])
    _gravar_csv(df_guardrails, ARQ_OUT_GUARDRAILS, ["guardrail", "regra"])
    _gravar_csv(resumo, ARQ_OUT_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-B1 — MATRIZ DIAGNOSTICA DE FONTE DE VERDADE DA SAIDA ===")
    print(f"status_global_v17_b1={status_global}")
    print(f"decisao_v17_funcional={decisao}")
    print(f"pontos_escolha_fonte_detectados={total_pontos}")
    print(f"pontos_p0={total_p0}")
    print(f"pontos_p1={total_p1}")
    print(f"funcoes_blocos_afetados={total_funcoes}")
    print(f"fontes_detectadas={total_fontes}")
    print(f"fontes_verdade_unicas_propostas={total_fontes_verdade}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

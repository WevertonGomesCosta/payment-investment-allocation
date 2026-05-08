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
OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a4"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_PONTOS = OUT_DIR / "v17_a4_pontos_suspeitos_saida_canonica.csv"
ARQ_PRIORIDADE = OUT_DIR / "v17_a4_priorizacao_migracao_saida_canonica.csv"
ARQ_GUARDRAILS = OUT_DIR / "v17_a4_guardrails_saida_canonica.csv"
ARQ_RESUMO = OUT_DIR / "v17_a4_resumo.csv"

CLASSES = [
    "formatacao_legitima",
    "normalizacao_transitoria_aceitavel",
    "inferencia_operacional_indevida",
    "correcao_funcional_proibida",
    "migrar_para_estado_temporal",
]

PADROES: list[dict[str, Any]] = [
    {
        "nome_padrao": "normalizacao_status_sem_fonte",
        "regex": r"_normalizar_sem_fonte_valida|sem_saldo_temporal|saldo_temporal_insuficiente|Lote sugerido|Origem switching",
        "classe": "normalizacao_transitoria_aceitavel",
        "severidade": "alta",
        "acao": "manter apenas como transitorio auditavel ate estado temporal decidir explicitamente a ausencia de fonte",
        "criterio": "nao pode criar fonte, trocar fonte ou resolver saldo; apenas ocultar campo invalido ja marcado como sem saldo auditavel",
    },
    {
        "nome_padrao": "preenchimento_nd_console",
        "regex": r"n/d|não determinado|nao determinado|_primeiro_valor_auditavel|_eh_indeterminado|_valor_auditavel_preenchido",
        "classe": "formatacao_legitima",
        "severidade": "baixa",
        "acao": "manter como renderizacao visual se nao alterar decisao nem valor financeiro",
        "criterio": "apenas substitui vazio por marcador textual na apresentacao",
    },
    {
        "nome_padrao": "lotes_sinteticos_pos_switching",
        "regex": r"lotes_sinteticos_pos_switching|Novo lote|valor_total|Lotes origem|pos_switch|pós-switching|pos-switching",
        "classe": "migrar_para_estado_temporal",
        "severidade": "bloqueante",
        "acao": "migrar materializacao sintetica para estado temporal V17 antes de consumo funcional",
        "criterio": "saida nao deve construir lote novo, somar valor de switching ou definir identificador canonico",
    },
    {
        "nome_padrao": "estado_pos_switching_na_saida",
        "regex": r"estado_pos_switching|ativo_pos_switching|migrado_por_switching|Produto destino|Status novo|Status origem",
        "classe": "migrar_para_estado_temporal",
        "severidade": "bloqueante",
        "acao": "mover estado pos-switching para ledger/estado temporal canonico",
        "criterio": "saida deve exibir estado decidido, nao construir estado operacional de switching",
    },
    {
        "nome_padrao": "fallback_recebido_disponivel",
        "regex": r"fallback|recebido_disponivel|fontes_elegiveis|quadro_fontes_elegiveis|valor_liquido_disponivel",
        "classe": "inferencia_operacional_indevida",
        "severidade": "alta",
        "acao": "auditar como ponte transitoria; migrar decisao para estado temporal ou remover se criar fonte fora do motor",
        "criterio": "saida nao deve escolher recebido_disponivel; apenas pode refletir decisao ja tomada e auditada",
    },
    {
        "nome_padrao": "limpeza_lotes_migrados",
        "regex": r"_limpar_lotes_migrados|partes_validas|conflito_intradia|mapa_migrados|data_sw|novo_lote",
        "classe": "correcao_funcional_proibida",
        "severidade": "bloqueante",
        "acao": "migrar regra intradiaria e exclusao de lotes migrados para estado temporal; saida nao deve remover fontes",
        "criterio": "qualquer exclusao de lote por data/switching deve ocorrer antes da saida canonica",
    },
    {
        "nome_padrao": "calculo_saldos_correntes",
        "regex": r"_mapa_saldos_correntes|valor_bruto_em_data|valor_liquido_em_data|valor_liquido_hoje|principal_remanescente|saldo_bruto|tabela_iof|faixas_ir",
        "classe": "migrar_para_estado_temporal",
        "severidade": "alta",
        "acao": "manter apenas se for espelho de estado ja calculado; caso recalcule valor, migrar para nucleo economico/estado temporal",
        "criterio": "saida nao deve recalcular rendimento, imposto, saldo bruto ou liquido",
    },
    {
        "nome_padrao": "avanco_lote_data",
        "regex": r"_avancar_lote_para_data|atualizar_juros|taxa_diaria|data_cursor|fator_dia|serie_cdi",
        "classe": "correcao_funcional_proibida",
        "severidade": "bloqueante",
        "acao": "remover futuramente da saida e mover para motor/estado temporal se ainda necessario",
        "criterio": "saida nao deve capitalizar lote nem avançar estado financeiro",
    },
    {
        "nome_padrao": "escolha_quadro_preferencial",
        "regex": r"_quadro_futuro_preferencial|motor_recomendacao|decisao_local_v1|quadro_recomendacoes|quadro_decisao_local_v1",
        "classe": "inferencia_operacional_indevida",
        "severidade": "alta",
        "acao": "saida deve receber quadro final ja definido por estado/camada orquestradora, nao escolher prioridade entre motores",
        "criterio": "se houver escolha entre fontes funcionais, migrar para orquestracao anterior a saida",
    },
    {
        "nome_padrao": "formatacao_console",
        "regex": r"pagamentos_.*_console|recebidos_.*_console|return \[|linhas\.append|linhas\.sort|limite|_round_monetario|_fmt_data|_split_fontes",
        "classe": "formatacao_legitima",
        "severidade": "baixa",
        "acao": "manter se apenas remodela campos para console/relatorio e nao altera fonte/valor/status operacional",
        "criterio": "permitido para apresentacao, amostragem e arredondamento visual auditavel",
    },
    {
        "nome_padrao": "normalizacao_situacao_atual",
        "regex": r"normalizar_valores_situacao_atual_exaurida|resumir_fechamento_situacao_atual|fechamento_atual",
        "classe": "normalizacao_transitoria_aceitavel",
        "severidade": "media",
        "acao": "validar se apenas normaliza rotulo; migrar se corrigir saldo/estado",
        "criterio": "normalizacao de label aceitavel; normalizacao de valor operacional deve sair da saida",
    },
]

ORDEM_PRIORIDADE = {
    "bloqueante": 0,
    "alta": 1,
    "media": 2,
    "baixa": 3,
}


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _classificar_linha(numero: int, texto: str) -> list[dict[str, Any]]:
    achados: list[dict[str, Any]] = []
    texto_limpo = texto.rstrip("\n")
    if not texto_limpo.strip():
        return achados

    for padrao in PADROES:
        if re.search(padrao["regex"], texto_limpo, flags=re.IGNORECASE):
            achados.append({
                "arquivo": str(ARQ_SAIDA_CANONICA.relative_to(RAIZ)),
                "linha": numero,
                "trecho": texto_limpo.strip()[:500],
                "nome_padrao": padrao["nome_padrao"],
                "classe_v17_a4": padrao["classe"],
                "severidade": padrao["severidade"],
                "acao_recomendada": padrao["acao"],
                "criterio_classificacao": padrao["criterio"],
                "altera_codigo": False,
            })
    return achados


def _deduplicar_por_linha_classe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["_ordem"] = df["severidade"].map(ORDEM_PRIORIDADE).fillna(9).astype(int)
    df = df.sort_values(["linha", "_ordem", "nome_padrao"], kind="stable")
    df = df.drop_duplicates(subset=["linha", "classe_v17_a4"], keep="first")
    return df.drop(columns=["_ordem"])


def _gerar_priorizacao(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "classe_v17_a4", "severidade_maxima", "qtd_pontos", "prioridade", "decisao", "acao_futura",
        ])

    linhas: list[dict[str, Any]] = []
    for classe, sub in df.groupby("classe_v17_a4", dropna=False):
        severidade_max = sorted(sub["severidade"].astype(str).unique(), key=lambda x: ORDEM_PRIORIDADE.get(x, 9))[0]
        qtd = int(len(sub))
        if classe == "correcao_funcional_proibida":
            prioridade = "P0"
            decisao = "migrar_ou_remover_antes_de_v17_funcional"
            acao = "nenhuma correcao operacional pode permanecer na saida quando a V17 funcional for aberta"
        elif classe == "migrar_para_estado_temporal":
            prioridade = "P0" if severidade_max == "bloqueante" else "P1"
            decisao = "migrar_para_estado_temporal"
            acao = "levar construcao de estado, lote sintetico, saldo ou switching para camada temporal canonica"
        elif classe == "inferencia_operacional_indevida":
            prioridade = "P1"
            decisao = "auditar_e_substituir_por_estado_decidido"
            acao = "saida pode refletir decisao ja tomada, mas nao escolher fonte, quadro ou fallback funcional"
        elif classe == "normalizacao_transitoria_aceitavel":
            prioridade = "P2"
            decisao = "permitir_transitoriamente_com_guardrail"
            acao = "aceitar apenas se nao alterar decisao, fonte ou valor financeiro"
        else:
            prioridade = "P3"
            decisao = "manter_como_formatacao"
            acao = "manter como apresentacao se nao houver efeito operacional"
        linhas.append({
            "classe_v17_a4": classe,
            "severidade_maxima": severidade_max,
            "qtd_pontos": qtd,
            "prioridade": prioridade,
            "decisao": decisao,
            "acao_futura": acao,
        })
    return pd.DataFrame(linhas).sort_values(["prioridade", "classe_v17_a4"], kind="stable")


def _gerar_guardrails() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "guardrail": "saida_nao_decide_fonte",
            "classe_relacionada": "inferencia_operacional_indevida",
            "regra": "saida_canonica pode exibir fonte decidida, mas nao escolher entre motor, decisao_local, fallback ou recebido_disponivel.",
        },
        {
            "guardrail": "saida_nao_corrige_estado",
            "classe_relacionada": "correcao_funcional_proibida",
            "regra": "saida_canonica nao pode limpar, remover ou trocar lote/fonte por regra temporal ou switching.",
        },
        {
            "guardrail": "saida_nao_materializa_switching",
            "classe_relacionada": "migrar_para_estado_temporal",
            "regra": "lote pos-switching e estado pos-switching devem ser produzidos no estado temporal, nao na renderizacao.",
        },
        {
            "guardrail": "saida_nao_recalcula_financeiro",
            "classe_relacionada": "migrar_para_estado_temporal|correcao_funcional_proibida",
            "regra": "saida_canonica nao deve recalcular juros, IR, IOF, saldo bruto, liquido ou remanescente.",
        },
        {
            "guardrail": "formatacao_e_permitida",
            "classe_relacionada": "formatacao_legitima",
            "regra": "formatar datas, nomes, limites de amostra e marcadores n/d e permitido quando nao muda semantica operacional.",
        },
        {
            "guardrail": "normalizacao_transitoria_controlada",
            "classe_relacionada": "normalizacao_transitoria_aceitavel",
            "regra": "normalizacao visual pode ser aceita temporariamente, mas deve ter origem e limite explicitos.",
        },
    ])


def main() -> int:
    if not ARQ_SAIDA_CANONICA.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {ARQ_SAIDA_CANONICA}")

    texto = ARQ_SAIDA_CANONICA.read_text(encoding="utf-8")
    linhas_arquivo = texto.splitlines()

    achados: list[dict[str, Any]] = []
    for i, linha in enumerate(linhas_arquivo, start=1):
        achados.extend(_classificar_linha(i, linha))

    df_pontos = _deduplicar_por_linha_classe(pd.DataFrame(achados))
    df_prioridade = _gerar_priorizacao(df_pontos)
    df_guardrails = _gerar_guardrails()

    total_pontos = int(len(df_pontos))
    qtd_por_classe = df_pontos["classe_v17_a4"].value_counts().to_dict() if not df_pontos.empty else {}
    qtd_proibida = int((df_pontos["classe_v17_a4"] == "correcao_funcional_proibida").sum()) if not df_pontos.empty else 0
    qtd_migrar = int((df_pontos["classe_v17_a4"] == "migrar_para_estado_temporal").sum()) if not df_pontos.empty else 0
    qtd_inferencia = int((df_pontos["classe_v17_a4"] == "inferencia_operacional_indevida").sum()) if not df_pontos.empty else 0
    qtd_normalizacao = int((df_pontos["classe_v17_a4"] == "normalizacao_transitoria_aceitavel").sum()) if not df_pontos.empty else 0
    qtd_formatacao = int((df_pontos["classe_v17_a4"] == "formatacao_legitima").sum()) if not df_pontos.empty else 0

    status_global = "ok_diagnostico"
    decisao_v17_funcional = "manter_bloqueio_ate_migrar_pontos_p0_p1"
    if qtd_proibida == 0 and qtd_migrar == 0 and qtd_inferencia == 0:
        decisao_v17_funcional = "sem_bloqueio_de_saida_detectado"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_a4", "valor": status_global, "status": "ok", "observacao": "auditoria diagnostica concluida"},
        {"metrica": "decisao_v17_funcional", "valor": decisao_v17_funcional, "status": "bloqueio_preventivo" if decisao_v17_funcional.startswith("manter") else "ok", "observacao": "V17-A4 nao altera codigo funcional"},
        {"metrica": "linhas_arquivo_saida_canonica", "valor": len(linhas_arquivo), "status": "info", "observacao": str(ARQ_SAIDA_CANONICA.relative_to(RAIZ))},
        {"metrica": "pontos_suspeitos_classificados", "valor": total_pontos, "status": "info", "observacao": "pontos podem ser repeticoes estruturais de um mesmo bloco"},
        {"metrica": "formatacao_legitima", "valor": qtd_formatacao, "status": "ok", "observacao": "permitido se apenas apresentacional"},
        {"metrica": "normalizacao_transitoria_aceitavel", "valor": qtd_normalizacao, "status": "transitorio", "observacao": "aceitavel apenas com guardrail"},
        {"metrica": "inferencia_operacional_indevida", "valor": qtd_inferencia, "status": "bloqueio_preventivo" if qtd_inferencia else "ok", "observacao": "deve ser substituida por estado decidido"},
        {"metrica": "correcao_funcional_proibida", "valor": qtd_proibida, "status": "bloqueio_preventivo" if qtd_proibida else "ok", "observacao": "nao pode permanecer na saida funcional V17"},
        {"metrica": "migrar_para_estado_temporal", "valor": qtd_migrar, "status": "bloqueio_preventivo" if qtd_migrar else "ok", "observacao": "estado/switching/saldo devem ser produzidos antes da saida"},
        {"metrica": "classes_detectadas", "valor": len(qtd_por_classe), "status": "info", "observacao": " | ".join(f"{k}={v}" for k, v in sorted(qtd_por_classe.items()))},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/saida"},
        {"metrica": "confirmacao_sem_alterar_saida_canonica", "valor": True, "status": "ok", "observacao": "saida_canonica.py apenas lido estaticamente"},
    ])

    _gravar_csv(df_pontos, ARQ_PONTOS, [
        "arquivo", "linha", "trecho", "nome_padrao", "classe_v17_a4", "severidade",
        "acao_recomendada", "criterio_classificacao", "altera_codigo",
    ])
    _gravar_csv(df_prioridade, ARQ_PRIORIDADE, [
        "classe_v17_a4", "severidade_maxima", "qtd_pontos", "prioridade", "decisao", "acao_futura",
    ])
    _gravar_csv(df_guardrails, ARQ_GUARDRAILS, ["guardrail", "classe_relacionada", "regra"])
    _gravar_csv(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A4 — AUDITORIA DIAGNOSTICA DA SAIDA CANONICA ===")
    print(f"status_global_v17_a4={status_global}")
    print(f"decisao_v17_funcional={decisao_v17_funcional}")
    print(f"pontos_suspeitos_classificados={total_pontos}")
    print(f"formatacao_legitima={qtd_formatacao}")
    print(f"normalizacao_transitoria_aceitavel={qtd_normalizacao}")
    print(f"inferencia_operacional_indevida={qtd_inferencia}")
    print(f"correcao_funcional_proibida={qtd_proibida}")
    print(f"migrar_para_estado_temporal={qtd_migrar}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    print("confirmacao_sem_alterar_saida_canonica=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

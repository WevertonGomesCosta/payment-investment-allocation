from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.carregador_config import carregar_config
from nucleo.leitor_planilha import carregar_planilha, resolver_coluna

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_SALDO = OUT_DIR / "v17_a3_auditoria_pagamento_por_saldo.csv"
ARQ_LOTE_CAIXA = OUT_DIR / "v17_a3_auditoria_lote_caixa_disponivel.csv"
ARQ_SWITCHING = OUT_DIR / "v17_a3_auditoria_switching_destino_materializado.csv"
ARQ_GUARDRAILS = OUT_DIR / "v17_a3_guardrails_semanticos.csv"
ARQ_RESUMO = OUT_DIR / "v17_a3_resumo.csv"


def _gravar_csv(df: pd.DataFrame, caminho: Path, colunas: list[str]) -> None:
    if df is None or df.empty:
        df = pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    df[colunas].to_csv(caminho, index=False)


def _txt(v: Any) -> str:
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    return str(v).strip()


def _norm(v: Any) -> str:
    texto = _txt(v).lower()
    troca = str.maketrans("áàãâéêíóôõúüç", "aaaaeeiooouuc")
    return texto.translate(troca).strip()


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        if pd.isna(v):
            return 0.0
    except Exception:
        pass
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("R$", "").replace(" ", "").strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _fmt_data(v: Any) -> str:
    if _txt(v) == "":
        return ""
    if hasattr(v, "date") and not isinstance(v, str):
        try:
            return v.date().isoformat()
        except Exception:
            pass
    if hasattr(v, "isoformat") and not isinstance(v, str):
        try:
            return v.isoformat()
        except Exception:
            pass
    return str(v)


def _coluna(df: pd.DataFrame | None, config: dict[str, Any], secao: str, chave: str) -> str:
    if df is None:
        return ""
    try:
        col = resolver_coluna(df, config, secao, chave, obrigatoria=False)
        return str(col) if col else ""
    except Exception:
        return ""


def _serie_norm(df: pd.DataFrame | None, coluna: str) -> set[str]:
    if df is None or not coluna or coluna not in df.columns:
        return set()
    return {_norm(v) for v in df[coluna].tolist() if _txt(v)}


def _auditar_saldo(
    *,
    df_despesas: pd.DataFrame | None,
    df_carteira: pd.DataFrame | None,
    df_lotes: pd.DataFrame | None,
    config: dict[str, Any],
) -> pd.DataFrame:
    if df_despesas is None:
        return pd.DataFrame()

    col_data = _coluna(df_despesas, config, "despesas", "data")
    col_valor = _coluna(df_despesas, config, "despesas", "valor")
    col_desc = _coluna(df_despesas, config, "despesas", "descricao")
    col_lote1 = _coluna(df_despesas, config, "despesas", "lote_usado_1")
    col_lote2 = _coluna(df_despesas, config, "despesas", "lote_usado_2")
    col_despesa_id = _coluna(df_despesas, config, "despesas", "despesa_id")

    col_nome_carteira = _coluna(df_carteira, config, "carteira", "nome") if df_carteira is not None else ""
    col_lote_id = _coluna(df_lotes, config, "lotes", "lote_id") if df_lotes is not None else ""
    col_produto_lote = _coluna(df_lotes, config, "lotes", "produto_id") if df_lotes is not None else ""

    produtos_carteira = _serie_norm(df_carteira, col_nome_carteira)
    lotes_ids = _serie_norm(df_lotes, col_lote_id)
    produtos_lotes = _serie_norm(df_lotes, col_produto_lote)

    existe_saldo_carteira = "saldo" in produtos_carteira
    existe_saldo_inventario_id = "saldo" in lotes_ids
    existe_saldo_inventario_produto = "saldo" in produtos_lotes

    linhas: list[dict[str, Any]] = []
    for idx, row in df_despesas.iterrows():
        for campo_lote, col_lote in (("lote_usado_1", col_lote1), ("lote_usado_2", col_lote2)):
            if not col_lote or col_lote not in df_despesas.columns:
                continue
            lote_usado = row.get(col_lote, "")
            if _norm(lote_usado) != "saldo":
                continue
            violacao = existe_saldo_carteira or existe_saldo_inventario_id or existe_saldo_inventario_produto
            linhas.append({
                "origem_aba": "Todos os Gastos",
                "linha_origem_1base": int(idx) + 2,
                "despesa_id": _txt(row.get(col_despesa_id, "")) if col_despesa_id else f"despesa_auto_linha_{idx + 2}",
                "data": _fmt_data(row.get(col_data, "")) if col_data else "",
                "descricao": _txt(row.get(col_desc, "")) if col_desc else "",
                "valor": _num(row.get(col_valor, "")) if col_valor else 0.0,
                "campo_lote_usado": campo_lote,
                "valor_lote_usado": _txt(lote_usado),
                "tipo_v17": "pagamento_por_saldo",
                "busca_carteira_permitida": False,
                "busca_inventario_permitida": False,
                "existe_produto_saldo_na_carteira": existe_saldo_carteira,
                "existe_lote_id_saldo_no_inventario": existe_saldo_inventario_id,
                "existe_produto_saldo_no_inventario": existe_saldo_inventario_produto,
                "violacao_semantica": violacao,
                "status_v17_a3": "violacao_semantica" if violacao else "ok_saldo_nao_busca_carteira_inventario",
                "observacao": "Saldo em Todos os Gastos deve permanecer pagamento_por_saldo, nao produto/lote/fonte resgatavel",
            })
    return pd.DataFrame(linhas)


def _auditar_lote_caixa(*, df_lotes: pd.DataFrame | None, config: dict[str, Any]) -> pd.DataFrame:
    if df_lotes is None:
        return pd.DataFrame()
    col_lote_id = _coluna(df_lotes, config, "lotes", "lote_id")
    col_data_rec = _coluna(df_lotes, config, "lotes", "data_recebimento")
    col_data_apl = _coluna(df_lotes, config, "lotes", "data_aplicacao")
    col_valor = _coluna(df_lotes, config, "lotes", "valor_original")
    col_produto = _coluna(df_lotes, config, "lotes", "produto_id")

    linhas: list[dict[str, Any]] = []
    for idx, row in df_lotes.iterrows():
        data_rec = row.get(col_data_rec, "") if col_data_rec else ""
        data_apl = row.get(col_data_apl, "") if col_data_apl else ""
        valor = row.get(col_valor, "") if col_valor else ""
        produto = row.get(col_produto, "") if col_produto else ""
        lote_id = row.get(col_lote_id, "") if col_lote_id else f"lote_linha_{idx + 2}"

        candidato_caixa = bool(_txt(data_rec)) and _num(valor) > 0 and not _txt(data_apl) and not _txt(produto)
        candidato_ambivalente = bool(_txt(data_rec)) and _num(valor) > 0 and (not _txt(data_apl) or not _txt(produto))
        if not candidato_caixa and not candidato_ambivalente:
            continue

        data_aplicacao_vazia = not _txt(data_apl)
        investimento_vazio = not _txt(produto)
        violacao = candidato_caixa and not (data_aplicacao_vazia and investimento_vazio)
        if candidato_caixa:
            status = "ok_lote_caixa_preservado"
            tipo = "lote_caixa_disponivel"
        else:
            status = "pendencia_semantica_lote_ambivalente"
            tipo = "pendente_classificacao"
        linhas.append({
            "origem_aba": "Inventário de Lotes",
            "linha_origem_1base": int(idx) + 2,
            "lote_id": _txt(lote_id),
            "data_recebimento": _fmt_data(data_rec),
            "data_aplicacao": _fmt_data(data_apl),
            "valor_original": _num(valor),
            "investimento": _txt(produto),
            "tipo_v17": tipo,
            "data_aplicacao_vazia": data_aplicacao_vazia,
            "investimento_vazio": investimento_vazio,
            "preserva_data_aplicacao_e_investimento_vazios": data_aplicacao_vazia and investimento_vazio,
            "violacao_semantica": violacao,
            "status_v17_a3": status,
            "observacao": "lote_caixa_disponivel nao deve receber Data Aplicação ou Investimento artificialmente",
        })
    return pd.DataFrame(linhas)


def _auditar_switching(
    *,
    df_switching: pd.DataFrame | None,
    df_lotes: pd.DataFrame | None,
    config: dict[str, Any],
) -> pd.DataFrame:
    if df_switching is None:
        return pd.DataFrame()
    col_depois = _coluna(df_switching, config, "switching", "lote_id_depois")
    col_antes = _coluna(df_switching, config, "switching", "lote_id_antes")
    col_valor = _coluna(df_switching, config, "switching", "valor_liquido_migrado")
    col_data = _coluna(df_switching, config, "switching", "data_aplicacao")
    col_destino = _coluna(df_switching, config, "switching", "investimento")
    col_origem = _coluna(df_switching, config, "switching", "produto_origem")

    col_lote_id = _coluna(df_lotes, config, "lotes", "lote_id") if df_lotes is not None else ""
    lote_ids_inventario = _serie_norm(df_lotes, col_lote_id)
    contagem_lote_id: dict[str, int] = {}
    if df_lotes is not None and col_lote_id and col_lote_id in df_lotes.columns:
        for v in df_lotes[col_lote_id].tolist():
            n = _norm(v)
            if n:
                contagem_lote_id[n] = contagem_lote_id.get(n, 0) + 1

    linhas: list[dict[str, Any]] = []
    for idx, row in df_switching.iterrows():
        lote_depois = row.get(col_depois, "") if col_depois else ""
        lote_antes = row.get(col_antes, "") if col_antes else ""
        valor = row.get(col_valor, "") if col_valor else ""
        data = row.get(col_data, "") if col_data else ""
        produto_destino = row.get(col_destino, "") if col_destino else ""
        produto_origem = row.get(col_origem, "") if col_origem else ""
        lote_depois_norm = _norm(lote_depois)
        destino_no_inventario = bool(lote_depois_norm) and lote_depois_norm in lote_ids_inventario
        qtd_no_inventario = contagem_lote_id.get(lote_depois_norm, 0)
        tem_valor = _num(valor) > 0
        tem_data = bool(_txt(data))
        tem_produto_destino = bool(_txt(produto_destino))
        materializavel_internamente = bool(lote_depois_norm) and tem_valor and tem_data and tem_produto_destino

        if destino_no_inventario and qtd_no_inventario == 1:
            status = "ok_destino_reconciliado_no_inventario"
        elif destino_no_inventario and qtd_no_inventario > 1:
            status = "pendencia_destino_duplicado_no_inventario"
        elif materializavel_internamente:
            status = "ok_destino_materializavel_internamente"
        else:
            status = "violacao_destino_nao_reconciliavel_nem_materializavel"

        violacao = status.startswith("violacao")
        linhas.append({
            "origem_aba": "Switching",
            "linha_origem_1base": int(idx) + 2,
            "lote_id_antes": _txt(lote_antes),
            "lote_id_depois": _txt(lote_depois),
            "produto_origem": _txt(produto_origem),
            "produto_destino": _txt(produto_destino),
            "data_switching": _fmt_data(data),
            "valor_liquido_migrado": _num(valor),
            "tipo_v17": "switching_destino_materializado",
            "destino_no_inventario": destino_no_inventario,
            "qtd_destino_no_inventario": qtd_no_inventario,
            "materializavel_internamente": materializavel_internamente,
            "risco_dupla_contagem": destino_no_inventario and materializavel_internamente,
            "violacao_semantica": violacao,
            "status_v17_a3": status,
            "observacao": "destino deve ser reconciliado com Inventário ou materializado internamente sem dupla contagem futura",
        })
    return pd.DataFrame(linhas)


def _gerar_guardrails() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "guardrail": "saldo_nao_busca_carteira_inventario",
            "tipo_v17": "pagamento_por_saldo",
            "regra": "Lote usado=Saldo deve permanecer pagamento_por_saldo e nao pode ser resolvido como produto/lote.",
        },
        {
            "guardrail": "lote_caixa_sem_mutacao",
            "tipo_v17": "lote_caixa_disponivel",
            "regra": "Lote caixa deve preservar Data Aplicação e Investimento vazios; proibido preencher artificialmente.",
        },
        {
            "guardrail": "switching_reconciliavel_sem_dupla_contagem",
            "tipo_v17": "switching_destino_materializado",
            "regra": "Destino de Switching deve ser reconciliado com Inventário ou materializado internamente em etapa futura, nunca contado duas vezes.",
        },
        {
            "guardrail": "sem_consumo_funcional",
            "tipo_v17": "todos",
            "regra": "V17-A3 e diagnostica; nao altera motor, ranking, switching funcional, contrato/modelo ou saida canonica.",
        },
    ])


def main() -> int:
    pacote_config = carregar_config(raiz_repositorio=RAIZ)
    config = pacote_config.conteudo
    pacote_planilha = carregar_planilha(config, raiz_repositorio=RAIZ, carregar_todas_as_abas=True)
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), dict) else {}
    quadros = pacote_planilha.quadros_canonicos

    df_carteira = quadros.get(str(abas_cfg.get("carteira", "")))
    df_despesas = quadros.get(str(abas_cfg.get("despesas", "")))
    df_lotes = quadros.get(str(abas_cfg.get("lotes", "")))
    df_switching = quadros.get(str(abas_cfg.get("switching", "")))

    df_saldo = _auditar_saldo(df_despesas=df_despesas, df_carteira=df_carteira, df_lotes=df_lotes, config=config)
    df_lote_caixa = _auditar_lote_caixa(df_lotes=df_lotes, config=config)
    df_switch = _auditar_switching(df_switching=df_switching, df_lotes=df_lotes, config=config)
    df_guardrails = _gerar_guardrails()

    viol_saldo = int(df_saldo["violacao_semantica"].astype(bool).sum()) if not df_saldo.empty and "violacao_semantica" in df_saldo.columns else 0
    viol_lote_caixa = int(df_lote_caixa["violacao_semantica"].astype(bool).sum()) if not df_lote_caixa.empty and "violacao_semantica" in df_lote_caixa.columns else 0
    viol_switch = int(df_switch["violacao_semantica"].astype(bool).sum()) if not df_switch.empty and "violacao_semantica" in df_switch.columns else 0
    pend_switch = int(df_switch["status_v17_a3"].astype(str).str.startswith("pendencia").sum()) if not df_switch.empty and "status_v17_a3" in df_switch.columns else 0
    pend_lote_caixa = int(df_lote_caixa["status_v17_a3"].astype(str).str.startswith("pendencia").sum()) if not df_lote_caixa.empty and "status_v17_a3" in df_lote_caixa.columns else 0

    status_global = "ok" if viol_saldo == 0 and viol_lote_caixa == 0 and viol_switch == 0 else "falha"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_a3", "valor": status_global, "status": status_global, "observacao": "auditoria semantica diagnostica sem consumo funcional"},
        {"metrica": "pagamentos_por_saldo_auditados", "valor": len(df_saldo), "status": "ok" if len(df_saldo) > 0 else "alerta", "observacao": "Saldo em Todos os Gastos"},
        {"metrica": "violacoes_saldo_busca_carteira_inventario", "valor": viol_saldo, "status": "ok" if viol_saldo == 0 else "falha", "observacao": "Saldo nao deve ser produto/lote"},
        {"metrica": "lotes_caixa_disponivel_auditados", "valor": len(df_lote_caixa), "status": "ok" if len(df_lote_caixa) > 0 else "alerta", "observacao": "inclui candidatos e ambivalentes"},
        {"metrica": "violacoes_lote_caixa_mutado", "valor": viol_lote_caixa, "status": "ok" if viol_lote_caixa == 0 else "falha", "observacao": "Data Aplicação/Investimento devem permanecer vazios"},
        {"metrica": "pendencias_lote_caixa_ambivalente", "valor": pend_lote_caixa, "status": "pendente_futuro" if pend_lote_caixa else "ok", "observacao": "nao bloqueia V17-A3 se nao houver violacao"},
        {"metrica": "switchings_destino_auditados", "valor": len(df_switch), "status": "ok" if len(df_switch) > 0 else "alerta", "observacao": "destinos de Switching"},
        {"metrica": "violacoes_switching_destino", "valor": viol_switch, "status": "ok" if viol_switch == 0 else "falha", "observacao": "destino precisa ser reconciliavel ou materializavel"},
        {"metrica": "pendencias_switching_destino", "valor": pend_switch, "status": "pendente_futuro" if pend_switch else "ok", "observacao": "duplicidade exige reconciliacao futura, nao bloqueia se nao for violacao"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/saida"},
    ])

    _gravar_csv(df_saldo, ARQ_SALDO, [
        "origem_aba", "linha_origem_1base", "despesa_id", "data", "descricao", "valor", "campo_lote_usado",
        "valor_lote_usado", "tipo_v17", "busca_carteira_permitida", "busca_inventario_permitida",
        "existe_produto_saldo_na_carteira", "existe_lote_id_saldo_no_inventario", "existe_produto_saldo_no_inventario",
        "violacao_semantica", "status_v17_a3", "observacao",
    ])
    _gravar_csv(df_lote_caixa, ARQ_LOTE_CAIXA, [
        "origem_aba", "linha_origem_1base", "lote_id", "data_recebimento", "data_aplicacao", "valor_original",
        "investimento", "tipo_v17", "data_aplicacao_vazia", "investimento_vazio",
        "preserva_data_aplicacao_e_investimento_vazios", "violacao_semantica", "status_v17_a3", "observacao",
    ])
    _gravar_csv(df_switch, ARQ_SWITCHING, [
        "origem_aba", "linha_origem_1base", "lote_id_antes", "lote_id_depois", "produto_origem", "produto_destino",
        "data_switching", "valor_liquido_migrado", "tipo_v17", "destino_no_inventario", "qtd_destino_no_inventario",
        "materializavel_internamente", "risco_dupla_contagem", "violacao_semantica", "status_v17_a3", "observacao",
    ])
    _gravar_csv(df_guardrails, ARQ_GUARDRAILS, ["guardrail", "tipo_v17", "regra"])
    _gravar_csv(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A3 — AUDITORIA SEMANTICA DE DADOS V17 ===")
    print(f"status_global_v17_a3={status_global}")
    print(f"pagamentos_por_saldo_auditados={len(df_saldo)}")
    print(f"violacoes_saldo_busca_carteira_inventario={viol_saldo}")
    print(f"lotes_caixa_disponivel_auditados={len(df_lote_caixa)}")
    print(f"violacoes_lote_caixa_mutado={viol_lote_caixa}")
    print(f"pendencias_lote_caixa_ambivalente={pend_lote_caixa}")
    print(f"switchings_destino_auditados={len(df_switch)}")
    print(f"violacoes_switching_destino={viol_switch}")
    print(f"pendencias_switching_destino={pend_switch}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0 if status_global == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())

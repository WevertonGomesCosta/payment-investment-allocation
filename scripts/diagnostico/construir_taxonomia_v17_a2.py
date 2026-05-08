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

OUT_DIR = RAIZ / "saidas" / "diagnostico" / "v17_a2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ARQ_TIPOS = OUT_DIR / "v17_a2_taxonomia_tipos_v17.csv"
ARQ_ADAPTERS = OUT_DIR / "v17_a2_adapters_taxonomia_antiga_para_v17.csv"
ARQ_CLASSIFICACAO = OUT_DIR / "v17_a2_classificacao_dados_v17.csv"
ARQ_PENDENCIAS = OUT_DIR / "v17_a2_pendencias_semanticas.csv"
ARQ_RESUMO = OUT_DIR / "v17_a2_resumo.csv"

TIPOS_V17 = [
    {
        "tipo_v17": "produto_carteira",
        "familia_entrada": "Carteira",
        "aba_key": "carteira",
        "papel_semantico": "produto real elegivel ao universo de carteira",
        "criterio_diagnostico": "linha da aba Carteira com produto/nome reconhecido",
        "usa_motor": False,
    },
    {
        "tipo_v17": "entrada_externa_salario",
        "familia_entrada": "Salários",
        "aba_key": "salarios",
        "papel_semantico": "entrada externa de caixa ainda nao automaticamente disponivel para pagamento/aporte",
        "criterio_diagnostico": "linha da aba Salários com data_recebimento e valor_bruto reconhecidos",
        "usa_motor": False,
    },
    {
        "tipo_v17": "lote_investido",
        "familia_entrada": "Inventário de Lotes",
        "aba_key": "lotes",
        "papel_semantico": "lote aplicado/materializado em produto de investimento",
        "criterio_diagnostico": "Inventário com Investimento preenchido e diferente de marcador de exaustao",
        "usa_motor": False,
    },
    {
        "tipo_v17": "lote_caixa_disponivel",
        "familia_entrada": "Inventário de Lotes",
        "aba_key": "lotes",
        "papel_semantico": "caixa materializado por recebimento e ainda nao aplicado",
        "criterio_diagnostico": "Data Recebimento e Valor Original preenchidos, Data Aplicação e Investimento vazios",
        "usa_motor": False,
    },
    {
        "tipo_v17": "pagamento_por_saldo",
        "familia_entrada": "Todos os Gastos",
        "aba_key": "despesas",
        "papel_semantico": "pagamento historico/operacional feito por caixa/saldo, nao por produto ou lote",
        "criterio_diagnostico": "Lote usado = Saldo em Todos os Gastos",
        "usa_motor": False,
    },
    {
        "tipo_v17": "pagamento_por_lote",
        "familia_entrada": "Todos os Gastos",
        "aba_key": "despesas",
        "papel_semantico": "pagamento associado a lote explicito informado na base",
        "criterio_diagnostico": "Lote usado preenchido e diferente de Saldo",
        "usa_motor": False,
    },
    {
        "tipo_v17": "switching_origem",
        "familia_entrada": "Switching",
        "aba_key": "switching",
        "papel_semantico": "lote/produto de origem de migração interna",
        "criterio_diagnostico": "Lote (ID) Antes ou alias reconhecido na aba Switching",
        "usa_motor": False,
    },
    {
        "tipo_v17": "switching_destino_materializado",
        "familia_entrada": "Switching",
        "aba_key": "switching",
        "papel_semantico": "lote/produto destino materializavel internamente a partir do switching",
        "criterio_diagnostico": "Lote (ID) Depois, Valor Líquido Migrado e produto/data destino reconhecidos",
        "usa_motor": False,
    },
]

ADAPTERS_ANTIGO_V17 = [
    {
        "tipo_antigo": "saldo_disponivel",
        "tipo_v17_alvo": "pagamento_por_saldo",
        "modo_adapter": "contextual_diagnostico",
        "regra_adapter": "quando vier de Todos os Gastos/Lote usado=Saldo, classificar como pagamento_por_saldo; nao tratar como produto ou lote",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "saldo_disponivel_geral",
        "tipo_v17_alvo": "pagamento_por_saldo",
        "modo_adapter": "contextual_diagnostico",
        "regra_adapter": "somente como indicio de caixa operacional; requer contexto antes de virar tipo V17",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "caixa_pre_aplicacao",
        "tipo_v17_alvo": "lote_caixa_disponivel",
        "modo_adapter": "direto_diagnostico",
        "regra_adapter": "mapear para lote_caixa_disponivel quando Data Recebimento/Valor existem e Data Aplicação/Investimento estao vazios",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "lote_resgatavel",
        "tipo_v17_alvo": "lote_investido",
        "modo_adapter": "direto_diagnostico",
        "regra_adapter": "mapear para lote_investido quando houver produto aplicado e lote materializado; elegibilidade de resgate fica fora da V17-A2",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "recebido_disponivel",
        "tipo_v17_alvo": "entrada_externa_salario|lote_caixa_disponivel",
        "modo_adapter": "condicional_diagnostico",
        "regra_adapter": "se vem da aba Salários, classificar como entrada_externa_salario; se vem do Inventário sem aplicação/produto, classificar como lote_caixa_disponivel",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "estado_pos_switching_janela",
        "tipo_v17_alvo": "switching_destino_materializado",
        "modo_adapter": "substituir_por_entrada_canonica_diagnostica",
        "regra_adapter": "na V17, destino deve ser materializado a partir da aba Switching e reconciliado com Inventário, nao criado como estado de janela funcional",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "pos_switch::",
        "tipo_v17_alvo": "switching_destino_materializado",
        "modo_adapter": "substituir_identificador_sintetico_por_tipo_v17",
        "regra_adapter": "identificador sintetico pos_switch:: nao deve ser ID canonico; usar Lote (ID) Depois ou chave diagnostica reconciliavel",
        "usa_motor": False,
    },
    {
        "tipo_antigo": "sem_saldo_temporal_auditavel",
        "tipo_v17_alvo": "",
        "modo_adapter": "nao_e_fonte_v17",
        "regra_adapter": "status terminal de falha apos refactibilizacao; nao deve ser tratado como fonte ou tipo de entrada V17",
        "usa_motor": False,
    },
]

PENDENCIAS_SEMANTICAS_FIXAS = [
    {
        "pendencia": "carteira_liquidez_dias_ausente",
        "tipo_v17_afetado": "produto_carteira",
        "classe": "regra_futura",
        "descricao": "A aba Carteira nao possui liquidez_dias explicita; nao mapear para carencia_dias sem decisao semantica.",
    },
    {
        "pendencia": "salarios_valor_liquido_ausente",
        "tipo_v17_afetado": "entrada_externa_salario",
        "classe": "regra_futura",
        "descricao": "A aba Salários possui valor_bruto, mas nao valor_liquido; nao tratar valor_bruto como liquido sem regra explicita.",
    },
]


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


def _classificar_carteira(df: pd.DataFrame | None, config: dict[str, Any], linhas: list[dict[str, Any]]) -> None:
    if df is None or df.empty:
        return
    col_nome = _coluna(df, config, "carteira", "nome")
    for idx, row in df.iterrows():
        nome = row.get(col_nome, "") if col_nome else ""
        if _txt(nome):
            linhas.append({
                "origem_aba": "Carteira",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": "produto_carteira",
                "id_referencia": _txt(nome),
                "valor_referencia": "",
                "data_referencia": "",
                "classificacao_diagnostica": "produto_carteira_reconhecido",
                "adapter_antigo_relacionado": "",
                "status_v17_a2": "ok_diagnostico",
                "observacao": "classificacao nao consumida pelo motor",
            })


def _classificar_salarios(df: pd.DataFrame | None, config: dict[str, Any], linhas: list[dict[str, Any]], pendencias: list[dict[str, Any]]) -> None:
    if df is None or df.empty:
        return
    col_nome = _coluna(df, config, "salarios", "entrada_id") or _coluna(df, config, "salarios", "descricao")
    col_data = _coluna(df, config, "salarios", "data_recebimento")
    col_bruto = _coluna(df, config, "salarios", "valor_bruto")
    col_liq = _coluna(df, config, "salarios", "valor_liquido")
    if not col_liq:
        pendencias.append({
            "pendencia": "salarios_valor_liquido_ausente_runtime",
            "tipo_v17_afetado": "entrada_externa_salario",
            "classe": "regra_futura",
            "descricao": "valor_liquido nao reconhecido em Salários; V17-A2 usa valor_bruto apenas como referencia diagnostica, nao como regra liquida funcional.",
        })
    for idx, row in df.iterrows():
        identificador = row.get(col_nome, "") if col_nome else f"salario_linha_{idx + 2}"
        valor = row.get(col_liq, "") if col_liq else row.get(col_bruto, "") if col_bruto else ""
        linhas.append({
            "origem_aba": "Salários",
            "linha_origem_1base": int(idx) + 2,
            "tipo_v17": "entrada_externa_salario",
            "id_referencia": _txt(identificador) or f"salario_linha_{idx + 2}",
            "valor_referencia": _num(valor),
            "data_referencia": _fmt_data(row.get(col_data, "")) if col_data else "",
            "classificacao_diagnostica": "entrada_externa_salario_reconhecida",
            "adapter_antigo_relacionado": "recebido_disponivel",
            "status_v17_a2": "ok_diagnostico_com_pendencia_valor_liquido" if not col_liq else "ok_diagnostico",
            "observacao": "nao assume disponibilidade integral nem valor liquido sem regra futura",
        })


def _classificar_despesas(df: pd.DataFrame | None, config: dict[str, Any], linhas: list[dict[str, Any]]) -> None:
    if df is None or df.empty:
        return
    col_id = _coluna(df, config, "despesas", "despesa_id")
    col_data = _coluna(df, config, "despesas", "data")
    col_valor = _coluna(df, config, "despesas", "valor")
    col_lote1 = _coluna(df, config, "despesas", "lote_usado_1")
    col_lote2 = _coluna(df, config, "despesas", "lote_usado_2")
    for idx, row in df.iterrows():
        despesa_id = row.get(col_id, "") if col_id else f"despesa_auto_linha_{idx + 2}"
        valor = row.get(col_valor, "") if col_valor else ""
        data = row.get(col_data, "") if col_data else ""
        lotes = []
        if col_lote1 and _txt(row.get(col_lote1, "")):
            lotes.append((col_lote1, row.get(col_lote1)))
        if col_lote2 and _txt(row.get(col_lote2, "")):
            lotes.append((col_lote2, row.get(col_lote2)))
        for col_lote, lote in lotes:
            if _norm(lote) == "saldo":
                tipo = "pagamento_por_saldo"
                classificacao = "saldo_em_gastos_classificado_como_pagamento_por_saldo"
                adapter = "saldo_disponivel"
                obs = "Saldo nao deve buscar Carteira nem Inventário"
            else:
                tipo = "pagamento_por_lote"
                classificacao = "lote_usado_classificado_como_pagamento_por_lote"
                adapter = "lote_resgatavel"
                obs = "associacao diagnostica; elegibilidade temporal fica fora da V17-A2"
            linhas.append({
                "origem_aba": "Todos os Gastos",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": tipo,
                "id_referencia": _txt(despesa_id),
                "valor_referencia": _num(valor),
                "data_referencia": _fmt_data(data),
                "classificacao_diagnostica": classificacao,
                "adapter_antigo_relacionado": adapter,
                "status_v17_a2": "ok_diagnostico",
                "observacao": f"{obs}; coluna={col_lote}",
            })


def _classificar_lotes(df: pd.DataFrame | None, config: dict[str, Any], linhas: list[dict[str, Any]], pendencias: list[dict[str, Any]]) -> None:
    if df is None or df.empty:
        return
    col_id = _coluna(df, config, "lotes", "lote_id")
    col_data_rec = _coluna(df, config, "lotes", "data_recebimento")
    col_data_apl = _coluna(df, config, "lotes", "data_aplicacao")
    col_valor = _coluna(df, config, "lotes", "valor_original")
    col_prod = _coluna(df, config, "lotes", "produto_id")
    for idx, row in df.iterrows():
        lote_id = row.get(col_id, "") if col_id else f"lote_linha_{idx + 2}"
        produto = row.get(col_prod, "") if col_prod else ""
        data_rec = row.get(col_data_rec, "") if col_data_rec else ""
        data_apl = row.get(col_data_apl, "") if col_data_apl else ""
        valor = row.get(col_valor, "") if col_valor else ""
        produto_norm = _norm(produto)
        tem_produto = bool(_txt(produto)) and produto_norm not in {"-", "—", "--", "–"}
        caixa_candidato = bool(_txt(data_rec)) and _num(valor) > 0 and not _txt(data_apl) and not _txt(produto)
        if tem_produto:
            linhas.append({
                "origem_aba": "Inventário de Lotes",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": "lote_investido",
                "id_referencia": _txt(lote_id),
                "valor_referencia": _num(valor),
                "data_referencia": _fmt_data(data_apl),
                "classificacao_diagnostica": "lote_com_investimento_classificado_como_lote_investido",
                "adapter_antigo_relacionado": "lote_resgatavel",
                "status_v17_a2": "ok_diagnostico",
                "observacao": "nao avalia liquidez/carencia nesta etapa",
            })
        elif caixa_candidato:
            linhas.append({
                "origem_aba": "Inventário de Lotes",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": "lote_caixa_disponivel",
                "id_referencia": _txt(lote_id),
                "valor_referencia": _num(valor),
                "data_referencia": _fmt_data(data_rec),
                "classificacao_diagnostica": "lote_sem_aplicacao_e_sem_investimento_classificado_como_lote_caixa_disponivel",
                "adapter_antigo_relacionado": "caixa_pre_aplicacao|recebido_disponivel",
                "status_v17_a2": "ok_diagnostico",
                "observacao": "proibido preencher Data Aplicação artificialmente",
            })
        elif produto_norm in {"-", "—", "--", "–"}:
            pendencias.append({
                "pendencia": "lote_exaurido_marcador_antigo",
                "tipo_v17_afetado": "lote_investido|lote_caixa_disponivel",
                "classe": "fora_fonte_ativa_v17",
                "descricao": f"Linha {idx + 2} do Inventário usa marcador de lote exaurido; nao deve voltar como fonte ativa V17 sem regra explicita.",
            })


def _classificar_switching(df: pd.DataFrame | None, config: dict[str, Any], linhas: list[dict[str, Any]]) -> None:
    if df is None or df.empty:
        return
    col_antes = _coluna(df, config, "switching", "lote_id_antes")
    col_depois = _coluna(df, config, "switching", "lote_id_depois")
    col_data = _coluna(df, config, "switching", "data_aplicacao")
    col_valor = _coluna(df, config, "switching", "valor_liquido_migrado")
    col_destino = _coluna(df, config, "switching", "investimento")
    col_origem = _coluna(df, config, "switching", "produto_origem")
    for idx, row in df.iterrows():
        valor = row.get(col_valor, "") if col_valor else ""
        data = row.get(col_data, "") if col_data else ""
        lote_antes = row.get(col_antes, "") if col_antes else ""
        lote_depois = row.get(col_depois, "") if col_depois else ""
        produto_origem = row.get(col_origem, "") if col_origem else ""
        produto_destino = row.get(col_destino, "") if col_destino else ""
        if _txt(lote_antes):
            linhas.append({
                "origem_aba": "Switching",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": "switching_origem",
                "id_referencia": _txt(lote_antes),
                "valor_referencia": _num(valor),
                "data_referencia": _fmt_data(data),
                "classificacao_diagnostica": "lote_origem_switching_reconhecido",
                "adapter_antigo_relacionado": "estado_pos_switching_janela",
                "status_v17_a2": "ok_diagnostico",
                "observacao": f"produto_origem={_txt(produto_origem)}; sem execucao funcional",
            })
        if _txt(lote_depois):
            linhas.append({
                "origem_aba": "Switching",
                "linha_origem_1base": int(idx) + 2,
                "tipo_v17": "switching_destino_materializado",
                "id_referencia": _txt(lote_depois),
                "valor_referencia": _num(valor),
                "data_referencia": _fmt_data(data),
                "classificacao_diagnostica": "lote_destino_switching_materializavel_diagnosticamente",
                "adapter_antigo_relacionado": "pos_switch::|estado_pos_switching_janela",
                "status_v17_a2": "ok_diagnostico",
                "observacao": f"produto_destino={_txt(produto_destino)}; requer reconciliacao futura com Inventário",
            })


def main() -> int:
    pacote_config = carregar_config(raiz_repositorio=RAIZ)
    config = pacote_config.conteudo
    pacote_planilha = carregar_planilha(config, raiz_repositorio=RAIZ, carregar_todas_as_abas=True)
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), dict) else {}
    quadros = pacote_planilha.quadros_canonicos

    linhas_classificacao: list[dict[str, Any]] = []
    pendencias: list[dict[str, Any]] = list(PENDENCIAS_SEMANTICAS_FIXAS)

    _classificar_carteira(quadros.get(str(abas_cfg.get("carteira", ""))), config, linhas_classificacao)
    _classificar_salarios(quadros.get(str(abas_cfg.get("salarios", ""))), config, linhas_classificacao, pendencias)
    _classificar_despesas(quadros.get(str(abas_cfg.get("despesas", ""))), config, linhas_classificacao)
    _classificar_lotes(quadros.get(str(abas_cfg.get("lotes", ""))), config, linhas_classificacao, pendencias)
    _classificar_switching(quadros.get(str(abas_cfg.get("switching", ""))), config, linhas_classificacao)

    df_tipos = pd.DataFrame(TIPOS_V17)
    df_adapters = pd.DataFrame(ADAPTERS_ANTIGO_V17)
    df_classificacao = pd.DataFrame(linhas_classificacao)
    df_pendencias = pd.DataFrame(pendencias)

    tipos_observados = set(df_classificacao["tipo_v17"].dropna().astype(str).unique()) if not df_classificacao.empty else set()
    tipos_definidos = {d["tipo_v17"] for d in TIPOS_V17}
    tipos_sem_observacao = sorted(tipos_definidos - tipos_observados)
    adapters_com_alvo_v17 = int((df_adapters["tipo_v17_alvo"].astype(str).str.strip() != "").sum()) if not df_adapters.empty else 0
    status_global = "ok" if tipos_definidos.issuperset(tipos_observados) and adapters_com_alvo_v17 >= 7 else "falha"

    resumo = pd.DataFrame([
        {"metrica": "status_global_v17_a2", "valor": status_global, "status": status_global, "observacao": "taxonomia/adapters diagnosticos sem consumo funcional"},
        {"metrica": "tipos_v17_definidos", "valor": len(tipos_definidos), "status": "ok", "observacao": "tipos previstos pela V17"},
        {"metrica": "tipos_v17_observados_nos_dados", "valor": len(tipos_observados), "status": "info", "observacao": "tipos encontrados na planilha atual"},
        {"metrica": "tipos_v17_sem_observacao_na_base_atual", "valor": len(tipos_sem_observacao), "status": "info", "observacao": " | ".join(tipos_sem_observacao)},
        {"metrica": "linhas_classificadas_v17", "valor": len(df_classificacao), "status": "info", "observacao": "classificacao diagnostica"},
        {"metrica": "adapters_antigo_v17_definidos", "valor": len(df_adapters), "status": "ok", "observacao": "inclui um status antigo nao mapeavel como fonte"},
        {"metrica": "adapters_com_tipo_v17_alvo", "valor": adapters_com_alvo_v17, "status": "ok" if adapters_com_alvo_v17 >= 7 else "falha", "observacao": "sem_saldo_temporal_auditavel nao e fonte V17"},
        {"metrica": "pendencias_semanticas_registradas", "valor": len(df_pendencias), "status": "pendente_futuro", "observacao": "nao bloqueia V17-A2 diagnostica"},
        {"metrica": "confirmacao_sem_alterar_motor", "valor": True, "status": "ok", "observacao": "script diagnostico isolado"},
        {"metrica": "confirmacao_sem_alterar_contrato_modelo", "valor": True, "status": "ok", "observacao": "sem edicao documental normativa"},
        {"metrica": "confirmacao_sem_alterar_ranking_saida_switching_funcional", "valor": True, "status": "ok", "observacao": "sem consumo por motor/ranking/saida"},
    ])

    _gravar_csv(df_tipos, ARQ_TIPOS, ["tipo_v17", "familia_entrada", "aba_key", "papel_semantico", "criterio_diagnostico", "usa_motor"])
    _gravar_csv(df_adapters, ARQ_ADAPTERS, ["tipo_antigo", "tipo_v17_alvo", "modo_adapter", "regra_adapter", "usa_motor"])
    _gravar_csv(df_classificacao, ARQ_CLASSIFICACAO, [
        "origem_aba", "linha_origem_1base", "tipo_v17", "id_referencia", "valor_referencia",
        "data_referencia", "classificacao_diagnostica", "adapter_antigo_relacionado", "status_v17_a2", "observacao",
    ])
    _gravar_csv(df_pendencias, ARQ_PENDENCIAS, ["pendencia", "tipo_v17_afetado", "classe", "descricao"])
    _gravar_csv(resumo, ARQ_RESUMO, ["metrica", "valor", "status", "observacao"])

    print("=== V17-A2 — TAXONOMIA V17 E ADAPTERS NAO FUNCIONAIS ===")
    print(f"status_global_v17_a2={status_global}")
    print(f"tipos_v17_definidos={len(tipos_definidos)}")
    print(f"tipos_v17_observados_nos_dados={len(tipos_observados)}")
    print(f"linhas_classificadas_v17={len(df_classificacao)}")
    print(f"adapters_antigo_v17_definidos={len(df_adapters)}")
    print(f"adapters_com_tipo_v17_alvo={adapters_com_alvo_v17}")
    print(f"pendencias_semanticas_registradas={len(df_pendencias)}")
    print(f"output_dir={OUT_DIR}")
    print("confirmacao_sem_alterar_motor=true")
    print("confirmacao_sem_alterar_contrato_modelo=true")
    print("confirmacao_sem_alterar_ranking_saida_switching_funcional=true")
    return 0 if status_global == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())

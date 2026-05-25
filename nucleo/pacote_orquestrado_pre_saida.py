from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

PENDENTE_AMBIGUO = "pendente_ambigua_v17_c2"
PENDENTE_ESTADO = "pendente_estado_temporal_futuro_v17_c2"
PENDENTE_AUSENTE = "pendente_fonte_ausente_v17_c2"

TIPOS_V17_POR_FONTE_ANTIGA = {
    "lote_resgatavel": "lote_investido",
    "lote_aportado": "lote_investido",
    "lote_investido": "lote_investido",
    "recebido_disponivel": "entrada_externa_salario",
    "caixa_pre_aplicacao": "lote_caixa_disponivel",
    "saldo": "pagamento_por_saldo",
    "saldo_disponivel": "pagamento_por_saldo",
    "pagamento_por_saldo": "pagamento_por_saldo",
    "switching_destino": "switching_destino_materializado",
}

FAMILIA_POR_TIPO_V17 = {
    "lote_investido": "Inventário de Lotes",
    "entrada_externa_salario": "Salários",
    "lote_caixa_disponivel": "Inventário de Lotes",
    "pagamento_por_saldo": "Todos os Gastos",
    "switching_destino_materializado": "Switching",
}


@dataclass(slots=True)
class PacoteOrquestradoPreSaida:
    versao: str = "V17-C2"
    recomendacoes_futuras: pd.DataFrame = field(default_factory=pd.DataFrame)
    decisoes_pagamento: pd.DataFrame = field(default_factory=pd.DataFrame)
    fontes_pagamento_v17: pd.DataFrame = field(default_factory=pd.DataFrame)
    estado_temporal_switching: pd.DataFrame = field(default_factory=pd.DataFrame)
    saldos_financeiros_lotes: pd.DataFrame = field(default_factory=pd.DataFrame)
    ranking_informativo: pd.DataFrame = field(default_factory=pd.DataFrame)
    auditoria_orquestracao: pd.DataFrame = field(default_factory=pd.DataFrame)
    resumo: dict[str, Any] = field(default_factory=dict)


def _norm(v: Any) -> str:
    return str(v or "").strip().lower()


def _as_df(obj: Any) -> pd.DataFrame:
    return obj.copy() if isinstance(obj, pd.DataFrame) else pd.DataFrame()


def _first_df(obj: Any, attrs: list[str]) -> tuple[pd.DataFrame, str]:
    if obj is None:
        return pd.DataFrame(), ""
    for attr in attrs:
        q = getattr(obj, attr, None)
        if isinstance(q, pd.DataFrame) and len(q):
            return q.copy(), attr
    return pd.DataFrame(), ""


def _col(df: pd.DataFrame, aliases: list[str]) -> str:
    if df.empty:
        return ""
    mapa = {_norm(c): c for c in df.columns}
    for a in aliases:
        achado = mapa.get(_norm(a))
        if achado is not None:
            return achado
    return ""


def _get(row: pd.Series | dict[str, Any] | None, col: str, padrao: Any = "") -> Any:
    if row is None:
        return padrao
    if col:
        try:
            if col in row.index:  # type: ignore[attr-defined]
                valor = row.get(col)  # type: ignore[call-arg]
                if valor is not None and not (isinstance(valor, str) and valor.strip() == ""):
                    return valor
        except Exception:
            if isinstance(row, dict) and col in row and row[col] not in (None, ""):
                return row[col]
    return padrao


def _valor(row: pd.Series, df: pd.DataFrame, aliases: list[str], padrao: Any = "") -> Any:
    return _get(row, _col(df, aliases), padrao)


def _valor_multi(fontes: list[tuple[pd.Series | dict[str, Any] | None, pd.DataFrame]], aliases: list[str], padrao: Any = "") -> Any:
    for row, df in fontes:
        if row is None or df is None or df.empty:
            continue
        col = _col(df, aliases)
        valor = _get(row, col, None)
        if valor not in (None, ""):
            return valor
    return padrao


def _mapa_por_pagamento(df: pd.DataFrame) -> dict[str, pd.Series]:
    if df is None or df.empty:
        return {}
    col_pid = _col(df, ["pagamento_id", "despesa_id", "Despesa ID", "id"])
    if not col_pid:
        return {}
    mapa: dict[str, pd.Series] = {}
    for _, row in df.iterrows():
        pid = str(row.get(col_pid) or "").strip()
        if pid and pid not in mapa:
            mapa[pid] = row
    return mapa


def _records(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=colunas)
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df[colunas].copy()


def _quadro_recomendacoes(contexto: Any) -> tuple[pd.DataFrame, str]:
    decisao = getattr(contexto, "decisao_local_v1", None)
    df, origem = _first_df(decisao, ["quadro_decisao_local_v1", "quadro_decisoes", "quadro_recomendacoes"])
    if len(df):
        return df, f"decisao_local_v1.{origem}"
    return pd.DataFrame(), "ausente"


def _quadro_recomputacao(contexto: Any) -> tuple[pd.DataFrame, str]:
    recomputacao = getattr(contexto, "recomputacao_sequencial_central_v1", None)
    df, origem = _first_df(recomputacao, ["quadro_recomputacao_sequencial_central"])
    if len(df):
        return df, f"recomputacao_sequencial_central_v1.{origem}"
    return pd.DataFrame(), "ausente"


def _montar_recomendacoes_futuras(contexto: Any) -> pd.DataFrame:
    df, origem = _quadro_recomendacoes(contexto)
    if df.empty:
        return pd.DataFrame(columns=["pagamento_id", "data_pagamento", "conta_descricao", "valor_pagamento", "status_recomendacao", "motivo_bloqueio", "pacote_do_dia", "necessita_switching", "fonte_verdade_origem"])
    linhas = []
    for i, row in df.iterrows():
        linhas.append({
            "pagamento_id": _valor(row, df, ["pagamento_id", "despesa_id", "Despesa ID", "id"], f"pagamento_auto_{i}"),
            "data_pagamento": _valor(row, df, ["data_pagamento", "Data", "data"], ""),
            "conta_descricao": _valor(row, df, ["conta", "Conta", "descricao_pagamento", "descricao", "Descrição", "descrição"], ""),
            "valor_pagamento": _valor(row, df, ["valor_pagamento", "Valor", "valor"], ""),
            "status_recomendacao": _valor(row, df, ["status_recomendacao", "Status recomendação", "Status recomendacao", "status", "status_central"], ""),
            "motivo_bloqueio": _valor(row, df, ["motivo_bloqueio", "Motivo bloqueio lote", "observacao_central", "motivo"], ""),
            "pacote_do_dia": _valor(row, df, ["pacote_do_dia", "Pacote do dia", "Estratégia", "estrategia", "criterio_central"], ""),
            "necessita_switching": _valor(row, df, ["necessita_switching", "Necessita switching"], ""),
            "fonte_verdade_origem": origem,
        })
    return pd.DataFrame(linhas)


def _montar_decisoes_pagamento(contexto: Any) -> pd.DataFrame:
    decisao = getattr(contexto, "decisao_local_v1", None)
    df, origem = _first_df(decisao, ["quadro_decisao_local_v1", "quadro_decisoes", "quadro_recomendacoes"])
    if df.empty:
        df, origem = _quadro_recomendacoes(contexto)
    if df.empty:
        return pd.DataFrame(columns=["pagamento_id", "tipo_fonte_escolhida_v17", "fonte_id", "valor_bruto_resgate", "valor_imposto", "valor_liquido_resgate", "saldo_antes", "saldo_depois", "status_decisao"])

    df_recomp, _ = _quadro_recomputacao(contexto)
    df_recomendacoes, _ = _quadro_recomendacoes(contexto)
    mapa_recomp = _mapa_por_pagamento(df_recomp)
    mapa_recomendacoes = _mapa_por_pagamento(df_recomendacoes)

    linhas = []
    for i, row in df.iterrows():
        pagamento_id = _valor(row, df, ["pagamento_id", "despesa_id", "Despesa ID", "id"], f"pagamento_auto_{i}")
        pid = str(pagamento_id or "").strip()
        row_recomp = mapa_recomp.get(pid)
        row_recomendacao = mapa_recomendacoes.get(pid)
        fontes = [(row, df), (row_recomp, df_recomp), (row_recomendacao, df_recomendacoes)]
        tipo_antigo = _norm(_valor_multi(fontes, ["tipo_fonte_escolhida", "tipo_fonte", "tipo_fonte_candidata", "tipo_fonte_final"], ""))
        tipo_v17 = TIPOS_V17_POR_FONTE_ANTIGA.get(tipo_antigo, tipo_antigo or PENDENTE_AMBIGUO)
        linhas.append({
            "pagamento_id": pagamento_id,
            "tipo_fonte_escolhida_v17": tipo_v17,
            "fonte_id": _valor_multi(fontes, ["fonte_id", "fonte_final_id", "lote_id", "lote_escolhido", "lote_final_central", "Lote sugerido", "lote"], ""),
            "valor_bruto_resgate": _valor_multi(fontes, ["valor_bruto_resgate", "bruto_central", "Bruto", "bruto"], PENDENTE_AMBIGUO),
            "valor_imposto": _valor_multi(fontes, ["valor_imposto", "imposto_central", "Imposto", "IR", "imposto"], PENDENTE_AMBIGUO),
            "valor_liquido_resgate": _valor_multi(fontes, ["valor_liquido_resgate", "liquido_central", "Líquido", "Liquido", "liquido"], PENDENTE_AMBIGUO),
            "saldo_antes": PENDENTE_ESTADO,
            "saldo_depois": PENDENTE_ESTADO,
            "status_decisao": _valor_multi(fontes, ["status_decisao", "status_central", "status", "Status recomendação", "Status recomendacao"], ""),
        })
    return pd.DataFrame(linhas)


def _montar_fontes_pagamento_v17(contexto: Any) -> pd.DataFrame:
    pacote = getattr(contexto, "fontes_elegiveis_pagamento", None)
    df, origem = _first_df(pacote, ["quadro_fontes_elegiveis", "quadro_fontes"])
    if df.empty:
        return pd.DataFrame(columns=["fonte_id", "tipo_v17", "familia_entrada", "data_materializacao", "valor_disponivel_bruto", "valor_disponivel_liquido", "status_elegibilidade"])
    linhas = []
    for i, row in df.iterrows():
        tipo_antigo = _norm(_valor(row, df, ["tipo_fonte", "tipo_fonte_escolhida", "tipo"], ""))
        tipo_v17 = TIPOS_V17_POR_FONTE_ANTIGA.get(tipo_antigo, tipo_antigo or PENDENTE_AMBIGUO)
        fonte_id = _valor(row, df, ["fonte_id", "lote_id", "recebido_id", "pagamento_id"], f"fonte_auto_{i}")
        linhas.append({
            "fonte_id": fonte_id,
            "tipo_v17": tipo_v17,
            "familia_entrada": FAMILIA_POR_TIPO_V17.get(tipo_v17, PENDENTE_AMBIGUO),
            "data_materializacao": _valor(row, df, ["data_materializacao", "data_recebimento", "data_lote", "data_aplicacao", "data_pagamento"], ""),
            "valor_disponivel_bruto": _valor(row, df, ["valor_bruto_disponivel", "valor_original", "valor"], PENDENTE_AMBIGUO),
            "valor_disponivel_liquido": _valor(row, df, ["valor_liquido_disponivel", "valor_liquido"], PENDENTE_ESTADO),
            "status_elegibilidade": _valor(row, df, ["elegivel_na_data_pagamento", "status_elegibilidade", "status"], ""),
        })
    return pd.DataFrame(linhas)


def _montar_estado_temporal_switching(contexto: Any) -> pd.DataFrame:
    pacote_planilha = getattr(contexto, "pacote_planilha", None)
    config = getattr(getattr(contexto, "pacote_config", None), "conteudo", {}) or {}
    aba = ((config.get("abas") or {}).get("switching") if isinstance(config, dict) else None) or "Switching"
    quadros = getattr(pacote_planilha, "quadros_canonicos", {}) if pacote_planilha is not None else {}
    df = quadros.get(str(aba)) if isinstance(quadros, dict) else None
    df = _as_df(df)
    if df.empty:
        return pd.DataFrame(columns=["switching_id", "lote_id_origem", "lote_id_destino", "data_switching", "produto_destino", "valor_liquido_migrado", "status_reconciliacao"])
    linhas = []
    for i, row in df.iterrows():
        destino = _valor(row, df, ["lote_id_depois", "Lote (ID) Depois", "lote depois", "lote_destino"], "")
        linhas.append({
            "switching_id": _valor(row, df, ["switching_id", "id"], f"switching_auto_{i}"),
            "lote_id_origem": _valor(row, df, ["lote_id_antes", "Lote (ID) Antes", "lote antes", "lote_origem"], ""),
            "lote_id_destino": destino,
            "data_switching": _valor(row, df, ["data_aplicacao", "Data Aplicação", "data_switching", "Data"], ""),
            "produto_destino": _valor(row, df, ["investimento", "Investimento", "Produto destino switching", "produto_destino"], ""),
            "valor_liquido_migrado": _valor(row, df, ["valor_liquido_migrado", "Valor Líquido Migrado", "Valor líquido migrado"], ""),
            "status_reconciliacao": "materializavel_diagnostico_v17_c2" if str(destino or "").strip() else PENDENTE_AUSENTE,
        })
    return pd.DataFrame(linhas)


def _montar_saldos_financeiros_lotes(contexto: Any) -> pd.DataFrame:
    replay = getattr(contexto, "replay_passado", None)
    lotes = getattr(replay, "lotes_apos_replay", []) if replay is not None else []
    data_ref = getattr(getattr(contexto, "execucao", None), "data_referencia", "")
    linhas = []
    for lote in lotes:
        linhas.append({
            "fonte_id": str(getattr(lote, "id", "")),
            "data_referencia": data_ref,
            "saldo_bruto": PENDENTE_ESTADO,
            "imposto_estimado": PENDENTE_ESTADO,
            "saldo_liquido": PENDENTE_ESTADO,
            "principal_remanescente": getattr(lote, "principal_remanescente", PENDENTE_AMBIGUO),
            "status_lote": "ativo" if float(getattr(lote, "principal_remanescente", 0.0) or 0.0) > 0 else "exaurido",
        })
    return pd.DataFrame(linhas)


def _montar_ranking_informativo(contexto: Any) -> pd.DataFrame:
    ranking = getattr(contexto, "ranking_carteira", None)
    df, origem = _first_df(ranking, ["top30", "quadro_ranking"])
    if df.empty:
        return pd.DataFrame(columns=["produto_id", "posicao_ranking", "score", "uso_permitido"])
    linhas = []
    for i, row in df.iterrows():
        linhas.append({
            "produto_id": _valor(row, df, ["produto_key", "Nome", "nome", "Produto"], f"produto_auto_{i}"),
            "posicao_ranking": _valor(row, df, ["Rank_Consolidado_Prazo_Ativos", "rank_destino", "posicao_ranking"], ""),
            "score": _valor(row, df, ["Score Final Prazo", "SAOF_Final_Prazo", "score_final", "score"], ""),
            "uso_permitido": "informativo",
        })
    return pd.DataFrame(linhas)


def _auditoria_componentes(componentes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    linhas = []
    for nome, df in componentes.items():
        texto = df.astype(str) if isinstance(df, pd.DataFrame) and len(df) else pd.DataFrame()
        pend_amb = int(texto.apply(lambda s: s.str.contains(PENDENTE_AMBIGUO, na=False)).sum().sum()) if len(texto) else 0
        pend_estado = int(texto.apply(lambda s: s.str.contains(PENDENTE_ESTADO, na=False)).sum().sum()) if len(texto) else 0
        pend_ausente = int(texto.apply(lambda s: s.str.contains(PENDENTE_AUSENTE, na=False)).sum().sum()) if len(texto) else 0
        linhas.append({
            "componente": nome,
            "origem_funcional": "montador_v17_c2",
            "status_orquestracao": "ok_com_pendencias" if (pend_amb + pend_estado + pend_ausente) else "ok",
            "linhas": int(len(df)) if isinstance(df, pd.DataFrame) else 0,
            "pendencias_ambiguas": pend_amb,
            "pendencias_estado_temporal": pend_estado,
            "pendencias_ausentes": pend_ausente,
            "mensagem_auditoria": "V17-C2 reduz pendencias seguras e preserva pendencias de estado temporal sem inventar valor",
        })
    return pd.DataFrame(linhas)


def montar_pacote_orquestrado_pre_saida(contexto: Any) -> PacoteOrquestradoPreSaida:
    componentes = {
        "recomendacoes_futuras": _montar_recomendacoes_futuras(contexto),
        "decisoes_pagamento": _montar_decisoes_pagamento(contexto),
        "fontes_pagamento_v17": _montar_fontes_pagamento_v17(contexto),
        "estado_temporal_switching": _montar_estado_temporal_switching(contexto),
        "saldos_financeiros_lotes": _montar_saldos_financeiros_lotes(contexto),
        "ranking_informativo": _montar_ranking_informativo(contexto),
    }
    auditoria = _auditoria_componentes(componentes)
    resumo = {
        "versao": "V17-C2",
        "componentes": len(componentes),
        "linhas_total": int(sum(len(df) for df in componentes.values())),
        "pendencias_ambiguas": int(auditoria["pendencias_ambiguas"].sum()) if len(auditoria) else 0,
        "pendencias_estado_temporal": int(auditoria["pendencias_estado_temporal"].sum()) if len(auditoria) else 0,
        "pendencias_ausentes": int(auditoria["pendencias_ausentes"].sum()) if len(auditoria) else 0,
        "consumido_por_saida_canonica": False,
        "altera_motor": False,
    }
    return PacoteOrquestradoPreSaida(
        versao="V17-C2",
        recomendacoes_futuras=componentes["recomendacoes_futuras"],
        decisoes_pagamento=componentes["decisoes_pagamento"],
        fontes_pagamento_v17=componentes["fontes_pagamento_v17"],
        estado_temporal_switching=componentes["estado_temporal_switching"],
        saldos_financeiros_lotes=componentes["saldos_financeiros_lotes"],
        ranking_informativo=componentes["ranking_informativo"],
        auditoria_orquestracao=auditoria,
        resumo=resumo,
    )

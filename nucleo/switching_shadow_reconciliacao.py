"""Camada canônica e reconciliatória do bloco 06 (switching shadow).

Este módulo abre apenas a metade técnica do bloco 06, limitada a:
- normalização shadow dos lotes observados;
- construção de índice canônico de lotes;
- projeção de eventos brutos de aporte histórico;
- reconciliação observado/legado vs shadow;
- consolidação e ordenação determinística da trilha técnica de eventos.

Ele não implementa ainda:
- replay shadow de contas pagas;
- relatório econômico;
- cálculo líquido/fiscal;
- diagnóstico econômico de switching.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from nucleo.carteira_canonica import PacoteCarteiraCanonica
from nucleo.dados_operacionais_canonicos import PacoteDadosOperacionaisCanonicos
from nucleo.utilitarios_neutros import arredondar_monetario, normalizar_identificador, para_data, para_float_monetario, para_int


@dataclass(slots=True)
class PacoteSwitchingShadowReconciliacao:
    lotes_shadow: pd.DataFrame
    indice_lotes: dict[str, Any]
    eventos_aporte_shadow: pd.DataFrame
    eventos_financeiros_brutos: pd.DataFrame
    eventos_financeiros_ordenados: pd.DataFrame
    auditoria_lotes_shadow: dict[str, Any]
    auditoria_eventos_aporte: dict[str, Any]
    reconciliacao_aportes: dict[str, Any]



def gerar_lote_tecnico_id(lote_id: Any, ordem_planilha_lote: Any, *, prefixo: str = "obs") -> str:
    lote_id_norm = normalizar_identificador(lote_id) or "sem_lote_id"
    ordem = para_int(ordem_planilha_lote, 0)
    ordem_txt = str(ordem) if ordem > 0 else "sem_ordem"
    return f"{prefixo}::{lote_id_norm}::{ordem_txt}"



def gerar_switch_grupo_id(lote_tecnico_id: Any, produto_destino_key: Any, data_evento: Any, ordem_switch: int = 1) -> str:
    lote_tecnico = normalizar_identificador(lote_tecnico_id) or "sem_origem"
    produto_destino = normalizar_identificador(produto_destino_key) or "sem_destino"
    data_norm = para_data(data_evento)
    data_txt = data_norm.isoformat() if data_norm is not None else "sem_data"
    return f"swgrp::{lote_tecnico}::{produto_destino}::{data_txt}::{int(ordem_switch)}"



def normalizar_lotes_shadow(
    inventario_canonico: pd.DataFrame,
    carteira_canonica: PacoteCarteiraCanonica | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    auditoria = {
        "qtd_lotes_shadow": 0,
        "qtd_produto_reconhecido": 0,
        "qtd_caixa_disponivel": 0,
        "qtd_caixa_futuro": 0,
        "qtd_caixa_exaurido": 0,
        "qtd_produto_nao_reconhecido": 0,
        "qtd_data_base_fiscal_inferida": 0,
        "qtd_ids_duplicados": 0,
        "qtd_lote_tecnico_duplicado": 0,
        "linhas_descartadas": [],
        "resumo_tipos_lote": {},
    }

    if inventario_canonico is None or len(inventario_canonico) == 0:
        return pd.DataFrame([]), auditoria

    registros: list[dict[str, Any]] = []
    for idx, row in inventario_canonico.iterrows():
        lote_id = normalizar_identificador(row.get("lote_id"))
        data_aplicacao = para_data(row.get("data_aplicacao"))
        valor_original = para_float_monetario(row.get("valor_original"), 0.0)
        if not lote_id:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "lote_id_vazio"})
            continue
        if data_aplicacao is None:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "data_aplicacao_invalida", "lote_id": lote_id})
            continue
        if valor_original <= 0:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "valor_original_nao_positivo", "lote_id": lote_id})
            continue

        ordem_planilha_lote = para_int(row.get("ordem_planilha_lote"), idx + 1)
        lote_tecnico_id = gerar_lote_tecnico_id(lote_id, ordem_planilha_lote, prefixo="obs")
        situacao_investimento = str(row.get("situacao_investimento") or "").strip()
        produto_encontrado = bool(row.get("produto_encontrado", False))

        if situacao_investimento == "aportado" and produto_encontrado:
            tipo_lote = "produto_observado"
            auditoria["qtd_produto_reconhecido"] += 1
        elif situacao_investimento == "aportado" and not produto_encontrado:
            tipo_lote = "produto_nao_reconhecido"
            auditoria["qtd_produto_nao_reconhecido"] += 1
        elif situacao_investimento == "nao_aportado_disponivel":
            tipo_lote = "caixa_disponivel"
            auditoria["qtd_caixa_disponivel"] += 1
        elif situacao_investimento == "recebido_futuro_nao_disponivel":
            tipo_lote = "caixa_futuro"
            auditoria["qtd_caixa_futuro"] += 1
        elif situacao_investimento == "nao_aportado_exaurido":
            tipo_lote = "caixa_exaurido"
            auditoria["qtd_caixa_exaurido"] += 1
        else:
            tipo_lote = "nao_classificado"

        data_base_fiscal = para_data(row.get("data_base_fiscal")) or data_aplicacao
        if bool(row.get("data_base_fiscal_inferida", False)):
            auditoria["qtd_data_base_fiscal_inferida"] += 1

        status_lote = str(row.get("status_lote_informado") or "").strip() or "ativo_observado"
        registros.append({
            "lote_id": lote_id,
            "lote_id_raw": str(row.get("lote_id_raw") or lote_id),
            "lote_tecnico_id": lote_tecnico_id,
            "ordem_planilha_lote": ordem_planilha_lote,
            "data_aplicacao": data_aplicacao,
            "data_base_fiscal": data_base_fiscal,
            "data_base_fiscal_inferida": bool(row.get("data_base_fiscal_inferida", False)),
            "valor_original": float(valor_original),
            "principal_remanescente_inicial": float(valor_original),
            "saldo_bruto_inicial": float(valor_original),
            "saldo_liquido_inicial": float(valor_original),
            "investimento_bruto": str(row.get("investimento_bruto") or ""),
            "produto_key": row.get("produto_key"),
            "produto_nome": row.get("produto_nome_canonico") or row.get("produto_informado") or None,
            "produto_nome_norm": row.get("produto_nome_norm"),
            "produto_encontrado": produto_encontrado,
            "tipo_match_produto": row.get("tipo_match_produto") or "vazio",
            "tipo_lote": tipo_lote,
            "situacao_investimento": situacao_investimento,
            "status_lote": status_lote,
            "origem_registro": row.get("origem_registro") or "inventario_lotes",
            "eh_lote_observado": True,
            "eh_aporte_historico": True,
        })

    quadro = pd.DataFrame(registros)
    auditoria["qtd_lotes_shadow"] = int(len(quadro))
    if len(quadro) > 0:
        auditoria["qtd_ids_duplicados"] = int(quadro["lote_id"].duplicated().sum())
        auditoria["qtd_lote_tecnico_duplicado"] = int(quadro["lote_tecnico_id"].duplicated().sum())
        auditoria["resumo_tipos_lote"] = {
            str(chave): int(valor)
            for chave, valor in quadro["tipo_lote"].value_counts(dropna=False).to_dict().items()
        }
    return quadro, auditoria



def construir_indice_lotes(df_lotes_shadow: pd.DataFrame) -> dict[str, Any]:
    indice = {
        "by_lote_tecnico_id": {},
        "by_lote_id": {},
    }
    if df_lotes_shadow is None or len(df_lotes_shadow) == 0:
        return indice
    for _, row in df_lotes_shadow.iterrows():
        registro = row.to_dict()
        lote_tecnico_id = str(registro.get("lote_tecnico_id") or "")
        lote_id = str(registro.get("lote_id") or "")
        if lote_tecnico_id:
            indice["by_lote_tecnico_id"][lote_tecnico_id] = registro
        if lote_id:
            indice["by_lote_id"].setdefault(lote_id, []).append(registro)
    return indice



def derivar_eventos_aporte_de_lotes(df_lotes_shadow: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    registros: list[dict[str, Any]] = []
    auditoria = {
        "qtd_eventos_aporte": 0,
        "soma_valores_aporte": 0.0,
    }
    if df_lotes_shadow is None or len(df_lotes_shadow) == 0:
        return pd.DataFrame([]), auditoria

    for _, row in df_lotes_shadow.iterrows():
        lote_id = row.get("lote_id")
        lote_tecnico_id = row.get("lote_tecnico_id")
        valor = para_float_monetario(row.get("valor_original"), 0.0)
        data_evento = para_data(row.get("data_aplicacao"))
        ordem = para_int(row.get("ordem_planilha_lote"), 0)
        produto_key = row.get("produto_key")
        produto_nome = row.get("produto_nome")
        evento_id = f"aporte::{lote_tecnico_id}"
        registros.append({
            "evento_id": evento_id,
            "evento_tipo": "aporte_historico",
            "data_evento": data_evento,
            "lote_origem_id": lote_id,
            "lote_tecnico_id": lote_tecnico_id,
            "produto_origem_key": None,
            "produto_destino_key": produto_key,
            "produto_destino_nome": produto_nome,
            "valor_bruto": float(valor),
            "valor_transferido": float(valor),
            "data_base_fiscal": para_data(row.get("data_base_fiscal")),
            "ordem_evento": ordem,
            "evento_grupo_id": f"grp::{lote_tecnico_id}::aporte",
            "origem_evento": row.get("origem_registro") or "inventario_lotes",
            "observacao_evento": "aporte_historico_derivado_do_inventario",
        })
        auditoria["qtd_eventos_aporte"] += 1
        auditoria["soma_valores_aporte"] += float(valor)
    return pd.DataFrame(registros), auditoria



def comparar_aportes_legado_vs_shadow(df_lotes_shadow: pd.DataFrame, df_eventos_aporte_shadow: pd.DataFrame) -> dict[str, Any]:
    legado = []
    if df_lotes_shadow is not None and len(df_lotes_shadow) > 0:
        for _, row in df_lotes_shadow.iterrows():
            legado.append({
                "lote_tecnico_id": str(row.get("lote_tecnico_id") or ""),
                "lote_id": normalizar_identificador(row.get("lote_id")),
                "data_evento": para_data(row.get("data_aplicacao")),
                "valor": para_float_monetario(row.get("valor_original"), 0.0),
            })

    shadow = []
    if df_eventos_aporte_shadow is not None and len(df_eventos_aporte_shadow) > 0:
        for _, row in df_eventos_aporte_shadow.iterrows():
            shadow.append({
                "lote_tecnico_id": str(row.get("lote_tecnico_id") or ""),
                "lote_id": normalizar_identificador(row.get("lote_origem_id")),
                "data_evento": para_data(row.get("data_evento")),
                "valor": para_float_monetario(row.get("valor_transferido"), 0.0),
            })

    ids_legado = {x["lote_tecnico_id"] for x in legado if x["lote_tecnico_id"]}
    ids_shadow = {x["lote_tecnico_id"] for x in shadow if x["lote_tecnico_id"]}
    map_legado = {x["lote_tecnico_id"]: x for x in legado if x["lote_tecnico_id"]}
    map_shadow = {x["lote_tecnico_id"]: x for x in shadow if x["lote_tecnico_id"]}

    datas_diferentes = []
    valores_diferentes = []
    for lote_tecnico_id in sorted(ids_legado & ids_shadow):
        a = map_legado[lote_tecnico_id]
        b = map_shadow[lote_tecnico_id]
        if a["data_evento"] != b["data_evento"]:
            datas_diferentes.append((lote_tecnico_id, a["data_evento"], b["data_evento"]))
        if abs(para_float_monetario(a["valor"], 0.0) - para_float_monetario(b["valor"], 0.0)) > 1e-9:
            valores_diferentes.append((lote_tecnico_id, a["valor"], b["valor"]))

    soma_legado = sum(para_float_monetario(x["valor"], 0.0) for x in legado)
    soma_shadow = sum(para_float_monetario(x["valor"], 0.0) for x in shadow)
    equivalentes_essenciais = (
        len(legado) == len(shadow)
        and len(ids_legado - ids_shadow) == 0
        and len(ids_shadow - ids_legado) == 0
        and len(datas_diferentes) == 0
        and len(valores_diferentes) == 0
        and abs(soma_legado - soma_shadow) <= 1e-9
    )
    return {
        "qtd_legado": len(legado),
        "qtd_shadow": len(shadow),
        "soma_legado": arredondar_monetario(soma_legado),
        "soma_shadow": arredondar_monetario(soma_shadow),
        "lote_tecnico_id_somente_legado": sorted(list(ids_legado - ids_shadow)),
        "lote_tecnico_id_somente_shadow": sorted(list(ids_shadow - ids_legado)),
        "datas_diferentes": datas_diferentes,
        "valores_diferentes": valores_diferentes,
        "equivalentes_essenciais": equivalentes_essenciais,
    }



def consolidar_eventos_financeiros_brutos(df_eventos_aporte_bruto: pd.DataFrame, df_eventos_switch_shadow: pd.DataFrame | None = None) -> pd.DataFrame:
    frames = []
    if df_eventos_aporte_bruto is not None and len(df_eventos_aporte_bruto) > 0:
        frames.append(df_eventos_aporte_bruto.copy())
    if df_eventos_switch_shadow is not None and len(df_eventos_switch_shadow) > 0:
        frames.append(df_eventos_switch_shadow.copy())
    if not frames:
        return pd.DataFrame([])

    df = pd.concat(frames, ignore_index=True, sort=False)
    prioridade_tipo = {"aporte_historico": 1, "switch_out": 2, "switch_in": 3}
    df["__data_ord__"] = pd.to_datetime(df.get("data_evento"), errors="coerce")
    if "ordem_evento" not in df.columns:
        df["ordem_evento"] = 0
    if "evento_id" not in df.columns:
        df["evento_id"] = [f"evento::{i}" for i in range(len(df))]
    df["__tipo_ord__"] = df.get("evento_tipo").map(prioridade_tipo).fillna(99)
    df = df.sort_values(
        by=["__data_ord__", "ordem_evento", "__tipo_ord__", "evento_id"],
        ascending=[True, True, True, True],
        kind="stable",
    ).reset_index(drop=True)
    return df.drop(columns=["__data_ord__", "__tipo_ord__"], errors="ignore")



def ordenar_eventos_financeiros_brutos_shadow(df_eventos_financeiros_brutos: pd.DataFrame) -> pd.DataFrame:
    return consolidar_eventos_financeiros_brutos(df_eventos_financeiros_brutos)



def carregar_switching_shadow_reconciliacao(
    dados_operacionais: PacoteDadosOperacionaisCanonicos,
    carteira_canonica: PacoteCarteiraCanonica | None = None,
) -> PacoteSwitchingShadowReconciliacao:
    lotes_shadow, auditoria_lotes_shadow = normalizar_lotes_shadow(
        dados_operacionais.inventario_canonico,
        carteira_canonica=carteira_canonica,
    )
    indice_lotes = construir_indice_lotes(lotes_shadow)
    eventos_aporte_shadow, auditoria_eventos_aporte = derivar_eventos_aporte_de_lotes(lotes_shadow)
    reconciliacao_aportes = comparar_aportes_legado_vs_shadow(lotes_shadow, eventos_aporte_shadow)
    eventos_financeiros_brutos = consolidar_eventos_financeiros_brutos(eventos_aporte_shadow, None)
    eventos_financeiros_ordenados = ordenar_eventos_financeiros_brutos_shadow(eventos_financeiros_brutos)
    return PacoteSwitchingShadowReconciliacao(
        lotes_shadow=lotes_shadow,
        indice_lotes=indice_lotes,
        eventos_aporte_shadow=eventos_aporte_shadow,
        eventos_financeiros_brutos=eventos_financeiros_brutos,
        eventos_financeiros_ordenados=eventos_financeiros_ordenados,
        auditoria_lotes_shadow=auditoria_lotes_shadow,
        auditoria_eventos_aporte=auditoria_eventos_aporte,
        reconciliacao_aportes=reconciliacao_aportes,
    )

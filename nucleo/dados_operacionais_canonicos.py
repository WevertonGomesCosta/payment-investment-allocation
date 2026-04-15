"""Canonização inicial dos dados operacionais do projeto.

Este módulo abre de forma restrita o bloco de dados operacionais, sem ainda
implementar replay do passado, núcleo financeiro, resgates ou capitalização.

Escopo desta etapa:
- leitura canônica do Inventário de Lotes;
- leitura canônica de Todos os Gastos;
- classificação operacional mínima dos lotes;
- separação estrutural entre contas pagas e não pagas.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Optional

import pandas as pd

from nucleo.carteira_canonica import PacoteCarteiraCanonica, normalizar_nome_produto
from nucleo.leitor_planilha import PacotePlanilha, resolver_coluna
from nucleo.utilitarios_neutros import (
    escolher_melhor_correspondencia_textual,
    limpar_texto,
    normalizar_identificador,
    normalizar_texto,
    para_bool,
    para_data,
    para_float_monetario,
    para_int,
)


@dataclass(slots=True)
class PacoteDadosOperacionaisCanonicos:
    nome_aba_lotes: str
    nome_aba_despesas: str
    inventario_canonico: pd.DataFrame
    gastos_canonicos: pd.DataFrame
    auditoria_inventario: dict[str, Any]
    auditoria_gastos: dict[str, Any]






def _classificar_investimento(valor_investimento: Any, data_aplicacao: Optional[date], data_referencia: date) -> dict[str, Any]:
    bruto = limpar_texto(valor_investimento)
    if bruto in {"-", "—", "–", "--"}:
        return {
            "investimento_bruto": bruto,
            "produto_informado": "",
            "situacao_investimento": "nao_aportado_exaurido",
            "aportado": False,
            "nao_aportado_disponivel": False,
            "nao_aportado_exaurido": True,
            "recebido_futuro_nao_disponivel": False,
            "disponivel_na_data_referencia": False,
        }

    if bruto == "":
        futuro = data_aplicacao is not None and data_aplicacao > data_referencia
        return {
            "investimento_bruto": bruto,
            "produto_informado": "",
            "situacao_investimento": "recebido_futuro_nao_disponivel" if futuro else "nao_aportado_disponivel",
            "aportado": False,
            "nao_aportado_disponivel": not futuro,
            "nao_aportado_exaurido": False,
            "recebido_futuro_nao_disponivel": futuro,
            "disponivel_na_data_referencia": not futuro,
        }

    return {
        "investimento_bruto": bruto,
        "produto_informado": bruto,
        "situacao_investimento": "aportado",
        "aportado": True,
        "nao_aportado_disponivel": False,
        "nao_aportado_exaurido": False,
        "recebido_futuro_nao_disponivel": False,
        "disponivel_na_data_referencia": bool(data_aplicacao is None or data_aplicacao <= data_referencia),
    }


def _resolver_produto_canonico(valor_produto: str, carteira: Optional[PacoteCarteiraCanonica], config: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    vazio = {
        "produto_key": None,
        "produto_nome_canonico": None,
        "produto_nome_norm": None,
        "produto_encontrado": False,
        "tipo_match_produto": "vazio",
        "score_match_produto": 0.0,
        "referencia_match_produto": "",
    }
    if not valor_produto:
        return vazio
    if carteira is None:
        return {
            "produto_key": None,
            "produto_nome_canonico": valor_produto,
            "produto_nome_norm": None,
            "produto_encontrado": False,
            "tipo_match_produto": "sem_carteira_canonica",
            "score_match_produto": 0.0,
            "referencia_match_produto": "",
        }

    by_key = carteira.mapa_produtos.get("by_key", {})
    by_nome = carteira.mapa_produtos.get("by_nome_norm", {})
    valor_txt = limpar_texto(valor_produto)
    valor_norm = normalizar_nome_produto(valor_txt)

    if valor_txt in by_key:
        info = by_key[valor_txt]
        return {
            "produto_key": info.get("produto_key"),
            "produto_nome_canonico": info.get("nome"),
            "produto_nome_norm": info.get("nome_norm"),
            "produto_encontrado": True,
            "tipo_match_produto": "produto_key_exato",
            "score_match_produto": 1.0,
            "referencia_match_produto": info.get("nome") or valor_txt,
        }

    if valor_norm in by_nome:
        produto_key = by_nome[valor_norm]
        info = by_key.get(produto_key, {})
        return {
            "produto_key": info.get("produto_key"),
            "produto_nome_canonico": info.get("nome"),
            "produto_nome_norm": info.get("nome_norm"),
            "produto_encontrado": True,
            "tipo_match_produto": "nome_norm",
            "score_match_produto": 1.0,
            "referencia_match_produto": info.get("nome") or valor_txt,
        }

    opcoes = []
    for produto_key, info in by_key.items():
        nome_ref = limpar_texto(info.get("nome") or produto_key)
        opcoes.append((produto_key, nome_ref))

    produto_key_match, meta_match = escolher_melhor_correspondencia_textual(valor_txt, opcoes, minimo_score=0.60)
    if produto_key_match:
        info = by_key.get(produto_key_match, {})
        return {
            "produto_key": info.get("produto_key"),
            "produto_nome_canonico": info.get("nome"),
            "produto_nome_norm": info.get("nome_norm"),
            "produto_encontrado": True,
            "tipo_match_produto": "correspondencia_textual",
            "score_match_produto": float(meta_match.get("score", 0.0) or 0.0),
            "referencia_match_produto": meta_match.get("referencia") or info.get("nome") or valor_txt,
        }

    return {
        "produto_key": None,
        "produto_nome_canonico": valor_txt,
        "produto_nome_norm": valor_norm,
        "produto_encontrado": False,
        "tipo_match_produto": "nao_encontrado",
        "score_match_produto": float(meta_match.get("score", 0.0) if 'meta_match' in locals() else 0.0),
        "referencia_match_produto": (meta_match.get("referencia") if 'meta_match' in locals() else "") or "",
    }


def _pago_para_bool(valor: Any, tratar_nulo_como_nao: bool) -> bool:
    if limpar_texto(valor) == "":
        return False if tratar_nulo_como_nao else False
    return para_bool(valor, False, verdadeiros={"ok", "sim", "s", "true", "1", "pago", "yes", "y"})


def carregar_inventario_canonico(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    carteira_canonica: Optional[PacoteCarteiraCanonica] = None,
) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}
    nome_aba = str(abas_cfg.get("lotes") or "Inventário de Lotes")
    df = pacote_planilha.quadros_brutos.get(nome_aba)
    if df is None:
        raise KeyError(f"Aba de lotes não encontrada na planilha: {nome_aba}")

    col_lote_id = resolver_coluna(df, config, "lotes", "lote_id")
    col_data_aplicacao = resolver_coluna(df, config, "lotes", "data_aplicacao")
    col_valor_original = resolver_coluna(df, config, "lotes", "valor_original")
    col_produto = resolver_coluna(df, config, "lotes", "produto_id", obrigatoria=False)
    col_status = resolver_coluna(df, config, "lotes", "status_lote", obrigatoria=False)
    col_data_base_fiscal = resolver_coluna(df, config, "lotes", "data_base_fiscal", obrigatoria=False)

    auditoria = {
        "colunas_resolvidas": {
            "lote_id": col_lote_id,
            "data_aplicacao": col_data_aplicacao,
            "valor_original": col_valor_original,
            "produto_id": col_produto,
            "status_lote": col_status,
            "data_base_fiscal": col_data_base_fiscal,
        },
        "linhas_descartadas": [],
    }

    registros = []
    for idx, row in df.iterrows():
        lote_id = normalizar_identificador(row.get(col_lote_id))
        data_aplicacao = para_data(row.get(col_data_aplicacao))
        valor_original = para_float_monetario(row.get(col_valor_original), 0.0)

        if not lote_id:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "lote_id_vazio"})
            continue
        if data_aplicacao is None:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "data_aplicacao_invalida", "lote_id": lote_id})
            continue
        if valor_original <= 0:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "valor_original_nao_positivo", "lote_id": lote_id})
            continue

        classificacao = _classificar_investimento(row.get(col_produto) if col_produto else None, data_aplicacao, data_referencia)
        produto_resolvido = _resolver_produto_canonico(classificacao["produto_informado"], carteira_canonica, config)
        data_base_fiscal = para_data(row.get(col_data_base_fiscal)) if col_data_base_fiscal else None
        data_base_fiscal_inferida = data_base_fiscal is None
        if data_base_fiscal is None:
            data_base_fiscal = data_aplicacao

        registros.append({
            "lote_id": lote_id,
            "lote_id_raw": limpar_texto(row.get(col_lote_id)),
            "ordem_planilha_lote": para_int(idx, 0) + 1,
            "origem_registro": "inventario_lotes",
            "data_aplicacao": data_aplicacao,
            "valor_original": valor_original,
            "data_base_fiscal": data_base_fiscal,
            "data_base_fiscal_inferida": data_base_fiscal_inferida,
            "status_lote_informado": limpar_texto(row.get(col_status)) if col_status else "",
            **classificacao,
            **produto_resolvido,
        })

    quadro = pd.DataFrame(registros)
    if len(quadro) == 0:
        validacao = {"ok": False, "erros": ["inventario_canonico_vazio"], "avisos": []}
        auditoria["validacao"] = validacao
        return nome_aba, quadro, auditoria

    validacao = {"ok": True, "erros": [], "avisos": []}
    if quadro["lote_id"].duplicated().any():
        validacao["ok"] = False
        validacao["erros"].append("lote_id_duplicado")
    if quadro["data_aplicacao"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("data_aplicacao_nula")
    if (quadro["valor_original"] <= 0).any():
        validacao["ok"] = False
        validacao["erros"].append("valor_original_nao_positivo")
    if quadro["aportado"].any() and (~quadro["produto_encontrado"] & quadro["aportado"]).any():
        validacao["avisos"].append("existem_lotes_aportados_sem_match_canonico_de_produto")
    if quadro["recebido_futuro_nao_disponivel"].any():
        validacao["avisos"].append("existem_recebidos_futuros_nao_disponiveis_hoje")
    if quadro["nao_aportado_exaurido"].any():
        validacao["avisos"].append("existem_lotes_nao_aportados_exauridos")

    auditoria["validacao"] = validacao
    quadro_aportado = quadro[quadro["aportado"]].copy()
    auditoria["resumo"] = {
        "total_lotes": int(len(quadro)),
        "aportados": int(quadro["aportado"].sum()),
        "nao_aportados_disponiveis": int(quadro["nao_aportado_disponivel"].sum()),
        "nao_aportados_exauridos": int(quadro["nao_aportado_exaurido"].sum()),
        "recebidos_futuros": int(quadro["recebido_futuro_nao_disponivel"].sum()),
        "aportados_com_match": int((quadro_aportado["produto_encontrado"] == True).sum()) if len(quadro_aportado) > 0 else 0,
        "aportados_sem_match": int((quadro_aportado["produto_encontrado"] == False).sum()) if len(quadro_aportado) > 0 else 0,
        "tipos_match_produto": {
            str(ch): int(v) for ch, v in quadro["tipo_match_produto"].fillna("vazio").value_counts(dropna=False).to_dict().items()
        },
    }
    return nome_aba, quadro, auditoria


def carregar_gastos_canonicos(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}
    nome_aba = str(abas_cfg.get("despesas") or "Todos os Gastos")
    df = pacote_planilha.quadros_brutos.get(nome_aba)
    if df is None:
        raise KeyError(f"Aba de despesas não encontrada na planilha: {nome_aba}")

    col_despesa_id = resolver_coluna(df, config, "despesas", "despesa_id", obrigatoria=False)
    col_data = resolver_coluna(df, config, "despesas", "data")
    col_descricao = resolver_coluna(df, config, "despesas", "descricao", obrigatoria=False)
    col_valor = resolver_coluna(df, config, "despesas", "valor")
    col_pago = resolver_coluna(df, config, "despesas", "pago", obrigatoria=False)
    col_lote_1 = resolver_coluna(df, config, "despesas", "lote_usado_1", obrigatoria=False)
    col_lote_2 = resolver_coluna(df, config, "despesas", "lote_usado_2", obrigatoria=False)

    politicas_cfg = config.get("politicas", {}) if isinstance(config.get("politicas"), Mapping) else {}
    tratar_pago_nulo_como_nao = bool(politicas_cfg.get("tratar_pago_nulo_como_nao", True))

    auditoria = {
        "colunas_resolvidas": {
            "despesa_id": col_despesa_id,
            "data": col_data,
            "descricao": col_descricao,
            "valor": col_valor,
            "pago": col_pago,
            "lote_usado_1": col_lote_1,
            "lote_usado_2": col_lote_2,
        },
        "linhas_descartadas": [],
    }

    registros = []
    sequencia_gerada = 1
    for idx, row in df.iterrows():
        despesa_id = limpar_texto(row.get(col_despesa_id)) if col_despesa_id else ""
        if despesa_id == "":
            despesa_id = f"despesa_auto_{sequencia_gerada:05d}"
            sequencia_gerada += 1

        data_evento = para_data(row.get(col_data))
        valor = para_float_monetario(row.get(col_valor), 0.0)
        if data_evento is None:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "data_invalida", "despesa_id": despesa_id})
            continue
        if valor <= 0:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "valor_nao_positivo", "despesa_id": despesa_id})
            continue

        lote_1 = normalizar_identificador(row.get(col_lote_1)) if col_lote_1 else ""
        lote_2 = normalizar_identificador(row.get(col_lote_2)) if col_lote_2 else ""
        pago = _pago_para_bool(row.get(col_pago) if col_pago else None, tratar_pago_nulo_como_nao)

        registros.append({
            "despesa_id": despesa_id,
            "data": data_evento,
            "descricao": limpar_texto(row.get(col_descricao)) if col_descricao else "",
            "valor": valor,
            "pago": pago,
            "lote_usado_1": lote_1,
            "lote_usado_2": lote_2,
            "qtd_lotes_informados": int(bool(lote_1)) + int(bool(lote_2)),
            "passado_pago_ate_data_referencia": bool(pago and data_evento <= data_referencia),
            "futuro_ou_pendente_na_data_referencia": bool((not pago) or data_evento > data_referencia),
        })

    quadro = pd.DataFrame(registros)
    if len(quadro) == 0:
        validacao = {"ok": False, "erros": ["gastos_canonicos_vazio"], "avisos": []}
        auditoria["validacao"] = validacao
        return nome_aba, quadro, auditoria

    validacao = {"ok": True, "erros": [], "avisos": []}
    if quadro["despesa_id"].duplicated().any():
        validacao["ok"] = False
        validacao["erros"].append("despesa_id_duplicado")
    if quadro["data"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("data_nula")
    if (quadro["valor"] <= 0).any():
        validacao["ok"] = False
        validacao["erros"].append("valor_nao_positivo")
    if (quadro["qtd_lotes_informados"] > 1).any():
        validacao["avisos"].append("existem_despesas_com_multiplos_lotes_informados")
    if quadro["passado_pago_ate_data_referencia"].any():
        validacao["avisos"].append("existem_despesas_pagamento_historico")
    if quadro["futuro_ou_pendente_na_data_referencia"].any():
        validacao["avisos"].append("existem_despesas_futuras_ou_pendentes")

    auditoria["validacao"] = validacao
    auditoria["resumo"] = {
        "total_despesas": int(len(quadro)),
        "pagas_ate_data_referencia": int(quadro["passado_pago_ate_data_referencia"].sum()),
        "futuras_ou_pendentes": int(quadro["futuro_ou_pendente_na_data_referencia"].sum()),
        "com_lote_informado": int((quadro["qtd_lotes_informados"] > 0).sum()),
    }
    return nome_aba, quadro, auditoria


def carregar_dados_operacionais_canonicos(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    carteira_canonica: Optional[PacoteCarteiraCanonica] = None,
) -> PacoteDadosOperacionaisCanonicos:
    nome_aba_lotes, inventario_canonico, auditoria_inventario = carregar_inventario_canonico(
        pacote_planilha,
        config,
        data_referencia=data_referencia,
        carteira_canonica=carteira_canonica,
    )
    nome_aba_despesas, gastos_canonicos, auditoria_gastos = carregar_gastos_canonicos(
        pacote_planilha,
        config,
        data_referencia=data_referencia,
    )
    return PacoteDadosOperacionaisCanonicos(
        nome_aba_lotes=nome_aba_lotes,
        nome_aba_despesas=nome_aba_despesas,
        inventario_canonico=inventario_canonico,
        gastos_canonicos=gastos_canonicos,
        auditoria_inventario=auditoria_inventario,
        auditoria_gastos=auditoria_gastos,
    )

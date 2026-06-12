"""Canonização inicial dos dados operacionais do projeto.

Este módulo abre de forma restrita o bloco de dados operacionais, sem ainda
implementar replay do passado, núcleo financeiro, resgates ou capitalização.

Escopo desta etapa:
- leitura canônica do Inventário de Lotes;
- leitura canônica de Todos os Gastos;
- leitura canônica de Salários;
- leitura canônica de Switching, incluindo aliases de aba;
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
from nucleo.inventario_lotes_expandido_pos_switching import (
    construir_inventario_lotes_expandido,
    normalizar_lotes_pos_switching_para_schema_inventario,
)
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
    nome_aba_salarios: str = ""
    nome_aba_switching: str = ""
    salarios_canonicos: Optional[pd.DataFrame] = None
    switching_canonico: Optional[pd.DataFrame] = None
    auditoria_salarios: Optional[dict[str, Any]] = None
    auditoria_switching: Optional[dict[str, Any]] = None
    inventario_lotes_expandido: Optional[pd.DataFrame] = None
    lotes_pos_switching_normalizados: Optional[pd.DataFrame] = None
    auditoria_inventario_expandido: Optional[dict[str, Any]] = None






def _classificar_investimento(
    valor_investimento: Any,
    data_aplicacao: Optional[date],
    data_referencia: date,
    *,
    data_recebimento: Optional[date] = None,
) -> dict[str, Any]:
    bruto = limpar_texto(valor_investimento)
    data_disponibilidade = data_recebimento or data_aplicacao
    disponivel_hoje = bool(data_disponibilidade is None or data_disponibilidade <= data_referencia)

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
        futuro = data_disponibilidade is not None and data_disponibilidade > data_referencia
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
        "disponivel_na_data_referencia": disponivel_hoje,
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
    col_data_recebimento = resolver_coluna(df, config, "lotes", "data_recebimento", obrigatoria=False)
    col_data_aplicacao = resolver_coluna(df, config, "lotes", "data_aplicacao")
    col_valor_original = resolver_coluna(df, config, "lotes", "valor_original")
    col_produto = resolver_coluna(df, config, "lotes", "produto_id", obrigatoria=False)
    col_status = resolver_coluna(df, config, "lotes", "status_lote", obrigatoria=False)
    col_data_base_fiscal = resolver_coluna(df, config, "lotes", "data_base_fiscal", obrigatoria=False)

    auditoria = {
        "colunas_resolvidas": {
            "lote_id": col_lote_id,
            "data_recebimento": col_data_recebimento,
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
        data_recebimento = para_data(row.get(col_data_recebimento)) if col_data_recebimento else None
        produto_informado_raw = row.get(col_produto) if col_produto else None
        produto_informado_txt = limpar_texto(produto_informado_raw)
        data_aplicacao = para_data(row.get(col_data_aplicacao))
        valor_original = para_float_monetario(row.get(col_valor_original), 0.0)

        if not lote_id:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "lote_id_vazio"})
            continue
        if data_aplicacao is None and produto_informado_txt == "" and data_recebimento is not None:
            data_aplicacao = data_recebimento
        if data_aplicacao is None:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "data_aplicacao_invalida", "lote_id": lote_id})
            continue
        if valor_original <= 0:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "valor_original_nao_positivo", "lote_id": lote_id})
            continue

        if data_recebimento is None:
            data_recebimento = data_aplicacao
        classificacao = _classificar_investimento(
            produto_informado_raw,
            data_aplicacao,
            data_referencia,
            data_recebimento=data_recebimento,
        )
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
            "data_recebimento": data_recebimento,
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
    if quadro["data_recebimento"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("data_recebimento_nula")
    if (quadro["data_recebimento"] > quadro["data_aplicacao"]).any():
        validacao["avisos"].append("existem_lotes_com_recebimento_apos_aplicacao")
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
        "recebidos_antes_da_aplicacao": int((quadro["data_recebimento"] < quadro["data_aplicacao"]).sum()),
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



def _resolver_aba_por_alias(
    pacote_planilha: PacotePlanilha,
    aliases: list[str],
    *,
    obrigatoria: bool = False,
) -> tuple[str, Optional[pd.DataFrame], dict[str, Any]]:
    mapa = {normalizar_texto(nome): nome for nome in pacote_planilha.nomes_abas}
    aliases_norm = [normalizar_texto(a) for a in aliases]

    for alias_norm in aliases_norm:
        if alias_norm in mapa:
            nome = mapa[alias_norm]
            return nome, pacote_planilha.quadros_brutos.get(nome), {
                "aba_encontrada": True,
                "nome_aba": nome,
                "aliases_aceitos": aliases,
                "tipo_match_aba": "alias_exato_normalizado",
            }

    auditoria = {
        "aba_encontrada": False,
        "nome_aba": "",
        "aliases_aceitos": aliases,
        "abas_disponiveis": list(pacote_planilha.nomes_abas),
        "tipo_match_aba": "nao_encontrada",
    }
    if obrigatoria:
        raise KeyError(f"Aba não encontrada. Aliases tentados: {aliases}. Abas disponíveis: {pacote_planilha.nomes_abas}")
    return "", None, auditoria


def _resolver_coluna_por_alias_local(
    df: pd.DataFrame,
    aliases: list[str],
) -> Optional[str]:
    if df is None or len(getattr(df, "columns", [])) == 0:
        return None
    mapa = {normalizar_texto(c): c for c in df.columns}
    for alias in aliases:
        alias_norm = normalizar_texto(alias)
        if alias_norm in mapa:
            return str(mapa[alias_norm])
    return None


def _primeira_coluna_monetaria(df: pd.DataFrame, excluir: set[str] | None = None) -> Optional[str]:
    excluir = excluir or set()
    melhor_coluna = None
    melhor_qtd = -1
    for col in df.columns:
        if str(col) in excluir:
            continue
        valores = df[col].apply(lambda v: para_float_monetario(v, 0.0))
        qtd = int((valores > 0).sum())
        if qtd > melhor_qtd:
            melhor_coluna = str(col)
            melhor_qtd = qtd
    return melhor_coluna if melhor_qtd > 0 else None


def carregar_salarios_canonicos(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    aliases_aba = ["Salários", "Salarios", "Salário", "Salario"]
    nome_aba, df, auditoria_aba = _resolver_aba_por_alias(pacote_planilha, aliases_aba, obrigatoria=False)

    auditoria: dict[str, Any] = {
        **auditoria_aba,
        "colunas_resolvidas": {},
        "linhas_descartadas": [],
    }

    if df is None:
        quadro = pd.DataFrame(columns=[
            "salario_id",
            "ordem_planilha_salario",
            "origem_registro",
            "data_recebimento",
            "descricao",
            "valor_bruto",
            "valor_liquido",
            "disponivel_na_data_referencia",
        ])
        auditoria["validacao"] = {"ok": True, "erros": [], "avisos": ["aba_salarios_ausente"]}
        auditoria["resumo"] = {"total_salarios": 0, "valor_bruto_total": 0.0, "valor_liquido_total": 0.0}
        return nome_aba, quadro, auditoria

    col_data = _resolver_coluna_por_alias_local(df, [
        "data_recebimento", "data recebimento", "Data Recebimento",
        "data", "Data", "mês", "mes", "Mês", "Mes",
    ])
    col_descricao = _resolver_coluna_por_alias_local(df, [
        "descricao", "descrição", "Descrição", "Descricao",
        "origem", "Origem", "fonte", "Fonte", "observacao", "observação",
    ])
    col_valor_bruto = _resolver_coluna_por_alias_local(df, [
        "valor_bruto", "valor bruto", "Valor Bruto",
        "salario_bruto", "salário bruto", "Salário Bruto", "Salario Bruto",
        "valor", "Valor", "salario", "salário", "Salário", "Salario",
    ])
    col_valor_liquido = _resolver_coluna_por_alias_local(df, [
        "valor_liquido", "valor líquido", "Valor Líquido", "Valor Liquido",
        "salario_liquido", "salário líquido", "Salário Líquido", "Salario Liquido",
        "liquido", "líquido", "Líquido", "Liquido",
    ])

    if col_valor_bruto is None:
        col_valor_bruto = _primeira_coluna_monetaria(df)

    auditoria["colunas_resolvidas"] = {
        "data_recebimento": col_data,
        "descricao": col_descricao,
        "valor_bruto": col_valor_bruto,
        "valor_liquido": col_valor_liquido,
    }

    registros = []
    for idx, row in df.iterrows():
        data_recebimento = para_data(row.get(col_data)) if col_data else None
        valor_bruto = para_float_monetario(row.get(col_valor_bruto), 0.0) if col_valor_bruto else 0.0
        valor_liquido = para_float_monetario(row.get(col_valor_liquido), valor_bruto) if col_valor_liquido else valor_bruto

        if data_recebimento is None and valor_bruto <= 0 and valor_liquido <= 0:
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "linha_vazia_ou_sem_valor"})
            continue

        registros.append({
            "salario_id": f"salario_auto_{len(registros) + 1:05d}",
            "ordem_planilha_salario": para_int(idx, 0) + 1,
            "origem_registro": "salarios",
            "data_recebimento": data_recebimento,
            "descricao": limpar_texto(row.get(col_descricao)) if col_descricao else "",
            "valor_bruto": valor_bruto,
            "valor_liquido": valor_liquido,
            "disponivel_na_data_referencia": bool(data_recebimento is None or data_recebimento <= data_referencia),
        })

    quadro = pd.DataFrame(registros)
    validacao = {"ok": True, "erros": [], "avisos": []}
    if len(quadro) == 0:
        validacao["avisos"].append("salarios_canonicos_vazio")
    if len(quadro) > 0 and (quadro["valor_bruto"] <= 0).any():
        validacao["avisos"].append("existem_salarios_sem_valor_bruto_positivo")
    if len(quadro) > 0 and quadro["data_recebimento"].isna().any():
        validacao["avisos"].append("existem_salarios_sem_data_recebimento")

    auditoria["validacao"] = validacao
    auditoria["resumo"] = {
        "total_salarios": int(len(quadro)),
        "valor_bruto_total": float(round(quadro["valor_bruto"].sum(), 2)) if len(quadro) else 0.0,
        "valor_liquido_total": float(round(quadro["valor_liquido"].sum(), 2)) if len(quadro) else 0.0,
        "disponiveis_na_data_referencia": int(quadro["disponivel_na_data_referencia"].sum()) if len(quadro) else 0,
    }
    return nome_aba, quadro, auditoria


def carregar_switching_canonico(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    aliases_aba = ["Switching", "Switiching", "Swtiching"]
    nome_aba, df, auditoria_aba = _resolver_aba_por_alias(pacote_planilha, aliases_aba, obrigatoria=False)

    auditoria: dict[str, Any] = {
        **auditoria_aba,
        "colunas_resolvidas": {},
        "linhas_descartadas": [],
    }

    cols = [
        "switching_id",
        "ordem_planilha_switching",
        "origem_registro",
        "data_recebimento",
        "data_aplicacao",
        "data_switching",
        "lote_origem",
        "lote_destino",
        "produto_origem",
        "produto_destino",
        "ganho_estimado",
        "valor_liquido_origem",
        "status",
    ]

    if df is None:
        quadro = pd.DataFrame(columns=cols)
        auditoria["validacao"] = {"ok": True, "erros": [], "avisos": ["aba_switching_ausente"]}
        auditoria["resumo"] = {"total_switchings": 0, "valor_liquido_origem_total": 0.0}
        return nome_aba, quadro, auditoria

    col_data_recebimento = _resolver_coluna_por_alias_local(df, [
        "data_recebimento", "data recebimento", "Data Recebimento",
        "recebimento", "Recebimento",
    ])
    col_data_aplicacao = _resolver_coluna_por_alias_local(df, [
        "data_aplicacao", "data aplicação", "data aplicacao",
        "Data Aplicação", "Data Aplicacao",
        "aplicação", "aplicacao", "Aplicação", "Aplicacao",
    ])
    col_data_switching = _resolver_coluna_por_alias_local(df, [
        "data_switching", "data switching", "Data Switching",
        "data sugerida", "Data sugerida", "Data Sugerida",
        "data", "Data",
    ])
    col_lote_origem = _resolver_coluna_por_alias_local(df, [
        "lote_origem", "lote origem", "Lote origem", "Lote Origem",
        "lote_id_antes", "lote antes", "Lote antes",
        "Lote (ID) Antes", "lote (id) antes",
    ])
    col_lote_destino = _resolver_coluna_por_alias_local(df, [
        "lote_destino", "lote destino", "Lote destino", "Lote Destino",
        "lote_pos_switching", "lote pós switching", "lote pos switching",
        "lote_id_depois", "lote depois", "Lote depois",
        "Lote (ID) Depois", "lote (id) depois",
    ])
    col_produto_origem = _resolver_coluna_por_alias_local(df, [
        "produto_origem", "produto origem", "Produto origem", "Produto Origem",
        "investimento_origem", "investimento origem",
    ])
    col_produto_destino = _resolver_coluna_por_alias_local(df, [
        "produto_destino", "produto destino", "Produto destino", "Produto Destino",
        "produto destino switching", "Produto destino switching", "Produto Destino Switching",
        "destino", "Destino", "investimento", "Investimento",
    ])
    col_ganho = _resolver_coluna_por_alias_local(df, [
        "ganho_estimado", "ganho estimado", "Ganho estimado", "Ganho Estimado",
        "ganho", "Ganho",
    ])
    col_valor = _resolver_coluna_por_alias_local(df, [
        "valor_liquido_origem", "valor líquido origem", "Valor líquido origem", "Valor Liquido Origem",
        "valor_liquido_migrado", "valor líquido migrado", "Valor líquido migrado", "Valor Liquido Migrado",
        "Valor Líquido Migrado",
        "valor", "Valor",
    ])
    col_status = _resolver_coluna_por_alias_local(df, ["status", "Status"])

    auditoria["colunas_resolvidas"] = {
        "data_recebimento": col_data_recebimento,
        "data_aplicacao": col_data_aplicacao,
        "data_switching": col_data_switching,
        "lote_origem": col_lote_origem,
        "lote_destino": col_lote_destino,
        "produto_origem": col_produto_origem,
        "produto_destino": col_produto_destino,
        "ganho_estimado": col_ganho,
        "valor_liquido_origem": col_valor,
        "status": col_status,
    }

    registros = []
    for idx, row in df.iterrows():
        data_recebimento = para_data(row.get(col_data_recebimento)) if col_data_recebimento else None
        data_aplicacao = para_data(row.get(col_data_aplicacao)) if col_data_aplicacao else None
        data_switching_historica = para_data(row.get(col_data_switching)) if col_data_switching else None

        if data_aplicacao is None:
            data_aplicacao = data_switching_historica
        if data_recebimento is None:
            data_recebimento = data_switching_historica or data_aplicacao

        data_switching = data_aplicacao or data_switching_historica or data_recebimento

        lote_origem = normalizar_identificador(row.get(col_lote_origem)) if col_lote_origem else ""
        lote_destino = normalizar_identificador(row.get(col_lote_destino)) if col_lote_destino else ""
        produto_destino = limpar_texto(row.get(col_produto_destino)) if col_produto_destino else ""
        valor_liquido = para_float_monetario(row.get(col_valor), 0.0) if col_valor else 0.0

        if (
            data_recebimento is None
            and data_aplicacao is None
            and data_switching is None
            and not lote_origem
            and not lote_destino
            and not produto_destino
            and valor_liquido <= 0
        ):
            auditoria["linhas_descartadas"].append({"idx": int(idx), "motivo": "linha_vazia"})
            continue

        registros.append({
            "switching_id": f"switching_auto_{len(registros) + 1:05d}",
            "ordem_planilha_switching": para_int(idx, 0) + 1,
            "origem_registro": "switching",
            "data_recebimento": data_recebimento,
            "data_aplicacao": data_aplicacao,
            "data_switching": data_switching,
            "lote_origem": lote_origem,
            "lote_destino": lote_destino,
            "produto_origem": limpar_texto(row.get(col_produto_origem)) if col_produto_origem else "",
            "produto_destino": produto_destino,
            "ganho_estimado": para_float_monetario(row.get(col_ganho), 0.0) if col_ganho else 0.0,
            "valor_liquido_origem": valor_liquido,
            "status": limpar_texto(row.get(col_status)) if col_status else "",
        })

    quadro = pd.DataFrame(registros, columns=cols)
    validacao = {"ok": True, "erros": [], "avisos": []}
    if len(quadro) == 0:
        validacao["avisos"].append("switching_canonico_vazio")
    if len(quadro) > 0 and quadro["data_recebimento"].isna().any():
        validacao["avisos"].append("existem_switchings_sem_data_recebimento")
    if len(quadro) > 0 and quadro["data_aplicacao"].isna().any():
        validacao["avisos"].append("existem_switchings_sem_data_aplicacao")
    if len(quadro) > 0 and quadro["data_switching"].isna().any():
        validacao["avisos"].append("existem_switchings_sem_data")
    if len(quadro) > 0 and (quadro["lote_origem"] == "").any():
        validacao["avisos"].append("existem_switchings_sem_lote_origem")
    if len(quadro) > 0 and (quadro["produto_destino"] == "").any() and (quadro["lote_destino"] == "").any():
        validacao["avisos"].append("existem_switchings_sem_destino_identificavel")

    auditoria["validacao"] = validacao
    auditoria["resumo"] = {
        "total_switchings": int(len(quadro)),
        "valor_liquido_origem_total": float(round(quadro["valor_liquido_origem"].sum(), 2)) if len(quadro) else 0.0,
        "com_data_recebimento": int(quadro["data_recebimento"].notna().sum()) if len(quadro) else 0,
        "com_data_aplicacao": int(quadro["data_aplicacao"].notna().sum()) if len(quadro) else 0,
        "com_lote_origem": int((quadro["lote_origem"] != "").sum()) if len(quadro) else 0,
        "com_lote_destino": int((quadro["lote_destino"] != "").sum()) if len(quadro) else 0,
        "com_produto_destino": int((quadro["produto_destino"] != "").sum()) if len(quadro) else 0,
    }
    return nome_aba, quadro, auditoria


def carregar_dados_operacionais_canonicos(
    pacote_planilha: PacotePlanilha,
    config: Mapping[str, Any],
    *,
    data_referencia: date,
    carteira_canonica: Optional[PacoteCarteiraCanonica] = None,
) -> PacoteDadosOperacionaisCanonicos:
    nome_aba_lotes, inventario_canonico_base, auditoria_inventario = carregar_inventario_canonico(
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
    nome_aba_salarios, salarios_canonicos, auditoria_salarios = carregar_salarios_canonicos(
        pacote_planilha,
        config,
        data_referencia=data_referencia,
    )
    nome_aba_switching, switching_canonico, auditoria_switching = carregar_switching_canonico(
        pacote_planilha,
        config,
        data_referencia=data_referencia,
    )
    lotes_pos_switching_normalizados, auditoria_pos = normalizar_lotes_pos_switching_para_schema_inventario(
        switching_canonico,
        config,
        data_referencia=data_referencia,
        carteira_canonica=carteira_canonica,
    )
    inventario_canonico_operacional, auditoria_expandido = construir_inventario_lotes_expandido(
        inventario_canonico_base,
        lotes_pos_switching_normalizados,
    )

    origem_ids = set()
    if isinstance(switching_canonico, pd.DataFrame) and len(switching_canonico) and "lote_origem" in switching_canonico.columns:
        origem_ids = {
            normalizar_identificador(v)
            for v in switching_canonico["lote_origem"].tolist()
            if normalizar_identificador(v)
        }

    base_origens = pd.DataFrame()
    if origem_ids and "lote_id" in inventario_canonico_base.columns:
        base_origens = inventario_canonico_base[
            inventario_canonico_base["lote_id"].astype(str).map(normalizar_identificador).isin(origem_ids)
        ].copy()

    qtd_origens_potencialmente_ativas = 0
    if len(base_origens):
        if "nao_aportado_exaurido" in base_origens.columns:
            qtd_origens_potencialmente_ativas = int((~base_origens["nao_aportado_exaurido"].fillna(False).astype(bool)).sum())
        else:
            qtd_origens_potencialmente_ativas = int(len(base_origens))

    auditoria_expandido = {
        **auditoria_expandido,
        **auditoria_pos,
        "inventario_canonico_operacional_expandido": True,
        "qtd_lotes_inventario_canonico_base": int(len(inventario_canonico_base)),
        "qtd_lotes_destino_switching_integrados": int(len(lotes_pos_switching_normalizados)),
        "qtd_lotes_inventario_canonico_operacional": int(len(inventario_canonico_operacional)),
        "qtd_lotes_origem_switching_distintos": int(len(origem_ids)),
        "qtd_lotes_origem_switching_encontrados_no_inventario": int(len(base_origens)),
        "qtd_lotes_origem_switching_potencialmente_ativos": int(qtd_origens_potencialmente_ativas),
        "risco_dupla_contagem_origem_switching": bool(qtd_origens_potencialmente_ativas > 0 and len(lotes_pos_switching_normalizados) > 0),
        "neutralizacao_temporal_origem_switching": "nao_realizada_nesta_microetapa",
    }

    auditoria_inventario_operacional = {
        **auditoria_inventario,
        "inventario_canonico_operacional_expandido": True,
        "qtd_lotes_inventario_canonico_base": int(len(inventario_canonico_base)),
        "qtd_lotes_pos_switching_integrados": int(len(lotes_pos_switching_normalizados)),
        "qtd_lotes_inventario_canonico_operacional": int(len(inventario_canonico_operacional)),
    }

    return PacoteDadosOperacionaisCanonicos(
        nome_aba_lotes=nome_aba_lotes,
        nome_aba_despesas=nome_aba_despesas,
        inventario_canonico=inventario_canonico_operacional,
        gastos_canonicos=gastos_canonicos,
        auditoria_inventario=auditoria_inventario_operacional,
        auditoria_gastos=auditoria_gastos,
        nome_aba_salarios=nome_aba_salarios,
        nome_aba_switching=nome_aba_switching,
        salarios_canonicos=salarios_canonicos,
        switching_canonico=switching_canonico,
        auditoria_salarios=auditoria_salarios,
        auditoria_switching=auditoria_switching,
        inventario_lotes_expandido=inventario_canonico_operacional,
        lotes_pos_switching_normalizados=lotes_pos_switching_normalizados,
        auditoria_inventario_expandido=auditoria_expandido,
    )


"""Canonização estrutural da aba Carteira.

Este módulo abre de forma restrita o bloco de produtos e carteira, limitando-se a:
- resolver colunas da aba Carteira com base no config;
- construir uma carteira canônica com `produto_key`;
- validar estrutura e consistência mínima;
- montar um mapa canônico simples de produtos.

Ele não cria ainda classes operacionais de produto, combos, switching ou cálculo
financeiro.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

import pandas as pd

from nucleo.leitor_planilha import PacotePlanilha, resolver_coluna
from nucleo.utilitarios_neutros import limpar_texto, para_bool, para_float_monetario, para_int, normalizar_texto


@dataclass(slots=True)
class PacoteCarteiraCanonica:
    nome_aba: str
    quadro_bruto: pd.DataFrame
    quadro_canonico: pd.DataFrame
    mapa_produtos: dict[str, dict[str, Any]]
    auditoria: dict[str, Any]
    validacao: dict[str, Any]


def normalizar_nome_produto(valor: Any) -> str:
    return normalizar_texto(valor)


def gerar_produto_key(produto_id: Any, nome_norm: str) -> str:
    produto_id_txt = "" if produto_id is None else str(produto_id).strip()
    if produto_id_txt:
        return produto_id_txt
    return f"prod::{nome_norm}"






def _normalizar_taxa_cdi(valor: Any, *, default: float = 0.0, limite_percentual_vs_multiplicador: float = 10.0) -> float:
    taxa = para_float_monetario(valor, default)
    if taxa >= limite_percentual_vs_multiplicador:
        return taxa / 100.0
    return taxa


def normalizar_carteira_bruta(df_carteira: pd.DataFrame, config: Mapping[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    campos = {
        "produto_id": resolver_coluna(df_carteira, config, "carteira", "produto_id", obrigatoria=False),
        "nome": resolver_coluna(df_carteira, config, "carteira", "nome", obrigatoria=True),
        "tipo": resolver_coluna(df_carteira, config, "carteira", "tipo", obrigatoria=False),
        "indexador": resolver_coluna(df_carteira, config, "carteira", "indexador", obrigatoria=False),
        "taxa_base": resolver_coluna(df_carteira, config, "carteira", "taxa_base", obrigatoria=True),
        "taxa_bonus": resolver_coluna(df_carteira, config, "carteira", "taxa_bonus", obrigatoria=False),
        "dias_bonus": resolver_coluna(df_carteira, config, "carteira", "dias_bonus", obrigatoria=False),
        "prazo_dias": resolver_coluna(df_carteira, config, "carteira", "prazo_dias", obrigatoria=False),
        "carencia_dias": resolver_coluna(df_carteira, config, "carteira", "carencia_dias", obrigatoria=False),
        "liquidez_dias": resolver_coluna(df_carteira, config, "carteira", "liquidez_dias", obrigatoria=False),
        "isento_ir": resolver_coluna(df_carteira, config, "carteira", "isento_ir", obrigatoria=False),
        "aplicacao_minima": resolver_coluna(df_carteira, config, "carteira", "aplicacao_minima", obrigatoria=False),
        "aplicacao_maxima": resolver_coluna(df_carteira, config, "carteira", "aplicacao_maxima", obrigatoria=False),
        "ativo": resolver_coluna(df_carteira, config, "carteira", "ativo", obrigatoria=False),
        "fgc": resolver_coluna(df_carteira, config, "carteira", "fgc", obrigatoria=False),
        "banco_emissor": resolver_coluna(df_carteira, config, "carteira", "banco_emissor", obrigatoria=False),
        "risco_real": resolver_coluna(df_carteira, config, "carteira", "risco_real", obrigatoria=False),
        "somente_combo": resolver_coluna(df_carteira, config, "carteira", "somente_combo", obrigatoria=False),
        "produto_base": resolver_coluna(df_carteira, config, "carteira", "produto_base", obrigatoria=False),
        "produto_bonus": resolver_coluna(df_carteira, config, "carteira", "produto_bonus", obrigatoria=False),
        "ratio_base": resolver_coluna(df_carteira, config, "carteira", "ratio_base", obrigatoria=False),
        "ratio_bonus": resolver_coluna(df_carteira, config, "carteira", "ratio_bonus", obrigatoria=False),
        "max_usos": resolver_coluna(df_carteira, config, "carteira", "max_usos", obrigatoria=False),
        "observacoes": resolver_coluna(df_carteira, config, "carteira", "observacoes", obrigatoria=False),
        "produto_padrao": resolver_coluna(df_carteira, config, "carteira", "produto_padrao", obrigatoria=False),
    }

    limite = para_float_monetario(
        (((config.get("politicas_taxa") or {}).get("limite_percentual_vs_multiplicador")) if isinstance(config, Mapping) else None),
        10.0,
    )

    auditoria = {
        "colunas_resolvidas": dict(campos),
        "linhas_descartadas": [],
        "sem_produto_id": 0,
        "produtos_total": 0,
        "limite_percentual_vs_multiplicador": limite,
    }

    registros: list[dict[str, Any]] = []
    for idx, row in df_carteira.iterrows():
        nome = limpar_texto(row[campos["nome"]]) if campos["nome"] in df_carteira.columns else ""
        if not nome:
            auditoria["linhas_descartadas"].append({"indice": int(idx), "motivo": "nome_vazio"})
            continue

        produto_id_raw = row[campos["produto_id"]] if campos["produto_id"] and campos["produto_id"] in df_carteira.columns else None
        if produto_id_raw is None or str(produto_id_raw).strip() == "":
            auditoria["sem_produto_id"] += 1

        nome_norm = normalizar_nome_produto(nome)
        produto_key = gerar_produto_key(produto_id_raw, nome_norm)

        registro = {
            "produto_key": produto_key,
            "produto_id_raw": None if produto_id_raw is None else limpar_texto(produto_id_raw),
            "nome": nome,
            "nome_norm": nome_norm,
            "tipo": limpar_texto(row[campos["tipo"]]) if campos["tipo"] else "",
            "indexador": limpar_texto(row[campos["indexador"]]) if campos["indexador"] else "",
            "taxa_base_cdi": _normalizar_taxa_cdi(row[campos["taxa_base"]], default=0.0, limite_percentual_vs_multiplicador=limite),
            "taxa_bonus_cdi": _normalizar_taxa_cdi(row[campos["taxa_bonus"]], default=0.0, limite_percentual_vs_multiplicador=limite) if campos["taxa_bonus"] else 0.0,
            "dias_bonus": para_int(row[campos["dias_bonus"]], 0) if campos["dias_bonus"] else 0,
            "prazo_dias": para_int(row[campos["prazo_dias"]], 0) if campos["prazo_dias"] else 0,
            "carencia_dias": para_int(row[campos["carencia_dias"]], 0) if campos["carencia_dias"] else 0,
            "liquidez_dias": para_int(row[campos["liquidez_dias"]], 0) if campos["liquidez_dias"] else 0,
            "isento_ir": para_bool(row[campos["isento_ir"]], False) if campos["isento_ir"] else False,
            "aplicacao_minima": para_float_monetario(row[campos["aplicacao_minima"]], 0.0) if campos["aplicacao_minima"] else 0.0,
            "aplicacao_maxima": para_float_monetario(row[campos["aplicacao_maxima"]], 0.0) if campos["aplicacao_maxima"] else 0.0,
            "ativo": para_bool(row[campos["ativo"]], True) if campos["ativo"] else True,
            "fgc": para_bool(row[campos["fgc"]], False) if campos["fgc"] else False,
            "banco_emissor": limpar_texto(row[campos["banco_emissor"]]) if campos["banco_emissor"] else "",
            "risco_real": limpar_texto(row[campos["risco_real"]]) if campos["risco_real"] else "",
            "somente_combo": para_bool(row[campos["somente_combo"]], False) if campos["somente_combo"] else False,
            "produto_base": limpar_texto(row[campos["produto_base"]]) if campos["produto_base"] else "",
            "produto_bonus": limpar_texto(row[campos["produto_bonus"]]) if campos["produto_bonus"] else "",
            "ratio_base": para_float_monetario(row[campos["ratio_base"]], 0.0) if campos["ratio_base"] else 0.0,
            "ratio_bonus": para_float_monetario(row[campos["ratio_bonus"]], 0.0) if campos["ratio_bonus"] else 0.0,
            "max_usos": para_int(row[campos["max_usos"]], 0) if campos["max_usos"] else 0,
            "observacoes": limpar_texto(row[campos["observacoes"]]) if campos["observacoes"] else "",
            "produto_padrao": para_bool(row[campos["produto_padrao"]], False) if campos["produto_padrao"] else False,
        }
        registros.append(registro)

    quadro_canonico = pd.DataFrame(registros)
    auditoria["produtos_total"] = int(len(quadro_canonico))
    return quadro_canonico, auditoria


def construir_mapa_produtos(quadro_canonico: pd.DataFrame) -> dict[str, dict[str, Any]]:
    mapa_by_key: dict[str, dict[str, Any]] = {}
    mapa_by_nome_norm: dict[str, str] = {}

    for _, row in quadro_canonico.iterrows():
        registro = row.to_dict()
        produto_key = str(registro["produto_key"])
        nome_norm = str(registro["nome_norm"])
        mapa_by_key[produto_key] = registro
        mapa_by_nome_norm[nome_norm] = produto_key

    return {
        "by_key": mapa_by_key,
        "by_nome_norm": mapa_by_nome_norm,
    }


def validar_carteira_canonica(quadro_canonico: pd.DataFrame) -> dict[str, Any]:
    validacao = {
        "ok": True,
        "erros": [],
        "avisos": [],
    }

    if quadro_canonico is None or len(quadro_canonico) == 0:
        validacao["ok"] = False
        validacao["erros"].append("carteira_canonica_vazia")
        return validacao

    if quadro_canonico["produto_key"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("produto_key_nulo")
    if quadro_canonico["produto_key"].duplicated().any():
        validacao["ok"] = False
        validacao["erros"].append("produto_key_duplicado")
    if quadro_canonico["nome_norm"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("nome_norm_nulo")
    if quadro_canonico["nome_norm"].duplicated().any():
        validacao["ok"] = False
        validacao["erros"].append("nome_norm_duplicado")

    if quadro_canonico["taxa_base_cdi"].isna().any():
        validacao["ok"] = False
        validacao["erros"].append("taxa_base_cdi_nula")
    if (quadro_canonico["taxa_base_cdi"] <= 0).any():
        validacao["avisos"].append("existem_taxas_base_nao_positivas")

    for campo in ("dias_bonus", "prazo_dias", "carencia_dias", "liquidez_dias", "max_usos"):
        if (quadro_canonico[campo] < 0).any():
            validacao["avisos"].append(f"{campo}_negativo")

    if (quadro_canonico["aplicacao_minima"] < 0).any():
        validacao["avisos"].append("aplicacao_minima_negativa")
    if (quadro_canonico["aplicacao_maxima"] < 0).any():
        validacao["avisos"].append("aplicacao_maxima_negativa")

    aplic_max = quadro_canonico["aplicacao_maxima"].fillna(0.0)
    aplic_min = quadro_canonico["aplicacao_minima"].fillna(0.0)
    if ((aplic_max > 0) & (aplic_max < aplic_min)).any():
        validacao["avisos"].append("aplicacao_maxima_menor_que_minima")

    qtd_produto_padrao = int(quadro_canonico["produto_padrao"].sum())
    if qtd_produto_padrao == 0:
        validacao["avisos"].append("nenhum_produto_padrao_marcado")
    elif qtd_produto_padrao > 1:
        validacao["avisos"].append("mais_de_um_produto_padrao_marcado")

    return validacao


def carregar_carteira_canonica(pacote_planilha: PacotePlanilha, config: Mapping[str, Any]) -> PacoteCarteiraCanonica:
    abas_cfg = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}
    nome_aba = str(abas_cfg.get("carteira", "Carteira"))

    if nome_aba not in pacote_planilha.quadros_brutos:
        raise KeyError(f"Aba de carteira não encontrada no pacote da planilha: {nome_aba}")

    quadro_bruto = pacote_planilha.quadros_brutos[nome_aba]
    quadro_canonico, auditoria = normalizar_carteira_bruta(quadro_bruto, config)
    mapa_produtos = construir_mapa_produtos(quadro_canonico)
    validacao = validar_carteira_canonica(quadro_canonico)

    return PacoteCarteiraCanonica(
        nome_aba=nome_aba,
        quadro_bruto=quadro_bruto,
        quadro_canonico=quadro_canonico,
        mapa_produtos=mapa_produtos,
        auditoria=auditoria,
        validacao=validacao,
    )

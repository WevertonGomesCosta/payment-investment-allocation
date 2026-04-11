from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tipos import (
    ConfigAbas,
    ConfigArquivos,
    ConfigColunasCarteiras,
    ConfigColunasGastos,
    ConfigColunasLotes,
    ConfigEscopoV1,
    ConfigExecucao,
    ConfigPoliticasModelo,
    ConfigPremissasMercado,
    ConfigProjeto,
    ConfigTributacao,
)


EXPECTED_ROOT_KEYS = {
    "arquivos",
    "abas",
    "colunas",
    "execucao",
    "premissas_mercado",
    "tributacao",
    "politicas_modelo",
    "escopo_v1",
}


class ConfigError(ValueError):
    """Erro semântico ou estrutural do arquivo de configuração."""



def _require_keys(data: dict[str, Any], required: set[str], where: str) -> None:
    missing = sorted(required - set(data.keys()))
    if missing:
        raise ConfigError(f"Chaves ausentes em {where}: {missing}")



def _strict_root_keys(data: dict[str, Any]) -> None:
    unknown = sorted(set(data.keys()) - EXPECTED_ROOT_KEYS)
    if unknown:
        raise ConfigError(
            "Config contém blocos fora do escopo v1: "
            f"{unknown}. Remova-os para manter a implementação metodológica enxuta."
        )



def load_config(path: str | Path, strict: bool = True) -> ConfigProjeto:
    raw_path = Path(path)
    with raw_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if strict:
        _strict_root_keys(raw)
    validate_config_minimo(raw)

    colunas = raw["colunas"]

    return ConfigProjeto(
        arquivos=ConfigArquivos(**raw["arquivos"]),
        abas=ConfigAbas(**raw["abas"]),
        colunas_gastos=ConfigColunasGastos(**colunas["gastos"]),
        colunas_lotes=ConfigColunasLotes(**colunas["lotes"]),
        colunas_carteiras=ConfigColunasCarteiras(**colunas["carteiras"]),
        execucao=ConfigExecucao(**raw["execucao"]),
        premissas_mercado=ConfigPremissasMercado(**raw["premissas_mercado"]),
        tributacao=ConfigTributacao(**raw["tributacao"]),
        politicas_modelo=ConfigPoliticasModelo(**raw["politicas_modelo"]),
        escopo_v1=ConfigEscopoV1(**raw["escopo_v1"]),
    )



def validate_config_minimo(raw: dict[str, Any]) -> None:
    _require_keys(raw, EXPECTED_ROOT_KEYS, "raiz")

    _require_keys(raw["arquivos"], {"planilha"}, "arquivos")
    _require_keys(raw["abas"], {"gastos", "lotes", "carteiras"}, "abas")
    _require_keys(raw["colunas"], {"gastos", "lotes", "carteiras"}, "colunas")

    _require_keys(
        raw["colunas"]["gastos"],
        {"data", "descricao", "valor", "pago", "lote_usado_1", "lote_usado_2"},
        "colunas.gastos",
    )
    _require_keys(
        raw["colunas"]["lotes"],
        {"id_lote", "data_entrada", "valor_original", "investimento"},
        "colunas.lotes",
    )
    _require_keys(
        raw["colunas"]["carteiras"],
        {
            "nome",
            "tipo",
            "indexador",
            "taxa_base",
            "taxa_bonus",
            "dias_bonus",
            "prazo_dias",
            "carencia_dias",
            "isento_ir",
            "aplicacao_minima",
            "aplicacao_maxima",
            "ativo",
            "somente_combo",
            "produto_base",
            "produto_bonus",
            "ratio_base",
            "ratio_bonus",
            "banco_emissor",
            "score_banco",
            "risco_real",
            "max_usos",
        },
        "colunas.carteiras",
    )

    _require_keys(
        raw["execucao"],
        {"timezone", "data_referencia_simulacao", "convencao_dias_ano"},
        "execucao",
    )
    _require_keys(
        raw["premissas_mercado"],
        {"cdi_anual_modelo", "selic_anual_modelo", "ipca_anual_modelo"},
        "premissas_mercado",
    )
    _require_keys(
        raw["tributacao"],
        {"usar_ir", "usar_iof", "criterio_limite_ir", "faixas_ir", "tabela_iof"},
        "tributacao",
    )
    _require_keys(
        raw["politicas_modelo"],
        {
            "tratar_pago_nulo_como_nao",
            "aceitar_multiplos_lotes_por_gasto",
            "permitir_split_resgate",
            "produto_inativo_em_novo_aporte",
            "produto_somente_combo_sem_decomposicao",
            "falha_reconciliacao_financeira",
        },
        "politicas_modelo",
    )
    _require_keys(
        raw["escopo_v1"],
        {
            "reconstruir_historico",
            "precificar_posicoes",
            "diagnosticar_pagamentos_futuros",
            "avaliar_aportes",
            "avaliar_switching",
            "buscar_cenario_otimo",
        },
        "escopo_v1",
    )

    if not isinstance(raw["tributacao"]["faixas_ir"], list) or not raw["tributacao"]["faixas_ir"]:
        raise ConfigError("tributacao.faixas_ir deve ser uma lista não vazia.")

    if not isinstance(raw["tributacao"]["tabela_iof"], list):
        raise ConfigError("tributacao.tabela_iof deve ser lista.")

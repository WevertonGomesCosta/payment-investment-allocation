"""Carregamento e resolução do config canônico do projeto.

Este módulo foi reconstruído para ficar mais neutro e mais aderente ao bloco
já auditado dos scripts-base, sem ainda assumir contratos de domínio mais
profundos.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from nucleo.ambiente import detectar_raiz_repositorio
from nucleo.config_utils import obter_config as obter_config_compartilhado

ARQUIVOS_CONFIG_PADRAO: tuple[str, ...] = (
    "config_atualizado_revisado_v7_populacao_inicial.json",
    "config_atualizado_revisado_v6_avaliacao.json",
    "config_atualizado_revisado_v5_otimizacao_bounds.json",
    "config_atualizado_revisado_v4_otimizacao.json",
    "config_atualizado_revisado_v3_treinamento.json",
    "config_atualizado_revisado_v2.json",
    "config_atualizado.json",
    "config.json",
)

VARIAVEIS_AMBIENTE_CONFIG: tuple[str, ...] = (
    "PAYMENT_INVESTMENT_ALLOCATION_CONFIG",
    "OTIMIZADOR_CONFIG",
)

CAMINHOS_OBRIGATORIOS_NUCLEO: tuple[tuple[str, ...], ...] = (
    ("execucao", "timezone"),
    ("arquivos", "planilha"),
    ("abas", "carteira"),
    ("abas", "lotes"),
    ("abas", "despesas"),
    ("colunas", "carteira"),
    ("colunas", "lotes"),
    ("colunas", "despesas"),
)


@dataclass(slots=True)
class PacoteConfig:
    caminho: Path
    raiz_repositorio: Path
    diretorio_dados: Path
    conteudo: dict[str, Any]


def _candidatos_config(raiz_repositorio: Path, nomes: Sequence[str]) -> list[Path]:
    candidatos: list[Path] = []
    for nome in nomes:
        candidatos.append((raiz_repositorio / "dados" / nome).resolve())
        candidatos.append((raiz_repositorio / "data" / nome).resolve())
        candidatos.append((raiz_repositorio / nome).resolve())
    vistos: set[Path] = set()
    ordenados: list[Path] = []
    for caminho in candidatos:
        if caminho not in vistos:
            ordenados.append(caminho)
            vistos.add(caminho)
    return ordenados


def resolver_caminho_config(
    caminho_explicito: Optional[str | Path] = None,
    *,
    raiz_repositorio: Optional[Path] = None,
    nomes_padrao: Iterable[str] = ARQUIVOS_CONFIG_PADRAO,
) -> Path:
    raiz = (raiz_repositorio or detectar_raiz_repositorio()).resolve()

    if caminho_explicito is not None:
        caminho = Path(caminho_explicito).expanduser().resolve()
        if not caminho.exists():
            raise FileNotFoundError(f"Config explícito não encontrado: {caminho}")
        return caminho

    for variavel in VARIAVEIS_AMBIENTE_CONFIG:
        valor = os.environ.get(variavel)
        if valor:
            caminho = Path(valor).expanduser().resolve()
            if caminho.exists():
                return caminho
            raise FileNotFoundError(f"Config apontado por {variavel} não encontrado: {caminho}")

    candidatos = _candidatos_config(raiz, list(nomes_padrao))
    for candidato in candidatos:
        if candidato.exists():
            return candidato

    caminhos_testados = "\n - ".join(str(c) for c in candidatos)
    raise FileNotFoundError(
        f"Nenhum arquivo de configuração encontrado. Caminhos testados:\n - {caminhos_testados}"
    )


def carregar_config(
    caminho_explicito: Optional[str | Path] = None,
    *,
    raiz_repositorio: Optional[Path] = None,
) -> PacoteConfig:
    raiz = (raiz_repositorio or detectar_raiz_repositorio()).resolve()
    caminho = resolver_caminho_config(caminho_explicito, raiz_repositorio=raiz)

    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except Exception as erro:
        raise RuntimeError(f"Falha ao ler o arquivo de configuração {caminho}: {erro}") from erro

    if not isinstance(conteudo, dict):
        raise RuntimeError(f"O arquivo de configuração {caminho} deve conter um objeto JSON na raiz.")

    validar_config_nucleo(conteudo)

    diretorio_dados = (raiz / "dados") if (raiz / "dados").exists() else (raiz / "data")
    return PacoteConfig(
        caminho=caminho,
        raiz_repositorio=raiz,
        diretorio_dados=diretorio_dados,
        conteudo=conteudo,
    )


def obter_config(config: dict[str, Any], *caminho: str, padrao: Any = None) -> Any:
    return obter_config_compartilhado(config, *caminho, padrao=padrao)


def obter_config_obrigatorio(config: dict[str, Any], *caminho: str) -> Any:
    atual: Any = config
    for chave in caminho:
        if not isinstance(atual, dict) or chave not in atual:
            raise KeyError(f"Config obrigatório ausente: {'/'.join(caminho)}")
        atual = atual[chave]
    return atual


def obter_primeiro_config_disponivel(
    config: dict[str, Any],
    caminhos: Iterable[Sequence[str]],
    *,
    padrao: Any = None,
) -> Any:
    for caminho in caminhos:
        valor = obter_config(config, *caminho, padrao=None)
        if valor is not None:
            return valor
    return padrao


def validar_config_nucleo(config: dict[str, Any]) -> None:
    for caminho in CAMINHOS_OBRIGATORIOS_NUCLEO:
        valor = obter_config_obrigatorio(config, *caminho)
        if valor in (None, ""):
            raise ValueError(f"Config obrigatório vazio: {'/'.join(caminho)}")

    for secao in ("carteira", "lotes", "despesas"):
        aliases = obter_config_obrigatorio(config, "colunas", secao)
        if not isinstance(aliases, dict) or not aliases:
            raise ValueError(f"Config inválido: colunas/{secao} deve ser um dicionário não vazio.")

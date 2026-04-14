"""Leitura e canonização inicial da planilha base do projeto.

Este módulo permanece propositalmente restrito à leitura estrutural e à
canonização inicial das colunas. Ele não cria ainda entidades finais nem
implementa derivação financeira profunda.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

import pandas as pd


@dataclass(slots=True)
class PacotePlanilha:
    caminho: Path
    nomes_abas: list[str]
    quadros_brutos: dict[str, pd.DataFrame]
    quadros_canonicos: dict[str, pd.DataFrame]


def _remover_acentos(texto: str) -> str:
    return "".join(
        caractere for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    )


def normalizar_texto(texto: Any) -> str:
    texto = "" if texto is None else str(texto)
    texto = _remover_acentos(texto).strip().lower()
    for antigo, novo in [("/", " "), ("-", " "), ("(", " "), (")", " ")]:
        texto = texto.replace(antigo, novo)
    return " ".join(texto.split())


def construir_mapa_alias(mapa_alias: Mapping[str, Iterable[str]]) -> dict[str, str]:
    mapa: dict[str, str] = {}
    for nome_canonico, aliases in mapa_alias.items():
        mapa[normalizar_texto(nome_canonico)] = nome_canonico
        for alias in aliases:
            mapa[normalizar_texto(alias)] = nome_canonico
    return mapa


def canonizar_colunas(
    quadro: pd.DataFrame,
    mapa_alias: Optional[Mapping[str, Iterable[str]]] = None,
) -> pd.DataFrame:
    quadro_canonico = quadro.copy()
    if not mapa_alias:
        quadro_canonico.columns = [normalizar_texto(coluna) for coluna in quadro_canonico.columns]
        return quadro_canonico

    lookup = construir_mapa_alias(mapa_alias)
    renomear: dict[str, str] = {}
    destinos_usados: set[str] = set()

    for original in quadro_canonico.columns:
        normalizado = normalizar_texto(original)
        destino = lookup.get(normalizado, normalizado)
        if destino in destinos_usados:
            sufixo = 2
            candidato = f"{destino}__dup{sufixo}"
            while candidato in destinos_usados:
                sufixo += 1
                candidato = f"{destino}__dup{sufixo}"
            destino = candidato
        renomear[original] = destino
        destinos_usados.add(destino)

    return quadro_canonico.rename(columns=renomear)


def aliases_coluna(config: Mapping[str, Any], secao: str, chave: str) -> list[str]:
    colunas_cfg = config.get("colunas", {}) if isinstance(config.get("colunas"), Mapping) else {}
    secao_cfg = colunas_cfg.get(secao, {}) if isinstance(colunas_cfg.get(secao), Mapping) else {}
    aliases = secao_cfg.get(chave)
    if aliases is None:
        raise KeyError(f"Config de coluna ausente para {secao}/{chave}.")
    if not isinstance(aliases, list) or not aliases:
        raise KeyError(f"Aliases de coluna inválidos para {secao}/{chave}.")
    return [str(alias) for alias in aliases]


def resolver_coluna(
    df: pd.DataFrame,
    config: Mapping[str, Any],
    secao: str,
    chave: str,
    obrigatoria: bool = True,
) -> Optional[str]:
    if df is None or len(getattr(df, "columns", [])) == 0:
        if obrigatoria:
            raise KeyError(f"DataFrame vazio ao resolver coluna {secao}/{chave}.")
        return None

    cols_reais = list(df.columns)
    mapa_norm = {normalizar_texto(c): c for c in cols_reais}

    try:
        aliases = aliases_coluna(config, secao, chave)
    except Exception:
        if obrigatoria:
            raise
        return None

    for alias in aliases:
        alias_norm = normalizar_texto(alias)
        if alias_norm in mapa_norm:
            return str(mapa_norm[alias_norm])

    if obrigatoria:
        raise KeyError(
            f"Coluna não encontrada para {secao}/{chave}. "
            f"Aliases tentados: {aliases}. Colunas disponíveis: {cols_reais}"
        )
    return None


def resolver_caminho_planilha(
    config: Mapping[str, Any],
    *,
    raiz_repositorio: Optional[Path] = None,
    caminho_explicito: Optional[str | Path] = None,
) -> Path:
    if caminho_explicito is not None:
        caminho = Path(caminho_explicito).expanduser().resolve()
        if not caminho.exists():
            raise FileNotFoundError(f"Planilha explícita não encontrada: {caminho}")
        return caminho

    raiz = (raiz_repositorio or Path.cwd()).resolve()
    arquivos_cfg = config.get("arquivos", {}) if isinstance(config.get("arquivos"), Mapping) else {}
    nome_arquivo = arquivos_cfg.get("planilha", "dados_financeiros.xlsx")

    candidatos = [
        raiz / "dados" / nome_arquivo,
        raiz / "data" / nome_arquivo,
        raiz / nome_arquivo,
    ]
    for candidato in candidatos:
        if candidato.exists():
            return candidato.resolve()

    caminhos_testados = "\n - ".join(str(c) for c in candidatos)
    raise FileNotFoundError(f"Planilha não encontrada. Caminhos testados:\n - {caminhos_testados}")


def carregar_planilha(
    config: Mapping[str, Any],
    *,
    raiz_repositorio: Optional[Path] = None,
    caminho_explicito: Optional[str | Path] = None,
    carregar_todas_as_abas: bool = True,
) -> PacotePlanilha:
    caminho_planilha = resolver_caminho_planilha(
        config,
        raiz_repositorio=raiz_repositorio,
        caminho_explicito=caminho_explicito,
    )

    excel = pd.ExcelFile(caminho_planilha)
    quadros_brutos: dict[str, pd.DataFrame] = {}
    quadros_canonicos: dict[str, pd.DataFrame] = {}

    abas_alvo = list(excel.sheet_names) if carregar_todas_as_abas else []
    abas_config = config.get("abas", {}) if isinstance(config.get("abas"), Mapping) else {}
    aliases_por_bloco = config.get("colunas", {}) if isinstance(config.get("colunas"), Mapping) else {}

    for nome_bloco, nome_aba in abas_config.items():
        if nome_aba in excel.sheet_names and nome_aba not in abas_alvo:
            abas_alvo.append(nome_aba)

    for nome_aba in abas_alvo:
        quadro = pd.read_excel(caminho_planilha, sheet_name=nome_aba)
        quadros_brutos[nome_aba] = quadro

        nome_bloco = next(
            (bloco for bloco, aba_cfg in abas_config.items() if aba_cfg == nome_aba),
            None,
        )
        mapa_alias = aliases_por_bloco.get(nome_bloco, {}) if nome_bloco else {}
        quadros_canonicos[nome_aba] = canonizar_colunas(quadro, mapa_alias=mapa_alias)

    return PacotePlanilha(
        caminho=caminho_planilha,
        nomes_abas=list(excel.sheet_names),
        quadros_brutos=quadros_brutos,
        quadros_canonicos=quadros_canonicos,
    )


def construir_resumo_planilha(pacote: PacotePlanilha) -> list[dict[str, Any]]:
    resumo: list[dict[str, Any]] = []
    for nome_aba in pacote.nomes_abas:
        quadro = pacote.quadros_brutos.get(nome_aba)
        if quadro is None:
            continue
        resumo.append(
            {
                "nome_aba": nome_aba,
                "n_linhas": int(quadro.shape[0]),
                "n_colunas": int(quadro.shape[1]),
                "colunas": list(map(str, quadro.columns)),
            }
        )
    return resumo

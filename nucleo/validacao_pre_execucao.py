"""Gate puro de validação pré-execução.

Este módulo implementa a Etapa 2 do macrofluxo operacional.

Responsabilidade:
- validar os artefatos já produzidos pela Etapa 1;
- retornar erros bloqueantes, avisos e evidências;
- impedir avanço para a Etapa 3 quando houver falha estrutural.

Proibições:
- não baixa planilha;
- não carrega planilha;
- não abre workbook;
- não resolve colunas para uso operacional;
- não canoniza colunas;
- não transforma dados;
- não decide pagamento, switching, ranking ou saída.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
import math
import unicodedata

import pandas as pd

from nucleo.ambiente import ContextoExecucao
from nucleo.carregador_config import PacoteConfig
from nucleo.entrada_resolvida import (
    AuditoriaCacheCDI,
    AuditoriaEntradaBruta,
    AuditoriaResolucaoEntrada,
    JanelaConsultaCDI,
    MapaAbasResolvidas,
    MapaColunasResolvidas,
    PacoteEntradaResolvida,
)
from nucleo.leitor_planilha import PacotePlanilha


ABAS_OPERACIONAIS_OBRIGATORIAS: tuple[str, ...] = (
    "carteira",
    "salarios",
    "despesas",
    "switching",
    "lotes",
)

COLUNAS_CRITICAS_OBRIGATORIAS: dict[str, tuple[str, ...]] = {
    "carteira": ("nome", "taxa_base"),
    "salarios": ("data_recebimento", "valor_bruto"),
    "despesas": ("data", "descricao", "valor", "pago"),
    "switching": (
        "lote_id_antes",
        "lote_id_depois",
        "data_aplicacao",
        "valor_liquido_migrado",
        "investimento",
    ),
    "lotes": ("lote_id", "data_aplicacao", "valor_original", "produto_id"),
}

COLUNAS_DATA_CRITICAS: dict[str, tuple[str, ...]] = {
    "salarios": ("data_recebimento",),
    "despesas": ("data",),
    "switching": ("data_aplicacao",),
    "lotes": ("data_aplicacao",),
}

COLUNAS_NUMERICAS_CRITICAS: dict[str, tuple[str, ...]] = {
    "carteira": ("taxa_base",),
    "salarios": ("valor_bruto",),
    "despesas": ("valor",),
    "switching": ("valor_liquido_migrado",),
    "lotes": ("valor_original",),
}


@dataclass(slots=True)
class PacoteValidacaoPreExecucao:
    ok: bool
    erros_bloqueantes: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    evidencias: dict[str, Any] = field(default_factory=dict)


def _registrar_erro(erros: list[str], mensagem: str) -> None:
    erros.append(str(mensagem))


def _registrar_aviso(avisos: list[str], mensagem: str) -> None:
    avisos.append(str(mensagem))


def _path_existe(valor: Any) -> bool:
    try:
        return Path(valor).exists()
    except Exception:
        return False


def _normalizar_token(valor: Any) -> str:
    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.replace("_", " ")
    texto = " ".join(texto.split())
    return texto


def _serie_nao_vazia(serie: pd.Series) -> pd.Series:
    if serie is None:
        return pd.Series(dtype=object)
    mascara = serie.notna()
    valores = serie.loc[mascara]
    if valores.empty:
        return valores
    texto = valores.astype(str).str.strip()
    return valores.loc[~texto.isin(("", "nan", "None", "NaT"))]


def _mapear_colunas_por_alias(
    quadro: pd.DataFrame,
    aliases_secao: dict[str, Any],
    chaves: tuple[str, ...],
) -> tuple[dict[str, str], dict[str, list[str]], list[str]]:
    colunas_reais = list(getattr(quadro, "columns", []))
    lookup = {_normalizar_token(col): str(col) for col in colunas_reais}

    encontradas: dict[str, str] = {}
    aliases_testados: dict[str, list[str]] = {}
    ausentes: list[str] = []

    for chave in chaves:
        aliases = aliases_secao.get(chave)
        if not isinstance(aliases, list) or not aliases:
            aliases_testados[chave] = []
            ausentes.append(chave)
            continue

        aliases_texto = [str(alias) for alias in aliases]
        aliases_testados[chave] = aliases_texto

        coluna_encontrada = None
        for alias in aliases_texto:
            coluna_encontrada = lookup.get(_normalizar_token(alias))
            if coluna_encontrada is not None:
                break

        if coluna_encontrada is None:
            ausentes.append(chave)
        else:
            encontradas[chave] = coluna_encontrada

    return encontradas, aliases_testados, ausentes


def _converter_numero_validacao(valor: Any) -> float | None:
    if valor is None:
        return None
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        try:
            if math.isnan(float(valor)):
                return None
        except Exception:
            pass
        return float(valor)

    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", "nat"}:
        return None

    texto = texto.replace("R$", "").replace("%", "").strip()
    texto = texto.replace(" ", "")

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except Exception:
        return None


def _validar_datas_minimas(
    bloco: str,
    quadro: pd.DataFrame,
    colunas_encontradas: dict[str, str],
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    for chave in COLUNAS_DATA_CRITICAS.get(bloco, ()):
        coluna = colunas_encontradas.get(chave)
        if not coluna:
            continue

        serie = _serie_nao_vazia(quadro[coluna])
        total = int(len(serie))
        if total == 0:
            _registrar_erro(erros, f"Campo crítico de data vazio em {bloco}/{chave}: coluna {coluna}")
            evidencias[f"{bloco}_{chave}_datas_parseaveis"] = 0
            evidencias[f"{bloco}_{chave}_datas_total"] = 0
            continue

        datas = pd.to_datetime(serie, errors="coerce", dayfirst=True)
        parseaveis = int(datas.notna().sum())

        evidencias[f"{bloco}_{chave}_datas_parseaveis"] = parseaveis
        evidencias[f"{bloco}_{chave}_datas_total"] = total

        if parseaveis == 0:
            _registrar_erro(erros, f"Nenhum valor de data interpretável em {bloco}/{chave}: coluna {coluna}")
        elif parseaveis < total:
            _registrar_aviso(
                avisos,
                f"Há valores de data não interpretáveis em {bloco}/{chave}: {total - parseaveis}/{total}",
            )


def _validar_numeros_minimos(
    bloco: str,
    quadro: pd.DataFrame,
    colunas_encontradas: dict[str, str],
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    for chave in COLUNAS_NUMERICAS_CRITICAS.get(bloco, ()):
        coluna = colunas_encontradas.get(chave)
        if not coluna:
            continue

        serie = _serie_nao_vazia(quadro[coluna])
        total = int(len(serie))
        if total == 0:
            _registrar_erro(erros, f"Campo crítico numérico vazio em {bloco}/{chave}: coluna {coluna}")
            evidencias[f"{bloco}_{chave}_numeros_parseaveis"] = 0
            evidencias[f"{bloco}_{chave}_numeros_total"] = 0
            continue

        convertidos = serie.map(_converter_numero_validacao)
        parseaveis = int(convertidos.notna().sum())

        evidencias[f"{bloco}_{chave}_numeros_parseaveis"] = parseaveis
        evidencias[f"{bloco}_{chave}_numeros_total"] = total

        if parseaveis == 0:
            _registrar_erro(erros, f"Nenhum valor numérico interpretável em {bloco}/{chave}: coluna {coluna}")
        elif parseaveis < total:
            _registrar_aviso(
                avisos,
                f"Há valores numéricos não interpretáveis em {bloco}/{chave}: {total - parseaveis}/{total}",
            )


def _validar_pacote_config(pacote_config: PacoteConfig, erros: list[str], evidencias: dict[str, Any]) -> None:
    if pacote_config is None:
        _registrar_erro(erros, "PacoteConfig ausente.")
        return

    evidencias["config_caminho"] = str(getattr(pacote_config, "caminho", ""))
    evidencias["config_raiz_repositorio"] = str(getattr(pacote_config, "raiz_repositorio", ""))
    evidencias["config_diretorio_dados"] = str(getattr(pacote_config, "diretorio_dados", ""))

    if not _path_existe(getattr(pacote_config, "caminho", None)):
        _registrar_erro(erros, f"Arquivo de config inexistente: {getattr(pacote_config, 'caminho', None)}")

    if not _path_existe(getattr(pacote_config, "raiz_repositorio", None)):
        _registrar_erro(erros, f"Raiz do repositório inexistente: {getattr(pacote_config, 'raiz_repositorio', None)}")

    if not _path_existe(getattr(pacote_config, "diretorio_dados", None)):
        _registrar_erro(erros, f"Diretório de dados inexistente: {getattr(pacote_config, 'diretorio_dados', None)}")

    conteudo = getattr(pacote_config, "conteudo", None)
    if not isinstance(conteudo, dict):
        _registrar_erro(erros, "Conteúdo do PacoteConfig não é dict.")
        return

    abas_cfg = conteudo.get("abas")
    if not isinstance(abas_cfg, dict):
        _registrar_erro(erros, "Config sem seção 'abas' válida.")
        return

    colunas_cfg = conteudo.get("colunas")
    if not isinstance(colunas_cfg, dict):
        _registrar_erro(erros, "Config sem seção 'colunas' válida.")
        return

    for chave in ABAS_OPERACIONAIS_OBRIGATORIAS:
        nome_aba = abas_cfg.get(chave)
        if not nome_aba:
            _registrar_erro(erros, f"Config sem abas/{chave}.")
        if chave not in colunas_cfg or not isinstance(colunas_cfg.get(chave), dict) or not colunas_cfg.get(chave):
            _registrar_erro(erros, f"Config sem colunas/{chave} como dicionário não vazio.")


def _validar_contexto_execucao(
    contexto_execucao: ContextoExecucao,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if contexto_execucao is None:
        _registrar_erro(erros, "ContextoExecucao ausente.")
        return

    evidencias["execucao_raiz_repositorio"] = str(getattr(contexto_execucao, "raiz_repositorio", ""))
    evidencias["execucao_diretorio_dados"] = str(getattr(contexto_execucao, "diretorio_dados", ""))
    evidencias["execucao_timezone"] = str(getattr(contexto_execucao, "timezone_nome", ""))
    evidencias["execucao_data_referencia"] = str(getattr(contexto_execucao, "data_referencia", ""))
    evidencias["execucao_warnings_configurados"] = bool(getattr(contexto_execucao, "warnings_configurados", False))

    if not _path_existe(getattr(contexto_execucao, "raiz_repositorio", None)):
        _registrar_erro(erros, f"Raiz do repositório inválida no ContextoExecucao: {getattr(contexto_execucao, 'raiz_repositorio', None)}")

    if not _path_existe(getattr(contexto_execucao, "diretorio_dados", None)):
        _registrar_erro(erros, f"Diretório de dados inválido no ContextoExecucao: {getattr(contexto_execucao, 'diretorio_dados', None)}")

    if not getattr(contexto_execucao, "timezone_nome", None):
        _registrar_erro(erros, "Timezone ausente no ContextoExecucao.")

    if getattr(contexto_execucao, "data_referencia", None) is None:
        _registrar_erro(erros, "Data de referência ausente no ContextoExecucao.")

    relatorio_dependencias = getattr(contexto_execucao, "relatorio_dependencias", None)
    if not isinstance(relatorio_dependencias, dict):
        _registrar_erro(erros, "Relatório de dependências ausente ou inválido no ContextoExecucao.")
    elif relatorio_dependencias.get("ausentes"):
        _registrar_aviso(avisos, f"Dependências ausentes reportadas: {relatorio_dependencias.get('ausentes')}")


def _validar_pacote_planilha_basico_sem_alias(
    pacote_planilha: PacotePlanilha,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if pacote_planilha is None:
        _registrar_erro(erros, "PacotePlanilha ausente.")
        return

    evidencias["planilha_caminho"] = str(getattr(pacote_planilha, "caminho", ""))
    evidencias["planilha_qtd_abas"] = len(getattr(pacote_planilha, "nomes_abas", []) or [])

    if not _path_existe(getattr(pacote_planilha, "caminho", None)):
        _registrar_erro(erros, f"Caminho da planilha inexistente: {getattr(pacote_planilha, 'caminho', None)}")

    nomes_abas = getattr(pacote_planilha, "nomes_abas", None)
    if not isinstance(nomes_abas, list) or not nomes_abas:
        _registrar_erro(erros, "Lista de abas ausente ou vazia no PacotePlanilha.")

    quadros_brutos = getattr(pacote_planilha, "quadros_brutos", None)
    if not isinstance(quadros_brutos, dict) or not quadros_brutos:
        _registrar_erro(erros, "quadros_brutos ausente, vazio ou inválido no PacotePlanilha.")
    else:
        evidencias["planilha_qtd_quadros_brutos"] = len(quadros_brutos)

    quadros_estruturais = getattr(pacote_planilha, "quadros_estruturais_resolvidos", None)
    if quadros_estruturais is None:
        quadros_estruturais = getattr(pacote_planilha, "quadros_canonicos", None)
    if not isinstance(quadros_estruturais, dict) or not quadros_estruturais:
        _registrar_erro(erros, "quadros_estruturais_resolvidos ausente, vazio ou inválido no PacotePlanilha.")
    else:
        evidencias["planilha_qtd_quadros_estruturais_resolvidos"] = len(quadros_estruturais)

    auditoria = getattr(pacote_planilha, "auditoria", None)
    if not isinstance(auditoria, dict):
        _registrar_erro(erros, "Auditoria da planilha ausente ou inválida.")
        auditoria = {}

    for chave in ("fonte_planilha", "fetch_status_planilha", "caminho_planilha", "qtd_abas_planilha"):
        if chave not in auditoria:
            _registrar_erro(erros, f"Auditoria da planilha sem campo obrigatório: {chave}")

    evidencias["planilha_fonte"] = auditoria.get("fonte_planilha")
    evidencias["planilha_fetch_status"] = auditoria.get("fetch_status_planilha")

    validacao = getattr(pacote_planilha, "validacao", None)
    if not isinstance(validacao, dict):
        _registrar_erro(erros, "Validação inicial da planilha ausente ou inválida.")
    else:
        evidencias["planilha_validacao_ok"] = validacao.get("ok")
        if validacao.get("erros"):
            _registrar_erro(erros, f"Erros prévios reportados pela Etapa 1: {validacao.get('erros')}")
        for aviso in validacao.get("avisos", []) or []:
            _registrar_aviso(avisos, f"Aviso prévio da Etapa 1: {aviso}")


def _validar_pacote_planilha(
    pacote_planilha: PacotePlanilha,
    pacote_config: PacoteConfig,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if pacote_planilha is None:
        _registrar_erro(erros, "PacotePlanilha ausente.")
        return

    evidencias["planilha_caminho"] = str(getattr(pacote_planilha, "caminho", ""))
    evidencias["planilha_qtd_abas"] = len(getattr(pacote_planilha, "nomes_abas", []) or [])

    if not _path_existe(getattr(pacote_planilha, "caminho", None)):
        _registrar_erro(erros, f"Caminho da planilha inexistente: {getattr(pacote_planilha, 'caminho', None)}")

    nomes_abas = getattr(pacote_planilha, "nomes_abas", None)
    if not isinstance(nomes_abas, list) or not nomes_abas:
        _registrar_erro(erros, "Lista de abas ausente ou vazia no PacotePlanilha.")
        nomes_abas = []

    quadros_brutos = getattr(pacote_planilha, "quadros_brutos", None)
    if not isinstance(quadros_brutos, dict):
        _registrar_erro(erros, "quadros_brutos ausente ou inválido no PacotePlanilha.")
        quadros_brutos = {}

    auditoria = getattr(pacote_planilha, "auditoria", None)
    if not isinstance(auditoria, dict):
        _registrar_erro(erros, "Auditoria da planilha ausente ou inválida.")
        auditoria = {}

    for chave in ("fonte_planilha", "fetch_status_planilha", "caminho_planilha", "qtd_abas_planilha"):
        if chave not in auditoria:
            _registrar_erro(erros, f"Auditoria da planilha sem campo obrigatório: {chave}")

    evidencias["planilha_fonte"] = auditoria.get("fonte_planilha")
    evidencias["planilha_fetch_status"] = auditoria.get("fetch_status_planilha")

    validacao = getattr(pacote_planilha, "validacao", None)
    if not isinstance(validacao, dict):
        _registrar_erro(erros, "Validação inicial da planilha ausente ou inválida.")
    else:
        evidencias["planilha_validacao_ok"] = validacao.get("ok")
        if validacao.get("erros"):
            _registrar_erro(erros, f"Erros prévios reportados pela Etapa 1: {validacao.get('erros')}")
        for aviso in validacao.get("avisos", []) or []:
            _registrar_aviso(avisos, f"Aviso prévio da Etapa 1: {aviso}")

    conteudo = getattr(pacote_config, "conteudo", {}) if pacote_config is not None else {}
    abas_cfg = conteudo.get("abas", {}) if isinstance(conteudo, dict) else {}
    colunas_cfg = conteudo.get("colunas", {}) if isinstance(conteudo, dict) else {}

    abas_obrigatorias: dict[str, str] = {}
    for chave in ABAS_OPERACIONAIS_OBRIGATORIAS:
        nome_aba = abas_cfg.get(chave)
        if nome_aba:
            abas_obrigatorias[chave] = str(nome_aba)

    evidencias["abas_obrigatorias"] = dict(abas_obrigatorias)

    for bloco, nome_aba in abas_obrigatorias.items():
        if nome_aba not in nomes_abas:
            _registrar_erro(erros, f"Aba obrigatória ausente na planilha: {bloco} -> {nome_aba}")
            continue

        quadro = quadros_brutos.get(nome_aba)
        if quadro is None:
            _registrar_erro(erros, f"Quadro bruto ausente para aba obrigatória: {nome_aba}")
            continue

        shape = getattr(quadro, "shape", None)
        evidencias[f"aba_{bloco}_shape"] = tuple(shape) if shape is not None else None

        if not shape or len(shape) != 2:
            _registrar_erro(erros, f"Quadro bruto sem shape tabular válido para aba: {nome_aba}")
            continue

        n_linhas, n_colunas = int(shape[0]), int(shape[1])
        if n_colunas <= 0:
            _registrar_erro(erros, f"Aba obrigatória sem colunas: {nome_aba}")
        if n_linhas <= 0:
            _registrar_erro(erros, f"Aba obrigatória sem linhas: {nome_aba}")

        aliases_secao = colunas_cfg.get(bloco)
        if not isinstance(aliases_secao, dict):
            _registrar_erro(erros, f"Config sem aliases válidos para bloco {bloco}.")
            continue

        colunas_criticas = COLUNAS_CRITICAS_OBRIGATORIAS.get(bloco, ())
        encontradas, aliases_testados, ausentes = _mapear_colunas_por_alias(
            quadro,
            aliases_secao,
            colunas_criticas,
        )

        evidencias[f"{bloco}_colunas_criticas_encontradas"] = dict(encontradas)
        evidencias[f"{bloco}_colunas_criticas_ausentes"] = list(ausentes)
        evidencias[f"{bloco}_aliases_testados"] = dict(aliases_testados)

        for chave_ausente in ausentes:
            _registrar_erro(erros, f"Coluna crítica ausente em {bloco}/{chave_ausente} na aba {nome_aba}.")

        _validar_datas_minimas(bloco, quadro, encontradas, erros, avisos, evidencias)
        _validar_numeros_minimos(bloco, quadro, encontradas, erros, avisos, evidencias)


def _validar_pacote_entrada_resolvida_estrutura(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
    erros: list[str],
    evidencias: dict[str, Any],
) -> None:
    if not isinstance(pacote_entrada_resolvida, PacoteEntradaResolvida):
        _registrar_erro(erros, "Objeto recebido não é PacoteEntradaResolvida.")
        evidencias["pacote_entrada_resolvida_tipo"] = type(pacote_entrada_resolvida).__name__
        return

    evidencias["pacote_entrada_resolvida_tipo"] = type(pacote_entrada_resolvida).__name__
    evidencias["pacote_entrada_resolvida_metadados"] = dict(pacote_entrada_resolvida.metadados or {})

    campos = {
        "pacote_config": pacote_entrada_resolvida.pacote_config,
        "contexto_execucao": pacote_entrada_resolvida.contexto_execucao,
        "pacote_planilha": pacote_entrada_resolvida.pacote_planilha,
        "mapa_abas_resolvidas": pacote_entrada_resolvida.mapa_abas_resolvidas,
        "mapa_colunas_resolvidas": pacote_entrada_resolvida.mapa_colunas_resolvidas,
        "quadros_brutos": pacote_entrada_resolvida.quadros_brutos,
        "quadros_estruturais_resolvidos": pacote_entrada_resolvida.quadros_estruturais_resolvidos,
        "janela_consulta_cdi": pacote_entrada_resolvida.janela_consulta_cdi,
        "pacote_cache_cdi": pacote_entrada_resolvida.pacote_cache_cdi,
        "auditoria_entrada_bruta": pacote_entrada_resolvida.auditoria_entrada_bruta,
        "auditoria_resolucao_entrada": pacote_entrada_resolvida.auditoria_resolucao_entrada,
        "auditoria_cache_cdi": pacote_entrada_resolvida.auditoria_cache_cdi,
    }
    for nome, valor in campos.items():
        evidencias[f"pacote_entrada_resolvida_{nome}_presente"] = valor is not None
        if valor is None:
            _registrar_erro(erros, f"PacoteEntradaResolvida sem componente obrigatório: {nome}")


def _validar_mapa_abas_resolvidas(
    mapa_abas_resolvidas: MapaAbasResolvidas,
    pacote_planilha: PacotePlanilha,
    erros: list[str],
    evidencias: dict[str, Any],
) -> dict[str, str]:
    if not isinstance(mapa_abas_resolvidas, MapaAbasResolvidas):
        _registrar_erro(erros, "MapaAbasResolvidas ausente ou inválido.")
        return {}

    abas_por_bloco = dict(mapa_abas_resolvidas.abas_por_bloco or {})
    nomes_abas = set(getattr(pacote_planilha, "nomes_abas", []) or []) if pacote_planilha is not None else set()

    evidencias["mapa_abas_qtd_blocos"] = len(abas_por_bloco)
    evidencias["mapa_abas_blocos"] = sorted(abas_por_bloco.keys())
    evidencias["mapa_abas_auditoria"] = dict(mapa_abas_resolvidas.auditoria or {})

    for bloco in ABAS_OPERACIONAIS_OBRIGATORIAS:
        aba = abas_por_bloco.get(bloco)
        if not aba:
            _registrar_erro(erros, f"MapaAbasResolvidas sem bloco obrigatório: {bloco}")
            continue
        if nomes_abas and aba not in nomes_abas:
            _registrar_erro(erros, f"MapaAbasResolvidas aponta para aba inexistente: {bloco} -> {aba}")

    return abas_por_bloco


def _validar_mapa_colunas_resolvidas(
    mapa_colunas_resolvidas: MapaColunasResolvidas,
    erros: list[str],
    evidencias: dict[str, Any],
) -> dict[str, dict[str, str]]:
    if not isinstance(mapa_colunas_resolvidas, MapaColunasResolvidas):
        _registrar_erro(erros, "MapaColunasResolvidas ausente ou inválido.")
        return {}

    colunas_por_bloco = {
        str(bloco): dict(colunas)
        for bloco, colunas in (mapa_colunas_resolvidas.colunas_por_bloco or {}).items()
        if isinstance(colunas, Mapping)
    }
    evidencias["mapa_colunas_qtd_blocos"] = len(colunas_por_bloco)
    evidencias["mapa_colunas_blocos"] = sorted(colunas_por_bloco.keys())
    evidencias["mapa_colunas_auditoria"] = dict(mapa_colunas_resolvidas.auditoria or {})

    for bloco in ABAS_OPERACIONAIS_OBRIGATORIAS:
        colunas_bloco = colunas_por_bloco.get(bloco)
        if not colunas_bloco:
            _registrar_erro(erros, f"MapaColunasResolvidas sem bloco obrigatório: {bloco}")
            continue
        ausentes = [campo for campo in COLUNAS_CRITICAS_OBRIGATORIAS.get(bloco, ()) if campo not in colunas_bloco]
        evidencias[f"{bloco}_mapa_colunas_criticas_ausentes"] = ausentes
        if ausentes:
            _registrar_erro(erros, f"MapaColunasResolvidas sem campos críticos em {bloco}: {ausentes}")

    return colunas_por_bloco


def _resolver_coluna_no_quadro_estrutural(
    quadro: pd.DataFrame,
    campo: str,
    coluna_fisica: str,
) -> str | None:
    colunas = set(map(str, getattr(quadro, "columns", [])))
    if campo in colunas:
        return campo
    if coluna_fisica in colunas:
        return coluna_fisica
    return None


def _validar_quadros_estruturais_resolvidos(
    quadros_estruturais_resolvidos: Mapping[str, Any],
    abas_por_bloco: dict[str, str],
    colunas_por_bloco: dict[str, dict[str, str]],
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if not isinstance(quadros_estruturais_resolvidos, Mapping) or not quadros_estruturais_resolvidos:
        _registrar_erro(erros, "quadros_estruturais_resolvidos ausente, vazio ou inválido.")
        return

    evidencias["quadros_estruturais_resolvidos_qtd"] = len(quadros_estruturais_resolvidos)

    for bloco in ABAS_OPERACIONAIS_OBRIGATORIAS:
        nome_aba = abas_por_bloco.get(bloco)
        quadro = quadros_estruturais_resolvidos.get(nome_aba) if nome_aba else None
        if quadro is None:
            quadro = quadros_estruturais_resolvidos.get(bloco)
        if quadro is None:
            _registrar_erro(erros, f"Quadro estrutural resolvido ausente para bloco: {bloco}")
            continue
        if not isinstance(quadro, pd.DataFrame):
            _registrar_erro(erros, f"Quadro estrutural resolvido não é DataFrame para bloco: {bloco}")
            continue

        shape = getattr(quadro, "shape", None)
        evidencias[f"{bloco}_quadro_estrutural_shape"] = tuple(shape) if shape is not None else None
        if not shape or len(shape) != 2:
            _registrar_erro(erros, f"Quadro estrutural sem shape tabular válido para bloco: {bloco}")
            continue
        n_linhas, n_colunas = int(shape[0]), int(shape[1])
        if n_colunas <= 0:
            _registrar_erro(erros, f"Quadro estrutural sem colunas para bloco: {bloco}")
        if n_linhas <= 0:
            _registrar_erro(erros, f"Quadro estrutural sem linhas para bloco: {bloco}")

        colunas_bloco = colunas_por_bloco.get(bloco, {})
        colunas_para_validacao: dict[str, str] = {}
        ausentes_no_quadro: list[str] = []
        for campo, coluna_fisica in colunas_bloco.items():
            coluna_resolvida = _resolver_coluna_no_quadro_estrutural(quadro, campo, coluna_fisica)
            if coluna_resolvida is None:
                ausentes_no_quadro.append(campo)
            else:
                colunas_para_validacao[campo] = coluna_resolvida

        evidencias[f"{bloco}_colunas_criticas_encontradas_pacote"] = dict(colunas_para_validacao)
        evidencias[f"{bloco}_colunas_criticas_ausentes_quadro_estrutural"] = ausentes_no_quadro
        for campo in ausentes_no_quadro:
            _registrar_erro(erros, f"Campo resolvido ausente no quadro estrutural em {bloco}/{campo}.")

        _validar_datas_minimas(bloco, quadro, colunas_para_validacao, erros, avisos, evidencias)
        _validar_numeros_minimos(bloco, quadro, colunas_para_validacao, erros, avisos, evidencias)


def _validar_janela_consulta_cdi(
    janela_consulta_cdi: JanelaConsultaCDI,
    contexto_execucao: ContextoExecucao,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if not isinstance(janela_consulta_cdi, JanelaConsultaCDI):
        _registrar_erro(erros, "JanelaConsultaCDI ausente ou inválida.")
        return

    data_ini = janela_consulta_cdi.data_inicial_consulta
    data_fim = janela_consulta_cdi.data_final_consulta
    data_ref = getattr(contexto_execucao, "data_referencia", None) if contexto_execucao is not None else None

    evidencias["janela_cdi_data_inicial_consulta"] = str(data_ini)
    evidencias["janela_cdi_data_final_consulta"] = str(data_fim)
    evidencias["janela_cdi_metadados"] = dict(janela_consulta_cdi.metadados or {})

    if data_ini is None:
        _registrar_erro(erros, "JanelaConsultaCDI sem data_inicial_consulta.")
    if data_fim is None:
        _registrar_erro(erros, "JanelaConsultaCDI sem data_final_consulta.")
    if data_ini is not None and data_fim is not None and data_fim < data_ini:
        _registrar_erro(erros, "JanelaConsultaCDI com data_final_consulta menor que data_inicial_consulta.")
    if data_ref is not None and data_fim is not None and data_fim < data_ref:
        _registrar_aviso(avisos, "JanelaConsultaCDI termina antes da data de referência.")


def _validar_pacote_cache_cdi(
    pacote_cache_cdi: Any,
    janela_consulta_cdi: JanelaConsultaCDI,
    contexto_execucao: ContextoExecucao,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    if pacote_cache_cdi is None:
        _registrar_erro(erros, "PacoteCacheCDIDiario ausente.")
        return

    serie_cdi = getattr(pacote_cache_cdi, "serie_cdi", None)
    auditoria = getattr(pacote_cache_cdi, "auditoria", None)
    validacao = getattr(pacote_cache_cdi, "validacao", None)
    caminho_cache = getattr(pacote_cache_cdi, "caminho_cache", None)

    if not isinstance(serie_cdi, dict) or not serie_cdi:
        _registrar_erro(erros, "PacoteCacheCDIDiario sem serie_cdi válida.")
    else:
        evidencias["cache_cdi_qtd_datas_serie"] = len(serie_cdi)
        try:
            evidencias["cache_cdi_ultima_data_serie"] = str(max(serie_cdi.keys()))
        except Exception:
            evidencias["cache_cdi_ultima_data_serie"] = None

    if caminho_cache is None:
        _registrar_erro(erros, "PacoteCacheCDIDiario sem caminho_cache.")
    else:
        evidencias["cache_cdi_caminho_cache"] = str(caminho_cache)
        if not _path_existe(caminho_cache):
            _registrar_aviso(avisos, f"Caminho do cache CDI não existe localmente: {caminho_cache}")

    if not isinstance(auditoria, dict):
        _registrar_erro(erros, "PacoteCacheCDIDiario sem auditoria válida.")
        auditoria = {}
    evidencias["cache_cdi_auditoria"] = dict(auditoria)
    for chave in (
        "data_inicial_consulta",
        "data_final_consulta",
        "fonte_serie_cdi",
        "fetch_status",
        "qtd_datas_serie_cdi",
        "caminho_cache",
    ):
        if chave not in auditoria:
            _registrar_erro(erros, f"Auditoria do cache CDI sem campo obrigatório: {chave}")

    if not isinstance(validacao, dict):
        _registrar_erro(erros, "PacoteCacheCDIDiario sem validacao válida.")
    else:
        evidencias["cache_cdi_validacao_ok"] = validacao.get("ok")
        if validacao.get("erros"):
            _registrar_erro(erros, f"Erros reportados pelo cache CDI: {validacao.get('erros')}")
        for aviso in validacao.get("avisos", []) or []:
            _registrar_aviso(avisos, f"Aviso do cache CDI: {aviso}")

    data_ref = getattr(contexto_execucao, "data_referencia", None) if contexto_execucao is not None else None
    ultima_data = None
    if isinstance(serie_cdi, dict) and serie_cdi:
        try:
            ultima_data = max(serie_cdi.keys())
        except Exception:
            ultima_data = None
    if data_ref is not None and ultima_data is not None and ultima_data < data_ref:
        _registrar_aviso(avisos, "Última data da série CDI é anterior à data de referência.")

    if isinstance(janela_consulta_cdi, JanelaConsultaCDI):
        data_ini = janela_consulta_cdi.data_inicial_consulta
        if data_ini is not None and isinstance(serie_cdi, dict) and serie_cdi:
            primeira_data = min(serie_cdi.keys())
            if primeira_data > data_ini:
                _registrar_aviso(avisos, "Série CDI começa após data_inicial_consulta da JanelaConsultaCDI.")


def _validar_auditorias_etapa1(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
    erros: list[str],
    avisos: list[str],
    evidencias: dict[str, Any],
) -> None:
    auditoria_entrada = pacote_entrada_resolvida.auditoria_entrada_bruta
    auditoria_resolucao = pacote_entrada_resolvida.auditoria_resolucao_entrada
    auditoria_cache = pacote_entrada_resolvida.auditoria_cache_cdi

    if not isinstance(auditoria_entrada, AuditoriaEntradaBruta):
        _registrar_erro(erros, "AuditoriaEntradaBruta ausente ou inválida.")
    else:
        evidencias["auditoria_entrada_bruta_fonte_planilha"] = auditoria_entrada.fonte_planilha
        evidencias["auditoria_entrada_bruta_fetch_status"] = auditoria_entrada.fetch_status_planilha
        if not auditoria_entrada.fonte_planilha:
            _registrar_aviso(avisos, "AuditoriaEntradaBruta sem fonte_planilha.")

    if not isinstance(auditoria_resolucao, AuditoriaResolucaoEntrada):
        _registrar_erro(erros, "AuditoriaResolucaoEntrada ausente ou inválida.")
    else:
        evidencias["auditoria_resolucao_entrada_ausencias"] = dict(auditoria_resolucao.ausencias or {})
        ausencias = auditoria_resolucao.ausencias or {}
        blocos_ausentes = ausencias.get("blocos_ausentes") if isinstance(ausencias, Mapping) else None
        if blocos_ausentes:
            _registrar_erro(erros, f"AuditoriaResolucaoEntrada reporta blocos ausentes: {blocos_ausentes}")

    if not isinstance(auditoria_cache, AuditoriaCacheCDI):
        _registrar_erro(erros, "AuditoriaCacheCDI ausente ou inválida.")
    else:
        evidencias["auditoria_cache_cdi_fonte_serie"] = auditoria_cache.fonte_serie_cdi
        evidencias["auditoria_cache_cdi_fetch_status"] = auditoria_cache.fetch_status
        evidencias["auditoria_cache_cdi_qtd_datas"] = auditoria_cache.qtd_datas_serie_cdi


def validar_pre_execucao(
    pacote_config: PacoteConfig,
    contexto_execucao: ContextoExecucao,
    pacote_planilha: PacotePlanilha,
) -> PacoteValidacaoPreExecucao:
    """Valida artefatos já produzidos pela Etapa 1.

    Esta função não cria, baixa, carrega, relê, transforma ou canoniza dados.
    """

    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {
        "etapa": "2",
        "tipo": "gate_puro_pre_execucao",
    }

    _validar_pacote_config(pacote_config, erros, evidencias)
    _validar_contexto_execucao(contexto_execucao, erros, avisos, evidencias)
    _validar_pacote_planilha(pacote_planilha, pacote_config, erros, avisos, evidencias)

    return PacoteValidacaoPreExecucao(
        ok=len(erros) == 0,
        erros_bloqueantes=erros,
        avisos=avisos,
        evidencias=evidencias,
    )


def validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
) -> PacoteValidacaoPreExecucao:
    """Valida a Etapa 1 a partir do PacoteEntradaResolvida em modo paralelo.

    Esta função usa os artefatos já resolvidos pela Etapa 1. Ela não baixa
    planilha, não abre workbook, não resolve aliases, não reconstrói mapas,
    não carrega cache BCB, não cria dados operacionais canônicos, não executa
    motor e não gera saída.
    """

    erros: list[str] = []
    avisos: list[str] = []
    evidencias: dict[str, Any] = {
        "etapa": "2",
        "tipo": "gate_puro_pre_execucao_pacote_entrada_resolvida",
        "modo_paralelo": True,
        "nao_substitui_validacao_legada": True,
        "nao_reconstroi_aliases": True,
        "nao_cria_dados_canonicos": True,
        "nao_altera_motor": True,
        "nao_altera_saida": True,
    }

    if not isinstance(pacote_entrada_resolvida, PacoteEntradaResolvida):
        _registrar_erro(erros, "Objeto recebido não é PacoteEntradaResolvida.")
        return PacoteValidacaoPreExecucao(
            ok=False,
            erros_bloqueantes=erros,
            avisos=avisos,
            evidencias=evidencias,
        )

    _validar_pacote_entrada_resolvida_estrutura(pacote_entrada_resolvida, erros, evidencias)

    pacote_config = pacote_entrada_resolvida.pacote_config
    contexto_execucao = pacote_entrada_resolvida.contexto_execucao
    pacote_planilha = pacote_entrada_resolvida.pacote_planilha
    mapa_abas_resolvidas = pacote_entrada_resolvida.mapa_abas_resolvidas
    mapa_colunas_resolvidas = pacote_entrada_resolvida.mapa_colunas_resolvidas
    quadros_estruturais_resolvidos = pacote_entrada_resolvida.quadros_estruturais_resolvidos
    janela_consulta_cdi = pacote_entrada_resolvida.janela_consulta_cdi
    pacote_cache_cdi = pacote_entrada_resolvida.pacote_cache_cdi

    _validar_pacote_config(pacote_config, erros, evidencias)
    _validar_contexto_execucao(contexto_execucao, erros, avisos, evidencias)
    _validar_pacote_planilha_basico_sem_alias(pacote_planilha, erros, avisos, evidencias)

    abas_por_bloco = _validar_mapa_abas_resolvidas(
        mapa_abas_resolvidas,
        pacote_planilha,
        erros,
        evidencias,
    )
    colunas_por_bloco = _validar_mapa_colunas_resolvidas(
        mapa_colunas_resolvidas,
        erros,
        evidencias,
    )
    _validar_quadros_estruturais_resolvidos(
        quadros_estruturais_resolvidos,
        abas_por_bloco,
        colunas_por_bloco,
        erros,
        avisos,
        evidencias,
    )
    _validar_janela_consulta_cdi(
        janela_consulta_cdi,
        contexto_execucao,
        erros,
        avisos,
        evidencias,
    )
    _validar_pacote_cache_cdi(
        pacote_cache_cdi,
        janela_consulta_cdi,
        contexto_execucao,
        erros,
        avisos,
        evidencias,
    )
    _validar_auditorias_etapa1(
        pacote_entrada_resolvida,
        erros,
        avisos,
        evidencias,
    )

    return PacoteValidacaoPreExecucao(
        ok=len(erros) == 0,
        erros_bloqueantes=erros,
        avisos=avisos,
        evidencias=evidencias,
    )

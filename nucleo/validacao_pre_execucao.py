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
- não resolve colunas;
- não canoniza colunas;
- não transforma dados;
- não decide pagamento, switching, ranking ou saída.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nucleo.ambiente import ContextoExecucao
from nucleo.carregador_config import PacoteConfig
from nucleo.leitor_planilha import PacotePlanilha


ABAS_OPERACIONAIS_OBRIGATORIAS: tuple[str, ...] = (
    "carteira",
    "salarios",
    "despesas",
    "switching",
    "lotes",
)


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

    abas_obrigatorias: dict[str, str] = {}
    for chave in ABAS_OPERACIONAIS_OBRIGATORIAS:
        nome_aba = abas_cfg.get(chave)
        if nome_aba:
            abas_obrigatorias[chave] = str(nome_aba)

    evidencias["abas_obrigatorias"] = dict(abas_obrigatorias)

    for chave, nome_aba in abas_obrigatorias.items():
        if nome_aba not in nomes_abas:
            _registrar_erro(erros, f"Aba obrigatória ausente na planilha: {chave} -> {nome_aba}")
            continue

        quadro = quadros_brutos.get(nome_aba)
        if quadro is None:
            _registrar_erro(erros, f"Quadro bruto ausente para aba obrigatória: {nome_aba}")
            continue

        shape = getattr(quadro, "shape", None)
        evidencias[f"aba_{chave}_shape"] = tuple(shape) if shape is not None else None

        if not shape or len(shape) != 2:
            _registrar_erro(erros, f"Quadro bruto sem shape tabular válido para aba: {nome_aba}")
            continue

        n_linhas, n_colunas = int(shape[0]), int(shape[1])
        if n_colunas <= 0:
            _registrar_erro(erros, f"Aba obrigatória sem colunas: {nome_aba}")
        if n_linhas <= 0:
            _registrar_erro(erros, f"Aba obrigatória sem linhas: {nome_aba}")


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

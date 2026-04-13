
# -*- coding: utf-8 -*-
"""
SCRIPT UNIFICADO — BASE PADRONIZADA INCREMENTAL
===============================================

Este arquivo consolida apenas os trechos já enviados dos dois scripts,
reorganizados em uma estrutura única e estável para facilitar as próximas
incorporações.

Regras desta base:
- inclui somente trechos efetivamente enviados;
- reorganiza o código em seções padronizadas;
- preserva compatibilidade entre convenções legadas (`config`/`CONFIG`);
- não antecipa leitura efetiva das abas nem lógica específica de negócio;
- parâmetros fixos já formalizados no `config` não devem ser duplicados no script,
  exceto quando houver fallback mínimo necessário para compatibilidade.

Estrutura padrão adotada:
00. Bootstrap mínimo e instalação de dependências
01. Imports principais, ambiente, data e warnings
02. Caminhos e resolução de arquivos
03. Configuração global
04. Helpers de acesso ao config
05. Contrato operacional, estado global e logging
06. Parâmetros derivados do config
07. Infraestrutura de arquivos externos e planilhas
08. Helpers de nomes de abas/colunas
09. Heurísticas auxiliares pré-leitura
10. Calendário financeiro, rede, BCB e tributação
11. Modelos de domínio
12. Baseline / regressão
13. Aliases globais de compatibilidade
"""

# =========================================================
# 00. BOOTSTRAP MÍNIMO E INSTALAÇÃO DE DEPENDÊNCIAS
# =========================================================
import sys
import subprocess
import os
import time
import warnings
import json
import re
import copy
import itertools
import unicodedata
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta, datetime
from importlib import metadata as importlib_metadata

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.config_runtime import (
    DEFAULT_CONFIG_FILES,
    data_hoje_referencia,
    obter_timezone_brasil,
    hoje_brasil,
    _resolver_config_path,
    carregar_config,
    sincronizar_config_global,
    _cfg_get,
    _cfg_get_required,
    _cfg_get_any,
    _cfg_get_required_any,
    _cfg_get_date_iso,
    detectar_ambiente_execucao,
    obter_contrato_operacional,
    validar_contrato_operacional,
    resumir_contrato_operacional,
)
from src.core.paths_io import (
    _caminhos_base_projeto,
    _localizar_arquivo,
    _iterar_candidatos_arquivo,
    _extrair_file_id_google,
    gdrive_export_xlsx,
    gdrive_uc_download,
    _baixar_url_para_arquivo,
    baixar_planilha_google,
    baixar_arquivo_drive,
    _resolver_arquivo_excel_local,
    set_paths_runtime,
)
from src.core.logging_utils import (
    log_debug,
    _debug_ativo,
    _log_debug,
    _print_once,
    set_console_mode,
)

def instalar_dependencias():
    """Instala dependências principais antes dos imports externos.

    Estratégia unificada:
    - tenta detectar por import real do módulo;
    - instala em modo silencioso quando necessário;
    - em Colab, tenta fallback via shell do IPython.
    """
    required = {
        "pandas": "pandas",
        "numpy": "numpy",
        "requests": "requests",
        "pulp": "pulp",
        "workalendar": "workalendar",
        "scipy": "scipy",
        "numba": "numba",
        "openpyxl": "openpyxl",
        "urllib3": "urllib3",
    }

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    print(">>> [SETUP] Verificando ambiente Python...")

    in_colab = "google.colab" in sys.modules
    missing = []

    for pip_name, import_name in required.items():
        try:
            __import__(import_name)
        except Exception:
            missing.append(pip_name)

    if missing:
        print(f" -> Instalando: {', '.join(sorted(missing))}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *sorted(missing), "--quiet"]
            )
            print(" -> Instalação concluída!\n")
        except Exception as e:
            print(f" -> [ERRO] Falha via subprocess: {e}")
            if in_colab:
                print(" -> Tentando via !pip no Colab...")
                try:
                    import IPython
                    for pkg in sorted(missing):
                        IPython.get_ipython().system(f"pip install {pkg} --quiet")
                    print(" -> Instalação via !pip concluída!\n")
                except Exception as e2:
                    raise RuntimeError(f"Falha crítica ao instalar dependências no Colab: {e2}") from e2
            else:
                raise RuntimeError(
                    "Falha ao instalar dependências automaticamente. "
                    f"Instale manualmente: pip install {' '.join(sorted(missing))}"
                ) from e
    else:
        print(" -> Todas as dependências OK.\n")

instalar_dependencias()

# =========================================================
# 01. IMPORTS PRINCIPAIS, AMBIENTE, DATA E WARNINGS
# =========================================================
import numpy as np
import pandas as pd
import requests
import pulp
from workalendar.america import Brazil
from scipy.optimize import differential_evolution
from numba import njit

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

try:
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning
except Exception:
    urllib3 = None
    InsecureRequestWarning = None

def configurar_warnings_rede():
    """Suprime avisos esperados de HTTPS sem verificação."""
    if InsecureRequestWarning is not None:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        if urllib3 is not None:
            urllib3.disable_warnings(InsecureRequestWarning)

configurar_warnings_rede()
warnings.filterwarnings("ignore")
cal = Brazil()


# =========================================================
# 02. CAMINHOS E RESOLUÇÃO DE ARQUIVOS
# =========================================================
DEFAULT_CONFIG_FILES = (
    "config_atualizado_revisado_v7_populacao_inicial.json",
    "config_atualizado_revisado_v6_avaliacao.json",
    "config_atualizado_revisado_v5_otimizacao_bounds.json",
    "config_atualizado_revisado_v4_otimizacao.json",
    "config_atualizado_revisado_v3_treinamento.json",
    "config_atualizado_revisado_v2.json",
    "config_atualizado.json",
    "config.json",
)


# =========================================================
# 03. CONFIGURAÇÃO GLOBAL
# =========================================================


config = sincronizar_config_global(carregar_config(strict=True))
CONFIG = config
CONFIG_PATH = _resolver_config_path()

# =========================================================
# 04. HELPERS DE ACESSO AO CONFIG
# =========================================================


# =========================================================
# 05. CONTRATO OPERACIONAL, ESTADO GLOBAL E LOGGING
# =========================================================
CONTRATO_OPERACIONAL: dict | None = None

CDI_FONTE_UTILIZADA = None
CDI_DATA_INICIAL_UTILIZADA = None
CDI_DATA_FINAL_UTILIZADA = None
CDI_QTD_OBSERVACOES = None
CDI_DATA_CORTE_CONGELADA = None
MAPA_PRODUTOS_CANONICO = None
INVESTIMENTOS_NORM = {}
USAR_INVESTIMENTOS_NORM_NEW = True
ROLLBACK_INVESTIMENTOS_NORM = False

DEBUG_CDI = True


# =========================================================
# 06. PARÂMETROS DERIVADOS DO CONFIG
# =========================================================
BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME = _cfg_get(
    ["bootstrap", "parametros_5p_default_nome"],
    "melhores_parametros_5p",
)
REDE_USER_AGENT_DOWNLOAD = _cfg_get(["rede", "user_agent_download_planilha"], "Mozilla/5.0")
REDE_USER_AGENT_BCB = _cfg_get(["rede", "user_agent_bcb"], "Mozilla/5.0 (compatible; FinBot/1.0)")
REDE_ACCEPT_BCB = _cfg_get(["rede", "accept_bcb"], "application/json")
REDE_TIMEOUT_DOWNLOAD_SEGUNDOS = _cfg_get(["rede", "timeout_download_segundos"], 30)
REDE_TIMEOUT_BCB_SEGUNDOS = _cfg_get(["rede", "timeout_bcb_segundos"], 10)
REDE_VERIFICAR_SSL = _cfg_get(["rede", "verificar_ssl"], False)
ARQUIVO_TEMPORARIO_FALLBACK_BCB = _cfg_get(["arquivos", "temporario_fallback_bcb"], "cdi_fallback.xlsx")
HISTORICO_BCB_DATA_MINIMA = _cfg_get_date_iso(["historico_bcb", "data_minima_consulta"], "2025-01-01")
HISTORICO_BCB_DATA_MINIMA_FORMATADA = _cfg_get(
    ["historico_bcb", "data_minima_consulta_formatada"],
    HISTORICO_BCB_DATA_MINIMA.strftime("%d/%m/%Y"),
)
CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO = _cfg_get(["calendario", "ano_inicio_dias_sem_rendimento"], 2025)
CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO = _cfg_get(["calendario", "ano_fim_dias_sem_rendimento"], 2035)
ORDEM_PROCESSAMENTO_SENTINELA = int(_cfg_get(["execucao", "ordem_processamento_sentinela"], 10**12))
AVALIACAO_WF_PCT_TREINO = float(_cfg_get(["avaliacao", "walkforward", "pct_treino"], 0.70))
AVALIACAO_WF_ROBUSTEZ_DEFAULT = float(_cfg_get(["avaliacao", "walkforward", "robustez_default"], 95.0))
AVALIACAO_RANKING_PESO_SALDO = float(_cfg_get(["avaliacao", "ranking", "peso_saldo"], 0.7))
AVALIACAO_RANKING_PESO_ROBUSTEZ = float(_cfg_get(["avaliacao", "ranking", "peso_robustez"], 0.3))
AUDITORIA_COLUNA_ESCOLHIDA = bool(_cfg_get(["auditoria", "auditar_coluna_escolhida"], True))

POL_COL_LOTE_ID_TOKENS_FORTES = set(_cfg_get(
    ["politicas_coluna", "lote_id_tokens_fortes"],
    ["id", "lote", "lote id", "lote (id)"],
))
POL_COL_LOTE_ID_TOKENS_CONJUNTOS = list(_cfg_get(
    ["politicas_coluna", "lote_id_exigir_tokens_conjuntos"],
    ["lote", "id"],
))
POL_COL_PRODUTO_TOKENS_BUSCA = list(_cfg_get(
    ["politicas_coluna", "produto_tokens_busca"],
    ["invest", "produto", "carteira", "aplic"],
))
POL_COL_PESO_PREENCHIMENTO_ID_LOTE = float(_cfg_get(
    ["politicas_coluna", "peso_preenchimento_id_lote"],
    1000.0,
))
POL_COL_BONUS_UNICIDADE_ID_LOTE = float(_cfg_get(
    ["politicas_coluna", "bonus_unicidade_id_lote"],
    10000.0,
))
POL_COL_PESO_PREENCHIMENTO_PRODUTO = float(_cfg_get(
    ["politicas_coluna", "peso_preenchimento_produto"],
    100.0,
))
POL_COL_PESO_MATCH_INVESTIMENTO_PRODUTO = float(_cfg_get(
    ["politicas_coluna", "peso_match_investimento_produto"],
    1000.0,
))
POL_COL_CARDINALIDADE_MINIMA_LOTE_ID = int(_cfg_get(
    ["politicas_coluna", "cardinalidade_minima_lote_id"],
    2,
))
POL_COL_EXIGIR_UNICIDADE_LOTE_ID = bool(_cfg_get(
    ["politicas_coluna", "exigir_unicidade_lote_id"],
    True,
))

POL_TAXA_LIMITE_PERCENTUAL_VS_MULTIPLICADOR = float(_cfg_get(
    ["politicas_taxa", "limite_percentual_vs_multiplicador"],
    10.0,
))
POL_TAXA_REMOVER_PERCENTUAL_STRING = bool(_cfg_get(
    ["politicas_taxa", "remover_percentual_string"],
    True,
))
POL_TAXA_SUBSTITUIR_VIRGULA_DECIMAL = bool(_cfg_get(
    ["politicas_taxa", "substituir_virgula_decimal"],
    True,
))

INVESTIMENTO_REFERENCIA_FUTURO_NOME = str(_cfg_get(
    ["defaults", "investimento_referencia_futuro"],
    "CDB Sofisa 105%",
))
INVESTIMENTO_REFERENCIA_FUTURO_MATCH_EXATO = bool(_cfg_get(
    ["defaults", "investimento_referencia_futuro_match_exato"],
    True,
))
TAXA_BASE_REFERENCIA_FUTURA_DEFAULT = float(_cfg_get(
    ["defaults_lote", "taxa_base_referencia_futura_default"],
    1.05,
))

if not (0.0 < AVALIACAO_WF_PCT_TREINO < 1.0):
    raise ValueError(f"avaliacao.walkforward.pct_treino inválido: {AVALIACAO_WF_PCT_TREINO}")
if AVALIACAO_WF_ROBUSTEZ_DEFAULT < 0.0:
    raise ValueError(f"avaliacao.walkforward.robustez_default inválido: {AVALIACAO_WF_ROBUSTEZ_DEFAULT}")
if AVALIACAO_RANKING_PESO_SALDO < 0.0 or AVALIACAO_RANKING_PESO_ROBUSTEZ < 0.0:
    raise ValueError("Pesos de avaliacao.ranking não podem ser negativos")
if abs((AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ) - 1.0) > 1e-9:
    raise ValueError(
        "Pesos de avaliacao.ranking devem somar 1.0; "
        f"atual={(AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ):.12f}"
    )

AMBIENTE_ATUAL = detectar_ambiente_execucao()
BASE_DIR_ATIVA = Path(
    _cfg_get(
        [
            "ambiente",
            "base_dir_colab" if AMBIENTE_ATUAL == "colab" else "base_dir_local",
        ],
        ".",
    )
)

TZ_BRASIL = obter_timezone_brasil()
DATA_REFERENCIA = hoje_brasil()

GOOGLE_CFG = _cfg_get(["google_drive"], {}) if isinstance(CONFIG, dict) else {}
PATHS_CFG = _cfg_get(["paths"], {}) if isinstance(CONFIG, dict) else {}
DOWNLOADS_CFG = _cfg_get(["downloads"], {}) if isinstance(CONFIG, dict) else {}
EXEC_CFG = _cfg_get(["execucao"], _cfg_get(["execution"], {})) if isinstance(CONFIG, dict) else {}
SIM_CFG = _cfg_get(["simulacao"], _cfg_get(["simulation"], {})) if isinstance(CONFIG, dict) else {}
SWITCH_CFG = _cfg_get(["switching"], {}) if isinstance(CONFIG, dict) else {}

# Entradas/URLs derivadas do config
GOOGLE_SHEETS_FILE_ID = _cfg_get(["google_drive", "sheets_file_id"], None)
FALLBACK_BCB_FILE_ID = _cfg_get(["google_drive", "fallback_bcb_file_id"], GOOGLE_CFG.get("fallback_bcb_file_id"))
FALLBACK_PARAM_5P_FILE_ID = _cfg_get(["google_drive", "fallback_param_5p_file_id"], GOOGLE_CFG.get("fallback_param_5p_file_id"))

GOOGLE_SHEETS_EDIT_BASE = _cfg_get_required(["urls", "google_sheets_edit_base"])
GOOGLE_SHEETS_EXPORT_BASE = _cfg_get_required(["urls", "google_sheets_export_base"])
GOOGLE_DRIVE_DOWNLOAD_BASE = _cfg_get_required(["urls", "google_drive_download_base"])

set_paths_runtime(
    google_sheets_export_base=GOOGLE_SHEETS_EXPORT_BASE,
    google_drive_download_base=GOOGLE_DRIVE_DOWNLOAD_BASE,
)


def _normalizar_nome_arquivo_json(nome_padrao: str) -> str:
    nome = str(nome_padrao or BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME).strip()
    if not nome:
        nome = str(BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME)
    if not nome.lower().endswith(".json"):
        nome = f"{nome}.json"
    return nome

BCB_SERIE_12_URL = _cfg_get_required(["urls", "bcb_sgs_12_url"])

if GOOGLE_SHEETS_FILE_ID:
    if "{file_id}" in str(GOOGLE_SHEETS_EDIT_BASE):
        LINK_GOOGLE_SHEETS = str(GOOGLE_SHEETS_EDIT_BASE).format(file_id=GOOGLE_SHEETS_FILE_ID)
    else:
        LINK_GOOGLE_SHEETS = f"{str(GOOGLE_SHEETS_EDIT_BASE).rstrip('/')}/{GOOGLE_SHEETS_FILE_ID}/edit"
else:
    LINK_GOOGLE_SHEETS = None

# compatibilidade legada
sheets_file_id = GOOGLE_SHEETS_FILE_ID

NOME_ARQUIVO_LOCAL = str(BASE_DIR_ATIVA / _cfg_get_required_any([
    ["arquivos", "planilha"],
    ["paths", "excel_local"],
]))
CACHE_BCB_FILE = str(BASE_DIR_ATIVA / _cfg_get_required_any([
    ["arquivos", "cache_bcb"],
    ["paths", "cache_bcb"],
]))

RESULTADO_OTIMIZADOR_FIXO = _cfg_get_any([["paths", "resultado_otimizador_fixo"]], default=None)

PARAM_5P_FIXO = _cfg_get_any([
    ["arquivos", "parametros_5p"],
    ["arquivos", "melhores_parametros_5p"],
    ["paths", "param_5p_fixo"],
], default=f"{BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME}.json")
_PARAM_FILE_NAME = _cfg_get_any([
    ["arquivos", "parametros_5p"],
    ["arquivos", "melhores_parametros_5p"],
], default=BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME)
PARAM_FILE_5P = str(BASE_DIR_ATIVA / _normalizar_nome_arquivo_json(_PARAM_FILE_NAME))

FALLBACK_BCB_URL = DOWNLOADS_CFG.get("fallback_bcb_url") or (gdrive_uc_download(FALLBACK_BCB_FILE_ID) if FALLBACK_BCB_FILE_ID else None)
FALLBACK_PARAM_URL_5P = DOWNLOADS_CFG.get("fallback_param_5p_url") or (gdrive_uc_download(FALLBACK_PARAM_5P_FILE_ID) if FALLBACK_PARAM_5P_FILE_ID else None)

PARAMS_HIBRIDO = None
PLANO_PAGAMENTOS_EXTERNO = None
ORIGEM_PLANO_PAGAMENTOS = None
_MODO_EXECUCAO_FUTURO_RAW = str(EXEC_CFG.get("modo_execucao_futuro", "rigido_plano_externo"))
AUTO_REBAIXAR_MODO_SE_PLANO_INCOMPATIVEL = bool(EXEC_CFG.get("auto_rebaixar_plano_incompativel", True))
MODO_FALLBACK_PLANO_INCOMPATIVEL = str(EXEC_CFG.get("modo_fallback_plano_incompativel", "dinamico"))

MODOS_EXECUCAO_FUTURO_INFO = {
    "dinamico": "Ignora o plano externo na execução das contas futuras e deixa o motor local decidir pagamentos e switches.",
    "rigido_plano_externo": "Tenta reproduzir o Extrato do arquivo externo conta a conta; quando faltar saldo ou o lote não existir, registra desvio e ajusta.",
    "rigido_melhor_data": "Usa a mesma lógica do plano externo, mas reancora cada switch na melhor data encontrada no diagnóstico antes de rodar o futuro.",
}

DIAGNOSTICO_MODO_EXECUCAO = {
    "modo_solicitado": None,
    "modo_efetivo": None,
    "houve_rebaixamento": False,
    "motivos_rebaixamento": [],
    "plano_externo_carregado": False,
    "origem_plano_externo": None,
    "observacao": "",
}

CONSOLE_MODO = "compacto"
AUDITAR_PLANO_EXTERNO = False
DEBUG_DOWNLOADS = False
DEBUG_SCHEMA_ABAS = False
DEBUG_SWITCH_EXECUCAO = False
DEBUG_ALOCACAO_FUTURA = False
EXPORTAR_DEBUG = False

_PRINT_ONCE_KEYS = set()
EXCEL_PATH_CACHE = None
DF_ABAS_CACHE = {}

set_console_mode(CONSOLE_MODO)
set_paths_runtime(
    user_agent_download=REDE_USER_AGENT_DOWNLOAD,
    timeout_download_segundos=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS,
    verificar_ssl=REDE_VERIFICAR_SSL,
    google_sheets_export_base=GOOGLE_SHEETS_EXPORT_BASE,
    google_drive_download_base=GOOGLE_DRIVE_DOWNLOAD_BASE,
    link_google_sheets=LINK_GOOGLE_SHEETS,
    nome_arquivo_local=NOME_ARQUIVO_LOCAL,
    debug_downloads=DEBUG_DOWNLOADS,
    logger=_log_debug,
)


def _fim_janela_alocacao(ref):
    primeiro = date(ref.year, ref.month, 1)
    prox = (primeiro.replace(day=28) + timedelta(days=4)).replace(day=1)
    prox2 = (prox.replace(day=28) + timedelta(days=4)).replace(day=1)
    return prox2 - timedelta(days=1)

PRODUTOS_GLOBAIS_SIMULACAO = []

def normalizar_modo_execucao_futuro(valor):
    txt = str(valor or "").strip().lower()
    aliases = {
        "dinamico": "dinamico",
        "dynamic": "dinamico",
        "rigido_plano_externo": "rigido_plano_externo",
        "plano_externo_rigido": "rigido_plano_externo",
        "rigido": "rigido_plano_externo",
        "rigido_melhor_data": "rigido_melhor_data",
        "melhor_data": "rigido_melhor_data",
        "rigido_com_melhor_data": "rigido_melhor_data",
    }
    return aliases.get(txt, "rigido_plano_externo")

MODO_EXECUCAO_FUTURO = normalizar_modo_execucao_futuro(_MODO_EXECUCAO_FUTURO_RAW)

ABA_GASTOS = _cfg_get(["abas", "despesas"], "Todos os Gastos")
ABA_INVENTARIO = _cfg_get(["abas", "lotes"], "Inventário de Lotes")
ABA_CARTEIRA = _cfg_get(["abas", "carteira"], "Carteira")

CDI_ANUAL = float(_cfg_get_any([
    ["premissas_mercado", "cdi_anual_modelo"],
    ["simulation", "cdi_anual"],
], default=0.1490))
PRODUTO_PADRAO = None
TAXA_DIA_BASE = ((1 + CDI_ANUAL) ** (1 / 252)) - 1

IOF_TABLE = np.array(_cfg_get_required(["iof", "tabela"]), dtype=np.float64)
if IOF_TABLE.size == 29:
    IOF_TABLE = np.concatenate(([1.0], IOF_TABLE))
elif IOF_TABLE.size != 30:
    raise RuntimeError(f"config['iof']['tabela'] deve ter 29 ou 30 valores; recebido: {IOF_TABLE.size}.")

IR_FAIXAS = {}
for faixa in _cfg_get(["ir", "faixas"], []) or []:
    dias_max = faixa.get("dias_max")
    chave = 9999 if dias_max is None else int(dias_max)
    aliquota = float(faixa["aliquota"])
    IR_FAIXAS[chave] = {"ir": aliquota, "proxima": aliquota, "delta": 0.0}
if IR_FAIXAS:
    _ordenadas = sorted(IR_FAIXAS.keys())
    for i, chave in enumerate(_ordenadas):
        prox = _ordenadas[i + 1] if i + 1 < len(_ordenadas) else chave
        IR_FAIXAS[chave]["proxima"] = IR_FAIXAS[prox]["ir"]
        IR_FAIXAS[chave]["delta"] = max(0.0, IR_FAIXAS[chave]["ir"] - IR_FAIXAS[prox]["ir"])

TAXA_BASE_DEFAULT = float(_cfg_get_required(["defaults_lote", "taxa_base_cdi"]))
TAXA_BONUS_DEFAULT = float(_cfg_get_required(["defaults_lote", "taxa_bonus_cdi"]))
DIAS_BONUS_DEFAULT = int(_cfg_get_required(["defaults_lote", "dias_bonus"]))
PRODUTO_FALLBACK_NOME_RAW = str(_cfg_get(["defaults_lote", "produto_fallback_nome"], ""))

DIAS_CLIFF_IR = int(_cfg_get_required(["pagamento", "dias_cliff_ir"]))
TOLERANCIA_MONETARIA = float(_cfg_get_required(["replay", "tolerancia_monetaria"]))
VALOR_MINIMO_LOTE_ATIVO = float(_cfg_get_required(["replay", "valor_minimo_lote_ativo"]))
VALOR_MINIMO_RESGATE_BRUTO = float(_cfg_get_required(["pagamento", "valor_minimo_resgate_bruto"]))
TOLERANCIA_AJUSTE_RESIDUAL_CONTA = float(_cfg_get(["pagamento", "tolerancia_ajuste_residual_conta"], 0.0) or 0.0)

SWITCHING_LIMIAR_GANHO = float(SWITCH_CFG.get("limiar_ganho_pct", 0.0001))
EXCLUIR_PRODUTOS_REGEX = list(_cfg_get(["switching", "excluir_produtos_regex"], [r"\bitau\b.*\b100%\b", r"cdb\s*itau\s*100"]) or [])
HORIZONTE_EXTRA_DIAS = int(SIM_CFG.get("horizonte_extra_dias", 365))
HORIZONTE_PROJECAO_DIAS = int(_cfg_get(["simulacao", "horizonte_extra_dias"], 365))
SWITCH_BUSCA_DIAS = int(_cfg_get(["switching", "switch_busca_dias"], 45))
PERMITIR_SWITCH_ANTES_30_DIAS = bool(_cfg_get(["switching", "permitir_switch_antes_30_dias"], False))
REOTIMIZAR_POOL_SWITCH_NO_FUTURO = bool(_cfg_get(["switching", "reotimizar_pool_switch_no_futuro"], True))
PERMITIR_SPLIT_LOTE = bool(_cfg_get(["switching", "permitir_split_lote"], True))
TOP_N_ALOCACAO = int(_cfg_get(["switching", "top_n_alocacao"], 4))
EXIBIR_ALERTAS_FALTA_CAIXA = bool(_cfg_get(["switching", "exibir_alertas_falta_caixa"], False))

TREINAMENTO_PERFIS = _cfg_get(["treinamento", "perfis"], {})
TREINAMENTO_MODO_AUTO = _cfg_get(["treinamento", "modo_auto"], {})
TREINAMENTO_MODO_AUTO_THRESHOLDS = TREINAMENTO_MODO_AUTO.get("thresholds", {}) if isinstance(TREINAMENTO_MODO_AUTO, dict) else {}
TREINAMENTO_REDUCAO_CONTAS = _cfg_get(["treinamento", "reducao_contas"], {})
TREINAMENTO_TEMPO_ALVO_MINIMO_ABSOLUTO = int((TREINAMENTO_MODO_AUTO or {}).get("tempo_alvo_minimo_absoluto", 3))
TREINAMENTO_TEMPO_ALVO_PADRAO_MINUTOS = int((TREINAMENTO_MODO_AUTO or {}).get("tempo_alvo_padrao_minutos", 12))

EXEC_DEFAULTS_INTERATIVOS = _cfg_get(["execucao", "defaults_interativos"], {}) or {}
MODO_TREINAMENTO_PADRAO = str(EXEC_DEFAULTS_INTERATIVOS.get("modo_treinamento_padrao", "1"))
PERFIL_TREINO_PADRAO = str(EXEC_DEFAULTS_INTERATIVOS.get("perfil_treino_padrao", "balanceado"))
PERFIL_TREINO_AUTO_OPCAO = str(EXEC_DEFAULTS_INTERATIVOS.get("perfil_treino_auto_opcao", "a"))
TEMPO_ALVO_AUTO_PADRAO_MINUTOS = int(EXEC_DEFAULTS_INTERATIVOS.get("tempo_alvo_auto_padrao_minutos", TREINAMENTO_TEMPO_ALVO_PADRAO_MINUTOS))

CFG_OPT_GEN = _cfg_get(["otimizacao", "genetica_profunda"], {}) or {}
CFG_OPT_PEN = _cfg_get(["otimizacao", "penalidade_5p"], {}) or {}
CFG_OPT_GEN_POP_INIT = CFG_OPT_GEN.get("populacao_inicial", {}) or {}
OPT_GEN_DIVISOR_POPSIZE_CLONES = int(CFG_OPT_GEN_POP_INIT.get("divisor_popsize_clones", 3))
OPT_GEN_MIN_CLONES = int(CFG_OPT_GEN_POP_INIT.get("min_clones", 1))
OPT_GEN_RUIDO_GAUSSIANO_DESVIO = float(CFG_OPT_GEN_POP_INIT.get("ruido_gaussiano_desvio", 0.1))
CFG_OPT_PEN_POP_INIT = CFG_OPT_PEN.get("populacao_inicial", {}) or {}
OPT_PEN_DIVISOR_POPSIZE_CLONES = int(CFG_OPT_PEN_POP_INIT.get("divisor_popsize_clones", 3))
OPT_PEN_MIN_CLONES = int(CFG_OPT_PEN_POP_INIT.get("min_clones", 1))
OPT_PEN_RUIDO_GAUSSIANO_DESVIO = float(CFG_OPT_PEN_POP_INIT.get("ruido_gaussiano_desvio", 0.1))
if OPT_GEN_DIVISOR_POPSIZE_CLONES < 1:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/divisor_popsize_clones deve ser >= 1")
if OPT_GEN_MIN_CLONES < 0:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/min_clones deve ser >= 0")
if OPT_GEN_RUIDO_GAUSSIANO_DESVIO < 0:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/ruido_gaussiano_desvio deve ser >= 0")
if OPT_PEN_DIVISOR_POPSIZE_CLONES < 1:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/divisor_popsize_clones deve ser >= 1")
if OPT_PEN_MIN_CLONES < 0:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/min_clones deve ser >= 0")
if OPT_PEN_RUIDO_GAUSSIANO_DESVIO < 0:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/ruido_gaussiano_desvio deve ser >= 0")

def _normalizar_conta_processamento(conta):
    """Normaliza a tupla de conta para (data, valor, desc, lote1, lote2, ordem)."""
    data = conta[0]
    valor = float(conta[1]) if len(conta) > 1 else 0.0
    desc = str(conta[2]) if len(conta) > 2 else ""
    lote1 = str(conta[3]).strip() if len(conta) > 3 and conta[3] is not None else ""
    lote2 = str(conta[4]).strip() if len(conta) > 4 and conta[4] is not None else ""
    ordem = int(conta[5]) if len(conta) > 5 and conta[5] is not None else ORDEM_PROCESSAMENTO_SENTINELA
    return data, valor, desc, lote1, lote2, ordem

def ordenar_contas_processamento(contas):
    """
    Ordena contas de forma estável e canônica, preservando a ordem original da planilha.
    """
    def _key(c):
        data = c[0]
        valor = float(c[1]) if len(c) > 1 else 0.0
        desc = str(c[2]) if len(c) > 2 else ""
        if len(c) >= 6:
            ordem = int(c[5]) if c[5] is not None else ORDEM_PROCESSAMENTO_SENTINELA
        elif len(c) == 4 and not isinstance(c[3], str):
            ordem = int(c[3]) if c[3] is not None else ORDEM_PROCESSAMENTO_SENTINELA
        else:
            ordem = ORDEM_PROCESSAMENTO_SENTINELA
        return (data, ordem, desc, valor)
    return sorted(contas, key=_key)

# =========================================================
# 07. INFRAESTRUTURA DE ARQUIVOS EXTERNOS E PLANILHAS
# =========================================================


def ler_aba_excel(nome_aba: str) -> pd.DataFrame:
    caminho = _resolver_arquivo_excel_local()
    chave = (str(caminho), str(nome_aba).strip())
    if chave not in DF_ABAS_CACHE:
        DF_ABAS_CACHE[chave] = pd.read_excel(caminho, sheet_name=nome_aba)
    return DF_ABAS_CACHE[chave].copy()

# =========================================================
# 08. HELPERS DE NOMES DE ABAS / COLUNAS
# =========================================================
_CFG_MISSING = object()

def _normalizar_token_coluna(valor) -> str:
    txt = "" if valor is None else str(valor)
    txt = txt.strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    txt = re.sub(r"[\s\-\/\(\)\[\]\{\}\.,;:]+", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def _normalizar_nome_coluna(col) -> str:
    return _normalizar_token_coluna(col)

def nome_aba(chave: str, default=_CFG_MISSING):
    """
    Compatibilidade entre os dois comportamentos originais:
      - obrigatório sem default;
      - opcional com fallback quando default for informado.
    """
    if default is _CFG_MISSING:
        return _cfg_get_required(["abas", chave])
    return _cfg_get(["abas", chave], default)

def aliases_coluna(secao: str, chave: str) -> list:
    aliases = _cfg_get(["colunas", secao, chave], None)
    if aliases is None:
        raise KeyError(f"Config de coluna ausente para {secao}/{chave}.")
    if not isinstance(aliases, list) or not aliases:
        raise KeyError(f"Aliases de coluna inválidos para {secao}/{chave}.")
    return aliases

def resolver_coluna(df: pd.DataFrame, secao: str, chave: str, required: bool = True):
    if df is None or len(getattr(df, "columns", [])) == 0:
        if required:
            raise KeyError(f"DataFrame vazio ao resolver coluna {secao}/{chave}.")
        return None

    cols_reais = list(df.columns)
    mapa_norm = {_normalizar_token_coluna(c): c for c in cols_reais}
    aliases = aliases_coluna(secao, chave)

    for alias in aliases:
        alias_norm = _normalizar_token_coluna(alias)
        if alias_norm in mapa_norm:
            return mapa_norm[alias_norm]

    if required:
        raise KeyError(
            f"Coluna não encontrada para {secao}/{chave}. "
            f"Aliases tentados: {aliases}. Colunas disponíveis: {cols_reais}"
        )
    return None

def _to_cdi_multiplier(x, default=1.0):
    """Converte um valor de planilha para multiplicador CDI."""
    try:
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return float(default)
        s = str(x).strip()
        if POL_TAXA_REMOVER_PERCENTUAL_STRING:
            s = s.replace('%', '')
        if POL_TAXA_SUBSTITUIR_VIRGULA_DECIMAL:
            s = s.replace(',', '.')
        if not s:
            return float(default)
        v = float(s)
        if v > POL_TAXA_LIMITE_PERCENTUAL_VS_MULTIPLICADOR:
            return v / 100.0
        return v
    except Exception:
        return float(default)

def _to_bool_produto(valor, default=False):
    if valor is None:
        return default
    try:
        if isinstance(valor, bool):
            return valor
        s = str(valor).strip().lower()
        if s in {"1", "true", "t", "sim", "s", "ok", "ativo", "yes", "y"}:
            return True
        if s in {"0", "false", "f", "nao", "não", "n", "inativo", "no"}:
            return False
        return default
    except Exception:
        return default

def _to_int_produto(valor, default=0):
    if valor is None or valor == "":
        return default
    try:
        s = str(valor).strip().replace(",", ".")
        return int(float(s))
    except Exception:
        return default

def _to_float_produto(valor, default=0.0):
    if valor is None or valor == "":
        return default
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        s = str(valor).strip()
        s = s.replace("R$", "").replace("%", "").replace(".", "").replace(",", ".")
        return float(s)
    except Exception:
        try:
            s = str(valor).strip().replace(",", ".")
            return float(s)
        except Exception:
            return default

def _normalizar_taxa_cdi(valor, *, default=0.0, limite_percentual_vs_multiplicador=10.0):
    if valor is None or valor == "":
        return default
    try:
        if isinstance(valor, (int, float)):
            x = float(valor)
        else:
            s = str(valor).strip().replace("%", "").replace(",", ".")
            x = float(s)
        if x >= limite_percentual_vs_multiplicador:
            return x / 100.0
        return x
    except Exception:
        return default

def _gerar_produto_key(produto_id, nome, normalizar_nome_fn):
    pid = None if produto_id is None else str(produto_id).strip()
    if pid:
        return pid
    nome = "" if nome is None else str(nome)
    nome_norm = normalizar_nome_fn(nome) if callable(normalizar_nome_fn) else nome.strip().lower()
    return f"prod::{nome_norm}"

def _normalizar_texto_produto(valor, default=""):
    if valor is None:
        return default
    try:
        return " ".join(str(valor).strip().split())
    except Exception:
        return default

def _switch_lotes_base(lotes_passados):
    lotes_base = copy.deepcopy([l for l in lotes_passados if (not l.esgotado and l.saldo_bruto > 0.01)])
    for l in lotes_base:
        l.switch_agendado = None
    return lotes_base

def _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos, agenda=None):
    lotes_cen = copy.deepcopy(lotes_base)
    agenda = agenda or {}
    if agenda:
        mapa = {x.id: x for x in lotes_cen}
        for lid, (dd, pp) in agenda.items():
            if lid in mapa:
                mapa[lid].switch_agendado = (dd, pp)
    _, met = simular_futuro(lotes_cen, contas, bcb_map, data_inicio=hoje, produtos=produtos, verbose=False)
    return float(met.get('riqueza', 0.0))

def _avaliar_iteracao_switch(lotes_base, contas, produtos, bcb_map, hoje, agenda_atual, riqueza_atual, iteracao):
    melhor_ganho = 0.0
    melhor_lote_id = None
    melhor_acao = None
    melhor_riqueza = riqueza_atual
    analise_iter = []
    pref_dates = {dd for (dd, _pp) in agenda_atual.values()}

    for lote in lotes_base:
        if lote.id in agenda_atual:
            continue
        cands = avaliar_switch_lote(lote, contas, produtos, bcb_map, hoje, preferred_datas=pref_dates, top_k=3)
        if not cands:
            continue
        for score_individual, data_sw, prod_sw in cands:
            agenda_teste = dict(agenda_atual)
            agenda_teste[lote.id] = (data_sw, prod_sw)
            riqueza_cen = _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos, agenda_teste)
            ganho = riqueza_cen - riqueza_atual
            analise_iter.append({
                'iter': iteracao,
                'lote': lote.id,
                'data_switch': data_sw,
                'produto_novo': prod_sw.nome,
                'ganho_portfolio': ganho,
                'riqueza_cen': riqueza_cen,
                'riqueza_base_iter': riqueza_atual,
                'score_individual': score_individual,
            })
            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_lote_id = lote.id
                melhor_acao = (data_sw, prod_sw)
                melhor_riqueza = riqueza_cen

    return melhor_lote_id, melhor_acao, melhor_ganho, melhor_riqueza, analise_iter

def _decisoes_switch_marginais(lotes_base, contas, produtos, bcb_map, hoje, agenda_atual, riqueza_base, riqueza_final):
    decisoes = {}
    if not agenda_atual:
        return decisoes
    for lid, (data_sw, prod_sw) in agenda_atual.items():
        agenda_sem = {lid2: v for lid2, v in agenda_atual.items() if lid2 != lid}
        riqueza_sem = _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos, agenda_sem)
        ganho_marg = riqueza_final - riqueza_sem
        decisoes[lid] = (data_sw, prod_sw, ganho_marg)
    return decisoes

def otimizar_switches_portfolio_guloso(lotes_passados: list, contas: list, produtos: list, bcb_map: dict, hoje: date,
                                       max_iter: int = 10, min_ganho_abs: float = 1.0, verbose: bool = True):
    lotes_base = _switch_lotes_base(lotes_passados)
    riqueza_base = _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos)
    riqueza_atual = riqueza_base
    agenda_atual = {}
    analise = []

    if verbose:
        print(f"\n>>> [SWITCH-OPT] riqueza baseline: R$ {riqueza_base:,.2f} | lotes: {len(lotes_base)}")

    for it in range(1, max_iter + 1):
        melhor_lote_id, melhor_acao, melhor_ganho, melhor_riqueza, analise_iter = _avaliar_iteracao_switch(
            lotes_base, contas, produtos, bcb_map, hoje, agenda_atual, riqueza_atual, it
        )
        analise.extend(analise_iter)

        if melhor_lote_id is None or melhor_ganho < min_ganho_abs:
            if verbose:
                print(f">>> [SWITCH-OPT] parada na iteração {it}: melhor ganho R$ {melhor_ganho:,.2f} < limiar R$ {min_ganho_abs:,.2f}")
            break

        agenda_atual[melhor_lote_id] = melhor_acao
        riqueza_atual = melhor_riqueza
        if verbose:
            print(f">>> [SWITCH-OPT] it {it}: aplica {melhor_lote_id} -> {melhor_acao[1].nome} em {melhor_acao[0]} | ganho R$ {melhor_ganho:,.2f} | riqueza R$ {riqueza_atual:,.2f}")

    riqueza_final = _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos, agenda_atual) if agenda_atual else riqueza_base
    decisoes = _decisoes_switch_marginais(lotes_base, contas, produtos, bcb_map, hoje, agenda_atual, riqueza_base, riqueza_final)

    df_a = pd.DataFrame(analise)
    if not df_a.empty:
        df_a.sort_values(['iter', 'ganho_portfolio'], ascending=[True, False], inplace=True)
        analise = df_a.to_dict('records')

    return decisoes, analise, riqueza_base, riqueza_final

def _normalizar_plano(plano):
    out = []
    for pp, vv in (plano or []):
        try:
            nome = pp.nome
        except Exception:
            nome = str(pp)
        out.append((nome, round(float(vv), 2)))
    out.sort(key=lambda x: x[0])
    return tuple(out)

def _comparar_reconhecimento_coluna_produto(df_lotes, col_produto, investimentos_map, *, normalizar_nome_fn=None):
    """Mede reconhecimento dos valores de uma coluna de produto contra um mapa de investimentos."""
    if normalizar_nome_fn is None:
        normalizar_nome_fn = normalizar_nome

    reconhecidos = set()
    nao_reconhecidos = set()
    total_validos = 0
    reconhecidos_por_valor = 0

    if col_produto is None or col_produto not in df_lotes.columns:
        return {
            "qtd_reconhecidos": 0,
            "qtd_nao_reconhecidos": 0,
            "reconhecidos": [],
            "nao_reconhecidos": [],
            "match_rate": 0.0,
        }

    for valor in df_lotes[col_produto].tolist():
        if valor is None:
            continue
        s = str(valor).strip()
        if s == "" or s.lower() == "nan":
            continue

        total_validos += 1
        nome_norm = normalizar_nome_fn(s)
        if nome_norm in investimentos_map:
            reconhecidos.add(nome_norm)
            reconhecidos_por_valor += 1
        else:
            nao_reconhecidos.add(nome_norm)

    match_rate = (reconhecidos_por_valor / total_validos) if total_validos > 0 else 0.0

    return {
        "qtd_reconhecidos": len(reconhecidos),
        "qtd_nao_reconhecidos": len(nao_reconhecidos),
        "reconhecidos": sorted(list(reconhecidos)),
        "nao_reconhecidos": sorted(list(nao_reconhecidos)),
        "match_rate": match_rate,
    }

def _resolver_colunas_carteira(df: pd.DataFrame) -> dict:
    """
    Resolve as colunas da aba Carteira usando o padrão canônico do config,
    mantendo aliases legados esperados pelo restante do script.
    """
    cols = {
        "nome": resolver_coluna(df, "carteira", "nome"),
        "taxa_base": resolver_coluna(df, "carteira", "taxa_base"),
        "taxa_bonus": resolver_coluna(df, "carteira", "taxa_bonus", required=False),
        "dias_bonus": resolver_coluna(df, "carteira", "dias_bonus", required=False),
        "prazo_dias": resolver_coluna(df, "carteira", "prazo_dias", required=False),
        "carencia_dias": resolver_coluna(df, "carteira", "carencia_dias", required=False),
        "liquidez_dias": resolver_coluna(df, "carteira", "liquidez_dias", required=False),
        "isento_ir": resolver_coluna(df, "carteira", "isento_ir", required=False),
        "aplicacao_minima": resolver_coluna(df, "carteira", "aplicacao_minima", required=False),
        "aplicacao_maxima": resolver_coluna(df, "carteira", "aplicacao_maxima", required=False),
        "ativo": resolver_coluna(df, "carteira", "ativo", required=False),
        "tipo": resolver_coluna(df, "carteira", "tipo", required=False),
        "indexador": resolver_coluna(df, "carteira", "indexador", required=False),
        "fgc": resolver_coluna(df, "carteira", "fgc", required=False),
        "observacoes": resolver_coluna(df, "carteira", "observacoes", required=False),
        "banco_emissor": resolver_coluna(df, "carteira", "banco_emissor", required=False),
        "risco_real": resolver_coluna(df, "carteira", "risco_real", required=False),
        "max_usos": resolver_coluna(df, "carteira", "max_usos", required=False),
        "somente_combo": resolver_coluna(df, "carteira", "somente_combo", required=False),
        "produto_base": resolver_coluna(df, "carteira", "produto_base", required=False),
        "produto_bonus": resolver_coluna(df, "carteira", "produto_bonus", required=False),
        "ratio_base": resolver_coluna(df, "carteira", "ratio_base", required=False),
        "ratio_bonus": resolver_coluna(df, "carteira", "ratio_bonus", required=False),
        "produto_id": resolver_coluna(df, "carteira", "produto_id", required=False),
    }

    cols["prazo"] = cols["prazo_dias"]
    cols["carencia"] = cols["carencia_dias"]
    cols["valor_min"] = cols["aplicacao_minima"]
    cols["valor_max"] = cols["aplicacao_maxima"]
    cols["obs"] = cols["observacoes"]
    cols["banco"] = cols["banco_emissor"]
    cols["risco"] = cols["risco_real"]

    cols["isento"] = cols["isento_ir"]
    cols["minimo"] = cols["aplicacao_minima"]
    cols["maximo"] = cols["aplicacao_maxima"]
    cols["base"] = cols["produto_base"]
    cols["bonus"] = cols["produto_bonus"]

    if not cols["minimo"]:
        raise ValueError("Coluna obrigatória de aplicação mínima não encontrada na aba Carteira.")

    return cols

def _parse_bool_planilha(valor, verdadeiros=("SIM", "S", "TRUE", "1", "ATIVO", "ISENTO")):
    if pd.isna(valor):
        return False
    return str(valor).upper().strip() in verdadeiros

def _parse_prazo_dias(valor):
    if pd.isna(valor):
        return 0
    txt = str(valor).strip()
    match = re.search(r"(\d+)", txt)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+\.?\d*)", txt)
    if match and "ano" in txt.lower():
        return int(float(match.group(1)) * 365)
    return 0

def _criar_produto_simples(row, cols):
    nome = str(row[cols["nome"]]).strip()
    taxa_base_val = _to_float_br(str(row[cols["taxa_base"]]).replace("%", ""), default=0.0)
    taxa_base = taxa_base_val / 100.0
    taxa_bonus = taxa_base
    dias_bonus = 0

    if cols["taxa_bonus"] and pd.notna(row.get(cols["taxa_bonus"])):
        taxa_bonus_val = _to_float_br(str(row[cols["taxa_bonus"]]).replace("%", ""), default=taxa_base_val)
        taxa_bonus = taxa_bonus_val / 100.0
    if cols["dias_bonus"] and pd.notna(row.get(cols["dias_bonus"])):
        dias_bonus = int(row[cols["dias_bonus"]])

    prazo_dias = _parse_prazo_dias(row.get(cols["prazo"])) if cols["prazo"] else 0
    carencia_dias = _parse_prazo_dias(row.get(cols["carencia"])) if cols["carencia"] else 0
    isento = _parse_bool_planilha(row.get(cols["isento"]), verdadeiros=("SIM", "S", "TRUE", "1", "ISENTO")) if cols["isento"] else False
    valor_min = _to_float_br(row[cols["minimo"]], default=0.0)
    valor_max = _to_float_br(row.get(cols["maximo"]), default=1e12) if cols["maximo"] else 1e12
    ativo = _parse_bool_planilha(row.get(cols["ativo"])) if cols["ativo"] else True

    for _rx in EXCLUIR_PRODUTOS_REGEX:
        if re.search(_rx, nome, flags=re.IGNORECASE):
            ativo = False
            break

    return Produto(
        nome=nome,
        taxa_base=taxa_base,
        taxa_bonus=taxa_bonus,
        dias_bonus=dias_bonus,
        prazo_dias=prazo_dias,
        carencia_dias=carencia_dias,
        isento_ir=isento,
        valor_min=valor_min,
        valor_max=valor_max,
        ativo=ativo,
    )

def _resolver_combo_por_nome(nome_combo: str, produtos_simples: dict):
    nome_norm = _normalizar_nome_texto(nome_combo)

    def _find_produto_by_pred(pred):
        for nm, produto in produtos_simples.items():
            if isinstance(produto, Produto) and pred(_normalizar_nome_texto(nm), produto):
                return produto
        return None

    if "combo" in nome_norm and "picpay" in nome_norm and "100-115" in nome_norm:
        base = _find_produto_by_pred(lambda nm, p: "picpay" in nm and "100" in nm and "combo" not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: "picpay" in nm and "115" in nm and "combo" not in nm)
        return base, bonus
    if "combo" in nome_norm and "picpay" in nome_norm and "100-120" in nome_norm and ("6 meses" in nome_norm or "6meses" in nome_norm or "180" in nome_norm):
        base = _find_produto_by_pred(lambda nm, p: ("6 meses" in nm or "6meses" in nm) and "100" in nm and "cdi" in nm and "combo" not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: ("6 meses" in nm or "6meses" in nm) and "120" in nm and "picpay" in nm and "combo" not in nm)
        return base, bonus
    if "combo" in nome_norm and "picpay" in nome_norm and "100-120" in nome_norm and ("3 meses" in nome_norm or "3meses" in nome_norm or "90" in nome_norm):
        base = _find_produto_by_pred(lambda nm, p: ("3 meses" in nm or "3meses" in nm) and "100" in nm and "cdi" in nm and "combo" not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: ("3 meses" in nm or "3meses" in nm) and "120" in nm and "picpay" in nm and "combo" not in nm)
        return base, bonus
    return None, None

def _carregar_produtos_da_carteira(df, cols):
    produtos_simples = {}
    combos = []
    for _, row in df.iterrows():
        nome = str(row[cols["nome"]]).strip()
        if not nome:
            continue
        eh_combo = (
            (cols["tipo"] and pd.notna(row.get(cols["tipo"])) and "combo" in str(row[cols["tipo"]]).lower())
            or "combo" in nome.lower()
        )
        if eh_combo:
            combos.append(row)
            continue
        produto = _criar_produto_simples(row, cols)
        if nome in produtos_simples:
            print(f"   Aviso: Produto com nome '{nome}' já existe. O último será sobrescrito. Considere usar nomes únicos.")
        produtos_simples[nome] = produto
    return produtos_simples, combos

def _carregar_combos_da_carteira(combos, cols, produtos_simples):
    for row in combos:
        nome = str(row[cols["nome"]]).strip()
        ativo = _parse_bool_planilha(row.get(cols["ativo"])) if cols["ativo"] else True
        base_prod = bonus_prod = None
        if cols["base"] and cols["bonus"] and row.get(cols["base"]) and row.get(cols["bonus"]):
            base_prod = produtos_simples.get(str(row[cols["base"]]).strip())
            bonus_prod = produtos_simples.get(str(row[cols["bonus"]]).strip())
        if base_prod is None or bonus_prod is None:
            base_prod, bonus_prod = _resolver_combo_por_nome(nome, produtos_simples)
        if isinstance(base_prod, Produto) and isinstance(bonus_prod, Produto):
            produtos_simples[nome] = ComboProduto(nome, base_prod, bonus_prod, ativo=ativo)
        else:
            print(f"   Aviso: Combo '{nome}' não pôde ser resolvido de forma exata. Verifique se os produtos base/bônus existem na Carteira com nomes consistentes.")
    return produtos_simples

def carregar_carteira() -> list:
    aba_carteira = nome_aba("carteira", ABA_CARTEIRA)
    df = ler_aba_excel(aba_carteira)
    _log_debug(f"[CHECK] Aba '{aba_carteira}': linhas={len(df)} | colunas={list(df.columns)}", DEBUG_SCHEMA_ABAS)
    df.columns = [str(c).strip() for c in df.columns]
    cols = _resolver_colunas_carteira(df)
    produtos_simples, combos = _carregar_produtos_da_carteira(df, cols)
    produtos_simples = _carregar_combos_da_carteira(combos, cols, produtos_simples)
    return list(produtos_simples.values())

def _listar_candidatos_parametros(nome_arquivo='melhores_parametros_5p.json'):
    candidatos = []

    cwd = Path.cwd().resolve()
    candidatos.append(cwd / nome_arquivo)
    candidatos.append(cwd / 'code' / nome_arquivo)

    if Path('/content').exists():
        candidatos.append(Path('/content') / nome_arquivo)
        candidatos.append(Path('/content/code') / nome_arquivo)

    try:
        script_dir = Path(__file__).resolve().parent
        candidatos.append(script_dir / nome_arquivo)
        candidatos.append(script_dir / 'code' / nome_arquivo)
        candidatos.append(script_dir.parent / nome_arquivo)
        candidatos.append(script_dir.parent / 'code' / nome_arquivo)
    except NameError:
        pass

    for caminho in _iterar_candidatos_arquivo(nome_arquivo):
        candidatos.append(caminho)

    vistos = set()
    unicos = []
    for caminho in candidatos:
        chave = str(caminho.resolve()) if caminho.exists() else str(caminho)
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(caminho)
    return unicos

def _eh_dict_params_hibrido(obj):
    if not isinstance(obj, dict):
        return False
    chaves_base = {'peso_iof', 'peso_ir', 'peso_idade', 'peso_liq', 'peso_cliff'}
    return chaves_base.issubset(set(obj.keys()))

def _extrair_params_hibrido_de_obj(data):
    if not isinstance(data, dict):
        return None

    candidatos = []

    if isinstance(data.get('params'), dict):
        candidatos.extend([
            data['params'].get('hibrido_6p'),
            data['params'].get('hibrido_5p'),
            data['params'].get('penalidade'),
        ])

    candidatos.extend([
        data.get('hibrido_6p'),
        data.get('hibrido_5p'),
        data.get('penalidade'),
        data,
    ])

    for cand in candidatos:
        if _eh_dict_params_hibrido(cand):
            out = dict(cand)
            if 'peso_vpl' not in out:
                out['peso_vpl'] = 0.0
            return out

    return None

def _carregar_json_parametros(path_arquivo):
    try:
        raw = Path(path_arquivo).read_text(encoding='utf-8-sig').strip()
        if not raw:
            return None
        data = json.loads(raw)
        return _extrair_params_hibrido_de_obj(data)
    except Exception:
        return None

def carregar_parametros_hibrido_5p():
    candidatos_locais = _listar_candidatos_parametros(_normalizar_nome_arquivo_json(PARAM_5P_FIXO))

    for caminho in candidatos_locais:
        if not caminho.exists():
            continue
        params = _carregar_json_parametros(caminho)
        if params is not None:
            return params, caminho.resolve()

    candidatos_download = []

    if 'FALLBACK_PARAM_URL_5P' in globals() and FALLBACK_PARAM_URL_5P:
        candidatos_download.append(FALLBACK_PARAM_URL_5P)

    file_id_cfg = None
    if isinstance(GOOGLE_CFG, dict):
        file_id_cfg = GOOGLE_CFG.get('fallback_param_5p_file_id')
    if file_id_cfg:
        candidatos_download.append(f'https://drive.google.com/file/d/{file_id_cfg}/view?usp=sharing')

    candidatos_download_unicos = []
    vistos_dl = set()
    for url in candidatos_download:
        if not url or url in vistos_dl:
            continue
        vistos_dl.add(url)
        candidatos_download_unicos.append(url)

    for idx, url in enumerate(candidatos_download_unicos, start=1):
        destino = Path('/content/melhores_parametros_5p.json') if Path('/content').exists() else Path(_normalizar_nome_arquivo_json('melhores_parametros_5p'))
        try:
            if destino.exists():
                destino.unlink()
        except Exception:
            pass

        ok = baixar_arquivo_drive(url, str(destino))
        if not ok or not destino.exists():
            continue

        params = _carregar_json_parametros(destino)
        if params is not None:
            return params, destino.resolve()

    return None, None

def carregar_parametros_hibrido_5p_passado():
    """Carrega parâmetros reais do HIBRIDO_5P apenas para o replay do passado."""
    params, origem = carregar_parametros_hibrido_5p()
    if params is None:
        params = {
            'peso_iof': 100.0,
            'peso_ir': 0.0,
            'peso_idade': 0.1,
            'peso_liq': 0.0,
            'peso_cliff': 1000.0,
            'peso_vpl': 0.0,
        }
        origem = 'default_otimizador_base'
    return params, origem

def _normalizar_data_plano_externo(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, pd.Timestamp):
        return valor.date()
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None

def _carregar_plano_externo_dataframe(df: pd.DataFrame):
    cols = {str(c).strip().lower(): c for c in df.columns}
    obrig = ['data', 'conta', 'lote', 'bruto', 'liquido']
    if not all(k in cols for k in obrig):
        return None

    plano = {}
    for _, row in df.iterrows():
        d = _normalizar_data_plano_externo(row[cols['data']])
        conta = row[cols['conta']]
        lote = row[cols['lote']]
        bruto = row[cols['bruto']]
        liquido = row[cols['liquido']]
        if d is None or pd.isna(conta) or pd.isna(lote) or pd.isna(bruto):
            continue
        chave = (d, str(conta).strip())
        plano.setdefault(chave, []).append({
            'Lote': str(lote).strip(),
            'Bruto': float(bruto or 0.0),
            'Liquido': float(liquido or 0.0) if not pd.isna(liquido) else None,
        })
    return plano

def _listar_diretorios_busca_resultados():
    dirs = []
    cwd = Path.cwd().resolve()
    dirs.append(cwd)
    if Path('/content').exists():
        dirs.append(Path('/content').resolve())
    try:
        script_dir = Path(__file__).resolve().parent
        dirs.append(script_dir)
        dirs.append(script_dir.parent)
    except NameError:
        pass

    vistos = set()
    unicos = []
    for d in dirs:
        try:
            chave = str(d.resolve())
        except Exception:
            chave = str(d)
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(d)
    return unicos

def _listar_candidatos_resultado_otimizador():
    candidatos = []
    if RESULTADO_OTIMIZADOR_FIXO:
        candidatos.append(Path(RESULTADO_OTIMIZADOR_FIXO))

    if isinstance(PATHS_CFG, dict):
        for chave_cfg in [
            'resultado_otimizador',
            'resultado_otimizador_hibrido',
            'optimizer_result',
            'external_plan_file',
        ]:
            nome_cfg = PATHS_CFG.get(chave_cfg)
            if nome_cfg:
                for caminho in _iterar_candidatos_arquivo(str(nome_cfg)):
                    candidatos.append(caminho)

    nomes_exatos = [
        'resultado_economica_cliff_agrupado.xlsx',
        'resultado_economica_vpl_agrupado.xlsx',
        'resultado_economica_cliff_individual.xlsx',
        'resultado_economica_vpl_individual.xlsx',
        'resultado_hibrido_5p_agrupado.xlsx',
        'resultado_hibrido_5p_individual.xlsx',
        'resultado_otimizador.xlsx',
    ]
    for nome in nomes_exatos:
        for caminho in _iterar_candidatos_arquivo(nome):
            candidatos.append(caminho)

    padroes = [
        'resultado_*_agrupado.xlsx',
        'resultado_*_individual.xlsx',
        'resultado_*.xlsx',
    ]
    for base in _listar_diretorios_busca_resultados():
        for padrao in padroes:
            try:
                for caminho in sorted(base.glob(padrao)):
                    candidatos.append(caminho)
            except Exception:
                pass

    vistos = set()
    unicos = []
    for caminho in candidatos:
        try:
            chave = str(caminho.resolve()) if caminho.exists() else str(caminho)
        except Exception:
            chave = str(caminho)
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(caminho)
    return unicos

def _score_arquivo_resultado_otimizador(caminho: Path):
    nome = caminho.name.lower()
    score = 0
    if 'economica_cliff' in nome:
        score += 1000
    if 'economica_vpl' in nome:
        score += 950
    if 'agrupado' in nome:
        score += 300
    if 'individual' in nome:
        score += 200
    if 'hibrido_5p' in nome:
        score += 100
    if 'resultado_otimizador' in nome:
        score += 50
    return score

def carregar_plano_pagamentos_externo():
    validos = []
    for caminho in _listar_candidatos_resultado_otimizador():
        if not caminho.exists() or not caminho.is_file():
            continue
        try:
            df_ext = pd.read_excel(caminho, sheet_name='Extrato')
            plano = _carregar_plano_externo_dataframe(df_ext)
            if plano:
                try:
                    mtime = caminho.stat().st_mtime
                except Exception:
                    mtime = 0.0
                validos.append((
                    _score_arquivo_resultado_otimizador(caminho),
                    mtime,
                    plano,
                    caminho.resolve(),
                ))
        except Exception:
            continue

    if not validos:
        return None, None

    validos.sort(key=lambda x: (x[0], x[1]), reverse=True)
    _, _, plano, origem = validos[0]
    return plano, origem

def _ajustar_modo_por_compatibilidade_plano(diag):
    modo_atual = normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)
    DIAGNOSTICO_MODO_EXECUCAO['modo_solicitado'] = modo_atual
    if modo_atual != 'rigido_plano_externo':
        DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_atual
        return modo_atual
    if not AUTO_REBAIXAR_MODO_SE_PLANO_INCOMPATIVEL:
        DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_atual
        return modo_atual
    if not isinstance(diag, dict) or diag.get('ok', True):
        DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_atual
        return modo_atual
    modo_novo = normalizar_modo_execucao_futuro(MODO_FALLBACK_PLANO_INCOMPATIVEL)
    if modo_novo == modo_atual:
        DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_atual
        return modo_atual
    motivos_lista = list(diag.get('motivos') or ['incompatibilidade_material'])
    motivos = ', '.join(motivos_lista)
    _log_debug(f">>> [PLANO-EXT] Incompatibilidade material detectada ({motivos}). Modo alterado automaticamente para: {modo_novo}", AUDITAR_PLANO_EXTERNO)
    _log_debug(">>> [PLANO-EXT] Plano externo carregado apenas para auditoria; a execução real seguirá o modo efetivo.", AUDITAR_PLANO_EXTERNO)
    globals()['MODO_EXECUCAO_FUTURO'] = modo_novo
    DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_novo
    DIAGNOSTICO_MODO_EXECUCAO['houve_rebaixamento'] = True
    DIAGNOSTICO_MODO_EXECUCAO['motivos_rebaixamento'] = motivos_lista
    DIAGNOSTICO_MODO_EXECUCAO['observacao'] = 'Plano externo carregado apenas para auditoria; execução real em modo efetivo.'
    return modo_novo

def _registrar_auditoria_plano(lista, *, data_ref, conta, lote_planejado=None, lote_executado=None,
                               bruto_planejado=None, bruto_executado=None, status=None, motivo=None,
                               modo=None):
    lista.append({
        'Data': data_ref,
        'Conta': conta,
        'Lote Planejado': lote_planejado,
        'Lote Executado': lote_executado,
        'Bruto Planejado': round(float(bruto_planejado), 2) if bruto_planejado is not None else None,
        'Bruto Executado': round(float(bruto_executado), 2) if bruto_executado is not None else None,
        'Status': status,
        'Motivo': motivo,
        'Modo': modo,
    })

def _df_or_empty(valor):
    return valor if isinstance(valor, pd.DataFrame) else pd.DataFrame(valor or [])

def _escrever_se_nao_vazio(writer, df, sheet_name, **kwargs):
    if df is not None and not df.empty:
        df.to_excel(writer, sheet_name=sheet_name, index=False, **kwargs)

def _gerar_df_consolidado(df, group_cols, value_col='Valor'):
    if df is None or df.empty:
        return pd.DataFrame()
    return (df.groupby(group_cols, as_index=False)[value_col].sum()
              .sort_values([group_cols[0], value_col], ascending=[True, False]))

def _montar_df_carteira_exportacao(produtos):
    linhas = []
    for p in produtos:
        if isinstance(p, ComboProduto):
            linhas.append({
                'Nome': p.nome,
                'Tipo': 'Combo',
                'Base': p.produto_base.nome,
                'Bonus': p.produto_bonus.nome,
                'Min (R$)': p.valor_min,
                'Max (R$)': p.valor_max,
                'Ativo': 'Sim' if p.ativo else 'Não'
            })
        else:
            linhas.append({
                'Nome': p.nome,
                'Taxa_Base_CDI': p.taxa_base * 100,
                'Taxa_Bonus_CDI': p.taxa_bonus * 100 if p.taxa_bonus != p.taxa_base else '',
                'Dias_Bonus': p.dias_bonus,
                'Prazo_Dias': p.prazo_dias,
                'Carencia_Dias': p.carencia_dias,
                'Isento_IR': 'Sim' if p.isento_ir else 'Não',
                'Min (R$)': p.valor_min,
                'Max (R$)': p.valor_max,
                'Ativo': 'Sim' if p.ativo else 'Não'
            })
    return pd.DataFrame(linhas)

def _montar_df_diagnostico_modo_execucao():
    diag = DIAGNOSTICO_MODO_EXECUCAO or {}
    return pd.DataFrame([
        {
            'modo_solicitado': diag.get('modo_solicitado'),
            'modo_efetivo': diag.get('modo_efetivo'),
            'houve_rebaixamento': 'Sim' if diag.get('houve_rebaixamento') else 'Não',
            'motivos_rebaixamento': '; '.join(diag.get('motivos_rebaixamento') or []),
            'plano_externo_carregado': 'Sim' if diag.get('plano_externo_carregado') else 'Não',
            'origem_plano_externo': diag.get('origem_plano_externo'),
            'observacao': diag.get('observacao'),
        }
    ])

def _escrever_resultados_excel(arquivo_saida, *, extrato_df, log_passado, df_relatorio,
                               df_analise_switch, df_validacao_pool, df_plano_aportes,
                               df_plano_switches, df_switches_detalhados,
                               df_exec_plano_externo, df_desvios_plano_externo,
                               df_fallbacks_plano_externo, df_diag_datas, df_diag_planos,
                               df_comparativo_validacao, df_diagnostico_modo, stats, df_resumo_lotes_atuais, produtos):
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        _escrever_se_nao_vazio(writer, extrato_df, 'Extrato Futuro')
        _escrever_se_nao_vazio(writer, pd.DataFrame(log_passado), 'Extrato Passado')
        df_relatorio.to_excel(writer, sheet_name='Situação Final', index=False)
        _escrever_se_nao_vazio(writer, df_plano_aportes, 'Plano_Aportes')
        _escrever_se_nao_vazio(writer, df_plano_switches, 'Plano_Switches')
        _escrever_se_nao_vazio(writer, df_switches_detalhados, 'Switches_Detalhados')
        if EXPORTAR_DEBUG:
            _escrever_se_nao_vazio(writer, df_analise_switch, 'Analise_Switch')
            _escrever_se_nao_vazio(writer, df_validacao_pool, 'Validacao_Pooling')
            _escrever_se_nao_vazio(writer, _gerar_df_consolidado(df_plano_aportes, ['Data', 'Produto']), 'Aportes_Consolidados')
            _escrever_se_nao_vazio(writer, _gerar_df_consolidado(df_plano_switches, ['Data', 'Produto']), 'Switches_Consolidados')
            _escrever_se_nao_vazio(writer, df_exec_plano_externo, 'Execucao_Plano_Externo')
            _escrever_se_nao_vazio(writer, df_desvios_plano_externo, 'Desvios_Plano_Externo')
            _escrever_se_nao_vazio(writer, df_fallbacks_plano_externo, 'Fallbacks_Plano_Externo')
            _escrever_se_nao_vazio(writer, df_diag_datas, 'Diagnostico_Datas')
            _escrever_se_nao_vazio(writer, df_diag_planos, 'Diagnostico_Planos')
            _escrever_se_nao_vazio(writer, df_comparativo_validacao, 'Comparativo_Validacao')
        if df_diagnostico_modo is None or getattr(df_diagnostico_modo, 'empty', True):
            df_diagnostico_modo = pd.DataFrame([{
                'modo_solicitado': DIAGNOSTICO_MODO_EXECUCAO.get('modo_solicitado'),
                'modo_efetivo': DIAGNOSTICO_MODO_EXECUCAO.get('modo_efetivo'),
                'houve_rebaixamento': 'Sim' if DIAGNOSTICO_MODO_EXECUCAO.get('houve_rebaixamento') else 'Não',
                'motivos_rebaixamento': '; '.join(DIAGNOSTICO_MODO_EXECUCAO.get('motivos_rebaixamento', [])),
                'plano_externo_carregado': 'Sim' if DIAGNOSTICO_MODO_EXECUCAO.get('plano_externo_carregado') else 'Não',
                'origem_plano_externo': DIAGNOSTICO_MODO_EXECUCAO.get('origem_plano_externo'),
                'observacao': DIAGNOSTICO_MODO_EXECUCAO.get('observacao', ''),
            }])
        if EXPORTAR_DEBUG:
            df_diagnostico_modo.to_excel(writer, sheet_name='Diagnostico_Modo', index=False)

        pd.DataFrame([stats]).to_excel(writer, sheet_name='Resumo', index=False, startrow=0)
        _escrever_se_nao_vazio(writer, df_resumo_lotes_atuais, 'Resumo', startrow=4)
        _montar_df_carteira_exportacao(produtos).to_excel(writer, sheet_name='Carteira', index=False)

def _imprimir_resumo_consolidado_switches(plano_switches_final):
    if not plano_switches_final or not _debug_ativo(DEBUG_SWITCH_EXECUCAO):
        return
    print("\n    Resumo consolidado de switches planejados (um por lote; valores líquidos estimados):")
    df_sw_console = pd.DataFrame(plano_switches_final)
    df_cons = _gerar_df_consolidado(df_sw_console, ['Data', 'Produto'])
    for _, rr in df_cons.iterrows():
        print(f"      - {rr['Data']} | {rr['Produto']:<24} | aplicar R$ {float(rr['Valor']):>10,.2f}")

def diagnosticar_resolvedor_hibrido_5p(lotes_disponiveis, alvo_liquido, data_atual, params, data_final, valores_otimos=None, bcb_map=None, taxa_proj=None):
    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE

    if isinstance(params, dict):
        p_iof = float(params.get('peso_iof', 100.0))
        p_ir = float(params.get('peso_ir', 0.0))
        p_age = float(params.get('peso_idade', 0.1))
        p_liq = float(params.get('peso_liq', 0.0))
        p_cliff = float(params.get('peso_cliff', 1000.0))
        p_vpl = float(params.get('peso_vpl', 250.0))
    else:
        p_iof = float(params[0]) if len(params) > 0 else 100.0
        p_ir = float(params[1]) if len(params) > 1 else 0.0
        p_age = float(params[2]) if len(params) > 2 else 0.1
        p_liq = float(params[3]) if len(params) > 3 else 0.0
        p_cliff = float(params[4]) if len(params) > 4 else 1000.0
        p_vpl = float(params[5]) if len(params) > 5 else 250.0

    dias_restantes = (data_final - data_atual).days
    dias_rend_restantes = contar_dias_rendimento(data_atual, data_final, bcb_map) if dias_restantes > 0 else 0

    rows = []
    for i, l in enumerate(lotes_disponiveis):
        dias = (data_atual - l.data_aplicacao).days
        iof = _taxa_iof(dias) if dias >= 0 else 1.0
        ir = _taxa_ir(dias, isento=(l.produto.isento_ir if l.produto else False)) if dias >= 0 else 0.225
        dist_prox = 999
        if dias < 180:
            dist_prox = 180 - dias
        elif dias < 360:
            dist_prox = 360 - dias
        elif dias < 720:
            dist_prox = 720 - dias
        penalty_cliff = 1.0 if dist_prox <= 10 else 0.0

        flq = float(l.get_fator_liquido(data_atual))
        penalidade = 1.0 + iof * p_iof + ir * p_ir + dias * p_age + flq * p_liq + penalty_cliff * p_cliff

        oportunidade = 0.0
        mult = 1.0
        fator_cresc = 1.0
        fator_liq_fut = flq
        if dias_rend_restantes > 0 and p_vpl > 0.0:
            idade_fiscal = max(0, (data_atual - l.data_base_fiscal).days)
            if l.produto is not None:
                if idade_fiscal < int(getattr(l.produto, 'dias_bonus', 0) or 0):
                    mult = float(getattr(l.produto, 'taxa_bonus', getattr(l.produto, 'taxa_base', 1.0)) or 1.0)
                else:
                    mult = float(getattr(l.produto, 'taxa_base', 1.0) or 1.0)
            fator_cresc = (1.0 + taxa_proj) ** (mult * dias_rend_restantes)
            dias_tot_fut = (data_final - l.data_aplicacao).days
            ir_fut = _taxa_ir(dias_tot_fut, isento=(l.produto.isento_ir if l.produto else False))
            fat_acum_fut = l.fator_acumulado * fator_cresc
            ratio_luc_fut = max(0.0, 1.0 - (1.0 / fat_acum_fut)) if fat_acum_fut > 1.0 else 0.0
            fator_liq_fut = 1.0 - (ratio_luc_fut * ir_fut)
            oportunidade = (fator_cresc * fator_liq_fut) - flq
            if oportunidade > 0.0:
                penalidade += p_vpl * oportunidade

        escolhido_bruto = float(valores_otimos[i]) if valores_otimos is not None and i < len(valores_otimos) else 0.0
        escolhido_liquido = escolhido_bruto * flq

        rows.append({
            "Data": data_atual,
            "Lote ID": str(getattr(l, 'id', '')).strip(),
            "Investimento": str(getattr(l, 'investimento', '') or ''),
            "Saldo Bruto Antes": dinheiro_round(float(getattr(l, 'saldo_bruto', 0.0) or 0.0)),
            "Principal Remanescente Antes": dinheiro_round(float(getattr(l, 'principal_remanescente', 0.0) or 0.0)),
            "Data Aplicação": getattr(l, 'data_aplicacao', None),
            "Data Base Fiscal": getattr(l, 'data_base_fiscal', None),
            "Dias": dias,
            "IOF": float(iof),
            "IR": float(ir),
            "Distância Próx. Faixa": int(dist_prox),
            "Penalty Cliff": float(penalty_cliff),
            "Fator Líquido Hoje": float(flq),
            "Dias Rend Restantes": int(dias_rend_restantes),
            "Multiplicador Futuro": float(mult),
            "Fator Cresc Futuro": float(fator_cresc),
            "Fator Líquido Futuro": float(fator_liq_fut),
            "Oportunidade": float(oportunidade),
            "Penalidade Total": float(penalidade),
            "Bruto Escolhido Resolver": dinheiro_round(float(escolhido_bruto)),
            "Líquido Escolhido Resolver": dinheiro_round(float(escolhido_liquido)),
            "Escolhido?": "Sim" if float(escolhido_bruto) > float(globals().get('VALOR_MINIMO_RESGATE_BRUTO', 0.01) or 0.01) else "Não",
        })
    return rows

def resolver_pulp_penalidade_5p(lotes, alvo, hoje, params):
    if isinstance(params, dict):
        p_iof = params.get('peso_iof', 100.0)
        p_ir = params.get('peso_ir', 0.0)
        p_age = params.get('peso_idade', 0.1)
        p_liq = params.get('peso_liq', 0.0)
        p_cliff = params.get('peso_cliff', 1000.0)
    else:
        p_iof = params[0] if len(params) > 0 else 100.0
        p_ir = params[1] if len(params) > 1 else 0.0
        p_age = params[2] if len(params) > 2 else 0.1
        p_liq = params[3] if len(params) > 3 else 0.0
        p_cliff = params[4] if len(params) > 4 else 1000.0

    prob = pulp.LpProblem("Min_Penalidade_5P", pulp.LpMinimize)
    x_vars = [pulp.LpVariable(f"x{i}", 0, l.saldo_bruto) for i, l in enumerate(lotes)]
    fator_liq = [l.get_fator_liquido(hoje) for l in lotes]
    prob += pulp.lpSum([x_vars[i] * fator_liq[i] for i in range(len(lotes))]) >= alvo

    custos = []
    for i, l in enumerate(lotes):
        dias = (hoje - l.data_base_fiscal).days
        iof = IOF_TABLE[dias] if dias < 30 else 0.0
        ir = obter_aliquota_ir(dias)
        dist_prox = 999
        if dias < 180:
            dist_prox = 180 - dias
        elif dias < 360:
            dist_prox = 360 - dias
        elif dias < 720:
            dist_prox = 720 - dias
        penalty_cliff = 1.0 if dist_prox <= DIAS_CLIFF_IR else 0.0
        flq = fator_liq[i]

        penalidade = (1.0 + (iof * p_iof) + (ir * p_ir) + (dias * p_age) + (flq * p_liq) + (penalty_cliff * p_cliff))
        custos.append(x_vars[i] * penalidade)

    prob += pulp.lpSum(custos)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] == "Optimal":
        return [v.varValue for v in x_vars]
    return [0.0] * len(lotes)

def resolver_pulp_hibrido_5p(lotes, alvo, hoje, params_pen, data_final, bcb_map=None, taxa_proj=None):
    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE

    if isinstance(params_pen, dict):
        p_iof = float(params_pen.get('peso_iof', 100.0))
        p_ir = float(params_pen.get('peso_ir', 0.0))
        p_age = float(params_pen.get('peso_idade', 0.1))
        p_liq = float(params_pen.get('peso_liq', 0.0))
        p_cliff = float(params_pen.get('peso_cliff', 1000.0))
        p_vpl = float(params_pen.get('peso_vpl', 250.0))
    else:
        p_iof = float(params_pen[0]) if len(params_pen) > 0 else 100.0
        p_ir = float(params_pen[1]) if len(params_pen) > 1 else 0.0
        p_age = float(params_pen[2]) if len(params_pen) > 2 else 0.1
        p_liq = float(params_pen[3]) if len(params_pen) > 3 else 0.0
        p_cliff = float(params_pen[4]) if len(params_pen) > 4 else 1000.0
        p_vpl = float(params_pen[5]) if len(params_pen) > 5 else 250.0

    prob = pulp.LpProblem("Hibrido_5P", pulp.LpMinimize)
    x_vars = [pulp.LpVariable(f"x{i}", 0, l.saldo_bruto) for i, l in enumerate(lotes)]
    fator_liq_now = [l.get_fator_liquido(hoje) for l in lotes]
    prob += pulp.lpSum([x_vars[i] * fator_liq_now[i] for i in range(len(lotes))]) >= alvo

    dias_restantes = (data_final - hoje).days
    dias_rend_restantes = contar_dias_rendimento(hoje, data_final, bcb_map) if dias_restantes > 0 else 0

    custos = []
    for i, l in enumerate(lotes):
        dias = (hoje - l.data_base_fiscal).days
        iof = IOF_TABLE[dias] if dias < 30 else 0.0
        ir = obter_aliquota_ir(dias)
        dist_prox = 999
        if dias < 180:
            dist_prox = 180 - dias
        elif dias < 360:
            dist_prox = 360 - dias
        elif dias < 720:
            dist_prox = 720 - dias
        penalty_cliff = 1.0 if dist_prox <= DIAS_CLIFF_IR else 0.0
        flq = fator_liq_now[i]

        penalidade = 1.0
        penalidade += iof * p_iof
        penalidade += ir * p_ir
        penalidade += dias * p_age
        penalidade += flq * p_liq
        penalidade += penalty_cliff * p_cliff

        if dias_rend_restantes > 0 and p_vpl > 0.0:
            idade = max(0, (hoje - l.data_base_fiscal).days)
            if getattr(l, 'taxa_bonus_cdi', 0.0) > 0.0 and idade < getattr(l, 'dias_bonus', 0):
                mult = float(l.taxa_bonus_cdi)
            else:
                mult = float(getattr(l, 'taxa_base_cdi', 1.0))

            fator_cresc = (1.0 + taxa_proj) ** (mult * dias_rend_restantes)
            dias_tot_fut = (data_final - l.data_base_fiscal).days
            ir_fut = obter_aliquota_ir(dias_tot_fut)

            fat_acum_fut = l.fator_acumulado * fator_cresc
            ratio_luc_fut = max(0.0, 1.0 - (1.0 / fat_acum_fut)) if fat_acum_fut > 1.0 else 0.0
            fator_liq_fut = 1.0 - (ratio_luc_fut * ir_fut)
            oportunidade = (fator_cresc * fator_liq_fut) - flq

            if oportunidade > 0.0:
                penalidade += p_vpl * oportunidade

        custos.append(x_vars[i] * penalidade)

    prob += pulp.lpSum(custos)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] == "Optimal":
        return [v.varValue for v in x_vars]
    return [0.0] * len(lotes)

def resolver_hibrido_5p(lotes_disponiveis, alvo_liquido, data_atual, params, data_final, bcb_map=None, taxa_proj=None):
    n = len(lotes_disponiveis)
    if n == 0:
        return []

    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE

    if isinstance(params, dict):
        p_iof = float(params.get('peso_iof', 100.0))
        p_ir = float(params.get('peso_ir', 0.0))
        p_age = float(params.get('peso_idade', 0.1))
        p_liq = float(params.get('peso_liq', 0.0))
        p_cliff = float(params.get('peso_cliff', 1000.0))
        p_vpl = float(params.get('peso_vpl', 250.0))
    else:
        p_iof = float(params[0]) if len(params) > 0 else 100.0
        p_ir = float(params[1]) if len(params) > 1 else 0.0
        p_age = float(params[2]) if len(params) > 2 else 0.1
        p_liq = float(params[3]) if len(params) > 3 else 0.0
        p_cliff = float(params[4]) if len(params) > 4 else 1000.0
        p_vpl = float(params[5]) if len(params) > 5 else 250.0

    prob = pulp.LpProblem("Hibrido_5P", pulp.LpMinimize)
    x_vars = [pulp.LpVariable(f"x{i}", 0, l.saldo_bruto) for i, l in enumerate(lotes_disponiveis)]
    fator_liq_now = [l.get_fator_liquido(data_atual) for l in lotes_disponiveis]

    prob += pulp.lpSum([x_vars[i] * fator_liq_now[i] for i in range(n)]) >= alvo_liquido

    dias_restantes = (data_final - data_atual).days
    dias_rend_restantes = contar_dias_rendimento(data_atual, data_final, bcb_map) if dias_restantes > 0 else 0

    custos = []
    for i, l in enumerate(lotes_disponiveis):
        dias = (data_atual - l.data_aplicacao).days

        iof = _taxa_iof(dias) if dias >= 0 else 1.0
        ir = _taxa_ir(dias, isento=(l.produto.isento_ir if l.produto else False)) if dias >= 0 else 0.225

        dist_prox = 999
        if dias < 180:
            dist_prox = 180 - dias
        elif dias < 360:
            dist_prox = 360 - dias
        elif dias < 720:
            dist_prox = 720 - dias
        penalty_cliff = 1.0 if dist_prox <= 10 else 0.0

        flq = fator_liq_now[i]

        penalidade = 1.0
        penalidade += iof * p_iof
        penalidade += ir * p_ir
        penalidade += dias * p_age
        penalidade += flq * p_liq
        penalidade += penalty_cliff * p_cliff

        if dias_rend_restantes > 0 and p_vpl > 0.0:
            idade_fiscal = max(0, (data_atual - l.data_base_fiscal).days)
            if l.produto is not None:
                if idade_fiscal < int(getattr(l.produto, 'dias_bonus', 0) or 0):
                    mult = float(getattr(l.produto, 'taxa_bonus', getattr(l.produto, 'taxa_base', 1.0)) or 1.0)
                else:
                    mult = float(getattr(l.produto, 'taxa_base', 1.0) or 1.0)
            else:
                mult = 1.0

            fator_cresc = (1.0 + taxa_proj) ** (mult * dias_rend_restantes)

            dias_tot_fut = (data_final - l.data_aplicacao).days
            ir_fut = _taxa_ir(dias_tot_fut, isento=(l.produto.isento_ir if l.produto else False))
            fat_acum_fut = l.fator_acumulado * fator_cresc
            ratio_luc_fut = max(0.0, 1.0 - (1.0 / fat_acum_fut)) if fat_acum_fut > 1.0 else 0.0
            fator_liq_fut = 1.0 - (ratio_luc_fut * ir_fut)
            oportunidade = (fator_cresc * fator_liq_fut) - flq

            if oportunidade > 0.0:
                penalidade += p_vpl * oportunidade

        custos.append(x_vars[i] * penalidade)

    prob += pulp.lpSum(custos)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus.get(prob.status) == "Optimal":
        return [max(0.0, float(v.varValue or 0.0)) for v in x_vars]
    return [0.0] * n

def _iter_produtos(produtos):
    if produtos is None:
        return []
    if isinstance(produtos, dict):
        return list(produtos.values())
    if isinstance(produtos, (list, tuple, set)):
        return list(produtos)
    try:
        return list(produtos)
    except Exception:
        return []

def _produto_signature(prod):
    try:
        taxa_base = round(float(getattr(prod, 'taxa_base', 0.0) or 0.0), 8)
    except Exception:
        taxa_base = 0.0
    try:
        taxa_bonus = round(float(getattr(prod, 'taxa_bonus', taxa_base) or taxa_base), 8)
    except Exception:
        taxa_bonus = taxa_base
    try:
        dias_bonus = int(getattr(prod, 'dias_bonus', 0) or 0)
    except Exception:
        dias_bonus = 0
    return (taxa_base, taxa_bonus, dias_bonus)

def _indexar_produtos_por_signature(produtos):
    idx = {}
    for p in _iter_produtos(produtos):
        sig = _produto_signature(p)
        idx.setdefault(sig, []).append(p)
    return idx

def _ler_df_excel_seguro(caminho, sheet_name):
    try:
        return pd.read_excel(caminho, sheet_name=sheet_name)
    except Exception:
        return None

def _coletar_referencias_produtos_plano_externo(caminho_origem):
    refs = {'nomes': set(), 'signatures': set()}
    if not caminho_origem:
        return refs
    caminho = Path(caminho_origem)
    for sheet_name in ['Carteira Final', 'Situacao Atual', 'Situação Atual']:
        df = _ler_df_excel_seguro(caminho, sheet_name)
        if df is None or df.empty:
            continue
        cols_norm = {str(c).strip().lower(): c for c in df.columns}

        for chave in ['produto', 'produto atual', 'investimento', 'aplicacao', 'aplicação']:
            col = cols_norm.get(chave)
            if col is not None:
                for v in df[col].dropna().tolist():
                    nome = str(v).strip()
                    if nome:
                        refs['nomes'].add(nome)

        col_tb = None
        col_tbonus = None
        col_dbonus = None
        for k, c in cols_norm.items():
            if ('taxa base' in k and 'cdi' in k) or k == 'taxa_base_cdi':
                col_tb = c
            if ('taxa bônus' in k and 'cdi' in k) or ('taxa bonus' in k and 'cdi' in k) or k == 'taxa_bonus_cdi':
                col_tbonus = c
            if 'dias bônus' in k or 'dias bonus' in k or k == 'dias_bonus':
                col_dbonus = c
        if col_tb is not None:
            for _, row in df.iterrows():
                try:
                    tb = float(row[col_tb]) / 100.0
                except Exception:
                    continue
                try:
                    tbonus = float(row[col_tbonus]) / 100.0 if col_tbonus is not None and pd.notna(row[col_tbonus]) else tb
                except Exception:
                    tbonus = tb
                try:
                    dbonus = int(row[col_dbonus]) if col_dbonus is not None and pd.notna(row[col_dbonus]) else 0
                except Exception:
                    dbonus = 0
                refs['signatures'].add((round(tb, 8), round(tbonus, 8), dbonus))
    return refs

def _diagnosticar_compatibilidade_plano_externo(produtos, caminho_origem):
    refs = _coletar_referencias_produtos_plano_externo(caminho_origem)
    diag = {
        'ok': True,
        'nomes_inativos_plano': [],
        'nomes_sem_corresp': [],
        'sigs_inativas': [],
        'sigs_sem_corresp': [],
        'motivos': [],
    }
    if not refs['nomes'] and not refs['signatures']:
        _log_debug('>>> [PLANO-EXT] Não foi possível inferir produtos do plano externo para checagem de compatibilidade.', AUDITAR_PLANO_EXTERNO)
        diag['ok'] = False
        diag['motivos'].append('nao_foi_possivel_inferir_produtos_do_plano')
        return diag

    ativos = {str(getattr(p, 'nome', '')).strip() for p in _iter_produtos(produtos) if bool(getattr(p, 'ativo', True))}
    inativos = {str(getattr(p, 'nome', '')).strip() for p in _iter_produtos(produtos) if not bool(getattr(p, 'ativo', True))}
    idx_sig = _indexar_produtos_por_signature(produtos)

    nomes_inativos_plano = sorted(n for n in refs['nomes'] if n in inativos and n not in ativos)
    nomes_sem_corresp = sorted(n for n in refs['nomes'] if n not in ativos and n not in inativos)

    sigs_inativas = []
    sigs_sem_corresp = []
    for sig in sorted(refs['signatures']):
        matches = idx_sig.get(sig, [])
        if not matches:
            sigs_sem_corresp.append(sig)
            continue
        if all(not bool(getattr(p, 'ativo', True)) for p in matches):
            sigs_inativas.append((sig, [str(getattr(p, 'nome', '')).strip() for p in matches]))

    diag['nomes_inativos_plano'] = nomes_inativos_plano
    diag['nomes_sem_corresp'] = nomes_sem_corresp
    diag['sigs_inativas'] = sigs_inativas
    diag['sigs_sem_corresp'] = sigs_sem_corresp

    if nomes_inativos_plano:
        _log_debug(f">>> [PLANO-EXT] Produtos do plano externo hoje inativos: {', '.join(nomes_inativos_plano)}", AUDITAR_PLANO_EXTERNO)
    if nomes_sem_corresp:
        _log_debug(f">>> [PLANO-EXT] Produtos do plano externo sem correspondência nominal na carteira atual: {', '.join(nomes_sem_corresp[:8])}" + (' ...' if len(nomes_sem_corresp) > 8 else ''), AUDITAR_PLANO_EXTERNO)
    if sigs_inativas:
        amostra = []
        for sig, nomes in sigs_inativas[:6]:
            amostra.append(f"{'/'.join(sorted(set(nomes)))} [{sig[0]*100:.0f}%/{sig[1]*100:.0f}%/{sig[2]}d]")
        _log_debug(f">>> [PLANO-EXT] Assinaturas do plano externo mapeadas apenas para produtos hoje inativos: {', '.join(amostra)}", AUDITAR_PLANO_EXTERNO)
    if sigs_sem_corresp:
        amostra = [f"[{s[0]*100:.0f}%/{s[1]*100:.0f}%/{s[2]}d]" for s in sigs_sem_corresp[:6]]
        _log_debug(f">>> [PLANO-EXT] Assinaturas do plano externo sem correspondência na carteira atual: {', '.join(amostra)}", AUDITAR_PLANO_EXTERNO)

    if not nomes_inativos_plano and not nomes_sem_corresp and not sigs_inativas and not sigs_sem_corresp:
        _log_debug('>>> [PLANO-EXT] Plano externo compatível com a carteira atual.', AUDITAR_PLANO_EXTERNO)
        return diag

    diag['ok'] = False
    if nomes_inativos_plano or sigs_inativas:
        diag['motivos'].append('plano_usa_produtos_inativos')
    if nomes_sem_corresp or sigs_sem_corresp:
        diag['motivos'].append('plano_sem_correspondencia_na_carteira')
    return diag

def _classificar_investimento_inventario(valor) -> dict:
    if pd.isna(valor):
        return {"produto_nome": "", "situacao": "sem_produto", "ja_aplicado": False}
    s = str(valor).strip()
    if s in {"-", "—", "–"}:
        return {"produto_nome": "", "situacao": "usado_sem_carteira", "ja_aplicado": True}
    if s.lower() in {"", "none", "nan"}:
        return {"produto_nome": "", "situacao": "sem_produto", "ja_aplicado": False}
    return {"produto_nome": s, "situacao": "alocado", "ja_aplicado": True}

def _resolver_produto_por_nome(produtos_dict, produto_nome: str):
    if not produto_nome:
        return None
    if produto_nome in produtos_dict:
        return produtos_dict.get(produto_nome)
    nome_norm = _normalizar_nome_texto(produto_nome)
    for nome, produto in produtos_dict.items():
        if _normalizar_nome_texto(nome) == nome_norm:
            return produto
    return None

def _resolver_produto_lote_shadow(valor_produto, mapa_produtos, *, normalizar_nome_fn=None):
    """Resolve o produto do lote contra o mapa canônico ativo."""
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    vazio = {
        'produto_key': None,
        'produto_nome': None,
        'produto_nome_norm': None,
        'produto_encontrado': False,
        'tipo_match_produto': 'vazio',
    }

    if valor_produto is None:
        return vazio

    s = str(valor_produto).strip()
    if s == '' or s.lower() == 'nan' or s == '-':
        return vazio

    by_key = mapa_produtos.get('by_key', {}) if isinstance(mapa_produtos, dict) else {}
    by_nome_norm = mapa_produtos.get('by_nome_norm', {}) if isinstance(mapa_produtos, dict) else {}

    if s in by_key:
        info = by_key[s]
        return {
            'produto_key': info.get('produto_key'),
            'produto_nome': info.get('nome'),
            'produto_nome_norm': info.get('nome_norm'),
            'produto_encontrado': True,
            'tipo_match_produto': 'chave_exata',
        }

    nome_norm = normalizar_nome_fn(s)
    if nome_norm in by_nome_norm:
        produto_key = by_nome_norm[nome_norm]
        info = by_key.get(produto_key, {})
        return {
            'produto_key': info.get('produto_key'),
            'produto_nome': info.get('nome'),
            'produto_nome_norm': info.get('nome_norm'),
            'produto_encontrado': True,
            'tipo_match_produto': 'nome_norm',
        }

    return {
        'produto_key': None,
        'produto_nome': s,
        'produto_nome_norm': nome_norm,
        'produto_encontrado': False,
        'tipo_match_produto': 'nao_encontrado',
    }

def normalizar_lotes_brutos(
    df_lotes,
    mapa_produtos,
    *,
    config: dict,
    contrato: dict,
    normalizar_nome_fn=None,
):
    """Constrói df_lotes_norm em modo sombra, sem substituir o fluxo legado."""
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    auditoria = {
        'coluna_id_lote': None,
        'coluna_produto_lote': None,
        'qtd_lotes_norm': 0,
        'qtd_produto_reconhecido': 0,
        'qtd_caixa': 0,
        'qtd_produto_nao_reconhecido': 0,
        'qtd_data_base_fiscal_inferida': 0,
        'qtd_ids_duplicados': 0,
        'linhas_descartadas': [],
    }

    col_id = selecionar_coluna_id_lote(df_lotes)
    col_produto = selecionar_coluna_produto_lote(df_lotes, INVESTIMENTOS_NORM, contexto='shadow lotes', auditar=False)
    auditoria['coluna_id_lote'] = col_id
    auditoria['coluna_produto_lote'] = col_produto

    col_data_aplic = resolver_coluna(df_lotes, 'lotes', 'data_aplicacao')
    col_valor_orig = resolver_coluna(df_lotes, 'lotes', 'valor_original')

    try:
        col_data_base_fiscal = resolver_coluna(df_lotes, 'lotes', 'data_base_fiscal', required=False)
    except Exception:
        col_data_base_fiscal = None

    try:
        col_status_lote = resolver_coluna(df_lotes, 'lotes', 'status_lote', required=False)
    except Exception:
        col_status_lote = None

    registros = []
    for i, (_, row) in enumerate(df_lotes.iterrows(), start=1):
        lote_id_raw = row[col_id] if col_id in df_lotes.columns else None
        lote_id = _normalizar_lote_id(lote_id_raw)
        data_aplicacao = _normalizar_data_lote(row[col_data_aplic] if col_data_aplic in df_lotes.columns else None)
        valor_original = _normalizar_valor_lote(row[col_valor_orig] if col_valor_orig in df_lotes.columns else None, default=None)

        if lote_id is None:
            auditoria['linhas_descartadas'].append({'ordem': i, 'motivo': 'lote_id_invalido'})
            continue
        if data_aplicacao is None:
            auditoria['linhas_descartadas'].append({'ordem': i, 'motivo': 'data_aplicacao_invalida', 'lote_id': lote_id})
            continue
        if valor_original is None or valor_original <= 0:
            auditoria['linhas_descartadas'].append({'ordem': i, 'motivo': 'valor_original_invalido', 'lote_id': lote_id})
            continue

        valor_produto_bruto = row[col_produto] if (col_produto and col_produto in df_lotes.columns) else None
        produto_info = _resolver_produto_lote_shadow(valor_produto_bruto, mapa_produtos, normalizar_nome_fn=normalizar_nome_fn)

        data_base_fiscal = None
        if col_data_base_fiscal and col_data_base_fiscal in df_lotes.columns:
            data_base_fiscal = _normalizar_data_lote(row[col_data_base_fiscal])
        if data_base_fiscal is None:
            data_base_fiscal = data_aplicacao
            auditoria['qtd_data_base_fiscal_inferida'] += 1

        status_lote = 'ativo_observado'
        if col_status_lote and col_status_lote in df_lotes.columns:
            raw_status = row[col_status_lote]
            if raw_status is not None and str(raw_status).strip() != '':
                status_lote = str(raw_status).strip()

        if produto_info['tipo_match_produto'] == 'vazio':
            tipo_lote = 'caixa'
            auditoria['qtd_caixa'] += 1
        elif produto_info['produto_encontrado']:
            tipo_lote = 'produto_observado'
            auditoria['qtd_produto_reconhecido'] += 1
        else:
            tipo_lote = 'produto_nao_reconhecido'
            auditoria['qtd_produto_nao_reconhecido'] += 1

        registros.append({
            'lote_id': lote_id,
            'lote_id_raw': None if lote_id_raw is None else str(lote_id_raw),
            'data_aplicacao': data_aplicacao,
            'data_base_fiscal': data_base_fiscal,
            'valor_original': float(valor_original),
            'principal_remanescente_inicial': float(valor_original),
            'saldo_bruto_inicial': float(valor_original),
            'saldo_liquido_inicial': float(valor_original),
            'produto_valor_bruto': None if valor_produto_bruto is None else str(valor_produto_bruto),
            'produto_key': produto_info['produto_key'],
            'produto_nome': produto_info['produto_nome'],
            'produto_nome_norm': produto_info['produto_nome_norm'],
            'produto_encontrado': bool(produto_info['produto_encontrado']),
            'tipo_match_produto': produto_info['tipo_match_produto'],
            'tipo_lote': tipo_lote,
            'status_lote': status_lote,
            'origem_registro': 'inventario_lotes',
            'eh_lote_observado': True,
            'eh_aporte_historico': True,
            'ordem_planilha_lote': i,
        })

    df_lotes_norm = pd.DataFrame(registros)
    auditoria['qtd_lotes_norm'] = len(df_lotes_norm)
    if len(df_lotes_norm) > 0:
        try:
            auditoria['qtd_ids_duplicados'] = int(df_lotes_norm['lote_id'].duplicated().sum())
        except Exception:
            auditoria['qtd_ids_duplicados'] = None
    return df_lotes_norm, auditoria

def construir_indice_lotes(df_lotes_norm):
    indice = {}
    if df_lotes_norm is None or len(df_lotes_norm) == 0:
        return indice
    for _, row in df_lotes_norm.iterrows():
        indice[row['lote_id']] = row.to_dict()
    return indice

def derivar_eventos_aporte_de_lotes(df_lotes_norm):
    registros = []
    if df_lotes_norm is None or len(df_lotes_norm) == 0:
        return pd.DataFrame(registros)
    for _, row in df_lotes_norm.iterrows():
        lote_id = row['lote_id']
        registros.append({
            'evento_id': f'aporte::{lote_id}',
            'tipo_evento': 'aporte_historico',
            'data_evento': row['data_aplicacao'],
            'lote_id': lote_id,
            'produto_key': row['produto_key'],
            'produto_nome': row['produto_nome'],
            'valor': _safe_float(row['valor_original'], 0.0),
            'origem_evento': 'inventario_lotes',
            'ordem_planilha_lote': row['ordem_planilha_lote'],
        })
    return pd.DataFrame(registros)

def comparar_aportes_legado_vs_shadow(aportes_legado, df_eventos_aporte_shadow):
    legado = []
    for ap in (aportes_legado or []):
        try:
            data_ap = _normalizar_data_lote(ap[0])
            valor_ap = _safe_float(ap[1], 0.0)
            lote_id = _normalizar_lote_id(ap[2] if len(ap) > 2 else None)
            legado.append({'lote_id': lote_id, 'data_evento': data_ap, 'valor': valor_ap})
        except Exception:
            continue

    shadow = []
    if df_eventos_aporte_shadow is not None and len(df_eventos_aporte_shadow) > 0:
        for _, row in df_eventos_aporte_shadow.iterrows():
            shadow.append({
                'lote_id': _normalizar_lote_id(row.get('lote_id')),
                'data_evento': _normalizar_data_lote(row.get('data_evento')),
                'valor': _safe_float(row.get('valor'), 0.0),
            })

    ids_legado = {x['lote_id'] for x in legado if x['lote_id'] is not None}
    ids_shadow = {x['lote_id'] for x in shadow if x['lote_id'] is not None}

    datas_diferentes = []
    valores_diferentes = []
    map_legado = {x['lote_id']: x for x in legado if x['lote_id'] is not None}
    map_shadow = {x['lote_id']: x for x in shadow if x['lote_id'] is not None}

    for lote_id in sorted(ids_legado & ids_shadow):
        a = map_legado[lote_id]
        b = map_shadow[lote_id]
        if a['data_evento'] != b['data_evento']:
            datas_diferentes.append((lote_id, a['data_evento'], b['data_evento']))
        if abs(_safe_float(a['valor'], 0.0) - _safe_float(b['valor'], 0.0)) > 1e-9:
            valores_diferentes.append((lote_id, a['valor'], b['valor']))

    soma_legado = sum(_safe_float(x['valor'], 0.0) for x in legado)
    soma_shadow = sum(_safe_float(x['valor'], 0.0) for x in shadow)

    equivalentes_essenciais = (
        len(legado) == len(shadow)
        and len(ids_legado - ids_shadow) == 0
        and len(ids_shadow - ids_legado) == 0
        and len(datas_diferentes) == 0
        and len(valores_diferentes) == 0
        and abs(soma_legado - soma_shadow) <= 1e-9
    )

    return {
        'qtd_legado': len(legado),
        'qtd_shadow': len(shadow),
        'soma_legado': soma_legado,
        'soma_shadow': soma_shadow,
        'ids_somente_legado': sorted(list(ids_legado - ids_shadow)),
        'ids_somente_shadow': sorted(list(ids_shadow - ids_legado)),
        'datas_diferentes': datas_diferentes,
        'valores_diferentes': valores_diferentes,
        'equivalentes_essenciais': equivalentes_essenciais,
    }

# ============================================================

def gerar_lote_tecnico_id(lote_id, ordem_planilha_lote, *, prefixo="obs"):
    """
    Gera chave técnica estável para lote, preservando distinção entre
    lote_id legado e ocorrência na planilha.
    """
    lote_id_norm = _normalizar_lote_id(lote_id)
    ordem = ordem_planilha_lote if ordem_planilha_lote is not None else "sem_ordem"
    if lote_id_norm is None:
        lote_id_norm = "sem_lote_id"
    return f"{prefixo}::{lote_id_norm}::{ordem}"

def gerar_switch_grupo_id(lote_tecnico_id, produto_destino_key, data_evento, ordem_switch=1):
    """
    Gera ID único para agrupar switch_out e switch_in do mesmo switching.
    """
    d = _normalizar_data_lote(data_evento)
    d_txt = str(d) if d is not None else "sem_data"
    destino = produto_destino_key if produto_destino_key is not None else "sem_destino"
    origem = lote_tecnico_id if lote_tecnico_id is not None else "sem_origem"
    return f"swgrp::{origem}::{destino}::{d_txt}::{ordem_switch}"

def projetar_eventos_brutos_de_aportes(df_eventos_aporte_shadow, df_lotes_norm):
    """
    Converte eventos de aporte históricos derivados dos lotes em eventos
    financeiros brutos canônicos do tipo 'aporte_historico'.
    """
    registros = []
    if df_eventos_aporte_shadow is None or len(df_eventos_aporte_shadow) == 0:
        return pd.DataFrame(registros)

    mapa_lotes = {}
    if df_lotes_norm is not None and len(df_lotes_norm) > 0:
        for _, row in df_lotes_norm.iterrows():
            lote_id = row.get("lote_id")
            ordem = row.get("ordem_planilha_lote")
            mapa_lotes[(lote_id, ordem)] = row.to_dict()

    for _, row in df_eventos_aporte_shadow.iterrows():
        lote_id = _normalizar_lote_id(row.get("lote_id"))
        ordem = row.get("ordem_planilha_lote")
        lote_info = mapa_lotes.get((lote_id, ordem), {})
        data_evento = _normalizar_data_lote(row.get("data_evento"))
        valor = _safe_float(row.get("valor"), 0.0)
        produto_key = lote_info.get("produto_key")
        produto_nome = lote_info.get("produto_nome")
        data_base_fiscal = _normalizar_data_lote(lote_info.get("data_base_fiscal", data_evento))
        lote_tecnico_id = gerar_lote_tecnico_id(lote_id, ordem, prefixo="obs")

        registros.append({
            "evento_id": row.get("evento_id", f"aporte::{lote_id}"),
            "evento_tipo": "aporte_historico",
            "data_evento": data_evento,
            "lote_origem_id": lote_id,
            "lote_tecnico_id": lote_tecnico_id,
            "produto_origem_key": None,
            "produto_destino_key": produto_key,
            "produto_destino_nome": produto_nome,
            "valor_bruto": valor,
            "valor_transferido": valor,
            "data_base_fiscal": data_base_fiscal,
            "ordem_evento": int(ordem) if ordem is not None else 0,
            "evento_grupo_id": f"grp::{lote_tecnico_id}::aporte",
            "origem_evento": "inventario_lotes",
            "observacao_evento": "aporte_historico_derivado_do_inventario",
        })

    return pd.DataFrame(registros)

def construir_regra_switch_shadow(
    *,
    lote_tecnico_id_origem,
    produto_destino_key,
    data_switch,
    valor_switch,
    manter_data_base_destino=False,
    observacao=None,
):
    """
    Constrói uma regra manual/sombra de switching.
    """
    return {
        "lote_tecnico_id_origem": lote_tecnico_id_origem,
        "produto_destino_key": produto_destino_key,
        "data_switch": _normalizar_data_lote(data_switch),
        "valor_switch": _safe_float(valor_switch, 0.0),
        "manter_data_base_destino": bool(manter_data_base_destino),
        "observacao": observacao,
    }

def derivar_eventos_switch_shadow(
    df_lotes_norm,
    regras_switch,
    *,
    normalizar_nome_fn=None,
):
    """
    Para cada regra válida, gera um par de eventos:
    - switch_out
    - switch_in
    """
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    registros = []
    auditoria = {
        "qtd_regras_switch": 0,
        "qtd_switch_out": 0,
        "qtd_switch_in": 0,
        "qtd_lotes_origem_nao_encontrados": 0,
        "qtd_produtos_destino_invalidos": 0,
        "qtd_switch_valor_excede_origem": 0,
        "qtd_eventos_totais": 0,
        "regras_invalidas": [],
    }

    regras_switch = regras_switch or []
    auditoria["qtd_regras_switch"] = len(regras_switch)

    if df_lotes_norm is None or len(df_lotes_norm) == 0:
        auditoria["regras_invalidas"].append("df_lotes_norm_vazio")
        return pd.DataFrame(registros), auditoria

    mapa_lotes_tecnicos = {}
    for _, row in df_lotes_norm.iterrows():
        lote_tecnico_id = gerar_lote_tecnico_id(
            row.get("lote_id"),
            row.get("ordem_planilha_lote"),
            prefixo="obs",
        )
        mapa_lotes_tecnicos[lote_tecnico_id] = row.to_dict()

    mapa_produtos = MAPA_PRODUTOS_CANONICO if isinstance(MAPA_PRODUTOS_CANONICO, dict) else {"by_key": {}, "by_nome_norm": {}}
    by_key = mapa_produtos.get("by_key", {})

    for i, regra in enumerate(regras_switch, start=1):
        lote_tecnico_id_origem = regra.get("lote_tecnico_id_origem")
        produto_destino_key = regra.get("produto_destino_key")
        data_switch = _normalizar_data_lote(regra.get("data_switch"))
        valor_switch = _safe_float(regra.get("valor_switch"), 0.0)
        manter_data_base_destino = bool(regra.get("manter_data_base_destino", False))
        observacao = regra.get("observacao")

        lote_origem = mapa_lotes_tecnicos.get(lote_tecnico_id_origem)
        if lote_origem is None:
            auditoria["qtd_lotes_origem_nao_encontrados"] += 1
            auditoria["regras_invalidas"].append(
                {"ordem_switch": i, "motivo": "lote_origem_nao_encontrado", "lote_tecnico_id_origem": lote_tecnico_id_origem}
            )
            continue

        if produto_destino_key not in by_key:
            auditoria["qtd_produtos_destino_invalidos"] += 1
            auditoria["regras_invalidas"].append(
                {"ordem_switch": i, "motivo": "produto_destino_invalido", "produto_destino_key": produto_destino_key}
            )
            continue

        valor_origem_max = _safe_float(lote_origem.get("valor_original"), 0.0)
        if valor_switch <= 0:
            auditoria["regras_invalidas"].append(
                {"ordem_switch": i, "motivo": "valor_switch_invalido", "valor_switch": valor_switch}
            )
            continue

        if valor_switch - valor_origem_max > 1e-9:
            auditoria["qtd_switch_valor_excede_origem"] += 1
            auditoria["regras_invalidas"].append(
                {
                    "ordem_switch": i,
                    "motivo": "valor_switch_excede_origem",
                    "valor_switch": valor_switch,
                    "valor_origem_max": valor_origem_max,
                }
            )
            continue

        data_aplicacao_origem = _normalizar_data_lote(lote_origem.get("data_aplicacao"))
        if data_switch is None or (data_aplicacao_origem is not None and data_switch < data_aplicacao_origem):
            auditoria["regras_invalidas"].append(
                {"ordem_switch": i, "motivo": "data_switch_invalida", "data_switch": data_switch}
            )
            continue

        produto_origem_key = lote_origem.get("produto_key")
        produto_destino = by_key.get(produto_destino_key, {})
        lote_origem_id = lote_origem.get("lote_id")
        ordem_planilha_lote = lote_origem.get("ordem_planilha_lote")
        evento_grupo_id = gerar_switch_grupo_id(
            lote_tecnico_id_origem,
            produto_destino_key,
            data_switch,
            ordem_switch=i,
        )

        data_base_fiscal_origem = _normalizar_data_lote(lote_origem.get("data_base_fiscal"))
        data_base_fiscal_destino = data_base_fiscal_origem if manter_data_base_destino else data_switch
        lote_tecnico_id_destino = f"sw::{evento_grupo_id}::in"

        registros.append({
            "evento_id": f"{evento_grupo_id}::out",
            "evento_tipo": "switch_out",
            "data_evento": data_switch,
            "lote_origem_id": lote_origem_id,
            "lote_tecnico_id": lote_tecnico_id_origem,
            "produto_origem_key": produto_origem_key,
            "produto_destino_key": produto_destino_key,
            "produto_destino_nome": produto_destino.get("nome"),
            "valor_bruto": valor_switch,
            "valor_transferido": valor_switch,
            "data_base_fiscal": data_base_fiscal_origem,
            "ordem_evento": int(ordem_planilha_lote) if ordem_planilha_lote is not None else 0,
            "evento_grupo_id": evento_grupo_id,
            "origem_evento": "switch_shadow",
            "observacao_evento": observacao or "switch_out_shadow",
        })

        registros.append({
            "evento_id": f"{evento_grupo_id}::in",
            "evento_tipo": "switch_in",
            "data_evento": data_switch,
            "lote_origem_id": lote_origem_id,
            "lote_tecnico_id": lote_tecnico_id_destino,
            "produto_origem_key": produto_origem_key,
            "produto_destino_key": produto_destino_key,
            "produto_destino_nome": produto_destino.get("nome"),
            "valor_bruto": valor_switch,
            "valor_transferido": valor_switch,
            "data_base_fiscal": data_base_fiscal_destino,
            "ordem_evento": int(ordem_planilha_lote) if ordem_planilha_lote is not None else 0,
            "evento_grupo_id": evento_grupo_id,
            "origem_evento": "switch_shadow",
            "observacao_evento": observacao or "switch_in_shadow",
        })

        auditoria["qtd_switch_out"] += 1
        auditoria["qtd_switch_in"] += 1

    auditoria["qtd_eventos_totais"] = len(registros)
    return pd.DataFrame(registros), auditoria

def consolidar_eventos_financeiros_brutos(
    df_eventos_aporte_bruto,
    df_eventos_switch_shadow=None,
):
    """
    Consolida trilha bruta de eventos financeiros.
    """
    frames = []
    if df_eventos_aporte_bruto is not None and len(df_eventos_aporte_bruto) > 0:
        frames.append(df_eventos_aporte_bruto.copy())
    if df_eventos_switch_shadow is not None and len(df_eventos_switch_shadow) > 0:
        frames.append(df_eventos_switch_shadow.copy())
    if not frames:
        return pd.DataFrame([])

    df = pd.concat(frames, ignore_index=True, sort=False)

    if "data_evento" in df.columns:
        try:
            df["__data_ord__"] = pd.to_datetime(df["data_evento"], errors="coerce")
        except Exception:
            df["__data_ord__"] = None
    else:
        df["__data_ord__"] = None

    if "ordem_evento" not in df.columns:
        df["ordem_evento"] = 0

    tipo_ordem = {"aporte_historico": 1, "switch_out": 2, "switch_in": 3}
    df["__tipo_ord__"] = df["evento_tipo"].map(tipo_ordem).fillna(99)

    df = df.sort_values(
        by=["__data_ord__", "ordem_evento", "__tipo_ord__", "evento_id"],
        ascending=[True, True, True, True],
        kind="stable",
    ).reset_index(drop=True)

    return df.drop(columns=["__data_ord__", "__tipo_ord__"], errors="ignore")

def ordenar_eventos_financeiros_brutos_shadow(df_eventos_financeiros_brutos):
    """
    Ordena eventos brutos de forma determinística para o replay sombra.
    """
    if df_eventos_financeiros_brutos is None or len(df_eventos_financeiros_brutos) == 0:
        return pd.DataFrame([])

    df = df_eventos_financeiros_brutos.copy()
    prioridade_tipo = {"aporte_historico": 1, "switch_out": 2, "switch_in": 3}

    if "data_evento" in df.columns:
        df["__data_ord__"] = pd.to_datetime(df["data_evento"], errors="coerce")
    else:
        df["__data_ord__"] = pd.NaT

    if "ordem_evento" not in df.columns:
        df["ordem_evento"] = 0

    df["__tipo_ord__"] = df["evento_tipo"].map(prioridade_tipo).fillna(99)

    if "evento_id" not in df.columns:
        df["evento_id"] = [f"evento::{i}" for i in range(len(df))]

    df = df.sort_values(
        by=["__data_ord__", "ordem_evento", "__tipo_ord__", "evento_id"],
        ascending=[True, True, True, True],
        kind="stable",
    ).reset_index(drop=True)

    return df.drop(columns=["__data_ord__", "__tipo_ord__"], errors="ignore")

def projetar_estado_lotes_pre_replay_shadow(df_eventos_ordenados):
    """
    Aplica os eventos brutos em modo sombra e projeta o estado técnico
    dos lotes antes do replay principal.
    """
    estado = {}
    inconsistencias = []

    auditoria = {
        "qtd_eventos_aporte": 0,
        "qtd_eventos_switch_out": 0,
        "qtd_eventos_switch_in": 0,
        "qtd_lotes_ativos": 0,
        "qtd_lotes_encerrados_por_switch": 0,
        "qtd_lotes_tecnicos_novos": 0,
        "soma_saldos_pre": 0.0,
        "soma_saldos_pos": 0.0,
        "delta_conservacao": 0.0,
        "qtd_inconsistencias": 0,
        "inconsistencias": [],
    }

    if df_eventos_ordenados is None or len(df_eventos_ordenados) == 0:
        return pd.DataFrame([]), auditoria

    soma_pre = 0.0
    for _, ev in df_eventos_ordenados.iterrows():
        if ev.get("evento_tipo") in ("aporte_historico", "switch_in"):
            soma_pre += _safe_float(ev.get("valor_transferido"), 0.0)
        if ev.get("evento_tipo") == "switch_out":
            soma_pre -= _safe_float(ev.get("valor_transferido"), 0.0)
    auditoria["soma_saldos_pre"] = soma_pre

    for _, ev in df_eventos_ordenados.iterrows():
        evento_tipo = ev.get("evento_tipo")
        evento_id = ev.get("evento_id")
        lote_tecnico_id = ev.get("lote_tecnico_id")
        lote_origem_id = ev.get("lote_origem_id")
        produto_origem_key = ev.get("produto_origem_key")
        produto_destino_key = ev.get("produto_destino_key")
        valor = _safe_float(ev.get("valor_transferido"), 0.0)
        data_evento = _normalizar_data_lote(ev.get("data_evento"))
        data_base_fiscal = _normalizar_data_lote(ev.get("data_base_fiscal"))
        evento_grupo_id = ev.get("evento_grupo_id")
        origem_evento = ev.get("origem_evento")
        observacao_evento = ev.get("observacao_evento")

        if evento_tipo == "aporte_historico":
            auditoria["qtd_eventos_aporte"] += 1
            if lote_tecnico_id in estado:
                inconsistencias.append({"evento_id": evento_id, "motivo": "aporte_historico_lote_tecnico_duplicado", "lote_tecnico_id": lote_tecnico_id})
                continue
            estado[lote_tecnico_id] = {
                "lote_tecnico_id": lote_tecnico_id,
                "lote_origem_id": lote_origem_id,
                "produto_key": produto_destino_key,
                "saldo_inicial": valor,
                "saldo_atual": valor,
                "data_aplicacao": data_evento,
                "data_base_fiscal": data_base_fiscal,
                "status": "ativo",
                "origem": "aporte_historico",
                "evento_grupo_id_origem": evento_grupo_id,
                "historico_eventos": [evento_id],
            }
            continue

        if evento_tipo == "switch_out":
            auditoria["qtd_eventos_switch_out"] += 1
            lote_origem = estado.get(lote_tecnico_id)
            if lote_origem is None:
                inconsistencias.append({"evento_id": evento_id, "motivo": "switch_out_sem_lote_origem", "lote_tecnico_id": lote_tecnico_id})
                continue
            saldo_antes = _safe_float(lote_origem.get("saldo_atual"), 0.0)
            if valor <= 0:
                inconsistencias.append({"evento_id": evento_id, "motivo": "switch_out_valor_invalido", "valor": valor})
                continue
            if saldo_antes + 1e-9 < valor:
                inconsistencias.append({"evento_id": evento_id, "motivo": "switch_out_excede_saldo", "saldo_antes": saldo_antes, "valor": valor})
                continue
            saldo_depois = saldo_antes - valor
            lote_origem["saldo_atual"] = max(saldo_depois, 0.0)
            lote_origem["historico_eventos"].append(evento_id)
            if lote_origem["saldo_atual"] <= 1e-9:
                lote_origem["saldo_atual"] = 0.0
                lote_origem["status"] = "encerrado_por_switch"
            continue

        if evento_tipo == "switch_in":
            auditoria["qtd_eventos_switch_in"] += 1
            if lote_tecnico_id in estado:
                inconsistencias.append({"evento_id": evento_id, "motivo": "switch_in_lote_tecnico_duplicado", "lote_tecnico_id": lote_tecnico_id})
                continue
            if valor <= 0:
                inconsistencias.append({"evento_id": evento_id, "motivo": "switch_in_valor_invalido", "valor": valor})
                continue
            estado[lote_tecnico_id] = {
                "lote_tecnico_id": lote_tecnico_id,
                "lote_origem_id": lote_origem_id,
                "produto_key": produto_destino_key,
                "saldo_inicial": valor,
                "saldo_atual": valor,
                "data_aplicacao": data_evento,
                "data_base_fiscal": data_base_fiscal,
                "status": "ativo",
                "origem": "switch_in",
                "evento_grupo_id_origem": evento_grupo_id,
                "historico_eventos": [evento_id],
                "produto_origem_key": produto_origem_key,
                "origem_evento": origem_evento,
                "observacao_evento": observacao_evento,
            }
            continue

        inconsistencias.append({"evento_id": evento_id, "motivo": "evento_tipo_desconhecido", "evento_tipo": evento_tipo})

    registros_estado = []
    qtd_ativos = 0
    qtd_encerrados_por_switch = 0
    qtd_lotes_tecnicos_novos = 0
    soma_pos = 0.0
    for lote_tecnico_id, info in estado.items():
        saldo_atual = _safe_float(info.get("saldo_atual"), 0.0)
        soma_pos += saldo_atual
        status = info.get("status")
        origem = info.get("origem")
        if status == "ativo":
            qtd_ativos += 1
        if status == "encerrado_por_switch":
            qtd_encerrados_por_switch += 1
        if origem == "switch_in":
            qtd_lotes_tecnicos_novos += 1
        registros_estado.append({
            "lote_tecnico_id": lote_tecnico_id,
            "lote_origem_id": info.get("lote_origem_id"),
            "produto_key": info.get("produto_key"),
            "saldo_inicial": _safe_float(info.get("saldo_inicial"), 0.0),
            "saldo_atual": saldo_atual,
            "data_aplicacao": info.get("data_aplicacao"),
            "data_base_fiscal": info.get("data_base_fiscal"),
            "status": status,
            "origem": origem,
            "evento_grupo_id_origem": info.get("evento_grupo_id_origem"),
            "qtd_eventos_historico": len(info.get("historico_eventos", [])),
        })

    auditoria["qtd_lotes_ativos"] = qtd_ativos
    auditoria["qtd_lotes_encerrados_por_switch"] = qtd_encerrados_por_switch
    auditoria["qtd_lotes_tecnicos_novos"] = qtd_lotes_tecnicos_novos
    auditoria["soma_saldos_pos"] = soma_pos
    auditoria["delta_conservacao"] = soma_pos - auditoria["soma_saldos_pre"]
    auditoria["qtd_inconsistencias"] = len(inconsistencias)
    auditoria["inconsistencias"] = inconsistencias

    return pd.DataFrame(registros_estado), auditoria

def ordenar_lotes_para_replay_shadow(df_estado_lotes_pre_replay):
    """
    Ordena lotes técnicos elegíveis para o replay sombra simplificado.

    Ordem:
    1. data_base_fiscal
    2. data_aplicacao
    3. prioridade da origem (aporte_historico antes de switch_in)
    4. lote_tecnico_id
    """
    if df_estado_lotes_pre_replay is None or len(df_estado_lotes_pre_replay) == 0:
        return pd.DataFrame([])

    df = df_estado_lotes_pre_replay.copy()
    df = df[df.get('status').eq('ativo') & (pd.to_numeric(df.get('saldo_atual'), errors='coerce').fillna(0.0) > 0)].copy()

    if len(df) == 0:
        df['ordem_replay_shadow'] = []
        return df

    prioridade_origem = {'aporte_historico': 1, 'switch_in': 2}
    df['__data_base_ord__'] = pd.to_datetime(df.get('data_base_fiscal'), errors='coerce')
    df['__data_aplic_ord__'] = pd.to_datetime(df.get('data_aplicacao'), errors='coerce')
    df['__origem_ord__'] = df.get('origem').map(prioridade_origem).fillna(99)

    if 'lote_tecnico_id' not in df.columns:
        df['lote_tecnico_id'] = [f'lote_tecnico::{i}' for i in range(len(df))]

    df = df.sort_values(
        by=['__data_base_ord__', '__data_aplic_ord__', '__origem_ord__', 'lote_tecnico_id'],
        ascending=[True, True, True, True],
        kind='stable',
    ).reset_index(drop=True)

    df['ordem_replay_shadow'] = np.arange(1, len(df) + 1)
    return df.drop(columns=['__data_base_ord__', '__data_aplic_ord__', '__origem_ord__'], errors='ignore')

def aplicar_contas_pagas_shadow(df_estado_lotes_pre_replay, contas_pagas):
    """
    Aplica um replay sombra simplificado das contas pagas sobre o estado técnico
    dos lotes. Não recalcula rendimento, IOF ou IR; apenas consome saldo_atual.
    """
    auditoria = {
        'qtd_contas_processadas': 0,
        'qtd_contas_cobertas': 0,
        'qtd_contas_parcialmente_cobertas': 0,
        'qtd_contas_nao_cobertas': 0,
        'valor_total_contas': 0.0,
        'valor_total_consumido': 0.0,
        'qtd_lotes_vivos': 0,
        'qtd_lotes_consumidos_no_replay': 0,
        'qtd_lotes_switch_vivos': 0,
        'qtd_lotes_switch_consumidos': 0,
        'qtd_inconsistencias': 0,
        'inconsistencias': [],
    }

    if df_estado_lotes_pre_replay is None or len(df_estado_lotes_pre_replay) == 0:
        return pd.DataFrame([]), pd.DataFrame([]), auditoria

    df_estado = ordenar_lotes_para_replay_shadow(df_estado_lotes_pre_replay)
    if len(df_estado) == 0:
        return df_estado, pd.DataFrame([]), auditoria

    df_estado = df_estado.copy()
    if 'saldo_atual' not in df_estado.columns:
        df_estado['saldo_atual'] = 0.0
    df_estado['saldo_atual'] = pd.to_numeric(df_estado['saldo_atual'], errors='coerce').fillna(0.0)

    registros_log = []

    for conta_idx, conta in enumerate(contas_pagas or [], start=1):
        try:
            data_conta = _normalizar_data_lote(conta[0]) if len(conta) > 0 else None
            valor_conta_original = _safe_float(conta[1], 0.0) if len(conta) > 1 else 0.0
            conta_id = conta[4] if len(conta) > 4 else conta_idx
        except Exception:
            data_conta = None
            valor_conta_original = 0.0
            conta_id = conta_idx

        auditoria['qtd_contas_processadas'] += 1
        auditoria['valor_total_contas'] += valor_conta_original

        restante = valor_conta_original
        consumiu_algum = False

        for idx in df_estado.index:
            if restante <= 1e-9:
                break

            status = df_estado.at[idx, 'status'] if 'status' in df_estado.columns else 'ativo'
            saldo_antes = _safe_float(df_estado.at[idx, 'saldo_atual'], 0.0)
            if status != 'ativo' or saldo_antes <= 1e-9:
                continue

            valor_consumido = min(saldo_antes, restante)
            if valor_consumido <= 0:
                continue

            saldo_depois = saldo_antes - valor_consumido
            df_estado.at[idx, 'saldo_atual'] = max(saldo_depois, 0.0)
            if df_estado.at[idx, 'saldo_atual'] <= 1e-9:
                df_estado.at[idx, 'saldo_atual'] = 0.0
                df_estado.at[idx, 'status'] = 'consumido_no_replay'

            registros_log.append({
                'conta_idx': conta_idx,
                'conta_id': conta_id,
                'data_conta': data_conta,
                'valor_conta_original': valor_conta_original,
                'valor_consumido': valor_consumido,
                'valor_restante_conta': max(restante - valor_consumido, 0.0),
                'lote_tecnico_id': df_estado.at[idx, 'lote_tecnico_id'] if 'lote_tecnico_id' in df_estado.columns else None,
                'lote_origem_id': df_estado.at[idx, 'lote_origem_id'] if 'lote_origem_id' in df_estado.columns else None,
                'saldo_lote_antes': saldo_antes,
                'saldo_lote_depois': df_estado.at[idx, 'saldo_atual'],
                'ordem_replay_shadow': df_estado.at[idx, 'ordem_replay_shadow'] if 'ordem_replay_shadow' in df_estado.columns else None,
            })

            restante -= valor_consumido
            auditoria['valor_total_consumido'] += valor_consumido
            consumiu_algum = True

        if restante <= 1e-9:
            auditoria['qtd_contas_cobertas'] += 1
        elif consumiu_algum:
            auditoria['qtd_contas_parcialmente_cobertas'] += 1
        else:
            auditoria['qtd_contas_nao_cobertas'] += 1

    vivos = df_estado[(df_estado['status'] == 'ativo') & (pd.to_numeric(df_estado['saldo_atual'], errors='coerce').fillna(0.0) > 0)] if len(df_estado) else df_estado
    consumidos = df_estado[df_estado['status'] == 'consumido_no_replay'] if len(df_estado) else df_estado
    switch_vivos = vivos[vivos.get('origem').eq('switch_in')] if len(vivos) else vivos
    switch_consumidos = consumidos[consumidos.get('origem').eq('switch_in')] if len(consumidos) else consumidos

    auditoria['qtd_lotes_vivos'] = int(len(vivos))
    auditoria['qtd_lotes_consumidos_no_replay'] = int(len(consumidos))
    auditoria['qtd_lotes_switch_vivos'] = int(len(switch_vivos))
    auditoria['qtd_lotes_switch_consumidos'] = int(len(switch_consumidos))
    auditoria['qtd_inconsistencias'] = len(auditoria['inconsistencias'])

    return df_estado, pd.DataFrame(registros_log), auditoria

# TRACE DO PIPELINE LEGADO DOS APORTES
# ============================================================

def capturar_snapshot_aportes_pipeline(aportes, *, nome):
    """Captura um snapshot mínimo de uma coleção de aportes no formato legado."""
    registros = []
    for ap in (aportes or []):
        try:
            registros.append({
                "data": _normalizar_data_lote(ap[0]) if len(ap) > 0 else None,
                "valor": _safe_float(ap[1], 0.0) if len(ap) > 1 else 0.0,
                "lote_id": _normalizar_lote_id(ap[2]) if len(ap) > 2 else None,
            })
        except Exception:
            continue

    return {
        "nome": nome,
        "qtd": len(registros),
        "soma": sum(r["valor"] for r in registros),
        "lote_ids": sorted([r["lote_id"] for r in registros if r["lote_id"] is not None]),
        "amostra": registros[:5],
    }

def comparar_snapshots_aportes_pipeline(snap_a, snap_b):
    """Compara dois snapshots do pipeline de aportes."""
    snap_a = snap_a or {}
    snap_b = snap_b or {}

    ids_a = set(snap_a.get("lote_ids", []))
    ids_b = set(snap_b.get("lote_ids", []))

    return {
        "qtd_a": snap_a.get("qtd"),
        "qtd_b": snap_b.get("qtd"),
        "soma_a": snap_a.get("soma"),
        "soma_b": snap_b.get("soma"),
        "ids_somente_a": sorted(list(ids_a - ids_b)),
        "ids_somente_b": sorted(list(ids_b - ids_a)),
        "delta_qtd": (snap_b.get("qtd", 0) - snap_a.get("qtd", 0)),
        "delta_soma": (_safe_float(snap_b.get("soma"), 0.0) - _safe_float(snap_a.get("soma"), 0.0)),
    }

def logar_snapshot_aportes_pipeline(snapshot, prefixo="[TRACE-APORTES]"):
    """Log resumido de um snapshot de aportes."""
    if not isinstance(snapshot, dict):
        print(f"{prefixo} snapshot_invalido")
        return

    print(
        f"{prefixo} nome={snapshot.get('nome')} "
        f"qtd={snapshot.get('qtd')} "
        f"soma={snapshot.get('soma')}"
    )

def logar_comparacao_aportes_pipeline(comp, prefixo="[TRACE-APORTES]"):
    """Log resumido da comparação entre dois estágios do pipeline."""
    if not isinstance(comp, dict):
        print(f"{prefixo} comparacao_invalida")
        return

    print(
        f"{prefixo} qtd_a={comp.get('qtd_a')} "
        f"qtd_b={comp.get('qtd_b')} "
        f"delta_qtd={comp.get('delta_qtd')} "
        f"soma_a={comp.get('soma_a')} "
        f"soma_b={comp.get('soma_b')} "
        f"delta_soma={comp.get('delta_soma')}"
    )

    if comp.get("ids_somente_a"):
        print(f"{prefixo} ids_somente_a={comp.get('ids_somente_a')[:10]}")
    if comp.get("ids_somente_b"):
        print(f"{prefixo} ids_somente_b={comp.get('ids_somente_b')[:10]}")

def _ler_inventario_lotes(produtos_dict):
    aba_inv = nome_aba("lotes", ABA_INVENTARIO)
    df_inv = ler_aba_excel(aba_inv)
    _log_debug(f"\n[CHECK] Aba '{aba_inv}': linhas={len(df_inv)} | colunas={list(df_inv.columns)}", DEBUG_SCHEMA_ABAS)
    df_inv.columns = [str(c).strip() for c in df_inv.columns]

    col_id = resolver_coluna(df_inv, "lotes", "lote_id", required=False)
    if col_id is None:
        col_id = selecionar_coluna_id_lote(df_inv, contexto="inventario_lotes", auditar=True)
    col_data = resolver_coluna(df_inv, "lotes", "data_aplicacao", required=True)
    col_valor = resolver_coluna(df_inv, "lotes", "valor_original", required=True)
    col_prod = resolver_coluna(df_inv, "lotes", "produto_id", required=False)
    if col_prod is None:
        investimentos_norm = {_normalizar_nome_texto(nome): prod for nome, prod in produtos_dict.items()}
        col_prod = selecionar_coluna_produto_lote(df_inv, investimentos_norm, contexto="inventario_lotes", auditar=True)

    df_inv[col_data] = pd.to_datetime(df_inv[col_data], errors="coerce").dt.date
    df_inv[col_valor] = pd.to_numeric(df_inv[col_valor], errors="coerce")
    df_inv = df_inv.dropna(subset=[col_id, col_data, col_valor]).copy()

    lote_produto = {}
    aportes_raw = []
    for _, row in df_inv.iterrows():
        lote_id = str(row[col_id]).strip()
        info_invest = _classificar_investimento_inventario(row.get(col_prod) if col_prod else None)
        produto_nome = info_invest["produto_nome"]
        produto_resolvido = _resolver_produto_por_nome(produtos_dict, produto_nome) if produto_nome else None
        lote_produto[lote_id] = produto_resolvido
        aportes_raw.append((
            pd.to_datetime(row[col_data]).date() if hasattr(pd.to_datetime(row[col_data], errors="coerce"), 'date') else row[col_data],
            float(row[col_valor]),
            lote_id,
            bool(info_invest["ja_aplicado"]),
        ))
    return lote_produto, aportes_raw

def _parse_pago_planilha(valor) -> bool:
    if pd.isna(valor):
        return False if CONTRATO_OPERACIONAL and CONTRATO_OPERACIONAL.get("politicas", {}).get("tratar_pago_nulo_como_nao", True) else False
    return str(valor).strip().upper() in {"OK", "SIM", "S", "TRUE", "1", "PAGO"}

def _ler_gastos_passados_futuros(hoje):
    aba_gastos = nome_aba("despesas", ABA_GASTOS)
    df_gastos = ler_aba_excel(aba_gastos)
    _log_debug(f"[CHECK] Aba '{aba_gastos}': linhas={len(df_gastos)} | colunas={list(df_gastos.columns)}", DEBUG_SCHEMA_ABAS)

    df_gastos.columns = [str(c).strip() for c in df_gastos.columns]

    col_data = resolver_coluna(df_gastos, "despesas", "data")
    col_valor = resolver_coluna(df_gastos, "despesas", "valor")
    col_desc = resolver_coluna(df_gastos, "despesas", "descricao", required=False)
    col_pago = resolver_coluna(df_gastos, "despesas", "pago", required=False)
    col_lote1 = resolver_coluna(df_gastos, "despesas", "lote_usado_1", required=False)
    col_lote2 = resolver_coluna(df_gastos, "despesas", "lote_usado_2", required=False)

    df_gastos[col_data] = pd.to_datetime(df_gastos[col_data], errors="coerce").dt.date
    df_gastos[col_valor] = pd.to_numeric(df_gastos[col_valor], errors="coerce")
    df_gastos = df_gastos.dropna(subset=[col_data, col_valor]).copy()

    if col_desc is None:
        col_desc = "__descricao_padrao__"
        df_gastos[col_desc] = "Despesa Diversa"

    tem_lotes_usados = (col_lote1 is not None) or (col_lote2 is not None)

    def _valor_lote(row, col):
        if col is None:
            return ""
        try:
            v = row[col]
        except Exception:
            return ""
        if pd.isna(v):
            return ""
        s = str(v).strip()
        return "" if s.lower() in {"", "nan", "none"} else s

    contas_pagas, contas_nao_pagas = [], []

    for ordem_processamento, (_, row) in enumerate(df_gastos.iterrows(), start=1):
        data = row[col_data]
        valor = float(row[col_valor])
        desc = str(row.get(col_desc, ""))[:100]
        pago = _parse_pago_planilha(row.get(col_pago)) if col_pago is not None else False
        lote1 = _valor_lote(row, col_lote1) if tem_lotes_usados else ""
        lote2 = _valor_lote(row, col_lote2) if tem_lotes_usados else ""
        conta_tuple = (data, valor, desc, lote1, lote2, ordem_processamento)
        if pago and data <= hoje:
            contas_pagas.append(conta_tuple)
        elif (not pago) and data >= hoje:
            contas_nao_pagas.append(conta_tuple)

    contas_pagas = ordenar_contas_processamento(contas_pagas)
    contas_nao_pagas = ordenar_contas_processamento(contas_nao_pagas)
    return contas_pagas, contas_nao_pagas

# =========================================================
# 09. HEURÍSTICAS AUXILIARES PRÉ-LEITURA
# =========================================================
def _serie_texto_normalizada(serie: pd.Series) -> pd.Series:
    return serie.fillna("").astype(str).str.strip()

def _avaliar_coluna_candidata(
    df: pd.DataFrame,
    coluna: str,
    *,
    exigir_unicidade: bool = False,
    peso_preenchimento: float = POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
    bonus_unicidade: float = POL_COL_BONUS_UNICIDADE_ID_LOTE,
):
    serie = _serie_texto_normalizada(df[coluna])
    total = len(serie)
    nao_vazios = int((serie != "").sum())
    taxa_preenchimento = (nao_vazios / total) if total else 0.0
    unicos = int(serie[serie != ""].nunique())
    duplicados = int(serie[serie != ""].duplicated().sum())
    score = taxa_preenchimento * float(peso_preenchimento) + unicos
    if exigir_unicidade and duplicados == 0 and nao_vazios > 0:
        score += float(bonus_unicidade)
    return {
        "coluna": coluna,
        "total": total,
        "nao_vazios": nao_vazios,
        "taxa_preenchimento": taxa_preenchimento,
        "unicos": unicos,
        "duplicados": duplicados,
        "score": score,
    }

def _escolher_melhor_coluna(
    df: pd.DataFrame,
    candidatas,
    *,
    exigir_unicidade: bool = False,
    peso_preenchimento: float = POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
    bonus_unicidade: float = POL_COL_BONUS_UNICIDADE_ID_LOTE,
):
    avaliacoes = [
        _avaliar_coluna_candidata(
            df,
            c,
            exigir_unicidade=exigir_unicidade,
            peso_preenchimento=peso_preenchimento,
            bonus_unicidade=bonus_unicidade,
        )
        for c in candidatas
    ]
    avaliacoes.sort(key=lambda x: (x["score"], x["nao_vazios"], x["unicos"]), reverse=True)
    return avaliacoes[0] if avaliacoes else None, avaliacoes

def _normalizar_nome_texto(valor: str) -> str:
    txt = str(valor or "").strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    txt = re.sub(r"\s+", " ", txt)
    return txt

def normalizar_nome(valor) -> str:
    """Fallback de compatibilidade para normalização textual de nomes/investimentos."""
    return _normalizar_nome_texto(valor)

PRODUTO_FALLBACK_NOME = normalizar_nome(PRODUTO_FALLBACK_NOME_RAW)

def selecionar_coluna_id_lote(df: pd.DataFrame, *, contexto: str = "lotes", auditar: bool | None = None) -> str:
    """Seleciona a coluna de ID do lote em modo híbrido, validado e auditável."""
    if auditar is None:
        auditar = AUDITORIA_COLUNA_ESCOLHIDA

    escolhida = None
    origem = None
    avaliacoes = []

    try:
        col_cfg = resolver_coluna(df, "lotes", "lote_id", required=False)
    except Exception:
        col_cfg = None

    if col_cfg is not None:
        avaliacao = _avaliar_coluna_candidata(
            df,
            col_cfg,
            exigir_unicidade=POL_COL_EXIGIR_UNICIDADE_LOTE_ID,
            peso_preenchimento=POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
            bonus_unicidade=POL_COL_BONUS_UNICIDADE_ID_LOTE,
        )
        avaliacoes.append({**avaliacao, "origem": "config"})
        if avaliacao["nao_vazios"] > 0:
            escolhida = col_cfg
            origem = "config"

    if escolhida is None:
        cols = list(df.columns)
        candidatas = []
        tokens_conjuntos = [str(tok).strip().lower() for tok in POL_COL_LOTE_ID_TOKENS_CONJUNTOS]
        for col in cols:
            norm = _normalizar_nome_coluna(col)
            if (
                (tokens_conjuntos and all(tok in norm for tok in tokens_conjuntos))
                or norm in POL_COL_LOTE_ID_TOKENS_FORTES
            ):
                candidatas.append(col)

        if not candidatas:
            raise KeyError(
                f"Não foi possível identificar com segurança a coluna de ID do lote em {contexto}. "
                f"Colunas disponíveis: {list(df.columns)}"
            )

        melhor, avals = _escolher_melhor_coluna(
            df,
            candidatas,
            exigir_unicidade=POL_COL_EXIGIR_UNICIDADE_LOTE_ID,
            peso_preenchimento=POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
            bonus_unicidade=POL_COL_BONUS_UNICIDADE_ID_LOTE,
        )
        avaliacoes.extend([{**a, "origem": "heuristica"} for a in avals])
        escolhida = melhor["coluna"]
        origem = "heuristica"

    serie = _serie_texto_normalizada(df[escolhida])
    if (serie != "").sum() == 0:
        raise RuntimeError(f"Coluna de ID do lote selecionada ({escolhida}) está vazia em {contexto}.")
    if serie[serie != ""].nunique() < POL_COL_CARDINALIDADE_MINIMA_LOTE_ID:
        raise RuntimeError(
            f"Coluna de ID do lote selecionada ({escolhida}) tem baixa cardinalidade em {contexto}; "
            "verifique aliases do config e estrutura da planilha."
        )

    if auditar:
        avaliacao_escolhida = _avaliar_coluna_candidata(
            df,
            escolhida,
            exigir_unicidade=POL_COL_EXIGIR_UNICIDADE_LOTE_ID,
            peso_preenchimento=POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
            bonus_unicidade=POL_COL_BONUS_UNICIDADE_ID_LOTE,
        )
        print(
            f" -> [AUDITORIA] Coluna de ID do lote em {contexto}: '{escolhida}' "
            f"(origem={origem}, preenchimento={avaliacao_escolhida['taxa_preenchimento']:.1%}, "
            f"unicos={avaliacao_escolhida['unicos']}, duplicados={avaliacao_escolhida['duplicados']})"
        )

    return escolhida

def selecionar_coluna_produto_lote(
    df: pd.DataFrame,
    investimentos_norm: dict,
    *,
    contexto: str = "lotes",
    auditar: bool | None = None,
):
    """Seleciona a coluna de produto/investimento do lote em modo híbrido, validado e auditável."""
    if auditar is None:
        auditar = AUDITORIA_COLUNA_ESCOLHIDA

    melhor_match = -1.0

    try:
        col_cfg = resolver_coluna(df, "lotes", "produto_id", required=False)
    except Exception:
        col_cfg = None

    candidatas = []
    if col_cfg is not None:
        candidatas.append((col_cfg, "config"))

    for col in df.columns:
        norm = _normalizar_nome_coluna(col)
        if any(tok in norm for tok in POL_COL_PRODUTO_TOKENS_BUSCA):
            candidatas.append((col, "heuristica"))

    seen = set()
    candidatas = [(c, o) for c, o in candidatas if not (c in seen or seen.add(c))]

    if not candidatas:
        return None

    def taxa_match(coluna: str) -> float:
        serie = _serie_texto_normalizada(df[coluna])
        vals = [normalizar_nome(v) for v in serie if v]
        if not vals:
            return 0.0
        reconhecidos = sum(1 for v in vals if v in investimentos_norm)
        return reconhecidos / len(vals)

    melhor_coluna = None
    melhor_origem = None
    melhor_av = None
    for col, origem_cand in candidatas:
        av = _avaliar_coluna_candidata(
            df,
            col,
            exigir_unicidade=False,
            peso_preenchimento=POL_COL_PESO_PREENCHIMENTO_PRODUTO,
            bonus_unicidade=0.0,
        )
        score = (
            av["taxa_preenchimento"] * POL_COL_PESO_PREENCHIMENTO_PRODUTO
            + taxa_match(col) * POL_COL_PESO_MATCH_INVESTIMENTO_PRODUTO
        )
        if score > melhor_match:
            melhor_match = score
            melhor_coluna = col
            melhor_origem = origem_cand
            melhor_av = av

    if melhor_coluna is None or melhor_av["nao_vazios"] == 0:
        return None

    if auditar:
        print(
            f" -> [AUDITORIA] Coluna de produto do lote em {contexto}: '{melhor_coluna}' "
            f"(origem={melhor_origem}, preenchimento={melhor_av['taxa_preenchimento']:.1%}, "
            f"match_investimentos={taxa_match(melhor_coluna):.1%})"
        )

    return melhor_coluna

# =========================================================
# 10. CALENDÁRIO FINANCEIRO, REDE, BCB E TRIBUTAÇÃO
# =========================================================
def _calcular_pascoa(ano):
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)

def gerar_dias_sem_rendimento_bancario(ano_ini=None, ano_fim=None):
    ano_ini = CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO if ano_ini is None else ano_ini
    ano_fim = CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO if ano_fim is None else ano_fim
    dias = set()
    for ano in range(int(ano_ini), int(ano_fim) + 1):
        pascoa = _calcular_pascoa(ano)
        terca_carnaval = pascoa - timedelta(days=47)
        dias.add(terca_carnaval)
    return dias

DIAS_SEM_RENDIMENTO_BANCARIO = gerar_dias_sem_rendimento_bancario()

def is_dia_rendimento(data_atual: date, bcb_map: dict = None) -> bool:
    if data_atual in DIAS_SEM_RENDIMENTO_BANCARIO:
        return False
    if bcb_map and data_atual in bcb_map:
        return True
    return cal.is_working_day(data_atual)

def contar_dias_rendimento(data_inicio: date, data_fim: date, bcb_map: dict = None) -> int:
    if data_fim <= data_inicio:
        return 0
    dias = 0
    d = data_inicio + timedelta(days=1)
    while d <= data_fim:
        if is_dia_rendimento(d, bcb_map):
            dias += 1
        d += timedelta(days=1)
    return dias

def extrair_lote_usado_unico(row, nome_coluna=None):
    """Extrai um único lote usado de uma linha do Excel.
    Retorna string vazia quando ausente.
    """
    if not nome_coluna or nome_coluna not in row.index:
        return ''

    val = row[nome_coluna]
    if pd.isna(val):
        return ''

    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return ''

    return s

def _normalizar_lote_id(valor):
    """
    Normaliza identificador de lote:
    - string
    - trim
    - remove sufixo '.0' vindo de Excel numérico
    """
    if valor is None:
        return None
    try:
        s = str(valor).strip()
        if s == "" or s.lower() == "nan":
            return None
        if s.endswith('.0'):
            s = s[:-2]
        return s
    except Exception:
        return None

def _normalizar_data_lote(valor):
    """Converte valor para date, de forma defensiva."""
    if valor is None:
        return None
    try:
        if hasattr(valor, 'date'):
            return valor.date()
    except Exception:
        pass
    try:
        ts = pd.to_datetime(valor, errors='coerce')
        if pd.isna(ts):
            return None
        return ts.date()
    except Exception:
        return None

def _normalizar_valor_lote(valor, default=None):
    """Converte valor monetário do lote para float."""
    if valor is None:
        return default
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        s = str(valor).strip()
        if s == '' or s.lower() == 'nan':
            return default
        s = s.replace('R$', '').replace('%', '').strip()
        try:
            return float(s)
        except Exception:
            pass
        s = s.replace('.', '').replace(',', '.')
        return float(s)
    except Exception:
        try:
            return float(valor)
        except Exception:
            return default

def extrair_metadata_serie_cdi(serie_cdi):
    """Extrai data inicial/final e quantidade de observações da série CDI."""
    meta = {'data_inicial': None, 'data_final': None, 'qtd_observacoes': 0}
    if serie_cdi is None:
        return meta
    try:
        if isinstance(serie_cdi, dict) and len(serie_cdi) > 0:
            datas = [_coagir_para_date(k) for k in serie_cdi.keys()]
            datas = [d for d in datas if d is not None]
            if datas:
                meta['data_inicial'] = min(datas)
                meta['data_final'] = max(datas)
                meta['qtd_observacoes'] = len(datas)
                return meta
    except Exception:
        pass
    try:
        if isinstance(serie_cdi, list) and len(serie_cdi) > 0:
            datas = []
            for item in serie_cdi:
                if isinstance(item, (tuple, list)) and len(item) >= 1:
                    datas.append(_coagir_para_date(item[0]))
                elif isinstance(item, dict):
                    if 'Data' in item:
                        datas.append(_coagir_para_date(item['Data']))
                    elif 'data' in item:
                        datas.append(_coagir_para_date(item['data']))
            datas = [d for d in datas if d is not None]
            if datas:
                meta['data_inicial'] = min(datas)
                meta['data_final'] = max(datas)
                meta['qtd_observacoes'] = len(datas)
                return meta
    except Exception:
        pass
    try:
        if hasattr(serie_cdi, 'index') and not hasattr(serie_cdi, 'columns'):
            datas = [_coagir_para_date(x) for x in list(serie_cdi.index)]
            datas = [d for d in datas if d is not None]
            if datas:
                meta['data_inicial'] = min(datas)
                meta['data_final'] = max(datas)
                meta['qtd_observacoes'] = len(datas)
                return meta
    except Exception:
        pass
    try:
        if hasattr(serie_cdi, 'columns') and hasattr(serie_cdi, '__len__'):
            col_data = None
            for cand in ('Data', 'data', 'DATE', 'date'):
                if cand in serie_cdi.columns:
                    col_data = cand
                    break
            if col_data is not None and len(serie_cdi) > 0:
                datas = [_coagir_para_date(x) for x in list(serie_cdi[col_data])]
                datas = [d for d in datas if d is not None]
                if datas:
                    meta['data_inicial'] = min(datas)
                    meta['data_final'] = max(datas)
                    meta['qtd_observacoes'] = len(datas)
                    return meta
    except Exception:
        pass
    return meta

def atualizar_metadata_cdi(serie_cdi, fonte: str) -> None:
    global CDI_FONTE_UTILIZADA, CDI_DATA_INICIAL_UTILIZADA, CDI_DATA_FINAL_UTILIZADA, CDI_QTD_OBSERVACOES
    meta = extrair_metadata_serie_cdi(serie_cdi)
    CDI_FONTE_UTILIZADA = fonte
    CDI_DATA_INICIAL_UTILIZADA = meta.get('data_inicial')
    CDI_DATA_FINAL_UTILIZADA = meta.get('data_final')
    CDI_QTD_OBSERVACOES = meta.get('qtd_observacoes')

def obter_data_corte_cdi(serie_cdi=None, fallback=None):
    global CDI_DATA_CORTE_CONGELADA
    try:
        meta = extrair_metadata_serie_cdi(serie_cdi)
        if meta.get('data_final') is not None:
            return meta['data_final']
    except Exception:
        pass
    if CDI_DATA_CORTE_CONGELADA is not None:
        return CDI_DATA_CORTE_CONGELADA
    try:
        if Path(CACHE_BCB_FILE).exists():
            with open(CACHE_BCB_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            mapa = cache_data.get('mapa', {})
            datas = [datetime.strptime(k, '%Y-%m-%d').date() for k in mapa.keys()]
            if datas:
                return max(datas)
    except Exception:
        pass
    return fallback

def construir_cdi_fixo_ate_data(data_inicial, data_final, taxa_diaria_padrao, calendario=None):
    """Constrói série CDI fixa somente até a data final informada."""
    if data_inicial is None or data_final is None:
        raise ValueError('Data inicial/final inválida para construir CDI fixo.')
    if data_final < data_inicial:
        raise ValueError('data_final < data_inicial na construção do CDI fixo.')
    serie = {}
    d = data_inicial
    while d <= data_final:
        incluir = True
        try:
            if calendario is not None and hasattr(calendario, 'is_working_day'):
                incluir = bool(calendario.is_working_day(d))
        except Exception:
            incluir = True
        if incluir:
            serie[d] = 1.0 + float(taxa_diaria_padrao)
        d = d + timedelta(days=1)
    return serie

def logar_metadata_cdi(prefixo='[CDI]'):
    if not DEBUG_CDI:
        return
    partes = [f"fonte={CDI_FONTE_UTILIZADA}", f"data_final={CDI_DATA_FINAL_UTILIZADA}", f"corte_congelado={CDI_DATA_CORTE_CONGELADA}"]
    print("[CDI] " + " | ".join(partes))

def obter_historico_bcb(data_inicio=None, usar_cache=True, fallback_url=FALLBACK_BCB_URL):
    """Carrega o CDI diário priorizando a API oficial do BCB.

    Ordem operacional adotada:
    1) API oficial do BCB;
    2) fallback do Drive, quando configurado;
    3) cache local já existente no ambiente;
    4) série fixa determinística até a data terminal conhecida.
    """
    global CDI_DATA_CORTE_CONGELADA
    print('>>> [BCB] Carregando histórico CDI diário...')

    if data_inicio:
        try:
            if isinstance(data_inicio, str):
                data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y').date()
            else:
                data_inicio_dt = _coagir_para_date(data_inicio)
        except Exception:
            data_inicio_dt = HISTORICO_BCB_DATA_MINIMA
    else:
        data_inicio_dt = HISTORICO_BCB_DATA_MINIMA

    data_inicio_dt = max(data_inicio_dt, HISTORICO_BCB_DATA_MINIMA)
    dt_query = data_inicio_dt.strftime('%d/%m/%Y')
    hoje_str = DATA_REFERENCIA.strftime('%d/%m/%Y')
    url = BCB_SERIE_12_URL.format(data_inicial=dt_query, data_final=hoje_str)
    headers = {'User-Agent': REDE_USER_AGENT_BCB, 'Accept': REDE_ACCEPT_BCB}

    try:
        r = requests.get(url, headers=headers, timeout=REDE_TIMEOUT_BCB_SEGUNDOS, verify=REDE_VERIFICAR_SSL)
        r.raise_for_status()
        dados_json = r.json()
        mapa_cdi = {}
        ultima_taxa = TAXA_DIA_BASE
        for item in dados_json:
            dt = datetime.strptime(item['data'], '%d/%m/%Y').date()
            val_pct = float(item['valor'])
            taxa_dec = val_pct / 100.0
            mapa_cdi[dt] = 1.0 + taxa_dec
            ultima_taxa = taxa_dec

        cache_data = {
            'mapa': {k.strftime('%Y-%m-%d'): v for k, v in mapa_cdi.items()},
            'taxa_projecao': ultima_taxa,
            'data_atualizacao': DATA_REFERENCIA.strftime('%Y-%m-%d'),
        }
        with open(CACHE_BCB_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)

        print(f" -> API BCB OK: {len(mapa_cdi)} dias carregados")
        atualizar_metadata_cdi(mapa_cdi, fonte='bcb_api')
        CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA
        logar_metadata_cdi()
        return mapa_cdi, ultima_taxa
    except Exception as e:
        print(f" -> API BCB falhou: {e}")

    if fallback_url:
        print(' -> Tentando fallback do Drive...')
        mapa_fallback, taxa_fallback = baixar_fallback_bcb()
        if mapa_fallback:
            atualizar_metadata_cdi(mapa_fallback, fonte='drive_fallback')
            CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA

            data_atual = data_inicio_dt
            data_final = obter_data_corte_cdi(mapa_fallback, fallback=DATA_REFERENCIA)
            dias_preenchidos = 0
            while data_atual <= data_final:
                if data_atual not in mapa_fallback:
                    mapa_fallback[data_atual] = 1.0 + TAXA_DIA_BASE
                    dias_preenchidos += 1
                data_atual += timedelta(days=1)

            cache_data = {
                'mapa': {k.strftime('%Y-%m-%d'): v for k, v in mapa_fallback.items()},
                'taxa_projecao': taxa_fallback,
                'data_atualizacao': DATA_REFERENCIA.strftime('%Y-%m-%d'),
                'fonte': 'fallback+preenchimento',
            }
            with open(CACHE_BCB_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)

            print(f" -> Fallback + preenchimento: {len(mapa_fallback)} dias totais")
            print(f"    ({len(mapa_fallback) - dias_preenchidos} do arquivo, {dias_preenchidos} preenchidos)")
            logar_metadata_cdi()
            return mapa_fallback, taxa_fallback

    if usar_cache and Path(CACHE_BCB_FILE).exists():
        print(' -> Tentando cache local do ambiente...')
        try:
            with open(CACHE_BCB_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            mapa_cdi = {datetime.strptime(k, '%Y-%m-%d').date(): v for k, v in cache_data['mapa'].items()}
            ultima_taxa = cache_data.get('taxa_projecao', cache_data.get('ultima', TAXA_DIA_BASE))
            atualizar_metadata_cdi(mapa_cdi, fonte='cache_local')
            CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA
            print(f" -> Cache local OK: {len(mapa_cdi)} dias")
            logar_metadata_cdi()
            return mapa_cdi, ultima_taxa
        except Exception as e:
            print(f" -> Cache local inválido: {e}")

    data_final_fixa = obter_data_corte_cdi(fallback=DATA_REFERENCIA)
    calendario = None
    try:
        calendario = Brazil()
    except Exception:
        calendario = None

    mapa_fixo = construir_cdi_fixo_ate_data(
        data_inicial=data_inicio_dt,
        data_final=data_final_fixa,
        taxa_diaria_padrao=TAXA_DIA_BASE,
        calendario=calendario,
    )
    atualizar_metadata_cdi(mapa_fixo, fonte='taxa_fixa_fallback')
    if CDI_DATA_CORTE_CONGELADA is None:
        CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA

    print(' -> Usando taxa fixa padrão somente até a data terminal congelada')
    logar_metadata_cdi()
    return mapa_fixo, TAXA_DIA_BASE

def _money_round_half_up(valor: float, casas: int = 2) -> float:
    """Arredondamento monetário canônico com HALF_UP."""
    try:
        q = Decimal("1." + ("0" * casas)) if casas > 0 else Decimal("1")
        return float(Decimal(str(valor)).quantize(q, rounding=ROUND_HALF_UP))
    except Exception:
        return float(valor)

def dinheiro_round(valor: float, casas: int = 2) -> float:
    """Alias legado para arredondamento monetário canônico."""
    return _money_round_half_up(valor, casas)

def _taxa_ir(dias: int, isento: bool = False) -> float:
    if isento:
        return 0.0
    if IR_FAIXAS:
        for dias_max in sorted(IR_FAIXAS.keys()):
            if dias <= dias_max:
                return float(IR_FAIXAS[dias_max]["ir"])
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15

def obter_aliquota_ir(dias: int, isento: bool = False) -> float:
    return _taxa_ir(dias, isento)

def _taxa_iof(dias: int) -> float:
    if dias < 30:
        return float(IOF_TABLE[dias])
    return 0.0

def _fator_liquido(fator_acumulado: float, dias_vida: int, isento: bool = False) -> float:
    if fator_acumulado <= 1.0:
        return 1.0
    iof = _taxa_iof(dias_vida)
    ir = _taxa_ir(dias_vida, isento)
    ratio_lucro = 1.0 - (1.0 / fator_acumulado)
    taxa_efetiva = iof + (1 - iof) * ir
    return 1.0 - ratio_lucro * taxa_efetiva

def _to_float_br(valor, default=0.0):
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return default
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    txt = str(valor).strip()
    if not txt:
        return default
    txt = txt.replace("R$", "").replace(" ", "")
    if "," in txt and "." in txt:
        txt = txt.replace(".", "").replace(",", ".")
    elif "," in txt:
        txt = txt.replace(",", ".")
    try:
        return float(txt)
    except Exception:
        return default

# =========================================================
# 11. MODELOS DE DOMÍNIO
# =========================================================
class Produto:
    """Produto simples (CDB, LCI, LCA, etc.)."""

    def __init__(
        self,
        nome: str,
        taxa_base: float,
        taxa_bonus: float = None,
        dias_bonus: int = 0,
        prazo_dias: int = 0,
        carencia_dias: int = 0,
        isento_ir: bool = False,
        valor_min: float = 0,
        valor_max: float = 1e12,
        ativo: bool = True,
        somente_combo: bool = False,
    ):
        self.nome = nome
        self.taxa_base = taxa_base
        self.taxa_bonus = taxa_bonus if taxa_bonus is not None else taxa_base
        self.dias_bonus = dias_bonus
        self.prazo_dias = prazo_dias
        self.carencia_dias = carencia_dias
        self.isento_ir = isento_ir
        self.valor_min = valor_min
        self.valor_max = valor_max
        self.ativo = ativo
        self.somente_combo = somente_combo

    def capacidade_aporte(self, valor: float) -> float:
        try:
            v = float(valor)
        except Exception:
            return 0.0
        vmin = float(getattr(self, "valor_min", 0.0) or 0.0)
        vmax = float(getattr(self, "valor_max", 1e18) or 1e18)
        if v < vmin:
            return 0.0
        return max(0.0, min(v, vmax))

    def aceita_aporte(self, valor: float) -> bool:
        return self.capacidade_aporte(valor) >= float(valor or 0.0) - 1e-9

    def taxa_dia(self, idade: int) -> float:
        """
        Retorna o multiplicador de CDI aplicável ao lote na idade informada.

        Importante:
        - prazo_dias NÃO interrompe a capitalização do lote existente;
        - prazo_dias permanece apenas como metadado/critério de elegibilidade;
        - a transição de rendimento segue apenas a regra bonus -> base.
        """
        mult = self.taxa_bonus if idade < self.dias_bonus else self.taxa_base
        return float(mult)

class ComboProduto:
    def __init__(
        self,
        nome: str,
        produto_base: Produto,
        produto_bonus: Produto,
        razao_base: float = 2.0,
        razao_bonus: float = 1.0,
        ativo: bool = True,
        somente_combo: bool = False,
    ):
        self.nome = nome
        self.produto_base = produto_base
        self.produto_bonus = produto_bonus
        self.razao_base = razao_base
        self.razao_bonus = razao_bonus
        self.valor_min = produto_base.valor_min + produto_bonus.valor_min
        self.valor_max = min(produto_base.valor_max, produto_bonus.valor_max) * (razao_base + razao_bonus) / razao_base
        self.ativo = ativo
        self.somente_combo = somente_combo

        try:
            w_sum = float(self.razao_base + self.razao_bonus)
            self.taxa_base = (
                float(self.produto_base.taxa_base) * self.razao_base
                + float(self.produto_bonus.taxa_base) * self.razao_bonus
            ) / w_sum
            tb_base = float(getattr(self.produto_base, "taxa_bonus", self.produto_base.taxa_base) or self.produto_base.taxa_base)
            tb_bon = float(getattr(self.produto_bonus, "taxa_bonus", self.produto_bonus.taxa_base) or self.produto_bonus.taxa_base)
            self.taxa_bonus = (tb_base * self.razao_base + tb_bon * self.razao_bonus) / w_sum
        except Exception:
            self.taxa_base = 1.0
            self.taxa_bonus = 1.0

    def aceita_aporte(self, valor: float) -> bool:
        vb, vx = self.dividir_valor(float(valor or 0.0))
        if vb <= 0 and vx <= 0:
            return False
        return (
            self.produto_base.aceita_aporte(vb) if vb > 0 else True
        ) and (
            self.produto_bonus.aceita_aporte(vx) if vx > 0 else True
        )

    def dividir_valor(self, total: float):
        if total < self.valor_min:
            return 0.0, 0.0

        ideal_base = total * self.razao_base / (self.razao_base + self.razao_bonus)
        ideal_bonus = total * self.razao_bonus / (self.razao_base + self.razao_bonus)

        if ideal_base < self.produto_base.valor_min:
            ideal_base = self.produto_base.valor_min
            ideal_bonus = total - ideal_base
        elif ideal_bonus < self.produto_bonus.valor_min:
            ideal_bonus = self.produto_bonus.valor_min
            ideal_base = total - ideal_bonus

        if ideal_base > self.produto_base.valor_max:
            ideal_base = self.produto_base.valor_max
            ideal_bonus = total - ideal_base
        if ideal_bonus > self.produto_bonus.valor_max:
            ideal_bonus = self.produto_bonus.valor_max
            ideal_base = total - ideal_bonus

        ideal_base = max(float(ideal_base), 0.0)
        ideal_bonus = max(float(ideal_bonus), 0.0)

        total = round(float(total), 2)
        ideal_base = round(float(ideal_base), 2)
        ideal_bonus = round(total - ideal_base, 2)

        if ideal_bonus < 0:
            ideal_bonus = 0.0
            ideal_base = round(total, 2)

        return ideal_base, ideal_bonus

class Lote:
    def __init__(
        self,
        id_lote,
        data_aplicacao: date,
        valor_inicial: float,
        produto: Produto = None,
        carencia_ate: date = None,
        data_base_fiscal: date = None,
        fator_acumulado_inicial: float = 1.0,
        pendente_aporte: bool = False,
        principal_remanescente_inicial: float = None,
        taxa_base_cdi: float = None,
        taxa_bonus_cdi: float = None,
        dias_bonus: int = None,
    ):
        self.id = str(id_lote).strip()
        self.data_aplicacao = data_aplicacao
        self.data_base_fiscal = data_base_fiscal or data_aplicacao
        self.valor_inicial = float(valor_inicial)
        self.saldo_bruto = float(valor_inicial)
        self.fator_acumulado = max(1.0, float(fator_acumulado_inicial))
        self.principal_remanescente = float(
            self.valor_inicial if principal_remanescente_inicial is None else principal_remanescente_inicial
        )
        self.esgotado = False
        self.vezes_usado = 0
        self.total_bruto_sacado = 0.0
        self.total_imposto_pago = 0.0
        self.total_liquido_sacado = 0.0
        self.produto = produto
        self.carencia_ate = carencia_ate
        self.pendente_aporte = bool(pendente_aporte)
        self.historico_switches = []
        self.switch_agendado = None
        self.switch_plano = None

        taxa_base_prod = (
            float(getattr(produto, "taxa_base", TAXA_BASE_DEFAULT) or TAXA_BASE_DEFAULT)
            if produto is not None else TAXA_BASE_DEFAULT
        )
        taxa_bonus_prod = (
            float(getattr(produto, "taxa_bonus", taxa_base_prod) or taxa_base_prod)
            if produto is not None else TAXA_BONUS_DEFAULT
        )
        dias_bonus_prod = (
            int(getattr(produto, "dias_bonus", DIAS_BONUS_DEFAULT) or DIAS_BONUS_DEFAULT)
            if produto is not None else DIAS_BONUS_DEFAULT
        )

        self.taxa_base_cdi = float(taxa_base_cdi if taxa_base_cdi is not None else taxa_base_prod)
        self.taxa_bonus_cdi = float(taxa_bonus_cdi if taxa_bonus_cdi is not None else taxa_bonus_prod)
        self.dias_bonus = int(dias_bonus if dias_bonus is not None else dias_bonus_prod)

    def get_taxa_dia(self, data_atual: date) -> float:
        idade = (data_atual - self.data_base_fiscal).days
        if self.taxa_bonus_cdi > 0.0 and idade < self.dias_bonus:
            return float(self.taxa_bonus_cdi)
        return float(self.taxa_base_cdi)

    def atualizar_juros(self, data_atual: date, taxa_diaria_decimal):
        if self.esgotado or data_atual <= self.data_aplicacao:
            return
        idade = (data_atual - self.data_base_fiscal).days
        mult = self.taxa_bonus_cdi if (self.taxa_bonus_cdi > 0.0 and idade < self.dias_bonus) else self.taxa_base_cdi
        fator_dia = (1.0 + taxa_diaria_decimal) ** mult
        self.saldo_bruto = _money_round_half_up(self.saldo_bruto * fator_dia)
        self.fator_acumulado *= fator_dia

    def get_fator_liquido(self, data_resgate: date) -> float:
        dias_vida = (data_resgate - self.data_base_fiscal).days
        if dias_vida < 0 or self.saldo_bruto <= 0:
            return 0.0
        isento = bool(self.produto.isento_ir) if self.produto else False
        iof = _taxa_iof(dias_vida)
        ir = _taxa_ir(dias_vida, isento)
        principal_base = max(min(self.principal_remanescente, self.saldo_bruto), 0.0)
        lucro = max(self.saldo_bruto - principal_base, 0.0)
        taxa_total = iof + (1 - iof) * ir
        imposto = lucro * taxa_total
        return max(1.0 - (imposto / self.saldo_bruto), 0.0)

    def valor_liquido_hoje(self, data_hoje: date) -> float:
        return self.saldo_bruto * self.get_fator_liquido(data_hoje)

    def sacar(self, valor_bruto: float) -> float:
        if valor_bruto >= self.saldo_bruto - 0.01:
            sacado = self.saldo_bruto
            self.saldo_bruto = 0.0
            self.principal_remanescente = 0.0
            self.esgotado = True
            self.vezes_usado += 1
            self.total_bruto_sacado += sacado
            return sacado

        if self.saldo_bruto <= 0:
            return 0.0

        valor_bruto = _money_round_half_up(float(valor_bruto))
        sacado = valor_bruto
        saldo_antes = max(float(self.saldo_bruto), 0.0)
        proporcao_sacada = min(max((valor_bruto / saldo_antes), 0.0), 1.0) if saldo_antes > 0 else 1.0
        principal_sacado = round(float(getattr(self, "principal_remanescente", self.valor_inicial)) * proporcao_sacada, 10)
        self.principal_remanescente = max(
            round(float(getattr(self, "principal_remanescente", self.valor_inicial)) - principal_sacado, 10),
            0.0,
        )
        self.saldo_bruto = _money_round_half_up(self.saldo_bruto - valor_bruto)
        self.vezes_usado += 1
        self.total_bruto_sacado += sacado
        return sacado

    def resgatar_total(self, data_resgate: date):
        bruto = self.saldo_bruto
        if bruto <= 0:
            return 0.0, 0.0
        fator = self.get_fator_liquido(data_resgate)
        liquido = bruto * fator
        imposto = bruto - liquido
        self.saldo_bruto = 0.0
        self.principal_remanescente = 0.0
        self.esgotado = True
        self.vezes_usado += 1
        self.total_bruto_sacado += bruto
        self.total_imposto_pago += imposto
        self.total_liquido_sacado += liquido
        return liquido, imposto

    def switch_para(self, novo_produto, data_switch: date) -> list:
        liquido, imposto = self.resgatar_total(data_switch)
        if liquido <= 0:
            return []
        self.historico_switches.append((data_switch, novo_produto.nome, liquido))

        if isinstance(novo_produto, ComboProduto):
            val_base, val_bonus = novo_produto.dividir_valor(liquido)
            novos = []
            if val_base > 0:
                base_id = f"{self.id}_sw_base_{data_switch.strftime('%Y%m%d')}"
                carencia_base = None
                if novo_produto.produto_base.carencia_dias > 0:
                    carencia_base = data_switch + timedelta(days=novo_produto.produto_base.carencia_dias)
                l_base = Lote(
                    base_id,
                    data_switch,
                    val_base,
                    produto=novo_produto.produto_base,
                    carencia_ate=carencia_base,
                    data_base_fiscal=data_switch,
                )
                novos.append(l_base)
            if val_bonus > 0:
                bonus_id = f"{self.id}_sw_bonus_{data_switch.strftime('%Y%m%d')}"
                carencia_bonus = None
                if novo_produto.produto_bonus.carencia_dias > 0:
                    carencia_bonus = data_switch + timedelta(days=novo_produto.produto_bonus.carencia_dias)
                l_bonus = Lote(
                    bonus_id,
                    data_switch,
                    val_bonus,
                    produto=novo_produto.produto_bonus,
                    carencia_ate=carencia_bonus,
                    data_base_fiscal=data_switch,
                )
                novos.append(l_bonus)
            return novos

        novo_id = f"{self.id}_sw_{data_switch.strftime('%Y%m%d')}"
        carencia_ate = None
        if novo_produto.carencia_dias > 0:
            carencia_ate = data_switch + timedelta(days=novo_produto.carencia_dias)
        novo_lote = Lote(
            id_lote=novo_id,
            data_aplicacao=data_switch,
            valor_inicial=liquido,
            produto=novo_produto,
            carencia_ate=carencia_ate,
            data_base_fiscal=data_switch,
        )
        return [novo_lote]

def criar_lote_de_aporte(dt, val, id_l, meta=None):
    """Cria um lote a partir do aporte preservando a regra financeira do otimizador."""
    meta = meta or {}
    produto_meta = meta.get("produto")
    lote = Lote(
        id_l,
        dt,
        val,
        produto=produto_meta,
        carencia_ate=meta.get("carencia_ate", None),
        data_base_fiscal=meta.get("data_base_fiscal", dt),
        fator_acumulado_inicial=meta.get("fator_acumulado_inicial", 1.0),
        taxa_base_cdi=meta.get("taxa_base_cdi", TAXA_BASE_DEFAULT),
        taxa_bonus_cdi=meta.get("taxa_bonus_cdi", TAXA_BONUS_DEFAULT),
        dias_bonus=meta.get("dias_bonus", DIAS_BONUS_DEFAULT),
        principal_remanescente_inicial=meta.get(
            "principal_remanescente",
            meta.get("principal_remanescente_inicial", float(val)),
        ),
    )
    lote.investimento = str(meta.get("investimento", getattr(produto_meta, "nome", "") or "") or "")
    if getattr(lote, "investimento", "") == "" and produto_meta is not None:
        lote.investimento = str(getattr(produto_meta, "nome", "") or "")
    if meta.get("produto_isento_ir", None) is not None and produto_meta is None:
        lote.produto_isento_ir = bool(meta.get("produto_isento_ir"))
    return lote

def atualizar_saldo_lotes_no_dia(lotes_ativos, data_atual, bcb_map=None, taxa_proj=None):
    """Aplica o rendimento diário aos lotes ativos usando CDI diário real do mapa BCB."""
    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE
    if not lotes_ativos or not is_dia_rendimento(data_atual, bcb_map):
        return
    if bcb_map and data_atual in bcb_map:
        fator_dia = float(bcb_map[data_atual])
        taxa_dia = fator_dia - 1.0
    else:
        taxa_dia = float(taxa_proj)
    for lote in lotes_ativos:
        if getattr(lote, "esgotado", False) or float(getattr(lote, "saldo_bruto", 0.0) or 0.0) <= 0.0:
            continue
        lote.atualizar_juros(data_atual, taxa_dia)

def executar_saque_lote(lote, valor_liquido_alvo, data_atual):
    """Executa o saque preservando a matemática financeira já validada."""
    saldo_antes = float(lote.saldo_bruto)
    fator = lote.get_fator_liquido(data_atual)
    if fator <= 0:
        return None

    bruto_necessario = valor_liquido_alvo / fator
    uso_bruto = min(bruto_necessario, lote.saldo_bruto)
    efetivo = _money_round_half_up(lote.sacar(uso_bruto))
    liquido = _money_round_half_up(efetivo * fator)
    imposto = _money_round_half_up(efetivo - liquido)
    lote.total_imposto_pago += imposto
    lote.total_liquido_sacado += liquido

    return {
        "lote": lote,
        "saldo_antes": saldo_antes,
        "fator_liquido": float(fator),
        "bruto": efetivo,
        "liquido": liquido,
        "imposto": imposto,
        "saldo_remanescente": float(lote.saldo_bruto),
    }

def taxa_base_efetiva(prod) -> float:
    if prod is None:
        return 1.0
    try:
        if isinstance(prod, ComboProduto):
            rb = float(getattr(prod, "razao_base", 2.0) or 2.0)
            rx = float(getattr(prod, "razao_bonus", 1.0) or 1.0)
            tb = float(getattr(getattr(prod, "produto_base", None), "taxa_base", 1.0) or 1.0)
            tx = float(getattr(getattr(prod, "produto_bonus", None), "taxa_base", 1.0) or 1.0)
            den = (rb + rx) if (rb + rx) > 0 else 1.0
            return (rb * tb + rx * tx) / den
    except Exception:
        pass
    try:
        return float(getattr(prod, "taxa_base", 1.0) or 1.0)
    except Exception:
        return 1.0

def simular_valor_final_produto(produto, data_inicio: date, valor_inicial: float,
                              data_fim: date, bcb_map: dict, produtos_rolagem: list = None) -> float:
    if data_fim <= data_inicio:
        if isinstance(produto, ComboProduto):
            vb, vx = produto.dividir_valor(valor_inicial)
            if vb <= 0 and vx <= 0:
                return -1e18
            l1 = Lote("V_BASE", data_inicio, vb, produto=produto.produto_base, data_base_fiscal=data_inicio,
                      carencia_ate=(data_inicio + timedelta(days=produto.produto_base.carencia_dias)) if produto.produto_base.carencia_dias > 0 else None)
            l2 = Lote("V_BONUS", data_inicio, vx, produto=produto.produto_bonus, data_base_fiscal=data_inicio,
                      carencia_ate=(data_inicio + timedelta(days=produto.produto_bonus.carencia_dias)) if produto.produto_bonus.carencia_dias > 0 else None)
            total = 0.0
            for l in (l1, l2):
                if l.saldo_bruto <= 0.01:
                    continue
                if l.carencia_ate and data_inicio < l.carencia_ate:
                    return -1e18
                total += l.saldo_bruto * l.get_fator_liquido(data_inicio)
            return total
        else:
            l = Lote("V", data_inicio, valor_inicial, produto=produto, data_base_fiscal=data_inicio,
                     carencia_ate=(data_inicio + timedelta(days=produto.carencia_dias)) if produto.carencia_dias > 0 else None)
            if l.carencia_ate and data_inicio < l.carencia_ate:
                return -1e18
            return l.saldo_bruto * l.get_fator_liquido(data_inicio)

    lotes = []
    if isinstance(produto, ComboProduto):
        vb, vx = produto.dividir_valor(valor_inicial)
        if vb <= 0 and vx <= 0:
            return -1e18
        lotes = [
            Lote("V_BASE", data_inicio, vb, produto=produto.produto_base, data_base_fiscal=data_inicio,
                 carencia_ate=(data_inicio + timedelta(days=produto.produto_base.carencia_dias)) if produto.produto_base.carencia_dias > 0 else None),
            Lote("V_BONUS", data_inicio, vx, produto=produto.produto_bonus, data_base_fiscal=data_inicio,
                 carencia_ate=(data_inicio + timedelta(days=produto.produto_bonus.carencia_dias)) if produto.produto_bonus.carencia_dias > 0 else None),
        ]
    else:
        lotes = [
            Lote("V", data_inicio, valor_inicial, produto=produto, data_base_fiscal=data_inicio,
                 carencia_ate=(data_inicio + timedelta(days=produto.carencia_dias)) if produto.carencia_dias > 0 else None)
        ]

    def _escolher_produto_rolagem(valor_liquido: float, data_ref: date):
        if not produtos_rolagem:
            return None
        candidatos = []
        for p in produtos_rolagem:
            if isinstance(p, ComboProduto):
                continue
            if not getattr(p, 'ativo', True) or getattr(p, 'somente_combo', False):
                continue
            if not p.aceita_aporte(valor_liquido):
                continue
            if p.carencia_dias > 0 and (data_ref + timedelta(days=p.carencia_dias)) > data_fim:
                continue
            candidatos.append(p)
        if not candidatos:
            return None
        candidatos.sort(key=lambda pp: float(getattr(pp, 'taxa_base', 1.0) or 1.0), reverse=True)
        return candidatos[0]

    d = data_inicio
    while d < data_fim:
        if is_dia_rendimento(d, bcb_map):
            atualizar_saldo_lotes_no_dia(lotes, d, bcb_map, TAXA_DIA_BASE)
            for l in lotes:
                if not l.esgotado and l.saldo_bruto > 0.01 and l.data_aplicacao <= d:
                    prod = l.produto
                    idade = (d - l.data_base_fiscal).days
                    if getattr(prod, 'prazo_dias', 0) > 0 and idade >= int(getattr(prod, 'prazo_dias', 0) or 0):
                        fator_liq = l.get_fator_liquido(d)
                        valor_liq = max(0.0, l.saldo_bruto * fator_liq)
                        p_novo = _escolher_produto_rolagem(valor_liquido=valor_liq, data_ref=d)
                        if p_novo is not None and valor_liq > 0.01:
                            l.saldo_bruto = valor_liq
                            l.valor_inicial = valor_liq
                            l.produto = p_novo
                            l.fator_acumulado = 1.0
                            l.data_base_fiscal = d
                            l.carencia_ate = (d + timedelta(days=p_novo.carencia_dias)) if p_novo.carencia_dias > 0 else None
        d += timedelta(days=1)

    total_liq = 0.0
    for l in lotes:
        if l.esgotado or l.saldo_bruto <= 0.01:
            continue
        if l.carencia_ate and data_fim < l.carencia_ate:
            return -1e18
        total_liq += l.saldo_bruto * l.get_fator_liquido(data_fim)
    return total_liq

def get_score_economico(lote: Lote, data_hoje: date, dias_cliff: int = 10) -> float:
    dias = (data_hoje - lote.data_aplicacao).days
    if dias < 30:
        return 1e9 + (30 - dias)

    fator = lote.get_fator_liquido(data_hoje)
    if fator <= 0.001:
        return 1e9

    custo_fiscal = 1.0 / fator
    penalidade_cliff = 0.0
    for threshold, info in sorted(IR_FAIXAS.items()):
        if dias < threshold:
            dias_ate = threshold - dias
            if dias_ate <= dias_cliff:
                ratio_lucro = max(0.0, 1.0 - (1.0 / lote.fator_acumulado)) if lote.fator_acumulado > 1 else 0.0
                delta = float(info.get('delta', 0.0) or 0.0)
                urgencia = (dias_cliff - dias_ate + 1) / dias_cliff
                penalidade_cliff = ratio_lucro * delta * urgencia * 20.0
            break

    return custo_fiscal + penalidade_cliff

def validacao_walk_forward(
    aportes,
    contas,
    competidores_params,
    pct_treino=AVALIACAO_WF_PCT_TREINO,
    bcb_map=None,
    taxa_proj=None,
    n_splits=4,
    contas_por_estrategia=None,
    lotes_iniciais=None,
    data_inicio_competicao=None,
):
    print("\n" + "=" * 70)
    print("VALIDAÇÃO WALK-FORWARD ROBUSTA")
    print("=" * 70)

    if not contas:
        print("  -> Sem contas para validar.")
        return {}

    contas_ord_ref = sorted(contas, key=lambda x: x[0])
    n_total_ref = len(contas_ord_ref)
    if n_total_ref < max(12, n_splits * 2):
        print(f"  -> Dados insuficientes para validação robusta ({n_total_ref} contas).")
        return {}

    def _coerce_date(v):
        if v is None:
            return None
        if isinstance(v, pd.Timestamp):
            return v.date()
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, date):
            return v
        try:
            vv = pd.to_datetime(v, errors="coerce")
            if pd.isna(vv):
                return None
            return vv.date()
        except Exception:
            return None

    def _conta_data(conta):
        try:
            return _coerce_date(conta[0])
        except Exception:
            return None

    def _aporte_data(item):
        try:
            return _coerce_date(item[0])
        except Exception:
            return None

    def _filtrar_aportes_intervalo(aportes_base, data_ini=None, data_fim=None):
        saida = []
        for ap in list(aportes_base or []):
            dt = _aporte_data(ap)
            if dt is None:
                continue
            if data_ini is not None and dt < data_ini:
                continue
            if data_fim is not None and dt > data_fim:
                continue
            saida.append(ap)
        return saida

    def _somar_aportes(aportes_base):
        total = 0.0
        for ap in list(aportes_base or []):
            try:
                total += float(ap[1] or 0.0)
            except Exception:
                pass
        return total

    def _somar_contas(contas_base):
        total = 0.0
        for c in list(contas_base or []):
            try:
                total += float(c[1] or 0.0)
            except Exception:
                pass
        return total

    def _saldo_liquido_base_fold(lotes_base, data_ref):
        total = 0.0
        for item in list(lotes_base or []):
            if item is None:
                continue

            if isinstance(item, (tuple, list)):
                try:
                    total += float(item[1] or 0.0)
                    continue
                except Exception:
                    continue

            try:
                saldo = float(getattr(item, 'saldo_bruto', 0.0) or 0.0)
                esgotado = bool(getattr(item, 'esgotado', False))
                if esgotado or saldo <= VALOR_MINIMO_LOTE_ATIVO:
                    continue

                fator = float(item.get_fator_liquido(data_ref) or 0.0)
                if not np.isfinite(fator) or fator <= 0.0:
                    fator = 1.0

                total += saldo * fator
            except Exception:
                continue

        return float(total)

    def _baseline_neutro_fold(lotes_base, aportes_base, contas_base, data_ref):
        saldo_ini = _saldo_liquido_base_fold(lotes_base, data_ref)
        total_aportes = _somar_aportes(aportes_base)
        total_contas = _somar_contas(contas_base)

        recursos = float(saldo_ini + total_aportes)
        baseline = max(float(recursos - total_contas), 0.0)
        return baseline, recursos

    if not (0.0 < float(pct_treino) < 1.0):
        pct_treino = AVALIACAO_WF_PCT_TREINO

    tamanho_teste_ref = max(1, int(round(n_total_ref * (1.0 - float(pct_treino)))))
    tamanho_teste_ref = min(tamanho_teste_ref, max(1, n_total_ref // 2))

    print(
        f"  Total contas (referência): {n_total_ref} | Splits: {n_splits} | "
        f"Pct treino: {pct_treino:.2%} | Janela teste ref: {tamanho_teste_ref}\n"
    )

    resultados_wf = {}

    for nome, params in competidores_params:
        try:
            contas_base = (contas_por_estrategia or {}).get(nome, contas)
            contas_ord = sorted(contas_base, key=lambda x: x[0])
            n_total = len(contas_ord)

            if n_total < max(12, n_splits * 2):
                print(f"  {nome:<20} [AVISO] contas insuficientes ({n_total})")
                continue

            tamanho_teste = max(1, int(round(n_total * (1.0 - float(pct_treino)))))
            tamanho_teste = min(tamanho_teste, max(1, n_total // 2))

            liq_adj_treino = []
            liq_adj_teste = []
            excesso_rel_treino = []
            excesso_rel_teste = []
            baseline_treino = []
            baseline_teste = []
            folds_validos = 0

            for i in range(1, n_splits + 1):
                fim_teste = n_total - (n_splits - i) * tamanho_teste
                ini_teste = max(1, fim_teste - tamanho_teste)

                contas_treino = contas_ord[:ini_teste]
                contas_teste = contas_ord[ini_teste:fim_teste]

                if not contas_treino or not contas_teste:
                    continue

                data_ini_treino = _conta_data(contas_treino[0])
                data_fim_treino = _conta_data(contas_treino[-1])
                data_ini_teste = _conta_data(contas_teste[0])
                data_fim_teste = _conta_data(contas_teste[-1])

                aportes_treino = _filtrar_aportes_intervalo(
                    aportes,
                    data_ini=data_inicio_competicao,
                    data_fim=data_fim_treino,
                )

                aportes_teste = _filtrar_aportes_intervalo(
                    aportes,
                    data_ini=data_ini_teste,
                    data_fim=data_fim_teste,
                )

                _, _, lotes_finais_treino, stats_tr = rodar_estrategia(
                    nome,
                    aportes_treino,
                    contas_treino,
                    params_opt=params,
                    bcb_map=bcb_map,
                    taxa_proj=taxa_proj,
                    lotes_iniciais=lotes_iniciais,
                    data_inicio_competicao=data_inicio_competicao,
                )

                _, _, _, stats_te = rodar_estrategia(
                    nome,
                    aportes_teste,
                    contas_teste,
                    params_opt=params,
                    bcb_map=bcb_map,
                    taxa_proj=taxa_proj,
                    lotes_iniciais=lotes_finais_treino,
                    data_inicio_competicao=data_ini_teste or data_inicio_competicao,
                )

                liq_tr = float(stats_tr.get("saldo_liquido_final", 0.0) or 0.0) - float(stats_tr.get("valor_nao_coberto", 0.0) or 0.0)
                liq_te = float(stats_te.get("saldo_liquido_final", 0.0) or 0.0) - float(stats_te.get("valor_nao_coberto", 0.0) or 0.0)

                baseline_tr, recursos_tr = _baseline_neutro_fold(
                    lotes_iniciais,
                    aportes_treino,
                    contas_treino,
                    data_ini_treino or data_inicio_competicao,
                )

                baseline_te, recursos_te = _baseline_neutro_fold(
                    lotes_finais_treino,
                    aportes_teste,
                    contas_teste,
                    data_ini_teste or data_fim_treino or data_inicio_competicao,
                )

                excesso_tr = (liq_tr - baseline_tr) / (max(abs(recursos_tr), 1e-9))
                excesso_te = (liq_te - baseline_te) / (max(abs(recursos_te), 1e-9))

                liq_adj_treino.append(liq_tr)
                liq_adj_teste.append(liq_te)
                baseline_treino.append(baseline_tr)
                baseline_teste.append(baseline_te)
                excesso_rel_treino.append(excesso_tr)
                excesso_rel_teste.append(excesso_te)
                folds_validos += 1

            if not excesso_rel_teste or folds_validos == 0:
                continue

            ef_treino = float(np.mean(excesso_rel_treino))
            ef_teste = float(np.mean(excesso_rel_teste))

            delta_ef = ((ef_treino - ef_teste) / (abs(ef_treino) + 1e-9)) * 100.0
            delta_ef_abs = abs(delta_ef)

            cv_excesso = float(np.std(excesso_rel_teste) / (abs(np.mean(excesso_rel_teste)) + 1e-9))
            score_robustez = max(0.0, 100.0 - delta_ef_abs - (cv_excesso * 25.0))

            resultados_wf[nome] = {
                "ef_treino": ef_treino,
                "ef_teste": ef_teste,
                "delta_ef": delta_ef,
                "delta_ef_abs": delta_ef_abs,
                "cv_excesso_teste": cv_excesso,
                "cv_liquido_teste": cv_excesso,
                "score_robustez": score_robustez,
                "saldo_liquido_teste_medio": float(np.mean(liq_adj_teste)),
                "baseline_teste_medio": float(np.mean(baseline_teste)),
                "excesso_rel_teste_medio": float(np.mean(excesso_rel_teste)),
                "folds_validos": int(folds_validos),
            }

            status = "⚠️ overfit" if delta_ef_abs > 2.0 else "✓ ok"
            print(
                f"  {nome:<20} ExRel tr={ef_treino:.4%} | ExRel te={ef_teste:.4%} | "
                f"Δ%={delta_ef:.2f} | |Δ|%={delta_ef_abs:.2f} | CVexc={cv_excesso:.3f} | "
                f"robustez={score_robustez:.2f} | folds={folds_validos} | {status}"
            )

        except Exception as e:
            print(f"  {nome:<20} [ERRO] {e}")

    if resultados_wf:
        print("\n  Top robustez:")
        for nome, data in sorted(resultados_wf.items(), key=lambda x: x[1]["score_robustez"], reverse=True)[:5]:
            print(
                f"   - {nome}: score={data['score_robustez']:.2f}, "
                f"excesso_teste={data['excesso_rel_teste_medio']:.4%}, "
                f"liq_teste={data['saldo_liquido_teste_medio']:,.2f}"
            )

    return resultados_wf

def get_score_economico_vpl(lote, data_hoje, data_final_horizonte, taxa_desconto_diaria, dias_cliff=10):
    score_base = get_score_economico(lote, data_hoje, dias_cliff)
    if score_base >= 1e8:
        return score_base

    dias_restantes = (data_final_horizonte - data_hoje).days
    if dias_restantes <= 0:
        return score_base

    fator_crescimento = ((1.0 + taxa_desconto_diaria) ** TAXA_BASE_DEFAULT) ** dias_restantes

    dias_total = (data_final_horizonte - lote.data_base_fiscal).days
    ir_fut = obter_aliquota_ir(dias_total)

    fat_acum_fut = lote.fator_acumulado * fator_crescimento
    ratio_luc_fut = max(0.0, 1.0 - (1.0 / fat_acum_fut)) if fat_acum_fut > 1 else 0.0
    fator_liq_fut = 1.0 - (ratio_luc_fut * ir_fut)
    valor_futuro_liquido = lote.saldo_bruto * fator_crescimento * fator_liq_fut
    valor_presente_liquido = valor_futuro_liquido / ((1 + taxa_desconto_diaria) ** dias_restantes)
    valor_agora_liquido = lote.saldo_bruto * lote.get_fator_liquido(data_hoje)

    diferenca_vpl = valor_presente_liquido - valor_agora_liquido
    return score_base - (diferenca_vpl / max(lote.saldo_bruto, 1.0))

def simular_pagamentos_com_produto(produto, data_inicio: date,
                                   valor_inicial: float, contas: list,
                                   bcb_map: dict, data_base: date = None) -> float:
    if data_base is None:
        data_base = data_inicio

    if isinstance(produto, ComboProduto):
        val_base, val_bonus = produto.dividir_valor(valor_inicial)
        if val_base <= 0 and val_bonus <= 0:
            return -1e18

        car_b = data_inicio + timedelta(days=produto.produto_base.carencia_dias) if produto.produto_base.carencia_dias > 0 else None
        car_x = data_inicio + timedelta(days=produto.produto_bonus.carencia_dias) if produto.produto_bonus.carencia_dias > 0 else None
        l_base = Lote("VIRTUAL_BASE", data_inicio, val_base, produto=produto.produto_base,
                      carencia_ate=car_b, data_base_fiscal=data_inicio)
        l_bonus = Lote("VIRTUAL_BONUS", data_inicio, val_bonus, produto=produto.produto_bonus,
                       carencia_ate=car_x, data_base_fiscal=data_inicio)

        lotes = [l_base, l_bonus]
        contas_ord = sorted([c for c in contas if c[0] >= data_inicio], key=lambda x: x[0])

        data_cur = data_inicio
        total_pago = 0.0

        for conta_item in contas_ord:
            data_conta, valor_conta = conta_item[0], conta_item[1]
            d = data_cur
            while d < data_conta:
                if is_dia_rendimento(d, bcb_map):
                    atualizar_saldo_lotes_no_dia(lotes, d, bcb_map, TAXA_DIA_BASE)
                d += timedelta(days=1)
            data_cur = data_conta

            falta = float(valor_conta)
            disponiveis = [
                l for l in lotes
                if not l.esgotado
                and l.saldo_bruto > 0.01
                and l.data_aplicacao <= data_conta
                and not (l.carencia_ate and data_conta < l.carencia_ate)
            ]
            disponiveis.sort(key=lambda l: get_score_economico(l, data_conta))

            for l in disponiveis:
                if falta <= 0.001:
                    break
                fator = l.get_fator_liquido(data_conta)
                if fator <= 0:
                    continue
                bruto_nec = falta / fator
                uso = min(bruto_nec, l.saldo_bruto)
                efetivo = l.sacar(uso)
                liquido = efetivo * fator
                falta -= liquido

            if falta > 0.01:
                return -1e18
            total_pago += valor_conta

        data_fim = (contas_ord[-1][0] if contas_ord else data_inicio) + timedelta(days=HORIZONTE_EXTRA_DIAS)
        d = data_cur
        while d < data_fim:
            if is_dia_rendimento(d, bcb_map):
                atualizar_saldo_lotes_no_dia(lotes, d, bcb_map, TAXA_DIA_BASE)
            d += timedelta(days=1)

        saldo_liq = 0.0
        for l in lotes:
            if l.esgotado or l.saldo_bruto <= 0.01:
                continue
            fl = l.get_fator_liquido(data_fim)
            saldo_liq += l.saldo_bruto * fl

        return total_pago + saldo_liq

    saldo = float(valor_inicial)
    data_cur = data_inicio
    fator_acum = 1.0
    total_pago = 0.0

    contas_ord = sorted(contas, key=lambda x: x[0])

    for conta_item in contas_ord:
        data_conta, valor_conta = conta_item[0], conta_item[1]
        if data_conta < data_inicio:
            continue
        d = data_cur
        while d < data_conta:
            if is_dia_rendimento(d, bcb_map):
                idade = (d - data_base).days
                mult = produto.taxa_dia(idade)
                if mult > 0:
                    f = (1.0 + TAXA_DIA_BASE) ** float(mult)
                    saldo = round(saldo * f, 2)
                    fator_acum *= f
            d += timedelta(days=1)
        data_cur = data_conta

        dias_vida = (data_conta - data_base).days
        fl = _fator_liquido(fator_acum, dias_vida, produto.isento_ir)
        if fl <= 0:
            return -1e18
        bruto_nec = valor_conta / fl
        if bruto_nec > saldo + 0.01:
            return -1e18
        saldo -= bruto_nec
        total_pago += valor_conta

    if saldo > 0.01:
        data_fim = (contas_ord[-1][0] if contas_ord else data_inicio) + timedelta(days=HORIZONTE_EXTRA_DIAS)
        d = data_cur
        while d < data_fim:
            if is_dia_rendimento(d, bcb_map):
                idade = (d - data_base).days
                mult = produto.taxa_dia(idade)
                if mult > 0:
                    f = (1.0 + TAXA_DIA_BASE) ** float(mult)
                    saldo = round(saldo * f, 2)
                    fator_acum *= f
            d += timedelta(days=1)
        dias_fim = (data_fim - data_base).days
        fl_fim = _fator_liquido(fator_acum, dias_fim, produto.isento_ir)
        saldo_liq = saldo * fl_fim
    else:
        saldo_liq = 0.0

    return total_pago + saldo_liq

def gerar_top_planos_alocacao(data_ref: date, total_liq: float, produtos: list, bcb_map: dict, contas_fut: list, top_k: int = 6):
    total_liq = float(total_liq)
    if total_liq <= 0.01:
        return []

    candidatos = []
    for p in produtos:
        if not getattr(p, "ativo", True):
            continue
        if getattr(p, "somente_combo", False):
            continue
        candidatos.append(p)

    if not candidatos:
        return []

    score_map = {}
    for p in candidatos:
        sc = simular_valor_final_produto(p, data_ref, 1000.0, data_ref + timedelta(days=365), bcb_map, produtos_rolagem=produtos)
        if sc <= -1e17:
            sc = 0.0
        score_map[p] = max(0.0, sc / 1000.0)

    candidatos.sort(key=lambda p: score_map[p], reverse=True)

    def _score_plano(pl):
        return sum(
            simular_valor_final_produto(pp, data_ref, vv, data_ref + timedelta(days=365), bcb_map, produtos_rolagem=produtos)
            for pp, vv in pl if vv > 0.01
        )

    planos = []
    pl_best, _, _ = alocar_lote_por_otimizacao(data_ref, data_ref, total_liq, produtos, bcb_map, contas_fut, foco_rendimento=True, max_produtos=3)
    if pl_best:
        planos.append(pl_best)

    for p in candidatos[:10]:
        if p.aceita_aporte(total_liq):
            planos.append([(p, total_liq)])

    top = candidatos[:12]
    for p in top:
        vmax = float(getattr(p, "valor_max", 1e18) or 1e18)
        vmin = float(getattr(p, "valor_min", 0.0) or 0.0)
        aplicar = min(total_liq, vmax)
        if aplicar <= 0.01:
            continue
        if aplicar + 0.01 < vmin:
            continue
        resto = total_liq - aplicar
        if resto <= 0.01:
            planos.append([(p, aplicar)])
            continue
        for q in top:
            if q is p:
                continue
            if q.aceita_aporte(resto):
                planos.append([(p, aplicar), (q, resto)])
                break

    uniq = {}
    for pl in planos:
        key = _normalizar_plano(pl)
        if key not in uniq:
            uniq[key] = pl

    ranked = []
    for key, pl in uniq.items():
        try:
            sc = _score_plano(pl)
        except Exception:
            sc = -1e18
        ranked.append((sc, pl))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [pl for _, pl in ranked[:top_k]]

def alocar_lote_por_otimizacao(data_hoje, data_aporte, valor, produtos, bcb_map, contas_futuras, foco_rendimento: bool = False, max_produtos: int = None):
    valor = float(valor)

    contas_relevantes = sorted([c for c in contas_futuras if c[0] >= data_aporte], key=lambda x: x[0])
    data_h_exibicao = data_aporte + timedelta(days=365)

    candidatos = []
    for p in produtos:
        if not getattr(p, 'ativo', True):
            continue
        if getattr(p, 'somente_combo', False):
            continue
        candidatos.append(p)

    if not candidatos:
        return [], "", data_h_exibicao

    score_map = {}
    for p in candidatos:
        score = simular_valor_final_produto(
            p,
            data_aporte,
            1000.0,
            data_aporte + timedelta(days=365),
            bcb_map,
            produtos_rolagem=produtos,
        )
        if score <= -1e17:
            score = 0.0
        score_map[p] = max(0.0, score / 1000.0)

    candidatos.sort(key=lambda p: score_map[p], reverse=True)
    top_txt = ", ".join([f"{p.nome}: w{score_map[p]:.6f}" for p in candidatos[:3]])

    def _score_aloc(aloc_local):
        if not aloc_local:
            return -1e18
        total = 0.0
        for pp, vv in aloc_local:
            if vv <= 0.01:
                continue
            if not pp.aceita_aporte(vv):
                return -1e18
            v = simular_valor_final_produto(
                pp,
                data_aporte,
                vv,
                data_aporte + timedelta(days=365),
                bcb_map,
                produtos_rolagem=produtos,
            )
            if v <= -1e17:
                return -1e18
            total += v
        return total

    def _aloc_taxa_alta():
        candidatos_taxa = sorted(
            candidatos,
            key=lambda x: (float(score_map.get(x, 0.0) or 0.0), float(getattr(x, 'taxa_base', 1.0) or 1.0)),
            reverse=True,
        )
        melhores = []

        for pp in candidatos_taxa:
            if pp.aceita_aporte(valor):
                melhores.append([(pp, valor)])

        for pp in candidatos_taxa:
            vmax = float(getattr(pp, 'valor_max', 1e18) or 1e18)
            vmin = float(getattr(pp, 'valor_min', 0.0) or 0.0)
            aplicar = min(valor, vmax)
            if aplicar + 0.01 < vmin or aplicar <= 0.01:
                continue
            resto = valor - aplicar
            if resto <= 0.01:
                melhores.append([(pp, aplicar)])
                continue
            for qq in candidatos_taxa:
                if qq is pp:
                    continue
                if qq.aceita_aporte(resto):
                    melhores.append([(pp, aplicar), (qq, resto)])
                    break

        if not melhores:
            return []
        melhores.sort(key=lambda al: _score_aloc(al), reverse=True)
        return melhores[0]

    if PERMITIR_SPLIT_LOTE and valor >= 10000:
        aloc_pref = _aloc_taxa_alta()
    else:
        aloc_pref = []

    if not PERMITIR_SPLIT_LOTE:
        for p in candidatos:
            if p.capacidade_aporte(valor) >= valor:
                return [(p, valor)], top_txt, data_h_exibicao
        return [], top_txt, data_h_exibicao

    restante = valor
    aloc = []
    alocado_por_prod = {}

    limite_prod = max_produtos if max_produtos is not None else TOP_N_ALOCACAO
    while restante > 0.01 and len(aloc) < limite_prod:
        melhor_p = None
        melhor_score = -1.0
        melhor_aplicar = 0.0

        for p in candidatos:
            vmax = float(getattr(p, 'valor_max', 1e18) or 1e18)
            vmin = float(getattr(p, 'valor_min', 0.0) or 0.0)
            ja = alocado_por_prod.get(p.nome, 0.0)
            capacidade = max(0.0, vmax - ja)
            if capacidade <= 0.01:
                continue

            aplicar = min(restante, capacidade)
            if ja <= 0.01 and aplicar < vmin:
                continue

            conc = ja / max(valor, 1.0)
            taxa_pref = float(getattr(p, 'taxa_base', 1.0) or 1.0)
            bonus_cap = 0.00005 * max(0.0, taxa_pref - 1.0)
            score_eff = (score_map[p] * (1.0 - 0.35 * conc)) + bonus_cap
            if score_eff > melhor_score:
                melhor_score = score_eff
                melhor_p = p
                melhor_aplicar = aplicar

        if melhor_p is None or melhor_aplicar <= 0.01:
            break

        achou = False
        for i, (p_exist, v_exist) in enumerate(aloc):
            if p_exist.nome == melhor_p.nome:
                aloc[i] = (p_exist, v_exist + melhor_aplicar)
                achou = True
                break
        if not achou:
            aloc.append((melhor_p, melhor_aplicar))

        alocado_por_prod[melhor_p.nome] = alocado_por_prod.get(melhor_p.nome, 0.0) + melhor_aplicar
        restante -= melhor_aplicar

    if restante > 0.01 and aloc:
        p, v = aloc[0]
        vmax = float(getattr(p, 'valor_max', 1e18) or 1e18)
        extra = min(restante, max(0.0, vmax - v))
        if extra > 0.01:
            aloc[0] = (p, v + extra)
            restante -= extra

    if aloc_pref:
        score_pref = _score_aloc(aloc_pref)
        score_greedy = _score_aloc(aloc)
        limiar = 0.995 if foco_rendimento else 1.0001
        if score_pref > score_greedy * limiar:
            aloc = aloc_pref

    return aloc, top_txt, data_h_exibicao

def _fator_oportunidade_lote(lote, data_cur: date, data_fim: date) -> float:
    try:
        fator_liq_hoje = float(lote.get_fator_liquido(data_cur) or 0.0)
    except Exception:
        fator_liq_hoje = 0.0
    if fator_liq_hoje <= 1e-9:
        return 1e18

    valor_base = 1000.0
    try:
        produto_ref = lote.produto if lote.produto is not None else PRODUTO_PADRAO
        valor_final = simular_valor_final_produto(
            produto_ref,
            data_cur,
            valor_base,
            data_fim,
            globals().get('bcb_map_global', {}) or {},
            produtos_rolagem=(PRODUTOS_GLOBAIS_SIMULACAO or []),
        )
    except Exception:
        try:
            dias = max(0, (data_fim - data_cur).days)
        except Exception:
            dias = 0
        valor_final = valor_base * (1.0 + 0.0001 * dias)

    custo_por_real_liquido = float(valor_final) / max(valor_base * fator_liq_hoje, 1e-9)
    penalidade = float(get_score_economico(lote, data_cur)) * 1e-6
    return custo_por_real_liquido + penalidade

def montar_log_movimento_lote(movimento, data_atual, conta_desc, bcb_map=None, ordem_processamento=None, sequencia_saque=1, evento_financeiro=None):
    """Padroniza o log do movimento financeiro do lote."""
    lote = movimento['lote']
    desc_safe = str(conta_desc)[:100].encode('utf-8', 'replace').decode('utf-8')
    saldo_rem = float(movimento['saldo_remanescente'])
    status_lote_ordem = 0 if saldo_rem <= VALOR_MINIMO_LOTE_ATIVO else 1
    status_lote_texto = 'zerado' if status_lote_ordem == 0 else 'com_sobra'
    return {
        'Data': data_atual,
        'Conta': desc_safe,
        'Ordem Processamento': int(ordem_processamento) if ordem_processamento is not None else None,
        'Sequencia Saque': int(sequencia_saque),
        'Evento Financeiro': int(evento_financeiro) if evento_financeiro is not None else None,
        'Status Lote Ordem': int(status_lote_ordem),
        'Status Lote': status_lote_texto,
        'Lote': lote.id,
        'Saldo Antes': movimento['saldo_antes'],
        'Bruto': movimento['bruto'],
        'Imposto': movimento['imposto'],
        'Liquido': movimento['liquido'],
        'Dias Corridos': (data_atual - lote.data_base_fiscal).days,
        'Dias Úteis': contar_dias_rendimento(lote.data_base_fiscal, data_atual, bcb_map),
        'Saldo Remanescente': saldo_rem,
    }

def estimar_liquido_lote_sem_pagamentos(lote, data_ref, bcb_map=None):
    """Estima o valor líquido resgatável do lote em uma data sem alterar o estado do objeto."""
    try:
        saldo_bruto = float(getattr(lote, "saldo_bruto", 0.0) or 0.0)
        if saldo_bruto <= 0.0:
            return 0.0
        fator_liquido = float(lote.get_fator_liquido(data_ref))
        if fator_liquido <= 0.0:
            return 0.0
        return max(0.0, saldo_bruto * fator_liquido)
    except Exception:
        return max(0.0, float(getattr(lote, "saldo_bruto", 0.0) or 0.0))

def calcular_saldo_atual_lotes(lotes, data_saldo):
    lotes_validos = [
        l for l in lotes
        if not getattr(l, "esgotado", False) and float(getattr(l, "saldo_bruto", 0.0) or 0.0) > VALOR_MINIMO_LOTE_ATIVO
    ]
    detalhes = []
    saldo_bruto_total = 0.0
    saldo_liquido_total = 0.0

    for lote in lotes_validos:
        saldo_bruto = float(round(float(getattr(lote, "saldo_bruto", 0.0) or 0.0), 2))
        fator_liquido = float(lote.get_fator_liquido(data_saldo))
        saldo_liquido = float(round(saldo_bruto * fator_liquido, 2))

        detalhes.append({
            "id_lote": getattr(lote, "id", None),
            "data_aplicacao": getattr(lote, "data_aplicacao", None),
            "data_base_fiscal": getattr(lote, "data_base_fiscal", None),
            "saldo_bruto": saldo_bruto,
            "fator_liquido": fator_liquido,
            "saldo_liquido": saldo_liquido,
            "fator_acumulado": float(getattr(lote, "fator_acumulado", 1.0) or 1.0),
            "taxa_base_cdi": float(getattr(lote, "taxa_base_cdi", 1.0) or 1.0),
            "taxa_bonus_cdi": float(getattr(lote, "taxa_bonus_cdi", 0.0) or 0.0),
            "dias_bonus": int(getattr(lote, "dias_bonus", 0) or 0),
        })

        saldo_bruto_total += saldo_bruto
        saldo_liquido_total += saldo_liquido

    return {
        "data_saldo": data_saldo,
        "saldo_bruto_total": float(round(saldo_bruto_total, 2)),
        "saldo_liquido_total": float(round(saldo_liquido_total, 2)),
        "detalhes_lotes": detalhes,
        "num_lotes_ativos": len(lotes_validos),
    }

def _lote_nao_investivel_mesmo_dia(lote, data_ref):
    produto = getattr(lote, "produto", None)
    investimento_nome = str(getattr(produto, "nome", "-") if produto is not None else "-").strip()
    return (
        investimento_nome in {"", "-", "—", "–"}
        and getattr(lote, "data_aplicacao", None) == data_ref
    )

def _datas_candidatas_switch(lote: Lote, contas_fut: list, data_hoje: date) -> list:
    dias_iof_fim = max(0, 30 - (data_hoje - lote.data_base_fiscal).days)
    janela = max(SWITCH_BUSCA_DIAS, dias_iof_fim)
    data_min_sw = data_hoje
    nome_atual = (lote.produto.nome.lower() if lote.produto else "")
    if (not PERMITIR_SWITCH_ANTES_30_DIAS) and ("turbinado" in nome_atual or "padr" in nome_atual):
        data_min_sw = max(data_hoje, lote.data_base_fiscal + timedelta(days=30))
    datas_diarias = {data_min_sw + timedelta(days=i) for i in range(0, janela + 1)}
    datas_contas = {c[0] for c in contas_fut if c[0] >= data_min_sw}
    datas_cliff = set()
    for k in (30, 180, 360, 720):
        d = lote.data_base_fiscal + timedelta(days=k)
        if d >= data_hoje:
            datas_cliff.add(d)
    datas_cliff = {d for d in datas_cliff if d >= data_min_sw}
    return sorted(datas_contas | datas_diarias | datas_cliff)

def _estado_lote_ate_switch(lote: Lote, contas_fut: list, bcb_map: dict, data_hoje: date, data_sw: date):
    contas_ate = [c for c in contas_fut if c[0] <= data_sw]
    contas_depois = [c for c in contas_fut if c[0] > data_sw]

    saldo = lote.saldo_bruto
    data_cur = data_hoje
    fa = lote.fator_acumulado
    total_pago_ate = 0.0

    for conta_item in contas_ate:
        data_c, valor_c = conta_item[0], conta_item[1]
        d = data_cur
        while d < data_c:
            if is_dia_rendimento(d, bcb_map):
                idade = (d - lote.data_base_fiscal).days
                mult = lote.produto.taxa_dia(idade)
                if mult > 0:
                    f_dia = (1.0 + TAXA_DIA_BASE) ** float(mult)
                    saldo = round(saldo * f_dia, 2)
                    fa *= f_dia
            d += timedelta(days=1)
        data_cur = data_c

        fl = _fator_liquido(fa, (data_c - lote.data_base_fiscal).days, lote.produto.isento_ir)
        if fl <= 0:
            return None
        bruto_nec = valor_c / fl
        if bruto_nec > saldo + 0.01:
            return None
        saldo -= bruto_nec
        total_pago_ate += valor_c

    d = data_cur
    while d < data_sw:
        if is_dia_rendimento(d, bcb_map):
            idade = (d - lote.data_base_fiscal).days
            mult = lote.produto.taxa_dia(idade)
            if mult > 0:
                f_dia = (1.0 + TAXA_DIA_BASE) ** float(mult)
                saldo = round(saldo * f_dia, 2)
                fa *= f_dia
        d += timedelta(days=1)

    dias_sw = (data_sw - lote.data_base_fiscal).days
    fl_sw = _fator_liquido(fa, dias_sw, lote.produto.isento_ir)
    if fl_sw <= 0:
        return None
    liquido_sw = saldo * fl_sw
    return (liquido_sw, total_pago_ate, contas_depois)

def avaliar_switch_lote(lote: Lote, contas: list, produtos: list,
                         bcb_map: dict, data_hoje: date, preferred_datas: set = None,
                         top_k: int = 3):
    if lote.produto is None:
        return []

    contas_fut = sorted([c for c in contas if c[0] >= data_hoje], key=lambda x: x[0])
    datas_teste = _datas_candidatas_switch(lote, contas_fut, data_hoje)

    pref_set = set(preferred_datas) if preferred_datas else set()
    if pref_set:
        try:
            datas_teste = sorted(set(datas_teste) | pref_set)
        except Exception:
            pass

    try:
        v_base = simular_valor_final_produto(
            lote.produto, data_hoje, float(lote.saldo_bruto),
            data_hoje + timedelta(days=365), bcb_map, produtos_rolagem=produtos
        )
    except Exception:
        v_base = float(lote.saldo_bruto)

    cands = []

    for data_sw in datas_teste:
        try:
            base_hold = lote.data_aplicacao
            try:
                base_fiscal = getattr(lote, "data_base_fiscal", None)
                if base_fiscal:
                    base_hold = max(base_hold, base_fiscal)
            except Exception:
                pass
            if base_hold and (data_sw - base_hold).days < int(SWITCH_MIN_HOLD_DIAS):
                continue
        except Exception:
            pass
        estado = _estado_lote_ate_switch(lote, contas_fut, bcb_map, data_hoje, data_sw)
        if estado is None:
            continue
        liquido_sw, total_pago_ate, _contas_depois = estado

        if liquido_sw <= 0.01:
            continue

        aloc, _, _ = alocar_lote_por_otimizacao(
            data_hoje, data_sw, liquido_sw, produtos, bcb_map, contas_fut,
            foco_rendimento=True, max_produtos=3
        )
        if not aloc:
            continue

        v_fut = 0.0
        for pp, vv in aloc:
            try:
                vpp = simular_valor_final_produto(
                    pp, data_sw, float(vv),
                    data_sw + timedelta(days=365), bcb_map, produtos_rolagem=produtos
                )
            except Exception:
                vpp = float(vv)
            v_fut += float(vpp)

        score = float(total_pago_ate) + float(v_fut)

        aloc_sorted = sorted(aloc, key=lambda x: float(x[1]), reverse=True)
        prod_repr = aloc_sorted[0][0]

        try:
            taxa_origem = taxa_base_efetiva(lote.produto)
            taxa_dest = taxa_base_efetiva(prod_repr)
            if not (taxa_dest > taxa_origem * (1.0 + float(SWITCH_MIN_UPGRADE_REL))):
                continue
        except Exception:
            pass

        if (score > float(v_base) * (1 + SWITCHING_LIMIAR_GANHO)) or (data_sw in pref_set):
            cands.append((score, data_sw, prod_repr))

    if not cands:
        return []

    cands.sort(key=lambda x: float(x[0]), reverse=True)
    seen = set()
    out = []
    for sc, dd, pp in cands:
        key = (dd, getattr(pp, "nome", str(pp)))
        if key in seen:
            continue
        seen.add(key)
        out.append((float(sc), dd, pp))
        if len(out) >= max(1, int(top_k)):
            break
    return out

def gerar_diagnostico_switches_portfolio(lotes_base: list, contas: list, produtos: list, bcb_map: dict, hoje: date,
                                        janela_datas: int = 7, top_k: int = 5):
    lotes_ref = copy.deepcopy(lotes_base)
    _, met_ref = simular_futuro(lotes_ref, contas, bcb_map, data_inicio=hoje, produtos=produtos, verbose=False)
    riqueza_ref = float(met_ref.get('riqueza', 0.0))

    lotes_switch = [l for l in lotes_base if (not l.esgotado and getattr(l, 'switch_agendado', None))]
    diag_datas = []
    diag_planos = []

    for l0 in lotes_switch:
        lid = l0.id
        data_sw, prod_alvo = l0.switch_agendado
        datas_cand = []
        for k in range(-janela_datas, janela_datas + 1):
            d = data_sw + timedelta(days=k)
            if d < hoje:
                continue
            if not PERMITIR_SWITCH_ANTES_30_DIAS and (d - l0.data_aplicacao).days < 30:
                continue
            datas_cand.append(d)

        resultados_data = []
        for d in datas_cand:
            lotes_cen = copy.deepcopy(lotes_base)
            mapa = {x.id: x for x in lotes_cen}
            if lid not in mapa:
                continue
            mapa[lid].switch_agendado = (d, prod_alvo)
            liq_est = max(0.0, estimar_liquido_lote_sem_pagamentos(mapa[lid], d, bcb_map))
            contas_fut = [c for c in contas if c[0] >= d]
            mapa[lid].switch_plano = gerar_top_planos_alocacao(d, liq_est, produtos, bcb_map, contas_fut, top_k=1)[0] if liq_est > 0.01 else None

            _, met = simular_futuro(lotes_cen, contas, bcb_map, data_inicio=hoje, produtos=produtos, verbose=False)
            riqueza = float(met.get('riqueza', 0.0))
            resultados_data.append((riqueza, d))

        resultados_data.sort(key=lambda x: x[0], reverse=True)
        for rank, (riqueza, d) in enumerate(resultados_data[:top_k], 1):
            diag_datas.append({
                'Lote ID': lid,
                'Produto Alvo': prod_alvo.nome if prod_alvo else '',
                'Data Avaliada': d,
                'Rank (Data)': rank,
                'Riqueza Cenário': riqueza,
                'Delta vs Escolhida': riqueza - riqueza_ref,
                'Data Escolhida': data_sw,
                'Riqueza Escolhida': riqueza_ref,
            })

        liq_est0 = max(0.0, estimar_liquido_lote_sem_pagamentos(l0, data_sw, bcb_map))
        contas_fut0 = [c for c in contas if c[0] >= data_sw]
        planos_top = gerar_top_planos_alocacao(data_sw, liq_est0, produtos, bcb_map, contas_fut0, top_k=top_k)

        resultados_plano = []
        for pl in planos_top:
            lotes_cen = copy.deepcopy(lotes_base)
            mapa = {x.id: x for x in lotes_cen}
            if lid not in mapa:
                continue
            mapa[lid].switch_agendado = (data_sw, prod_alvo)
            mapa[lid].switch_plano = pl
            _, met = simular_futuro(lotes_cen, contas, bcb_map, data_inicio=hoje, produtos=produtos, verbose=False)
            riqueza = float(met.get('riqueza', 0.0))
            resultados_plano.append((riqueza, pl))

        resultados_plano.sort(key=lambda x: x[0], reverse=True)
        for rank, (riqueza, pl) in enumerate(resultados_plano[:top_k], 1):
            diag_planos.append({
                'Lote ID': lid,
                'Data Switch': data_sw,
                'Rank (Plano)': rank,
                'Riqueza Cenário': riqueza,
                'Delta vs Escolhida': riqueza - riqueza_ref,
                'Plano (Produto=Valor)': "; ".join([f"{pp.nome if hasattr(pp,'nome') else str(pp)}={float(vv):,.2f}" for pp, vv in pl]),
                'Riqueza Escolhida': riqueza_ref,
            })

    return diag_datas, diag_planos, riqueza_ref

def simular_passado(
    aportes_raw: list,
    contas_pagas: list,
    bcb_map: dict,
    lote_produto: dict,
    data_referencia_snapshot: date = None,
):
    params_hibrido_passado, origem_params_hibrido_passado = carregar_parametros_hibrido_5p_passado()
    _log_debug(f">>> [PASSADO-HIBRIDO] parâmetros locais carregados de: {origem_params_hibrido_passado}", DEBUG_DOWNLOADS)

    lotes_por_id = {}
    for d, val, lid, ja_aplicado in aportes_raw:
        produto_lote = lote_produto.get(str(lid).strip())
        meta_lote = {
            "produto": produto_lote,
            "investimento": getattr(produto_lote, "nome", "-") if produto_lote is not None else "-",
            "data_base_fiscal": d,
            "fator_acumulado_inicial": 1.0,
            "taxa_base_cdi": float(
                getattr(produto_lote, "taxa_base", TAXA_BASE_DEFAULT)
                if produto_lote is not None else TAXA_BASE_DEFAULT
            ),
            "taxa_bonus_cdi": float(
                getattr(produto_lote, "taxa_bonus", TAXA_BONUS_DEFAULT)
                if produto_lote is not None else TAXA_BONUS_DEFAULT
            ),
            "dias_bonus": int(
                getattr(produto_lote, "dias_bonus", DIAS_BONUS_DEFAULT)
                if produto_lote is not None else DIAS_BONUS_DEFAULT
            ),
            "principal_remanescente": float(val),
            "carencia_ate": (
                d + timedelta(days=int(getattr(produto_lote, "carencia_dias", 0) or 0))
            ) if produto_lote is not None and int(getattr(produto_lote, "carencia_dias", 0) or 0) > 0 else None,
        }
        lote = criar_lote_de_aporte(d, val, str(lid).strip(), meta_lote)
        lote.data_efetiva_snapshot_lote = d
        lotes_por_id[lote.id] = lote

    contas_pagas = ordenar_contas_processamento(contas_pagas)
    log_passado = []
    auditoria_fina_rows = []
    tolerancia_zeramento = max(float(globals().get("VALOR_MINIMO_LOTE_ATIVO", 0.01) or 0.01), 5.0)

    if not lotes_por_id:
        return [], [], pd.DataFrame(), pd.DataFrame()

    if not contas_pagas:
        lotes_final = list(lotes_por_id.values())
        data_snapshot = data_referencia_snapshot or min(getattr(l, "data_aplicacao", None) for l in lotes_final)
        estado_lotes_passado = pd.DataFrame([
            serializar_lote_remanescente(l, data_snapshot)
            for l in lotes_final
        ])
        return lotes_final, [], estado_lotes_passado, pd.DataFrame()

    data_inicial = min(l.data_aplicacao for l in lotes_por_id.values())
    ultima_conta_paga = max(c[0] for c in contas_pagas)
    data_final = ultima_conta_paga if data_referencia_snapshot is None else data_referencia_snapshot

    contas_por_data = {}
    for conta in contas_pagas:
        contas_por_data.setdefault(conta[0], []).append(conta)

    data_atual = data_inicial
    while data_atual <= data_final:
        auditoria_dia = {}
        lotes_com_evento_no_dia = set()

        # Auditorias específicas por lote foram removidas desta base unificada.

        lotes_legados_explicitos_do_dia = set()
        for conta_item_scan in contas_por_data.get(data_atual, []):
            _dscan, _vscan, _descan, _l1scan, _l2scan, _oscan = _normalizar_conta_processamento(conta_item_scan)
            if _l1scan and str(_l1scan).strip() and str(_l1scan).lower() != "nan":
                lotes_legados_explicitos_do_dia.add(str(_l1scan).strip())
            if _l2scan and str(_l2scan).strip() and str(_l2scan).lower() != "nan":
                lotes_legados_explicitos_do_dia.add(str(_l2scan).strip())

        if is_dia_rendimento(data_atual, bcb_map):
            taxa_dia_atual = (float(bcb_map[data_atual]) - 1.0) if (bcb_map and data_atual in bcb_map) else float(TAXA_DIA_BASE)

            for l in lotes_por_id.values():
                if not l.esgotado and l.saldo_bruto > 0 and l.data_aplicacao <= data_atual and l.id in auditoria_dia:
                    mult = float(l.get_taxa_dia(data_atual))
                    fator_dia = (1.0 + taxa_dia_atual) ** float(mult) if mult > 0 else 1.0
                    auditoria_dia[l.id]["Multiplicador CDI no Dia"] = mult
                    auditoria_dia[l.id]["Fator Diário Aplicado"] = float(fator_dia)

            lotes_para_capitalizar_antes = [
                l for l in lotes_por_id.values()
                if str(getattr(l, "id", "")).strip() not in lotes_legados_explicitos_do_dia
            ]
            atualizar_saldo_lotes_no_dia(lotes_para_capitalizar_antes, data_atual, bcb_map, TAXA_DIA_BASE)

            for l in lotes_para_capitalizar_antes:
                if not l.esgotado and l.saldo_bruto > 0 and l.data_aplicacao <= data_atual:
                    lotes_com_evento_no_dia.add(l.id)
                    l.data_efetiva_snapshot_lote = data_atual
                    if l.id in auditoria_dia:
                        auditoria_dia[l.id]["Saldo Após Capitalização"] = dinheiro_round(float(getattr(l, "saldo_bruto", 0.0) or 0.0))

        lotes_usados_no_dia = set()
        lotes_nao_investiveis_usados_no_mesmo_dia = set()

        for conta_item in contas_por_data.get(data_atual, []):
            data, valor, desc, lote1, lote2, ordem_processamento = _normalizar_conta_processamento(conta_item)
            falta = float(valor)

            lotes_usados = []
            if lote1 and str(lote1).strip() and str(lote1).lower() != "nan":
                lotes_usados.append(str(lote1).strip())
            if lote2 and str(lote2).strip() and str(lote2).lower() != "nan":
                lotes_usados.append(str(lote2).strip())

            disponiveis = [
                l for l in lotes_por_id.values()
                if (not l.esgotado)
                and float(getattr(l, "saldo_bruto", 0.0) or 0.0) > 0.01
                and getattr(l, "data_aplicacao", data_atual) <= data_atual
                and not (getattr(l, "carencia_ate", None) and data_atual < getattr(l, "carencia_ate"))
            ]

            disponiveis_admissiveis = (
                [l for l in disponiveis if str(getattr(l, "id", "")).strip() in set(lotes_usados)]
                if lotes_usados else list(disponiveis)
            )

            saques_planejados = []

            if (not lotes_usados) and params_hibrido_passado is not None and disponiveis_admissiveis:
                valores_otimos = resolver_hibrido_5p(
                    disponiveis_admissiveis,
                    float(falta),
                    data_atual,
                    params_hibrido_passado,
                    data_final,
                    bcb_map,
                    TAXA_DIA_BASE,
                )
                candidatos_hibrido_rows = diagnosticar_resolvedor_hibrido_5p(
                    disponiveis_admissiveis,
                    float(falta),
                    data_atual,
                    params_hibrido_passado,
                    data_final,
                    valores_otimos=valores_otimos,
                    bcb_map=bcb_map,
                    taxa_proj=TAXA_DIA_BASE,
                )
                lote_foco_escolhido = False
                for rr in candidatos_hibrido_rows:
                    rr["Conta"] = desc
                    rr["Valor Conta"] = dinheiro_round(float(valor))
                    rr["Falta Inicial"] = dinheiro_round(float(falta))
                    rr["Ordem Processamento"] = int(ordem_processamento)
                    rr["Conta Key"] = f"{data_atual.isoformat()}|{int(ordem_processamento):04d}|{desc}|{dinheiro_round(float(valor)):.2f}"

                valor_minimo_resgate_bruto = float(globals().get("VALOR_MINIMO_RESGATE_BRUTO", 0.0) or 0.0)
                for lote_ref, val_bruto in zip(disponiveis_admissiveis, valores_otimos):
                    if float(val_bruto or 0.0) > valor_minimo_resgate_bruto:
                        saques_planejados.append(
                            (lote_ref, min(float(val_bruto), float(lote_ref.saldo_bruto)), "hibrido")
                        )
            else:
                for id_lote in lotes_usados:
                    if falta <= 0.001:
                        break
                    l = lotes_por_id.get(id_lote)
                    if not l or l.esgotado:
                        continue
                    liquido_max_lote = _money_round_half_up(float(l.valor_liquido_hoje(data_atual) or 0.0))
                    if liquido_max_lote <= 0:
                        continue
                    saques_planejados.append((l, None, "legacy"))

            for item in saques_planejados:
                if falta <= 0.001:
                    break

                l, val_b, modo_saque = item if len(item) == 3 else (item[0], item[1], "hibrido")
                lotes_usados_no_dia.add(l.id)
                if _lote_nao_investivel_mesmo_dia(l, data_atual):
                    lotes_nao_investiveis_usados_no_mesmo_dia.add(l.id)

                if modo_saque == "legacy":
                    valor_liquido_alvo = min(
                        _money_round_half_up(float(falta)),
                        _money_round_half_up(float(l.valor_liquido_hoje(data_atual) or 0.0)),
                    )
                    if valor_liquido_alvo <= 0:
                        continue
                    movimento = executar_saque_lote(l, valor_liquido_alvo, data_atual)
                else:
                    fator = l.get_fator_liquido(data_atual)
                    if fator <= 0:
                        continue
                    valor_liquido_alvo = round(float(val_b) * float(fator), 2)
                    valor_liquido_alvo = min(valor_liquido_alvo, round(float(falta), 2))
                    movimento = executar_saque_lote(l, valor_liquido_alvo, data_atual)

                if movimento is None:
                    continue

                saldo_antes = float(movimento["saldo_antes"])
                principal_remanescente_antes = float(
                    movimento.get("principal_remanescente_antes", getattr(l, "principal_remanescente", 0.0)) or 0.0
                )
                efetivo = float(movimento["bruto"])
                liquido = float(movimento["liquido"])
                imposto = float(movimento["imposto"])
                falta -= liquido

                dias_corridos = (data_atual - l.data_aplicacao).days
                dias_uteis = contar_dias_rendimento(l.data_aplicacao, data_atual, bcb_map)

                lotes_com_evento_no_dia.add(l.id)
                l.data_efetiva_snapshot_lote = data_atual

                log_passado.append({
                    "Data": data_atual,
                    "Conta": desc,
                    "Lote": l.id,
                    "Saldo Antes": saldo_antes,
                    "Bruto": efetivo,
                    "Imposto": imposto,
                    "Liquido": liquido,
                    "Dias Corridos": dias_corridos,
                    "Dias Úteis": dias_uteis,
                    "Saldo Remanescente": float(movimento["saldo_remanescente"]),
                })

                if l.id in auditoria_dia:
                    auditoria_dia[l.id]["Saque Bruto no Dia"] = dinheiro_round(float(auditoria_dia[l.id]["Saque Bruto no Dia"]) + float(efetivo))
                    auditoria_dia[l.id]["Saque Líquido no Dia"] = dinheiro_round(float(auditoria_dia[l.id]["Saque Líquido no Dia"]) + float(liquido))
                    auditoria_dia[l.id]["Imposto no Dia"] = dinheiro_round(float(auditoria_dia[l.id]["Imposto no Dia"]) + float(imposto))

            tolerancia_residual = float(globals().get("TOLERANCIA_AJUSTE_RESIDUAL_CONTA", 0.0) or 0.0)
            if lotes_usados and falta > 0.0001 and float(falta) <= tolerancia_residual:
                for id_lote_res in reversed(lotes_usados):
                    if falta <= 0.0001:
                        break
                    lres = lotes_por_id.get(id_lote_res)
                    if not lres or getattr(lres, "esgotado", False):
                        continue
                    liquido_max_res = _money_round_half_up(float(lres.valor_liquido_hoje(data_atual) or 0.0))
                    if liquido_max_res <= 0:
                        continue
                    alvo_residual = min(_money_round_half_up(float(falta)), liquido_max_res)
                    if alvo_residual <= 0:
                        continue
                    movimento_residual = executar_saque_lote(lres, alvo_residual, data_atual)
                    if movimento_residual is None:
                        continue

                    saldo_antes_res = float(movimento_residual["saldo_antes"])
                    efetivo_res = float(movimento_residual["bruto"])
                    liquido_res = float(movimento_residual["liquido"])
                    imposto_res = float(movimento_residual["imposto"])
                    falta -= liquido_res

                    dias_corridos_res = (data_atual - lres.data_aplicacao).days
                    dias_uteis_res = contar_dias_rendimento(lres.data_aplicacao, data_atual, bcb_map)

                    lotes_com_evento_no_dia.add(lres.id)
                    lres.data_efetiva_snapshot_lote = data_atual
                    log_passado.append({
                        "Data": data_atual,
                        "Conta": desc,
                        "Lote": lres.id,
                        "Saldo Antes": saldo_antes_res,
                        "Bruto": efetivo_res,
                        "Imposto": imposto_res,
                        "Liquido": liquido_res,
                        "Dias Corridos": dias_corridos_res,
                        "Dias Úteis": dias_uteis_res,
                        "Saldo Remanescente": float(movimento_residual["saldo_remanescente"]),
                    })

                    if lres.id in auditoria_dia:
                        auditoria_dia[lres.id]["Saque Bruto no Dia"] = dinheiro_round(float(auditoria_dia[lres.id]["Saque Bruto no Dia"]) + float(efetivo_res))
                        auditoria_dia[lres.id]["Saque Líquido no Dia"] = dinheiro_round(float(auditoria_dia[lres.id]["Saque Líquido no Dia"]) + float(liquido_res))
                        auditoria_dia[lres.id]["Imposto no Dia"] = dinheiro_round(float(auditoria_dia[lres.id]["Imposto no Dia"]) + float(imposto_res))

        if is_dia_rendimento(data_atual, bcb_map) and lotes_legados_explicitos_do_dia:
            lotes_para_capitalizar_depois = [
                l for l in lotes_por_id.values()
                if str(getattr(l, "id", "")).strip() in lotes_legados_explicitos_do_dia
                and str(getattr(l, "id", "")).strip() not in set(lotes_usados_no_dia)
                and not getattr(l, "esgotado", False)
                and float(getattr(l, "saldo_bruto", 0.0) or 0.0) > 0.0
                and getattr(l, "data_aplicacao", data_atual) <= data_atual
            ]
            atualizar_saldo_lotes_no_dia(lotes_para_capitalizar_depois, data_atual, bcb_map, TAXA_DIA_BASE)
            for l in lotes_para_capitalizar_depois:
                lotes_com_evento_no_dia.add(l.id)
                l.data_efetiva_snapshot_lote = data_atual
                if l.id in auditoria_dia:
                    auditoria_dia[l.id]["Saldo Após Capitalização"] = dinheiro_round(float(getattr(l, "saldo_bruto", 0.0) or 0.0))

        for lote_id_force in list(lotes_nao_investiveis_usados_no_mesmo_dia):
            lforce = lotes_por_id.get(lote_id_force)
            if lforce is None:
                continue
            lforce.saldo_bruto = 0.0
            lforce.principal_remanescente = 0.0
            lforce.esgotado = True
            lotes_com_evento_no_dia.add(lforce.id)
            lforce.data_efetiva_snapshot_lote = data_atual

        for lote_id_trunc in list(lotes_usados_no_dia):
            ltr = lotes_por_id.get(lote_id_trunc)
            if ltr is None:
                continue
            saldo_residual = float(getattr(ltr, "saldo_bruto", 0.0) or 0.0)
            if saldo_residual <= tolerancia_zeramento:
                ltr.saldo_bruto = 0.0
                ltr.principal_remanescente = 0.0
                ltr.esgotado = True
                lotes_com_evento_no_dia.add(ltr.id)
                ltr.data_efetiva_snapshot_lote = data_atual

        for lote_id, row in auditoria_dia.items():
            l1 = lotes_por_id.get(lote_id)
            if l1 is not None:
                if lote_id in lotes_com_evento_no_dia:
                    l1.data_efetiva_snapshot_lote = data_atual
                row["Saldo Final do Dia"] = dinheiro_round(float(getattr(l1, "saldo_bruto", 0.0) or 0.0))
                row["Fator Acumulado Final"] = float(getattr(l1, "fator_acumulado", 1.0) or 1.0)
                row["Principal Remanescente Final"] = dinheiro_round(float(getattr(l1, "principal_remanescente", getattr(l1, "valor_inicial", 0.0)) or 0.0))
                row["Data Efetiva do Snapshot do Lote"] = getattr(l1, "data_efetiva_snapshot_lote", None)
            auditoria_fina_rows.append(row)

        data_atual += timedelta(days=1)

    lotes_final = list(lotes_por_id.values())
    estado_lotes_passado = pd.DataFrame([
        serializar_lote_remanescente(l, data_final) for l in lotes_final
    ])
    df_auditoria_fina = pd.DataFrame(auditoria_fina_rows)
    return lotes_final, log_passado, estado_lotes_passado, df_auditoria_fina

def _calcular_data_referencia_snapshot(hoje, contas_pagas, data_referencia_efetiva=None):
    """Replica o corte temporal do otimizador de gastos original.

    No legado, a simulação do passado roda até a própria data da última conta paga,
    sem avançar um dia extra para formar o snapshot. O +1 dia empurrava os lotes
    antigos, especialmente os de março, para uma posição econômica adiantada.
    """
    if data_referencia_efetiva is not None:
        return data_referencia_efetiva
    if not contas_pagas:
        return hoje
    ultima_conta_paga = max(c[0] for c in contas_pagas)
    return min(hoje, ultima_conta_paga)

def _montar_lotes_pendentes(aportes_raw, data_referencia_snapshot):
    lotes_pendentes = []
    for data_apl, valor, lote_id, ja_aplicado in aportes_raw:
        if ja_aplicado:
            continue
        data_lote = max(data_apl, data_referencia_snapshot)
        lotes_pendentes.append(Lote(lote_id, data_lote, float(valor), produto=None, pendente_aporte=True))
    return lotes_pendentes

def carregar_inventario_e_gastos(produtos: list, bcb_map: dict):
    """Carrega inventário e gastos e materializa o snapshot pós-passado sem auditorias específicas por lote."""
    produtos_dict = {p.nome: p for p in produtos}
    hoje_logico = data_hoje_referencia()
    try:
        hoje = obter_data_referencia_efetiva_runtime() or hoje_logico
    except Exception:
        hoje = hoje_logico

    lote_produto, aportes_raw = _ler_inventario_lotes(produtos_dict)
    contas_pagas, contas_nao_pagas = _ler_gastos_passados_futuros(hoje)
    data_referencia_snapshot = _calcular_data_referencia_snapshot(
        hoje,
        contas_pagas,
        data_referencia_efetiva=hoje,
    )

    lotes_todos, log_passado, estado_lotes_passado, _auditoria_fina = simular_passado(
        aportes_raw,
        contas_pagas,
        bcb_map,
        lote_produto,
        data_referencia_snapshot=data_referencia_snapshot,
    )
    lotes_todos = list(lotes_todos) + _montar_lotes_pendentes(aportes_raw, data_referencia_snapshot)

    for lote in lotes_todos:
        if lote.id in lote_produto:
            lote.produto = lote_produto[lote.id]

    lotes_passados = [
        lote for lote in lotes_todos
        if lote.saldo_bruto > 0.01
        and lote.data_aplicacao <= data_referencia_snapshot
        and not getattr(lote, 'pendente_aporte', False)
    ]
    lotes_futuros = [
        lote for lote in lotes_todos
        if lote.data_aplicacao > data_referencia_snapshot or getattr(lote, 'pendente_aporte', False)
    ]

    return (
        lotes_passados,
        lotes_futuros,
        contas_nao_pagas,
        log_passado,
        data_referencia_snapshot,
        estado_lotes_passado,
    )

# =========================================================
# 12. BASELINE / REGRESSÃO
# =========================================================
def _safe_len(obj) -> int:
    try:
        return len(obj) if obj is not None else 0
    except Exception:
        return 0

def _safe_float(x, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

def _sum_registros_valor(registros: list | None) -> float:
    total = 0.0
    if not registros:
        return total
    for item in registros:
        try:
            total += _safe_float(item[1], 0.0)
        except Exception:
            continue
    return total

def _sample_head_tail(colecao: list | tuple | None, *, n: int = 3) -> dict:
    if not colecao:
        return {"head": [], "tail": []}
    try:
        lst = list(colecao)
    except Exception:
        return {"head": [], "tail": []}
    if len(lst) <= n:
        return {"head": lst[:], "tail": lst[:]}
    return {"head": lst[:n], "tail": lst[-n:]}

def capturar_snapshot_estrutural_legado(
    investimentos_norm: dict | None = None,
    aportes: list | None = None,
    contas_pagas: list | None = None,
    contas_nao_pagas: list | None = None,
    contas_agrupadas: list | None = None,
    *,
    nome: str = "baseline_estrutural_legado",
) -> dict:
    return {
        "tipo_snapshot": "estrutural",
        "nome_snapshot": nome,
        "qtd_investimentos_norm": _safe_len(investimentos_norm),
        "qtd_aportes": _safe_len(aportes),
        "qtd_contas_pagas": _safe_len(contas_pagas),
        "qtd_contas_nao_pagas": _safe_len(contas_nao_pagas),
        "qtd_contas_agrupadas": _safe_len(contas_agrupadas),
        "soma_aportes": _sum_registros_valor(aportes),
        "soma_contas_pagas": _sum_registros_valor(contas_pagas),
        "soma_contas_nao_pagas": _sum_registros_valor(contas_nao_pagas),
        "amostra_aportes": _sample_head_tail(aportes),
        "amostra_contas_pagas": _sample_head_tail(contas_pagas),
        "amostra_contas_nao_pagas": _sample_head_tail(contas_nao_pagas),
        "amostra_contas_agrupadas": _sample_head_tail(contas_agrupadas),
    }

def _inferir_data_snapshot_passado(log_passado_global=None, estado_lotes_passado=None):
    """
    Infere a data efetiva do snapshot do passado.
    Prioriza a maior 'Data' do log_passado_global.
    Fallback: maior 'Data Aplicação' encontrada no estado dos lotes.
    """
    try:
        if log_passado_global:
            datas = []
            for item in log_passado_global:
                if isinstance(item, dict) and item.get("Data") is not None:
                    d = item.get("Data")
                    if hasattr(d, "date"):
                        try:
                            d = d.date()
                        except Exception:
                            pass
                    datas.append(d)
            if datas:
                return max(datas)
    except Exception:
        pass

    try:
        if estado_lotes_passado is not None:
            itens = estado_lotes_passado.values() if isinstance(estado_lotes_passado, dict) else estado_lotes_passado
            datas = []
            for item in itens:
                if isinstance(item, dict) and item.get("Data Aplicação") is not None:
                    d = item.get("Data Aplicação")
                    if hasattr(d, "date"):
                        try:
                            d = d.date()
                        except Exception:
                            pass
                    datas.append(d)
            if datas:
                return max(datas)
    except Exception:
        pass

    return None

def _extrair_saldos_minimos_de_estado(
    estado_lotes_passado,
    log_passado_global=None
) -> tuple[float | None, float | None, int | None]:
    """
    Extrai saldos mínimos do snapshot do passado.
    """
    if estado_lotes_passado is None:
        return None, None, None

    try:
        if isinstance(estado_lotes_passado, dict):
            itens = list(estado_lotes_passado.values())
            qtd_lotes = len(estado_lotes_passado)
        elif isinstance(estado_lotes_passado, list):
            itens = list(estado_lotes_passado)
            qtd_lotes = len(estado_lotes_passado)
        else:
            return None, None, None

        data_snapshot = _inferir_data_snapshot_passado(
            log_passado_global=log_passado_global,
            estado_lotes_passado=estado_lotes_passado
        )

        saldo_bruto_total = 0.0
        saldo_liquido_total = 0.0
        achou_bruto = False
        achou_liquido = False

        for lote in itens:
            if not isinstance(lote, dict):
                continue

            bruto = None
            for chave_bruto in (
                "Saldo Após Passado",
                "Saldo Bruto",
                "saldo_bruto",
                "saldo_bruto_atual",
            ):
                if chave_bruto in lote and lote.get(chave_bruto) is not None:
                    bruto = _safe_float(lote.get(chave_bruto), 0.0)
                    achou_bruto = True
                    break

            if bruto is None:
                continue

            saldo_bruto_total += bruto

            liquido = None
            for chave_liq in (
                "Saldo Líquido Após Passado",
                "Saldo Liquido Após Passado",
                "Saldo Liquido",
                "Saldo Líquido",
                "saldo_liquido",
                "saldo_liquido_atual",
            ):
                if chave_liq in lote and lote.get(chave_liq) is not None:
                    liquido = _safe_float(lote.get(chave_liq), 0.0)
                    achou_liquido = True
                    break

            if liquido is None and data_snapshot is not None:
                try:
                    data_base = lote.get("Data Base Fiscal", lote.get("Data Aplicação"))
                    if hasattr(data_base, "date"):
                        try:
                            data_base = data_base.date()
                        except Exception:
                            pass

                    if data_base is not None:
                        dias_vida = max((data_snapshot - data_base).days, 0)

                        principal_remanescente = _safe_float(
                            lote.get("Principal Remanescente", lote.get("Valor Inicial", bruto)),
                            bruto
                        )
                        principal_base = max(min(principal_remanescente, bruto), 0.0)
                        lucro = max(bruto - principal_base, 0.0)

                        ir = obter_aliquota_ir(dias_vida)
                        imposto = lucro * ir
                        liquido = max(bruto - imposto, 0.0)
                        achou_liquido = True
                except Exception:
                    liquido = None

            if liquido is not None:
                saldo_liquido_total += liquido

        return (
            float(round(saldo_bruto_total, 2)) if achou_bruto else None,
            float(round(saldo_liquido_total, 2)) if achou_liquido else None,
            qtd_lotes,
        )

    except Exception:
        return None, None, None

def capturar_snapshot_financeiro_minimo(
    estado_lotes_passado=None,
    log_passado_global=None,
    resultado_final: dict | None = None,
    *,
    nome: str = "baseline_financeiro_legado",
) -> dict:
    saldo_bruto_total, saldo_liquido_total, qtd_lotes_estado = _extrair_saldos_minimos_de_estado(
        estado_lotes_passado,
        log_passado_global=log_passado_global,
    )
    return {
        "tipo_snapshot": "financeiro",
        "nome_snapshot": nome,
        "qtd_lotes_estado": qtd_lotes_estado,
        "qtd_logs_passado": _safe_len(log_passado_global),
        "saldo_bruto_total": saldo_bruto_total,
        "saldo_liquido_total": saldo_liquido_total,
        "campos_resultado_final": sorted(list(resultado_final.keys())) if isinstance(resultado_final, dict) else [],
    }

def capturar_snapshot_financeiro_final(
    *,
    df_res=None,
    col_saldo: str | None = None,
    melhor_estrategia: str | None = None,
    resultados_wf: dict | None = None,
    lotes_melhor=None,
    df_situacao_atual=None,
    nome: str = "snapshot_financeiro_final",
) -> dict:
    """
    Captura um snapshot financeiro final da execução, já com ranking consolidado
    e situação atual da melhor estratégia.
    """
    snap = {
        "tipo_snapshot": "financeiro_final",
        "nome_snapshot": nome,
        "melhor_estrategia": melhor_estrategia,
        "saldo_coluna_usada": col_saldo,
        "modo_vencedor": None,
        "saldo_liquido_ajustado_final": None,
        "saldo_liquido_final": None,
        "saldo_bruto_final": None,
        "valor_nao_coberto_final": None,
        "robustez_wf_final": None,
        "score_final": None,
        "lotes_usados_final": None,
        "total_lotes_final": None,
        "tempo_execucao_final": None,
        "wf_delta_ef": None,
        "wf_cv_liquido_teste": None,
        "wf_saldo_liquido_teste": None,
        "wf_saldo_liquido_treino": None,
        "qtd_lotes_melhor": None,
        "qtd_lotes_relatorio_atual": None,
        "saldo_bruto_atual_total": None,
        "saldo_liquido_atual_total": None,
        "patrimonio_liquido_total": None,
        "total_liquido_sacado_total": None,
        "ganho_otimizacao_total": None,
        "relatorio_atual_vazio": None,
    }

    try:
        if df_res is not None and len(df_res) > 0:
            row0 = df_res.iloc[0]
            snap["modo_vencedor"] = row0.get("Modo", None)
            snap["saldo_liquido_ajustado_final"] = row0.get("Saldo Líq Aj.", row0.get("Saldo Líquido Ajustado (R$)", None))
            snap["saldo_liquido_final"] = row0.get("Saldo Líq", row0.get("Saldo Líquido", row0.get("Saldo Líquido (R$)", None)))
            snap["saldo_bruto_final"] = row0.get("Saldo Bruto", row0.get("Saldo Final (R$)", None))
            snap["valor_nao_coberto_final"] = row0.get("Não Coberto", row0.get("Valor Não Coberto (R$)", None))
            snap["robustez_wf_final"] = row0.get("WF", row0.get("Robustez WF", None))
            snap["score_final"] = row0.get("Score", row0.get("Score Final", None))
            snap["lotes_usados_final"] = row0.get("Lotes Usados", None)
            snap["total_lotes_final"] = row0.get("Total Lotes", None)
            snap["tempo_execucao_final"] = row0.get("Tempo", row0.get("Tempo (s)", None))
    except Exception:
        pass

    try:
        if melhor_estrategia and isinstance(resultados_wf, dict) and melhor_estrategia in resultados_wf:
            wf = resultados_wf.get(melhor_estrategia, {})
            if isinstance(wf, dict):
                snap["wf_delta_ef"] = wf.get("delta_ef", wf.get("deltaEF", None))
                snap["wf_cv_liquido_teste"] = wf.get("cv_liquido_teste", wf.get("cv_liq", wf.get("CVliq", None)))
                snap["wf_saldo_liquido_teste"] = wf.get("saldo_liq_teste", None)
                snap["wf_saldo_liquido_treino"] = wf.get("saldo_liq_treino", None)
                if snap["robustez_wf_final"] is None:
                    snap["robustez_wf_final"] = wf.get("score_robustez", wf.get("robustez", None))
    except Exception:
        pass

    try:
        snap["qtd_lotes_melhor"] = len(lotes_melhor) if lotes_melhor is not None else None
    except Exception:
        pass

    try:
        if df_situacao_atual is None:
            snap["relatorio_atual_vazio"] = None
        elif getattr(df_situacao_atual, "empty", True):
            snap["relatorio_atual_vazio"] = True
            snap["qtd_lotes_relatorio_atual"] = 0
        else:
            snap["relatorio_atual_vazio"] = False
            snap["qtd_lotes_relatorio_atual"] = len(df_situacao_atual)

            def _sum_col(df, col):
                try:
                    return float(df[col].fillna(0).sum()) if col in df.columns else None
                except Exception:
                    return None

            snap["saldo_bruto_atual_total"] = _sum_col(df_situacao_atual, "Saldo Bruto Atual (R$)")
            snap["saldo_liquido_atual_total"] = _sum_col(df_situacao_atual, "Saldo Líquido Atual (R$)")
            snap["patrimonio_liquido_total"] = _sum_col(df_situacao_atual, "Patrimônio Líquido até Hoje (R$)")
            snap["total_liquido_sacado_total"] = _sum_col(df_situacao_atual, "Total Líquido Sacado (R$)")
            snap["ganho_otimizacao_total"] = _sum_col(df_situacao_atual, "Ganho da Otimização vs Dinheiro Parado (R$)")
    except Exception:
        pass

    return snap

def serializar_snapshot_baseline(snapshot: dict, *, prefixo: str = "[BASELINE]") -> None:
    if not isinstance(snapshot, dict):
        print(f"{prefixo} snapshot inválido")
        return
    tipo = snapshot.get("tipo_snapshot", "desconhecido")
    nome = snapshot.get("nome_snapshot", "sem_nome")
    print(f"{prefixo} tipo={tipo} nome_snapshot={nome}")
    if tipo == "estrutural":
        print(f"{prefixo} qtd_investimentos_norm={snapshot.get('qtd_investimentos_norm')} qtd_aportes={snapshot.get('qtd_aportes')} soma_aportes={snapshot.get('soma_aportes')}")
        print(f"{prefixo} qtd_contas_pagas={snapshot.get('qtd_contas_pagas')} soma_contas_pagas={snapshot.get('soma_contas_pagas')}")
        print(f"{prefixo} qtd_contas_nao_pagas={snapshot.get('qtd_contas_nao_pagas')} soma_contas_nao_pagas={snapshot.get('soma_contas_nao_pagas')}")
        print(f"{prefixo} qtd_contas_agrupadas={snapshot.get('qtd_contas_agrupadas')}")
    elif tipo == "financeiro":
        print(f"{prefixo} qtd_lotes_estado={snapshot.get('qtd_lotes_estado')} qtd_logs_passado={snapshot.get('qtd_logs_passado')}")
        print(f"{prefixo} saldo_bruto_total={snapshot.get('saldo_bruto_total')} saldo_liquido_total={snapshot.get('saldo_liquido_total')}")
        if snapshot.get("campos_resultado_final"):
            print(f"{prefixo} campos_resultado_final={snapshot.get('campos_resultado_final')}")
    elif tipo == "financeiro_final":
        print(
            f"{prefixo} melhor_estrategia={snapshot.get('melhor_estrategia')} "
            f"modo_vencedor={snapshot.get('modo_vencedor')} "
            f"saldo_coluna_usada={snapshot.get('saldo_coluna_usada')}"
        )
        print(
            f"{prefixo} saldo_liquido_ajustado_final={snapshot.get('saldo_liquido_ajustado_final')} "
            f"saldo_liquido_final={snapshot.get('saldo_liquido_final')} "
            f"saldo_bruto_final={snapshot.get('saldo_bruto_final')} "
            f"valor_nao_coberto_final={snapshot.get('valor_nao_coberto_final')}"
        )
        print(
            f"{prefixo} robustez_wf_final={snapshot.get('robustez_wf_final')} "
            f"score_final={snapshot.get('score_final')} "
            f"lotes_usados_final={snapshot.get('lotes_usados_final')} "
            f"total_lotes_final={snapshot.get('total_lotes_final')}"
        )
        print(
            f"{prefixo} qtd_lotes_relatorio_atual={snapshot.get('qtd_lotes_relatorio_atual')} "
            f"saldo_liquido_atual_total={snapshot.get('saldo_liquido_atual_total')} "
            f"patrimonio_liquido_total={snapshot.get('patrimonio_liquido_total')} "
            f"ganho_otimizacao_total={snapshot.get('ganho_otimizacao_total')}"
        )

CONTRATO_OPERACIONAL = obter_contrato_operacional(config)
validar_contrato_operacional(CONTRATO_OPERACIONAL)
print(f"[CONTRATO] {resumir_contrato_operacional(CONTRATO_OPERACIONAL)}")

# =========================================================
# 12.1 HELPERS DE RELATÓRIO, TAXAS E SERIALIZAÇÃO DE LOTES
# =========================================================
def get_taxas_lote(nome_investimento):
    """Retorna (taxa_base, taxa_bonus, dias_bonus) para o investimento, com fallback."""
    if nome_investimento and str(nome_investimento).lower() not in ('nan', 'none', ''):
        nome_norm = normalizar_nome(nome_investimento)
        info = INVESTIMENTOS_NORM.get(nome_norm)
        if info:
            return info['base'], info['bonus'] or 0.0, info['dias_bonus']
    info_turb = INVESTIMENTOS_NORM.get(PRODUTO_FALLBACK_NOME)
    if info_turb:
        return info_turb['base'], info_turb['bonus'] or 0.0, info_turb['dias_bonus']
    return TAXA_BASE_DEFAULT, TAXA_BONUS_DEFAULT, DIAS_BONUS_DEFAULT

def acumular_saques_por_lote(log_movimentos):
    """Acumula saques bruto e líquido por lote a partir do log histórico."""
    total_bruto = {}
    total_liquido = {}
    for entrada in log_movimentos:
        lote_id = str(entrada.get('Lote'))
        total_bruto[lote_id] = total_bruto.get(lote_id, 0.0) + float(entrada.get('Bruto', 0.0))
        total_liquido[lote_id] = total_liquido.get(lote_id, 0.0) + float(entrada.get('Liquido', 0.0))
    return total_bruto, total_liquido

def obter_data_referencia_relatorio_local(mapa_bcb, data_referencia=None):
    """Retorna a data-base operacional do relatório.

    O saldo atual deve refletir a posição do app bancário na própria data de referência.
    Lacunas do BCB no dia corrente são cobertas pela projeção do motor.
    """
    if data_referencia is None:
        data_referencia = DATA_REFERENCIA
    return data_referencia

def obter_data_referencia_relatorio(mapa_bcb, data_referencia=None):
    return obter_data_referencia_relatorio_local(mapa_bcb, data_referencia)

def obter_data_fiscal_liquido_relatorio(mapa_bcb, data_fiscal_relatorio, data_base_fiscal):
    """Alinha a data fiscal do líquido atual à última data fechada disponível no mapa BCB."""
    if mapa_bcb:
        datas_validas = [d for d in mapa_bcb.keys() if d <= data_fiscal_relatorio]
        if datas_validas:
            data_fiscal = max(datas_validas)
        else:
            data_fiscal = data_fiscal_relatorio
    else:
        data_fiscal = data_fiscal_relatorio
    return max(data_base_fiscal, data_fiscal)

def calcular_liquido_atual_relatorio(lote, saldo_bruto_atual, data_resgate_fiscal):
    dias_vida = (data_resgate_fiscal - lote.data_base_fiscal).days + 1
    if dias_vida < 0:
        return 0.0
    iof = float(IOF_TABLE[dias_vida]) if dias_vida < 30 else 0.0
    ir = _taxa_ir(dias_vida, getattr(getattr(lote, 'produto', None), 'isento_ir', False))
    principal_attr = float(getattr(lote, 'principal_remanescente', getattr(lote, 'valor_inicial', 0.0)) or 0.0)
    principal_base = max(min(principal_attr, float(saldo_bruto_atual)), 0.0)
    lucro = max(float(saldo_bruto_atual) - principal_base, 0.0)
    iof_valor_round = dinheiro_round(lucro * iof)
    base_ir = max(lucro - iof_valor_round, 0.0)
    ir_valor_round = dinheiro_round(base_ir * ir)
    imposto_total = dinheiro_round(iof_valor_round + ir_valor_round)
    liquido = dinheiro_round(max(float(saldo_bruto_atual) - imposto_total, 0.0))
    return liquido

def listar_datas_economicas_relatorio(data_snapshot_lote, data_referencia_efetiva, bcb_map=None, data_aplicacao=None):
    """Lista as datas econômicas efetivamente aplicáveis no relatório atual."""
    if data_snapshot_lote is None or data_referencia_efetiva is None:
        return []
    if data_snapshot_lote >= data_referencia_efetiva:
        return []

    datas = []
    d = data_snapshot_lote + timedelta(days=1)
    while d <= data_referencia_efetiva:
        if (data_aplicacao is None or data_aplicacao <= d) and is_dia_rendimento(d, bcb_map or {}):
            datas.append(d)
        d += timedelta(days=1)
    return datas

def serializar_lote_remanescente(lote, data_final=None):
    prod = getattr(lote, 'produto', None)
    data_base_fiscal = getattr(lote, 'data_base_fiscal', getattr(lote, 'data_aplicacao', None))
    data_efetiva_global = data_final or getattr(lote, 'data_aplicacao', None)
    data_efetiva_lote = getattr(lote, 'data_efetiva_snapshot_lote', None)

    return {
        'Data Efetiva': data_efetiva_global,
        'Data Efetiva do Snapshot do Lote': data_efetiva_lote,
        'Saldo Bruto': dinheiro_round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0)),
        'Lote ID': str(getattr(lote, 'id', '') or '').strip(),
        'Data Aplicação': getattr(lote, 'data_aplicacao', None),
        'Valor Inicial': dinheiro_round(float(getattr(lote, 'valor_inicial', 0.0) or 0.0)),
        'Saldo Após Passado': dinheiro_round(float(getattr(lote, 'saldo_bruto', 0.0) or 0.0)),
        'Esgotado no Passado': bool(getattr(lote, 'esgotado', False) or float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.01),
        'Data Base Fiscal': data_base_fiscal,
        'Fator Acumulado': float(getattr(lote, 'fator_acumulado', 1.0) or 1.0),
        'Taxa Base CDI': float(getattr(lote, 'taxa_base_cdi', getattr(prod, 'taxa_base', TAXA_BASE_DEFAULT)) or TAXA_BASE_DEFAULT),
        'Taxa Bonus CDI': float(getattr(lote, 'taxa_bonus_cdi', getattr(prod, 'taxa_bonus', 0.0)) or 0.0),
        'Dias Bonus': int(getattr(lote, 'dias_bonus', getattr(prod, 'dias_bonus', 0)) or 0),
        'Principal Remanescente': dinheiro_round(float(getattr(lote, 'principal_remanescente', getattr(lote, 'valor_inicial', 0.0)) or 0.0)),
        'Investimento': getattr(prod, 'nome', '-'),
        'meta': {
            'carencia_ate': getattr(lote, 'carencia_ate', None),
            'produto_isento_ir': bool(getattr(prod, 'isento_ir', False) if prod is not None else False),
            'data_efetiva_snapshot_lote': data_efetiva_lote,
        }
    }

# =========================================================
# 12.2 RELATÓRIOS, RECONSTRUÇÃO E FECHAMENTO OPERACIONAL
# =========================================================
def _coagir_para_date(valor):
    """Converte timestamps/datetime para ``date`` quando possível."""
    if valor is None:
        return None
    try:
        if hasattr(valor, "date"):
            return valor.date()
    except Exception:
        pass
    return valor

def reconstruir_lote_para_relatorio(st, produtos_por_nome=None):
    """Reconstrói o lote a partir do snapshot como fonte autoritativa."""
    nome_label = str(st.get('Investimento', '-') or '-').strip()
    data_aplic = _coagir_para_date(st.get('Data Aplicação'))
    data_base_fiscal = _coagir_para_date(st.get('Data Base Fiscal')) or data_aplic
    valor_inicial = float(st.get('Valor Inicial', 0.0) or 0.0)
    fator_acum = float(st.get('Fator Acumulado', 1.0) or 1.0)
    principal_rem = float(st.get('Principal Remanescente', valor_inicial) or valor_inicial)
    carencia_ate = _coagir_para_date(st.get('Carência Até'))

    taxa_base_snap = float(st.get('Taxa Base CDI', TAXA_BASE_DEFAULT) or TAXA_BASE_DEFAULT)
    taxa_bonus_default = TAXA_BONUS_DEFAULT if TAXA_BONUS_DEFAULT > 0 else taxa_base_snap
    taxa_bonus_snap = float(st.get('Taxa Bonus CDI', taxa_bonus_default) or taxa_bonus_default)
    dias_bonus_snap = int(st.get('Dias Bonus', DIAS_BONUS_DEFAULT) or DIAS_BONUS_DEFAULT)
    isento_ir_snap = bool(st.get('Produto Isento IR', False) or False)

    produto_snapshot = None
    if produtos_por_nome and nome_label in produtos_por_nome and produtos_por_nome.get(nome_label) is not None:
        produto_snapshot = produtos_por_nome.get(nome_label)
    else:
        produto_snapshot = Produto(
            nome=nome_label if nome_label else '-',
            taxa_base=taxa_base_snap,
            taxa_bonus=taxa_bonus_snap if taxa_bonus_snap > 0 else taxa_base_snap,
            dias_bonus=dias_bonus_snap,
            prazo_dias=0,
            carencia_dias=0,
            isento_ir=isento_ir_snap,
            ativo=True,
        )

    lote = criar_lote_de_aporte(
        data_aplic,
        valor_inicial,
        st.get('Lote ID', ''),
        {
            'produto': produto_snapshot,
            'investimento': nome_label if nome_label else '-',
            'carencia_ate': carencia_ate,
            'data_base_fiscal': data_base_fiscal,
            'fator_acumulado_inicial': fator_acum,
            'taxa_base_cdi': taxa_base_snap,
            'taxa_bonus_cdi': taxa_bonus_snap,
            'dias_bonus': dias_bonus_snap,
            'principal_remanescente': principal_rem,
            'produto_isento_ir': isento_ir_snap,
        }
    )

    lote.saldo_bruto = float(st.get('Saldo Após Passado', 0.0) or 0.0)
    lote.esgotado = bool(st.get('Esgotado no Passado', False) or lote.saldo_bruto <= 0.01)

    data_snapshot = pd.to_datetime(st.get('Data Efetiva do Snapshot do Lote', st.get('Data Efetiva')), errors='coerce')
    lote.data_efetiva_snapshot_lote = None if pd.isna(data_snapshot) else data_snapshot.date()
    return lote

def atualizar_lote_reconstruido_ate_data(lote, data_corte_passado, data_referencia_efetiva, bcb_map):
    """Atualiza lote reconstruído até a data efetiva do relatório."""
    if lote is None or getattr(lote, 'esgotado', False):
        return lote

    data_snapshot_lote = getattr(lote, 'data_efetiva_snapshot_lote', None) or data_corte_passado
    if data_snapshot_lote is None or data_referencia_efetiva is None or data_snapshot_lote >= data_referencia_efetiva:
        return lote

    datas_rendimento = listar_datas_economicas_relatorio(
        data_snapshot_lote=data_snapshot_lote,
        data_referencia_efetiva=data_referencia_efetiva,
        bcb_map=bcb_map,
        data_aplicacao=getattr(lote, 'data_aplicacao', None),
    )
    for d in datas_rendimento:
        atualizar_saldo_lotes_no_dia([lote], d, bcb_map, TAXA_DIA_BASE)
    return lote

def baixar_fallback_bcb():
    """Baixa arquivo de fallback do Google Drive e preenche datas faltantes."""
    print(">>> [BCB FALLBACK] Baixando dados históricos do Drive...")

    if not FALLBACK_BCB_FILE_ID and not FALLBACK_BCB_URL:
        print(" -> [AVISO] FALLBACK_BCB_FILE_ID não definido no config. Fallback desabilitado.")
        return {}, TAXA_DIA_BASE

    url_export = FALLBACK_BCB_URL or gdrive_uc_download(FALLBACK_BCB_FILE_ID)

    try:
        headers = {"User-Agent": REDE_USER_AGENT_DOWNLOAD}
        response = requests.get(
            url_export,
            headers=headers,
            timeout=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS,
            verify=REDE_VERIFICAR_SSL,
        )
        response.raise_for_status()

        fallback_file = ARQUIVO_TEMPORARIO_FALLBACK_BCB
        with open(fallback_file, 'wb') as f:
            f.write(response.content)

        df = pd.read_excel(fallback_file)
        mapa_cdi = {}
        ultima_taxa = TAXA_DIA_BASE

        for _, row in df.iterrows():
            try:
                dt = pd.to_datetime(row['data']).date()
                val_pct = float(row['valor'])
                taxa_dec = val_pct / 100.0
                mapa_cdi[dt] = 1.0 + taxa_dec
                ultima_taxa = taxa_dec
            except Exception:
                continue

        if mapa_cdi:
            data_inicio = min(mapa_cdi.keys())
            data_final = DATA_REFERENCIA
            data_atual = data_inicio
            while data_atual <= data_final:
                if data_atual not in mapa_cdi:
                    mapa_cdi[data_atual] = 1.0 + TAXA_DIA_BASE
                data_atual += timedelta(days=1)
            print(f" -> Fallback OK: {len(mapa_cdi)} dias totais\n")
        else:
            print(f" -> Fallback carregado: {len(mapa_cdi)} dias\n")

        return mapa_cdi, ultima_taxa
    except Exception as e:
        print(f" -> [ERRO] Falha no fallback: {e}\n")
        return {}, TAXA_DIA_BASE

def gerar_relatorio_situacao_atual(
    lotes_hoje,
    estado_lotes_passado,
    log_passado,
    valores_originais,
    mapa_bcb,
    data_referencia=None,
):
    """Gera o relatório de situação atual com base no snapshot pós-passado.

    Mantém o foco em uma saída limpa e objetiva, sem auditorias específicas por lote.
    """
    if data_referencia is None:
        data_referencia = DATA_REFERENCIA
    data_referencia_efetiva = obter_data_referencia_relatorio(mapa_bcb, data_referencia)

    if estado_lotes_passado is None:
        return pd.DataFrame()
    if isinstance(estado_lotes_passado, pd.DataFrame):
        estado_rows = estado_lotes_passado.to_dict('records')
    else:
        estado_rows = list(estado_lotes_passado or [])
    if not estado_rows:
        return pd.DataFrame()

    total_sacado_bruto_passado, total_sacado_liquido_passado = acumular_saques_por_lote(log_passado or [])

    datas_log = []
    for x in (log_passado or []):
        try:
            d = x.get('Data') if isinstance(x, dict) else None
            d = _coagir_para_date(pd.to_datetime(d, errors='coerce')) if d is not None else None
            if d is not None:
                datas_log.append(d)
        except Exception:
            pass
    data_corte_passado = max(datas_log) if datas_log else None

    produtos_por_nome = {}
    for lote in lotes_hoje or []:
        prod = getattr(lote, 'produto', None)
        nome = getattr(prod, 'nome', '') if prod is not None else ''
        if nome:
            produtos_por_nome[nome] = prod

    relatorio = []
    for st in estado_rows:
        lote_id = str(st.get('Lote ID', '') or '').strip()
        data_aplicacao_original = _coagir_para_date(st.get('Data Aplicação', st.get('Data Base Fiscal')))
        data_base_fiscal = _coagir_para_date(st.get('Data Base Fiscal', data_aplicacao_original))
        if data_base_fiscal is None or data_base_fiscal > data_referencia_efetiva:
            continue

        lotex = reconstruir_lote_para_relatorio(st, produtos_por_nome)
        lotex.investimento = str(st.get('Investimento', '') or '')
        if data_corte_passado is not None and data_referencia_efetiva > data_corte_passado:
            lotex = atualizar_lote_reconstruido_ate_data(lotex, data_corte_passado, data_referencia_efetiva, mapa_bcb)

        saldo_bruto_atual = float(round(max(lotex.saldo_bruto, 0.0), 2))
        data_fiscal_relatorio = data_referencia_efetiva
        if data_corte_passado is not None and data_corte_passado > data_fiscal_relatorio:
            data_fiscal_relatorio = data_corte_passado

        data_fiscal_para_liquido = obter_data_fiscal_liquido_relatorio(mapa_bcb, data_fiscal_relatorio, data_base_fiscal)
        liq_atual = calcular_liquido_atual_relatorio(lotex, saldo_bruto_atual, data_fiscal_para_liquido)

        val_orig = float(valores_originais.get(lote_id, st.get('Valor Inicial', 0.0) or 0.0))
        total_sacado = float(total_sacado_bruto_passado.get(lote_id, 0.0))
        total_liquido_sacado = float(total_sacado_liquido_passado.get(lote_id, 0.0))

        dias_hoje = (data_fiscal_relatorio - data_base_fiscal).days
        dias_uteis_hoje = contar_dias_rendimento(data_base_fiscal, data_fiscal_relatorio, mapa_bcb)

        patrimonio_liquido_ate_hoje = liq_atual + total_liquido_sacado
        rendimento_liquido_acumulado_lotes = patrimonio_liquido_ate_hoje - val_orig
        saldo_se_dinheiro_ficasse_parado = max(val_orig - total_liquido_sacado, 0.0)
        ganho_otimizacao_vs_dinheiro_parado = liq_atual - saldo_se_dinheiro_ficasse_parado
        rent_bruta = ((saldo_bruto_atual + total_sacado) / val_orig - 1) * 100 if val_orig > 0 else 0.0
        rent_liquida = (patrimonio_liquido_ate_hoje / val_orig - 1) * 100 if val_orig > 0 else 0.0

        relatorio.append({
            'Lote ID': lote_id,
            'Carteira': lotex.investimento or '-',
            'Data Aplicação': data_aplicacao_original,
            'Data Base Fiscal': data_base_fiscal,
            'Dias Corridos até Hoje': dias_hoje,
            'Dias Úteis até Hoje': dias_uteis_hoje,
            'Valor Original (R$)': dinheiro_round(val_orig),
            'Total Bruto Sacado (R$)': dinheiro_round(total_sacado),
            'Total Líquido Sacado (R$)': dinheiro_round(total_liquido_sacado),
            'Saldo Bruto Atual (R$)': saldo_bruto_atual,
            'Saldo Líquido Atual (R$)': liq_atual,
            'Patrimônio Líquido até Hoje (R$)': dinheiro_round(patrimonio_liquido_ate_hoje),
            'Rendimento Líquido Acumulado dos Lotes (R$)': dinheiro_round(rendimento_liquido_acumulado_lotes),
            'Saldo se Dinheiro Ficasse Parado (R$)': dinheiro_round(saldo_se_dinheiro_ficasse_parado),
            'Ganho da Otimização vs Dinheiro Parado (R$)': dinheiro_round(ganho_otimizacao_vs_dinheiro_parado),
            'Rentabilidade Bruta (%)': round(rent_bruta, 2),
            'Rentabilidade Líquida (%)': round(rent_liquida, 2),
            'Esgotado no Passado': bool(st.get('Esgotado no Passado', False)),
            'Taxa Base CDI (%)': round(float(st.get('Taxa Base CDI', TAXA_BASE_DEFAULT)) * 100, 0),
        })

    if not relatorio:
        return pd.DataFrame()

    df_relatorio_atual = pd.DataFrame(relatorio)
    total_row = {
        'Lote ID': 'TOTAL',
        'Carteira': '',
        'Valor Original (R$)': round(df_relatorio_atual['Valor Original (R$)'].sum(), 2),
        'Total Bruto Sacado (R$)': round(df_relatorio_atual['Total Bruto Sacado (R$)'].sum(), 2),
        'Total Líquido Sacado (R$)': round(df_relatorio_atual['Total Líquido Sacado (R$)'].sum(), 2),
        'Saldo Bruto Atual (R$)': round(df_relatorio_atual['Saldo Bruto Atual (R$)'].sum(), 2),
        'Saldo Líquido Atual (R$)': round(df_relatorio_atual['Saldo Líquido Atual (R$)'].sum(), 2),
        'Patrimônio Líquido até Hoje (R$)': round(df_relatorio_atual['Patrimônio Líquido até Hoje (R$)'].sum(), 2),
        'Rendimento Líquido Acumulado dos Lotes (R$)': round(df_relatorio_atual['Rendimento Líquido Acumulado dos Lotes (R$)'].sum(), 2),
        'Saldo se Dinheiro Ficasse Parado (R$)': round(df_relatorio_atual['Saldo se Dinheiro Ficasse Parado (R$)'].sum(), 2),
        'Ganho da Otimização vs Dinheiro Parado (R$)': round(df_relatorio_atual['Ganho da Otimização vs Dinheiro Parado (R$)'].sum(), 2),
    }
    return pd.concat([df_relatorio_atual, pd.DataFrame([total_row])], ignore_index=True)


def gerar_relatorio_melhor_estrategia_por_lotes_finais(
    *,
    lotes_finais,
    data_terminal_estrategia,
    total_resgatado_liquido=0.0,
    mapa_bcb=None,
    estrategia=None,
    modo=None,
    valor_nao_coberto=0.0,
    info_ranking=None,
    info_wf=None,
):
    """Gera a aba e o resumo da melhor estratégia a partir da carteira final real."""
    info_ranking = dict(info_ranking or {})
    info_wf = dict(info_wf or {})

    data_ref = data_terminal_estrategia or DATA_REFERENCIA
    try:
        data_ref = obter_data_referencia_relatorio(mapa_bcb, data_ref)
    except Exception:
        pass

    linhas = []
    saldo_bruto_total = 0.0
    saldo_liquido_total = 0.0
    total_liquido_sacado_lotes = 0.0
    valor_original_total = 0.0
    total_lotes = 0
    lotes_ativos = 0

    for lote in list(lotes_finais or []):
        if lote is None:
            continue

        lote_id = str(getattr(lote, 'id', '') or '').strip()
        data_aplic = _coagir_para_date(getattr(lote, 'data_aplicacao', None))
        data_base_fiscal = _coagir_para_date(getattr(lote, 'data_base_fiscal', None) or data_aplic)

        if data_aplic is not None and data_aplic > data_ref:
            continue

        total_lotes += 1

        saldo_bruto = float(getattr(lote, 'saldo_bruto', 0.0) or 0.0)
        esgotado = bool(getattr(lote, 'esgotado', False))
        if (not esgotado) and saldo_bruto > VALOR_MINIMO_LOTE_ATIVO:
            lotes_ativos += 1

        try:
            fator_liq = float(lote.get_fator_liquido(data_ref) or 0.0) if saldo_bruto > 0.0 else 0.0
        except Exception:
            fator_liq = 1.0 if saldo_bruto > 0.0 else 0.0
        if not np.isfinite(fator_liq) or fator_liq < 0.0:
            fator_liq = 1.0 if saldo_bruto > 0.0 else 0.0

        saldo_liquido = float(max(saldo_bruto * fator_liq, 0.0))
        valor_original = float(getattr(lote, 'valor_inicial', 0.0) or 0.0)
        total_bruto_sacado_lote = float(getattr(lote, 'total_bruto_sacado', 0.0) or 0.0)
        total_liquido_sacado_lote = float(getattr(lote, 'total_liquido_sacado', 0.0) or 0.0)

        saldo_bruto_total += saldo_bruto
        saldo_liquido_total += saldo_liquido
        total_liquido_sacado_lotes += total_liquido_sacado_lote
        valor_original_total += valor_original

        nome_produto = str(getattr(getattr(lote, 'produto', None), 'nome', None) or getattr(lote, 'investimento', None) or '-')
        if data_base_fiscal is not None:
            dias_corridos = max((data_ref - data_base_fiscal).days, 0)
            dias_uteis = contar_dias_rendimento(data_base_fiscal, data_ref, mapa_bcb or {})
        else:
            dias_corridos = None
            dias_uteis = None

        patrimonio_liquido = saldo_liquido + total_liquido_sacado_lote
        rendimento_liquido = patrimonio_liquido - valor_original
        saldo_parado = max(valor_original - total_liquido_sacado_lote, 0.0)
        ganho_otimizacao = saldo_liquido - saldo_parado
        rent_bruta = ((saldo_bruto + total_bruto_sacado_lote) / valor_original - 1.0) * 100.0 if valor_original > 0.0 else 0.0
        rent_liquida = (patrimonio_liquido / valor_original - 1.0) * 100.0 if valor_original > 0.0 else 0.0

        linhas.append({
            'Lote ID': lote_id,
            'Carteira': nome_produto,
            'Data Aplicação': data_aplic,
            'Data Base Fiscal': data_base_fiscal,
            'Dias Corridos até Hoje': dias_corridos,
            'Dias Úteis até Hoje': dias_uteis,
            'Valor Original (R$)': dinheiro_round(valor_original),
            'Total Bruto Sacado (R$)': dinheiro_round(total_bruto_sacado_lote),
            'Total Líquido Sacado (R$)': dinheiro_round(total_liquido_sacado_lote),
            'Saldo Bruto Atual (R$)': dinheiro_round(saldo_bruto),
            'Saldo Líquido Atual (R$)': dinheiro_round(saldo_liquido),
            'Patrimônio Líquido até Hoje (R$)': dinheiro_round(patrimonio_liquido),
            'Rendimento Líquido Acumulado dos Lotes (R$)': dinheiro_round(rendimento_liquido),
            'Saldo se Dinheiro Ficasse Parado (R$)': dinheiro_round(saldo_parado),
            'Ganho da Otimização vs Dinheiro Parado (R$)': dinheiro_round(ganho_otimizacao),
            'Rentabilidade Bruta (%)': round(rent_bruta, 2),
            'Rentabilidade Líquida (%)': round(rent_liquida, 2),
            'Esgotado no Passado': esgotado,
            'Taxa Base CDI (%)': round(float(getattr(getattr(lote, 'produto', None), 'taxa_base', TAXA_BASE_DEFAULT) or TAXA_BASE_DEFAULT) * 100, 0),
        })

    df_relatorio = pd.DataFrame(linhas)

    total_liquido_sacado = max(float(total_resgatado_liquido or 0.0), float(total_liquido_sacado_lotes))
    patrimonio_liquido_total = float(saldo_liquido_total) + float(total_liquido_sacado)

    total_row = {
        'Lote ID': 'TOTAL',
        'Carteira': '',
        'Valor Original (R$)': dinheiro_round(valor_original_total),
        'Total Bruto Sacado (R$)': dinheiro_round(float(pd.to_numeric(df_relatorio.get('Total Bruto Sacado (R$)', pd.Series(dtype=float)), errors='coerce').fillna(0.0).sum()) if not df_relatorio.empty else 0.0),
        'Total Líquido Sacado (R$)': dinheiro_round(total_liquido_sacado),
        'Saldo Bruto Atual (R$)': dinheiro_round(saldo_bruto_total),
        'Saldo Líquido Atual (R$)': dinheiro_round(saldo_liquido_total),
        'Patrimônio Líquido até Hoje (R$)': dinheiro_round(patrimonio_liquido_total),
        'Rendimento Líquido Acumulado dos Lotes (R$)': dinheiro_round(patrimonio_liquido_total - valor_original_total),
        'Saldo se Dinheiro Ficasse Parado (R$)': dinheiro_round(max(valor_original_total - total_liquido_sacado, 0.0)),
        'Ganho da Otimização vs Dinheiro Parado (R$)': dinheiro_round(saldo_liquido_total - max(valor_original_total - total_liquido_sacado, 0.0)),
    }

    if df_relatorio.empty:
        df_relatorio = pd.DataFrame([total_row])
    else:
        df_relatorio = pd.concat([df_relatorio, pd.DataFrame([total_row])], ignore_index=True)

    resumo = pd.DataFrame([{
        'Estratégia': estrategia,
        'Modo': modo,
        'Data Terminal': data_ref,
        'Saldo Bruto Atual (R$)': dinheiro_round(saldo_bruto_total),
        'Saldo Líquido Atual (R$)': dinheiro_round(saldo_liquido_total),
        'Total Líquido Sacado (R$)': dinheiro_round(total_liquido_sacado),
        'Patrimônio Líquido até Hoje (R$)': dinheiro_round(patrimonio_liquido_total),
        'Valor Não Coberto (R$)': dinheiro_round(float(valor_nao_coberto or 0.0)),
        'Saldo Líq Aj. (R$)': dinheiro_round(float(saldo_liquido_total) - float(valor_nao_coberto or 0.0)),
        'WF': round(float(info_wf.get('score_robustez', info_ranking.get('WF', 0.0)) or 0.0), 2),
        'Score': round(float(info_ranking.get('Score', 0.0) or 0.0), 2),
        'Lotes Ativos': int(lotes_ativos),
        'Total Lotes': int(total_lotes),
    }])

    return df_relatorio, resumo

# =========================================================
# 12A. HELPERS DE POOL / SWITCH FUTURO
# =========================================================
def _taxa_eff(prod) -> float:
    if prod is None:
        return 1.0
    if getattr(prod, 'is_combo', False):
        return float(getattr(prod, 'taxa_combo_equivalente', getattr(prod, 'taxa_base', 1.0)) or 1.0)
    return float(getattr(prod, 'taxa_base', 1.0) or 1.0)

def _switch_detalhe_dict(data_cur, lote_origem, produto_origem, taxa_origem, taxa_destino,
                         bruto_resgatado, liquido_resgatado, imposto_resgate, parte,
                         produto_destino, valor_parte, soma_partes, diff_total,
                         combo_total=None, combo_razao=None, combo_produto_base=None,
                         combo_produto_bonus=None, combo_base=None, combo_bonus=None,
                         valor_planejado_total=None, valor_executado_total=None,
                         status_execucao=None, motivo_desvio=None):
    return {
        'Data': data_cur,
        'Lote_Origem': lote_origem,
        'Produto_Origem': produto_origem,
        'Taxa_Origem': round(float(taxa_origem), 6) if taxa_origem is not None else None,
        'Taxa_Destino': round(float(taxa_destino), 6) if taxa_destino is not None else None,
        'Bruto_Resgatado': round(float(bruto_resgatado), 2) if bruto_resgatado is not None else None,
        'Liquido_Resgatado': round(float(liquido_resgatado), 2) if liquido_resgatado is not None else None,
        'Imposto_Resgate': round(float(imposto_resgate), 2) if imposto_resgate is not None else None,
        'Parte': parte,
        'Produto_Destino': produto_destino,
        'Valor_Parte': round(float(valor_parte), 2),
        'Combo_Total': round(float(combo_total), 2) if combo_total is not None else None,
        'Combo_Razao': combo_razao,
        'Combo_Produto_Base': combo_produto_base,
        'Combo_Produto_Bonus': combo_produto_bonus,
        'Combo_Base': round(float(combo_base), 2) if combo_base is not None else None,
        'Combo_Bonus': round(float(combo_bonus), 2) if combo_bonus is not None else None,
        'Soma_Partes': round(float(soma_partes), 2),
        'Diff_Total': round(float(diff_total), 2),
        'Valor_Planejado_Total': round(float(valor_planejado_total), 2) if valor_planejado_total is not None else None,
        'Valor_Executado_Total': round(float(valor_executado_total), 2) if valor_executado_total is not None else None,
        'Status_Execucao': status_execucao,
        'Motivo_Desvio': motivo_desvio,
    }

def _append_switch_detalhes(switches_detalhados, data_cur, lote_origem, produto_origem, taxa_origem,
                            bruto_resgatado, liquido_resgatado, imposto_resgate, alocacoes,
                            total_plano, diff_total, verbose=False,
                            valor_planejado_total=None, valor_executado_total=None,
                            status_execucao=None, motivo_desvio=None):
    acumulado = 0.0
    for j, (pp, vv) in enumerate(alocacoes, 1):
        vv = round(float(vv), 2)
        if vv <= 0.00:
            continue
        acumulado = round(acumulado + vv, 2)
        restante = round(float(liquido_resgatado or 0.0) - acumulado, 2)
        if abs(restante) < 0.005:
            restante = 0.0
        taxa_destino = _taxa_eff(pp)
        if isinstance(pp, ComboProduto):
            vb, vx = pp.dividir_valor(vv)
            vb = round(float(vb), 2)
            vx = round(float(vx), 2)
            if verbose:
                print(f"         - Parte {j}: Combo {pp.nome} total R$ {vv:,.2f} (2:1) => base R$ {vb:,.2f} | bônus R$ {vx:,.2f} | restante R$ {restante:,.2f}")
            switches_detalhados.append(_switch_detalhe_dict(
                data_cur, lote_origem, produto_origem, taxa_origem, taxa_destino,
                bruto_resgatado, liquido_resgatado, imposto_resgate, j, pp.nome, vv,
                total_plano, diff_total, combo_total=vv,
                combo_razao=f"{pp.razao_base:.0f}:{pp.razao_bonus:.0f}",
                combo_produto_base=pp.produto_base.nome,
                combo_produto_bonus=pp.produto_bonus.nome,
                combo_base=vb, combo_bonus=vx,
                valor_planejado_total=valor_planejado_total,
                valor_executado_total=valor_executado_total,
                status_execucao=status_execucao,
                motivo_desvio=motivo_desvio,
            ))
        else:
            vmax_pp = float(getattr(pp, 'valor_max', 1e18) or 1e18)
            vmin_pp = float(getattr(pp, 'valor_min', 0.0) or 0.0)
            lim_txt = f" (min {vmin_pp:,.0f} / max {vmax_pp:,.0f})" if (vmax_pp < 1e17 or vmin_pp > 0) else ''
            if verbose:
                print(f"         - Parte {j}: {pp.nome} R$ {vv:,.2f}{lim_txt} | restante R$ {restante:,.2f}")
            switches_detalhados.append(_switch_detalhe_dict(
                data_cur, lote_origem, produto_origem, taxa_origem, taxa_destino,
                bruto_resgatado, liquido_resgatado, imposto_resgate, j, pp.nome, vv,
                total_plano, diff_total,
                valor_planejado_total=valor_planejado_total,
                valor_executado_total=valor_executado_total,
                status_execucao=status_execucao,
                motivo_desvio=motivo_desvio,
            ))

def _criar_lotes_alocacao_switch(alocacoes, data_cur, prefixo_id, novos_lotes, lotes_ativos):
    for i_al, (prod, val) in enumerate(alocacoes):
        val = float(val)
        if val <= 0.01:
            continue
        if isinstance(prod, ComboProduto):
            vb, vx = prod.dividir_valor(val)
            if vb > 0:
                nb = Lote(
                    f"{prefixo_id}_{i_al}_B", data_cur, vb,
                    produto=prod.produto_base, data_base_fiscal=data_cur,
                    carencia_ate=(data_cur + timedelta(days=prod.produto_base.carencia_dias))
                    if prod.produto_base.carencia_dias > 0 else None,
                )
                novos_lotes.append(nb)
                lotes_ativos.append(nb)
            if vx > 0:
                nx = Lote(
                    f"{prefixo_id}_{i_al}_X", data_cur, vx,
                    produto=prod.produto_bonus, data_base_fiscal=data_cur,
                    carencia_ate=(data_cur + timedelta(days=prod.produto_bonus.carencia_dias))
                    if prod.produto_bonus.carencia_dias > 0 else None,
                )
                novos_lotes.append(nx)
                lotes_ativos.append(nx)
        else:
            nn = Lote(
                f"{prefixo_id}_{i_al}", data_cur, val,
                produto=prod, data_base_fiscal=data_cur,
                carencia_ate=(data_cur + timedelta(days=prod.carencia_dias))
                if prod.carencia_dias > 0 else None,
            )
            novos_lotes.append(nn)
            lotes_ativos.append(nn)

def _calcular_plano_pool_switch(lotes_switch_dia, data_cur, produtos, contas_ord, bcb_map,
                                planos_pool_switch):
    contas_fut = [c for c in contas_ord if c[0] >= data_cur]
    total_liquido_pool = 0.0
    aloc_pool = []
    plano_predefinido = None

    if planos_pool_switch and data_cur in planos_pool_switch:
        _total_liquido_pool_pre, aloc_pool_pre = planos_pool_switch.get(data_cur, (0.0, []))
        plano_predefinido = [(p, float(v)) for p, v in aloc_pool_pre if float(v) > 0.01]

    if plano_predefinido:
        aloc_pool = list(plano_predefinido)
        for l in lotes_switch_dia:
            fl = l.get_fator_liquido(data_cur)
            total_liquido_pool += max(0.0, l.saldo_bruto * fl)
        soma_plano = sum(float(v) for _, v in aloc_pool)
        if soma_plano > 0.01 and total_liquido_pool > 0.01 and abs(soma_plano - total_liquido_pool) > 0.01:
            fator_ajuste = total_liquido_pool / soma_plano
            aloc_pool = [(p, float(v) * fator_ajuste) for p, v in aloc_pool]
        return aloc_pool, total_liquido_pool

    if not REOTIMIZAR_POOL_SWITCH_NO_FUTURO:
        por_prod = {}
        for l in lotes_switch_dia:
            fl = l.get_fator_liquido(data_cur)
            liq = max(0.0, l.saldo_bruto * fl)
            total_liquido_pool += liq
            _, prod_alvo = l.switch_agendado
            if prod_alvo and prod_alvo.ativo and prod_alvo.aceita_aporte(liq):
                por_prod[prod_alvo] = por_prod.get(prod_alvo, 0.0) + liq
        if por_prod:
            return [(pp, vv) for pp, vv in por_prod.items() if vv > 0.01], total_liquido_pool

    for l in lotes_switch_dia:
        fl = l.get_fator_liquido(data_cur)
        total_liquido_pool += max(0.0, l.saldo_bruto * fl)
    aloc_pool, _, _ = alocar_lote_por_otimizacao(
        data_cur, data_cur, total_liquido_pool, produtos, bcb_map, contas_fut,
        foco_rendimento=True, max_produtos=3,
    )
    return aloc_pool, total_liquido_pool

def _executar_pool_switch_dia(data_cur, lotes_switch_dia, produtos, contas_ord, bcb_map,
                              planos_pool_switch, switches_detalhados, novos_lotes,
                              lotes_ativos, verbose=False):
    aloc_pool, total_liquido_pool = _calcular_plano_pool_switch(
        lotes_switch_dia, data_cur, produtos, contas_ord, bcb_map, planos_pool_switch
    )
    if not aloc_pool:
        return

    if verbose:
        print(f"   [SWITCH-POOL] {data_cur} | {len(lotes_switch_dia)} lotes | líquido total R$ {total_liquido_pool:,.2f}")
        for j, (pp, vv) in enumerate(aloc_pool, 1):
            if isinstance(pp, ComboProduto):
                vb, vx = pp.dividir_valor(vv)
                print(f"      -> Pool Parte {j}: Combo {pp.nome} | base R$ {vb:,.2f} | bonus R$ {vx:,.2f}")
            else:
                print(f"      -> Pool Parte {j}: {pp.nome} (R$ {vv:,.2f})")

    try:
        origem_ids = ';'.join([str(_l.id) for _l in lotes_switch_dia])
    except Exception:
        origem_ids = ''
    total_plano_pool = sum(float(v) for _, v in aloc_pool) if aloc_pool else 0.0
    try:
        _num = 0.0
        _den = 0.0
        for _l in lotes_switch_dia:
            _saldo = float(getattr(_l, 'saldo_atual', 0.0) or 0.0)
            _t = float(_taxa_eff(getattr(_l, 'produto', None)))
            if _saldo > 0 and _t > 0:
                _num += _saldo * _t
                _den += _saldo
        taxa_origem_pool = (_num / _den) if _den > 0 else 1.0
    except Exception:
        taxa_origem_pool = 1.0

    _append_switch_detalhes(
        switches_detalhados, data_cur, f"POOL[{origem_ids}]", 'POOL', taxa_origem_pool,
        None, total_liquido_pool, None, aloc_pool, total_plano_pool,
        float(total_liquido_pool) - float(total_plano_pool), verbose=verbose,
        valor_planejado_total=total_plano_pool,
        valor_executado_total=total_plano_pool,
        status_execucao='execucao_fiel',
        motivo_desvio=None,
    )

    for l in lotes_switch_dia:
        l.esgotado = True
        l.saldo_bruto = 0.0
        l.switch_agendado = None

    _criar_lotes_alocacao_switch(
        aloc_pool, data_cur, f"POOLSW_{data_cur.strftime('%Y%m%d')}", novos_lotes, lotes_ativos
    )

def _scale_plano_switch(plano_ref, total_liq):
    if not plano_ref:
        return []
    soma = sum(float(v) for _, v in plano_ref if float(v) > 0.0)
    if soma <= 0.01:
        return []
    fator = float(total_liq) / soma
    return [(pp, float(v) * fator) for pp, v in plano_ref]

def _avaliar_switching_e_diagnosticos(
    lotes_passados,
    lotes_futuros,
    contas,
    produtos,
    bcb_map,
    hoje,
    estado_lotes_passado_snapshot=None,
    log_passado=None,
    data_referencia_snapshot=None,
    contexto_canonico=None,
):
    print("\n>>> [SWITCHING] Avaliando switches para os lotes atuais...")
    switches_agendados = 0
    switches_hoje_exec = 0
    lotes_novos_hoje = []

    for l in lotes_passados:
        if l.saldo_bruto > 0.01:
            l.esgotado = False
        if l.produto is None:
            l.produto = PRODUTO_PADRAO

    df_situacao_atual = pd.DataFrame()
    idx_situacao_atual = pd.DataFrame()

    if isinstance(contexto_canonico, dict):
        df_situacao_atual = _df_or_empty(contexto_canonico.get('df_situacao_atual_canonica'))
        idx_situacao_atual = _df_or_empty(contexto_canonico.get('idx_situacao_atual_canonica'))

    if df_situacao_atual.empty and estado_lotes_passado_snapshot is not None and log_passado is not None:
        try:
            estado_rows = (
                estado_lotes_passado_snapshot.to_dict('records')
                if isinstance(estado_lotes_passado_snapshot, pd.DataFrame)
                else list(estado_lotes_passado_snapshot or [])
            )
            valores_originais = {
                str(st.get('Lote ID', '')).strip(): float(st.get('Valor Inicial', 0.0) or 0.0)
                for st in estado_rows
                if str(st.get('Lote ID', '')).strip()
            }
        except Exception:
            valores_originais = {}

        df_situacao_atual = gerar_relatorio_situacao_atual(
            lotes_hoje=lotes_passados,
            estado_lotes_passado=estado_lotes_passado_snapshot,
            log_passado=log_passado,
            valores_originais=valores_originais,
            mapa_bcb=bcb_map,
            data_referencia=hoje,
        )

    decisoes_sw, analise_switch, riqueza_base, riqueza_final = otimizar_switches_portfolio_guloso(
        lotes_passados, contas, produtos, bcb_map, hoje, max_iter=12, min_ganho_abs=5.0, verbose=_debug_ativo(DEBUG_SWITCH_EXECUCAO)
    )
    _log_debug(f"    baseline R$ {riqueza_base:,.2f} -> potencial final R$ {riqueza_final:,.2f}", DEBUG_SWITCH_EXECUCAO)

    lotes_por_id = {l.id: l for l in lotes_passados}
    grupos_sw = {}
    for lid, (d_sw, p_sw, ganho) in list(decisoes_sw.items()):
        grupos_sw.setdefault(d_sw, []).append(lid)

    for d_sw, ids in grupos_sw.items():
        if len(ids) < 2:
            continue
        total_sw = sum(max(0.0, lotes_por_id[i].saldo_bruto) for i in ids if i in lotes_por_id)
        if total_sw <= 0.01:
            continue
        aloc_sw, _, _ = alocar_lote_por_otimizacao(
            hoje, d_sw, total_sw, produtos, bcb_map, contas, foco_rendimento=True, max_produtos=2
        )
        if not aloc_sw:
            continue
        orig_prod_set = {decisoes_sw[i][1].nome for i in ids if i in decisoes_sw}
        pool_prod_set = {p_alvo.nome for p_alvo, _ in aloc_sw}
        max_taxa_orig = max(float(getattr(decisoes_sw[i][1], 'taxa_base', 1.0) or 1.0) for i in ids if i in decisoes_sw)
        max_taxa_pool = max(float(getattr(p_alvo, 'taxa_base', 1.0) or 1.0) for p_alvo, _ in aloc_sw)
        if len(pool_prod_set) == 1 and len(orig_prod_set) > 1 and max_taxa_pool + 1e-9 < max_taxa_orig:
            continue
        bucket = [[p_alvo, float(v_alvo)] for p_alvo, v_alvo in aloc_sw]
        ids_ord = sorted(ids, key=lambda x: lotes_por_id[x].saldo_bruto if x in lotes_por_id else 0.0, reverse=True)
        for lid in ids_ord:
            lobj = lotes_por_id.get(lid)
            if lobj is None:
                continue
            val = lobj.saldo_bruto
            escolha = None
            for k, (p_alvo, disp) in enumerate(bucket):
                if disp + 0.01 >= val and p_alvo.aceita_aporte(val):
                    escolha = k
                    break
            if escolha is None:
                candidatos_ok = [b for b in bucket if b[0].aceita_aporte(val)]
                if candidatos_ok:
                    p_alvo = max(candidatos_ok, key=lambda b: float(getattr(b[0], 'taxa_base', 1.0) or 1.0))[0]
                    ganho_ant = decisoes_sw[lid][2]
                    decisoes_sw[lid] = (d_sw, p_alvo, ganho_ant)
                continue
            p_alvo, disp = bucket[escolha]
            bucket[escolha][1] = max(0.0, disp - val)
            ganho_ant = decisoes_sw[lid][2]
            decisoes_sw[lid] = (d_sw, p_alvo, ganho_ant)

    validacao_pool = []
    datas_futuras = [d for (_lid, (d, _p, _g)) in decisoes_sw.items() if d != hoje]
    data_pool_ref = None
    if datas_futuras:
        cont = {}
        for d in datas_futuras:
            cont[d] = cont.get(d, 0) + 1
        data_pool_ref = max(cont, key=cont.get)

    if data_pool_ref is not None:
        analise_por_lote_data = {}
        for a in analise_switch:
            lid = a.get('Lote ID')
            dsw = a.get('Data Switch')
            if lid and dsw:
                analise_por_lote_data[(lid, dsw)] = a
        for lid, (d_sw, p_sw, g_sw) in list(decisoes_sw.items()):
            if d_sw != hoje:
                continue
            cand = analise_por_lote_data.get((lid, data_pool_ref))
            if not cand:
                continue
            ganho_pool = float(cand.get('Ganho Estimado', 0.0) or 0.0)
            prod_pool = cand.get('Produto Candidato')
            if ganho_pool >= 0.90 * float(g_sw):
                p_obj = next((pp for pp in produtos if pp.nome == prod_pool), None)
                if p_obj is not None and p_obj.ativo:
                    decisoes_sw[lid] = (data_pool_ref, p_obj, ganho_pool)
                    validacao_pool.append({
                        'Lote ID': lid,
                        'Data Original': d_sw,
                        'Produto Original': p_sw.nome if hasattr(p_sw, 'nome') else str(p_sw),
                        'Ganho Original': round(float(g_sw), 2),
                        'Data Ajustada': data_pool_ref,
                        'Produto Ajustado': p_obj.nome,
                        'Ganho Ajustado': round(float(ganho_pool), 2),
                        'Motivo': 'Alinhamento para pooling',
                    })

    melhores_por_lote = {}
    for a in analise_switch:
        lid = a.get('Lote ID')
        sf = float(a.get('Score Final', 0.0) or 0.0)
        if lid not in melhores_por_lote or sf > melhores_por_lote[lid]['Score Final']:
            melhores_por_lote[lid] = {
                'Score Final': sf,
                'Produto Candidato': a.get('Produto Candidato'),
                'Data Switch': a.get('Data Switch'),
                'Ganho Estimado': a.get('Ganho Estimado', 0.0),
            }

    planos_pool_switch = {}
    plano_switches = []
    df_switch_view = df_situacao_atual.copy() if isinstance(df_situacao_atual, pd.DataFrame) else pd.DataFrame()
    if not df_switch_view.empty and 'Lote ID' in df_switch_view.columns:
        df_switch_view = df_switch_view[df_switch_view['Lote ID'].astype(str) != 'TOTAL'].copy()
        if 'Data Aplicação' in df_switch_view.columns:
            datas_aplic = pd.to_datetime(df_switch_view['Data Aplicação'], errors='coerce')
            df_switch_view = df_switch_view[datas_aplic.dt.date <= hoje].copy()
        cols_ord = [c for c in ['Data Aplicação', 'Lote ID'] if c in df_switch_view.columns]
        if cols_ord:
            df_switch_view = df_switch_view.sort_values(cols_ord).reset_index(drop=True)

    for _, row_atual in df_switch_view.iterrows():
        lote_id = str(row_atual.get('Lote ID', '')).strip()
        if not lote_id:
            continue
        carteira_nome = str(row_atual.get('Carteira', '-') or '-')
        saldo_bruto_atual = float(row_atual.get('Saldo Bruto Atual (R$)', 0.0) or 0.0)
        saldo_liquido_atual = float(row_atual.get('Saldo Líquido Atual (R$)', 0.0) or 0.0)
        print(
            f"    - Lote {lote_id}: {carteira_nome} | "
            f"bruto atual R$ {saldo_bruto_atual:,.2f} | "
            f"líquido atual R$ {saldo_liquido_atual:,.2f} | ",
            end='',
        )
        if lote_id not in decisoes_sw:
            info = melhores_por_lote.get(lote_id)
            if info:
                print(f"manter. melhor candidato seria {info['Produto Candidato']} em {info['Data Switch']}")
            else:
                print("manter. (sem candidato viável)")
            continue

        data_sw, prod_alvo, ganho = decisoes_sw[lote_id]
        valor_aplicar = saldo_liquido_atual
        lobj = lotes_por_id.get(lote_id)

        if data_sw == hoje:
            print(f"SWITCH HOJE -> {prod_alvo.nome} | aplicar ~R$ {valor_aplicar:,.2f}")
            plano_switches.append({'Data': hoje, 'Origem': lote_id, 'Produto': prod_alvo.nome, 'Valor': round(valor_aplicar, 2), 'Ganho_Estimado': round(ganho, 2), 'Tipo': 'Switch'})
            if lobj is None or not prod_alvo.ativo:
                if lobj is None:
                    print("      (lote não ativo no motor de switching, sem execução real)")
                elif not prod_alvo.ativo:
                    print("      (produto inativo, ignorado)")
                continue
            novos = lobj.switch_para(prod_alvo, hoje)
            lotes_novos_hoje.extend(novos)
            switches_hoje_exec += 1
        else:
            delta_lote_ate_switch = None
            if lobj is not None:
                try:
                    liq_switch_prev = float(estimar_liquido_lote_sem_pagamentos(lobj, data_sw, bcb_map))
                    delta_lote_ate_switch = liq_switch_prev - float(valor_aplicar or 0.0)
                except Exception:
                    delta_lote_ate_switch = None
            delta_txt = f" | delta lote até switch R$ {delta_lote_ate_switch:,.2f}" if delta_lote_ate_switch is not None else ""
            print(f"AGENDAR {data_sw} -> {prod_alvo.nome} | aplicar ~R$ {valor_aplicar:,.2f}{delta_txt}")
            plano_switches.append({'Data': data_sw, 'Origem': lote_id, 'Produto': prod_alvo.nome, 'Valor': round(valor_aplicar, 2), 'Ganho_Estimado': round(ganho, 2), 'Tipo': 'Switch'})
            if lobj is not None:
                lobj.switch_agendado = (data_sw, prod_alvo)
                try:
                    liq_est = float(estimar_liquido_lote_sem_pagamentos(lobj, data_sw, bcb_map))
                except Exception:
                    liq_est = max(0.0, float(getattr(lobj, 'saldo_bruto', 0.0) or 0.0))
                if liq_est > 0.01:
                    contas_fut_sw = [c for c in contas if c[0] >= data_sw]
                    planos_top = gerar_top_planos_alocacao(data_sw, liq_est, produtos, bcb_map, contas_fut_sw, top_k=1)
                    lobj.switch_plano = planos_top[0] if planos_top else None
            switches_agendados += 1

    grupos_agendados = {}
    for l in lotes_passados:
        if not l.esgotado and l.switch_agendado is not None:
            d_sw, _ = l.switch_agendado
            grupos_agendados.setdefault(d_sw, []).append(l)

    for d_sw, lotes_d in sorted(grupos_agendados.items(), key=lambda x: x[0]):
        if len(lotes_d) < 2:
            continue
        total_liq = sum(max(0.0, estimar_liquido_lote_sem_pagamentos(lx, d_sw, bcb_map)) for lx in lotes_d)
        if total_liq <= 0.01:
            continue
        contas_fut_d = [c for c in contas if c[0] >= d_sw]
        aloc_pool, top_pool, _ = alocar_lote_por_otimizacao(hoje, d_sw, total_liq, produtos, bcb_map, contas_fut_d, foco_rendimento=True, max_produtos=3)
        if not aloc_pool:
            continue
        planos_pool_switch[d_sw] = (float(total_liq), list(aloc_pool))
        print(f"\n  [POOL SWITCH {d_sw}] {len(lotes_d)} lote(s) | líquido consolidado R$ {total_liq:,.2f}")
        for i, (pp, vv) in enumerate(aloc_pool, 1):
            if isinstance(pp, ComboProduto):
                vb, vx = pp.dividir_valor(vv)
                print(f"     {i:>2}. Combo {pp.nome:<24} total R$ {vv:>10,.2f} | base R$ {vb:>9,.2f} | bônus R$ {vx:>9,.2f}")
            else:
                taxa = float(getattr(pp, 'taxa_base', 1.0) or 1.0) * 100.0
                print(f"     {i:>2}. {pp.nome:<30} R$ {vv:>10,.2f} | taxa {taxa:>6.2f}% CDI")
        if top_pool:
            print(f"       TOP pool: {top_pool}")

    lotes_passados.extend(lotes_novos_hoje)
    plano_switches_final = []
    datas_pool = set(planos_pool_switch.keys())
    for item in plano_switches:
        if item.get('Data') not in datas_pool:
            plano_switches_final.append(item)
    for d_sw, pool_info in sorted(planos_pool_switch.items(), key=lambda x: x[0]):
        _total_liquido_pool, aloc = pool_info
        for prod_sw, val_sw in aloc:
            nome_sw = prod_sw.nome if hasattr(prod_sw, 'nome') else str(prod_sw)
            plano_switches_final.append({'Data': d_sw, 'Origem': 'POOL', 'Produto': nome_sw, 'Valor': round(float(val_sw), 2), 'Ganho_Estimado': None, 'Tipo': 'Switch-POOL'})

    _imprimir_resumo_consolidado_switches(plano_switches_final)
    todos_lotes_pre = lotes_passados + lotes_futuros
    diag_datas, diag_planos = [], []
    df_comparativo_validacao = pd.DataFrame()

    try:
        diag_datas, diag_planos, _ = gerar_diagnostico_switches_portfolio(
            todos_lotes_pre, contas, produtos, bcb_map, hoje, janela_datas=7, top_k=5
        )
    except Exception as e:
        print(f"   [WARN] Falha ao gerar diagnóstico de switches: {e}")

    try:
        gerador_comparativo = globals().get('_gerar_comparativo_validacao_switching')
        if callable(gerador_comparativo):
            df_comparativo_validacao = gerador_comparativo(
                todos_lotes_pre, contas, produtos, bcb_map, hoje, planos_pool_switch, diag_datas, diag_planos
            )
    except Exception as e:
        print(f"   [WARN] Falha ao gerar comparativo de validação: {e}")

    if getattr(idx_situacao_atual, 'empty', True) and isinstance(df_situacao_atual, pd.DataFrame) and not df_situacao_atual.empty:
        try:
            idx_situacao_atual = df_situacao_atual.set_index('Lote ID', drop=False)
        except Exception:
            idx_situacao_atual = df_situacao_atual.copy()

    return {
        'lotes_passados': lotes_passados,
        'lotes_futuros': lotes_futuros,
        'planos_pool_switch': planos_pool_switch,
        'plano_switches_final': plano_switches_final,
        'switches_agendados': switches_agendados,
        'switches_hoje_exec': switches_hoje_exec,
        'analise_switch': analise_switch,
        'validacao_pool': validacao_pool,
        'diag_datas': diag_datas,
        'diag_planos': diag_planos,
        'df_comparativo_validacao': df_comparativo_validacao,
        'df_situacao_atual': df_situacao_atual,
        'idx_situacao_atual': idx_situacao_atual,
        'riqueza_base_switch': riqueza_base,
        'riqueza_final_switch': riqueza_final,
    }

def _gerar_comparativo_validacao_switching(base_lotes_cenarios, contas, produtos, bcb_map, hoje, planos_pool_switch, diag_datas, diag_planos):
    df_diag_datas_local = pd.DataFrame(diag_datas) if isinstance(diag_datas, list) else pd.DataFrame()
    df_diag_planos_local = pd.DataFrame(diag_planos) if isinstance(diag_planos, list) else pd.DataFrame()

    def _limpar_switches(lotes_):
        for lx in lotes_:
            lx.switch_agendado = None
            lx.switch_plano = None

    def _recalcular_plano_para_lote(lx, data_sw):
        liq_est = max(0.0, estimar_liquido_lote_sem_pagamentos(lx, data_sw, bcb_map))
        if liq_est <= 0.01:
            return None
        contas_fut = [c for c in contas if c[0] >= data_sw]
        planos = gerar_top_planos_alocacao(data_sw, liq_est, produtos, bcb_map, contas_fut, top_k=1)
        return planos[0] if planos else None

    def _aplicar_melhor_data(lotes_):
        if df_diag_datas_local.empty:
            return
        best_by_lote = (df_diag_datas_local.sort_values(['Lote ID', 'Rank (Data)']).groupby('Lote ID', as_index=False).first())
        mapa = {lx.id: lx for lx in lotes_}
        for _, rr in best_by_lote.iterrows():
            lid = rr['Lote ID']
            if lid not in mapa:
                continue
            lx = mapa[lid]
            if not lx.switch_agendado:
                continue
            _, prod_alvo = lx.switch_agendado
            d_best = rr['Data Avaliada']
            lx.switch_agendado = (d_best, prod_alvo)
            lx.switch_plano = _recalcular_plano_para_lote(lx, d_best)

    def _aplicar_melhor_plano(lotes_):
        prod_by_name = {p.nome: p for p in produtos}
        best_plans = pd.DataFrame()
        if not df_diag_planos_local.empty:
            best_plans = (df_diag_planos_local.sort_values(['Lote ID', 'Rank (Plano)']).groupby('Lote ID', as_index=False).first())
        for lx in lotes_:
            if not lx.switch_agendado:
                continue
            lid = lx.id
            d, _ = lx.switch_agendado
            plano = None
            if not best_plans.empty:
                row = best_plans[best_plans['Lote ID'] == lid]
                if not row.empty:
                    s = str(row.iloc[0].get('Plano (Produto=Valor)', '')).strip()
                    partes = []
                    if s:
                        for tok in s.split(';'):
                            tok = tok.strip()
                            if not tok or '=' not in tok:
                                continue
                            nome, vv = tok.split('=', 1)
                            nome = nome.strip()
                            try:
                                valor = float(str(vv).replace('.', '').replace(',', '.'))
                            except Exception:
                                try:
                                    valor = float(vv)
                                except Exception:
                                    valor = None
                            if valor is None:
                                continue
                            pobj = prod_by_name.get(nome)
                            if pobj is None:
                                continue
                            partes.append((pobj, float(valor)))
                    if partes:
                        plano = partes
            if plano is None:
                plano = _recalcular_plano_para_lote(lx, d)
            lx.switch_plano = plano

    def _rodar_pooling_expandido(nome='Pooling Expandido (min altos)', janela_extra=7, max_lotes_considerar=10, max_n_bruteforce=12):
        min_alvo = 10000.0
        for p in produtos:
            if isinstance(p, Produto) and re.search(r'\bXP\s*150\b', p.nome, re.I):
                try:
                    min_alvo = float(getattr(p, 'valor_min', 10000.0) or 10000.0)
                except Exception:
                    min_alvo = 10000.0
                break
        datas = set()
        if not df_diag_datas_local.empty and 'Data Avaliada' in df_diag_datas_local.columns:
            for _, rr in df_diag_datas_local.sort_values(['Rank (Data)']).head(12).iterrows():
                d = rr.get('Data Avaliada')
                if isinstance(d, (date, datetime)):
                    datas.add(d if isinstance(d, date) else d.date())
        for lx in base_lotes_cenarios:
            if getattr(lx, 'switch_agendado', None):
                d, _ = lx.switch_agendado
                if isinstance(d, date):
                    for k in range(-janela_extra, janela_extra + 1):
                        datas.add(d + timedelta(days=k))
        datas = sorted([d for d in datas if d >= hoje])
        melhor = None
        for d in datas:
            cand = []
            for lx in base_lotes_cenarios:
                if lx.esgotado:
                    continue
                if not PERMITIR_SWITCH_ANTES_30_DIAS and (d - lx.data_aplicacao).days < 30:
                    continue
                liq_est = float(max(0.0, estimar_liquido_lote_sem_pagamentos(lx, d, bcb_map)))
                if liq_est <= 0.01:
                    continue
                cand.append((liq_est, lx.id))
            if len(cand) < 2:
                continue
            cand.sort(reverse=True, key=lambda x: x[0])
            cand = cand[:max_lotes_considerar]
            liq_map = {lid: liq for liq, lid in cand}
            lids = list(liq_map.keys())
            n = len(lids)
            subsets = []
            if n <= max_n_bruteforce:
                for r in range(2, n + 1):
                    for comb in itertools.combinations(lids, r):
                        s = sum(liq_map[i] for i in comb)
                        if s + 0.01 >= min_alvo:
                            subsets.append((s, comb))
            else:
                s = 0.0
                comb = []
                for lid in lids:
                    comb.append(lid)
                    s += liq_map[lid]
                    if s + 0.01 >= min_alvo and len(comb) >= 2:
                        subsets.append((s, tuple(comb)))
                        break
            if not subsets:
                continue
            subsets.sort(reverse=True, key=lambda x: x[0])
            subsets = subsets[:30]
            for s, comb in subsets:
                lotes_cen = copy.deepcopy(base_lotes_cenarios)
                mapa = {x.id: x for x in lotes_cen}
                ok = True
                for lid in comb:
                    if lid not in mapa:
                        ok = False
                        break
                    mapa[lid].switch_agendado = (d, None)
                    mapa[lid].switch_plano = None
                if not ok:
                    continue
                _, met = simular_futuro(lotes_cen, contas, bcb_map, data_inicio=hoje, produtos=produtos, verbose=False)
                riqueza = float(met.get('riqueza', 0.0))
                if (melhor is None) or (riqueza > melhor[0] + 1e-9):
                    melhor = (riqueza, {'Data': d, 'Lotes Pool': ';'.join(map(str, comb)), 'Liquido Pool Est.': float(s), 'Min alvo': float(min_alvo)}, met)
        if melhor is None:
            return None
        riqueza, det, met = melhor
        return {'Cenário': nome, 'Riqueza Final': float(riqueza), 'Saldo Líquido Final': float(met.get('saldo_final', 0.0)), 'Imposto Pago': float(met.get('total_imposto', 0.0)), 'Total Resgatado': float(met.get('total_resgatado', 0.0)), 'Switches Executados': int(met.get('switches_exec', 0)), 'Detalhes': f"Data={det['Data']} | Pool={det['Lotes Pool']} | LiqEst={det['Liquido Pool Est.']:.2f} | MinAlvo={det['Min alvo']:.2f}"}

    def _rodar_cenario(nome, lotes_):
        lotes_run = copy.deepcopy(lotes_)
        _, st = simular_futuro(lotes_run, contas, bcb_map, data_inicio=hoje, produtos=produtos, planos_pool_switch=planos_pool_switch, verbose=False)
        return {'Cenário': nome, 'Riqueza Final': float(st.get('riqueza', 0.0)), 'Saldo Líquido Final': float(st.get('saldo_liquido', 0.0)), 'Imposto Pago': float(st.get('total_imposto', 0.0)), 'Total Resgatado': float(st.get('total_resgatado', 0.0)), 'Switches Executados': int(st.get('switches_exec', 0))}

    lotes_sem = copy.deepcopy(base_lotes_cenarios)
    _limpar_switches(lotes_sem)
    lotes_atual = copy.deepcopy(base_lotes_cenarios)
    lotes_best_date = copy.deepcopy(base_lotes_cenarios)
    _aplicar_melhor_data(lotes_best_date)
    lotes_best_plan = copy.deepcopy(base_lotes_cenarios)
    _aplicar_melhor_plano(lotes_best_plan)
    lotes_best_both = copy.deepcopy(base_lotes_cenarios)
    _aplicar_melhor_data(lotes_best_both)
    _aplicar_melhor_plano(lotes_best_both)
    rows = [
        _rodar_cenario('Sem Switching', lotes_sem),
        _rodar_cenario('Plano Atual', lotes_atual),
        _rodar_cenario('Melhor Data (diagnóstico)', lotes_best_date),
        _rodar_cenario('Melhor Plano (TOP1 no dia)', lotes_best_plan),
        _rodar_cenario('Melhor Data + Plano', lotes_best_both),
    ]
    try:
        row_pool = _rodar_pooling_expandido()
        if row_pool:
            rows.append(row_pool)
    except Exception:
        pass
    df = pd.DataFrame(rows)
    if not df.empty:
        base_val = float(df.loc[df['Cenário'] == 'Plano Atual', 'Riqueza Final'].iloc[0])
        df['Δ vs Plano Atual'] = df['Riqueza Final'] - base_val
    return df

def _aplicar_modo_execucao_futuro_final(todos_lotes, artefatos_switching, contas, produtos, bcb_map):
    modo = normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)
    if modo in ('dinamico', 'rigido_plano_externo'):
        return todos_lotes

    diag_datas = artefatos_switching.get('diag_datas') or []
    if not diag_datas:
        return todos_lotes

    df_diag = pd.DataFrame(diag_datas)
    if df_diag.empty or 'Lote ID' not in df_diag.columns or 'Data Avaliada' not in df_diag.columns:
        return todos_lotes

    try:
        df_diag = df_diag.sort_values(['Lote ID', 'Rank (Data)'])
    except Exception:
        df_diag = df_diag.sort_values(['Lote ID'])

    best_by_lote = df_diag.groupby('Lote ID', as_index=False).first()
    mapa_best = {str(r['Lote ID']).strip(): r for _, r in best_by_lote.iterrows()}

    for lote in todos_lotes:
        if not getattr(lote, 'switch_agendado', None):
            continue
        row = mapa_best.get(str(lote.id).strip())
        if row is None:
            continue

        data_best = row.get('Data Avaliada')
        if isinstance(data_best, pd.Timestamp):
            data_best = data_best.date()
        elif isinstance(data_best, datetime):
            data_best = data_best.date()
        if not isinstance(data_best, date):
            continue

        _, produto_alvo = lote.switch_agendado
        lote.switch_agendado = (data_best, produto_alvo)

        liquido_estimado = max(0.0, estimar_liquido_lote_sem_pagamentos(lote, data_best, bcb_map))
        if liquido_estimado <= 0.01:
            lote.switch_plano = None
            continue

        contas_fut = [c for c in contas if c[0] >= data_best]
        planos = gerar_top_planos_alocacao(data_best, liquido_estimado, produtos, bcb_map, contas_fut, top_k=1)
        lote.switch_plano = planos[0] if planos else None

    return todos_lotes

def _resolver_plano_switch_individual(lote, data_cur, liquido_sw, prod_alvo, produtos, bcb_map, contas_ord):
    contas_fut = [c for c in contas_ord if c[0] >= data_cur]
    aloc_sw = []
    valor_planejado_total = None
    valor_executado_total = None
    status_execucao = 'otimizado'
    motivo_desvio = None

    if getattr(lote, 'switch_plano', None):
        plano_ref = [(pp, float(v)) for pp, v in lote.switch_plano if float(v) > 0.01]
        soma_plano = sum(float(v) for _, v in plano_ref)
        if soma_plano > 0.01:
            valor_planejado_total = float(soma_plano)
            if normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO) == 'rigido_plano_externo':
                valor_executado_total = min(float(liquido_sw), float(soma_plano))
                fator = (valor_executado_total / soma_plano) if soma_plano > 0.01 else 0.0
                aloc_sw = [(pp, float(v) * fator) for pp, v in plano_ref if float(v) * fator > 0.01]
                if valor_executado_total + 0.01 < soma_plano:
                    status_execucao = 'ajustado'
                    motivo_desvio = 'saldo_insuficiente_no_dia'
                else:
                    status_execucao = 'execucao_fiel'
            else:
                aloc_sw = _scale_plano_switch(plano_ref, liquido_sw)
                valor_executado_total = sum(float(v) for _, v in aloc_sw)
                if abs(valor_executado_total - soma_plano) <= 0.01:
                    status_execucao = 'execucao_fiel'
                elif valor_executado_total + 0.01 < soma_plano:
                    status_execucao = 'ajustado'
                    motivo_desvio = 'saldo_insuficiente_no_dia'
                else:
                    status_execucao = 'ajustado'
                    motivo_desvio = 'escala_dinamica_do_plano'

            ok = True
            for pp, vv in aloc_sw:
                vv = float(vv)
                if vv <= 0.01:
                    continue
                if not getattr(pp, 'ativo', True) or not pp.aceita_aporte(vv):
                    ok = False
                    break
            if not ok:
                aloc_sw = []
                valor_executado_total = None
                status_execucao = 'fallback'
                motivo_desvio = 'plano_invalido_para_regras_do_produto'

    if not aloc_sw:
        aloc_sw, _, _ = alocar_lote_por_otimizacao(
            data_cur, data_cur, liquido_sw, produtos, bcb_map, contas_fut,
            foco_rendimento=True, max_produtos=3,
        )
        if aloc_sw:
            if valor_planejado_total is None:
                valor_planejado_total = sum(float(v) for _, v in aloc_sw)
            valor_executado_total = sum(float(v) for _, v in aloc_sw)
            if status_execucao == 'otimizado':
                motivo_desvio = motivo_desvio or 'sem_plano_predefinido'
            else:
                motivo_desvio = motivo_desvio or 'fallback_otimizacao'

    if not aloc_sw:
        aloc_sw = [(prod_alvo, liquido_sw)]
        valor_executado_total = float(liquido_sw)
        if valor_planejado_total is None:
            valor_planejado_total = float(liquido_sw)
        status_execucao = 'fallback'
        motivo_desvio = motivo_desvio or 'fallback_produto_alvo'

    return aloc_sw, valor_planejado_total, valor_executado_total, status_execucao, motivo_desvio

def _executar_switch_individual(lote, data_cur, prod_alvo, produtos, bcb_map, contas_ord,
                                switches_detalhados, novos_lotes, lotes_ativos, verbose=False):
    try:
        fl_est = lote.get_fator_liquido(data_cur)
        liq_est = max(0.0, lote.saldo_bruto * fl_est)
    except Exception:
        liq_est = max(0.0, lote.saldo_bruto)

    bruto_pre = float(lote.saldo_bruto)
    if verbose:
        print(f"   [SWITCH] {data_cur} | Lote {lote.id} | bruto R$ {lote.saldo_bruto:,.2f} | liq_est R$ {liq_est:,.2f} | {lote.produto.nome if lote.produto else 'Padrão'} → {prod_alvo.nome}")

    if not prod_alvo.ativo:
        print("      Aviso: Produto alvo inativo. Ignorado.")
        lote.switch_agendado = None
        return

    liquido_sw, imposto_sw = lote.resgatar_total(data_cur)
    if liquido_sw <= 0.01:
        lote.switch_agendado = None
        return

    aloc_sw, valor_planejado_total, valor_executado_total, status_execucao, motivo_desvio = _resolver_plano_switch_individual(
        lote, data_cur, liquido_sw, prod_alvo, produtos, bcb_map, contas_ord
    )
    total_plano = sum(float(v) for _, v in aloc_sw) if aloc_sw else 0.0
    diff_plano = float(liquido_sw) - float(total_plano)

    if verbose and aloc_sw:
        print(f"      [SPLIT] total_liq R$ {liquido_sw:,.2f} | partes {len(aloc_sw)} | soma_partes R$ {total_plano:,.2f} | diff R$ {diff_plano:,.2f}")
        if valor_planejado_total is not None:
            print(f"      [AUDIT] planejado R$ {float(valor_planejado_total):,.2f} | executado R$ {float(valor_executado_total or total_plano):,.2f} | status {status_execucao} | motivo {motivo_desvio or '-'}")

    _append_switch_detalhes(
        switches_detalhados, data_cur, lote.id, lote.produto.nome if lote.produto else 'Padrão',
        _taxa_eff(lote.produto), bruto_pre, liquido_sw, imposto_sw, aloc_sw,
        total_plano, diff_plano, verbose=verbose,
        valor_planejado_total=valor_planejado_total,
        valor_executado_total=valor_executado_total,
        status_execucao=status_execucao,
        motivo_desvio=motivo_desvio,
    )
    _criar_lotes_alocacao_switch(
        aloc_sw, data_cur, f"{lote.id}_sw_{data_cur.strftime('%Y%m%d')}", novos_lotes, lotes_ativos
    )
    lote.switch_agendado = None

def _ordenar_lotes_para_pagamento(lotes_disponiveis, data_cur: date, data_fim: date = None, ids_preferidos=None):
    ids_preferidos = set(str(x).strip() for x in (ids_preferidos or []) if str(x).strip())
    ranqueados = []
    for l in (lotes_disponiveis or []):
        try:
            custo = _fator_oportunidade_lote(l, data_cur, data_fim or data_cur)
        except Exception:
            try:
                custo = float(get_score_economico(l, data_cur))
            except Exception:
                custo = 0.0
        bonus_pref = -1e-9 if str(getattr(l, 'id', '')).strip() in ids_preferidos else 0.0
        ranqueados.append((custo + bonus_pref, l))
    ranqueados.sort(key=lambda x: x[0])
    return [l for _, l in ranqueados]

def processar_contas_do_dia(lotes: list, contas: list, data_ref: date):
    contas_hoje = [c for c in contas if c[0] == data_ref]
    data_fim = max((c[0] for c in contas), default=data_ref)

    def _sacar_do_lote(l, falta_local):
        fator = l.get_fator_liquido(data_ref)
        if fator <= 0:
            return falta_local
        bruto_nec = falta_local / fator
        uso = min(bruto_nec, l.saldo_bruto)
        efetivo = l.sacar(uso)
        liquido = round(efetivo * fator, 6)
        imposto = round(efetivo - liquido, 6)
        l.total_imposto_pago += imposto
        l.total_liquido_sacado += liquido
        return falta_local - liquido

    for conta in contas_hoje:
        _, valor_conta, desc, lote1, lote2, _ordem = _normalizar_conta_processamento(conta)
        falta = float(valor_conta)
        ids_preferidos = [str(x).strip() for x in [lote1, lote2] if x is not None and str(x).strip()]

        disponiveis = [
            l for l in lotes
            if not l.esgotado
            and l.saldo_bruto > 0.01
            and l.data_aplicacao <= data_ref
            and not (l.carencia_ate and data_ref < l.carencia_ate)
        ]
        ordenados = _ordenar_lotes_para_pagamento(
            disponiveis,
            data_ref,
            data_fim,
            ids_preferidos=ids_preferidos,
        )

        for l in ordenados:
            if falta <= 0.001:
                break
            falta = _sacar_do_lote(l, falta)

        if falta > 0.01 and EXIBIR_ALERTAS_FALTA_CAIXA:
            print(f"  ⚠  Falta R$ {falta:.2f} para pagar conta {desc} em {data_ref} (pré-switch)")

def rodar_estrategia(nome, aportes_in, contas_in, params_opt=None, bcb_map=None, taxa_proj=None, data_referencia=None, lotes_iniciais=None, data_inicio_competicao=None):
    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE

    aportes = [x for x in aportes_in]
    contas = [x for x in contas_in]

    aportes_por_data = {}
    for x in aportes:
        dt, val, id_l = x[0], x[1], x[2]
        meta = x[3] if len(x) > 3 and isinstance(x[3], dict) else {}
        aportes_por_data.setdefault(dt, []).append((dt, val, id_l, meta))

    contas_por_data = {}
    for item in contas:
        if len(item) >= 4:
            dt, valor, desc, ordem_processamento = item[0], item[1], item[2], item[3]
        else:
            dt, valor, desc, ordem_processamento = item[0], item[1], item[2], None
        contas_por_data.setdefault(dt, []).append((dt, valor, desc, ordem_processamento))
    for dt in list(contas_por_data.keys()):
        contas_por_data[dt] = ordenar_contas_processamento(contas_por_data[dt])

    lotes_iniciais = list(lotes_iniciais or [])
    data_inicio_competicao = data_inicio_competicao or data_referencia or DATA_REFERENCIA

    datas_aportes = [x[0] for x in aportes] if aportes else []
    datas_contas = [x[0] for x in contas] if contas else []

    if lotes_iniciais:
        d_ini = min([data_inicio_competicao] + datas_aportes + datas_contas) if (datas_aportes or datas_contas) else data_inicio_competicao
        d_ini = max(d_ini, data_inicio_competicao)
    else:
        d_ini = min(datas_aportes) if datas_aportes else DATA_REFERENCIA

    d_fim = max(datas_contas) if datas_contas else DATA_REFERENCIA
    if data_referencia is not None:
        d_fim = min(d_fim, data_referencia)
    horizonte_proj_dias = HORIZONTE_PROJECAO_DIAS
    d_proj = max(d_fim + timedelta(days=horizonte_proj_dias), d_fim)

    data_atual = d_ini
    lotes_pool = []
    lotes_ativos = []

    for item in lotes_iniciais:
        try:
            id_l, saldo_atual, meta = item
        except Exception:
            continue
        novo_lote = criar_lote_de_aporte(data_inicio_competicao, saldo_atual, id_l, meta or {})
        lotes_pool.append(novo_lote)
        lotes_ativos.append(novo_lote)
    log = []
    evento_financeiro_global = 1
    valor_contas_total = 0.0
    valor_nao_coberto = 0.0
    contas_nao_cobertas = 0

    while data_atual <= d_fim:
        novos = aportes_por_data.get(data_atual, [])
        for dt, val, id_l, meta in novos:
            novo_lote = criar_lote_de_aporte(dt, val, id_l, meta)
            lotes_pool.append(novo_lote)
            lotes_ativos.append(novo_lote)

        atualizar_saldo_lotes_no_dia(lotes_ativos, data_atual, bcb_map=bcb_map, taxa_proj=taxa_proj)

        if lotes_ativos:
            lotes_ativos = [l for l in lotes_ativos if not l.esgotado]

        contas_dia = contas_por_data.get(data_atual, [])
        for _, valor_conta, desc, ordem_processamento in contas_dia:
            sequencia_saque = 1
            valor_contas_total += float(valor_conta)
            lotes_disponiveis = [
                l for l in lotes_ativos
                if (not l.esgotado) and (l.saldo_bruto > VALOR_MINIMO_LOTE_ATIVO) and (l.data_aplicacao <= data_atual)
            ]
            if not lotes_disponiveis:
                valor_nao_coberto += float(valor_conta)
                contas_nao_cobertas += 1
                continue

            saques = []

            if nome == "ECONOMICA_CLIFF":
                lotes_disponiveis.sort(key=lambda l: get_score_economico(l, data_atual, dias_cliff=15))
                falta = valor_conta
                for l in lotes_disponiveis:
                    if falta <= 0.001:
                        break
                    score = get_score_economico(l, data_atual, dias_cliff=15)
                    if score >= 1e8:
                        continue
                    fator = l.get_fator_liquido(data_atual)
                    if fator <= 0:
                        continue
                    uso = min(falta / fator, l.saldo_bruto)
                    saques.append((l, uso))
                    falta -= uso * fator
                if falta > 0.001:
                    for l in lotes_disponiveis:
                        if falta <= 0.001:
                            break
                        if l.esgotado or l.saldo_bruto <= VALOR_MINIMO_LOTE_ATIVO:
                            continue
                        if any(l is s[0] for s in saques):
                            continue
                        fator = l.get_fator_liquido(data_atual)
                        if fator <= 0:
                            continue
                        uso = min(falta / fator, l.saldo_bruto)
                        saques.append((l, uso))
                        falta -= uso * fator

            elif nome == "ECONOMICA_VPL":
                lotes_disponiveis.sort(key=lambda l: get_score_economico_vpl(
                    l, data_atual, d_proj, taxa_proj, dias_cliff=10
                ))
                falta = valor_conta
                for l in lotes_disponiveis:
                    if falta <= 0.001:
                        break
                    fator = l.get_fator_liquido(data_atual)
                    if fator <= 0:
                        continue
                    uso = min(falta / fator, l.saldo_bruto)
                    saques.append((l, uso))
                    falta -= uso * fator

            elif nome == "HEURISTICA":
                lotes_disponiveis.sort(key=lambda l: ((data_atual - l.data_base_fiscal).days < 30, l.data_base_fiscal))
                falta = valor_conta
                for l in lotes_disponiveis:
                    if falta <= 0.001:
                        break
                    fator = l.get_fator_liquido(data_atual)
                    if fator == 0:
                        continue
                    bruto = falta / fator
                    uso = min(bruto, l.saldo_bruto)
                    saques.append((l, uso))
                    falta -= uso * fator

            elif nome == "GENETICA_5P":
                if params_opt is None:
                    raise ValueError("params_opt obrigatório para GENETICA_5P")
                if isinstance(params_opt, dict):
                    w_iof = params_opt.get('peso_iof', 100.0)
                    w_ir = params_opt.get('peso_ir', 0.0)
                    w_age = params_opt.get('peso_idade', 0.1)
                    w_liq = params_opt.get('peso_liq', 0.0)
                    w_cliff = params_opt.get('peso_cliff', 1000.0)
                else:
                    p = list(params_opt)
                    w_iof = p[0] if len(p) > 0 else 100.0
                    w_ir = p[1] if len(p) > 1 else 0.0
                    w_age = p[2] if len(p) > 2 else 0.1
                    w_liq = p[3] if len(p) > 3 else 0.0
                    w_cliff = p[4] if len(p) > 4 else 1000.0

                def score_lote(l):
                    dias = (data_atual - l.data_base_fiscal).days
                    iof = IOF_TABLE[dias] if dias < 30 else 0.0
                    ir = obter_aliquota_ir(dias)
                    dist_prox = 999
                    if dias < 180:
                        dist_prox = 180 - dias
                    elif dias < 360:
                        dist_prox = 360 - dias
                    elif dias < 720:
                        dist_prox = 720 - dias
                    penalty_cliff = 1.0 if dist_prox <= DIAS_CLIFF_IR else 0.0
                    flq = l.get_fator_liquido(data_atual)
                    score = (iof * w_iof * 100) + (ir * w_ir * 100) + (dias * w_age * -0.1) + (flq * w_liq * 10) + (penalty_cliff * w_cliff * 50)
                    return score

                lotes_disponiveis.sort(key=score_lote)
                falta = valor_conta
                for l in lotes_disponiveis:
                    if falta <= 0.001:
                        break
                    fator = l.get_fator_liquido(data_atual)
                    if fator <= 0:
                        continue
                    uso = min(falta / fator, l.saldo_bruto)
                    saques.append((l, uso))
                    falta -= uso * fator

            elif nome == "PENALIDADE_5P":
                res = resolver_pulp_penalidade_5p(lotes_disponiveis, valor_conta, data_atual, params_opt)
                for i, val in enumerate(res):
                    if val > VALOR_MINIMO_RESGATE_BRUTO:
                        saques.append((lotes_disponiveis[i], val))

            elif nome == "HIBRIDO_5P":
                res = resolver_pulp_hibrido_5p(lotes_disponiveis, valor_conta, data_atual, params_opt, d_proj, bcb_map=bcb_map, taxa_proj=taxa_proj)
                for i, val in enumerate(res):
                    if val > VALOR_MINIMO_RESGATE_BRUTO:
                        saques.append((lotes_disponiveis[i], val))

            falta_pos = float(valor_conta)
            for l, val_b in saques:
                fator = l.get_fator_liquido(data_atual)
                valor_liquido_alvo = round(val_b * fator, 2)
                movimento = executar_saque_lote(l, valor_liquido_alvo, data_atual)
                if movimento is None:
                    continue
                log.append(montar_log_movimento_lote(
                    movimento, data_atual, desc, bcb_map=bcb_map,
                    ordem_processamento=ordem_processamento, sequencia_saque=sequencia_saque,
                    evento_financeiro=evento_financeiro_global
                ))
                sequencia_saque += 1
                evento_financeiro_global += 1
                falta_pos -= movimento['liquido']

            if falta_pos > TOLERANCIA_MONETARIA:
                valor_nao_coberto += float(falta_pos)
                contas_nao_cobertas += 1

            lotes_ativos = [l for l in lotes_ativos if (not l.esgotado) and (l.saldo_bruto > VALOR_MINIMO_LOTE_ATIVO)]

        data_atual += timedelta(days=1)

    resumo_saldo_atual = calcular_saldo_atual_lotes(lotes_pool, d_fim)
    saldo_final = resumo_saldo_atual['saldo_bruto_total']
    total_resgatado_liquido = sum(l.total_liquido_sacado for l in lotes_pool)
    total_imposto = sum(l.total_imposto_pago for l in lotes_pool)
    total_bruto_sacado = sum(l.total_bruto_sacado for l in lotes_pool)
    eficiencia_fiscal = (total_resgatado_liquido / total_bruto_sacado * 100.0) if total_bruto_sacado > 0 else 100.0

    saldo_liquido_final = resumo_saldo_atual['saldo_liquido_total']
    riqueza_total = total_resgatado_liquido + saldo_liquido_final

    taxa_anual_desc = 0.08
    dias_ate_final = max((d_fim - d_ini).days, 1)
    fator_desc = (1 + taxa_anual_desc) ** (dias_ate_final / 365.25)
    npv_riqueza = riqueza_total / fator_desc

    lotes_usados = [l for l in lotes_pool if l.vezes_usado > 0]
    num_lotes_usados = len(lotes_usados)

    return saldo_liquido_final, pd.DataFrame(log), lotes_pool, {
        'total_resgatado_liquido': total_resgatado_liquido,
        'total_imposto': total_imposto,
        'total_bruto_sacado': total_bruto_sacado,
        'eficiencia_fiscal': eficiencia_fiscal,
        'saldo_liquido_final': saldo_liquido_final,
        'riqueza_total': riqueza_total,
        'npv_riqueza': npv_riqueza,
        'valor_contas_total': valor_contas_total,
        'valor_nao_coberto': valor_nao_coberto,
        'contas_nao_cobertas': contas_nao_cobertas,
        'num_lotes_usados': num_lotes_usados,
        'total_lotes': len(lotes_pool),
        'resumo_saldo_atual': resumo_saldo_atual,
        'data_inicio': d_ini,
        'data_fim': d_fim,
        'data_referencia_relatorio': d_fim,
        'data_proj': d_proj,
    }

def _agrupar_contas_por_data(contas_ord):
    contas_por_data = {}
    for conta in contas_ord:
        contas_por_data.setdefault(conta[0], []).append(conta)
    return contas_por_data

def _lotes_disponiveis_no_dia(lotes_ativos, data_cur):
    return [
        l for l in lotes_ativos
        if not l.esgotado
        and l.saldo_bruto > 0.01
        and l.data_aplicacao <= data_cur
        and not (l.carencia_ate and data_cur < l.carencia_ate)
    ]

def _registrar_movimento_pagamento(log, data_cur, desc, lote_ref, saldo_pre, efetivo, imposto, liquido, modo_pagamento):
    log.append({
        'Data': data_cur,
        'Conta': desc,
        'Lote': lote_ref.id,
        'Produto': lote_ref.produto.nome if lote_ref.produto else 'Padrão',
        'Saldo Antes': round(saldo_pre, 2),
        'Bruto Sacado': round(efetivo, 2),
        'Imposto': round(imposto, 2),
        'Liquido Sacado': round(liquido, 2),
        'Saldo Remanescente': round(lote_ref.saldo_bruto, 2),
        'Modo Pagamento': modo_pagamento,
    })

def _sacar_de_lote(lote_ref, data_cur, bruto_saque):
    saldo_pre = lote_ref.saldo_bruto
    fator = lote_ref.get_fator_liquido(data_cur)
    if fator <= 0:
        return None
    efetivo = lote_ref.sacar(bruto_saque)
    liquido = round(efetivo * fator, 6)
    imposto = round(efetivo - liquido, 6)
    lote_ref.total_imposto_pago += imposto
    lote_ref.total_liquido_sacado += liquido
    return saldo_pre, efetivo, imposto, liquido

def _executar_plano_externo_rigido_conta(data_cur, desc, falta, disponiveis, log, execucao_plano_externo, desvios_plano_externo):
    key = (data_cur, str(desc).strip())
    plano_linhas = PLANO_PAGAMENTOS_EXTERNO.get(key, []) if (disponiveis and PLANO_PAGAMENTOS_EXTERNO) else []
    if not (disponiveis and plano_linhas and normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO) == 'rigido_plano_externo'):
        return falta, False, False

    mapa_lotes = {str(l.id).strip(): l for l in disponiveis}
    usou = False
    for item in plano_linhas:
        if falta <= 0.001:
            break
        lote_id_planejado = str(item.get('Lote', '')).strip()
        bruto_planejado = float(item.get('Bruto', 0.0) or 0.0)
        lote_ref = mapa_lotes.get(lote_id_planejado)
        if lote_ref is None:
            _registrar_auditoria_plano(desvios_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=lote_id_planejado,
                                       lote_executado=None, bruto_planejado=bruto_planejado, bruto_executado=0.0,
                                       status='DESVIO_LOTE', motivo='lote_planejado_indisponivel', modo='PLANO_EXTERNO_RIGIDO')
            continue
        uso = min(bruto_planejado, lote_ref.saldo_bruto)
        if uso <= 0.01:
            _registrar_auditoria_plano(desvios_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=lote_id_planejado,
                                       lote_executado=lote_ref.id, bruto_planejado=bruto_planejado, bruto_executado=uso,
                                       status='DESVIO_VALOR', motivo='saldo_insuficiente_ou_zero', modo='PLANO_EXTERNO_RIGIDO')
            continue
        mov = _sacar_de_lote(lote_ref, data_cur, uso)
        if mov is None:
            _registrar_auditoria_plano(desvios_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=lote_id_planejado,
                                       lote_executado=lote_ref.id, bruto_planejado=bruto_planejado, bruto_executado=0.0,
                                       status='DESVIO_VALOR', motivo='fator_liquido_invalido', modo='PLANO_EXTERNO_RIGIDO')
            continue
        saldo_pre, efetivo, imposto, liquido = mov
        _registrar_movimento_pagamento(log, data_cur, desc, lote_ref, saldo_pre, efetivo, imposto, liquido, 'PLANO_EXTERNO_RIGIDO')
        lista_dest = execucao_plano_externo if abs(efetivo - bruto_planejado) <= 0.01 else desvios_plano_externo
        status = 'EXEC_FIEL' if lista_dest is execucao_plano_externo else 'DESVIO_VALOR'
        motivo = 'execucao_fiel' if status == 'EXEC_FIEL' else 'saldo_insuficiente_para_replicar_bruto'
        _registrar_auditoria_plano(lista_dest, data_ref=data_cur, conta=desc, lote_planejado=lote_id_planejado,
                                   lote_executado=lote_ref.id, bruto_planejado=bruto_planejado, bruto_executado=efetivo,
                                   status=status, motivo=motivo, modo='PLANO_EXTERNO_RIGIDO')
        falta -= liquido
        usou = True
    return falta, usou, True

def _executar_plano_externo_baseline_conta(data_cur, desc, falta, disponiveis, log):
    key = (data_cur, str(desc).strip())
    plano_linhas = PLANO_PAGAMENTOS_EXTERNO.get(key, []) if (disponiveis and PLANO_PAGAMENTOS_EXTERNO) else []
    if not (disponiveis and plano_linhas):
        return falta, False
    mapa_lotes = {str(l.id).strip(): l for l in disponiveis}
    aplicado = False
    for item in plano_linhas:
        if falta <= 0.001:
            break
        lote_ref = mapa_lotes.get(str(item.get('Lote', '')).strip())
        if lote_ref is None:
            continue
        uso = min(float(item.get('Bruto', 0.0) or 0.0), lote_ref.saldo_bruto)
        if uso <= 0.01:
            continue
        mov = _sacar_de_lote(lote_ref, data_cur, uso)
        if mov is None:
            continue
        saldo_pre, efetivo, imposto, liquido = mov
        _registrar_movimento_pagamento(log, data_cur, desc, lote_ref, saldo_pre, efetivo, imposto, liquido, 'PLANO_EXTERNO_BASELINE')
        falta -= liquido
        aplicado = True
    return falta, aplicado

def _executar_fallback_hibrido_conta(data_cur, desc, falta, disponiveis, data_fim, bcb_map, log, fallbacks_plano_externo, plano_rigido_encontrado=False):
    if not (falta > 0.001 and disponiveis and PARAMS_HIBRIDO is not None):
        return falta, False
    disponiveis_rest = [l for l in disponiveis if not l.esgotado and l.saldo_bruto > 0.01]
    if not disponiveis_rest:
        return falta, False
    valores_otimos = resolver_hibrido_5p(disponiveis_rest, float(falta), data_cur, PARAMS_HIBRIDO, data_fim, bcb_map, TAXA_DIA_BASE)
    if not any(v and v > 0.01 for v in valores_otimos):
        return falta, False
    if plano_rigido_encontrado:
        _registrar_auditoria_plano(fallbacks_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=None,
                                   lote_executado=None, bruto_planejado=None, bruto_executado=None,
                                   status='FALLBACK_HIBRIDO', motivo=f'falta_residual={round(falta, 2)}', modo='PLANO_EXTERNO_RIGIDO')
    for lote_ref, val_bruto in zip(disponiveis_rest, valores_otimos):
        if falta <= 0.001:
            break
        if val_bruto <= 0.01:
            continue
        val_bruto = min(val_bruto, lote_ref.saldo_bruto)
        mov = _sacar_de_lote(lote_ref, data_cur, val_bruto)
        if mov is None:
            continue
        saldo_pre, efetivo, imposto, liquido = mov
        _registrar_movimento_pagamento(log, data_cur, desc, lote_ref, saldo_pre, efetivo, imposto, liquido, 'HIBRIDO_5P')
        _registrar_auditoria_plano(fallbacks_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=None,
                                   lote_executado=lote_ref.id, bruto_planejado=0.0, bruto_executado=efetivo,
                                   status='FALLBACK_HIBRIDO', motivo='cobertura_restante_pos_plano', modo='HIBRIDO_5P')
        falta -= liquido
    return falta, True

def _executar_fallback_heuristico_conta(data_cur, desc, falta, disponiveis, log, fallbacks_plano_externo, plano_rigido_encontrado=False, data_fim=None):
    if not (falta > 0.001 and disponiveis):
        return falta, False
    if plano_rigido_encontrado:
        _registrar_auditoria_plano(fallbacks_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=None,
                                   lote_executado=None, bruto_planejado=None, bruto_executado=None,
                                   status='FALLBACK_HEURISTICO', motivo=f'falta_residual={round(falta, 2)}', modo='PLANO_EXTERNO_RIGIDO')
    if data_fim is not None:
        disponiveis = _ordenar_lotes_para_pagamento(disponiveis, data_cur, data_fim)
    else:
        disponiveis = sorted(disponiveis, key=lambda l: get_score_economico(l, data_cur))
    usou = False
    for lote_ref in disponiveis:
        if falta <= 0.001:
            break
        fator = lote_ref.get_fator_liquido(data_cur)
        if fator <= 0:
            continue
        bruto_nec = falta / fator
        uso = min(bruto_nec, lote_ref.saldo_bruto)
        mov = _sacar_de_lote(lote_ref, data_cur, uso)
        if mov is None:
            continue
        saldo_pre, efetivo, imposto, liquido = mov
        _registrar_movimento_pagamento(log, data_cur, desc, lote_ref, saldo_pre, efetivo, imposto, liquido, 'HEURISTICA')
        _registrar_auditoria_plano(fallbacks_plano_externo, data_ref=data_cur, conta=desc, lote_planejado=None,
                                   lote_executado=lote_ref.id, bruto_planejado=0.0, bruto_executado=efetivo,
                                   status='FALLBACK_HEURISTICO', motivo='heuristica_final', modo='HEURISTICA')
        falta -= liquido
        usou = True
    return falta, usou

def _processar_conta_futura(data_cur, valor_conta, desc, lotes_ativos, data_fim, bcb_map, log,
                            execucao_plano_externo, desvios_plano_externo, fallbacks_plano_externo):
    falta = float(valor_conta)
    disponiveis = _lotes_disponiveis_no_dia(lotes_ativos, data_cur)

    falta, usou_plano_rigido, plano_rigido_encontrado = _executar_plano_externo_rigido_conta(
        data_cur, desc, falta, disponiveis, log, execucao_plano_externo, desvios_plano_externo
    )
    usou_otimizacao = bool(usou_plano_rigido)
    usou_plano_externo = bool(usou_plano_rigido)

    if not plano_rigido_encontrado:
        falta, usou_baseline = _executar_plano_externo_baseline_conta(
            data_cur, desc, falta, disponiveis, log
        )
        usou_plano_externo = usou_plano_externo or bool(usou_baseline)
        usou_otimizacao = usou_otimizacao or bool(usou_baseline)

    falta, usou_hibrido = _executar_fallback_hibrido_conta(
        data_cur, desc, falta, disponiveis, data_fim, bcb_map, log,
        fallbacks_plano_externo, plano_rigido_encontrado=plano_rigido_encontrado
    )
    usou_otimizacao = usou_otimizacao or bool(usou_hibrido)

    usou_heuristica = False
    if falta > 0.001 and (not usou_otimizacao):
        falta, usou_heuristica = _executar_fallback_heuristico_conta(
            data_cur, desc, falta, disponiveis, log, fallbacks_plano_externo,
            plano_rigido_encontrado=plano_rigido_encontrado, data_fim=data_fim
        )

    if falta > 0.01 and EXIBIR_ALERTAS_FALTA_CAIXA:
        modo = 'PLANO_EXTERNO' if usou_plano_externo else ('HIBRIDO_5P' if usou_otimizacao else 'HEURISTICA')
        print(f"  ⚠  Falta R$ {falta:.2f} para pagar conta {desc} em {data_cur} [{modo}]")

    return {
        'falta': falta,
        'usou_otimizacao': usou_otimizacao,
        'usou_plano_externo': usou_plano_externo,
        'usou_heuristica': bool(usou_heuristica),
    }

def _processar_juros_do_dia(data_cur, lotes_ativos, bcb_map):
    atualizar_saldo_lotes_no_dia(lotes_ativos, data_cur, bcb_map, TAXA_DIA_BASE)

def _calcular_metricas_futuro(lotes_ativos, novos_lotes, switches_detalhados, data_inicio, data_fim):
    saldo_bruto = sum(l.saldo_bruto for l in lotes_ativos)
    saldo_liquido = sum(
        l.saldo_bruto * l.get_fator_liquido(data_fim)
        for l in lotes_ativos if not l.esgotado
    )
    total_resgatado = sum(l.total_liquido_sacado for l in lotes_ativos)
    total_imposto = sum(l.total_imposto_pago for l in lotes_ativos)
    riqueza = total_resgatado + saldo_liquido

    num_lotes_ativos_final = sum(1 for l in lotes_ativos if l.saldo_bruto > 0.01 and not l.esgotado)
    num_lotes_relatorio = sum(1 for l in lotes_ativos if (l.saldo_bruto > 0.01 or l.total_bruto_sacado > 0.01 or l.valor_inicial > 0.01))
    switches_exec_reais = len({
        str(r.get('Lote_Origem'))
        for r in switches_detalhados
        if r.get('Lote_Origem') and not str(r.get('Lote_Origem')).startswith('POOL[')
    })

    return {
        'saldo_bruto': round(saldo_bruto, 2),
        'saldo_liquido': round(saldo_liquido, 2),
        'total_resgatado': round(total_resgatado, 2),
        'total_imposto': round(total_imposto, 2),
        'riqueza': round(riqueza, 2),
        'num_lotes': int(num_lotes_ativos_final),
        'num_lotes_relatorio': int(num_lotes_relatorio),
        'lotes_usados': sum(1 for l in lotes_ativos if l.vezes_usado > 0),
        'switches_exec': int(switches_exec_reais),
        'switches_partes_criadas': int(len(novos_lotes)),
        'switches_detalhados': switches_detalhados,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'data_referencia_relatorio': data_fim,
    }

def simular_futuro(lotes: list, contas: list, bcb_map: dict, data_inicio: date = None, produtos: list = None,
                   planos_pool_switch: dict = None, verbose: bool = True):
    if data_inicio is None:
        data_inicio = data_hoje_referencia()

    contas_ord = sorted(contas, key=lambda x: x[0])
    data_fim = max((c[0] for c in contas_ord), default=data_inicio)
    contas_por_data = _agrupar_contas_por_data(contas_ord)

    lotes_ativos = list(lotes)
    novos_lotes: list[Lote] = []
    log: list[dict] = []
    switches_detalhados: list[dict] = []
    execucao_plano_externo: list[dict] = []
    desvios_plano_externo: list[dict] = []
    fallbacks_plano_externo: list[dict] = []

    data_cur = data_inicio

    while data_cur <= data_fim:
        if is_dia_rendimento(data_cur, bcb_map):
            _processar_juros_do_dia(data_cur, lotes_ativos, bcb_map)

        for conta in contas_por_data.get(data_cur, []):
            _, valor_conta, desc = conta[:3]
            _processar_conta_futura(
                data_cur, valor_conta, desc, lotes_ativos, data_fim, bcb_map, log,
                execucao_plano_externo, desvios_plano_externo, fallbacks_plano_externo
            )

        lotes_switch_dia = [
            l for l in lotes_ativos
            if (not l.esgotado and l.switch_agendado is not None and l.switch_agendado[0] == data_cur)
        ]
        if produtos and len(lotes_switch_dia) >= 2:
            _executar_pool_switch_dia(
                data_cur, lotes_switch_dia, produtos, contas_ord, bcb_map,
                planos_pool_switch, switches_detalhados, novos_lotes,
                lotes_ativos, verbose=verbose,
            )

        for l in lotes_ativos:
            if l.esgotado or l.switch_agendado is None:
                continue
            data_sw, prod_alvo = l.switch_agendado
            if data_sw == data_cur:
                _executar_switch_individual(
                    l, data_cur, prod_alvo, produtos, bcb_map, contas_ord,
                    switches_detalhados, novos_lotes, lotes_ativos, verbose=verbose,
                )
        data_cur += timedelta(days=1)

    stats = _calcular_metricas_futuro(
        lotes_ativos, novos_lotes, switches_detalhados, data_inicio, data_fim
    )
    stats.update({
        'execucao_plano_externo': execucao_plano_externo,
        'desvios_plano_externo': desvios_plano_externo,
        'fallbacks_plano_externo': fallbacks_plano_externo,
        'lotes_finais': list(lotes_ativos),
        'novos_lotes_switch': list(novos_lotes),
        'saldo_liquido_final': round(float(stats.get('saldo_liquido', 0.0) or 0.0), 2),
        'saldo_bruto_final': round(float(stats.get('saldo_bruto', 0.0) or 0.0), 2),
    })

    return pd.DataFrame(log), stats

# =========================================================
# 13. ALIASES GLOBAIS DE COMPATIBILIDADE
# =========================================================

# =========================================================
# 14. PATCH FINAL — CAIXA DO DIA, SNAPSHOT E ALOCAÇÃO INICIAL
# =========================================================

def _resumo_lotes_df(lotes, data_ref):
    rows = []
    for l in lotes:
        try:
            fl = l.get_fator_liquido(data_ref) if getattr(l, 'saldo_bruto', 0.0) > 0 else 0.0
        except Exception:
            fl = 0.0
        rows.append({
            'Lote ID': getattr(l, 'id', ''),
            'Data Aplicação': getattr(l, 'data_aplicacao', None),
            'Produto': getattr(getattr(l, 'produto', None), 'nome', 'Padrão') if getattr(l, 'produto', None) else 'Padrão',
            'Saldo Bruto': round(float(getattr(l, 'saldo_bruto', 0.0) or 0.0), 2),
            'Saldo Líquido': round(float((getattr(l, 'saldo_bruto', 0.0) or 0.0) * fl), 2),
            'Esgotado': bool(getattr(l, 'esgotado', False)),
            'Pendente Aporte': bool(getattr(l, 'pendente_aporte', False)),
        })
    return pd.DataFrame(rows)

def _carregar_snapshot_inicial(produtos, bcb_map):
    print("\n>>> [PASSADO] Carregando inventário e simulando passado...")
    lotes_passados, lotes_futuros, contas, log_passado, data_referencia_snapshot, estado_lotes_passado = carregar_inventario_e_gastos(produtos, bcb_map)
    snapshot_lotes_atuais = _resumo_lotes_df(list(lotes_passados) + list(lotes_futuros), data_referencia_snapshot)
    if isinstance(estado_lotes_passado, pd.DataFrame):
        estado_lotes_passado_snapshot = estado_lotes_passado.copy()
    else:
        estado_lotes_passado_snapshot = pd.DataFrame(list(estado_lotes_passado or []))
    return {
        'lotes_passados': lotes_passados,
        'lotes_futuros': lotes_futuros,
        'contas': contas,
        'log_passado': log_passado,
        'snapshot_lotes_atuais': snapshot_lotes_atuais,
        'estado_lotes_passado_snapshot': estado_lotes_passado_snapshot,
        'data_referencia_snapshot': data_referencia_snapshot,
    }

def _contas_sem_data(contas, data_ref):
    return [c for c in contas if c[0] != data_ref]

def _alocar_aportes_iniciais(lotes_passados, lotes_futuros, produtos, bcb_map, contas, hoje):
    if contas:
        processar_contas_do_dia(lotes_passados, contas, hoje)

    lotes_passados = [l for l in lotes_passados if getattr(l, 'saldo_bruto', 0.0) > 0.01 and not getattr(l, 'esgotado', False)]
    contas_apos_data_referencia = _contas_sem_data(contas, hoje)

    print("\n>>> [ALOCACAO] Janela operacional: mês atual + próximo mês")

    candidatos = []
    for l in lotes_passados:
        if getattr(l, 'saldo_bruto', 0.0) > 0.01 and getattr(l, 'produto', None) is None:
            candidatos.append(l)
    for l in lotes_futuros:
        if getattr(l, 'saldo_bruto', 0.0) > 0.01 and getattr(l, 'produto', None) is None:
            candidatos.append(l)

    por_data = {}
    for l in candidatos:
        por_data.setdefault(l.data_aplicacao, []).append(l)

    plano_aportes = []
    lotes_futuros_out = [l for l in lotes_futuros if getattr(l, 'produto', None) is not None]
    lotes_passados_out = [l for l in lotes_passados if getattr(l, 'produto', None) is not None]
    resumo_meses = {}

    for data_apl in sorted(por_data):
        grupo = [l for l in por_data[data_apl] if getattr(l, 'saldo_bruto', 0.0) > 0.01 and not getattr(l, 'esgotado', False)]
        if not grupo:
            continue
        valor_total = round(sum(float(l.saldo_bruto) for l in grupo), 2)
        if valor_total <= 0.01:
            continue

        aloc, top_mercado, _ = alocar_lote_por_otimizacao(hoje, data_apl, valor_total, produtos, bcb_map, contas_apos_data_referencia, foco_rendimento=True, max_produtos=2)
        mes_ref = date(data_apl.year, data_apl.month, 1)
        info_mes = resumo_meses.setdefault(mes_ref, {'datas': 0, 'valor': 0.0})
        info_mes['datas'] += 1
        info_mes['valor'] += valor_total

        if _debug_ativo(DEBUG_ALOCACAO_FUTURA) and data_apl <= _fim_janela_alocacao(hoje):
            print(f"\n  [DATA {data_apl}] {len(grupo)} lote(s) | consolidado R$ {valor_total:,.2f}")
            if aloc:
                for i, (prod, valor) in enumerate(aloc, start=1):
                    print(f"      {i}. {prod.nome:<30} R$ {valor:>10,.2f} | taxa {float(getattr(prod, 'taxa_base', 0.0) or 0.0):.2f}% CDI")
                if top_mercado:
                    if isinstance(top_mercado, str):
                        top_txt = top_mercado
                    else:
                        itens_top = []
                        for item in list(top_mercado)[:3]:
                            if isinstance(item, (list, tuple)) and len(item) >= 2 and hasattr(item[0], 'nome'):
                                itens_top.append(f"{item[0].nome}: w{float(item[1]):.6f}")
                            elif hasattr(item, 'nome'):
                                itens_top.append(str(item.nome))
                            else:
                                itens_top.append(str(item))
                        top_txt = ', '.join(itens_top)
                    print(f"       TOP mercado: {top_txt}")
            else:
                print("      ⚠ Nenhum plano viável encontrado.")

        if aloc:
            for prod, valor in aloc:
                plano_aportes.append({'Data': data_apl, 'Produto': prod.nome, 'Valor': round(float(valor), 2)})
            resto = valor_total
            parte_idx = 1
            for prod, valor in aloc:
                v = round(min(resto, float(valor)), 2)
                if v <= 0.01:
                    continue
                lote_id = f"APORTE {data_apl} #{parte_idx}"
                novo = Lote(lote_id, data_apl, v, produto=prod)
                if data_apl <= hoje:
                    lotes_passados_out.append(novo)
                else:
                    lotes_futuros_out.append(novo)
                resto = round(resto - v, 2)
                parte_idx += 1
            if resto > 0.01:
                novo = Lote(f"APORTE {data_apl} #RESTO", data_apl, resto, produto=None, pendente_aporte=True)
                if data_apl <= hoje:
                    lotes_passados_out.append(novo)
                else:
                    lotes_futuros_out.append(novo)
        else:
            for l in grupo:
                if l.data_aplicacao <= hoje:
                    lotes_passados_out.append(l)
                else:
                    lotes_futuros_out.append(l)

    primeiro_mes = date(hoje.year, hoje.month, 1)
    segundo_mes = (primeiro_mes.replace(day=28) + timedelta(days=4)).replace(day=1)
    meses_janela = [primeiro_mes, segundo_mes]

    for mes_ref in meses_janela:
        info = resumo_meses.get(mes_ref, {'datas': 0, 'valor': 0.0})
        print(f"    {mes_ref.strftime('%B/%Y').capitalize()}: {info['datas']} data(s) | R$ {info['valor']:,.2f}")

    restantes = [(mes_ref, info) for mes_ref, info in sorted(resumo_meses.items()) if mes_ref not in set(meses_janela)]
    if restantes:
        qtd_datas = sum(info['datas'] for _, info in restantes)
        qtd_meses = len(restantes)
        print(f"    Futuro posterior: {qtd_datas} data(s) em {qtd_meses} mês(es) mantidas para alocação rolante")

    lotes_passados = [l for l in lotes_passados_out if getattr(l, 'saldo_bruto', 0.0) > 0.01 and l.data_aplicacao <= hoje]
    lotes_futuros = [l for l in lotes_futuros_out if getattr(l, 'saldo_bruto', 0.0) > 0.01 and l.data_aplicacao > hoje]
    return lotes_passados, lotes_futuros, pd.DataFrame(plano_aportes), contas_apos_data_referencia

def _resolver_taxa_proj_unificada(bcb_map):
    if isinstance(bcb_map, dict) and bcb_map:
        try:
            datas_validas = [d for d in bcb_map.keys() if isinstance(d, date)]
            if datas_validas:
                ultima_data = max(datas_validas)
                ultimo_valor = float(bcb_map.get(ultima_data) or TAXA_DIA_BASE)
                # bcb_map guarda fator diário (ex.: 1.00054266), não taxa decimal.
                if ultimo_valor > 1.0:
                    return max(ultimo_valor - 1.0, 0.0)
                return ultimo_valor
        except Exception:
            pass

    taxa = float(globals().get('TAXA_PROJ', TAXA_DIA_BASE) or TAXA_DIA_BASE)
    if taxa > 1.0:
        return max(taxa - 1.0, 0.0)
    return taxa

def _carregar_e_validar_plano_externo_unificado(
    *,
    snapshot,
    contas_futuras,
    hoje,
    produtos,
    bcb_map,
):
    del snapshot, contas_futuras, hoje, bcb_map
    globals()['PLANO_PAGAMENTOS_EXTERNO'] = None
    globals()['ORIGEM_PLANO_PAGAMENTOS'] = None

    DIAGNOSTICO_MODO_EXECUCAO['modo_solicitado'] = normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)
    DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)
    DIAGNOSTICO_MODO_EXECUCAO['houve_rebaixamento'] = False
    DIAGNOSTICO_MODO_EXECUCAO['motivos_rebaixamento'] = []
    DIAGNOSTICO_MODO_EXECUCAO['plano_externo_carregado'] = False
    DIAGNOSTICO_MODO_EXECUCAO['origem_plano_externo'] = None
    DIAGNOSTICO_MODO_EXECUCAO['observacao'] = ''

    plano_externo, origem_plano = carregar_plano_pagamentos_externo()
    diag_plano = {
        'ok': True,
        'motivos': [],
        'origem': None,
    }

    if plano_externo:
        globals()['PLANO_PAGAMENTOS_EXTERNO'] = plano_externo
        globals()['ORIGEM_PLANO_PAGAMENTOS'] = str(origem_plano) if origem_plano is not None else None
        DIAGNOSTICO_MODO_EXECUCAO['plano_externo_carregado'] = True
        DIAGNOSTICO_MODO_EXECUCAO['origem_plano_externo'] = str(origem_plano) if origem_plano is not None else None
        try:
            diag_plano = _diagnosticar_compatibilidade_plano_externo(produtos, origem_plano)
        except Exception as e:
            diag_plano = {
                'ok': False,
                'motivos': [f'falha_diagnostico_plano:{e}'],
                'origem': str(origem_plano) if origem_plano is not None else None,
            }
        diag_plano['origem'] = str(origem_plano) if origem_plano is not None else None
        modo_efetivo = _ajustar_modo_por_compatibilidade_plano(diag_plano)
        DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_efetivo
        if not diag_plano.get('ok', True) and not DIAGNOSTICO_MODO_EXECUCAO.get('observacao'):
            DIAGNOSTICO_MODO_EXECUCAO['observacao'] = 'Plano externo carregado com restrições de compatibilidade.'
    else:
        DIAGNOSTICO_MODO_EXECUCAO['observacao'] = 'Nenhum plano externo carregado; execução seguirá o motor local.'
        diag_plano = {
            'ok': False,
            'motivos': ['plano_externo_nao_encontrado'],
            'origem': None,
        }
        if normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO) == 'rigido_plano_externo':
            modo_efetivo = _ajustar_modo_por_compatibilidade_plano(diag_plano)
            DIAGNOSTICO_MODO_EXECUCAO['modo_efetivo'] = modo_efetivo

    return {
        'plano_externo': globals().get('PLANO_PAGAMENTOS_EXTERNO'),
        'origem_plano_externo': globals().get('ORIGEM_PLANO_PAGAMENTOS'),
        'modo_execucao_efetivo': DIAGNOSTICO_MODO_EXECUCAO.get('modo_efetivo'),
        'diagnostico_modo_execucao': dict(DIAGNOSTICO_MODO_EXECUCAO),
        'diagnostico_plano_externo': diag_plano,
    }

def _safe_input(prompt: str, default: str = "") -> str:
    try:
        valor = input(prompt)
    except EOFError:
        valor = ""
    except Exception:
        valor = ""
    valor = str(valor or "").strip()
    return valor if valor else str(default or "")

def _resolver_contexto_canonico_compartilhado(*, snapshot, lotes_passados, bcb_map, hoje):
    estado_lotes_passado = snapshot.get('estado_lotes_passado_snapshot')
    log_passado = list(snapshot.get('log_passado') or [])

    valores_originais = {}
    estado_rows = estado_lotes_passado
    if isinstance(estado_rows, pd.DataFrame):
        estado_rows = estado_rows.to_dict('records')
    for st in list(estado_rows or []):
        lid = str(st.get('Lote ID', '') or '').strip()
        if not lid:
            continue
        try:
            valores_originais[lid] = float(st.get('Valor Inicial', 0.0) or 0.0)
        except Exception:
            try:
                valores_originais[lid] = float(st.get('Valor Inicial', 0.0))
            except Exception:
                pass

    df_situacao_atual_canonica = pd.DataFrame()
    idx_situacao_atual_canonica = pd.DataFrame()
    if estado_lotes_passado is not None and log_passado is not None:
        try:
            df_situacao_atual_canonica = gerar_relatorio_situacao_atual(
                lotes_hoje=lotes_passados,
                estado_lotes_passado=estado_lotes_passado,
                log_passado=log_passado,
                valores_originais=valores_originais,
                mapa_bcb=bcb_map,
                data_referencia=hoje,
            )
            if isinstance(df_situacao_atual_canonica, pd.DataFrame) and not df_situacao_atual_canonica.empty:
                try:
                    idx_situacao_atual_canonica = df_situacao_atual_canonica.set_index('Lote ID', drop=False)
                except Exception:
                    idx_situacao_atual_canonica = df_situacao_atual_canonica.copy()
        except Exception:
            df_situacao_atual_canonica = pd.DataFrame()
            idx_situacao_atual_canonica = pd.DataFrame()

    return {
        'estado_lotes_passado': estado_lotes_passado,
        'log_passado': log_passado,
        'valores_originais': valores_originais,
        'df_situacao_atual_canonica': df_situacao_atual_canonica,
        'idx_situacao_atual_canonica': idx_situacao_atual_canonica,
        'data_referencia': hoje,
        'mapa_bcb': bcb_map,
    }

def _selecionar_modo_treinamento_unificado(*, dados_aportes, dados_contas_agr, contas_ind_simples, bcb_map, lotes_iniciais_competicao=None, data_inicio_competicao=None):
    print('-' * 60)
    print('OPÇÕES DE TREINAMENTO')
    print('-' * 60)
    print('1. Modo rápido (carregar parâmetros salvos)')
    print('2. Modo profundo (executar otimizações - pode levar HORAS)')
    print('3. Modo refinamento (otimizar a partir de parâmetros existentes)')
    opcao = _safe_input('Escolha (1/2/3): ', MODO_TREINAMENTO_PADRAO)
    if opcao not in {'1', '2', '3'}:
        opcao = str(MODO_TREINAMENTO_PADRAO or '1')

    perfil_treino = PERFIL_TREINO_PADRAO
    if opcao in {'2', '3'}:
        print('\nPerfis de treino:')
        print('  r = rápido (≈ menor tempo, boa aproximação)')
        print('  b = balanceado (padrão recomendado)')
        print('  p = profundo (máxima busca, mais lento)')
        print('  a = auto (usa o padrão configurado)')
        p = _safe_input('Escolha perfil (r/b/p/a): ', {
            'rapido': 'r', 'balanceado': 'b', 'profundo': 'p', 'auto': PERFIL_TREINO_AUTO_OPCAO,
        }.get(PERFIL_TREINO_PADRAO, 'b')).lower()
        if p == 'r':
            perfil_treino = 'rapido'
        elif p == 'p':
            perfil_treino = 'profundo'
        elif p == 'a':
            perfil_treino = 'auto'
        else:
            perfil_treino = 'balanceado'

    cfg_treino = TREINAMENTO_PERFIS.get(perfil_treino) or TREINAMENTO_PERFIS.get('balanceado') or {'wf_splits': AVALIACAO_WF_SPLITS_DEFAULT}

    params_hibrido, origem_params = carregar_parametros_hibrido_5p()
    best_params_5p = dict(params_hibrido) if isinstance(params_hibrido, dict) else {
        'peso_iof': 100.0, 'peso_ir': 0.0, 'peso_idade': 0.1, 'peso_liq': 0.0, 'peso_cliff': 1000.0, 'peso_vpl': 0.0,
    }
    best_genes_5p = np.array([10.0, 10.0, 0.0, 10.0, 50.0])

    otimizadores_disponiveis = all(callable(globals().get(n)) for n in ['treinar_genetica_profundo', 'treinar_penalidade_5p', 'salvar_parametros', 'reduzir_contas_treinamento'])

    if opcao == '1':
        print('✓ Modo rápido: usando parâmetros salvos/fallback.\n')
    elif not otimizadores_disponiveis:
        print('! Modo profundo/refinamento solicitado, mas os otimizadores completos não estão expostos nesta trilha canônica.')
        print('  -> A execução seguirá com parâmetros salvos/fallback para manter o motor unificado consistente.\n')
    else:
        print('! Modo profundo/refinamento solicitado; mantendo a trilha canônica sem reabrir o runner legado.\n')

    try:
        saldo_agr_ref, _, _, stats_agr_ref = rodar_estrategia(
            'GENETICA_5P', dados_aportes, dados_contas_agr,
            params_opt=best_genes_5p, bcb_map=bcb_map, taxa_proj=globals().get('TAXA_PROJ', TAXA_DIA_BASE),
            lotes_iniciais=lotes_iniciais_competicao,
            data_inicio_competicao=data_inicio_competicao,
        )
        saldo_ind_ref, _, _, stats_ind_ref = rodar_estrategia(
            'GENETICA_5P', dados_aportes, contas_ind_simples,
            params_opt=best_genes_5p, bcb_map=bcb_map, taxa_proj=globals().get('TAXA_PROJ', TAXA_DIA_BASE),
            lotes_iniciais=lotes_iniciais_competicao,
            data_inicio_competicao=data_inicio_competicao,
        )
        print('\n>>> TESTE DE AGRUPAMENTO (REFERÊNCIA) <<<')
        print(f"[1/2] AGRUPADO  -> Saldo Líquido: R$ {float(stats_agr_ref.get('saldo_liquido_final', saldo_agr_ref) or 0.0):,.2f} | Não Coberto: R$ {float(stats_agr_ref.get('valor_nao_coberto', 0.0) or 0.0):,.2f}")
        print(f"[2/2] INDIVIDUAL -> Saldo Líquido: R$ {float(stats_ind_ref.get('saldo_liquido_final', saldo_ind_ref) or 0.0):,.2f} | Não Coberto: R$ {float(stats_ind_ref.get('valor_nao_coberto', 0.0) or 0.0):,.2f}")
        score_agr_ref = float(stats_agr_ref.get('saldo_liquido_final', saldo_agr_ref) or 0.0) - float(stats_agr_ref.get('valor_nao_coberto', 0.0) or 0.0)
        score_ind_ref = float(stats_ind_ref.get('saldo_liquido_final', saldo_ind_ref) or 0.0) - float(stats_ind_ref.get('valor_nao_coberto', 0.0) or 0.0)
        modo_ref = 'individual' if score_ind_ref > score_agr_ref else 'agrupado'
        print(f" -> Modo recomendado pelo teste de agrupamento: {modo_ref.upper()}\n")
    except Exception:
        modo_ref = 'agrupado'

    return {
        'opcao_treinamento': opcao,
        'perfil_treino': perfil_treino,
        'cfg_treino': cfg_treino,
        'best_genes_5p': best_genes_5p,
        'best_params_5p': best_params_5p,
        'origem_parametros': str(origem_params) if origem_params is not None else None,
        'modo_referencia': modo_ref,
    }

def _materializar_artefatos_switching_unificados(
    *,
    snapshot,
    lotes_passados,
    lotes_futuros,
    contas_futuras,
    produtos,
    bcb_map,
    hoje,
    contexto_canonico=None,
):
    artefatos = _avaliar_switching_e_diagnosticos(
        lotes_passados=lotes_passados,
        lotes_futuros=lotes_futuros,
        contas=contas_futuras,
        produtos=produtos,
        bcb_map=bcb_map,
        hoje=hoje,
        estado_lotes_passado_snapshot=snapshot.get('estado_lotes_passado_snapshot'),
        log_passado=snapshot.get('log_passado'),
        data_referencia_snapshot=snapshot.get('data_referencia_snapshot'),
        contexto_canonico=contexto_canonico,
    )
    artefatos['snapshot_lotes_atuais'] = snapshot.get('snapshot_lotes_atuais')
    artefatos['log_passado'] = snapshot.get('log_passado')
    artefatos['estado_lotes_passado_snapshot'] = snapshot.get('estado_lotes_passado_snapshot')
    artefatos['data_referencia_snapshot'] = snapshot.get('data_referencia_snapshot')
    return artefatos

def _executar_futuro_unificado(
    *,
    lotes_passados,
    lotes_futuros,
    contas_futuras,
    produtos,
    bcb_map,
    hoje,
    artefatos_switching,
):
    print("\n>>> [FUTURO] Iniciando simulação futura unificada...")
    todos_lotes = copy.deepcopy(list(lotes_passados) + list(lotes_futuros))
    todos_lotes = _aplicar_modo_execucao_futuro_final(todos_lotes, artefatos_switching, contas_futuras, produtos, bcb_map)

    extrato_df, stats = simular_futuro(
        todos_lotes,
        contas_futuras,
        bcb_map,
        data_inicio=hoje,
        produtos=produtos,
        planos_pool_switch=artefatos_switching.get('planos_pool_switch'),
        verbose=_debug_ativo(DEBUG_SWITCH_EXECUCAO),
    )

    stats.setdefault('saldo_liquido_final', float(stats.get('saldo_liquido', 0.0) or 0.0))
    print(f"    saldo bruto final R$ {float(stats.get('saldo_bruto', 0.0) or 0.0):,.2f} | saldo líquido final R$ {float(stats.get('saldo_liquido', 0.0) or 0.0):,.2f}")
    stats.setdefault('saldo_bruto_final', float(stats.get('saldo_bruto', 0.0) or 0.0))
    stats['lotes_finais'] = list(stats.get('lotes_finais') or list(todos_lotes))
    stats['riqueza_base_switch'] = float(artefatos_switching.get('riqueza_base_switch', 0.0) or 0.0)
    stats['riqueza_final_switch'] = float(artefatos_switching.get('riqueza_final_switch', 0.0) or 0.0)

    data_ref_relatorio = stats.get('data_referencia_relatorio', stats.get('data_fim', hoje))
    relatorio = []
    for l in stats['lotes_finais']:
        if getattr(l, 'saldo_bruto', 0.0) > 0.01 or getattr(l, 'vezes_usado', 0) > 0:
            fl = l.get_fator_liquido(data_ref_relatorio) if getattr(l, 'saldo_bruto', 0.0) > 0 else 0.0
            liq_hoje = round(float(getattr(l, 'saldo_bruto', 0.0) or 0.0) * float(fl or 0.0), 2)
            bruto_total = float(getattr(l, 'saldo_bruto', 0.0) or 0.0) + float(getattr(l, 'total_bruto_sacado', 0.0) or 0.0)
            rent_b = (bruto_total / float(getattr(l, 'valor_inicial', 0.0) or 1.0) - 1.0) * 100.0 if float(getattr(l, 'valor_inicial', 0.0) or 0.0) > 0 else 0.0
            rent_l = ((liq_hoje + float(getattr(l, 'total_liquido_sacado', 0.0) or 0.0)) / float(getattr(l, 'valor_inicial', 0.0) or 1.0) - 1.0) * 100.0 if float(getattr(l, 'valor_inicial', 0.0) or 0.0) > 0 else 0.0
            sw_info = '; '.join(f"{d} → {n} (R${v:,.2f})" for d, n, v in getattr(l, 'historico_switches', [])) if getattr(l, 'historico_switches', None) else '—'
            relatorio.append({
                'Lote ID': getattr(l, 'id', None),
                'Produto': getattr(getattr(l, 'produto', None), 'nome', 'Padrão'),
                'Data Aplicação': getattr(l, 'data_aplicacao', None),
                'Valor Inicial': round(float(getattr(l, 'valor_inicial', 0.0) or 0.0), 2),
                'Saldo Bruto Atual': round(float(getattr(l, 'saldo_bruto', 0.0) or 0.0), 2),
                'Saldo Líquido Atual': liq_hoje,
                'Total Bruto Sacado': round(float(getattr(l, 'total_bruto_sacado', 0.0) or 0.0), 2),
                'Total Líquido Sacado': round(float(getattr(l, 'total_liquido_sacado', 0.0) or 0.0), 2),
                'Rentabilidade Bruta %': round(rent_b, 4),
                'Rentabilidade Líquida %': round(rent_l, 4),
                'Vezes Usado': int(getattr(l, 'vezes_usado', 0) or 0),
                'Switches': sw_info,
            })

    return {
        'extrato_futuro': extrato_df,
        'stats_futuro': stats,
        'lotes_finais_reais': list(stats.get('lotes_finais') or []),
        'df_relatorio_final': pd.DataFrame(relatorio),
        'switches_detalhados': stats.get('switches_detalhados', []),
        'execucao_plano_externo': stats.get('execucao_plano_externo', []),
        'desvios_plano_externo': stats.get('desvios_plano_externo', []),
        'fallbacks_plano_externo': stats.get('fallbacks_plano_externo', []),
    }


def _montar_dados_competicao_unificada(
    *,
    snapshot,
    lotes_passados,
    lotes_futuros,
    contas_futuras,
    produtos,
    bcb_map,
    hoje,
    contexto_canonico=None,
    treinamento_ctx=None,
):
    taxa_proj = _resolver_taxa_proj_unificada(bcb_map)

    lotes_ref = list(lotes_passados) + list(lotes_futuros)
    lotes_iniciais_competicao = []
    dados_aportes = []
    data_inicio_competicao = hoje

    for l in lotes_ref:
        saldo_ref = float(getattr(l, 'saldo_bruto', 0.0) or 0.0)
        if saldo_ref <= 0.01 or bool(getattr(l, 'esgotado', False)):
            continue

        produto_meta = getattr(l, 'produto', None)
        data_aplicacao_original = getattr(l, 'data_aplicacao', hoje)
        data_base_fiscal = getattr(l, 'data_base_fiscal', data_aplicacao_original)

        meta = {
            'produto': produto_meta,
            'carencia_ate': getattr(l, 'carencia_ate', None),
            'data_base_fiscal': data_base_fiscal,
            'fator_acumulado_inicial': 1.0,
            'taxa_base_cdi': float(
                getattr(l, 'taxa_base_cdi', getattr(produto_meta, 'taxa_base', TAXA_BASE_DEFAULT))
                or TAXA_BASE_DEFAULT
            ),
            'taxa_bonus_cdi': float(
                getattr(l, 'taxa_bonus_cdi', getattr(produto_meta, 'taxa_bonus', TAXA_BONUS_DEFAULT))
                or TAXA_BONUS_DEFAULT
            ),
            'dias_bonus': int(
                getattr(l, 'dias_bonus', getattr(produto_meta, 'dias_bonus', DIAS_BONUS_DEFAULT))
                or DIAS_BONUS_DEFAULT
            ),
            'principal_remanescente': float(
                getattr(l, 'principal_remanescente', saldo_ref) or saldo_ref
            ),
            'investimento': str(
                getattr(produto_meta, 'nome', getattr(l, 'investimento', '') or '') or ''
            ),
            'produto_isento_ir': bool(getattr(produto_meta, 'isento_ir', False))
                if produto_meta is not None else bool(getattr(l, 'produto_isento_ir', False)),
            'data_aplicacao_original': data_aplicacao_original,
            'saldo_snapshot': saldo_ref,
            'snapshot_data': hoje,
        }

        if data_aplicacao_original <= hoje and not bool(getattr(l, 'pendente_aporte', False)):
            lotes_iniciais_competicao.append((
                str(getattr(l, 'id', '')),
                saldo_ref,
                meta,
            ))
        else:
            dados_aportes.append((
                data_aplicacao_original,
                saldo_ref,
                str(getattr(l, 'id', '')),
                meta,
            ))

    lotes_iniciais_competicao.sort(key=lambda x: str(x[0]))
    dados_aportes.sort(key=lambda x: (x[0], str(x[2])))

    contas_ind_simples = []
    for conta in contas_futuras:
        dt, valor, desc, lote1, lote2, ordem = _normalizar_conta_processamento(conta)
        contas_ind_simples.append((dt, float(valor), str(desc), int(ordem)))
    contas_ind_simples = ordenar_contas_processamento(contas_ind_simples)

    df_agr = pd.DataFrame([
        {
            'Data': c[0],
            'Valor': float(c[1]),
            'Descrição': str(c[2]),
            'Ordem Processamento': int(c[3]),
        }
        for c in contas_ind_simples
    ])

    contas_agrupadas = []
    if not df_agr.empty:
        df_agr = df_agr.groupby('Data', as_index=False).agg({
            'Valor': 'sum',
            'Descrição': lambda x: ' | '.join(str(v) for v in x)[:100],
            'Ordem Processamento': 'min',
        })
        for _, row in df_agr.iterrows():
            contas_agrupadas.append((
                row['Data'],
                float(row['Valor']),
                str(row['Descrição']),
                int(row['Ordem Processamento']) if pd.notna(row['Ordem Processamento']) else ORDEM_PROCESSAMENTO_SENTINELA,
            ))
    contas_agrupadas = ordenar_contas_processamento(contas_agrupadas)

    if isinstance(contexto_canonico, dict):
        valores_originais = dict(contexto_canonico.get('valores_originais') or {})
    else:
        valores_originais = {}
        estado_rows = snapshot.get('estado_lotes_passado_snapshot')
        if isinstance(estado_rows, pd.DataFrame):
            estado_rows = estado_rows.to_dict('records')
        for st in list(estado_rows or []):
            lid = str(st.get('Lote ID', '') or '').strip()
            if lid:
                try:
                    valores_originais[lid] = float(st.get('Valor Inicial', 0.0) or 0.0)
                except Exception:
                    values = st.get('Valor Inicial', 0.0)
                    try:
                        valores_originais[lid] = float(values)
                    except Exception:
                        pass

    if isinstance(treinamento_ctx, dict):
        best_params_5p = dict(treinamento_ctx.get('best_params_5p') or {}) or {
            'peso_iof': 100.0, 'peso_ir': 0.0, 'peso_idade': 0.1, 'peso_liq': 0.0, 'peso_cliff': 1000.0, 'peso_vpl': 0.0,
        }
        best_genes_5p = np.array(
            treinamento_ctx.get('best_genes_5p')
            if treinamento_ctx.get('best_genes_5p') is not None
            else [10.0, 10.0, 0.0, 10.0, 50.0]
        )
        origem_params = treinamento_ctx.get('origem_parametros')
        cfg_treino_local = dict(treinamento_ctx.get('cfg_treino') or {})
    else:
        params_hibrido, origem_params = carregar_parametros_hibrido_5p()
        best_params_5p = dict(params_hibrido) if isinstance(params_hibrido, dict) else {
            'peso_iof': 100.0, 'peso_ir': 0.0, 'peso_idade': 0.1, 'peso_liq': 0.0, 'peso_cliff': 1000.0, 'peso_vpl': 0.0,
        }
        best_genes_5p = np.array([10.0, 10.0, 0.0, 10.0, 50.0])
        cfg_treino_local = {'wf_splits': AVALIACAO_WF_SPLITS_DEFAULT if 'AVALIACAO_WF_SPLITS_DEFAULT' in globals() else 4}

    competidores = [
        ('PENALIDADE_5P', best_params_5p),
        ('HIBRIDO_5P', best_params_5p),
        ('ECONOMICA_VPL', None),
        ('ECONOMICA_CLIFF', None),
        ('HEURISTICA', None),
        ('GENETICA_5P', best_genes_5p),
    ]

    return {
        'lotes_iniciais_competicao': lotes_iniciais_competicao,
        'dados_aportes': dados_aportes,
        'dados_contas_agr': contas_agrupadas,
        'contas_ind_simples': contas_ind_simples,
        'valores_originais': valores_originais,
        'data_referencia': hoje,
        'data_inicio_competicao': data_inicio_competicao,
        'cfg_treino': cfg_treino_local,
        'competidores': competidores,
        'best_params_5p': best_params_5p,
        'best_genes_5p': best_genes_5p,
        'origem_params_hibrido_5p': str(origem_params) if origem_params is not None else None,
        'taxa_proj': taxa_proj,
        'modo_referencia': (treinamento_ctx or {}).get('modo_referencia'),
        'treinamento_ctx': treinamento_ctx or {},
        'log_passado': list((contexto_canonico or {}).get('log_passado') or snapshot.get('log_passado') or []),
        'estado_lotes_passado': (contexto_canonico or {}).get('estado_lotes_passado', snapshot.get('estado_lotes_passado_snapshot')),
    }


def _auditar_base_competitiva(lotes_iniciais_competicao, dados_aportes):
    def _norm_id(v):
        return str(v or '').strip()

    ids_ini = []
    ids_apo = []
    soma_ini = 0.0
    soma_apo = 0.0

    for item in list(lotes_iniciais_competicao or []):
        try:
            lote_id, valor, _meta = item
        except Exception:
            continue
        lid = _norm_id(lote_id)
        if lid:
            ids_ini.append(lid)
        try:
            soma_ini += float(valor or 0.0)
        except Exception:
            pass

    for item in list(dados_aportes or []):
        try:
            _dt, valor, lote_id, _meta = item
        except Exception:
            continue
        lid = _norm_id(lote_id)
        if lid:
            ids_apo.append(lid)
        try:
            soma_apo += float(valor or 0.0)
        except Exception:
            pass

    set_ini = set(ids_ini)
    set_apo = set(ids_apo)

    dup_ini = sorted([lid for lid in set_ini if ids_ini.count(lid) > 1])
    dup_apo = sorted([lid for lid in set_apo if ids_apo.count(lid) > 1])
    overlap = sorted(set_ini.intersection(set_apo))

    auditoria = {
        'qtd_lotes_iniciais': len(list(lotes_iniciais_competicao or [])),
        'qtd_aportes': len(list(dados_aportes or [])),
        'soma_lotes_iniciais': round(float(soma_ini), 2),
        'soma_aportes': round(float(soma_apo), 2),
        'ids_duplicados_lotes_iniciais': dup_ini,
        'ids_duplicados_aportes': dup_apo,
        'ids_sobrepostos': overlap,
        'tem_sobreposicao': bool(overlap),
    }

    print("\n[AUDITORIA BASE COMPETITIVA]")
    print(f"  -> lotes_iniciais_competicao: {auditoria['qtd_lotes_iniciais']} | soma R$ {auditoria['soma_lotes_iniciais']:,.2f}")
    print(f"  -> dados_aportes:             {auditoria['qtd_aportes']} | soma R$ {auditoria['soma_aportes']:,.2f}")

    if dup_ini:
        print(f"  [ALERTA] IDs duplicados em lotes_iniciais_competicao: {dup_ini[:10]}")
    if dup_apo:
        print(f"  [ALERTA] IDs duplicados em dados_aportes: {dup_apo[:10]}")
    if overlap:
        print(f"  [ALERTA] IDs presentes nos dois grupos: {overlap[:10]}")
    else:
        print("  -> Sem sobreposição de IDs entre lotes iniciais e aportes.")

    return auditoria


def _snapshot_direto_lotes_ranking(lotes_finais, data_referencia, bcb_map=None, total_resgatado_liquido=0.0):
    data_ref = data_referencia or DATA_REFERENCIA
    try:
        data_ref_efetiva = obter_data_referencia_relatorio(bcb_map, data_ref)
    except Exception:
        data_ref_efetiva = data_ref

    saldo_bruto = 0.0
    saldo_liquido = 0.0
    total_lotes = 0
    lotes_ativos = 0

    for lote in list(lotes_finais or []):
        if lote is None:
            continue

        total_lotes += 1

        try:
            data_apl = getattr(lote, 'data_aplicacao', data_ref_efetiva)
            if isinstance(data_apl, pd.Timestamp):
                data_apl = data_apl.date()
            elif isinstance(data_apl, datetime):
                data_apl = data_apl.date()
        except Exception:
            data_apl = data_ref_efetiva

        if data_apl is not None and data_apl > data_ref_efetiva:
            continue

        saldo = float(getattr(lote, 'saldo_bruto', 0.0) or 0.0)
        esgotado = bool(getattr(lote, 'esgotado', False))

        if esgotado or saldo <= VALOR_MINIMO_LOTE_ATIVO:
            continue

        lotes_ativos += 1
        saldo_bruto += saldo

        try:
            fator_liq = float(lote.get_fator_liquido(data_ref_efetiva) or 0.0)
        except Exception:
            fator_liq = 1.0

        if not np.isfinite(fator_liq) or fator_liq <= 0.0:
            fator_liq = 1.0

        saldo_liquido += saldo * fator_liq

    patrimonio_liquido = float(saldo_liquido) + float(total_resgatado_liquido or 0.0)

    return {
        'data_referencia_efetiva': data_ref_efetiva,
        'saldo_bruto': round(float(saldo_bruto), 2),
        'saldo_liquido': round(float(saldo_liquido), 2),
        'patrimonio_liquido': round(float(patrimonio_liquido), 2),
        'lotes_ativos': int(lotes_ativos),
        'total_lotes': int(total_lotes),
    }

def _executar_bloco_competitivo_unificado(
    *,
    dados_competicao,
    snapshot,
    bcb_map,
    hoje,
):
    del snapshot
    dados_aportes = list(dados_competicao.get('dados_aportes') or [])
    dados_contas_agr = list(dados_competicao.get('dados_contas_agr') or [])
    contas_ind_simples = list(dados_competicao.get('contas_ind_simples') or [])
    competidores = list(dados_competicao.get('competidores') or [])
    taxa_proj = float(dados_competicao.get('taxa_proj') or TAXA_DIA_BASE)
    valores_originais = dict(dados_competicao.get('valores_originais') or {})
    log_passado = list(dados_competicao.get('log_passado') or [])
    estado_lotes_passado = dados_competicao.get('estado_lotes_passado')
    lotes_iniciais_competicao = list(dados_competicao.get('lotes_iniciais_competicao') or [])
    data_inicio_competicao = dados_competicao.get('data_inicio_competicao') or hoje

    auditoria_base_competitiva = _auditar_base_competitiva(
        lotes_iniciais_competicao=lotes_iniciais_competicao,
        dados_aportes=dados_aportes,
    )

    ranking = []
    resultados_wf = {}
    contas_por_estrategia = {}
    df_res = pd.DataFrame()
    melhor_estrategia = None
    modo_vencedor = None
    lotes_melhor = []
    df_situacao_atual_melhor = pd.DataFrame()
    df_situacao_final_melhor = pd.DataFrame()
    resumo_melhor_estrategia = pd.DataFrame()
    snapshot_financeiro_final = {}
    col_saldo = None

    if (not dados_aportes and not lotes_iniciais_competicao) or not competidores:
        return {
            'ranking_df': pd.DataFrame(),
            'resultados_wf': {},
            'melhor_estrategia': None,
            'modo_vencedor': None,
            'lotes_melhor': [],
            'df_situacao_atual_melhor': pd.DataFrame(),
            'df_situacao_final_melhor': pd.DataFrame(),
            'resumo_melhor_estrategia': pd.DataFrame(),
            'snapshot_financeiro_final': {},
            'resultados_estrategias': {},
            'auditoria_base_competitiva': {},
        }

    print("\n" + '-' * 60)
    print("COMPETIÇÃO FINAL (modo escolhido por estratégia)")
    print('-' * 60 + "\n")

    modo_analise_forcado = str(dados_competicao.get('modo_referencia') or 'agrupado')
    print('OPÇÃO DE MODO PARA A ANÁLISE FINAL')
    print('-' * 60)
    print(f" -> Modo recomendado pelo teste de agrupamento: {modo_analise_forcado}")
    print(f" -> Modo da análise final aplicado automaticamente: {modo_analise_forcado}")

    total_resgatado_passado = 0.0
    total_imposto_passado = 0.0
    for entrada in log_passado:
        try:
            total_resgatado_passado += float(entrada.get('Liquido', 0.0) or 0.0)
            total_imposto_passado += float(entrada.get('Imposto', 0.0) or 0.0)
        except Exception:
            continue

    resultados_estrategias = {}
    for nome, params in competidores:
        print(f" -> {nome}...")
        t0 = time.time()
        try:
            saldo_agr_e, _, _, stats_agr_e = rodar_estrategia(
                nome,
                dados_aportes,
                dados_contas_agr,
                params_opt=params,
                bcb_map=bcb_map,
                taxa_proj=taxa_proj,
                lotes_iniciais=lotes_iniciais_competicao,
                data_inicio_competicao=data_inicio_competicao,
            )
            saldo_ind_e, _, _, stats_ind_e = rodar_estrategia(
                nome,
                dados_aportes,
                contas_ind_simples,
                params_opt=params,
                bcb_map=bcb_map,
                taxa_proj=taxa_proj,
                lotes_iniciais=lotes_iniciais_competicao,
                data_inicio_competicao=data_inicio_competicao,
            )
            score_agr_e = stats_agr_e.get('saldo_liquido_final', saldo_agr_e) - stats_agr_e.get('valor_nao_coberto', 0.0)
            score_ind_e = stats_ind_e.get('saldo_liquido_final', saldo_ind_e) - stats_ind_e.get('valor_nao_coberto', 0.0)
            if modo_analise_forcado == 'individual':
                contas_exec = contas_ind_simples
                modo_exec = 'individual'
            elif modo_analise_forcado == 'agrupado':
                contas_exec = dados_contas_agr
                modo_exec = 'agrupado'
            elif score_ind_e > score_agr_e:
                contas_exec = contas_ind_simples
                modo_exec = 'individual'
            else:
                contas_exec = dados_contas_agr
                modo_exec = 'agrupado'
            contas_por_estrategia[nome] = contas_exec

            saldo, df_log, lotes_finais, stats = rodar_estrategia(
                nome,
                dados_aportes,
                contas_exec,
                params_opt=params,
                bcb_map=bcb_map,
                taxa_proj=taxa_proj,
                lotes_iniciais=lotes_iniciais_competicao,
                data_inicio_competicao=data_inicio_competicao,
            )
            print(f"    Modo: {modo_exec}")

            data_terminal_estrategia = (
                stats.get('data_referencia_relatorio')
                or stats.get('data_fim')
                or max((c[0] for c in contas_exec), default=hoje)
            )

            try:
                total_resgatado_liquido_local = (
                    float(total_resgatado_passado or 0.0)
                    + float(stats.get('total_resgatado_liquido', 0.0) or 0.0)
                )

                df_situacao_local, _ = gerar_relatorio_melhor_estrategia_por_lotes_finais(
                    lotes_finais=lotes_finais,
                    data_terminal_estrategia=data_terminal_estrategia,
                    total_resgatado_liquido=total_resgatado_liquido_local,
                    mapa_bcb=bcb_map,
                    estrategia=nome,
                    modo=modo_exec,
                    valor_nao_coberto=float(stats.get('valor_nao_coberto', 0.0) or 0.0),
                    info_ranking={},
                    info_wf={},
                )
            except Exception:
                df_situacao_local = pd.DataFrame()

            snapshot_direto = _snapshot_direto_lotes_ranking(
                lotes_finais=lotes_finais,
                data_referencia=data_terminal_estrategia,
                bcb_map=bcb_map,
                total_resgatado_liquido=(
                    float(total_resgatado_passado)
                    + float(stats.get('total_resgatado_liquido', 0.0) or 0.0)
                ),
            )

            saldo_bruto_ranking = float(snapshot_direto['saldo_bruto'])
            saldo_liquido_ranking = float(snapshot_direto['saldo_liquido'])
            patrimonio_liquido_ranking = float(snapshot_direto['patrimonio_liquido'])

            valor_nao_coberto = float(stats.get('valor_nao_coberto', 0.0) or 0.0)
            saldo_liquido_aj_ranking = saldo_liquido_ranking - valor_nao_coberto

            total_lotes = int(snapshot_direto.get('total_lotes', 0) or 0)
            lotes_usados = int(stats.get('num_lotes_usados', 0) or 0)
            if lotes_usados <= 0:
                lotes_usados = int(snapshot_direto.get('lotes_ativos', 0) or 0)

            auditoria_ranking = {
                'snapshot_direto': dict(snapshot_direto),
                'saldo_bruto_relatorio': None,
                'saldo_liquido_relatorio': None,
                'patrimonio_liquido_relatorio': None,
                'delta_saldo_bruto_relatorio_vs_direto': None,
                'delta_saldo_liquido_relatorio_vs_direto': None,
                'delta_patrimonio_relatorio_vs_direto': None,
            }

            if isinstance(df_situacao_local, pd.DataFrame) and not df_situacao_local.empty:
                try:
                    rel_bruto = 0.0
                    rel_liq = 0.0
                    rel_pat = 0.0

                    row_total = (
                        df_situacao_local[df_situacao_local['Lote ID'] == 'TOTAL']
                        if 'Lote ID' in df_situacao_local.columns
                        else pd.DataFrame()
                    )

                    if not row_total.empty:
                        row0 = row_total.iloc[0]
                        rel_bruto = float(row0.get('Saldo Bruto Atual (R$)', 0.0) or 0.0)
                        rel_liq = float(row0.get('Saldo Líquido Atual (R$)', 0.0) or 0.0)
                        rel_pat = float(row0.get('Patrimônio Líquido até Hoje (R$)', 0.0) or 0.0)
                    else:
                        if 'Saldo Bruto Atual (R$)' in df_situacao_local.columns:
                            rel_bruto = float(pd.to_numeric(df_situacao_local['Saldo Bruto Atual (R$)'], errors='coerce').fillna(0.0).sum())
                        if 'Saldo Líquido Atual (R$)' in df_situacao_local.columns:
                            rel_liq = float(pd.to_numeric(df_situacao_local['Saldo Líquido Atual (R$)'], errors='coerce').fillna(0.0).sum())
                        if 'Patrimônio Líquido até Hoje (R$)' in df_situacao_local.columns:
                            rel_pat = float(pd.to_numeric(df_situacao_local['Patrimônio Líquido até Hoje (R$)'], errors='coerce').fillna(0.0).sum())

                    auditoria_ranking.update({
                        'saldo_bruto_relatorio': round(rel_bruto, 2),
                        'saldo_liquido_relatorio': round(rel_liq, 2),
                        'patrimonio_liquido_relatorio': round(rel_pat, 2),
                        'delta_saldo_bruto_relatorio_vs_direto': round(rel_bruto - saldo_bruto_ranking, 2),
                        'delta_saldo_liquido_relatorio_vs_direto': round(rel_liq - saldo_liquido_ranking, 2),
                        'delta_patrimonio_relatorio_vs_direto': round(rel_pat - patrimonio_liquido_ranking, 2),
                    })

                except Exception:
                    pass

            tempo_exec = round(time.time() - t0, 2)

            resultados_estrategias[nome] = {
                'saldo_final': saldo,
                'df_log': df_log,
                'lotes_finais': lotes_finais,
                'stats': stats,
                'modo_exec': modo_exec,
                'df_situacao_local': df_situacao_local,
                'data_terminal_estrategia': data_terminal_estrategia,
                'auditoria_ranking': auditoria_ranking,
            }

            ranking.append({
                'Estratégia': nome,
                'Modo': modo_exec,
                'Saldo Líq Aj.': round(float(saldo_liquido_aj_ranking), 2),
                'Saldo Líq': round(float(saldo_liquido_ranking), 2),
                'Saldo Bruto': round(float(saldo_bruto_ranking), 2),
                'Saldo Final (R$)': round(float(saldo_bruto_ranking), 2),
                'Saldo Líquido (R$)': round(float(saldo_liquido_ranking), 2),
                'Saldo Líquido Ajustado (R$)': round(float(saldo_liquido_aj_ranking), 2),
                'Total Resgatado (R$)': round(float(stats.get('total_resgatado_liquido', 0.0) or 0.0), 2),
                'Imposto Total (R$)': round(float(stats.get('total_imposto', 0.0) or 0.0), 2),
                'Total Resgatado c/ Passado (R$)': round(float(stats.get('total_resgatado_liquido', 0.0) or 0.0) + total_resgatado_passado, 2),
                'Imposto Total c/ Passado (R$)': round(float(stats.get('total_imposto', 0.0) or 0.0) + total_imposto_passado, 2),
                'Não Coberto': round(float(valor_nao_coberto), 2),
                'Valor Não Coberto (R$)': round(float(valor_nao_coberto), 2),
                'Contas Não Cobertas': int(stats.get('contas_nao_cobertas', 0) or 0),
                'Eficiência Fiscal (%)': round(float(stats.get('eficiencia_fiscal', 0.0) or 0.0), 2),
                'Riqueza Total (R$)': round(float(stats.get('riqueza_total', 0.0) or 0.0), 2),
                'NPV Riqueza (R$)': round(float(stats.get('npv_riqueza', 0.0) or 0.0), 2),
                'Patrimônio Líq.': round(float(patrimonio_liquido_ranking), 2),
                'Lotes Usados': lotes_usados,
                'Total Lotes': total_lotes,
                'Lotes': f"{lotes_usados}/{total_lotes}" if total_lotes else f"{lotes_usados}/0",
                'Tempo': tempo_exec,
                'Tempo (s)': tempo_exec,
            })
        except Exception as e:
            ranking.append({
                'Estratégia': nome,
                'Modo': 'erro',
                'Saldo Final (R$)': None,
                'Saldo Líquido (R$)': None,
                'Saldo Líquido Ajustado (R$)': None,
                'Total Resgatado (R$)': None,
                'Imposto Total (R$)': None,
                'Total Resgatado c/ Passado (R$)': None,
                'Imposto Total c/ Passado (R$)': None,
                'Valor Não Coberto (R$)': None,
                'Contas Não Cobertas': None,
                'Eficiência Fiscal (%)': None,
                'Riqueza Total (R$)': None,
                'NPV Riqueza (R$)': None,
                'Lotes Usados': None,
                'Total Lotes': None,
                'Tempo (s)': round(time.time() - t0, 2),
                'Erro': str(e),
            })

    try:
        resultados_wf = validacao_walk_forward(
            dados_aportes,
            dados_contas_agr,
            competidores,
            pct_treino=AVALIACAO_WF_PCT_TREINO,
            bcb_map=bcb_map,
            taxa_proj=taxa_proj,
            n_splits=int(dados_competicao.get('cfg_treino', {}).get('wf_splits', 4) or 4),
            contas_por_estrategia=contas_por_estrategia,
            lotes_iniciais=lotes_iniciais_competicao,
            data_inicio_competicao=data_inicio_competicao,
        )
    except Exception:
        resultados_wf = {}

    if ranking:
        df_res = pd.DataFrame(ranking)
        for cand in ['Saldo Líq Aj.', 'Saldo Líquido Ajustado (R$)', 'Saldo Líq', 'Saldo Líquido (R$)', 'Saldo Bruto', 'Saldo Final (R$)']:
            if cand in df_res.columns:
                col_saldo = cand
                break
        if col_saldo is None:
            for c in df_res.columns:
                if 'Saldo' in c or 'saldo' in c:
                    col_saldo = c
                    break
        if col_saldo is not None:
            robustez_map = {k: v.get('score_robustez', AVALIACAO_WF_ROBUSTEZ_DEFAULT) for k, v in (resultados_wf or {}).items() if isinstance(v, dict)}
            df_res['WF'] = df_res['Estratégia'].map(lambda n: robustez_map.get(n, AVALIACAO_WF_ROBUSTEZ_DEFAULT))
            df_res['Robustez WF'] = df_res['WF']
            saldo_numerico = pd.to_numeric(df_res[col_saldo], errors='coerce').fillna(-1e18)
            df_res['Score'] = saldo_numerico * (AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ * (pd.to_numeric(df_res['WF'], errors='coerce').fillna(0.0) / 100.0))
            df_res['Score Final'] = df_res['Score']
            base_mask = df_res['Estratégia'] == 'HEURISTICA'
            base_saldo = float(df_res.loc[base_mask, col_saldo].iloc[0]) if base_mask.any() else None
            if base_saldo not in (None, 0):
                df_res['Ganho %'] = ((saldo_numerico - base_saldo) / base_saldo) * 100.0
            else:
                df_res['Ganho %'] = 0.0
            df_res = df_res.sort_values(by=['Score', col_saldo], ascending=False, na_position='last').reset_index(drop=True)

    if not df_res.empty:
        melhor_estrategia = df_res.iloc[0]['Estratégia']
        modo_vencedor = df_res.iloc[0].get('Modo')
        params_map = {n: p for n, p in competidores}
        contas_exec = contas_por_estrategia.get(melhor_estrategia, dados_contas_agr)
        try:
            _, _, lotes_melhor, stats_melhor = rodar_estrategia(
                melhor_estrategia,
                dados_aportes,
                contas_exec,
                params_opt=params_map.get(melhor_estrategia),
                bcb_map=bcb_map,
                taxa_proj=taxa_proj,
                lotes_iniciais=lotes_iniciais_competicao,
                data_inicio_competicao=data_inicio_competicao,
            )
        except Exception:
            lotes_melhor = []
            stats_melhor = {}

        data_terminal_melhor = (
            stats_melhor.get('data_referencia_relatorio')
            or stats_melhor.get('data_fim')
            or max((c[0] for c in contas_exec), default=hoje)
        )

        try:
            info_ranking_melhor = df_res.iloc[0].to_dict() if not df_res.empty else {}
            info_wf_melhor = dict(resultados_wf.get(melhor_estrategia) or {})
            total_resgatado_liquido_melhor = (
                float(total_resgatado_passado or 0.0)
                + float(stats_melhor.get('total_resgatado_liquido', 0.0) or 0.0)
            )
            df_situacao_atual_melhor = gerar_relatorio_situacao_atual(
                lotes_hoje=lotes_melhor,
                estado_lotes_passado=estado_lotes_passado,
                log_passado=log_passado,
                valores_originais=valores_originais,
                mapa_bcb=bcb_map,
                data_referencia=hoje,
            )
            df_situacao_final_melhor, resumo_melhor_estrategia = gerar_relatorio_melhor_estrategia_por_lotes_finais(
                lotes_finais=lotes_melhor,
                data_terminal_estrategia=data_terminal_melhor,
                total_resgatado_liquido=total_resgatado_liquido_melhor,
                mapa_bcb=bcb_map,
                estrategia=melhor_estrategia,
                modo=modo_vencedor,
                valor_nao_coberto=float(stats_melhor.get('valor_nao_coberto', 0.0) or 0.0),
                info_ranking=info_ranking_melhor,
                info_wf=info_wf_melhor,
            )
        except Exception:
            df_situacao_atual_melhor = pd.DataFrame()
            df_situacao_final_melhor = pd.DataFrame()
            resumo_melhor_estrategia = pd.DataFrame()

        snapshot_financeiro_final = capturar_snapshot_financeiro_final(
            df_res=df_res,
            col_saldo=col_saldo,
            melhor_estrategia=melhor_estrategia,
            resultados_wf=resultados_wf,
            lotes_melhor=lotes_melhor,
            df_situacao_atual=df_situacao_final_melhor,
            nome='snapshot_financeiro_final_unificado',
        )

    if not df_res.empty:
        print("\n" + "=" * 100)
        print("RANKING FINAL - TODAS AS ESTRATÉGIAS")
        print("=" * 100)
        print()
        print(f"{'Estratégia':<22} {'Modo':<10} {'Saldo Líq Aj.':>14} {'Saldo Líq':>12} {'Saldo Bruto':>14} {'Não Coberto':>13} {'WF':>7} {'Score':>12} {'Lotes':>10} {'Tempo':>8} {'Ganho %':>10}")
        print("-" * 172)
        for _, row in df_res.iterrows():
            lotes_str = row.get('Lotes')
            if not lotes_str:
                lotes_str = f"{int(row.get('Lotes Usados', 0) or 0)}/{int(row.get('Total Lotes', 0) or 0)}"
            print(
                f"{str(row.get('Estratégia', '')):<22} "
                f"{str(row.get('Modo', '-')):<10} "
                f"{float(row.get('Saldo Líq Aj.', row.get('Saldo Líquido Ajustado (R$)', 0.0)) or 0.0):>14,.2f} "
                f"{float(row.get('Saldo Líq', row.get('Saldo Líquido (R$)', 0.0)) or 0.0):>12,.2f} "
                f"{float(row.get('Saldo Bruto', row.get('Saldo Final (R$)', 0.0)) or 0.0):>14,.2f} "
                f"{float(row.get('Não Coberto', row.get('Valor Não Coberto (R$)', 0.0)) or 0.0):>13,.2f} "
                f"{float(row.get('WF', row.get('Robustez WF', 0.0)) or 0.0):>7.2f} "
                f"{float(row.get('Score', row.get('Score Final', 0.0)) or 0.0):>12,.2f} "
                f"{str(lotes_str):>10} "
                f"{float(row.get('Tempo', row.get('Tempo (s)', 0.0)) or 0.0):>8.2f} "
                f"{float(row.get('Ganho %', 0.0) or 0.0):>9.2f}%"
            )
        if resultados_wf:
            print("\nResumo de robustez (top 5):")
            itens_top = sorted(resultados_wf.items(), key=lambda kv: float((kv[1] or {}).get('score_robustez', -1e9)), reverse=True)[:5]
            for nome, info in itens_top:
                print(
                    f" - {nome}: robustez={float((info or {}).get('score_robustez', 0.0) or 0.0):.2f} | "
                    f"liq_teste={float((info or {}).get('saldo_liquido_teste_medio', 0.0) or 0.0):,.2f}"
                )

    if melhor_estrategia:
        print("\n" + "=" * 90)
        print("SITUAÇÃO ATUAL - MELHOR ESTRATÉGIA")
        print("=" * 90)
        print(f"Estratégia vencedora: {melhor_estrategia}")
        if modo_vencedor:
            print(f"Modo utilizado: {modo_vencedor}")
        if not df_situacao_atual_melhor.empty:
            colunas_imp = [
                'Lote ID',
                'Carteira',
                'Data Aplicação',
                'Data Base Fiscal',
                'Dias Corridos até Hoje',
                'Dias Úteis até Hoje',
                'Valor Original (R$)',
                'Total Líquido Sacado (R$)',
                'Saldo Bruto Atual (R$)',
                'Saldo Líquido Atual (R$)',
                'Patrimônio Líquido até Hoje (R$)',
                'Ganho da Otimização vs Dinheiro Parado (R$)',
            ]
            colunas_imp = [c for c in colunas_imp if c in df_situacao_atual_melhor.columns]
            if colunas_imp:
                df_print = df_situacao_atual_melhor[colunas_imp].copy()
            else:
                df_print = df_situacao_atual_melhor.copy()
            try:
                with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 220):
                    print(df_print.to_string(index=False))
            except Exception:
                print(df_print)
        print("\n✅ Otimização concluída!")

    return {
        'ranking_df': df_res,
        'resultados_wf': resultados_wf,
        'melhor_estrategia': melhor_estrategia,
        'modo_vencedor': modo_vencedor,
        'lotes_melhor': lotes_melhor,
        'df_situacao_atual_melhor': df_situacao_atual_melhor,
        'df_situacao_final_melhor': df_situacao_final_melhor,
        'resumo_melhor_estrategia': resumo_melhor_estrategia,
        'snapshot_financeiro_final': snapshot_financeiro_final,
        'resultados_estrategias': resultados_estrategias,
        'auditoria_base_competitiva': auditoria_base_competitiva,
    }


def _exportar_resultados_unificados(
    *,
    caminho_excel,
    hoje,
    snapshot,
    plano_aportes,
    artefatos_switching,
    resultado_futuro,
    resultado_competitivo,
    diagnostico_plano,
    arquivo_saida=None,
):
    del caminho_excel
    if arquivo_saida is None:
        arquivo_saida = 'resultado_unificado_v34_ranking_auditado.xlsx'

    stats_futuro = dict(resultado_futuro.get('stats_futuro') or {})
    if not stats_futuro:
        stats_futuro = {
            'saldo_liquido_final': 0.0,
            'saldo_bruto_final': 0.0,
            'riqueza': 0.0,
        }

    _escrever_resultados_excel(
        arquivo_saida,
        extrato_df=_df_or_empty(resultado_futuro.get('extrato_futuro')),
        log_passado=snapshot.get('log_passado') or [],
        df_relatorio=_df_or_empty(resultado_futuro.get('df_relatorio_final')),
        df_analise_switch=_df_or_empty(artefatos_switching.get('analise_switch')),
        df_validacao_pool=_df_or_empty(artefatos_switching.get('validacao_pool')),
        df_plano_aportes=_df_or_empty(plano_aportes),
        df_plano_switches=_df_or_empty(artefatos_switching.get('plano_switches_final')),
        df_switches_detalhados=_df_or_empty(resultado_futuro.get('switches_detalhados')),
        df_exec_plano_externo=_df_or_empty(resultado_futuro.get('execucao_plano_externo')),
        df_desvios_plano_externo=_df_or_empty(resultado_futuro.get('desvios_plano_externo')),
        df_fallbacks_plano_externo=_df_or_empty(resultado_futuro.get('fallbacks_plano_externo')),
        df_diag_datas=_df_or_empty(artefatos_switching.get('diag_datas')),
        df_diag_planos=_df_or_empty(artefatos_switching.get('diag_planos')),
        df_comparativo_validacao=_df_or_empty(artefatos_switching.get('df_comparativo_validacao')),
        df_diagnostico_modo=_montar_df_diagnostico_modo_execucao(),
        stats=stats_futuro,
        df_resumo_lotes_atuais=_df_or_empty(snapshot.get('snapshot_lotes_atuais')),
        produtos=PRODUTOS_GLOBAIS_SIMULACAO or [],
    )

    with pd.ExcelWriter(arquivo_saida, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        if EXPORTAR_DEBUG:
            _escrever_se_nao_vazio(writer, _df_or_empty(artefatos_switching.get('df_situacao_atual')), 'Situacao_Atual_Switching')
        _escrever_se_nao_vazio(writer, _df_or_empty(resultado_competitivo.get('ranking_df')), 'Ranking_Final')
        _escrever_se_nao_vazio(writer, pd.DataFrame.from_dict(resultado_competitivo.get('resultados_wf') or {}, orient='index').reset_index().rename(columns={'index': 'Estratégia'}), 'Resultados_Walk_Forward')
        _escrever_se_nao_vazio(writer, _df_or_empty(resultado_competitivo.get('df_situacao_atual_melhor')), 'Situacao_Atual_Melhor_Estrat')
        _escrever_se_nao_vazio(writer, _df_or_empty(resultado_competitivo.get('df_situacao_final_melhor')), 'Situacao_Final_Melhor_Estrat')
        _escrever_se_nao_vazio(writer, pd.DataFrame([resultado_competitivo.get('snapshot_financeiro_final') or {}]), 'Snapshot_Financeiro_Final')
        resumo_melhor = resultado_competitivo.get('resumo_melhor_estrategia')
        if not isinstance(resumo_melhor, pd.DataFrame) or resumo_melhor.empty:
            ranking_df = resultado_competitivo.get('ranking_df')
            if isinstance(ranking_df, pd.DataFrame) and not ranking_df.empty:
                resumo_melhor = ranking_df.head(1).copy()
            else:
                resumo_melhor = pd.DataFrame([{
                    'Estratégia': resultado_competitivo.get('melhor_estrategia'),
                    'Modo': resultado_competitivo.get('modo_vencedor'),
                }])
        _escrever_se_nao_vazio(writer, _df_or_empty(resumo_melhor), 'Resumo_Melhor_Estrategia')
        resultados_estrategias = resultado_competitivo.get('resultados_estrategias') or {}
        linhas_resultados = []
        for nome, payload in resultados_estrategias.items():
            stats_local = payload.get('stats') or {}
            linhas_resultados.append({
                'Estratégia': nome,
                'Modo': payload.get('modo_exec'),
                'Saldo Líquido Final (R$)': round(float(stats_local.get('saldo_liquido_final', 0.0) or 0.0), 2),
                'Valor Não Coberto (R$)': round(float(stats_local.get('valor_nao_coberto', 0.0) or 0.0), 2),
                'Riqueza Total (R$)': round(float(stats_local.get('riqueza_total', 0.0) or 0.0), 2),
                'NPV Riqueza (R$)': round(float(stats_local.get('npv_riqueza', 0.0) or 0.0), 2),
                'Lotes Usados': stats_local.get('num_lotes_usados'),
                'Total Lotes': stats_local.get('total_lotes'),
            })
        _escrever_se_nao_vazio(writer, pd.DataFrame(linhas_resultados), 'Resultados_Estrategias')
        if EXPORTAR_DEBUG:
            _escrever_se_nao_vazio(writer, pd.DataFrame([diagnostico_plano.get('diagnostico_plano_externo') or {}]), 'Diagnostico_Plano_Externo')

    return {
        'arquivo_saida': arquivo_saida,
        'melhor_estrategia': resultado_competitivo.get('melhor_estrategia'),
        'modo_vencedor': resultado_competitivo.get('modo_vencedor'),
        'qtd_lotes_finais': len(resultado_futuro.get('lotes_finais_reais') or []),
        'qtd_linhas_extrato': len(_df_or_empty(resultado_futuro.get('extrato_futuro'))),
    }

# =========================================================
# 15. BOOTSTRAP CANÔNICO DE EXECUÇÃO
# =========================================================

def _inicializar_contexto_execucao():
    print("=" * 74)
    print("SIMULADOR FINANCEIRO V34 LIMPEZA CÓDIGO V3 - INICIALIZAÇÃO")
    print("=" * 74)

    hoje = data_hoje_referencia()
    caminho_excel = _resolver_arquivo_excel_local()
    _print_once('planilha_principal', f">>> [ARQUIVOS] Planilha principal carregada: {caminho_excel}")

    bcb_map, ultima_taxa = obter_historico_bcb()
    _print_once('bcb_resumo', f">>> [BCB] Dias CDI carregados: {len(bcb_map)} | última taxa base: {float(ultima_taxa):.8f}")

    produtos = carregar_carteira()
    if not produtos:
        raise RuntimeError("Nenhum produto encontrado na aba Carteira.")

    global PRODUTO_PADRAO, PRODUTOS_GLOBAIS_SIMULACAO
    PRODUTOS_GLOBAIS_SIMULACAO = list(produtos)

    PRODUTO_PADRAO, origem_produto_padrao = resolver_produto_padrao(produtos)
    nome_padrao = getattr(PRODUTO_PADRAO, 'nome', 'N/D') if PRODUTO_PADRAO is not None else 'N/D'
    print(f">>> [DADOS] Carteira={len(produtos)} | Produto padrão={nome_padrao} | origem={origem_produto_padrao}")

    return caminho_excel, hoje, bcb_map, produtos

def main():
    caminho_excel, hoje, bcb_map, produtos = _inicializar_contexto_execucao()
    globals()['MAPA_BCB'] = bcb_map
    globals()['DATA_REFERENCIA'] = hoje
    globals()['TAXA_PROJ'] = _resolver_taxa_proj_unificada(bcb_map)

    snapshot = _carregar_snapshot_inicial(produtos, bcb_map)
    lotes_passados = list(snapshot['lotes_passados'])
    lotes_futuros = list(snapshot['lotes_futuros'])
    contas = list(snapshot['contas'])

    lotes_passados, lotes_futuros, plano_aportes, contas_futuras = _alocar_aportes_iniciais(
        lotes_passados,
        lotes_futuros,
        produtos,
        bcb_map,
        contas,
        hoje,
    )

    contexto_canonico = _resolver_contexto_canonico_compartilhado(
        snapshot=snapshot,
        lotes_passados=lotes_passados,
        bcb_map=bcb_map,
        hoje=hoje,
    )

    diagnostico_plano = _carregar_e_validar_plano_externo_unificado(
        snapshot=snapshot,
        contas_futuras=contas_futuras,
        hoje=hoje,
        produtos=produtos,
        bcb_map=bcb_map,
    )

    artefatos_switching = _materializar_artefatos_switching_unificados(
        snapshot=snapshot,
        lotes_passados=lotes_passados,
        lotes_futuros=lotes_futuros,
        contas_futuras=contas_futuras,
        produtos=produtos,
        bcb_map=bcb_map,
        hoje=hoje,
        contexto_canonico=contexto_canonico,
    )
    artefatos_switching['plano_aportes'] = plano_aportes
    artefatos_switching['contexto_canonico'] = contexto_canonico

    resultado_futuro = _executar_futuro_unificado(
        lotes_passados=artefatos_switching['lotes_passados'],
        lotes_futuros=artefatos_switching['lotes_futuros'],
        contas_futuras=contas_futuras,
        produtos=produtos,
        bcb_map=bcb_map,
        hoje=hoje,
        artefatos_switching=artefatos_switching,
    )

    dados_competicao_base = _montar_dados_competicao_unificada(
        snapshot=snapshot,
        lotes_passados=artefatos_switching['lotes_passados'],
        lotes_futuros=artefatos_switching['lotes_futuros'],
        contas_futuras=contas_futuras,
        produtos=produtos,
        bcb_map=bcb_map,
        hoje=hoje,
        contexto_canonico=contexto_canonico,
        treinamento_ctx={},
    )

    treinamento_ctx = _selecionar_modo_treinamento_unificado(
        dados_aportes=dados_competicao_base.get('dados_aportes') or [],
        dados_contas_agr=dados_competicao_base.get('dados_contas_agr') or [],
        contas_ind_simples=dados_competicao_base.get('contas_ind_simples') or [],
        bcb_map=bcb_map,
        lotes_iniciais_competicao=dados_competicao_base.get('lotes_iniciais_competicao') or [],
        data_inicio_competicao=dados_competicao_base.get('data_inicio_competicao'),
    )

    dados_competicao = _montar_dados_competicao_unificada(
        snapshot=snapshot,
        lotes_passados=artefatos_switching['lotes_passados'],
        lotes_futuros=artefatos_switching['lotes_futuros'],
        contas_futuras=contas_futuras,
        produtos=produtos,
        bcb_map=bcb_map,
        hoje=hoje,
        contexto_canonico=contexto_canonico,
        treinamento_ctx=treinamento_ctx,
    )

    resultado_competitivo = _executar_bloco_competitivo_unificado(
        dados_competicao=dados_competicao,
        snapshot=snapshot,
        bcb_map=bcb_map,
        hoje=hoje,
    )

    exportacao = _exportar_resultados_unificados(
        caminho_excel=caminho_excel,
        hoje=hoje,
        snapshot=snapshot,
        plano_aportes=plano_aportes,
        artefatos_switching=artefatos_switching,
        resultado_futuro=resultado_futuro,
        resultado_competitivo=resultado_competitivo,
        diagnostico_plano=diagnostico_plano,
    )

    return {
        'status': 'ok',
        'hoje': hoje,
        'snapshot_base': snapshot,
        'diagnostico_plano': diagnostico_plano,
        'plano_aportes': plano_aportes,
        'resultado_operacional': {
            'switching': artefatos_switching,
            'futuro': resultado_futuro,
        },
        'treinamento_ctx': treinamento_ctx,
        'resultado_competitivo': resultado_competitivo,
        'exportacao_final': exportacao,
    }

# =========================================================

# =========================================================

# =========================================================
# 13.1 REBIND MODULAR FASE 2–3 (DOMAIN + INGEST)
# =========================================================
from src.domain.tax_engine import (
    set_tax_runtime,
    _money_round_half_up as _money_round_half_up_modular,
    dinheiro_round as dinheiro_round_modular,
    _taxa_ir as _taxa_ir_modular,
    obter_aliquota_ir as obter_aliquota_ir_modular,
    _taxa_iof as _taxa_iof_modular,
    _fator_liquido as _fator_liquido_modular,
)
from src.domain.models import (
    set_models_runtime,
    Produto as Produto_modular,
    ComboProduto as ComboProduto_modular,
    Lote as Lote_modular,
    criar_lote_de_aporte as criar_lote_de_aporte_modular,
    atualizar_saldo_lotes_no_dia as atualizar_saldo_lotes_no_dia_modular,
    executar_saque_lote as executar_saque_lote_modular,
    montar_log_movimento_lote as montar_log_movimento_lote_modular,
    calcular_saldo_atual_lotes as calcular_saldo_atual_lotes_modular,
    serializar_lote_remanescente as serializar_lote_remanescente_modular,
)
from src.ingest.excel_loader import (
    set_excel_loader_runtime,
    ler_aba_excel as ler_aba_excel_modular,
    _normalizar_token_coluna as _normalizar_token_coluna_modular,
    _normalizar_nome_coluna as _normalizar_nome_coluna_modular,
    nome_aba as nome_aba_modular,
    aliases_coluna as aliases_coluna_modular,
    resolver_coluna as resolver_coluna_modular,
)

set_tax_runtime(ir_faixas=IR_FAIXAS, iof_table=IOF_TABLE)
set_models_runtime(
    taxa_base_default=TAXA_BASE_DEFAULT,
    taxa_bonus_default=TAXA_BONUS_DEFAULT,
    dias_bonus_default=DIAS_BONUS_DEFAULT,
    taxa_dia_base=TAXA_DIA_BASE,
    valor_minimo_lote_ativo=VALOR_MINIMO_LOTE_ATIVO,
)
set_excel_loader_runtime(
    resolver_arquivo_excel_local=_resolver_arquivo_excel_local,
    dataframe_cache=DF_ABAS_CACHE,
)

_money_round_half_up = _money_round_half_up_modular
dinheiro_round = dinheiro_round_modular
_taxa_ir = _taxa_ir_modular
obter_aliquota_ir = obter_aliquota_ir_modular
_taxa_iof = _taxa_iof_modular
_fator_liquido = _fator_liquido_modular

Produto = Produto_modular
ComboProduto = ComboProduto_modular
Lote = Lote_modular
criar_lote_de_aporte = criar_lote_de_aporte_modular
atualizar_saldo_lotes_no_dia = atualizar_saldo_lotes_no_dia_modular
executar_saque_lote = executar_saque_lote_modular
montar_log_movimento_lote = montar_log_movimento_lote_modular
calcular_saldo_atual_lotes = calcular_saldo_atual_lotes_modular
serializar_lote_remanescente = serializar_lote_remanescente_modular

ler_aba_excel = ler_aba_excel_modular
_normalizar_token_coluna = _normalizar_token_coluna_modular
_normalizar_nome_coluna = _normalizar_nome_coluna_modular
nome_aba = nome_aba_modular
aliases_coluna = aliases_coluna_modular
resolver_coluna = resolver_coluna_modular


# =========================================================
# 13.2 REBIND MODULAR FASE 2–3 (CARTEIRA + INVENTÁRIO/GASTOS)
# =========================================================
from src.ingest.carteira_loader import (
    set_carteira_loader_runtime,
    _resolver_colunas_carteira as _resolver_colunas_carteira_modular,
    _parse_bool_planilha as _parse_bool_planilha_modular,
    _parse_prazo_dias as _parse_prazo_dias_modular,
    _criar_produto_simples as _criar_produto_simples_modular,
    _resolver_combo_por_nome as _resolver_combo_por_nome_modular,
    _carregar_produtos_da_carteira as _carregar_produtos_da_carteira_modular,
    _carregar_combos_da_carteira as _carregar_combos_da_carteira_modular,
    carregar_carteira as carregar_carteira_modular,
)

def _obter_data_referencia_efetiva_runtime_safe():
    try:
        from src.orchestration.bootstrap import obter_data_referencia_efetiva_runtime as _fn
        return _fn()
    except Exception:
        try:
            return globals().get('DATA_REFERENCIA', data_hoje_referencia())
        except Exception:
            return globals().get('DATA_REFERENCIA', None)

from src.ingest.inventory_loader import (
    set_inventory_loader_runtime,
    _classificar_investimento_inventario as _classificar_investimento_inventario_modular,
    _resolver_produto_por_nome as _resolver_produto_por_nome_modular,
    _ler_inventario_lotes as _ler_inventario_lotes_modular,
    _parse_pago_planilha as _parse_pago_planilha_modular,
    _ler_gastos_passados_futuros as _ler_gastos_passados_futuros_modular,
    _serie_texto_normalizada as _serie_texto_normalizada_modular,
    _avaliar_coluna_candidata as _avaliar_coluna_candidata_modular,
    _escolher_melhor_coluna as _escolher_melhor_coluna_modular,
    _normalizar_nome_texto as _normalizar_nome_texto_modular,
    normalizar_nome as normalizar_nome_modular,
    selecionar_coluna_id_lote as selecionar_coluna_id_lote_modular,
    selecionar_coluna_produto_lote as selecionar_coluna_produto_lote_modular,
    _calcular_data_referencia_snapshot as _calcular_data_referencia_snapshot_modular,
    _montar_lotes_pendentes as _montar_lotes_pendentes_modular,
    carregar_inventario_e_gastos as carregar_inventario_e_gastos_modular,
)

set_carteira_loader_runtime(
    aba_carteira=ABA_CARTEIRA,
    debug_schema_abas=DEBUG_SCHEMA_ABAS,
    excluir_produtos_regex=EXCLUIR_PRODUTOS_REGEX,
    log_debug_fn=_log_debug,
)
set_inventory_loader_runtime(
    aba_inventario=ABA_INVENTARIO,
    aba_gastos=ABA_GASTOS,
    debug_schema_abas=DEBUG_SCHEMA_ABAS,
    auditoria_coluna_escolhida=AUDITORIA_COLUNA_ESCOLHIDA,
    pol_col_lote_id_tokens_conjuntos=POL_COL_LOTE_ID_TOKENS_CONJUNTOS,
    pol_col_lote_id_tokens_fortes=POL_COL_LOTE_ID_TOKENS_FORTES,
    pol_col_produto_tokens_busca=POL_COL_PRODUTO_TOKENS_BUSCA,
    pol_col_peso_preenchimento_id_lote=POL_COL_PESO_PREENCHIMENTO_ID_LOTE,
    pol_col_bonus_unicidade_id_lote=POL_COL_BONUS_UNICIDADE_ID_LOTE,
    pol_col_peso_preenchimento_produto=POL_COL_PESO_PREENCHIMENTO_PRODUTO,
    pol_col_peso_match_investimento_produto=POL_COL_PESO_MATCH_INVESTIMENTO_PRODUTO,
    pol_col_cardinalidade_minima_lote_id=POL_COL_CARDINALIDADE_MINIMA_LOTE_ID,
    pol_col_exigir_unicidade_lote_id=POL_COL_EXIGIR_UNICIDADE_LOTE_ID,
    contrato_operacional=CONTRATO_OPERACIONAL,
    log_debug_fn=_log_debug,
    simular_passado_fn=simular_passado,
    data_referencia_efetiva_fn=_obter_data_referencia_efetiva_runtime_safe,
)

_resolver_colunas_carteira = _resolver_colunas_carteira_modular
_parse_bool_planilha = _parse_bool_planilha_modular
_parse_prazo_dias = _parse_prazo_dias_modular
_criar_produto_simples = _criar_produto_simples_modular
_resolver_combo_por_nome = _resolver_combo_por_nome_modular
_carregar_produtos_da_carteira = _carregar_produtos_da_carteira_modular
_carregar_combos_da_carteira = _carregar_combos_da_carteira_modular
carregar_carteira = carregar_carteira_modular

_classificar_investimento_inventario = _classificar_investimento_inventario_modular
_resolver_produto_por_nome = _resolver_produto_por_nome_modular
_ler_inventario_lotes = _ler_inventario_lotes_modular
_parse_pago_planilha = _parse_pago_planilha_modular
_ler_gastos_passados_futuros = _ler_gastos_passados_futuros_modular
_serie_texto_normalizada = _serie_texto_normalizada_modular
_avaliar_coluna_candidata = _avaliar_coluna_candidata_modular
_escolher_melhor_coluna = _escolher_melhor_coluna_modular
_normalizar_nome_texto = _normalizar_nome_texto_modular
normalizar_nome = normalizar_nome_modular
selecionar_coluna_id_lote = selecionar_coluna_id_lote_modular
selecionar_coluna_produto_lote = selecionar_coluna_produto_lote_modular
_calcular_data_referencia_snapshot = _calcular_data_referencia_snapshot_modular
_montar_lotes_pendentes = _montar_lotes_pendentes_modular
carregar_inventario_e_gastos = carregar_inventario_e_gastos_modular


# =========================================================
# 13.3 REBIND MODULAR FASE 4 (REPLAY: SNAPSHOT + CURRENT REPORT)
# =========================================================
from src.replay.snapshot_engine import (
    set_snapshot_runtime,
    simular_passado as simular_passado_modular,
    _safe_len as _safe_len_modular,
    _safe_float as _safe_float_modular,
    _sum_registros_valor as _sum_registros_valor_modular,
    _sample_head_tail as _sample_head_tail_modular,
    _inferir_data_snapshot_passado as _inferir_data_snapshot_passado_modular,
    _extrair_saldos_minimos_de_estado as _extrair_saldos_minimos_de_estado_modular,
    capturar_snapshot_financeiro_minimo as capturar_snapshot_financeiro_minimo_modular,
    capturar_snapshot_financeiro_final as capturar_snapshot_financeiro_final_modular,
)
from src.replay.current_report import (
    set_current_report_runtime,
    get_taxas_lote as get_taxas_lote_modular,
    acumular_saques_por_lote as acumular_saques_por_lote_modular,
    obter_data_referencia_relatorio_local as obter_data_referencia_relatorio_local_modular,
    obter_data_referencia_relatorio as obter_data_referencia_relatorio_modular,
    obter_data_fiscal_liquido_relatorio as obter_data_fiscal_liquido_relatorio_modular,
    calcular_liquido_atual_relatorio as calcular_liquido_atual_relatorio_modular,
    listar_datas_economicas_relatorio as listar_datas_economicas_relatorio_modular,
    _coagir_para_date as _coagir_para_date_modular,
    reconstruir_lote_para_relatorio as reconstruir_lote_para_relatorio_modular,
    atualizar_lote_reconstruido_ate_data as atualizar_lote_reconstruido_ate_data_modular,
    gerar_relatorio_situacao_atual as gerar_relatorio_situacao_atual_modular,
)

set_snapshot_runtime(
    debug_downloads=DEBUG_DOWNLOADS,
    log_debug_fn=_log_debug,
    carregar_parametros_hibrido_5p_passado_fn=carregar_parametros_hibrido_5p_passado,
    resolver_hibrido_5p_fn=resolver_hibrido_5p,
    diagnosticar_resolvedor_hibrido_5p_fn=diagnosticar_resolvedor_hibrido_5p,
    lote_nao_investivel_mesmo_dia_fn=_lote_nao_investivel_mesmo_dia,
)
set_current_report_runtime(
    data_referencia=DATA_REFERENCIA,
    investimentos_norm=INVESTIMENTOS_NORM,
    produto_fallback_nome=PRODUTO_FALLBACK_NOME,
)
set_inventory_loader_runtime(simular_passado_fn=simular_passado_modular, data_referencia_efetiva_fn=_obter_data_referencia_efetiva_runtime_safe)

simular_passado = simular_passado_modular
_safe_len = _safe_len_modular
_safe_float = _safe_float_modular
_sum_registros_valor = _sum_registros_valor_modular
_sample_head_tail = _sample_head_tail_modular
_inferir_data_snapshot_passado = _inferir_data_snapshot_passado_modular
_extrair_saldos_minimos_de_estado = _extrair_saldos_minimos_de_estado_modular
capturar_snapshot_financeiro_minimo = capturar_snapshot_financeiro_minimo_modular
capturar_snapshot_financeiro_final = capturar_snapshot_financeiro_final_modular

get_taxas_lote = get_taxas_lote_modular
acumular_saques_por_lote = acumular_saques_por_lote_modular
obter_data_referencia_relatorio_local = obter_data_referencia_relatorio_local_modular
obter_data_referencia_relatorio = obter_data_referencia_relatorio_modular
obter_data_fiscal_liquido_relatorio = obter_data_fiscal_liquido_relatorio_modular
calcular_liquido_atual_relatorio = calcular_liquido_atual_relatorio_modular
listar_datas_economicas_relatorio = listar_datas_economicas_relatorio_modular
_coagir_para_date = _coagir_para_date_modular
reconstruir_lote_para_relatorio = reconstruir_lote_para_relatorio_modular
atualizar_lote_reconstruido_ate_data = atualizar_lote_reconstruido_ate_data_modular
gerar_relatorio_situacao_atual = gerar_relatorio_situacao_atual_modular



# =========================================================
# 13.4 REBIND MODULAR FASE 5 (PAYMENTS: ALLOCATION + OPTIMIZER)
# =========================================================
from src.payments.allocation_engine import (
    set_allocation_runtime,
    _normalizar_plano as _normalizar_plano_modular,
    simular_valor_final_produto as simular_valor_final_produto_modular,
    get_score_economico as get_score_economico_modular,
    get_score_economico_vpl as get_score_economico_vpl_modular,
    simular_pagamentos_com_produto as simular_pagamentos_com_produto_modular,
    gerar_top_planos_alocacao as gerar_top_planos_alocacao_modular,
    _fator_oportunidade_lote as _fator_oportunidade_lote_modular,
    alocar_lote_por_otimizacao as alocar_lote_por_otimizacao_modular,
)
from src.payments.payment_optimizer import (
    set_payment_optimizer_runtime,
    resolver_pulp_penalidade_5p as resolver_pulp_penalidade_5p_modular,
    resolver_pulp_hibrido_5p as resolver_pulp_hibrido_5p_modular,
    resolver_hibrido_5p as resolver_hibrido_5p_modular,
    _ordenar_lotes_para_pagamento as _ordenar_lotes_para_pagamento_modular,
    processar_contas_do_dia as processar_contas_do_dia_modular,
    rodar_estrategia as rodar_estrategia_modular,
    _registrar_movimento_pagamento as _registrar_movimento_pagamento_modular,
    _sacar_de_lote as _sacar_de_lote_modular,
    _executar_plano_externo_rigido_conta as _executar_plano_externo_rigido_conta_modular,
    _executar_plano_externo_baseline_conta as _executar_plano_externo_baseline_conta_modular,
    _executar_fallback_hibrido_conta as _executar_fallback_hibrido_conta_modular,
    _executar_fallback_heuristico_conta as _executar_fallback_heuristico_conta_modular,
)

set_allocation_runtime(
    taxa_dia_base=TAXA_DIA_BASE,
    horizonte_extra_dias=HORIZONTE_EXTRA_DIAS,
    permitir_split_lote=PERMITIR_SPLIT_LOTE,
    top_n_alocacao=TOP_N_ALOCACAO,
    ir_faixas=IR_FAIXAS,
    produto_padrao=globals().get('PRODUTO_PADRAO', None),
    produtos_globais_simulacao=globals().get('PRODUTOS_GLOBAIS_SIMULACAO', []),
    bcb_map_global_runtime=globals().get('bcb_map_global', {}) or {},
)
set_payment_optimizer_runtime(
    data_referencia=DATA_REFERENCIA,
    dias_cliff_ir=DIAS_CLIFF_IR,
    horizonte_projecao_dias=HORIZONTE_PROJECAO_DIAS,
    taxa_dia_base=TAXA_DIA_BASE,
    tolerancia_monetaria=TOLERANCIA_MONETARIA,
    valor_minimo_lote_ativo=VALOR_MINIMO_LOTE_ATIVO,
    valor_minimo_resgate_bruto=VALOR_MINIMO_RESGATE_BRUTO,
    iof_table=IOF_TABLE,
    params_hibrido=PARAMS_HIBRIDO,
    plano_pagamentos_externo=PLANO_PAGAMENTOS_EXTERNO,
    modo_execucao_futuro=MODO_EXECUCAO_FUTURO,
    exibir_alertas_falta_caixa=EXIBIR_ALERTAS_FALTA_CAIXA,
    registrar_auditoria_plano_fn=_registrar_auditoria_plano,
)
set_snapshot_runtime(resolver_hibrido_5p_fn=resolver_hibrido_5p_modular)

_normalizar_plano = _normalizar_plano_modular
simular_valor_final_produto = simular_valor_final_produto_modular
get_score_economico = get_score_economico_modular
get_score_economico_vpl = get_score_economico_vpl_modular
simular_pagamentos_com_produto = simular_pagamentos_com_produto_modular
gerar_top_planos_alocacao = gerar_top_planos_alocacao_modular
_fator_oportunidade_lote = _fator_oportunidade_lote_modular
alocar_lote_por_otimizacao = alocar_lote_por_otimizacao_modular

resolver_pulp_penalidade_5p = resolver_pulp_penalidade_5p_modular
resolver_pulp_hibrido_5p = resolver_pulp_hibrido_5p_modular
resolver_hibrido_5p = resolver_hibrido_5p_modular
_ordenar_lotes_para_pagamento = _ordenar_lotes_para_pagamento_modular
processar_contas_do_dia = processar_contas_do_dia_modular
rodar_estrategia = rodar_estrategia_modular
_registrar_movimento_pagamento = _registrar_movimento_pagamento_modular
_sacar_de_lote = _sacar_de_lote_modular
_executar_plano_externo_rigido_conta = _executar_plano_externo_rigido_conta_modular
_executar_plano_externo_baseline_conta = _executar_plano_externo_baseline_conta_modular
_executar_fallback_hibrido_conta = _executar_fallback_hibrido_conta_modular
_executar_fallback_heuristico_conta = _executar_fallback_heuristico_conta_modular



# =========================================================
# 13.5 REBIND MODULAR FASE 6 (SWITCHING: ENGINE + PLANNER)
# =========================================================
from src.switching.switch_engine import (
    set_switch_engine_runtime,
    _datas_candidatas_switch as _datas_candidatas_switch_modular,
    _estado_lote_ate_switch as _estado_lote_ate_switch_modular,
    avaliar_switch_lote as avaliar_switch_lote_modular,
    gerar_diagnostico_switches_portfolio as gerar_diagnostico_switches_portfolio_modular,
)
from src.switching.switch_planner import (
    set_switch_planner_runtime,
    _taxa_eff as _taxa_eff_modular,
    _switch_detalhe_dict as _switch_detalhe_dict_modular,
    _append_switch_detalhes as _append_switch_detalhes_modular,
    _criar_lotes_alocacao_switch as _criar_lotes_alocacao_switch_modular,
    _scale_plano_switch as _scale_plano_switch_modular,
    _avaliar_switching_e_diagnosticos as _avaliar_switching_e_diagnosticos_modular,
    _resolver_plano_switch_individual as _resolver_plano_switch_individual_modular,
    _executar_switch_individual as _executar_switch_individual_modular,
)

set_switch_engine_runtime(
    switch_busca_dias=SWITCH_BUSCA_DIAS,
    permitir_switch_antes_30_dias=PERMITIR_SWITCH_ANTES_30_DIAS,
    taxa_dia_base=TAXA_DIA_BASE,
    switching_limiar_ganho=SWITCHING_LIMIAR_GANHO,
    switch_min_hold_dias=globals().get('SWITCH_MIN_HOLD_DIAS', 0),
    switch_min_upgrade_rel=globals().get('SWITCH_MIN_UPGRADE_REL', 0.0),
)
set_switch_planner_runtime(
    produto_padrao=globals().get('PRODUTO_PADRAO', None),
    debug_switch_execucao=DEBUG_SWITCH_EXECUCAO,
    modo_execucao_futuro=MODO_EXECUCAO_FUTURO,
    debug_ativo_fn=_debug_ativo,
    log_debug_fn=_log_debug,
    df_or_empty_fn=_df_or_empty,
    imprimir_resumo_consolidado_switches_fn=_imprimir_resumo_consolidado_switches,
    reotimizar_pool_switch_no_futuro=REOTIMIZAR_POOL_SWITCH_NO_FUTURO,
    permitir_switch_antes_30_dias=PERMITIR_SWITCH_ANTES_30_DIAS,
)

_datas_candidatas_switch = _datas_candidatas_switch_modular
_estado_lote_ate_switch = _estado_lote_ate_switch_modular
avaliar_switch_lote = avaliar_switch_lote_modular
gerar_diagnostico_switches_portfolio = gerar_diagnostico_switches_portfolio_modular

_taxa_eff = _taxa_eff_modular
_switch_detalhe_dict = _switch_detalhe_dict_modular
_append_switch_detalhes = _append_switch_detalhes_modular
_criar_lotes_alocacao_switch = _criar_lotes_alocacao_switch_modular
_scale_plano_switch = _scale_plano_switch_modular
_avaliar_switching_e_diagnosticos = _avaliar_switching_e_diagnosticos_modular
_resolver_plano_switch_individual = _resolver_plano_switch_individual_modular
_executar_switch_individual = _executar_switch_individual_modular

# =========================================================
# 13.6 REBIND MODULAR FASE 7 (FUTURE: SIMULATOR)
# =========================================================
from src.future.future_simulator import (
    set_future_runtime,
    _processar_conta_futura as _processar_conta_futura_modular,
    _processar_juros_do_dia as _processar_juros_do_dia_modular,
    _calcular_metricas_futuro as _calcular_metricas_futuro_modular,
    simular_futuro as simular_futuro_modular,
)

set_future_runtime(
    taxa_dia_base=TAXA_DIA_BASE,
    exibir_alertas_falta_caixa=EXIBIR_ALERTAS_FALTA_CAIXA,
)

_processar_conta_futura = _processar_conta_futura_modular
_processar_juros_do_dia = _processar_juros_do_dia_modular
_calcular_metricas_futuro = _calcular_metricas_futuro_modular
simular_futuro = simular_futuro_modular


# =========================================================
# 13.7 REBIND MODULAR FASE 8 (COMPETITIVE: TRAINING + WALKFORWARD)
# =========================================================
from src.competitive.training import (
    set_training_runtime,
    _listar_candidatos_parametros as _listar_candidatos_parametros_modular,
    _eh_dict_params_hibrido as _eh_dict_params_hibrido_modular,
    _extrair_params_hibrido_de_obj as _extrair_params_hibrido_de_obj_modular,
    _carregar_json_parametros as _carregar_json_parametros_modular,
    escolher_perfil_auto as escolher_perfil_auto_modular,
    carregar_parametros_hibrido_5p as carregar_parametros_hibrido_5p_modular,
    carregar_parametros_hibrido_5p_passado as carregar_parametros_hibrido_5p_passado_modular,
)
from src.competitive.walkforward import (
    set_walkforward_runtime,
    validacao_walk_forward as validacao_walk_forward_modular,
)

set_training_runtime(
    treinamento_auto_tempo_alvo_curto_max=(TREINAMENTO_MODO_AUTO_THRESHOLDS or {}).get('tempo_alvo_curto_max', 8),
    treinamento_auto_tempo_alvo_longo_min=(TREINAMENTO_MODO_AUTO_THRESHOLDS or {}).get('tempo_alvo_longo_min', 25),
    treinamento_auto_carga_media_min=(TREINAMENTO_MODO_AUTO_THRESHOLDS or {}).get('carga_media_min', 60.0),
    treinamento_auto_carga_alta_min=(TREINAMENTO_MODO_AUTO_THRESHOLDS or {}).get('carga_alta_min', 120.0),
    treinamento_auto_carga_baixa_max=(TREINAMENTO_MODO_AUTO_THRESHOLDS or {}).get('carga_baixa_max', 45.0),
    param_5p_fixo=PARAM_5P_FIXO,
    fallback_param_url_5p=FALLBACK_PARAM_URL_5P,
    google_cfg=GOOGLE_CFG,
    bootstrap_parametros_5p_default_nome=globals().get('BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME', 'melhores_parametros_5p.json'),
    baixar_arquivo_drive_fn=baixar_arquivo_drive,
    normalizar_nome_arquivo_json_fn=_normalizar_nome_arquivo_json,
)
set_walkforward_runtime(
    avaliacao_wf_pct_treino=AVALIACAO_WF_PCT_TREINO,
    valor_minimo_lote_ativo=VALOR_MINIMO_LOTE_ATIVO,
    rodar_estrategia_fn=rodar_estrategia,
)

_listar_candidatos_parametros = _listar_candidatos_parametros_modular
_eh_dict_params_hibrido = _eh_dict_params_hibrido_modular
_extrair_params_hibrido_de_obj = _extrair_params_hibrido_de_obj_modular
_carregar_json_parametros = _carregar_json_parametros_modular
escolher_perfil_auto = escolher_perfil_auto_modular
carregar_parametros_hibrido_5p = carregar_parametros_hibrido_5p_modular
carregar_parametros_hibrido_5p_passado = carregar_parametros_hibrido_5p_passado_modular
validacao_walk_forward = validacao_walk_forward_modular

# =========================================================
# 13.8 REBIND MODULAR FASE 9 (ORCHESTRATION: UNIFIED PIPELINE)
# =========================================================
from src.domain.market_calendar import (
    set_market_calendar_runtime,
    _calcular_pascoa as _calcular_pascoa_modular,
    gerar_dias_sem_rendimento_bancario as gerar_dias_sem_rendimento_bancario_modular,
    is_dia_rendimento as is_dia_rendimento_modular,
    contar_dias_rendimento as contar_dias_rendimento_modular,
    extrair_lote_usado_unico as extrair_lote_usado_unico_modular,
    _normalizar_lote_id as _normalizar_lote_id_modular,
    _normalizar_data_lote as _normalizar_data_lote_modular,
    _normalizar_valor_lote as _normalizar_valor_lote_modular,
    extrair_metadata_serie_cdi as extrair_metadata_serie_cdi_modular,
    atualizar_metadata_cdi as atualizar_metadata_cdi_modular,
    obter_data_corte_cdi as obter_data_corte_cdi_modular,
    construir_cdi_fixo_ate_data as construir_cdi_fixo_ate_data_modular,
    logar_metadata_cdi as logar_metadata_cdi_modular,
    obter_historico_bcb as obter_historico_bcb_modular,
    baixar_fallback_bcb as baixar_fallback_bcb_modular,
)
from src.shared.execution_policy import (
    set_execution_policy_runtime,
    _fim_janela_alocacao as _fim_janela_alocacao_modular,
    normalizar_modo_execucao_futuro as normalizar_modo_execucao_futuro_modular,
    _normalizar_conta_processamento as _normalizar_conta_processamento_modular,
    ordenar_contas_processamento as ordenar_contas_processamento_modular,
)
from src.replay.lotes_shadow import (
    set_lotes_shadow_runtime,
    _resolver_produto_lote_shadow as _resolver_produto_lote_shadow_modular,
    normalizar_lotes_brutos as normalizar_lotes_brutos_modular,
    construir_indice_lotes as construir_indice_lotes_modular,
    derivar_eventos_aporte_de_lotes as derivar_eventos_aporte_de_lotes_modular,
    comparar_aportes_legado_vs_shadow as comparar_aportes_legado_vs_shadow_modular,
    gerar_lote_tecnico_id as gerar_lote_tecnico_id_modular,
    gerar_switch_grupo_id as gerar_switch_grupo_id_modular,
    projetar_eventos_brutos_de_aportes as projetar_eventos_brutos_de_aportes_modular,
    construir_regra_switch_shadow as construir_regra_switch_shadow_modular,
    derivar_eventos_switch_shadow as derivar_eventos_switch_shadow_modular,
    consolidar_eventos_financeiros_brutos as consolidar_eventos_financeiros_brutos_modular,
    ordenar_eventos_financeiros_brutos_shadow as ordenar_eventos_financeiros_brutos_shadow_modular,
    projetar_estado_lotes_pre_replay_shadow as projetar_estado_lotes_pre_replay_shadow_modular,
    ordenar_lotes_para_replay_shadow as ordenar_lotes_para_replay_shadow_modular,
    aplicar_contas_pagas_shadow as aplicar_contas_pagas_shadow_modular,
    capturar_snapshot_aportes_pipeline as capturar_snapshot_aportes_pipeline_modular,
    comparar_snapshots_aportes_pipeline as comparar_snapshots_aportes_pipeline_modular,
    logar_snapshot_aportes_pipeline as logar_snapshot_aportes_pipeline_modular,
    logar_comparacao_aportes_pipeline as logar_comparacao_aportes_pipeline_modular,
)

from src.orchestration.unified_pipeline import (
    set_orchestration_runtime,
    _selecionar_modo_treinamento_unificado as _selecionar_modo_treinamento_unificado_modular,
    _materializar_artefatos_switching_unificados as _materializar_artefatos_switching_unificados_modular,
    _executar_futuro_unificado as _executar_futuro_unificado_modular,
    _executar_bloco_competitivo_unificado as _executar_bloco_competitivo_unificado_modular,
    _exportar_resultados_unificados as _exportar_resultados_unificados_modular,
)


set_execution_policy_runtime(
    ordem_processamento_sentinela=ORDEM_PROCESSAMENTO_SENTINELA,
)

set_market_calendar_runtime(
    calendario_ano_inicio_dias_sem_rendimento=CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO,
    calendario_ano_fim_dias_sem_rendimento=CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO,
    debug_cdi=DEBUG_CDI,
    fallback_bcb_url=FALLBACK_BCB_URL,
    fallback_bcb_file_id=FALLBACK_BCB_FILE_ID,
    taxa_dia_base=TAXA_DIA_BASE,
    rede_user_agent_download=REDE_USER_AGENT_DOWNLOAD,
    rede_user_agent_bcb=REDE_USER_AGENT_BCB,
    rede_accept_bcb=REDE_ACCEPT_BCB,
    rede_timeout_download_segundos=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS,
    rede_timeout_bcb_segundos=REDE_TIMEOUT_BCB_SEGUNDOS,
    rede_verificar_ssl=REDE_VERIFICAR_SSL,
    arquivo_temporario_fallback_bcb=ARQUIVO_TEMPORARIO_FALLBACK_BCB,
    data_referencia=DATA_REFERENCIA,
    cache_bcb_file=CACHE_BCB_FILE,
    historico_bcb_data_minima=HISTORICO_BCB_DATA_MINIMA,
    bcb_serie_12_url=BCB_SERIE_12_URL,
    cal_instance=cal,
    coagir_para_date_fn=_coagir_para_date,
)

set_lotes_shadow_runtime(
    investimentos_norm=INVESTIMENTOS_NORM,
    mapa_produtos_canonico=MAPA_PRODUTOS_CANONICO,
    selecionar_coluna_id_lote_fn=selecionar_coluna_id_lote,
    selecionar_coluna_produto_lote_fn=selecionar_coluna_produto_lote,
    resolver_coluna_fn=resolver_coluna,
    safe_float_fn=_safe_float,
    normalizar_nome_fn=normalizar_nome,
)

_calcular_pascoa = _calcular_pascoa_modular
gerar_dias_sem_rendimento_bancario = gerar_dias_sem_rendimento_bancario_modular
is_dia_rendimento = is_dia_rendimento_modular
contar_dias_rendimento = contar_dias_rendimento_modular
extrair_lote_usado_unico = extrair_lote_usado_unico_modular
_normalizar_lote_id = _normalizar_lote_id_modular
_normalizar_data_lote = _normalizar_data_lote_modular
_normalizar_valor_lote = _normalizar_valor_lote_modular
extrair_metadata_serie_cdi = extrair_metadata_serie_cdi_modular
atualizar_metadata_cdi = atualizar_metadata_cdi_modular
obter_data_corte_cdi = obter_data_corte_cdi_modular
construir_cdi_fixo_ate_data = construir_cdi_fixo_ate_data_modular
logar_metadata_cdi = logar_metadata_cdi_modular
obter_historico_bcb = obter_historico_bcb_modular
baixar_fallback_bcb = baixar_fallback_bcb_modular
_fim_janela_alocacao = _fim_janela_alocacao_modular
normalizar_modo_execucao_futuro = normalizar_modo_execucao_futuro_modular
_normalizar_conta_processamento = _normalizar_conta_processamento_modular
ordenar_contas_processamento = ordenar_contas_processamento_modular

_resolver_produto_lote_shadow = _resolver_produto_lote_shadow_modular
normalizar_lotes_brutos = normalizar_lotes_brutos_modular
construir_indice_lotes = construir_indice_lotes_modular
derivar_eventos_aporte_de_lotes = derivar_eventos_aporte_de_lotes_modular
comparar_aportes_legado_vs_shadow = comparar_aportes_legado_vs_shadow_modular
gerar_lote_tecnico_id = gerar_lote_tecnico_id_modular
gerar_switch_grupo_id = gerar_switch_grupo_id_modular
projetar_eventos_brutos_de_aportes = projetar_eventos_brutos_de_aportes_modular
construir_regra_switch_shadow = construir_regra_switch_shadow_modular
derivar_eventos_switch_shadow = derivar_eventos_switch_shadow_modular
consolidar_eventos_financeiros_brutos = consolidar_eventos_financeiros_brutos_modular
ordenar_eventos_financeiros_brutos_shadow = ordenar_eventos_financeiros_brutos_shadow_modular
projetar_estado_lotes_pre_replay_shadow = projetar_estado_lotes_pre_replay_shadow_modular
ordenar_lotes_para_replay_shadow = ordenar_lotes_para_replay_shadow_modular
aplicar_contas_pagas_shadow = aplicar_contas_pagas_shadow_modular
capturar_snapshot_aportes_pipeline = capturar_snapshot_aportes_pipeline_modular
comparar_snapshots_aportes_pipeline = comparar_snapshots_aportes_pipeline_modular
logar_snapshot_aportes_pipeline = logar_snapshot_aportes_pipeline_modular
logar_comparacao_aportes_pipeline = logar_comparacao_aportes_pipeline_modular

set_orchestration_runtime(
    modo_treinamento_padrao=globals().get('MODO_TREINAMENTO_PADRAO', '1'),
    perfil_treino_padrao=globals().get('PERFIL_TREINO_PADRAO', 'balanceado'),
    perfil_treino_auto_opcao=globals().get('PERFIL_TREINO_AUTO_OPCAO', 'b'),
    avaliacao_wf_splits_default=globals().get('AVALIACAO_WF_SPLITS_DEFAULT', 4),
    taxa_dia_base=globals().get('TAXA_DIA_BASE', 0.0),
    taxa_proj=globals().get('TAXA_PROJ', globals().get('TAXA_DIA_BASE', 0.0)),
    treinamento_perfis=globals().get('TREINAMENTO_PERFIS', {}),
    debug_switch_execucao=globals().get('DEBUG_SWITCH_EXECUCAO', False),
    avaliacao_ranking_peso_saldo=globals().get('AVALIACAO_RANKING_PESO_SALDO', 1.0),
    avaliacao_ranking_peso_robustez=globals().get('AVALIACAO_RANKING_PESO_ROBUSTEZ', 0.0),
    avaliacao_wf_pct_treino=globals().get('AVALIACAO_WF_PCT_TREINO', 0.7),
    avaliacao_wf_robustez_default=globals().get('AVALIACAO_WF_ROBUSTEZ_DEFAULT', 0.0),
    exportar_debug=globals().get('EXPORTAR_DEBUG', False),
    produtos_globais_simulacao=globals().get('PRODUTOS_GLOBAIS_SIMULACAO', []) or [],
    modo_execucao_futuro=globals().get('MODO_EXECUCAO_FUTURO', 'padrao'),
    safe_input_fn=_safe_input,
    carregar_parametros_hibrido_5p_fn=carregar_parametros_hibrido_5p,
    debug_ativo_fn=_debug_ativo,
    auditar_base_competitiva_fn=_auditar_base_competitiva,
    snapshot_direto_lotes_ranking_fn=_snapshot_direto_lotes_ranking,
    gerar_relatorio_melhor_estrategia_por_lotes_finais_fn=gerar_relatorio_melhor_estrategia_por_lotes_finais,
    df_or_empty_fn=_df_or_empty,
    escrever_resultados_excel_fn=_escrever_resultados_excel,
    escrever_se_nao_vazio_fn=_escrever_se_nao_vazio,
    montar_df_diagnostico_modo_execucao_fn=_montar_df_diagnostico_modo_execucao,
)

_selecionar_modo_treinamento_unificado = _selecionar_modo_treinamento_unificado_modular
_materializar_artefatos_switching_unificados = _materializar_artefatos_switching_unificados_modular
_executar_futuro_unificado = _executar_futuro_unificado_modular
_executar_bloco_competitivo_unificado = _executar_bloco_competitivo_unificado_modular
_exportar_resultados_unificados = _exportar_resultados_unificados_modular

# =========================================================
# 13.9 REBIND MODULAR FASE 10.1 (MARKET CALENDAR + EXECUTION POLICY)
# =========================================================
from src.domain.market_calendar import (
    set_market_calendar_runtime,
    _calcular_pascoa as _calcular_pascoa_modular,
    gerar_dias_sem_rendimento_bancario as gerar_dias_sem_rendimento_bancario_modular,
    is_dia_rendimento as is_dia_rendimento_modular,
    contar_dias_rendimento as contar_dias_rendimento_modular,
    extrair_lote_usado_unico as extrair_lote_usado_unico_modular,
    _normalizar_lote_id as _normalizar_lote_id_modular,
    _normalizar_data_lote as _normalizar_data_lote_modular,
    _normalizar_valor_lote as _normalizar_valor_lote_modular,
    extrair_metadata_serie_cdi as extrair_metadata_serie_cdi_modular,
    atualizar_metadata_cdi as atualizar_metadata_cdi_modular,
    obter_data_corte_cdi as obter_data_corte_cdi_modular,
    construir_cdi_fixo_ate_data as construir_cdi_fixo_ate_data_modular,
    logar_metadata_cdi as logar_metadata_cdi_modular,
    obter_historico_bcb as obter_historico_bcb_modular,
    baixar_fallback_bcb as baixar_fallback_bcb_modular,
)
from src.shared.execution_policy import (
    set_execution_policy_runtime,
    _fim_janela_alocacao as _fim_janela_alocacao_modular,
    normalizar_modo_execucao_futuro as normalizar_modo_execucao_futuro_modular,
    _normalizar_conta_processamento as _normalizar_conta_processamento_modular,
    ordenar_contas_processamento as ordenar_contas_processamento_modular,
)

set_execution_policy_runtime(
    ordem_processamento_sentinela=ORDEM_PROCESSAMENTO_SENTINELA,
)
set_market_calendar_runtime(
    calendario_ano_inicio_dias_sem_rendimento=CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO,
    calendario_ano_fim_dias_sem_rendimento=CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO,
    debug_cdi=DEBUG_CDI,
    fallback_bcb_url=FALLBACK_BCB_URL,
    fallback_bcb_file_id=FALLBACK_BCB_FILE_ID,
    taxa_dia_base=TAXA_DIA_BASE,
    rede_user_agent_download=REDE_USER_AGENT_DOWNLOAD,
    rede_user_agent_bcb=REDE_USER_AGENT_BCB,
    rede_accept_bcb=REDE_ACCEPT_BCB,
    rede_timeout_download_segundos=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS,
    rede_timeout_bcb_segundos=REDE_TIMEOUT_BCB_SEGUNDOS,
    rede_verificar_ssl=REDE_VERIFICAR_SSL,
    arquivo_temporario_fallback_bcb=ARQUIVO_TEMPORARIO_FALLBACK_BCB,
    data_referencia=DATA_REFERENCIA,
    cache_bcb_file=CACHE_BCB_FILE,
    historico_bcb_data_minima=HISTORICO_BCB_DATA_MINIMA,
    bcb_serie_12_url=BCB_SERIE_12_URL,
    cal_instance=cal,
    coagir_para_date_fn=_coagir_para_date,
)

_calcular_pascoa = _calcular_pascoa_modular
gerar_dias_sem_rendimento_bancario = gerar_dias_sem_rendimento_bancario_modular
DIAS_SEM_RENDIMENTO_BANCARIO = gerar_dias_sem_rendimento_bancario()
is_dia_rendimento = is_dia_rendimento_modular
contar_dias_rendimento = contar_dias_rendimento_modular
extrair_lote_usado_unico = extrair_lote_usado_unico_modular
_normalizar_lote_id = _normalizar_lote_id_modular
_normalizar_data_lote = _normalizar_data_lote_modular
_normalizar_valor_lote = _normalizar_valor_lote_modular
extrair_metadata_serie_cdi = extrair_metadata_serie_cdi_modular
atualizar_metadata_cdi = atualizar_metadata_cdi_modular
obter_data_corte_cdi = obter_data_corte_cdi_modular
construir_cdi_fixo_ate_data = construir_cdi_fixo_ate_data_modular
logar_metadata_cdi = logar_metadata_cdi_modular
obter_historico_bcb = obter_historico_bcb_modular
baixar_fallback_bcb = baixar_fallback_bcb_modular

_fim_janela_alocacao = _fim_janela_alocacao_modular
normalizar_modo_execucao_futuro = normalizar_modo_execucao_futuro_modular
_normalizar_conta_processamento = _normalizar_conta_processamento_modular
ordenar_contas_processamento = ordenar_contas_processamento_modular

# =========================================================
# 13.10 REBIND MODULAR FASE 10.2 (REPLAY: LOTES SHADOW)
# =========================================================
from src.replay.lotes_shadow import (
    set_lotes_shadow_runtime,
    _resolver_produto_lote_shadow as _resolver_produto_lote_shadow_modular,
    normalizar_lotes_brutos as normalizar_lotes_brutos_modular,
    construir_indice_lotes as construir_indice_lotes_modular,
    derivar_eventos_aporte_de_lotes as derivar_eventos_aporte_de_lotes_modular,
    comparar_aportes_legado_vs_shadow as comparar_aportes_legado_vs_shadow_modular,
    gerar_lote_tecnico_id as gerar_lote_tecnico_id_modular,
    gerar_switch_grupo_id as gerar_switch_grupo_id_modular,
    projetar_eventos_brutos_de_aportes as projetar_eventos_brutos_de_aportes_modular,
    construir_regra_switch_shadow as construir_regra_switch_shadow_modular,
    derivar_eventos_switch_shadow as derivar_eventos_switch_shadow_modular,
    consolidar_eventos_financeiros_brutos as consolidar_eventos_financeiros_brutos_modular,
    ordenar_eventos_financeiros_brutos_shadow as ordenar_eventos_financeiros_brutos_shadow_modular,
    projetar_estado_lotes_pre_replay_shadow as projetar_estado_lotes_pre_replay_shadow_modular,
    ordenar_lotes_para_replay_shadow as ordenar_lotes_para_replay_shadow_modular,
    aplicar_contas_pagas_shadow as aplicar_contas_pagas_shadow_modular,
)

set_lotes_shadow_runtime(
    mapa_produtos_canonico=MAPA_PRODUTOS_CANONICO,
    investimentos_norm=INVESTIMENTOS_NORM,
    selecionar_coluna_id_lote_fn=selecionar_coluna_id_lote,
    selecionar_coluna_produto_lote_fn=selecionar_coluna_produto_lote,
    resolver_coluna_fn=resolver_coluna,
    safe_float_fn=_safe_float,
)

_resolver_produto_lote_shadow = _resolver_produto_lote_shadow_modular
normalizar_lotes_brutos = normalizar_lotes_brutos_modular
construir_indice_lotes = construir_indice_lotes_modular
derivar_eventos_aporte_de_lotes = derivar_eventos_aporte_de_lotes_modular
comparar_aportes_legado_vs_shadow = comparar_aportes_legado_vs_shadow_modular
gerar_lote_tecnico_id = gerar_lote_tecnico_id_modular
gerar_switch_grupo_id = gerar_switch_grupo_id_modular
projetar_eventos_brutos_de_aportes = projetar_eventos_brutos_de_aportes_modular
construir_regra_switch_shadow = construir_regra_switch_shadow_modular
derivar_eventos_switch_shadow = derivar_eventos_switch_shadow_modular
consolidar_eventos_financeiros_brutos = consolidar_eventos_financeiros_brutos_modular
ordenar_eventos_financeiros_brutos_shadow = ordenar_eventos_financeiros_brutos_shadow_modular
projetar_estado_lotes_pre_replay_shadow = projetar_estado_lotes_pre_replay_shadow_modular
ordenar_lotes_para_replay_shadow = ordenar_lotes_para_replay_shadow_modular
aplicar_contas_pagas_shadow = aplicar_contas_pagas_shadow_modular


# =========================================================
# 13.11 REBIND MODULAR FASE 10.3 (IO: EXTERNAL PLAN + ORCHESTRATION: BOOTSTRAP)
# =========================================================
from src.io.external_plan_loader import (
    set_external_plan_loader_runtime,
    _normalizar_data_plano_externo as _normalizar_data_plano_externo_modular,
    _carregar_plano_externo_dataframe as _carregar_plano_externo_dataframe_modular,
    _listar_diretorios_busca_resultados as _listar_diretorios_busca_resultados_modular,
    _listar_candidatos_resultado_otimizador as _listar_candidatos_resultado_otimizador_modular,
    _score_arquivo_resultado_otimizador as _score_arquivo_resultado_otimizador_modular,
    carregar_plano_pagamentos_externo as carregar_plano_pagamentos_externo_modular,
    _ajustar_modo_por_compatibilidade_plano as _ajustar_modo_por_compatibilidade_plano_modular,
    _coletar_referencias_produtos_plano_externo as _coletar_referencias_produtos_plano_externo_modular,
    _diagnosticar_compatibilidade_plano_externo as _diagnosticar_compatibilidade_plano_externo_modular,
)
from src.orchestration.bootstrap import (
    set_bootstrap_runtime,
    _resolver_taxa_proj_unificada as _resolver_taxa_proj_unificada_modular,
    _carregar_e_validar_plano_externo_unificado as _carregar_e_validar_plano_externo_unificado_modular,
    _resolver_contexto_canonico_compartilhado as _resolver_contexto_canonico_compartilhado_modular,
    _inicializar_contexto_execucao as _inicializar_contexto_execucao_modular,
    obter_data_referencia_efetiva_runtime,
)

def _sincronizar_contexto_bootstrap(*, caminho_excel=None, hoje=None, bcb_map=None, produtos=None, produto_padrao=None, produtos_globais_simulacao=None):
    del caminho_excel
    if hoje is not None:
        globals()['DATA_REFERENCIA'] = hoje
    if bcb_map is not None:
        globals()['MAPA_BCB'] = bcb_map
        globals()['bcb_map_global'] = bcb_map
    if produto_padrao is not None:
        globals()['PRODUTO_PADRAO'] = produto_padrao
    if produtos_globais_simulacao is not None:
        globals()['PRODUTOS_GLOBAIS_SIMULACAO'] = list(produtos_globais_simulacao)
    if bcb_map is not None or produto_padrao is not None or produtos_globais_simulacao is not None:
        set_allocation_runtime(
            produto_padrao=globals().get('PRODUTO_PADRAO', None),
            produtos_globais_simulacao=globals().get('PRODUTOS_GLOBAIS_SIMULACAO', []),
            bcb_map_global_runtime=globals().get('MAPA_BCB', {}) or {},
        )
        set_switch_planner_runtime(
            produto_padrao=globals().get('PRODUTO_PADRAO', None),
            modo_execucao_futuro=globals().get('MODO_EXECUCAO_FUTURO', MODO_EXECUCAO_FUTURO),
            reotimizar_pool_switch_no_futuro=REOTIMIZAR_POOL_SWITCH_NO_FUTURO,
            permitir_switch_antes_30_dias=PERMITIR_SWITCH_ANTES_30_DIAS,
        )
        set_orchestration_runtime(
            produtos_globais_simulacao=globals().get('PRODUTOS_GLOBAIS_SIMULACAO', []) or [],
            taxa_proj=globals().get('TAXA_PROJ', globals().get('TAXA_DIA_BASE', 0.0)),
        )

def _sincronizar_plano_externo_bootstrap(*, plano_externo=None, origem_plano=None, modo_execucao_efetivo=None, diagnostico=None):
    globals()['PLANO_PAGAMENTOS_EXTERNO'] = plano_externo
    globals()['ORIGEM_PLANO_PAGAMENTOS'] = origem_plano
    if modo_execucao_efetivo:
        globals()['MODO_EXECUCAO_FUTURO'] = modo_execucao_efetivo
    if isinstance(diagnostico, dict):
        globals()['DIAGNOSTICO_MODO_EXECUCAO'] = diagnostico
    set_payment_optimizer_runtime(
        plano_pagamentos_externo=plano_externo,
        modo_execucao_futuro=globals().get('MODO_EXECUCAO_FUTURO', MODO_EXECUCAO_FUTURO),
    )
    set_switch_planner_runtime(
        modo_execucao_futuro=globals().get('MODO_EXECUCAO_FUTURO', MODO_EXECUCAO_FUTURO),
        reotimizar_pool_switch_no_futuro=REOTIMIZAR_POOL_SWITCH_NO_FUTURO,
        permitir_switch_antes_30_dias=PERMITIR_SWITCH_ANTES_30_DIAS,
    )

set_external_plan_loader_runtime(
    resultado_otimizador_fixo=RESULTADO_OTIMIZADOR_FIXO,
    paths_cfg=PATHS_CFG,
    auditar_plano_externo=AUDITAR_PLANO_EXTERNO,
    modo_execucao_futuro=MODO_EXECUCAO_FUTURO,
    auto_rebaixar_modo_se_plano_incompativel=AUTO_REBAIXAR_MODO_SE_PLANO_INCOMPATIVEL,
    modo_fallback_plano_incompativel=MODO_FALLBACK_PLANO_INCOMPATIVEL,
    diagnostico_modo_execucao=DIAGNOSTICO_MODO_EXECUCAO,
    ler_df_excel_seguro_fn=_ler_df_excel_seguro,
    iter_produtos_fn=_iter_produtos,
    indexar_produtos_por_signature_fn=_indexar_produtos_por_signature,
    log_debug_fn=_log_debug,
)

set_bootstrap_runtime(
    taxa_dia_base=TAXA_DIA_BASE,
    taxa_proj=globals().get('TAXA_PROJ', TAXA_DIA_BASE),
    modo_execucao_futuro=globals().get('MODO_EXECUCAO_FUTURO', MODO_EXECUCAO_FUTURO),
    data_referencia_efetiva=obter_data_referencia_efetiva_runtime(),
    sync_execution_context_fn=_sincronizar_contexto_bootstrap,
    sync_plano_externo_fn=_sincronizar_plano_externo_bootstrap,
)

_normalizar_data_plano_externo = _normalizar_data_plano_externo_modular
_carregar_plano_externo_dataframe = _carregar_plano_externo_dataframe_modular
_listar_diretorios_busca_resultados = _listar_diretorios_busca_resultados_modular
_listar_candidatos_resultado_otimizador = _listar_candidatos_resultado_otimizador_modular
_score_arquivo_resultado_otimizador = _score_arquivo_resultado_otimizador_modular
carregar_plano_pagamentos_externo = carregar_plano_pagamentos_externo_modular
_ajustar_modo_por_compatibilidade_plano = _ajustar_modo_por_compatibilidade_plano_modular
_coletar_referencias_produtos_plano_externo = _coletar_referencias_produtos_plano_externo_modular
_diagnosticar_compatibilidade_plano_externo = _diagnosticar_compatibilidade_plano_externo_modular

_resolver_taxa_proj_unificada = _resolver_taxa_proj_unificada_modular
_carregar_e_validar_plano_externo_unificado = _carregar_e_validar_plano_externo_unificado_modular
_resolver_contexto_canonico_compartilhado = _resolver_contexto_canonico_compartilhado_modular
_inicializar_contexto_execucao = _inicializar_contexto_execucao_modular

def main_cli():
    return main()

if __name__ == '__main__':
    main_cli()

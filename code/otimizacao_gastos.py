# -*- coding: utf-8 -*-
"""OTIMIZADOR DE RESGATES FINANCEIROS - v14.0

Estratégias: PENALIDADE_5P, HIBRIDO_5P, ECONOMICA_VPL, ECONOMICA_CLIFF,
HEURISTICA e GENETICA_5P.
"""

# =========================================================
# 00. BOOTSTRAP E AMBIENTE
# =========================================================
import sys
import subprocess
import os
import time
import warnings
import json
import re
import unicodedata
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta, datetime
import pandas as pd

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
    """Suprime avisos esperados de HTTPS sem verificação para manter a saída limpa."""
    if InsecureRequestWarning is not None:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        if urllib3 is not None:
            urllib3.disable_warnings(InsecureRequestWarning)

configurar_warnings_rede()

# =========================================================
# auto-install
# =========================================================
def instalar_dependencias():
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'pulp': 'pulp',
        'workalendar': 'workalendar',
        'scipy': 'scipy',
        'numba': 'numba',
        'openpyxl': 'openpyxl',
    }

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    print(">>> [SETUP] Verificando ambiente Python...")

    IN_COLAB = 'google.colab' in sys.modules

    missing = []
    for pip_name, import_name in required.items():
        try:
            __import__(import_name)
        except Exception:
            missing.append(pip_name)

    if missing:
        print(f" -> Instalando: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing, '--quiet'])
            print(" -> Instalação concluída!\n")
        except Exception as e:
            print(f" -> [ERRO] Falha via subprocess: {e}")
            if IN_COLAB:
                print(" -> Tentando via !pip no Colab...")
                try:
                    import IPython
                    for pkg in missing:
                        IPython.get_ipython().system(f'pip install {pkg} --quiet')
                    print(" -> Instalação via !pip concluída!\n")
                except Exception as e2:
                    print(f" -> [ERRO CRÍTICO]: {e2}")
                    sys.exit(1)
            else:
                print(" -> Instale manualmente: pip install " + " ".join(missing))
                sys.exit(1)
    else:
        print(" -> Todas as dependências OK.\n")

instalar_dependencias()

# =========================================================
# imports pós-instalação
# =========================================================
import numpy as np
import pandas as pd
import requests
import pulp
from workalendar.america import Brazil
from scipy.optimize import differential_evolution
from numba import njit

# =========================================================
# 01. CONFIG, CONTRATO E RESOLUÇÃO
# =========================================================
DEFAULT_CONFIG_FILES = (
    "code/config_atualizado.json",
    "code/config.json",
)

def _resolver_config_path() -> Path:
    env_path = os.environ.get("OTIMIZADOR_CONFIG")
    if env_path:
        return Path(env_path)
    for nome_arquivo in DEFAULT_CONFIG_FILES:
        candidato = Path(nome_arquivo)
        if candidato.exists():
            return candidato
    return Path(DEFAULT_CONFIG_FILES[0])

CONFIG_PATH = _resolver_config_path()
BASE_DIR_ATIVA = CONFIG_PATH.parent.resolve() if str(CONFIG_PATH.parent) not in ("", ".") else Path.cwd().resolve()

def carregar_config(config_path: Path = CONFIG_PATH) -> dict:
    if not config_path.exists():
        raise RuntimeError(
            f"Arquivo de configuração não encontrado: {config_path}. "
            "Crie um config.json válido antes de executar o script."
        )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Falha ao ler o arquivo de configuração {config_path}: {e}") from e
    if not isinstance(data, dict):
        raise RuntimeError(f"O arquivo de configuração {config_path} deve conter um objeto JSON na raiz.")
    return data

config = carregar_config()


def _cfg_get(path, default=None):
    cur = config
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _cfg_get_required(path):
    cur = config
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError(f"Config obrigatório ausente: {'/'.join(path)}")
        cur = cur[k]
    return cur

def _cfg_get_any(paths, default=None):
    for path in paths:
        val = _cfg_get(path, None)
        if val is not None:
            return val
    return default

def _cfg_get_required_any(paths):
    val = _cfg_get_any(paths, None)
    if val is None:
        caminhos = ' ou '.join('/'.join(p) for p in paths)
        raise KeyError(f"Config obrigatório ausente: {caminhos}")
    return val

BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME = _cfg_get_required(["bootstrap", "parametros_5p_default_nome"])
REDE_USER_AGENT_DOWNLOAD = _cfg_get_required(["rede", "user_agent_download_planilha"])
REDE_USER_AGENT_BCB = _cfg_get_required(["rede", "user_agent_bcb"])
REDE_ACCEPT_BCB = _cfg_get_required(["rede", "accept_bcb"])
REDE_TIMEOUT_DOWNLOAD_SEGUNDOS = _cfg_get_required(["rede", "timeout_download_segundos"])
REDE_TIMEOUT_BCB_SEGUNDOS = _cfg_get_required(["rede", "timeout_bcb_segundos"])
REDE_VERIFICAR_SSL = _cfg_get_required(["rede", "verificar_ssl"])
ARQUIVO_TEMPORARIO_FALLBACK_BCB = _cfg_get_required(["arquivos", "temporario_fallback_bcb"])
HISTORICO_BCB_DATA_MINIMA = date.fromisoformat(str(_cfg_get_required(["historico_bcb", "data_minima_consulta"])))
HISTORICO_BCB_DATA_MINIMA_FORMATADA = _cfg_get_required(["historico_bcb", "data_minima_consulta_formatada"])
CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO = int(_cfg_get_required(["calendario", "ano_inicio_dias_sem_rendimento"]))
CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO = int(_cfg_get_required(["calendario", "ano_fim_dias_sem_rendimento"]))
ORDEM_PROCESSAMENTO_SENTINELA = _cfg_get_required(["execucao", "ordem_processamento_sentinela"])
AVALIACAO_WF_PCT_TREINO = float(_cfg_get_required(["avaliacao", "walkforward", "pct_treino"]))
AVALIACAO_WF_ROBUSTEZ_DEFAULT = float(_cfg_get_required(["avaliacao", "walkforward", "robustez_default"]))
AVALIACAO_RANKING_PESO_SALDO = float(_cfg_get_required(["avaliacao", "ranking", "peso_saldo"]))
AVALIACAO_RANKING_PESO_ROBUSTEZ = float(_cfg_get_required(["avaliacao", "ranking", "peso_robustez"]))
if not (0.0 < AVALIACAO_WF_PCT_TREINO < 1.0):
    raise ValueError(f"avaliacao.walkforward.pct_treino inválido: {AVALIACAO_WF_PCT_TREINO}")
if AVALIACAO_WF_ROBUSTEZ_DEFAULT < 0.0:
    raise ValueError(f"avaliacao.walkforward.robustez_default inválido: {AVALIACAO_WF_ROBUSTEZ_DEFAULT}")
if AVALIACAO_RANKING_PESO_SALDO < 0.0 or AVALIACAO_RANKING_PESO_ROBUSTEZ < 0.0:
    raise ValueError("Pesos de avaliacao.ranking não podem ser negativos")
if abs((AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ) - 1.0) > 1e-9:
    raise ValueError(
        f"Pesos de avaliacao.ranking devem somar 1.0; atual={(AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ):.12f}"
    )


# =========================================================
# contrato e metadata cdi
# =========================================================
CONTRATO_OPERACIONAL = None
CDI_FONTE_UTILIZADA = None
CDI_DATA_FINAL_UTILIZADA = None
CDI_DATA_CORTE_CONGELADA = None
MAPA_PRODUTOS_CANONICO = None
USAR_INVESTIMENTOS_NORM_NEW = True

DEBUG_CDI = True
DEBUG_SHADOW = False

DEBUG_SWITCH_SHADOW = False

def log_resumo(tag: str, **kwargs) -> None:
    partes = [f"{k}={v}" for k, v in kwargs.items()]
    print(f"[{tag}] " + " | ".join(partes))

def log_debug(flag: bool, tag: str, **kwargs) -> None:
    if flag:
        partes = [f"{k}={v}" for k, v in kwargs.items()]
        print(f"[{tag}] " + " | ".join(partes))

def log_erro(tag: str, erro) -> None:
    print(f"[{tag}] erro={erro}")

def obter_contrato_operacional(config: dict) -> dict:
    """
    Traduz o config expandido para o contrato operacional real desta versão.

    Nesta versão:
    - Aportes NÃO são lidos de aba própria; são derivados de lotes.
    - Ligações gasto-lote NÃO são lidas de aba própria; são derivadas internamente.
    - As entradas primárias reais são: carteira, lotes e despesas.
    """
    abas_cfg = config.get("abas", {}) if isinstance(config, dict) else {}
    validacoes_cfg = config.get("validacoes", {}) if isinstance(config, dict) else {}
    politicas_cfg = config.get("politicas", {}) if isinstance(config, dict) else {}
    colunas_cfg = config.get("colunas", {}) if isinstance(config, dict) else {}

    contrato = {
        "versao": "contrato_operacional_v1",
        "abas_entrada_obrigatorias": {
            "carteira": abas_cfg.get("carteira", "Carteira"),
            "lotes": abas_cfg.get("lotes", "Inventário de Lotes"),
            "despesas": abas_cfg.get("despesas", "Todos os Gastos"),
        },
        "abas_entrada_opcionais": {
            "ratings_bancos": abas_cfg.get("ratings_bancos", "Ratings_Bancos"),
        },
        "abas_derivadas_internamente": {
            "aportes": True,
            "ligacoes_gastos_lotes": True,
        },
        "usa_aba_aportes": False,
        "usa_aba_ligacoes_gastos_lotes": False,
        "deriva_aportes_de_lotes": True,
        "deriva_ligacoes_de_gastos": True,
        "politicas": {
            "permitir_alias_coluna": bool(politicas_cfg.get("permitir_alias_coluna", True)),
            "abortar_sem_coluna_critica": bool(politicas_cfg.get("abortar_sem_coluna_critica", True)),
            "tratar_pago_nulo_como_nao": bool(politicas_cfg.get("tratar_pago_nulo_como_nao", True)),
            "aceitar_multiplos_lotes_por_despesa": bool(politicas_cfg.get("aceitar_multiplos_lotes_por_despesa", True)),
            "lote_futuro_sem_produto": politicas_cfg.get("lote_futuro_sem_produto", "permitir"),
            "lote_futuro_sem_produto_comportamento": politicas_cfg.get(
                "lote_futuro_sem_produto_comportamento", "caixa"
            ),
        },
        "validacoes": {
            "produto_inexistente_em_lote": validacoes_cfg.get("produto_inexistente_em_lote", "erro"),
            "produto_inativo_em_novo_aporte": validacoes_cfg.get("produto_inativo_em_novo_aporte", "erro"),
            "despesa_id_ausente": validacoes_cfg.get("despesa_id_ausente", "gerar_automatico"),
            "valor_nao_numerico": validacoes_cfg.get("valor_nao_numerico", "erro"),
            "data_invalida": validacoes_cfg.get("data_invalida", "erro"),
            "coluna_ausente_critica": validacoes_cfg.get("coluna_ausente_critica", "erro"),
        },
        "colunas_relevantes": {
            "carteira": colunas_cfg.get("carteira", {}),
            "lotes": colunas_cfg.get("lotes", {}),
            "despesas": colunas_cfg.get("despesas", {}),
        },
    }
    return contrato

def validar_contrato_operacional(contrato: dict) -> None:
    if not isinstance(contrato, dict):
        raise ValueError("Contrato operacional inválido: esperado dict.")
    abas_obrig = contrato.get("abas_entrada_obrigatorias", {})
    for chave in ("carteira", "lotes", "despesas"):
        valor = abas_obrig.get(chave)
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"Contrato operacional inválido: aba obrigatória '{chave}' ausente ou vazia.")
    if bool(contrato.get("usa_aba_aportes", False)) and bool(contrato.get("deriva_aportes_de_lotes", False)):
        raise ValueError("Contrato operacional inconsistente: usa_aba_aportes e deriva_aportes_de_lotes não podem ser True ao mesmo tempo.")
    if bool(contrato.get("usa_aba_ligacoes_gastos_lotes", False)) and bool(contrato.get("deriva_ligacoes_de_gastos", False)):
        raise ValueError("Contrato operacional inconsistente: usa_aba_ligacoes_gastos_lotes e deriva_ligacoes_de_gastos não podem ser True ao mesmo tempo.")
    politicas = contrato.get("politicas", {})
    for chave in (
        "permitir_alias_coluna",
        "abortar_sem_coluna_critica",
        "tratar_pago_nulo_como_nao",
        "aceitar_multiplos_lotes_por_despesa",
        "lote_futuro_sem_produto",
        "lote_futuro_sem_produto_comportamento",
    ):
        if chave not in politicas:
            raise ValueError(f"Contrato operacional inválido: política ausente '{chave}'.")

def resumir_contrato_operacional(contrato: dict) -> str:
    abas_obrig = contrato.get("abas_entrada_obrigatorias", {})
    abas_opt = contrato.get("abas_entrada_opcionais", {})
    politicas = contrato.get("politicas", {})
    partes = [
        f"versao={contrato.get('versao')}",
        (
            "abas_obrigatorias="
            f"{{carteira: {abas_obrig.get('carteira')}, "
            f"lotes: {abas_obrig.get('lotes')}, "
            f"despesas: {abas_obrig.get('despesas')}}}"
        ),
        (
            "abas_opcionais="
            f"{{ratings_bancos: {abas_opt.get('ratings_bancos')}}}"
        ),
        f"deriva_aportes_de_lotes={contrato.get('deriva_aportes_de_lotes')}",
        f"usa_aba_aportes={contrato.get('usa_aba_aportes')}",
        f"deriva_ligacoes_de_gastos={contrato.get('deriva_ligacoes_de_gastos')}",
        f"usa_aba_ligacoes_gastos_lotes={contrato.get('usa_aba_ligacoes_gastos_lotes')}",
        f"tratar_pago_nulo_como_nao={politicas.get('tratar_pago_nulo_como_nao')}",
        f"aceitar_multiplos_lotes_por_despesa={politicas.get('aceitar_multiplos_lotes_por_despesa')}",
        f"permitir_alias_coluna={politicas.get('permitir_alias_coluna')}",
    ]
    return " | ".join(partes)

def _safe_float(x, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default

def _normalizar_nome_arquivo_json(nome_padrao: str) -> str:
    nome = str(nome_padrao or BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME).strip()
    if not nome:
        nome = str(BOOTSTRAP_PARAMETROS_5P_DEFAULT_NOME)
    if not nome.lower().endswith('.json'):
        nome = f'{nome}.json'
    return nome

CONTRATO_OPERACIONAL = obter_contrato_operacional(config)
validar_contrato_operacional(CONTRATO_OPERACIONAL)
print(f"[CONTRATO] {resumir_contrato_operacional(CONTRATO_OPERACIONAL)}")

# =========================================================
# 02. POLÍTICAS E UTILITÁRIOS CENTRAIS
# =========================================================

_tz_nome = _cfg_get_required(["execucao", "timezone"])
if ZoneInfo is not None:
    try:
        TZ_BRASIL = ZoneInfo(_tz_nome)
    except Exception:
        TZ_BRASIL = None
else:
    TZ_BRASIL = None
if TZ_BRASIL is None:
    try:
        import pytz
        TZ_BRASIL = pytz.timezone(_tz_nome)
    except Exception:
        TZ_BRASIL = None
try:
    DATA_REFERENCIA = datetime.now(TZ_BRASIL).date() if TZ_BRASIL is not None else datetime.now().date()
except Exception:
    DATA_REFERENCIA = datetime.now().date()

# =========================================================
# configurações globais
# =========================================================
NOME_ARQUIVO_LOCAL = str(BASE_DIR_ATIVA / _cfg_get_required_any([["arquivos", "planilha"], ["paths", "excel_local"]]))
CACHE_BCB_FILE = str(BASE_DIR_ATIVA / _cfg_get_required_any([["arquivos", "cache_bcb"], ["paths", "cache_bcb"]]))
_PARAM_FILE_NAME = _cfg_get_required_any(
    [["arquivos", "parametros_5p"], ["arquivos", "melhores_parametros_5p"]]
)
PARAM_FILE_5P = str(BASE_DIR_ATIVA / _normalizar_nome_arquivo_json(_PARAM_FILE_NAME))

GOOGLE_SHEETS_FILE_ID = _cfg_get(["google_drive", "sheets_file_id"], None)
FALLBACK_BCB_FILE_ID = _cfg_get(["google_drive", "fallback_bcb_file_id"], None)
FALLBACK_PARAM_5P_FILE_ID = _cfg_get(["google_drive", "fallback_param_5p_file_id"], None)

GOOGLE_SHEETS_EXPORT_BASE = _cfg_get_required(["urls", "google_sheets_export_base"])
GOOGLE_DRIVE_DOWNLOAD_BASE = _cfg_get_required(["urls", "google_drive_download_base"])
BCB_SERIE_12_URL = _cfg_get_required(["urls", "bcb_sgs_12_url"])

ABA_EXTRATO = _cfg_get_required(["saidas", "aba_extrato"])
ABA_AUDITORIA_EXTRATO = _cfg_get_required(["saidas", "aba_auditoria_extrato"])
ABA_CARTEIRA_FINAL = _cfg_get_required(["saidas", "aba_carteira_final"])
ABA_RESUMO = _cfg_get_required(["saidas", "aba_resumo"])
ABA_SITUACAO_ATUAL = _cfg_get_required(["saidas", "aba_situacao_atual"])
ABA_SWITCH_DIAGNOSTICO = "switch_diagnostico"
ABA_SWITCH_EXECUCAO = "switch_execucao"
TEMPLATE_RESULTADO_ESTRATEGIA = _cfg_get_required(["saidas", "template_arquivo_resultado_estrategia"])

FALLBACK_BCB_URL = GOOGLE_DRIVE_DOWNLOAD_BASE.format(file_id=FALLBACK_BCB_FILE_ID) if FALLBACK_BCB_FILE_ID else None
FALLBACK_PARAM_URL_5P = GOOGLE_DRIVE_DOWNLOAD_BASE.format(file_id=FALLBACK_PARAM_5P_FILE_ID) if FALLBACK_PARAM_5P_FILE_ID else None

CDI_ANUAL = float(_cfg_get_required(["premissas_mercado", "cdi_anual_modelo"]))
CONVENCAO_DIAS_ANO_CDI = int(_cfg_get_required(["execucao", "convencao_dias_ano", "cdi"]))
TAXA_DIA_BASE = ((1 + CDI_ANUAL) ** (1 / CONVENCAO_DIAS_ANO_CDI)) - 1

TAXA_BASE_DEFAULT = float(_cfg_get_required(["defaults_lote", "taxa_base_cdi"]))
TAXA_BONUS_DEFAULT = float(_cfg_get_required(["defaults_lote", "taxa_bonus_cdi"]))
DIAS_BONUS_DEFAULT = int(_cfg_get_required(["defaults_lote", "dias_bonus"]))
PRODUTO_FALLBACK_NOME_RAW = str(_cfg_get(["defaults_lote", "produto_fallback_nome"], ""))
INVESTIMENTO_REFERENCIA_FUTURO_NOME = str(_cfg_get_any([["defaults", "investimento_referencia_futuro"]], "") or "").strip()
INVESTIMENTO_REFERENCIA_FUTURO_MATCH_EXATO = bool(_cfg_get_any([["defaults", "investimento_referencia_futuro_match_exato"]], True))
TAXA_BASE_REFERENCIA_FUTURA_DEFAULT = float(_cfg_get_any([["defaults_lote", "taxa_base_referencia_futura_default"], ["defaults", "taxa_base_referencia_futura_default"]], TAXA_BASE_DEFAULT))

IOF_TABLE = np.array(_cfg_get_required(["iof", "tabela"]), dtype=np.float64)
if IOF_TABLE.size == 29:
    IOF_TABLE = np.concatenate(([1.0], IOF_TABLE))
elif IOF_TABLE.size != 30:
    raise RuntimeError(
        f"config['iof']['tabela'] deve ter 29 ou 30 valores; recebido: {IOF_TABLE.size}."
    )

IR_FAIXAS = {}
for faixa in _cfg_get_required(["ir", "faixas"]):
    dias_max = faixa.get("dias_max")
    chave = 9999 if dias_max is None else int(dias_max)
    aliquota = float(faixa["aliquota"])
    IR_FAIXAS[chave] = {"ir": aliquota, "proxima": aliquota, "delta": 0.0}

if not IR_FAIXAS:
    raise RuntimeError("config['ir']['faixas'] não pode estar vazio.")

_ordenadas = sorted(IR_FAIXAS.keys())
for i, chave in enumerate(_ordenadas):
    prox = _ordenadas[i + 1] if i + 1 < len(_ordenadas) else chave
    IR_FAIXAS[chave]["proxima"] = IR_FAIXAS[prox]["ir"]
    IR_FAIXAS[chave]["delta"] = max(0.0, IR_FAIXAS[chave]["ir"] - IR_FAIXAS[prox]["ir"])

IR_MARCOS_CLIFF = tuple(sorted(int(f["dias_max"]) for f in _cfg_get_required(["ir", "faixas"]) if f.get("dias_max") is not None))
IR_MARCOS_CLIFF_NUMBA = np.array(IR_MARCOS_CLIFF, dtype=np.int64)
DIAS_CLIFF_IR = int(_cfg_get_required(["pagamento", "dias_cliff_ir"]))
LOTES_MONITORADOS_LIQUIDO = set(_cfg_get_required(["auditoria", "lotes_monitorados_liquido"]))
TOLERANCIA_MONETARIA = float(_cfg_get_required(["replay", "tolerancia_monetaria"]))
VALOR_MINIMO_LOTE_ATIVO = float(_cfg_get_required(["replay", "valor_minimo_lote_ativo"]))
VALOR_MINIMO_RESGATE_BRUTO = float(_cfg_get_required(["pagamento", "valor_minimo_resgate_bruto"]))

### Parei Aqui


TREINAMENTO_PERFIS = _cfg_get_required(["treinamento", "perfis"])

TREINAMENTO_TEMPO_ALVO_MINIMO_ABSOLUTO = int(_cfg_get_required(["treinamento", "modo_auto", "tempo_alvo_minimo_absoluto"]))
TREINAMENTO_AUTO_TEMPO_ALVO_CURTO_MAX = int(_cfg_get_required(["treinamento", "modo_auto", "thresholds", "tempo_alvo_curto_max"]))
TREINAMENTO_AUTO_TEMPO_ALVO_LONGO_MIN = int(_cfg_get_required(["treinamento", "modo_auto", "thresholds", "tempo_alvo_longo_min"]))
TREINAMENTO_AUTO_CARGA_MEDIA_MIN = float(_cfg_get_required(["treinamento", "modo_auto", "thresholds", "carga_media_min"]))
TREINAMENTO_AUTO_CARGA_ALTA_MIN = float(_cfg_get_required(["treinamento", "modo_auto", "thresholds", "carga_alta_min"]))
TREINAMENTO_AUTO_CARGA_BAIXA_MAX = float(_cfg_get_required(["treinamento", "modo_auto", "thresholds", "carga_baixa_max"]))
TREINAMENTO_MAX_CONTAS_PADRAO = int(_cfg_get_required(["treinamento", "reducao_contas", "max_contas_padrao"]))

MODO_TREINAMENTO_PADRAO = str(_cfg_get_required(["execucao", "defaults_interativos", "modo_treinamento_padrao"]))
PERFIL_TREINO_PADRAO = str(_cfg_get_required(["execucao", "defaults_interativos", "perfil_treino_padrao"]))
PERFIL_TREINO_AUTO_OPCAO = str(_cfg_get_required(["execucao", "defaults_interativos", "perfil_treino_auto_opcao"]))
TEMPO_ALVO_AUTO_PADRAO_MINUTOS = int(_cfg_get_required(["execucao", "defaults_interativos", "tempo_alvo_auto_padrao_minutos"]))

HORIZONTE_PROJECAO_DIAS = int(_cfg_get_required(["simulacao", "horizonte_extra_dias"]))

CFG_OPT_GEN = _cfg_get_required(["otimizacao", "genetica_profunda"])
CFG_OPT_PEN = _cfg_get_required(["otimizacao", "penalidade_5p"])

OPT_GEN_SEED = int(_cfg_get_required(["otimizacao", "genetica_profunda", "seed"]))
OPT_GEN_STRATEGY = str(_cfg_get_required(["otimizacao", "genetica_profunda", "strategy"]))
OPT_GEN_UPDATING = str(_cfg_get_required(["otimizacao", "genetica_profunda", "updating"]))
OPT_GEN_INIT_SEM_POPULACAO_INICIAL = str(_cfg_get_required(["otimizacao", "genetica_profunda", "init_sem_populacao_inicial"]))
OPT_GEN_WORKERS = int(_cfg_get_required(["otimizacao", "genetica_profunda", "workers"]))

OPT_PEN_SEED = int(_cfg_get_required(["otimizacao", "penalidade_5p", "seed"]))
OPT_PEN_STRATEGY = str(_cfg_get_required(["otimizacao", "penalidade_5p", "strategy"]))
OPT_PEN_UPDATING = str(_cfg_get_required(["otimizacao", "penalidade_5p", "updating"]))
OPT_PEN_INIT_SEM_POPULACAO_INICIAL = str(_cfg_get_required(["otimizacao", "penalidade_5p", "init_sem_populacao_inicial"]))
OPT_PEN_WORKERS = int(_cfg_get_required(["otimizacao", "penalidade_5p", "workers"]))

CFG_OPT_GEN_POP_INIT = CFG_OPT_GEN.get("populacao_inicial", {}) or {}
OPT_GEN_DIVISOR_POPSIZE_CLONES = int(CFG_OPT_GEN_POP_INIT.get("divisor_popsize_clones", 3))
OPT_GEN_MIN_CLONES = int(CFG_OPT_GEN_POP_INIT.get("min_clones", 1))
OPT_GEN_RUIDO_GAUSSIANO_MEDIA = float(CFG_OPT_GEN_POP_INIT.get("ruido_gaussiano_media", 0.0))
OPT_GEN_RUIDO_GAUSSIANO_DESVIO = float(CFG_OPT_GEN_POP_INIT.get("ruido_gaussiano_desvio", 0.1))
if OPT_GEN_DIVISOR_POPSIZE_CLONES < 1:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/divisor_popsize_clones deve ser >= 1")
if OPT_GEN_MIN_CLONES < 0:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/min_clones deve ser >= 0")
if OPT_GEN_RUIDO_GAUSSIANO_DESVIO < 0:
    raise ValueError("otimizacao/genetica_profunda/populacao_inicial/ruido_gaussiano_desvio deve ser >= 0")

CFG_OPT_PEN_POP_INIT = CFG_OPT_PEN.get("populacao_inicial", {}) or {}
OPT_PEN_DIVISOR_POPSIZE_CLONES = int(CFG_OPT_PEN_POP_INIT.get("divisor_popsize_clones", 3))
OPT_PEN_MIN_CLONES = int(CFG_OPT_PEN_POP_INIT.get("min_clones", 1))
OPT_PEN_RUIDO_GAUSSIANO_MEDIA = float(CFG_OPT_PEN_POP_INIT.get("ruido_gaussiano_media", 0.0))
OPT_PEN_RUIDO_GAUSSIANO_DESVIO = float(CFG_OPT_PEN_POP_INIT.get("ruido_gaussiano_desvio", 0.1))
if OPT_PEN_DIVISOR_POPSIZE_CLONES < 1:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/divisor_popsize_clones deve ser >= 1")
if OPT_PEN_MIN_CLONES < 0:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/min_clones deve ser >= 0")
if OPT_PEN_RUIDO_GAUSSIANO_DESVIO < 0:
    raise ValueError("otimizacao/penalidade_5p/populacao_inicial/ruido_gaussiano_desvio deve ser >= 0")

def _cfg_bounds_to_tuples(cfg_dict, *path, expected_dims=5):
    cur = cfg_dict
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError(f"Chave obrigatória ausente no config: {'/'.join(path)}")
        cur = cur[k]
    raw = cur
    if not isinstance(raw, list):
        raise TypeError(f"Bounds em {'/'.join(path)} devem ser uma lista.")
    if len(raw) != expected_dims:
        raise ValueError(f"Bounds em {'/'.join(path)} devem ter {expected_dims} dimensões, encontrado {len(raw)}.")
    bounds = []
    for i, item in enumerate(raw):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"Bound na posição {i} em {'/'.join(path)} deve ter exatamente 2 valores.")
        lo, hi = float(item[0]), float(item[1])
        if lo > hi:
            raise ValueError(f"Bound inválido na posição {i} em {'/'.join(path)}: mínimo {lo} maior que máximo {hi}.")
        bounds.append((lo, hi))
    return bounds

OPT_GEN_BOUNDS = _cfg_bounds_to_tuples(config, "otimizacao", "genetica_profunda", "bounds")
OPT_PEN_BOUNDS = _cfg_bounds_to_tuples(config, "otimizacao", "penalidade_5p", "bounds")

def obter_aliquota_ir(dias_vida):
    dias_vida = int(dias_vida)
    for threshold in sorted(IR_FAIXAS.keys()):
        if dias_vida <= threshold:
            return float(IR_FAIXAS[threshold]["ir"])
    ultima = max(IR_FAIXAS.keys())
    return float(IR_FAIXAS[ultima]["ir"])

IR_THRESHOLDS_NUMBA = np.array(sorted(IR_FAIXAS.keys()), dtype=np.int64)
IR_ALIQUOTAS_NUMBA = np.array([float(IR_FAIXAS[k]["ir"]) for k in sorted(IR_FAIXAS.keys())], dtype=np.float64)

@njit(nogil=True, fastmath=True)
def obter_aliquota_ir_numba(dias_vida, thresholds, aliquotas):
    dias_vida = int(dias_vida)
    for i in range(len(thresholds)):
        if dias_vida <= thresholds[i]:
            return aliquotas[i]
    return aliquotas[len(aliquotas) - 1]


def distancia_proximo_cliff_ir(dias_vida):
    dias_vida = int(dias_vida)
    for marco in IR_MARCOS_CLIFF:
        if dias_vida < marco:
            return marco - dias_vida
    return 999

@njit(nogil=True, fastmath=True)
def distancia_proximo_cliff_ir_numba(dias_vida):
    dias_vida = int(dias_vida)
    for i in range(len(IR_MARCOS_CLIFF_NUMBA)):
        marco = IR_MARCOS_CLIFF_NUMBA[i]
        if dias_vida < marco:
            return float(marco - dias_vida)
    return 999.0

cal = Brazil()

# =========================================================
# 03. PRODUTOS E CARTEIRA
# =========================================================
INVESTIMENTOS_NORM = {}  # chave normalizada -> {base, bonus, dias_bonus}

def normalizar_nome(nome):
    """Colapsa espaços, remove espaços extras e converte para minúsculas."""
    if not isinstance(nome, str):
        return ''
    return re.sub(r'\s+', ' ', nome).strip().lower()

def _eh_produto_lote_ausente(valor):
    if valor is None:
        return True
    s = str(valor).strip().lower()
    return s in {'', '-', '—', '--', 'nan', 'none', 'null'}

def _resolver_nome_produto_lote_efetivo(valor_produto):
    if _eh_produto_lote_ausente(valor_produto):
        return PRODUTO_FALLBACK_NOME_RAW
    return str(valor_produto).strip()

PRODUTO_FALLBACK_NOME = normalizar_nome(PRODUTO_FALLBACK_NOME_RAW)

def _normalizar_chave_coluna(valor):
    s = '' if valor is None else str(valor)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace('_', ' ')
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def nome_aba(chave: str) -> str:
    chave = str(chave or '').strip()
    if not chave:
        raise KeyError('nome_aba requer uma chave não vazia.')

    if isinstance(CONTRATO_OPERACIONAL, dict):
        for bloco in ('abas_entrada_obrigatorias', 'abas_entrada_opcionais'):
            nome = (CONTRATO_OPERACIONAL.get(bloco) or {}).get(chave)
            if isinstance(nome, str) and nome.strip():
                return nome.strip()

    nome = _cfg_get(['abas', chave], None)
    if isinstance(nome, str) and nome.strip():
        return nome.strip()

    return chave

def _aliases_config_coluna(secao: str, campo: str) -> list:
    aliases = []
    try:
        aliases_cfg = (((config or {}).get('colunas') or {}).get(secao) or {}).get(campo)
        if isinstance(aliases_cfg, list):
            aliases.extend(str(x) for x in aliases_cfg if str(x).strip())
        elif isinstance(aliases_cfg, str) and aliases_cfg.strip():
            aliases.append(aliases_cfg)
    except Exception:
        pass
    if campo not in aliases:
        aliases.append(campo)
    return aliases

def resolver_coluna(df: pd.DataFrame, secao: str, campo: str, required: bool = True):
    if df is None or len(getattr(df, 'columns', [])) == 0:
        if required:
            raise KeyError(f'Sem colunas disponíveis para resolver {secao}.{campo}')
        return None

    colunas = list(df.columns)
    mapa_norm = {_normalizar_chave_coluna(c): c for c in colunas}
    aliases = _aliases_config_coluna(secao, campo)

    for alias in aliases:
        if alias in df.columns:
            return alias

    for alias in aliases:
        alias_norm = _normalizar_chave_coluna(alias)
        if alias_norm in mapa_norm:
            return mapa_norm[alias_norm]

    tokens_alvo = set(_normalizar_chave_coluna(a) for a in aliases if str(a).strip())
    melhor = None
    melhor_score = -1
    for col in colunas:
        col_norm = _normalizar_chave_coluna(col)
        score = 0
        if col_norm in tokens_alvo:
            score += 1000
        for alias in aliases:
            alias_norm = _normalizar_chave_coluna(alias)
            if alias_norm and alias_norm in col_norm:
                score = max(score, 100 + len(alias_norm))
        if score > melhor_score:
            melhor = col
            melhor_score = score

    if melhor is not None and melhor_score >= 100:
        return melhor

    if required:
        raise KeyError(
            f'Coluna não encontrada para {secao}.{campo}. Aliases={aliases}. Colunas disponíveis={colunas}'
        )
    return None

def selecionar_coluna_id_lote(df: pd.DataFrame, contexto: str | None = None):
    return resolver_coluna(df, 'lotes', 'lote_id', required=True)

def _construir_vocab_investimentos(investimentos_map: dict | None):
    vocab = set()
    if not isinstance(investimentos_map, dict):
        return vocab
    for chave, info in investimentos_map.items():
        if chave is not None:
            vocab.add(normalizar_nome(chave))
        if isinstance(info, dict):
            for campo in ('nome_original', 'investimento', 'nome', 'produto_nome'):
                valor = info.get(campo)
                if valor:
                    vocab.add(normalizar_nome(valor))
    return {v for v in vocab if v}

def selecionar_coluna_produto_lote(df: pd.DataFrame, investimentos_map=None):
    candidatos = []
    alias_preferencial = resolver_coluna(df, 'lotes', 'produto_id', required=False)
    if alias_preferencial is not None:
        candidatos.append(alias_preferencial)

    tokens_busca = [
        _normalizar_chave_coluna(x)
        for x in (_cfg_get(['politicas_coluna', 'produto_tokens_busca'], []) or [])
    ]
    for col in df.columns:
        col_norm = _normalizar_chave_coluna(col)
        if any(tok and tok in col_norm for tok in tokens_busca):
            candidatos.append(col)

    vistos = set()
    candidatos_ordenados = []
    for c in candidatos + list(df.columns):
        if c not in vistos:
            vistos.add(c)
            candidatos_ordenados.append(c)

    vocab = _construir_vocab_investimentos(investimentos_map)
    melhor = None
    melhor_score = float('-inf')
    for col in candidatos_ordenados:
        serie = df[col] if col in df.columns else None
        if serie is None:
            continue
        score = 0.0
        if alias_preferencial and col == alias_preferencial:
            score += 1000.0
        col_norm = _normalizar_chave_coluna(col)
        if 'invest' in col_norm or 'produto' in col_norm:
            score += 100.0

        total_validos = 0
        reconhecidos = 0
        for valor in serie.tolist():
            if valor is None:
                continue
            s = str(valor).strip()
            if not s or s.lower() in {'nan', 'none', 'null', '-', '—', '--'}:
                continue
            total_validos += 1
            if normalizar_nome(s) in vocab:
                reconhecidos += 1
        if total_validos > 0:
            score += 500.0 * (reconhecidos / total_validos)

        if score > melhor_score:
            melhor = col
            melhor_score = score

    if melhor is not None:
        return melhor
    raise KeyError(f'Não foi possível selecionar a coluna de produto dos lotes. Colunas disponíveis={list(df.columns)}')

def _to_cdi_multiplier(x, default=1.0):
    """
    Converte um valor da planilha para multiplicador CDI.
    Ex.: 103 -> 1.03, 1.03 -> 1.03, '103%' -> 1.03
    """
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
        # Heurística configurável: se for acima do limite, assume percentual; senão, multiplicador
        if v > POL_TAXA_LIMITE_PERCENTUAL_VS_MULTIPLICADOR:
            return v / 100.0
        return v
    except Exception:
        return float(default)

# =========================================================
# carteira canônica
# =========================================================

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
    """
    Converte taxa para multiplicador decimal interno.
    Exemplos:
      103   -> 1.03
      103%  -> 1.03
      1.03  -> 1.03
      130   -> 1.30
    """
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

def normalizar_carteira_bruta(
    df_carteira,
    config: dict,
    contrato: dict,
    *,
    normalizar_nome_fn=None,
):
    """
    Constrói a carteira canônica em modo sombra.
    Não altera o INVESTIMENTOS_NORM ativo.
    """
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    auditoria = {
        "colunas_resolvidas": {},
        "defaults_aplicados": [],
        "linhas_descartadas": [],
        "sem_produto_id": 0,
        "produtos_total": 0,
    }

    campos = {
        "produto_id": resolver_coluna(df_carteira, "carteira", "produto_id", required=False),
        "nome": resolver_coluna(df_carteira, "carteira", "nome", required=True),
        "tipo": resolver_coluna(df_carteira, "carteira", "tipo", required=False),
        "indexador": resolver_coluna(df_carteira, "carteira", "indexador", required=False),
        "taxa_base": resolver_coluna(df_carteira, "carteira", "taxa_base", required=True),
        "taxa_bonus": resolver_coluna(df_carteira, "carteira", "taxa_bonus", required=False),
        "dias_bonus": resolver_coluna(df_carteira, "carteira", "dias_bonus", required=False),
        "carencia_dias": resolver_coluna(df_carteira, "carteira", "carencia_dias", required=False),
        "liquidez_dias": resolver_coluna(df_carteira, "carteira", "liquidez_dias", required=False),
        "isento_ir": resolver_coluna(df_carteira, "carteira", "isento_ir", required=False),
        "ativo": resolver_coluna(df_carteira, "carteira", "ativo", required=False),
        "aplicacao_minima": resolver_coluna(df_carteira, "carteira", "aplicacao_minima", required=False),
        "aplicacao_maxima": resolver_coluna(df_carteira, "carteira", "aplicacao_maxima", required=False),
        "fgc": resolver_coluna(df_carteira, "carteira", "fgc", required=False),
        "banco_emissor": resolver_coluna(df_carteira, "carteira", "banco_emissor", required=False),
        "risco_real": resolver_coluna(df_carteira, "carteira", "risco_real", required=False),
        "somente_combo": resolver_coluna(df_carteira, "carteira", "somente_combo", required=False),
        "produto_base": resolver_coluna(df_carteira, "carteira", "produto_base", required=False),
        "produto_bonus": resolver_coluna(df_carteira, "carteira", "produto_bonus", required=False),
        "ratio_base": resolver_coluna(df_carteira, "carteira", "ratio_base", required=False),
        "ratio_bonus": resolver_coluna(df_carteira, "carteira", "ratio_bonus", required=False),
        "max_usos": resolver_coluna(df_carteira, "carteira", "max_usos", required=False),
    }
    auditoria["colunas_resolvidas"] = campos.copy()

    limite = None
    try:
        if isinstance(contrato, dict):
            limite = contrato.get("politicas", {}).get("limite_percentual_vs_multiplicador", None)
    except Exception:
        limite = None

    if limite is None:
        try:
            if isinstance(config, dict):
                limite = config.get("politicas", {}).get("limite_percentual_vs_multiplicador", 10.0)
        except Exception:
            limite = 10.0

    limite = _to_float_produto(limite, 10.0)

    registros = []
    for idx, row in df_carteira.iterrows():
        nome = _normalizar_texto_produto(row[campos["nome"]]) if campos["nome"] in df_carteira.columns else ""
        if not nome:
            auditoria["linhas_descartadas"].append(
                {"idx": int(idx), "motivo": "nome_vazio"}
            )
            continue

        produto_id_raw = None
        if campos["produto_id"] and campos["produto_id"] in df_carteira.columns:
            produto_id_raw = row[campos["produto_id"]]
        if produto_id_raw is None or str(produto_id_raw).strip() == "":
            auditoria["sem_produto_id"] += 1

        nome_norm = normalizar_nome_fn(nome)
        produto_key = _gerar_produto_key(produto_id_raw, nome, normalizar_nome_fn)

        taxa_base = _normalizar_taxa_cdi(
            row[campos["taxa_base"]] if campos["taxa_base"] in df_carteira.columns else None,
            default=0.0,
            limite_percentual_vs_multiplicador=limite,
        )
        taxa_bonus = _normalizar_taxa_cdi(
            row[campos["taxa_bonus"]] if campos["taxa_bonus"] and campos["taxa_bonus"] in df_carteira.columns else None,
            default=0.0,
            limite_percentual_vs_multiplicador=limite,
        )

        reg = {
            "produto_key": produto_key,
            "produto_id_raw": None if produto_id_raw is None else str(produto_id_raw).strip(),
            "nome": nome,
            "nome_norm": nome_norm,
            "taxa_base_cdi": taxa_base,
            "taxa_bonus_cdi": taxa_bonus,
            "dias_bonus": _to_int_produto(row[campos["dias_bonus"]], 0) if campos["dias_bonus"] and campos["dias_bonus"] in df_carteira.columns else 0,
            "ativo": _to_bool_produto(row[campos["ativo"]], True) if campos["ativo"] and campos["ativo"] in df_carteira.columns else True,
            "tipo_produto": _normalizar_texto_produto(row[campos["tipo"]]) if campos["tipo"] and campos["tipo"] in df_carteira.columns else "",
            "indexador": _normalizar_texto_produto(row[campos["indexador"]]) if campos["indexador"] and campos["indexador"] in df_carteira.columns else "",
            "carencia_dias": _to_int_produto(row[campos["carencia_dias"]], 0) if campos["carencia_dias"] and campos["carencia_dias"] in df_carteira.columns else 0,
            "liquidez_dias": _to_int_produto(row[campos["liquidez_dias"]], 0) if campos["liquidez_dias"] and campos["liquidez_dias"] in df_carteira.columns else 0,
            "isento_ir": _to_bool_produto(row[campos["isento_ir"]], False) if campos["isento_ir"] and campos["isento_ir"] in df_carteira.columns else False,
            "aplicacao_minima": _to_float_produto(row[campos["aplicacao_minima"]], 0.0) if campos["aplicacao_minima"] and campos["aplicacao_minima"] in df_carteira.columns else 0.0,
            "aplicacao_maxima": _to_float_produto(row[campos["aplicacao_maxima"]], 0.0) if campos["aplicacao_maxima"] and campos["aplicacao_maxima"] in df_carteira.columns else 0.0,
            "fgc": _to_bool_produto(row[campos["fgc"]], False) if campos["fgc"] and campos["fgc"] in df_carteira.columns else False,
            "banco_emissor": _normalizar_texto_produto(row[campos["banco_emissor"]]) if campos["banco_emissor"] and campos["banco_emissor"] in df_carteira.columns else "",
            "risco_real": _normalizar_texto_produto(row[campos["risco_real"]]) if campos["risco_real"] and campos["risco_real"] in df_carteira.columns else "",
            "somente_combo": _to_bool_produto(row[campos["somente_combo"]], False) if campos["somente_combo"] and campos["somente_combo"] in df_carteira.columns else False,
            "produto_base": _normalizar_texto_produto(row[campos["produto_base"]]) if campos["produto_base"] and campos["produto_base"] in df_carteira.columns else "",
            "produto_bonus": _normalizar_texto_produto(row[campos["produto_bonus"]]) if campos["produto_bonus"] and campos["produto_bonus"] in df_carteira.columns else "",
            "ratio_base": _to_float_produto(row[campos["ratio_base"]], 0.0) if campos["ratio_base"] and campos["ratio_base"] in df_carteira.columns else 0.0,
            "ratio_bonus": _to_float_produto(row[campos["ratio_bonus"]], 0.0) if campos["ratio_bonus"] and campos["ratio_bonus"] in df_carteira.columns else 0.0,
            "max_usos": _to_int_produto(row[campos["max_usos"]], 0) if campos["max_usos"] and campos["max_usos"] in df_carteira.columns else 0,
        }
        registros.append(reg)

    df_carteira_norm = pd.DataFrame(registros)
    auditoria["produtos_total"] = len(df_carteira_norm)
    return df_carteira_norm, auditoria

def construir_mapa_produtos(
    df_carteira_norm,
    *,
    normalizar_nome_fn=None,
):
    """
    Constrói mapa canônico de produtos em modo sombra.
    """
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    mapa = {"by_key": {}, "by_nome_norm": {}}
    auditoria = {
        "duplicados_produto_key": [],
        "duplicados_nome_norm": [],
    }

    for _, row in df_carteira_norm.iterrows():
        produto_key = row["produto_key"]
        nome_norm = row["nome_norm"]

        registro = {
            "produto_key": produto_key,
            "nome": row["nome"],
            "nome_norm": nome_norm,
            "taxa_base_cdi": _safe_float(row["taxa_base_cdi"], 0.0),
            "taxa_bonus_cdi": _safe_float(row["taxa_bonus_cdi"], 0.0),
            "dias_bonus": _to_int_produto(row["dias_bonus"], 0),
            "ativo": bool(row["ativo"]),
            "tipo_produto": row["tipo_produto"],
            "indexador": row["indexador"],
            "carencia_dias": _to_int_produto(row["carencia_dias"], 0),
            "liquidez_dias": _to_int_produto(row["liquidez_dias"], 0),
            "isento_ir": bool(row["isento_ir"]),
            "somente_combo": bool(row["somente_combo"]),
            "produto_base": row["produto_base"],
            "produto_bonus": row["produto_bonus"],
            "ratio_base": _safe_float(row["ratio_base"], 0.0),
            "ratio_bonus": _safe_float(row["ratio_bonus"], 0.0),
            "max_usos": _to_int_produto(row["max_usos"], 0),
            "banco_emissor": row["banco_emissor"],
            "fgc": bool(row["fgc"]),
            "risco_real": row["risco_real"],
        }

        if produto_key in mapa["by_key"]:
            auditoria["duplicados_produto_key"].append(produto_key)
        mapa["by_key"][produto_key] = registro

        if nome_norm in mapa["by_nome_norm"]:
            auditoria["duplicados_nome_norm"].append(nome_norm)
        mapa["by_nome_norm"][nome_norm] = produto_key

    return mapa, auditoria

def validar_carteira_normalizada(
    df_carteira_norm,
    *,
    abortar_em_erro=False,
):
    """
    Validação mínima em modo sombra. Não aborta por padrão.
    """
    auditoria = {
        "erros": [],
        "avisos": [],
        "ok": True,
    }

    if df_carteira_norm is None or len(df_carteira_norm) == 0:
        auditoria["erros"].append("carteira_normalizada_vazia")

    if df_carteira_norm is not None and len(df_carteira_norm) > 0:
        if df_carteira_norm["produto_key"].isna().any():
            auditoria["erros"].append("produto_key_nulo")
        if df_carteira_norm["produto_key"].duplicated().any():
            auditoria["erros"].append("produto_key_duplicado")
        if df_carteira_norm["nome_norm"].isna().any():
            auditoria["erros"].append("nome_norm_nulo")
        if df_carteira_norm["nome_norm"].duplicated().any():
            auditoria["erros"].append("nome_norm_duplicado")

        try:
            invalidos = df_carteira_norm[df_carteira_norm["dias_bonus"] < 0]
            if len(invalidos) > 0:
                auditoria["avisos"].append(f"dias_bonus_negativo={len(invalidos)}")
        except Exception:
            pass

        for campo in ("carencia_dias", "liquidez_dias"):
            try:
                invalidos = df_carteira_norm[df_carteira_norm[campo] < 0]
                if len(invalidos) > 0:
                    auditoria["avisos"].append(f"{campo}_negativo={len(invalidos)}")
            except Exception:
                pass

        try:
            invalidos = df_carteira_norm[df_carteira_norm["taxa_base_cdi"].isna()]
            if len(invalidos) > 0:
                auditoria["avisos"].append(f"taxa_base_nula={len(invalidos)}")
        except Exception:
            pass

    if auditoria["erros"]:
        auditoria["ok"] = False
        if abortar_em_erro:
            raise ValueError(f"Carteira canônica inválida: {auditoria['erros']}")

    return auditoria

def projetar_investimentos_norm_legado(
    df_carteira_norm,
):
    """
    Projeta a carteira canônica para o formato legado de INVESTIMENTOS_NORM.
    NÃO substitui a estrutura atual; apenas gera INVESTIMENTOS_NORM_NEW.

    Mantém compatibilidade total com o contrato legado consumido por
    get_taxas_lote(), expondo também as chaves:
    - base
    - bonus
    - dias_bonus
    """
    investimentos = {}
    for _, row in df_carteira_norm.iterrows():
        nome_norm = row["nome_norm"]
        base = _safe_float(row["taxa_base_cdi"], 0.0)
        bonus = _safe_float(row["taxa_bonus_cdi"], 0.0)
        dias_bonus = _to_int_produto(row["dias_bonus"], 0)

        investimentos[nome_norm] = {
            "investimento": row["nome"],
            "base": base,
            "bonus": bonus,
            "dias_bonus": dias_bonus,

            "taxa_base_cdi": base,
            "taxa_bonus_cdi": bonus,
            "produto_key": row["produto_key"],
            "ativo": bool(row["ativo"]),
            "somente_combo": bool(row["somente_combo"]),
        }
    return investimentos

def comparar_investimentos_norm(
    investimentos_old: dict | None,
    investimentos_new: dict | None,
    *,
    tolerancia: float = 1e-12,
):
    """
    Compara INVESTIMENTOS_NORM legado com a projeção canônica em modo sombra.
    """
    old = investimentos_old or {}
    new = investimentos_new or {}

    chaves_old = set(old.keys())
    chaves_new = set(new.keys())

    divergencias_taxa_base = []
    divergencias_taxa_bonus = []
    divergencias_dias_bonus = []

    for k in sorted(chaves_old & chaves_new):
        vo = old.get(k, {})
        vn = new.get(k, {})

        base_old = _safe_float(vo.get("taxa_base_cdi", vo.get("base")), 0.0)
        base_new = _safe_float(vn.get("taxa_base_cdi", vn.get("base")), 0.0)
        if abs(base_old - base_new) > tolerancia:
            divergencias_taxa_base.append((k, base_old, base_new))

        bonus_old = _safe_float(vo.get("taxa_bonus_cdi", vo.get("bonus")), 0.0)
        bonus_new = _safe_float(vn.get("taxa_bonus_cdi", vn.get("bonus")), 0.0)
        if abs(bonus_old - bonus_new) > tolerancia:
            divergencias_taxa_bonus.append((k, bonus_old, bonus_new))

        dias_old = _to_int_produto(vo.get("dias_bonus"), 0)
        dias_new = _to_int_produto(vn.get("dias_bonus"), 0)
        if dias_old != dias_new:
            divergencias_dias_bonus.append((k, dias_old, dias_new))

    iguais_essenciais = (
        len(chaves_old - chaves_new) == 0 and
        len(chaves_new - chaves_old) == 0 and
        len(divergencias_taxa_base) == 0 and
        len(divergencias_taxa_bonus) == 0 and
        len(divergencias_dias_bonus) == 0
    )

    return {
        "qtd_old": len(old),
        "qtd_new": len(new),
        "chaves_somente_old": sorted(list(chaves_old - chaves_new)),
        "chaves_somente_new": sorted(list(chaves_new - chaves_old)),
        "divergencias_taxa_base": divergencias_taxa_base,
        "divergencias_taxa_bonus": divergencias_taxa_bonus,
        "divergencias_dias_bonus": divergencias_dias_bonus,
        "iguais_essenciais": iguais_essenciais,
    }

def ativar_investimentos_norm_controlado(
    investimentos_old: dict | None,
    investimentos_new: dict | None,
    *,
    usar_novo: bool = True,
):
    """Decide qual mapa será ativado inicialmente."""
    old = investimentos_old or {}
    new = investimentos_new or {}

    meta = {
        "fonte_ativa": None,
        "qtd_old": len(old),
        "qtd_new": len(new),
        "motivo": None,
    }

    if not usar_novo:
        meta["fonte_ativa"] = "old"
        meta["motivo"] = "flag_uso_novo_false"
        return old, meta

    if not isinstance(new, dict) or len(new) == 0:
        meta["fonte_ativa"] = "old"
        meta["motivo"] = "novo_indisponivel_ou_vazio"
        return old, meta

    meta["fonte_ativa"] = "new"
    meta["motivo"] = "novo_disponivel"
    return new, meta

def _comparar_reconhecimento_coluna_produto(df_lotes, col_produto, investimentos_map, *, normalizar_nome_fn=None):
    """Mede reconhecimento dos valores de uma coluna de produto contra um mapa de investimentos."""
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

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

def comparar_matching_produtos_lotes(
    df_lotes,
    investimentos_old: dict,
    investimentos_new: dict,
    *,
    normalizar_nome_fn=None,
):
    """Compara o efeito do mapa antigo vs novo no matching dos produtos dos lotes."""
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    coluna_old = selecionar_coluna_produto_lote(
        df_lotes,
        investimentos_old or {}
    )
    coluna_new = selecionar_coluna_produto_lote(
        df_lotes,
        investimentos_new or {}
    )

    metricas_old = _comparar_reconhecimento_coluna_produto(
        df_lotes,
        coluna_old,
        investimentos_old or {},
        normalizar_nome_fn=normalizar_nome_fn,
    )
    metricas_new = _comparar_reconhecimento_coluna_produto(
        df_lotes,
        coluna_new,
        investimentos_new or {},
        normalizar_nome_fn=normalizar_nome_fn,
    )

    somente_old = sorted(list(set(metricas_old["reconhecidos"]) - set(metricas_new["reconhecidos"])))
    somente_new = sorted(list(set(metricas_new["reconhecidos"]) - set(metricas_old["reconhecidos"])))

    matching_identico = (
        coluna_old == coluna_new
        and abs(metricas_old["match_rate"] - metricas_new["match_rate"]) <= 1e-12
        and metricas_old["qtd_reconhecidos"] == metricas_new["qtd_reconhecidos"]
        and len(somente_old) == 0
        and len(somente_new) == 0
    )

    return {
        "coluna_produto_old": coluna_old,
        "coluna_produto_new": coluna_new,
        "match_old": metricas_old["match_rate"],
        "match_new": metricas_new["match_rate"],
        "qtd_reconhecidos_old": metricas_old["qtd_reconhecidos"],
        "qtd_reconhecidos_new": metricas_new["qtd_reconhecidos"],
        "qtd_nao_reconhecidos_old": metricas_old["qtd_nao_reconhecidos"],
        "qtd_nao_reconhecidos_new": metricas_new["qtd_nao_reconhecidos"],
        "somente_old": somente_old,
        "somente_new": somente_new,
        "matching_identico": matching_identico,
    }

def decidir_rollback_investimentos_norm(comparacao_matching: dict) -> bool:
    """Decide se deve haver rollback local para o mapa antigo."""
    if not isinstance(comparacao_matching, dict):
        return True

    if comparacao_matching.get("coluna_produto_old") != comparacao_matching.get("coluna_produto_new"):
        return True

    match_old = _safe_float(comparacao_matching.get("match_old"), 0.0)
    match_new = _safe_float(comparacao_matching.get("match_new"), 0.0)
    if match_new + 1e-12 < match_old:
        return True

    if comparacao_matching.get("qtd_reconhecidos_new", 0) < comparacao_matching.get("qtd_reconhecidos_old", 0):
        return True

    if len(comparacao_matching.get("somente_old", [])) > 0:
        return True

    if not bool(comparacao_matching.get("matching_identico", False)):
        return True

    return False

def logar_ativacao_investimentos_norm(meta_ativacao: dict, comparacao_matching: dict | None = None, rollback: bool | None = None):
    """Loga ativação e eventual rollback do mapa de investimentos."""
    if isinstance(meta_ativacao, dict):
        print(
            "[SWAP-INVEST] "
            f"fonte_ativa_inicial={meta_ativacao.get('fonte_ativa')} "
            f"qtd_old={meta_ativacao.get('qtd_old')} "
            f"qtd_new={meta_ativacao.get('qtd_new')} "
            f"motivo={meta_ativacao.get('motivo')}"
        )

    if isinstance(comparacao_matching, dict):
        print(
            "[SWAP-INVEST] "
            f"coluna_old={comparacao_matching.get('coluna_produto_old')} "
            f"coluna_new={comparacao_matching.get('coluna_produto_new')} "
            f"match_old={comparacao_matching.get('match_old'):.3f} "
            f"match_new={comparacao_matching.get('match_new'):.3f}"
        )
        print(
            "[SWAP-INVEST] "
            f"qtd_reconhecidos_old={comparacao_matching.get('qtd_reconhecidos_old')} "
            f"qtd_reconhecidos_new={comparacao_matching.get('qtd_reconhecidos_new')} "
            f"rollback={rollback}"
        )

    if isinstance(meta_ativacao, dict) and "fonte_ativa_final" in meta_ativacao:
        print(
            "[SWAP-INVEST] "
            f"fonte_ativa_final={meta_ativacao.get('fonte_ativa_final')} "
            f"motivo_final={meta_ativacao.get('motivo_final')}"
        )

def carregar_investimentos():
    """Lê a aba configurada de carteira e retorna dicionário normalizado com as regras."""
    try:
        df = pd.read_excel(NOME_ARQUIVO_LOCAL, sheet_name=nome_aba("carteira"))
        col_nome = resolver_coluna(df, "carteira", "nome")
        col_taxa_base = resolver_coluna(df, "carteira", "taxa_base")
        col_taxa_bonus = resolver_coluna(df, "carteira", "taxa_bonus", required=False)
        col_dias_bonus = resolver_coluna(df, "carteira", "dias_bonus", required=False)

        invest = {}
        for _, row in df.iterrows():
            nome = str(row[col_nome]).strip()
            if not nome or nome.lower() in ("nan", "none"):
                continue

            bonus_raw = row.get(col_taxa_bonus) if col_taxa_bonus else None
            invest[normalizar_nome(nome)] = {
                "base": _to_cdi_multiplier(row.get(col_taxa_base), default=TAXA_BASE_DEFAULT),
                "bonus": None if (bonus_raw is None or (isinstance(bonus_raw, float) and pd.isna(bonus_raw))) else _to_cdi_multiplier(bonus_raw, default=TAXA_BONUS_DEFAULT),
                "dias_bonus": int(row[col_dias_bonus]) if col_dias_bonus and pd.notna(row.get(col_dias_bonus)) else DIAS_BONUS_DEFAULT,
                "nome_original": nome,
            }

        print(f" >>> Carregados {len(invest)} investimentos da aba {nome_aba('carteira')}.")

        investimentos_norm_new = invest
        try:
            global MAPA_PRODUTOS_CANONICO

            df_carteira = pd.read_excel(NOME_ARQUIVO_LOCAL, sheet_name=nome_aba("carteira"))
            carteira_canonica_df, _ = normalizar_carteira_bruta(
                df_carteira,
                config,
                CONTRATO_OPERACIONAL,
                normalizar_nome_fn=normalizar_nome,
            )
            MAPA_PRODUTOS_CANONICO, _ = construir_mapa_produtos(
                carteira_canonica_df,
                normalizar_nome_fn=normalizar_nome,
            )

            auditoria_validacao_carteira = validar_carteira_normalizada(
                carteira_canonica_df,
                abortar_em_erro=False,
            )
            investimentos_norm_new = projetar_investimentos_norm_legado(carteira_canonica_df)
            comparacao_investimentos_norm = comparar_investimentos_norm(invest, investimentos_norm_new)

            if DEBUG_SHADOW:
                log_debug(
                    DEBUG_SHADOW,
                    "SHADOW-CARTEIRA",
                    produtos_norm=len(carteira_canonica_df),
                    mapa_by_key=len(MAPA_PRODUTOS_CANONICO.get("by_key", {})),
                    investimentos_new=len(investimentos_norm_new),
                )
                log_debug(
                    DEBUG_SHADOW,
                    "SHADOW-CARTEIRA",
                    iguais_essenciais=comparacao_investimentos_norm.get("iguais_essenciais"),
                    somente_old=len(comparacao_investimentos_norm.get("chaves_somente_old", [])),
                    somente_new=len(comparacao_investimentos_norm.get("chaves_somente_new", [])),
                    div_base=len(comparacao_investimentos_norm.get("divergencias_taxa_base", [])),
                    div_bonus=len(comparacao_investimentos_norm.get("divergencias_taxa_bonus", [])),
                    div_dias=len(comparacao_investimentos_norm.get("divergencias_dias_bonus", [])),
                )

                avisos = auditoria_validacao_carteira.get("avisos")
                erros = auditoria_validacao_carteira.get("erros")
                if avisos:
                    print(f"[SHADOW-CARTEIRA] avisos_validacao={avisos}")
                if erros:
                    print(f"[SHADOW-CARTEIRA] erros_validacao={erros}")

        except Exception as e:
            print(f"[SHADOW-CARTEIRA] erro={e}")

        investimentos_norm_old = dict(invest) if isinstance(invest, dict) else {}
        try:
            investimentos_norm_ativo, meta_ativacao_invest = ativar_investimentos_norm_controlado(
                investimentos_norm_old,
                investimentos_norm_new,
                usar_novo=USAR_INVESTIMENTOS_NORM_NEW,
            )

            df_lotes = pd.read_excel(NOME_ARQUIVO_LOCAL, sheet_name=nome_aba("lotes"))
            comparacao_matching_lotes = comparar_matching_produtos_lotes(
                df_lotes,
                investimentos_norm_old,
                investimentos_norm_ativo,
                normalizar_nome_fn=normalizar_nome,
            )

            rollback_investimentos_norm = decidir_rollback_investimentos_norm(comparacao_matching_lotes)
            if rollback_investimentos_norm:
                investimentos_norm_ativo = investimentos_norm_old
                meta_ativacao_invest["fonte_ativa_final"] = "old"
                meta_ativacao_invest["motivo_final"] = "rollback_matching"
            else:
                meta_ativacao_invest["fonte_ativa_final"] = meta_ativacao_invest.get("fonte_ativa")
                meta_ativacao_invest["motivo_final"] = "matching_preservado"

            if DEBUG_SHADOW or rollback_investimentos_norm:
                logar_ativacao_investimentos_norm(
                    meta_ativacao_invest,
                    comparacao_matching_lotes,
                    rollback=rollback_investimentos_norm,
                )

            invest = investimentos_norm_ativo

        except Exception as e:
            try:
                if investimentos_norm_old:
                    invest = investimentos_norm_old
            except Exception:
                pass
            print(f"[SWAP-INVEST] erro={e}")
            print("[SWAP-INVEST] fonte_ativa_final=old motivo_final=erro_no_swap")

        return invest
    except Exception as e:
        print(f" >>> [AVISO] Não foi possível carregar a carteira: {e}")
        return {}

def obter_taxa_base_referencia_futura(default=None):
    """Retorna a taxa base de referência para projeções futuras.

    Prioriza o investimento de referência configurado e preserva fallback compatível.
    """
    if default is None:
        default = TAXA_BASE_REFERENCIA_FUTURA_DEFAULT

    ref_nome_norm = normalizar_nome(INVESTIMENTO_REFERENCIA_FUTURO_NOME)

    if INVESTIMENTO_REFERENCIA_FUTURO_MATCH_EXATO:
        info = INVESTIMENTOS_NORM.get(ref_nome_norm)
        if info is not None:
            try:
                return float(info.get('base', default))
            except Exception:
                return float(default)
    else:
        for nome_norm, info in INVESTIMENTOS_NORM.items():
            if ref_nome_norm and ref_nome_norm in nome_norm:
                try:
                    return float(info.get('base', default))
                except Exception:
                    return float(default)

    for nome_norm, info in INVESTIMENTOS_NORM.items():
        if 'sofisa' in nome_norm and '105' in nome_norm:
            try:
                return float(info.get('base', default))
            except Exception:
                return float(default)
    return float(default)

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

def carregar_valores_originais_lotes(nome_arquivo: str) -> dict:
    """Carrega valores originais por lote para relatórios e validações."""
    try:
        df_lotes_orig = pd.read_excel(nome_arquivo, sheet_name=nome_aba('lotes'))
        col_id = selecionar_coluna_id_lote(df_lotes_orig, contexto='aba de lotes (valores originais)')
        valores_originais = {}
        for _, row in df_lotes_orig.iterrows():
            lid = str(row[col_id]).strip()
            if not lid:
                continue
            col_valor = resolver_coluna(df_lotes_orig, 'lotes', 'valor_original')
            valores_originais[lid] = float(row[col_valor])
        print(f" -> Valores originais carregados para {len(valores_originais)} lotes.")
        return valores_originais
    except Exception as e:
        print(f"Aviso: não foi possível carregar valores originais - {e}")
        return {}

def acumular_saques_por_lote(log_movimentos):
    """Acumula saques bruto e líquido por lote a partir do log histórico."""
    total_bruto = {}
    total_liquido = {}
    for entrada in log_movimentos:
        lote_id = str(entrada.get('Lote'))
        total_bruto[lote_id] = total_bruto.get(lote_id, 0.0) + float(entrada.get('Bruto', 0.0))
        total_liquido[lote_id] = total_liquido.get(lote_id, 0.0) + float(entrada.get('Liquido', 0.0))
    return total_bruto, total_liquido

def obter_data_referencia_relatorio(data_referencia=None):
    """Retorna a data-base operacional do relatório.

    Modelo financeiro adotado:
    - o saldo atual deve refletir a posição do app bancário na data de referência
      do Brasil (America/Sao_Paulo);
    - para datas ainda não publicadas no BCB, o script já possui uma taxa futura
      de referência (TAXA_PROJ) e deve projetar esses dias úteis faltantes;
    - portanto, a data-base do relatório é a própria DATA_REFERENCIA, e não a
      penúltima/última data do mapa BCB.

    O mapa do BCB continua sendo usado sempre que existir taxa real para a data;
    nos dias úteis posteriores ao último ponto do mapa, o motor aplica TAXA_PROJ.
    """
    if data_referencia is None:
        data_referencia = DATA_REFERENCIA
    return data_referencia

def dinheiro_round(valor):
    return float(Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def ordenar_contas_processamento(contas):
    """Ordena contas de forma estável e canônica, preservando a ordem original da planilha.

    Formato aceito:
    - (data, valor, desc)
    - (data, valor, desc, ordem)
    - (data, valor, desc, lote, ordem)
    """
    def _key(c):
        data = c[0]
        valor = float(c[1]) if len(c) > 1 else 0.0
        desc = str(c[2]) if len(c) > 2 else ""
        if len(c) >= 5:
            ordem = int(c[4]) if c[4] is not None else ORDEM_PROCESSAMENTO_SENTINELA
        elif len(c) == 4 and not isinstance(c[3], str):
            ordem = int(c[3]) if c[3] is not None else ORDEM_PROCESSAMENTO_SENTINELA
        else:
            ordem = ORDEM_PROCESSAMENTO_SENTINELA
        return (data, ordem, desc, valor)
    return sorted(contas, key=_key)

def obter_data_fiscal_liquido_relatorio(data_fiscal_relatorio, data_base_fiscal):
    return max(data_base_fiscal, data_fiscal_relatorio)

def calcular_liquido_atual_relatorio(lote, saldo_bruto_atual, data_resgate_fiscal):
    dias_vida = (data_resgate_fiscal - lote.data_base_fiscal).days
    if dias_vida < 0:
        return 0.0
    iof = IOF_TABLE[dias_vida] if dias_vida < 30 else 0.0
    ir = obter_aliquota_ir(dias_vida)
    principal_base = max(min(float(getattr(lote, 'principal_remanescente', lote.valor_inicial)), saldo_bruto_atual), 0.0)
    lucro = max(saldo_bruto_atual - principal_base, 0.0)
    taxa_total = iof + (1 - iof) * ir
    imposto = dinheiro_round(lucro * taxa_total)
    liquido = dinheiro_round(max(saldo_bruto_atual - imposto, 0.0))
    return liquido

def diagnosticar_liquido_atual_relatorio(lote, saldo_bruto_atual, data_resgate_fiscal):
    dias_vida = (data_resgate_fiscal - lote.data_base_fiscal).days
    principal_base = max(min(float(getattr(lote, 'principal_remanescente', lote.valor_inicial)), saldo_bruto_atual), 0.0)
    lucro = max(saldo_bruto_atual - principal_base, 0.0)
    if dias_vida < 0:
        return {
            'dias_vida': dias_vida,
            'principal_base': dinheiro_round(principal_base),
            'lucro': dinheiro_round(lucro),
            'iof_aliquota': 0.0,
            'ir_aliquota': 0.0,
            'iof_valor_bruto': 0.0,
            'iof_valor_round': 0.0,
            'base_ir': dinheiro_round(lucro),
            'ir_valor_bruto': 0.0,
            'ir_valor_round': 0.0,
            'imposto_total': 0.0,
            'liquido_final': 0.0,
        }
    iof = IOF_TABLE[dias_vida] if dias_vida < 30 else 0.0
    ir = obter_aliquota_ir(dias_vida)
    iof_valor_bruto = lucro * iof
    iof_valor_round = dinheiro_round(iof_valor_bruto)
    base_ir = max(lucro - iof_valor_round, 0.0)
    ir_valor_bruto = base_ir * ir
    ir_valor_round = dinheiro_round(ir_valor_bruto)
    imposto_total = dinheiro_round(iof_valor_round + ir_valor_round)
    liquido_final = dinheiro_round(max(saldo_bruto_atual - imposto_total, 0.0))
    return {
        'dias_vida': dias_vida,
        'principal_base': dinheiro_round(principal_base),
        'lucro': dinheiro_round(lucro),
        'iof_aliquota': float(iof),
        'ir_aliquota': float(ir),
        'iof_valor_bruto': float(iof_valor_bruto),
        'iof_valor_round': float(iof_valor_round),
        'base_ir': dinheiro_round(base_ir),
        'ir_valor_bruto': float(ir_valor_bruto),
        'ir_valor_round': float(ir_valor_round),
        'imposto_total': float(imposto_total),
        'liquido_final': float(liquido_final),
    }

def gerar_relatorio_situacao_atual(
    estado_lotes_passado,
    log_passado,
    valores_originais,
    mapa_bcb,
    data_referencia=None,
):
    """
    Gera a aba 'Situacao Atual' apenas com o estado efetivamente realizado até a data atual.

    Importante:
    - NÃO incorpora saques futuros da estratégia vencedora;
    - usa somente o snapshot pós-passado e atualiza os lotes até a data efetiva do relatório;
    - alinha saldo bruto e saldo líquido na mesma data-base fechada.
    """
    if data_referencia is None:
        data_referencia = DATA_REFERENCIA
    data_referencia_efetiva = obter_data_referencia_relatorio(data_referencia)

    if not estado_lotes_passado:
        return pd.DataFrame()

    total_sacado_bruto_passado, total_sacado_liquido_passado = acumular_saques_por_lote(log_passado or [])
    data_corte_passado = max((x.get('Data') for x in (log_passado or []) if x.get('Data') is not None), default=None)

    relatorio = []
    diagnosticos_liquido = []
    for st in estado_lotes_passado:
        lote_id = str(st['Lote ID'])
        data_aplicacao_original = st.get('Data Aplicação', st.get('Data Base Fiscal'))
        data_base_fiscal = st.get('Data Base Fiscal', data_aplicacao_original)
        investimento_ausente_na_origem = bool(st.get('Investimento Ausente na Origem', False))
        if data_base_fiscal > data_referencia_efetiva:
            continue
        if investimento_ausente_na_origem and data_aplicacao_original == data_referencia_efetiva:
            continue

        lotex = Lote(
            lote_id,
            data_aplicacao_original,
            st['Valor Inicial'],
            data_base_fiscal=data_base_fiscal,
            fator_acumulado_inicial=float(st.get('Fator Acumulado', 1.0)),
            taxa_base_cdi=float(st.get('Taxa Base CDI', TAXA_BASE_DEFAULT)),
            taxa_bonus_cdi=float(st.get('Taxa Bonus CDI', TAXA_BONUS_DEFAULT)),
            dias_bonus=int(st.get('Dias Bonus', DIAS_BONUS_DEFAULT)),
            principal_remanescente_inicial=float(st.get('Principal Remanescente', st['Valor Inicial'])),
        )
        lotex.investimento = str(st.get('Investimento', '') or '')
        lotex.investimento_ausente_na_origem = investimento_ausente_na_origem
        lotex.saldo_bruto = max(float(st.get('Saldo Após Passado', 0.0)), 0.0)
        lotex.esgotado = lotex.saldo_bruto <= VALOR_MINIMO_LOTE_ATIVO

        investimento_norm_rel = normalizar_nome(lotex.investimento)
        produto_turbinado_norm = normalizar_nome(PRODUTO_FALLBACK_NOME_RAW)
        bonus_dias_relatorio = int(lotex.dias_bonus)
        aplicar_bonus_localizado_relatorio = (
            not lotex.esgotado
            and investimento_norm_rel == produto_turbinado_norm
            and lotex.taxa_bonus_cdi > 0.0
            and bonus_dias_relatorio > 0
        )
        if aplicar_bonus_localizado_relatorio:
            lotex.dias_bonus = bonus_dias_relatorio + 1

        # Atualiza apenas o rendimento entre o corte do passado e a data efetiva do relatório.
        if data_corte_passado is not None and data_referencia_efetiva > data_corte_passado:
            d = data_corte_passado + timedelta(days=1)
            while d <= data_referencia_efetiva:
                atualizar_saldo_lotes_no_dia([lotex], d, bcb_map=mapa_bcb, taxa_proj=TAXA_PROJ)
                d += timedelta(days=1)

        if aplicar_bonus_localizado_relatorio:
            lotex.dias_bonus = bonus_dias_relatorio

        saldo_bruto_atual = float(round(max(lotex.saldo_bruto, 0.0), 2))

        # O líquido usa a data fiscal efetiva para manter coerência com o bruto já materializado no snapshot.
        data_fiscal_relatorio = data_referencia_efetiva
        if data_corte_passado is not None and data_corte_passado > data_fiscal_relatorio:
            data_fiscal_relatorio = data_corte_passado

        data_fiscal_para_liquido = obter_data_fiscal_liquido_relatorio(
            data_fiscal_relatorio,
            data_base_fiscal
        )

        liq_atual = calcular_liquido_atual_relatorio(
            lotex,
            saldo_bruto_atual,
            data_fiscal_para_liquido
        )
        if lote_id in LOTES_MONITORADOS_LIQUIDO:
            diag = diagnosticar_liquido_atual_relatorio(lotex, saldo_bruto_atual, data_fiscal_para_liquido)
            diag.update({
                'Lote ID': lote_id,
                'Carteira': lotex.investimento or '-',
                'Data Aplicação': data_aplicacao_original,
                'Data Base Fiscal': data_base_fiscal,
                'Data Fiscal Líquido': data_fiscal_para_liquido,
                'Saldo Bruto Atual (R$)': saldo_bruto_atual,
            })
            diagnosticos_liquido.append(diag)

        val_orig = float(valores_originais.get(lote_id, st['Valor Inicial']))
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
            "Lote ID": lote_id,
            "Carteira": lotex.investimento or '-',
            "Data Aplicação": data_aplicacao_original,
            "Data Base Fiscal": data_base_fiscal,
            "Dias Corridos até Hoje": dias_hoje,
            "Dias Úteis até Hoje": dias_uteis_hoje,
            "Valor Original (R$)": dinheiro_round(val_orig),
            "Total Bruto Sacado (R$)": dinheiro_round(total_sacado),
            "Total Líquido Sacado (R$)": dinheiro_round(total_liquido_sacado),
            "Saldo Bruto Atual (R$)": saldo_bruto_atual,
            "Saldo Líquido Atual (R$)": liq_atual,
            "Patrimônio Líquido até Hoje (R$)": dinheiro_round(patrimonio_liquido_ate_hoje),
            "Rendimento Líquido Acumulado dos Lotes (R$)": dinheiro_round(rendimento_liquido_acumulado_lotes),
            "Saldo se Dinheiro Ficasse Parado (R$)": dinheiro_round(saldo_se_dinheiro_ficasse_parado),
            "Ganho da Otimização vs Dinheiro Parado (R$)": dinheiro_round(ganho_otimizacao_vs_dinheiro_parado),
            "Rentabilidade Bruta (%)": round(rent_bruta, 2),
            "Rentabilidade Líquida (%)": round(rent_liquida, 2),
            "Esgotado no Passado": bool(st.get('Esgotado no Passado', False)),
            "Taxa Base CDI (%)": round(float(st.get('Taxa Base CDI', TAXA_BASE_DEFAULT)) * 100, 0),
        })

    if not relatorio:
        return pd.DataFrame()

    df_relatorio_atual = pd.DataFrame(relatorio)
    total_row = {
        "Lote ID": "TOTAL",
        "Carteira": "",
        "Valor Original (R$)": round(df_relatorio_atual["Valor Original (R$)"].sum(), 2),
        "Total Bruto Sacado (R$)": round(df_relatorio_atual["Total Bruto Sacado (R$)"].sum(), 2),
        "Total Líquido Sacado (R$)": round(df_relatorio_atual["Total Líquido Sacado (R$)"].sum(), 2),
        "Saldo Bruto Atual (R$)": round(df_relatorio_atual["Saldo Bruto Atual (R$)"].sum(), 2),
        "Saldo Líquido Atual (R$)": round(df_relatorio_atual["Saldo Líquido Atual (R$)"].sum(), 2),
        "Patrimônio Líquido até Hoje (R$)": round(df_relatorio_atual["Patrimônio Líquido até Hoje (R$)"].sum(), 2),
        "Rendimento Líquido Acumulado dos Lotes (R$)": round(df_relatorio_atual["Rendimento Líquido Acumulado dos Lotes (R$)"].sum(), 2),
        "Saldo se Dinheiro Ficasse Parado (R$)": round(df_relatorio_atual["Saldo se Dinheiro Ficasse Parado (R$)"].sum(), 2),
        "Ganho da Otimização vs Dinheiro Parado (R$)": round(df_relatorio_atual["Ganho da Otimização vs Dinheiro Parado (R$)"].sum(), 2),
    }
    return pd.concat([df_relatorio_atual, pd.DataFrame([total_row])], ignore_index=True)

# =========================================================
# 04. CDI E CALENDÁRIO
# =========================================================
def gdrive_uc_download(file_id: str) -> str:
    return GOOGLE_DRIVE_DOWNLOAD_BASE.format(file_id=file_id)

def baixar_planilha_google():
    print(f">>> [DOWNLOAD] Iniciando download...")
    if not GOOGLE_SHEETS_FILE_ID:
        print(" -> [ERRO] GOOGLE_SHEETS_FILE_ID não definido. Crie/ajuste o arquivo config.json.")
        return False
    url_export = GOOGLE_SHEETS_EXPORT_BASE.format(file_id=GOOGLE_SHEETS_FILE_ID)
    try:
        headers = {"User-Agent": REDE_USER_AGENT_DOWNLOAD}
        response = requests.get(url_export, headers=headers, timeout=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS, verify=REDE_VERIFICAR_SSL)
        response.raise_for_status()
        with open(NOME_ARQUIVO_LOCAL, 'wb') as f:
            f.write(response.content)
        print(f" -> Sucesso! Arquivo salvo em: {NOME_ARQUIVO_LOCAL}\n")
        return True
    except Exception as e:
        print(f" -> [ERRO] Falha no download: {e}")
        return False

def baixar_fallback_bcb():
    """Baixa arquivo de fallback do Google Drive e preenche datas faltantes."""
    print(">>> [BCB FALLBACK] Baixando dados históricos do Drive...")

    if not FALLBACK_BCB_FILE_ID and not FALLBACK_BCB_URL:
        print(" -> [AVISO] FALLBACK_BCB_FILE_ID não definido no config.json. Fallback desabilitado.")
        return {}, TAXA_DIA_BASE

    url_export = FALLBACK_BCB_URL or gdrive_uc_download(FALLBACK_BCB_FILE_ID)

    try:
        headers = {"User-Agent": REDE_USER_AGENT_DOWNLOAD}
        response = requests.get(url_export, headers=headers, timeout=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS, verify=REDE_VERIFICAR_SSL)
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
            dias_preenchidos = 0

            while data_atual <= data_final:
                if data_atual not in mapa_cdi:
                    mapa_cdi[data_atual] = 1.0 + TAXA_DIA_BASE
                    dias_preenchidos += 1
                data_atual += timedelta(days=1)

            print(f" -> Fallback OK: {len(mapa_cdi)} dias totais")
            print(f"    ({len(mapa_cdi) - dias_preenchidos} do arquivo, {dias_preenchidos} preenchidos)\n")
        else:
            print(f" -> Fallback carregado: {len(mapa_cdi)} dias\n")

        return mapa_cdi, ultima_taxa

    except Exception as e:
        print(f" -> [ERRO] Falha no fallback: {e}\n")
        return {}, TAXA_DIA_BASE

def _coagir_para_date(valor):
    """Converte timestamps/datetime para date quando possível."""
    if valor is None:
        return None
    try:
        if hasattr(valor, "date"):
            return valor.date()
    except Exception:
        pass
    return valor

def extrair_metadata_serie_cdi(serie_cdi):
    """Extrai data inicial/final e quantidade de observações da série CDI."""
    meta = {"data_inicial": None, "data_final": None, "qtd_observacoes": 0}
    if serie_cdi is None:
        return meta
    try:
        if isinstance(serie_cdi, dict) and len(serie_cdi) > 0:
            datas = [_coagir_para_date(k) for k in serie_cdi.keys()]
            datas = [d for d in datas if d is not None]
            if datas:
                meta["data_inicial"] = min(datas)
                meta["data_final"] = max(datas)
                meta["qtd_observacoes"] = len(datas)
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
                    if "Data" in item:
                        datas.append(_coagir_para_date(item["Data"]))
                    elif "data" in item:
                        datas.append(_coagir_para_date(item["data"]))
            datas = [d for d in datas if d is not None]
            if datas:
                meta["data_inicial"] = min(datas)
                meta["data_final"] = max(datas)
                meta["qtd_observacoes"] = len(datas)
                return meta
    except Exception:
        pass
    try:
        if hasattr(serie_cdi, "index") and not hasattr(serie_cdi, "columns"):
            datas = [_coagir_para_date(x) for x in list(serie_cdi.index)]
            datas = [d for d in datas if d is not None]
            if datas:
                meta["data_inicial"] = min(datas)
                meta["data_final"] = max(datas)
                meta["qtd_observacoes"] = len(datas)
                return meta
    except Exception:
        pass
    try:
        if hasattr(serie_cdi, "columns") and hasattr(serie_cdi, "__len__"):
            col_data = None
            for cand in ("Data", "data", "DATE", "date"):
                if cand in serie_cdi.columns:
                    col_data = cand
                    break
            if col_data is not None and len(serie_cdi) > 0:
                datas = [_coagir_para_date(x) for x in list(serie_cdi[col_data])]
                datas = [d for d in datas if d is not None]
                if datas:
                    meta["data_inicial"] = min(datas)
                    meta["data_final"] = max(datas)
                    meta["qtd_observacoes"] = len(datas)
                    return meta
    except Exception:
        pass
    return meta

def atualizar_metadata_cdi(serie_cdi, fonte: str) -> None:
    global CDI_FONTE_UTILIZADA, CDI_DATA_FINAL_UTILIZADA
    meta = extrair_metadata_serie_cdi(serie_cdi)
    CDI_FONTE_UTILIZADA = fonte
    CDI_DATA_FINAL_UTILIZADA = meta.get("data_final")

def obter_data_corte_cdi(serie_cdi=None, fallback=None):
    global CDI_DATA_CORTE_CONGELADA
    try:
        meta = extrair_metadata_serie_cdi(serie_cdi)
        if meta.get("data_final") is not None:
            return meta["data_final"]
    except Exception:
        pass
    if CDI_DATA_CORTE_CONGELADA is not None:
        return CDI_DATA_CORTE_CONGELADA
    try:
        if Path(CACHE_BCB_FILE).exists():
            import json as _json
            with open(CACHE_BCB_FILE, 'r', encoding='utf-8') as f:
                cache_data = _json.load(f)
            mapa = cache_data.get('mapa', {})
            datas = [datetime.strptime(k, '%Y-%m-%d').date() for k in mapa.keys()]
            if datas:
                return max(datas)
    except Exception:
        pass
    return fallback

def construir_cdi_fixo_ate_data(data_inicial, data_final, taxa_diaria_padrao, calendario=None):
    """Constrói série CDI fixa SOMENTE até a data_final informada."""
    if data_inicial is None or data_final is None:
        raise ValueError("Data inicial/final inválida para construir CDI fixo.")
    if data_final < data_inicial:
        raise ValueError("data_final < data_inicial na construção do CDI fixo.")
    serie = {}
    d = data_inicial
    while d <= data_final:
        incluir = True
        try:
            if calendario is not None and hasattr(calendario, "is_working_day"):
                incluir = bool(calendario.is_working_day(d))
        except Exception:
            incluir = True
        if incluir:
            serie[d] = 1.0 + float(taxa_diaria_padrao)
        d = d + timedelta(days=1)
    return serie

def logar_metadata_cdi():
    if not DEBUG_CDI:
        return
    log_resumo(
        "CDI",
        fonte=CDI_FONTE_UTILIZADA,
        data_final=CDI_DATA_FINAL_UTILIZADA,
        corte_congelado=CDI_DATA_CORTE_CONGELADA,
    )

def obter_historico_bcb(data_inicio=None, usar_cache=True):
    global CDI_DATA_CORTE_CONGELADA
    print(">>> [BCB] Carregando histórico CDI diário...")

    if usar_cache and Path(CACHE_BCB_FILE).exists():
        try:
            with open(CACHE_BCB_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            mapa_cdi = {datetime.strptime(k, '%Y-%m-%d').date(): v
                       for k, v in cache_data['mapa'].items()}
            ultima_data_cache = max(mapa_cdi.keys())
            hoje = DATA_REFERENCIA
            if (hoje - ultima_data_cache).days <= 2:
                print(f" -> Cache válido: {len(mapa_cdi)} dias (até {ultima_data_cache})")
                print(f" -> Usando CDI DIÁRIO real para cada data\n")
                atualizar_metadata_cdi(mapa_cdi, fonte="cache_local")
                CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA
                logar_metadata_cdi()
                return mapa_cdi, cache_data['taxa_projecao']
            else:
                print(f" -> Cache desatualizado (última: {ultima_data_cache})")
                try:
                    atualizar_metadata_cdi(mapa_cdi, fonte="cache_local_desatualizado")
                    CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA
                    logar_metadata_cdi()
                except Exception:
                    pass
        except Exception as e:
            print(f" -> Cache inválido: {e}")

    if data_inicio:
        dt_query = max(data_inicio, HISTORICO_BCB_DATA_MINIMA).strftime('%d/%m/%Y')
    else:
        dt_query = HISTORICO_BCB_DATA_MINIMA_FORMATADA

    hoje_str = DATA_REFERENCIA.strftime('%d/%m/%Y')
    url = BCB_SERIE_12_URL.format(data_inicial=dt_query, data_final=hoje_str)
    headers = {"User-Agent": REDE_USER_AGENT_BCB, "Accept": REDE_ACCEPT_BCB}

    try:
        print(" -> Tentando API do BCB...")
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
            'data_atualizacao': DATA_REFERENCIA.strftime('%Y-%m-%d')
        }
        with open(CACHE_BCB_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)

        print(f" -> API BCB OK: {len(mapa_cdi)} dias carregados")
        print(f" -> Usando CDI DIÁRIO real para cada data\n")
        atualizar_metadata_cdi(mapa_cdi, fonte="bcb_api")
        CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA
        logar_metadata_cdi()
        return mapa_cdi, ultima_taxa

    except Exception as e:
        print(f" -> API BCB falhou: {e}")

        print(" -> Tentando arquivo fallback do Drive...")
        mapa_fallback, taxa_fallback = baixar_fallback_bcb()

        if mapa_fallback:
            atualizar_metadata_cdi(mapa_fallback, fonte="drive_fallback")
            CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA

            if data_inicio:
                data_atual = data_inicio
            else:
                data_atual = min(mapa_fallback.keys()) if mapa_fallback else HISTORICO_BCB_DATA_MINIMA

            data_final = obter_data_corte_cdi(mapa_fallback, fallback=DATA_REFERENCIA)
            dias_preenchidos = 0

            while data_atual <= data_final:
                if data_atual not in mapa_fallback:
                    mapa_fallback[data_atual] = 1.0 + TAXA_DIA_BASE
                    dias_preenchidos += 1
                data_atual += timedelta(days=1)

            print(f" -> Fallback + preenchimento: {len(mapa_fallback)} dias totais")
            print(f"    ({len(mapa_fallback) - dias_preenchidos} do arquivo, {dias_preenchidos} preenchidos)")
            print(f" -> Usando CDI DIÁRIO (real quando disponível, padrão quando não)\n")

            cache_data = {
                'mapa': {k.strftime('%Y-%m-%d'): v for k, v in mapa_fallback.items()},
                'taxa_projecao': taxa_fallback,
                'data_atualizacao': DATA_REFERENCIA.strftime('%Y-%m-%d'),
                'fonte': 'fallback+preenchimento'
            }
            with open(CACHE_BCB_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)

            atualizar_metadata_cdi(mapa_fallback, fonte="drive_fallback_preenchido")
            logar_metadata_cdi()
            return mapa_fallback, taxa_fallback

        data_final_fixa = obter_data_corte_cdi(fallback=None)
        if data_final_fixa is None:
            raise ValueError(
                "Não foi possível determinar a data terminal do CDI para fallback fixo comparável."
            )

        data_inicial_fixa = data_inicio if data_inicio else HISTORICO_BCB_DATA_MINIMA
        calendario = None
        try:
            calendario = Brazil()
        except Exception:
            calendario = None

        mapa_fixo = construir_cdi_fixo_ate_data(
            data_inicial=data_inicial_fixa,
            data_final=data_final_fixa,
            taxa_diaria_padrao=TAXA_DIA_BASE,
            calendario=calendario,
        )
        atualizar_metadata_cdi(mapa_fixo, fonte="taxa_fixa_fallback")
        if CDI_DATA_CORTE_CONGELADA is None:
            CDI_DATA_CORTE_CONGELADA = CDI_DATA_FINAL_UTILIZADA

        print(f" -> Usando taxa fixa padrão SOMENTE até a data terminal congelada\n")
        logar_metadata_cdi()
        return mapa_fixo, TAXA_DIA_BASE

# =========================================================
# calendário
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

def gerar_dias_sem_rendimento_bancario(
    ano_ini=CALENDARIO_ANO_INICIO_DIAS_SEM_RENDIMENTO,
    ano_fim=CALENDARIO_ANO_FIM_DIAS_SEM_RENDIMENTO,
):
    dias = set()
    for ano in range(ano_ini, ano_fim + 1):
        pascoa = _calcular_pascoa(ano)
        terca_carnaval = pascoa - timedelta(days=47)
        dias.update([terca_carnaval])
    return dias

DIAS_SEM_RENDIMENTO_BANCARIO = gerar_dias_sem_rendimento_bancario()

def is_dia_rendimento(data_atual, bcb_map=None):
    if data_atual in DIAS_SEM_RENDIMENTO_BANCARIO:
        return False
    if bcb_map:
        try:
            max_bcb = max(bcb_map.keys())
            if data_atual <= max_bcb:
                return data_atual in bcb_map
        except Exception:
            pass
    return cal.is_working_day(data_atual)

def contar_dias_rendimento(data_inicio, data_fim, bcb_map=None):
    if data_fim <= data_inicio:
        return 0
    dias = 0
    d = data_inicio + timedelta(days=1)
    while d <= data_fim:
        if is_dia_rendimento(d, bcb_map):
            dias += 1
        d += timedelta(days=1)
    return dias

# =========================================================
# 05. DADOS OPERACIONAIS E REPLAY DO PASSADO
# =========================================================

def extrair_lote_usado_unico(row, nome_coluna=None):
    """
    Extrai um único lote usado de uma linha do Excel.
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

def simular_passado(aportes_raw, contas_pagas, bcb_map, taxa_proj):
    """
    Simula os pagamentos passados para ajustar os saldos dos lotes.
    Retorna:
      - novos_aportes: lotes remanescentes para simulação futura
      - log_passado: extrato dos saques passados
      - estado_lotes_passado: snapshot de TODOS os lotes após contas pagas
    """
    if not aportes_raw or not contas_pagas:
        return aportes_raw, [], []

    print(">>> [SIMULAÇÃO PASSADO] Processando contas pagas...")

    aportes_ordenados = sorted(aportes_raw, key=lambda x: x[0])
    data_inicial = aportes_ordenados[0][0]
    data_final = max(c[0] for c in contas_pagas)

    lotes = []
    for x in aportes_ordenados:
        meta = x[3] if len(x) > 3 and isinstance(x[3], dict) else {}
        lotes.append(criar_lote_de_aporte(x[0], x[1], x[2], meta))

    lotes_por_id = {l.id: l for l in lotes}
    contas_pagas_ordenadas = ordenar_contas_processamento(contas_pagas)

    data_atual = data_inicial
    contas_processadas = 0
    log_passado = []
    evento_financeiro_global = 1

    while data_atual <= data_final:
        atualizar_saldo_lotes_no_dia(lotes, data_atual, bcb_map=bcb_map, taxa_proj=taxa_proj)

        contas_hoje = [c for c in contas_pagas_ordenadas if c[0] == data_atual]
        for conta in contas_hoje:
            _, valor_conta, desc, lote_usado, ordem_processamento = conta
            sequencia_saque = 1
            if not lote_usado:
                continue

            l = lotes_por_id.get(lote_usado)
            if not l or l.esgotado:
                contas_processadas += 1
                continue

            movimento = executar_saque_lote(l, valor_conta, data_atual)
            if movimento is None:
                contas_processadas += 1
                continue

            log_passado.append(montar_log_movimento_lote(
                movimento, data_atual, desc, bcb_map=bcb_map,
                ordem_processamento=ordem_processamento, sequencia_saque=sequencia_saque,
                evento_financeiro=evento_financeiro_global
            ))
            sequencia_saque += 1
            evento_financeiro_global += 1
            contas_processadas += 1
        data_atual += timedelta(days=1)

    novos_aportes = []
    for l in lotes:
        if l.saldo_bruto <= VALOR_MINIMO_LOTE_ATIVO:
            continue
        novos_aportes.append(serializar_lote_remanescente(l, data_final))

    estado_lotes_passado = []
    for l in lotes:
        estado_lotes_passado.append({
            'Lote ID': l.id,
            'Data Aplicação': l.data_aplicacao,
            'Data Base Fiscal': l.data_base_fiscal,
            'Valor Inicial': float(l.valor_inicial),
            'Saldo Após Passado': float(round(l.saldo_bruto, 2)),
            'Fator Acumulado': float(l.fator_acumulado),
            'Esgotado no Passado': bool(l.esgotado),
            'Vezes Usado no Passado': int(l.vezes_usado),
            'Total Sacado no Passado': float(round(l.total_bruto_sacado, 2)),
            'Taxa Base CDI': float(l.taxa_base_cdi),
            'Taxa Bonus CDI': float(l.taxa_bonus_cdi),
            'Dias Bonus': int(l.dias_bonus),
            'Principal Remanescente': float(getattr(l, 'principal_remanescente', l.valor_inicial)),
            'Investimento': str(getattr(l, 'investimento', '') or ''),
        })

    print(f" -> {contas_processadas} contas processadas")
    print(f" -> {len(novos_aportes)} lotes remanescentes | {len(estado_lotes_passado)} lotes no snapshot\n")
    return novos_aportes, log_passado, estado_lotes_passado

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

def _resolver_produto_lote_shadow(valor_produto, mapa_produtos, *, normalizar_nome_fn=None):
    """
    Resolve o produto do lote contra o mapa canônico ativo.
    """
    if normalizar_nome_fn is None:
        normalizar_nome_fn = lambda x: str(x).strip().lower()

    vazio = {
        'produto_key': None,
        'produto_nome': None,
        'produto_nome_norm': None,
        'produto_encontrado': False,
        'tipo_match_produto': 'vazio',
    }

    if valor_produto is None and not PRODUTO_FALLBACK_NOME_RAW:
        return vazio

    placeholder_produto = _eh_produto_lote_ausente(valor_produto)
    s = _resolver_nome_produto_lote_efetivo(valor_produto)
    if not s:
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
            'tipo_match_produto': 'fallback_config' if placeholder_produto else 'chave_exata',
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
            'tipo_match_produto': 'fallback_config' if placeholder_produto else 'nome_norm',
        }

    return {
        'produto_key': None,
        'produto_nome': s,
        'produto_nome_norm': nome_norm,
        'produto_encontrado': False,
        'tipo_match_produto': 'nao_encontrado',
    }

# =========================================================
# 06. SWITCHING SHADOW E RECONCILIAÇÃO
# =========================================================
def normalizar_lotes_brutos(
    df_lotes,
    mapa_produtos,
    *,
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
    col_produto = selecionar_coluna_produto_lote(df_lotes, INVESTIMENTOS_NORM)
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

# =========================================================
# switching em modo sombra
# =========================================================

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

def comparar_remanescente_legado_vs_shadow(estado_lotes_passado_legado, df_estado_pos_passado_shadow):
    """
    Compara o remanescente legado pós-passado com o remanescente sombra.
    A comparação estrutural é aproximada via lote_origem_id.
    """
    legado_reg = []
    for item in (estado_lotes_passado_legado or []):
        try:
            lote_id = _normalizar_lote_id(item.get('Lote ID'))
            saldo = _safe_float(item.get('Saldo Após Passado'), 0.0)
            if saldo > 1e-9:
                legado_reg.append({'lote_id': lote_id, 'saldo': saldo})
        except Exception:
            continue

    df_shadow = df_estado_pos_passado_shadow.copy() if df_estado_pos_passado_shadow is not None else pd.DataFrame([])
    if len(df_shadow) > 0:
        df_shadow = df_shadow[(pd.to_numeric(df_shadow.get('saldo_atual'), errors='coerce').fillna(0.0) > 1e-9) & (df_shadow.get('status') == 'ativo')].copy()
    shadow_reg = []
    if len(df_shadow) > 0:
        for _, row in df_shadow.iterrows():
            shadow_reg.append({
                'lote_tecnico_id': row.get('lote_tecnico_id'),
                'lote_origem_id': _normalizar_lote_id(row.get('lote_origem_id')),
                'saldo': _safe_float(row.get('saldo_atual'), 0.0),
                'origem': row.get('origem'),
            })

    ids_legado = {r['lote_id'] for r in legado_reg if r['lote_id'] is not None}
    ids_shadow = {r['lote_origem_id'] for r in shadow_reg if r['lote_origem_id'] is not None}
    switch_shadow = [r for r in shadow_reg if r.get('origem') == 'switch_in']

    return {
        'qtd_legado': len(legado_reg),
        'qtd_shadow': len(shadow_reg),
        'soma_legado': sum(r['saldo'] for r in legado_reg),
        'soma_shadow': sum(r['saldo'] for r in shadow_reg),
        'delta_qtd': len(shadow_reg) - len(legado_reg),
        'delta_soma': sum(r['saldo'] for r in shadow_reg) - sum(r['saldo'] for r in legado_reg),
        'ids_origem_somente_legado': sorted(list(ids_legado - ids_shadow)),
        'ids_origem_somente_shadow': sorted(list(ids_shadow - ids_legado)),
        'qtd_lotes_switch_no_shadow': len(switch_shadow),
        'soma_lotes_switch_no_shadow': sum(r['saldo'] for r in switch_shadow),
    }


def resolver_destino_switch_v1(produto_atual, investimentos_norm, config, *, normalizar_nome_fn=None):
    if normalizar_nome_fn is None:
        normalizar_nome_fn = normalizar_nome

    defaults_cfg = (config or {}).get("defaults", {}) if isinstance(config, dict) else {}
    destino_raw = str(defaults_cfg.get("investimento_referencia_futuro", "") or "").strip()
    match_exato = bool(defaults_cfg.get("investimento_referencia_futuro_match_exato", True))

    if not destino_raw:
        return {
            "produto_destino_recomendado": None,
            "produto_destino_key": None,
            "destino_info": None,
            "motivo_indisponibilidade": "destino_nao_configurado",
            "destino_igual_ao_atual": False,
        }

    destino_norm = normalizar_nome_fn(destino_raw)
    info_dest = None
    if match_exato:
        info_dest = (investimentos_norm or {}).get(destino_norm)
    else:
        for nome_norm, info in (investimentos_norm or {}).items():
            if destino_norm and destino_norm in str(nome_norm):
                info_dest = info
                break

    if info_dest is None:
        return {
            "produto_destino_recomendado": destino_raw,
            "produto_destino_key": None,
            "destino_info": None,
            "motivo_indisponibilidade": "destino_nao_encontrado",
            "destino_igual_ao_atual": False,
        }

    atual_norm = normalizar_nome_fn(produto_atual)
    destino_igual = bool(atual_norm and atual_norm == normalizar_nome_fn(info_dest.get("investimento", destino_raw)))

    return {
        "produto_destino_recomendado": info_dest.get("investimento", destino_raw),
        "produto_destino_key": info_dest.get("produto_key"),
        "destino_info": info_dest,
        "motivo_indisponibilidade": "",
        "destino_igual_ao_atual": destino_igual,
    }


def estimar_patrimonio_switch_v1(
    saldo_inicial,
    taxa_base_cdi,
    taxa_bonus_cdi,
    dias_bonus_restantes,
    horizonte_dias,
    mapa_bcb,
    data_referencia,
):
    saldo = float(max(_safe_float(saldo_inicial, 0.0), 0.0))
    horizonte_dias = int(max(_safe_float(horizonte_dias, 0), 0))
    if saldo <= 0.0 or horizonte_dias <= 0:
        return dinheiro_round(saldo)

    dias_bonus_restantes = int(max(_safe_float(dias_bonus_restantes, 0), 0))
    taxa_base_cdi = float(_safe_float(taxa_base_cdi, 0.0))
    taxa_bonus_cdi = float(_safe_float(taxa_bonus_cdi, 0.0))

    for offset in range(1, horizonte_dias + 1):
        d = data_referencia + timedelta(days=offset)
        if not is_dia_rendimento(d, mapa_bcb):
            continue
        taxa_dia = _safe_float(mapa_bcb.get(d), 1.0 + TAXA_PROJ) - 1.0 if mapa_bcb else TAXA_PROJ
        em_bonus = taxa_bonus_cdi > 0.0 and offset <= dias_bonus_restantes
        mult = taxa_bonus_cdi if em_bonus else taxa_base_cdi
        fator_dia = (1.0 + taxa_dia) ** mult
        saldo = dinheiro_round(saldo * fator_dia)

    return dinheiro_round(saldo)


def _switch_info_produto(info, nome_padrao):
    info = info or {}
    nome_produto = str(info.get("investimento") or info.get("nome_original") or nome_padrao or "").strip()
    produto_key = info.get("produto_key")
    nome_norm = normalizar_nome(nome_produto or nome_padrao)

    meta_canonica = {}
    try:
        mapa = MAPA_PRODUTOS_CANONICO or {}
        if produto_key and isinstance(mapa.get("by_key"), dict):
            meta_canonica = mapa.get("by_key", {}).get(produto_key) or {}
        if (not meta_canonica) and nome_norm and isinstance(mapa.get("by_nome_norm"), dict):
            meta_canonica = mapa.get("by_nome_norm", {}).get(nome_norm) or {}
    except Exception:
        meta_canonica = {}

    base = float(_safe_float(info.get("base", meta_canonica.get("taxa_base_cdi", TAXA_BASE_DEFAULT)), TAXA_BASE_DEFAULT))
    bonus = float(_safe_float(info.get("bonus", meta_canonica.get("taxa_bonus_cdi", 0.0)), 0.0))
    dias_bonus = int(max(_safe_float(info.get("dias_bonus", meta_canonica.get("dias_bonus", 0)), 0), 0))
    indexador = str(
        info.get("indexador")
        or meta_canonica.get("indexador")
        or ""
    ).strip()
    tipo_produto = str(
        info.get("tipo_produto")
        or meta_canonica.get("tipo_produto")
        or ""
    ).strip()

    return {
        "produto": nome_produto,
        "produto_key": produto_key or meta_canonica.get("produto_key"),
        "nome_norm": nome_norm,
        "base": base,
        "bonus": bonus,
        "dias_bonus": dias_bonus,
        "ativo": bool(info.get("ativo", meta_canonica.get("ativo", True))),
        "somente_combo": bool(info.get("somente_combo", meta_canonica.get("somente_combo", False))),
        "aplicacao_minima": float(max(_safe_float(info.get("aplicacao_minima", meta_canonica.get("aplicacao_minima", 0.0)), 0.0), 0.0)),
        "aplicacao_maxima": float(max(_safe_float(info.get("aplicacao_maxima", meta_canonica.get("aplicacao_maxima", 0.0)), 0.0), 0.0)),
        "indexador": indexador,
        "tipo_produto": tipo_produto,
        "destino_info": info,
        "meta_canonica": meta_canonica,
    }


def _switch_indexador_suportado(meta):
    meta = meta or {}
    indexador = str(meta.get("indexador") or "").strip().lower()
    nome = str(meta.get("produto") or "").strip().lower()
    tipo_produto = str(meta.get("tipo_produto") or "").strip().lower()
    base = float(_safe_float(meta.get("base"), 0.0))
    bonus = float(_safe_float(meta.get("bonus"), 0.0))

    tokens_nao_suportados = ("ipca", "prefix", "pré", "pre", "selic")
    if any(tok in indexador for tok in tokens_nao_suportados):
        return False, f"indexador_nao_suportado:{indexador or 'vazio'}"
    if any(tok in nome for tok in tokens_nao_suportados):
        return False, "produto_nao_suportado_pela_projecao_atual"
    if any(tok in tipo_produto for tok in tokens_nao_suportados):
        return False, f"tipo_produto_nao_suportado:{tipo_produto or 'vazio'}"

    if base <= 0.0:
        return False, "taxa_base_invalida"
    if base > 5.0 or bonus > 5.0:
        return False, "taxa_fora_escala_cdi"

    if indexador and ("cdi" not in indexador and "di" not in indexador):
        return False, f"indexador_nao_cdi:{indexador}"

    return True, "ok"


def _classificar_origem_recurso_switch(row, data_referencia=None):
    dias_corridos = int(_safe_float(row.get("Dias Corridos até Hoje"), 0))
    saldo_liquido = dinheiro_round(_safe_float(row.get("Saldo Líquido Atual (R$)"), 0.0))
    saldo_bruto = dinheiro_round(_safe_float(row.get("Saldo Bruto Atual (R$)"), 0.0))
    total_liquido_sacado = dinheiro_round(_safe_float(row.get("Total Líquido Sacado (R$)"), 0.0))
    data_aplicacao = _normalizar_data_lote(row.get("Data Aplicação"))

    caixa_disponivel = (
        saldo_liquido > 0.0
        and saldo_bruto > 0.0
        and total_liquido_sacado <= 1e-9
        and (
            dias_corridos <= 0
            or (data_referencia is not None and data_aplicacao is not None and data_aplicacao >= data_referencia)
        )
    )
    return "caixa_disponivel" if caixa_disponivel else "lote_investido"


def listar_destinos_elegiveis_switch_v2(
    produto_atual,
    valor_aporte,
    investimentos_norm,
    *,
    normalizar_nome_fn=None,
    excluir_produto_atual=True,
):
    if normalizar_nome_fn is None:
        normalizar_nome_fn = normalizar_nome

    valor_aporte = float(max(_safe_float(valor_aporte, 0.0), 0.0))
    atual_norm = normalizar_nome_fn(produto_atual)
    destinos = []

    for nome_norm, info in (investimentos_norm or {}).items():
        meta = _switch_info_produto(info, nome_norm)
        nome_produto = meta["produto"]
        destino_norm = normalizar_nome_fn(nome_produto)

        if not nome_produto:
            continue
        if excluir_produto_atual and atual_norm and destino_norm == atual_norm:
            continue
        if not meta["ativo"]:
            continue
        if meta["somente_combo"]:
            continue
        if meta["aplicacao_minima"] > 0 and valor_aporte + 1e-9 < meta["aplicacao_minima"]:
            continue
        if meta["aplicacao_maxima"] > 0 and valor_aporte - 1e-9 > meta["aplicacao_maxima"]:
            continue

        suportado, motivo_suporte = _switch_indexador_suportado(meta)
        if not suportado:
            continue
        meta["motivo_suporte"] = motivo_suporte
        destinos.append(meta)

    return destinos


def escolher_melhor_destino_switch_v2(
    produto_atual,
    valor_aporte,
    patrimonio_referencia,
    horizonte_analise_dias,
    investimentos_norm,
    mapa_bcb,
    data_referencia,
    *,
    normalizar_nome_fn=None,
    excluir_produto_atual=True,
):
    if normalizar_nome_fn is None:
        normalizar_nome_fn = normalizar_nome

    destinos = listar_destinos_elegiveis_switch_v2(
        produto_atual,
        valor_aporte,
        investimentos_norm,
        normalizar_nome_fn=normalizar_nome_fn,
        excluir_produto_atual=excluir_produto_atual,
    )

    if not destinos:
        return {
            "produto_destino_recomendado": None,
            "produto_destino_key": None,
            "destino_info": None,
            "motivo_indisponibilidade": "nenhum_destino_elegivel",
            "destino_igual_ao_atual": False,
            "n_destinos_avaliados": 0,
            "patrimonio_destino": dinheiro_round(valor_aporte),
            "ganho_switch": dinheiro_round(valor_aporte - patrimonio_referencia),
            "ganho_pct": 0.0,
            "ganho_diario": 0.0,
            "criterio_escolha_destino": "sem_candidatos",
        }

    melhor = None
    for candidato in destinos:
        patrimonio_candidato = estimar_patrimonio_switch_v1(
            valor_aporte,
            candidato["base"],
            candidato["bonus"],
            candidato["dias_bonus"],
            horizonte_analise_dias,
            mapa_bcb,
            data_referencia,
        )
        ganho_candidato = dinheiro_round(patrimonio_candidato - patrimonio_referencia)
        ganho_pct = round((ganho_candidato / patrimonio_referencia), 6) if patrimonio_referencia > 0 else 0.0
        ganho_diario = ganho_candidato / horizonte_analise_dias if horizonte_analise_dias > 0 else 0.0

        cand = dict(candidato)
        cand.update({
            "patrimonio_destino": patrimonio_candidato,
            "ganho_switch": ganho_candidato,
            "ganho_pct": ganho_pct,
            "ganho_diario": ganho_diario,
        })

        if melhor is None:
            melhor = cand
            continue

        chave_nova = (
            dinheiro_round(cand["patrimonio_destino"]),
            dinheiro_round(cand["ganho_switch"]),
            cand["base"],
            cand["dias_bonus"],
            cand["produto"],
        )
        chave_melhor = (
            dinheiro_round(melhor["patrimonio_destino"]),
            dinheiro_round(melhor["ganho_switch"]),
            melhor["base"],
            melhor["dias_bonus"],
            melhor["produto"],
        )
        if chave_nova > chave_melhor:
            melhor = cand

    atual_norm = normalizar_nome_fn(produto_atual)
    destino_norm = normalizar_nome_fn(melhor["produto"])
    return {
        "produto_destino_recomendado": melhor["produto"],
        "produto_destino_key": melhor.get("produto_key"),
        "destino_info": melhor.get("destino_info") or {},
        "motivo_indisponibilidade": "",
        "destino_igual_ao_atual": bool(excluir_produto_atual and atual_norm and destino_norm == atual_norm),
        "n_destinos_avaliados": len(destinos),
        "patrimonio_destino": dinheiro_round(melhor["patrimonio_destino"]),
        "ganho_switch": dinheiro_round(melhor["ganho_switch"]),
        "ganho_pct": float(melhor["ganho_pct"]),
        "ganho_diario": float(melhor["ganho_diario"]),
        "criterio_escolha_destino": "maior_patrimonio_estimado",
    }


def calcular_pressao_caixa_curto_prazo_v1(contas_exec, data_referencia, config):
    sim_cfg = (config or {}).get("simulacao", {}) if isinstance(config, dict) else {}
    horizonte_min = int(_safe_float(sim_cfg.get("horizonte_minimo_dias", 30), 30))
    data_limite = data_referencia + timedelta(days=horizonte_min)
    necessidade = 0.0

    for conta in contas_exec or []:
        try:
            data_conta = _normalizar_data_lote(conta[0]) if len(conta) > 0 else None
            valor_conta = _safe_float(conta[1], 0.0) if len(conta) > 1 else 0.0
        except Exception:
            continue
        if data_conta is None or data_conta < data_referencia or data_conta > data_limite:
            continue
        necessidade += max(valor_conta, 0.0)

    return dinheiro_round(necessidade)


def aplicar_bloqueio_pagamento_proximo_v1(df_switch_diag, necessidade_curto_prazo):
    if df_switch_diag is None or len(df_switch_diag) == 0:
        return pd.DataFrame()

    df = df_switch_diag.copy()
    df["bloqueado_por_pagamento_proximo"] = False
    if "motivo_bloqueio" not in df.columns:
        df["motivo_bloqueio"] = ""

    necessidade = float(max(_safe_float(necessidade_curto_prazo, 0.0), 0.0))
    if necessidade <= 1e-9:
        return df

    cols_ord = ["custo_fiscal_saida", "dias_para_cliff_ir", "saldo_liquido_atual"]
    for c in cols_ord:
        if c not in df.columns:
            df[c] = 0.0

    candidatos = df[df["saldo_liquido_atual"] > 0].sort_values(
        by=["custo_fiscal_saida", "dias_para_cliff_ir", "saldo_liquido_atual"],
        ascending=[True, True, False],
        kind="mergesort",
    )

    acumulado = 0.0
    for idx, row in candidatos.iterrows():
        if acumulado >= necessidade:
            break
        df.at[idx, "bloqueado_por_pagamento_proximo"] = True
        motivo = str(df.at[idx, "motivo_bloqueio"] or "").strip()
        motivo_extra = "necessario_para_curto_prazo"
        df.at[idx, "motivo_bloqueio"] = f"{motivo}; {motivo_extra}".strip("; ").strip()
        acumulado += _safe_float(row.get("saldo_liquido_atual"), 0.0)

    return df


def gerar_switch_diagnostico(
    df_situacao_atual,
    contas_exec,
    investimentos_norm,
    mapa_bcb,
    data_referencia,
    config,
):
    if df_situacao_atual is None or len(df_situacao_atual) == 0:
        return pd.DataFrame()

    sim_cfg = (config or {}).get("simulacao", {}) if isinstance(config, dict) else {}
    horizonte_analise_dias = int(_safe_float(sim_cfg.get("horizonte_alocacao_dias", HORIZONTE_PROJECAO_DIAS), HORIZONTE_PROJECAO_DIAS))
    registros = []

    df_base = df_situacao_atual.copy()
    if "Lote ID" in df_base.columns:
        df_base = df_base[df_base["Lote ID"].astype(str).str.upper() != "TOTAL"].copy()
    if "Saldo Bruto Atual (R$)" in df_base.columns:
        df_base = df_base[pd.to_numeric(df_base["Saldo Bruto Atual (R$)"], errors="coerce").fillna(0.0) > 0].copy()

    if len(df_base):
        df_base["origem_recurso"] = df_base.apply(lambda row: _classificar_origem_recurso_switch(row, data_referencia=data_referencia), axis=1)
        df_base = df_base[df_base["origem_recurso"] != "caixa_disponivel"].copy()

    for _, row in df_base.iterrows():
        lote_id = str(row.get("Lote ID", "")).strip()
        origem_recurso = str(row.get("origem_recurso", "lote_investido") or "lote_investido").strip()
        produto_atual = str(row.get("Carteira", "") or "").strip()
        saldo_bruto_atual = dinheiro_round(_safe_float(row.get("Saldo Bruto Atual (R$)"), 0.0))
        saldo_liquido_atual = dinheiro_round(_safe_float(row.get("Saldo Líquido Atual (R$)"), 0.0))
        data_aplicacao = _normalizar_data_lote(row.get("Data Aplicação"))
        data_base_fiscal = _normalizar_data_lote(row.get("Data Base Fiscal"))
        dias_corridos = int(_safe_float(row.get("Dias Corridos até Hoje"), 0))
        dias_uteis = int(_safe_float(row.get("Dias Úteis até Hoje"), 0))
        valor_original = dinheiro_round(_safe_float(row.get("Valor Original (R$)"), 0.0))
        total_liquido_sacado = dinheiro_round(_safe_float(row.get("Total Líquido Sacado (R$)"), 0.0))

        produto_norm = normalizar_nome(produto_atual)
        info_atual = (investimentos_norm or {}).get(produto_norm)
        if info_atual:
            taxa_atual_base_raw = _safe_float(info_atual.get("base"), TAXA_BASE_DEFAULT)
            taxa_atual_bonus_raw = _safe_float(info_atual.get("bonus"), 0.0)
            dias_bonus_total = int(_safe_float(info_atual.get("dias_bonus"), 0))
        else:
            taxa_atual_base_raw, taxa_atual_bonus_raw, dias_bonus_total = get_taxas_lote(produto_atual)

        dias_bonus_restantes = max(dias_bonus_total - dias_corridos, 0)
        custo_fiscal_saida = dinheiro_round(max(saldo_bruto_atual - saldo_liquido_atual, 0.0))
        imposto_estimado_saida = custo_fiscal_saida
        fator_liquido_saida = round((saldo_liquido_atual / saldo_bruto_atual), 6) if saldo_bruto_atual > 0 else 0.0
        dias_para_cliff_ir = int(distancia_proximo_cliff_ir(dias_corridos))
        em_janela_iof = bool(dias_corridos < 30)

        patrimonio_manter = estimar_patrimonio_switch_v1(
            saldo_bruto_atual,
            taxa_atual_base_raw,
            taxa_atual_bonus_raw,
            dias_bonus_restantes,
            horizonte_analise_dias,
            mapa_bcb,
            data_referencia,
        )

        destino = escolher_melhor_destino_switch_v2(
            produto_atual,
            saldo_liquido_atual,
            patrimonio_manter,
            horizonte_analise_dias,
            investimentos_norm,
            mapa_bcb,
            data_referencia,
            normalizar_nome_fn=normalizar_nome,
            excluir_produto_atual=True,
        )
        info_dest = destino.get("destino_info") or {}
        taxa_dest_base_raw = _safe_float(info_dest.get("base"), 0.0)
        taxa_dest_bonus_raw = _safe_float(info_dest.get("bonus"), 0.0)
        dias_bonus_dest = int(_safe_float(info_dest.get("dias_bonus"), 0))
        patrimonio_switch = dinheiro_round(destino.get("patrimonio_destino", saldo_liquido_atual))
        ganho_switch = dinheiro_round(destino.get("ganho_switch", patrimonio_switch - patrimonio_manter))
        ganho_pct = round(_safe_float(destino.get("ganho_pct"), 0.0), 6) if patrimonio_manter > 0 else 0.0
        ganho_diario = _safe_float(destino.get("ganho_diario"), 0.0)
        dias_payback = round((custo_fiscal_saida / ganho_diario), 2) if ganho_diario > 1e-12 else float("inf")

        motivo_bloqueio = ""
        elegivel_preliminar = True
        motivo_decisao = ""

        if not destino.get("produto_destino_recomendado"):
            elegivel_preliminar = False
            motivo_decisao = destino.get("motivo_indisponibilidade") or "destino_indisponivel"
        elif destino.get("destino_igual_ao_atual"):
            elegivel_preliminar = False
            motivo_decisao = "produto_destino_igual_ao_atual"
        elif em_janela_iof:
            elegivel_preliminar = False
            motivo_bloqueio = "janela_iof"
            motivo_decisao = "bloqueado_fiscal_curto_prazo"
        elif ganho_switch <= 0:
            elegivel_preliminar = False
            motivo_decisao = "ganho_liquido_nao_positivo"
        elif dias_payback > horizonte_analise_dias:
            elegivel_preliminar = False
            motivo_decisao = "payback_fora_do_horizonte"
        elif dias_bonus_restantes > 0 and ganho_switch <= max(custo_fiscal_saida, 0.01):
            elegivel_preliminar = False
            motivo_bloqueio = "bonus_atual_ainda_relevante"
            motivo_decisao = "bloqueado_bonus_atual"

        registros.append({
            "lote_id": lote_id,
            "origem_recurso": origem_recurso,
            "produto_atual": produto_atual,
            "produto_destino_recomendado": destino.get("produto_destino_recomendado"),
            "produto_destino_key": destino.get("produto_destino_key"),
            "n_destinos_avaliados": int(_safe_float(destino.get("n_destinos_avaliados"), 0)),
            "criterio_escolha_destino": destino.get("criterio_escolha_destino") or "maior_patrimonio_estimado",
            "data_aplicacao": data_aplicacao,
            "data_base_fiscal": data_base_fiscal,
            "dias_corridos_ate_hoje": dias_corridos,
            "dias_uteis_ate_hoje": dias_uteis,
            "valor_original": valor_original,
            "total_liquido_sacado": total_liquido_sacado,
            "saldo_bruto_atual": saldo_bruto_atual,
            "saldo_liquido_atual": saldo_liquido_atual,
            "imposto_estimado_saida": imposto_estimado_saida,
            "custo_fiscal_saida": custo_fiscal_saida,
            "fator_liquido_saida": fator_liquido_saida,
            "dias_para_cliff_ir": dias_para_cliff_ir,
            "em_janela_iof": em_janela_iof,
            "taxa_atual_base": round(taxa_atual_base_raw * 100, 4),
            "taxa_atual_bonus": round(taxa_atual_bonus_raw * 100, 4),
            "dias_bonus_restantes": dias_bonus_restantes,
            "taxa_destino_base": round(taxa_dest_base_raw * 100, 4),
            "taxa_destino_bonus": round(taxa_dest_bonus_raw * 100, 4),
            "dias_bonus_destino": dias_bonus_dest,
            "horizonte_analise_dias": horizonte_analise_dias,
            "patrimonio_estimado_manter_horizonte": patrimonio_manter,
            "patrimonio_estimado_switch_horizonte": patrimonio_switch,
            "ganho_liquido_estimado_switch": ganho_switch,
            "ganho_percentual_estimado_switch": ganho_pct,
            "ganho_diario_incremental_estimado": dinheiro_round(ganho_diario),
            "dias_payback_switch": None if dias_payback == float("inf") else dias_payback,
            "bloqueado_por_pagamento_proximo": False,
            "motivo_bloqueio": motivo_bloqueio,
            "elegivel_switch": bool(elegivel_preliminar),
            "switch_recomendado": bool(elegivel_preliminar),
            "motivo_decisao": motivo_decisao or "elegivel_preliminar",
            "prioridade_switch": "media" if elegivel_preliminar else "bloqueado",
        })

    df_switch_diag = pd.DataFrame(registros)
    if len(df_switch_diag) == 0:
        return df_switch_diag

    necessidade_curto_prazo = calcular_pressao_caixa_curto_prazo_v1(contas_exec, data_referencia, config)
    df_switch_diag = aplicar_bloqueio_pagamento_proximo_v1(df_switch_diag, necessidade_curto_prazo)

    if "bloqueado_por_pagamento_proximo" not in df_switch_diag.columns:
        df_switch_diag["bloqueado_por_pagamento_proximo"] = False

    for idx in df_switch_diag.index:
        if bool(df_switch_diag.at[idx, "bloqueado_por_pagamento_proximo"]):
            df_switch_diag.at[idx, "elegivel_switch"] = False
            df_switch_diag.at[idx, "switch_recomendado"] = False
            motivo_decisao = str(df_switch_diag.at[idx, "motivo_decisao"] or "").strip()
            if "curto_prazo" not in motivo_decisao:
                df_switch_diag.at[idx, "motivo_decisao"] = (motivo_decisao + "; bloqueado_por_pagamento_proximo").strip("; ").strip()

        if bool(df_switch_diag.at[idx, "switch_recomendado"]):
            ganho = _safe_float(df_switch_diag.at[idx, "ganho_liquido_estimado_switch"], 0.0)
            payback = df_switch_diag.at[idx, "dias_payback_switch"]
            if ganho > 100 or (payback is not None and _safe_float(payback, 9999) <= max(30, horizonte_analise_dias * 0.25)):
                df_switch_diag.at[idx, "prioridade_switch"] = "alta"
            elif ganho > 0:
                df_switch_diag.at[idx, "prioridade_switch"] = "media"
            else:
                df_switch_diag.at[idx, "prioridade_switch"] = "baixa"
        else:
            df_switch_diag.at[idx, "prioridade_switch"] = "bloqueado"

    ordenacao = ["switch_recomendado", "prioridade_switch", "ganho_liquido_estimado_switch", "saldo_liquido_atual"]
    asc = [False, True, False, False]
    return df_switch_diag.sort_values(by=ordenacao, ascending=asc, kind="mergesort").reset_index(drop=True)


def gerar_switch_execucao_v2(
    df_situacao_atual,
    contas_exec,
    investimentos_norm,
    mapa_bcb,
    data_referencia,
    config,
):
    if df_situacao_atual is None or len(df_situacao_atual) == 0:
        return pd.DataFrame()

    sim_cfg = (config or {}).get("simulacao", {}) if isinstance(config, dict) else {}
    horizonte_analise_dias = int(_safe_float(sim_cfg.get("horizonte_alocacao_dias", HORIZONTE_PROJECAO_DIAS), HORIZONTE_PROJECAO_DIAS))
    registros = []

    df_base = df_situacao_atual.copy()
    if "Lote ID" in df_base.columns:
        df_base = df_base[df_base["Lote ID"].astype(str).str.upper() != "TOTAL"].copy()
    if "Saldo Líquido Atual (R$)" in df_base.columns:
        df_base = df_base[pd.to_numeric(df_base["Saldo Líquido Atual (R$)"], errors="coerce").fillna(0.0) > 0].copy()

    if len(df_base):
        df_base["origem_recurso"] = df_base.apply(lambda row: _classificar_origem_recurso_switch(row, data_referencia=data_referencia), axis=1)
        df_base = df_base[df_base["origem_recurso"] == "caixa_disponivel"].copy()

    for _, row in df_base.iterrows():
        lote_id = str(row.get("Lote ID", "")).strip()
        origem_recurso = str(row.get("origem_recurso", "caixa_disponivel") or "caixa_disponivel").strip()
        produto_origem = "CAIXA_DISPONIVEL" if origem_recurso == "caixa_disponivel" else str(row.get("Carteira", "") or "").strip()
        valor_aporte = dinheiro_round(_safe_float(row.get("Saldo Líquido Atual (R$)"), 0.0))
        if valor_aporte <= 0:
            continue

        escolha = escolher_melhor_destino_switch_v2(
            produto_origem,
            valor_aporte,
            valor_aporte,
            horizonte_analise_dias,
            investimentos_norm,
            mapa_bcb,
            data_referencia,
            normalizar_nome_fn=normalizar_nome,
            excluir_produto_atual=False,
        )
        info_dest = escolha.get("destino_info") or {}
        taxa_dest_base_raw = _safe_float(info_dest.get("base"), 0.0)
        taxa_dest_bonus_raw = _safe_float(info_dest.get("bonus"), 0.0)
        dias_bonus_dest = int(_safe_float(info_dest.get("dias_bonus"), 0))
        patrimonio_aporte = dinheiro_round(escolha.get("patrimonio_destino", valor_aporte))
        ganho_aporte = dinheiro_round(patrimonio_aporte - valor_aporte)
        elegivel_aporte = bool(escolha.get("produto_destino_recomendado"))
        motivo_decisao = "elegivel_aporte"
        if not elegivel_aporte:
            motivo_decisao = escolha.get("motivo_indisponibilidade") or "nenhum_destino_elegivel"

        registros.append({
            "lote_id_origem": lote_id,
            "origem_recurso": origem_recurso,
            "produto_origem": produto_origem,
            "valor_aporte_disponivel": valor_aporte,
            "produto_destino_recomendado": escolha.get("produto_destino_recomendado"),
            "produto_destino_key": escolha.get("produto_destino_key"),
            "n_destinos_avaliados": int(_safe_float(escolha.get("n_destinos_avaliados"), 0)),
            "criterio_escolha_destino": escolha.get("criterio_escolha_destino") or "maior_patrimonio_estimado",
            "taxa_destino_base": round(taxa_dest_base_raw * 100, 4),
            "taxa_destino_bonus": round(taxa_dest_bonus_raw * 100, 4),
            "dias_bonus_destino": dias_bonus_dest,
            "horizonte_alocacao_dias": horizonte_analise_dias,
            "patrimonio_estimado_aporte_horizonte": patrimonio_aporte,
            "ganho_estimado_aporte_horizonte": ganho_aporte,
            "ganho_percentual_estimado_aporte": round((ganho_aporte / valor_aporte), 6) if valor_aporte > 0 else 0.0,
            "ganho_diario_estimado_aporte": dinheiro_round((ganho_aporte / horizonte_analise_dias) if horizonte_analise_dias > 0 else 0.0),
            "saldo_liquido_atual": valor_aporte,
            "custo_fiscal_saida": 0.0,
            "dias_para_cliff_ir": 999,
            "bloqueado_por_pagamento_proximo": False,
            "motivo_bloqueio": "",
            "elegivel_aporte": elegivel_aporte,
            "recomendado_aporte": elegivel_aporte,
            "motivo_decisao": motivo_decisao,
            "prioridade_aporte": "media" if elegivel_aporte else "bloqueado",
        })

    df_exec = pd.DataFrame(registros)
    if len(df_exec) == 0:
        return df_exec

    necessidade_curto_prazo = calcular_pressao_caixa_curto_prazo_v1(contas_exec, data_referencia, config)
    df_exec = aplicar_bloqueio_pagamento_proximo_v1(df_exec, necessidade_curto_prazo)

    for idx in df_exec.index:
        if bool(df_exec.at[idx, "bloqueado_por_pagamento_proximo"]):
            df_exec.at[idx, "elegivel_aporte"] = False
            df_exec.at[idx, "recomendado_aporte"] = False
            motivo_decisao = str(df_exec.at[idx, "motivo_decisao"] or "").strip()
            if "curto_prazo" not in motivo_decisao:
                df_exec.at[idx, "motivo_decisao"] = (motivo_decisao + "; bloqueado_por_pagamento_proximo").strip("; ").strip()
            df_exec.at[idx, "prioridade_aporte"] = "bloqueado"
        elif bool(df_exec.at[idx, "recomendado_aporte"]):
            ganho = _safe_float(df_exec.at[idx, "ganho_estimado_aporte_horizonte"], 0.0)
            if ganho > 100:
                df_exec.at[idx, "prioridade_aporte"] = "alta"
            elif ganho > 0:
                df_exec.at[idx, "prioridade_aporte"] = "media"
            else:
                df_exec.at[idx, "prioridade_aporte"] = "baixa"
        else:
            df_exec.at[idx, "prioridade_aporte"] = "bloqueado"

    ordenacao = ["recomendado_aporte", "prioridade_aporte", "ganho_estimado_aporte_horizonte", "valor_aporte_disponivel"]
    asc = [False, True, False, False]
    return df_exec.sort_values(by=ordenacao, ascending=asc, kind="mergesort").reset_index(drop=True)


def carregar_dados_excel_detalhado():
    if not baixar_planilha_google() and not os.path.exists(NOME_ARQUIVO_LOCAL):
        raise FileNotFoundError("ERRO: Sem arquivo e sem internet.")

    print(">>> [EXCEL] Lendo arquivo local...")
    try:
        xls = pd.ExcelFile(NOME_ARQUIVO_LOCAL)

        df_gastos = pd.read_excel(xls, nome_aba('despesas'))
        col_data_gasto = resolver_coluna(df_gastos, 'despesas', 'data')
        col_valor_gasto = resolver_coluna(df_gastos, 'despesas', 'valor')
        col_desc_gasto = resolver_coluna(df_gastos, 'despesas', 'descricao', required=False)
        col_pago = resolver_coluna(df_gastos, 'despesas', 'pago', required=False)
        col_lote_unico = resolver_coluna(df_gastos, 'despesas', 'lote_usado_1', required=False)

        df_gastos.dropna(subset=[col_data_gasto, col_valor_gasto], inplace=True)
        df_gastos[col_data_gasto] = pd.to_datetime(df_gastos[col_data_gasto]).dt.date

        if col_desc_gasto is None:
            col_desc_gasto = '__descricao_padrao__'
            df_gastos[col_desc_gasto] = 'Despesa Diversa'

        tem_lotes_usados = col_lote_unico is not None

        contas_pagas = []
        contas_nao_pagas = []
        if col_pago is not None:
            df_gastos[col_pago] = df_gastos[col_pago].astype(str).str.upper().str.strip()
            for ordem_processamento, (_, row) in enumerate(df_gastos.iterrows(), start=1):
                desc = str(row[col_desc_gasto])[:100].encode('utf-8', 'replace').decode('utf-8')
                if row[col_pago] == 'OK':
                    lote_usado = extrair_lote_usado_unico(row, col_lote_unico) if tem_lotes_usados else ''
                    contas_pagas.append((row[col_data_gasto], float(row[col_valor_gasto]), desc, lote_usado, ordem_processamento))
                else:
                    contas_nao_pagas.append((row[col_data_gasto], float(row[col_valor_gasto]), desc, ordem_processamento))
        else:
            print(f"   [AVISO] Coluna de pagamento não encontrada na aba {nome_aba('despesas')}. Todas as contas serão consideradas não pagas.")
            for ordem_processamento, (_, row) in enumerate(df_gastos.iterrows(), start=1):
                desc = str(row[col_desc_gasto])[:100].encode('utf-8', 'replace').decode('utf-8')
                contas_nao_pagas.append((row[col_data_gasto], float(row[col_valor_gasto]), desc, ordem_processamento))

        contas_pagas = ordenar_contas_processamento(contas_pagas)
        contas_nao_pagas = ordenar_contas_processamento(contas_nao_pagas)

        df_lotes = pd.read_excel(xls, nome_aba('lotes'))
        col_id = selecionar_coluna_id_lote(df_lotes)
        col_data_apl = resolver_coluna(df_lotes, 'lotes', 'data_aplicacao')
        col_valor_original = resolver_coluna(df_lotes, 'lotes', 'valor_original')
        col_invest = selecionar_coluna_produto_lote(df_lotes, INVESTIMENTOS_NORM)
        df_lotes.dropna(subset=[col_id, col_data_apl, col_valor_original], inplace=True)

        try:
            df_lotes_norm, auditoria_lotes_canonica = normalizar_lotes_brutos(
                df_lotes,
                MAPA_PRODUTOS_CANONICO if isinstance(MAPA_PRODUTOS_CANONICO, dict) else {'by_key': {}, 'by_nome_norm': {}},
                normalizar_nome_fn=normalizar_nome,
            )
            indice_lotes_canonico = construir_indice_lotes(df_lotes_norm)
            df_eventos_aporte_shadow = derivar_eventos_aporte_de_lotes(df_lotes_norm)

            log_debug(
                DEBUG_SHADOW,
                "SHADOW-LOTES",
                lotes_norm=len(df_lotes_norm),
                indice_lotes=len(indice_lotes_canonico),
                eventos_aporte=len(df_eventos_aporte_shadow),
            )
            if isinstance(auditoria_lotes_canonica, dict):
                log_debug(
                    DEBUG_SHADOW,
                    "SHADOW-LOTES",
                    produto_reconhecido=auditoria_lotes_canonica.get('qtd_produto_reconhecido'),
                    caixa=auditoria_lotes_canonica.get('qtd_caixa'),
                    produto_nao_reconhecido=auditoria_lotes_canonica.get('qtd_produto_nao_reconhecido'),
                    ids_duplicados=auditoria_lotes_canonica.get('qtd_ids_duplicados'),
                )
        except Exception as e:
            log_erro("SHADOW-LOTES", e)

        aportes = []
        for _, row in df_lotes.iterrows():
            d = pd.to_datetime(row[col_data_apl]).date()
            val = float(row[col_valor_original])
            lid = str(row[col_id])
            invest_raw = row[col_invest] if col_invest and col_invest in df_lotes.columns and pd.notna(row[col_invest]) else ''
            investimento_ausente_na_origem = _eh_produto_lote_ausente(invest_raw)
            invest = _resolver_nome_produto_lote_efetivo(invest_raw)
            if invest and normalizar_nome(invest) not in INVESTIMENTOS_NORM:
                print(f" -> [AUDITORIA] Produto do lote não reconhecido na carteira: '{invest}' (lote={lid}). Usando fallback de taxas.")
            taxa_base, taxa_bonus, dias_bonus = get_taxas_lote(invest)
            meta = {
                'taxa_base_cdi': taxa_base,
                'taxa_bonus_cdi': taxa_bonus,
                'dias_bonus': dias_bonus,
                'investimento': invest,
                'investimento_ausente_na_origem': bool(investimento_ausente_na_origem),
            }
            aportes.append((d, val, lid, meta))
        aportes.sort(key=lambda x: x[0])

        try:
            global comparacao_aportes_shadow
            if df_eventos_aporte_shadow is not None:
                comparacao_aportes_shadow = comparar_aportes_legado_vs_shadow(
                    aportes,
                    df_eventos_aporte_shadow,
                )
                log_debug(
                    DEBUG_SHADOW,
                    "SHADOW-LOTES",
                    qtd_legado=comparacao_aportes_shadow.get('qtd_legado'),
                    qtd_shadow=comparacao_aportes_shadow.get('qtd_shadow'),
                    soma_legado=comparacao_aportes_shadow.get('soma_legado'),
                    soma_shadow=comparacao_aportes_shadow.get('soma_shadow'),
                    equivalentes_essenciais=comparacao_aportes_shadow.get('equivalentes_essenciais'),
                )
                if DEBUG_SHADOW and comparacao_aportes_shadow.get('ids_somente_legado'):
                    print(f"[SHADOW-LOTES] ids_somente_legado={comparacao_aportes_shadow.get('ids_somente_legado')}")
                if DEBUG_SHADOW and comparacao_aportes_shadow.get('ids_somente_shadow'):
                    print(f"[SHADOW-LOTES] ids_somente_shadow={comparacao_aportes_shadow.get('ids_somente_shadow')}")
                if DEBUG_SHADOW and comparacao_aportes_shadow.get('datas_diferentes'):
                    print(f"[SHADOW-LOTES] datas_diferentes={comparacao_aportes_shadow.get('datas_diferentes')[:5]}")
                if DEBUG_SHADOW and comparacao_aportes_shadow.get('valores_diferentes'):
                    print(f"[SHADOW-LOTES] valores_diferentes={comparacao_aportes_shadow.get('valores_diferentes')[:5]}")
        except Exception as e:
            log_erro("SHADOW-LOTES", e)

        try:
            df_eventos_aporte_bruto_shadow = projetar_eventos_brutos_de_aportes(
                df_eventos_aporte_shadow,
                df_lotes_norm,
            )
            df_eventos_switch_shadow, auditoria_switch_shadow = derivar_eventos_switch_shadow(
                df_lotes_norm,
                [],
                normalizar_nome_fn=normalizar_nome,
            )
            df_eventos_financeiros_brutos = consolidar_eventos_financeiros_brutos(
                df_eventos_aporte_bruto_shadow,
                df_eventos_switch_shadow,
            )
            if DEBUG_SWITCH_SHADOW:
                print(
                    "[SHADOW-SWITCH] "
                    f"eventos_aporte_bruto={len(df_eventos_aporte_bruto_shadow)} "
                    f"eventos_switch={len(df_eventos_switch_shadow)} "
                    f"eventos_totais={len(df_eventos_financeiros_brutos)}"
                )
                if isinstance(auditoria_switch_shadow, dict):
                    print(
                        "[SHADOW-SWITCH] "
                        f"qtd_regras_switch={auditoria_switch_shadow.get('qtd_regras_switch')} "
                        f"qtd_switch_out={auditoria_switch_shadow.get('qtd_switch_out')} "
                        f"qtd_switch_in={auditoria_switch_shadow.get('qtd_switch_in')} "
                        f"qtd_lotes_origem_nao_encontrados={auditoria_switch_shadow.get('qtd_lotes_origem_nao_encontrados')} "
                        f"qtd_produtos_destino_invalidos={auditoria_switch_shadow.get('qtd_produtos_destino_invalidos')} "
                        f"qtd_switch_valor_excede_origem={auditoria_switch_shadow.get('qtd_switch_valor_excede_origem')}"
                    )
                if df_eventos_switch_shadow is not None and len(df_eventos_switch_shadow) > 0:
                    print("[SHADOW-SWITCH] amostra_eventos_switch=")
                    print(df_eventos_switch_shadow.head(4).to_string(index=False))
        except Exception as e:
            print(f"[SHADOW-SWITCH] erro={e}")

        try:
            df_eventos_ordenados_shadow = ordenar_eventos_financeiros_brutos_shadow(
                df_eventos_financeiros_brutos
            )

            estado_lotes_shadow_pre_replay, auditoria_replay_switch_shadow = projetar_estado_lotes_pre_replay_shadow(
                df_eventos_ordenados_shadow
            )
            if DEBUG_SWITCH_SHADOW:
                print(
                    "[SHADOW-SWITCH-REPLAY] "
                    f"eventos_total={len(df_eventos_ordenados_shadow)} "
                    f"lotes_ativos={auditoria_replay_switch_shadow.get('qtd_lotes_ativos')} "
                    f"lotes_encerrados_por_switch={auditoria_replay_switch_shadow.get('qtd_lotes_encerrados_por_switch')} "
                    f"lotes_tecnicos_novos={auditoria_replay_switch_shadow.get('qtd_lotes_tecnicos_novos')} "
                    f"soma_saldos_pre={auditoria_replay_switch_shadow.get('soma_saldos_pre')} "
                    f"soma_saldos_pos={auditoria_replay_switch_shadow.get('soma_saldos_pos')} "
                    f"delta_conservacao={auditoria_replay_switch_shadow.get('delta_conservacao')} "
                    f"qtd_inconsistencias={auditoria_replay_switch_shadow.get('qtd_inconsistencias')}"
                )
                if estado_lotes_shadow_pre_replay is not None and len(estado_lotes_shadow_pre_replay) > 0:
                    print("[SHADOW-SWITCH-REPLAY] amostra_estado_pre_replay=")
                    print(estado_lotes_shadow_pre_replay.head(8).to_string(index=False))
                if auditoria_replay_switch_shadow.get('inconsistencias'):
                    print("[SHADOW-SWITCH-REPLAY] inconsistencias=")
                    print(auditoria_replay_switch_shadow.get('inconsistencias')[:5])
        except Exception as e:
            print(f"[SHADOW-SWITCH-REPLAY] erro={e}")

        print(f" -> Dados brutos: {len(aportes)} lotes, {len(contas_pagas)} pagas, {len(contas_nao_pagas)} não pagas")

        taxas_info = {}
        for ap in aportes:
            key = (ap[3]['taxa_base_cdi'], ap[3]['taxa_bonus_cdi'], ap[3]['dias_bonus'])
            taxas_info[key] = taxas_info.get(key, 0) + 1
        for k, cnt in taxas_info.items():
            print(f"    -> {cnt} lote(s) com taxa_base={k[0]*100:.0f}% CDI, bonus={k[1]*100:.0f}% CDI por {k[2]} dias")

        log_passado_global = []
        estado_lotes_passado = []
        if contas_pagas and tem_lotes_usados:
            global MAPA_BCB, TAXA_PROJ
            aportes, log_passado_global, estado_lotes_passado = simular_passado(aportes, contas_pagas, MAPA_BCB, TAXA_PROJ)
        else:
            estado_lotes_passado = [
                {
                    'Lote ID': str(ap[2]),
                    'Data Aplicação': ap[0],
                    'Valor Inicial': float(ap[1]),
                    'Saldo Após Passado': float(ap[1]),
                    'Esgotado no Passado': False,
                    'Data Base Fiscal': ap[0],
                    'Fator Acumulado': 1.0,
                    'Taxa Base CDI': float(ap[3].get('taxa_base_cdi', TAXA_BASE_DEFAULT)),
                    'Taxa Bonus CDI': float(ap[3].get('taxa_bonus_cdi', TAXA_BONUS_DEFAULT)),
                    'Dias Bonus': int(ap[3].get('dias_bonus', DIAS_BONUS_DEFAULT)),
                    'Principal Remanescente': float(ap[3].get('principal_remanescente', ap[1])),
                    'Investimento': str(ap[3].get('investimento', '') or ''),
                    'Investimento Ausente na Origem': bool(ap[3].get('investimento_ausente_na_origem', False)),
                }
                for ap in aportes
            ]

        try:
            df_lotes_ordenados_replay_shadow = ordenar_lotes_para_replay_shadow(
                estado_lotes_shadow_pre_replay
            )
            estado_lotes_shadow_pos_passado, _, auditoria_replay_contas_switch_shadow = aplicar_contas_pagas_shadow(
                df_lotes_ordenados_replay_shadow,
                contas_pagas,
            )
            comparacao_remanescente_legado_vs_shadow = comparar_remanescente_legado_vs_shadow(
                estado_lotes_passado,
                estado_lotes_shadow_pos_passado,
            )
            if DEBUG_SWITCH_SHADOW:
                print(
                    "[SHADOW-SWITCH-PAST] "
                    f"contas_processadas={auditoria_replay_contas_switch_shadow.get('qtd_contas_processadas')} "
                    f"contas_cobertas={auditoria_replay_contas_switch_shadow.get('qtd_contas_cobertas')} "
                    f"lotes_vivos_shadow={auditoria_replay_contas_switch_shadow.get('qtd_lotes_vivos')} "
                    f"lotes_switch_vivos={auditoria_replay_contas_switch_shadow.get('qtd_lotes_switch_vivos')} "
                    f"soma_shadow={comparacao_remanescente_legado_vs_shadow.get('soma_shadow')} "
                    f"soma_legado={comparacao_remanescente_legado_vs_shadow.get('soma_legado')} "
                    f"delta_soma={comparacao_remanescente_legado_vs_shadow.get('delta_soma')}"
                )
        except Exception as e:
            print(f"[SHADOW-SWITCH-PAST] erro={e}")

        df_agrupado = pd.DataFrame(
            contas_nao_pagas,
            columns=['Data', 'Valor', 'Descrição', 'Ordem Processamento']
        )
        df_agrupado = df_agrupado.groupby('Data', as_index=False).agg({
            'Valor': 'sum',
            'Descrição': lambda x: ' | '.join(str(v) for v in x)[:100],
            'Ordem Processamento': 'min',
        })

        contas_agrupadas = []
        for _, row in df_agrupado.iterrows():
            desc = str(row['Descrição'])[:100].encode('utf-8', 'replace').decode('utf-8')
            contas_agrupadas.append((
                row['Data'],
                float(row['Valor']),
                desc,
                int(row['Ordem Processamento']) if pd.notna(row['Ordem Processamento']) else ORDEM_PROCESSAMENTO_SENTINELA,
            ))
        contas_agrupadas = ordenar_contas_processamento(contas_agrupadas)

        contas_individuais = ordenar_contas_processamento(contas_nao_pagas)

        print(f" -> Carregados: {len(aportes)} lotes, {len(contas_individuais)} contas individuais, {len(contas_agrupadas)} dias.\n")
        return aportes, contas_agrupadas, contas_individuais, log_passado_global, estado_lotes_passado

    except Exception as e:
        raise ValueError(f"Erro ao ler Excel: {e}")


# =========================================================
# 07. NÚCLEO FINANCEIRO
# =========================================================
def preparar_dados_vetorizados(aportes_raw, contas_raw):
    if not aportes_raw:
        return None, None, None, None, None, None, None, None, None, None

    aportes_raw.sort(key=lambda x: x[0])
    d_base = aportes_raw[0][0]
    d_fim_contas = max(x[0] for x in contas_raw) if contas_raw else DATA_REFERENCIA
    d_fim = d_fim_contas + timedelta(days=500)
    total_dias = (d_fim - d_base).days + 1

    cache_uteis = np.zeros(total_dias, dtype=np.int64)
    c = 0
    for i in range(total_dias):
        if cal.is_working_day(d_base + timedelta(days=i)):
            c += 1
        cache_uteis[i] = c

    lotes_dias = np.array([(x[0] - d_base).days for x in aportes_raw], dtype=np.int64)
    lotes_base_fiscal_dias = np.array([
        (x[3].get('data_base_fiscal', x[0]) - d_base).days for x in aportes_raw
    ], dtype=np.int64)
    lotes_vals = np.array([x[1] for x in aportes_raw], dtype=np.float64)
    contas_dias = np.array([(item[0] - d_base).days for item in contas_raw], dtype=np.int64)
    contas_vals = np.array([float(item[1]) for item in contas_raw], dtype=np.float64)

    # Arrays de taxas por lote
    lotes_taxa_base = np.array([x[3].get('taxa_base_cdi', TAXA_BASE_DEFAULT) for x in aportes_raw], dtype=np.float64)
    lotes_taxa_bonus = np.array([x[3].get('taxa_bonus_cdi', TAXA_BONUS_DEFAULT) for x in aportes_raw], dtype=np.float64)
    lotes_dias_bonus = np.array([x[3].get('dias_bonus', DIAS_BONUS_DEFAULT) for x in aportes_raw], dtype=np.int64)

    return lotes_dias, lotes_base_fiscal_dias, lotes_vals, contas_dias, contas_vals, cache_uteis, d_base, \
           lotes_taxa_base, lotes_taxa_bonus, lotes_dias_bonus

# =========================================================
# numba engine
# =========================================================
@njit(nogil=True, fastmath=True)
def sim_numba_core(genes, lotes_v_orig, lotes_base_fiscal_orig, vals_v_orig, contas_dias, contas_vals, cache_uteis,
                   lotes_taxa_base, lotes_taxa_bonus, lotes_dias_bonus):
    """
    Versão 5p: w_iof, w_ir, w_age, w_liq, w_cliff + penalidade residual
    Usa taxas CDI individuais por lote.
    """
    w_iof, w_ir, w_age, w_liq, w_cliff = genes
    saldo = vals_v_orig.copy()
    fator_lotes = np.ones(len(saldo), dtype=np.float64)
    last_upd = lotes_v_orig.copy()
    lotes_v = lotes_v_orig
    lotes_base_fiscal = lotes_base_fiscal_orig
    n_contas = len(contas_dias)
    n_lotes = len(lotes_v)
    saldo_negativo = 0.0

    for k in range(n_contas):
        dia = contas_dias[k]
        val_conta = contas_vals[k]
        for i in range(n_lotes):
            if saldo[i] > VALOR_MINIMO_LOTE_ATIVO and lotes_v[i] <= dia:
                d_uteis = cache_uteis[dia] - cache_uteis[last_upd[i]]
                if d_uteis > 0:
                    d_vida_fiscal = dia - lotes_base_fiscal[i]
                    if lotes_taxa_bonus[i] > 0.0 and d_vida_fiscal <= lotes_dias_bonus[i]:
                        tx = lotes_taxa_bonus[i]
                    else:
                        tx = lotes_taxa_base[i]
                    fator = (1.0 + TAXA_DIA_BASE) ** (tx * d_uteis)
                    saldo[i] *= fator
                    fator_lotes[i] *= fator
                    last_upd[i] = dia

        count_valid = 0
        cand_idx = np.empty(n_lotes, dtype=np.int64)
        cand_score = np.empty(n_lotes, dtype=np.float64)
        cand_flq = np.empty(n_lotes, dtype=np.float64)
        for i in range(n_lotes):
            if saldo[i] > VALOR_MINIMO_LOTE_ATIVO and lotes_v[i] <= dia:
                d_vida = dia - lotes_base_fiscal[i]
                iof = IOF_TABLE[d_vida] if d_vida < 30 else 0.0
                ir = obter_aliquota_ir_numba(d_vida, IR_THRESHOLDS_NUMBA, IR_ALIQUOTAS_NUMBA)
                dist_prox = distancia_proximo_cliff_ir_numba(d_vida)
                penalty_cliff = 1.0 if dist_prox <= DIAS_CLIFF_IR else 0.0
                fac = fator_lotes[i]
                r_luc = 0.0
                if fac > 1:
                    r_luc = 1 - (1/fac)
                flq_val = 1.0 - (r_luc * (iof + (1-iof)*ir))
                sc = (iof * w_iof * 100.0) + (ir * w_ir * 100.0) + \
                     (d_vida * w_age * -0.1) + (flq_val * w_liq * 10.0) + \
                     (penalty_cliff * w_cliff * 50.0)
                cand_idx[count_valid] = i
                cand_score[count_valid] = sc
                cand_flq[count_valid] = flq_val
                count_valid += 1

        if count_valid == 0:
            saldo_negativo += val_conta
            continue

        for i in range(count_valid):
            for j in range(i + 1, count_valid):
                if cand_score[j] < cand_score[i]:
                    tmp_s = cand_score[i]; cand_score[i] = cand_score[j]; cand_score[j] = tmp_s
                    tmp_idx = cand_idx[i]; cand_idx[i] = cand_idx[j]; cand_idx[j] = tmp_idx
                    tmp_flq = cand_flq[i]; cand_flq[i] = cand_flq[j]; cand_flq[j] = tmp_flq

        falta = val_conta
        for k_cand in range(count_valid):
            if falta <= 0.001:
                break
            idx_real = cand_idx[k_cand]
            flq = cand_flq[k_cand]
            if flq <= 0:
                continue
            disp_bruto = saldo[idx_real]
            uso_bruto = min(falta / flq, disp_bruto)
            saldo[idx_real] -= uso_bruto
            falta -= uso_bruto * flq
        if falta > TOLERANCIA_MONETARIA:
            saldo_negativo += falta

    soma_final = 0.0
    for i in range(n_lotes):
        soma_final += saldo[i]

    LIMIAR_RESIDUO = 10.0
    PENALIDADE_RESIDUO = 5.0
    penalidade_residuos = 0.0
    for i in range(n_lotes):
        if 0 < saldo[i] < LIMIAR_RESIDUO:
            penalidade_residuos += PENALIDADE_RESIDUO

    return -(soma_final - (saldo_negativo * 10.0) - penalidade_residuos)

# =========================================================
# classe lote
# =========================================================
class Lote:
    def __init__(self, id_lote, data_aplicacao, valor_inicial,
                 data_base_fiscal=None, fator_acumulado_inicial=1.0,
                 taxa_base_cdi=None, taxa_bonus_cdi=None, dias_bonus=None,
                 principal_remanescente_inicial=None):
        self.id = str(id_lote).strip()
        self.data_aplicacao = data_aplicacao
        self.data_base_fiscal = data_base_fiscal if data_base_fiscal is not None else data_aplicacao
        self.valor_inicial = float(valor_inicial)
        self.saldo_bruto = float(valor_inicial)
        self.fator_acumulado = max(1.0, float(fator_acumulado_inicial))
        self.principal_remanescente = float(self.valor_inicial if principal_remanescente_inicial is None else principal_remanescente_inicial)
        self.esgotado = False
        self.vezes_usado = 0
        self.total_bruto_sacado = 0.0
        self.total_imposto_pago = 0.0
        self.total_liquido_sacado = 0.0
        self.taxa_base_cdi = taxa_base_cdi if taxa_base_cdi is not None else TAXA_BASE_DEFAULT
        self.taxa_bonus_cdi = taxa_bonus_cdi if taxa_bonus_cdi is not None else TAXA_BONUS_DEFAULT
        self.dias_bonus = dias_bonus if dias_bonus is not None else DIAS_BONUS_DEFAULT

    def atualizar_juros(self, data_atual, taxa_diaria_decimal):
        if self.esgotado or data_atual <= self.data_aplicacao:
            return
        idade = (data_atual - self.data_base_fiscal).days
        em_bonus = self.taxa_bonus_cdi > 0.0 and idade < self.dias_bonus
        if em_bonus:
            mult = self.taxa_bonus_cdi
        else:
            mult = self.taxa_base_cdi
        fator_dia = (1.0 + taxa_diaria_decimal) ** mult
        self.saldo_bruto = round(self.saldo_bruto * fator_dia, 2)
        self.fator_acumulado *= fator_dia

    def get_fator_liquido(self, data_resgate):
        dias_vida = (data_resgate - self.data_base_fiscal).days
        if dias_vida < 0:
            return 0.0
        iof = IOF_TABLE[dias_vida] if dias_vida < 30 else 0.0
        ir = obter_aliquota_ir(dias_vida)
        principal_base = max(min(self.principal_remanescente, self.saldo_bruto), 0.0)
        lucro = max(self.saldo_bruto - principal_base, 0.0)
        if self.saldo_bruto <= 0:
            return 0.0
        taxa_total = iof + (1 - iof) * ir
        imposto = lucro * taxa_total
        return max(1.0 - (imposto / self.saldo_bruto), 0.0)

    def sacar(self, valor_bruto):
        if valor_bruto >= self.saldo_bruto - TOLERANCIA_MONETARIA:
            sacado = self.saldo_bruto
            self.saldo_bruto = 0.0
            self.principal_remanescente = 0.0
            self.esgotado = True
            self.vezes_usado += 1
            self.total_bruto_sacado += sacado
            return sacado
        if self.saldo_bruto <= 0:
            return 0.0
        valor_bruto = round(valor_bruto, 2)
        proporcao_sacada = min(max(valor_bruto / self.saldo_bruto, 0.0), 1.0) if self.saldo_bruto > 0 else 1.0
        principal_sacado = round(self.principal_remanescente * proporcao_sacada, 10)
        self.principal_remanescente = max(round(self.principal_remanescente - principal_sacado, 10), 0.0)
        self.saldo_bruto = round(self.saldo_bruto - valor_bruto, 2)
        self.vezes_usado += 1
        self.total_bruto_sacado += valor_bruto
        return valor_bruto

def criar_lote_de_aporte(dt, val, id_l, meta=None):
    """Cria um lote a partir do aporte preservando a regra financeira existente."""
    meta = meta or {}
    lote = Lote(
        id_l, dt, val,
        data_base_fiscal=meta.get('data_base_fiscal', dt),
        fator_acumulado_inicial=meta.get('fator_acumulado_inicial', 1.0),
        taxa_base_cdi=meta.get('taxa_base_cdi', TAXA_BASE_DEFAULT),
        taxa_bonus_cdi=meta.get('taxa_bonus_cdi', TAXA_BONUS_DEFAULT),
        dias_bonus=meta.get('dias_bonus', DIAS_BONUS_DEFAULT),
        principal_remanescente_inicial=meta.get('principal_remanescente', meta.get('principal_remanescente_inicial', float(val))),
    )
    lote.investimento = str(meta.get('investimento', '') or '')
    lote.investimento_ausente_na_origem = bool(meta.get('investimento_ausente_na_origem', False))
    return lote

def atualizar_saldo_lotes_no_dia(lotes_ativos, data_atual, bcb_map=None, taxa_proj=None):
    """Aplica o rendimento diário aos lotes ativos sem alterar a regra financeira."""
    if taxa_proj is None:
        taxa_proj = TAXA_DIA_BASE
    if not lotes_ativos or not is_dia_rendimento(data_atual, bcb_map):
        return
    if bcb_map and data_atual in bcb_map:
        fator_dia = bcb_map[data_atual]
        taxa_dia = fator_dia - 1.0
    else:
        taxa_dia = taxa_proj
    for lote in lotes_ativos:
        lote.atualizar_juros(data_atual, taxa_dia)

def executar_saque_lote(lote, valor_liquido_alvo, data_atual):
    """Executa o saque preservando a matemática financeira já validada."""
    saldo_antes = float(lote.saldo_bruto)
    fator = lote.get_fator_liquido(data_atual)
    if fator <= 0:
        return None

    bruto_necessario = valor_liquido_alvo / fator
    uso_bruto = min(bruto_necessario, lote.saldo_bruto)
    efetivo = round(lote.sacar(uso_bruto), 2)
    liquido = round(efetivo * fator, 2)
    imposto = round(efetivo - liquido, 2)
    lote.total_imposto_pago += imposto
    lote.total_liquido_sacado += liquido

    return {
        'lote': lote,
        'saldo_antes': saldo_antes,
        'fator_liquido': float(fator),
        'bruto': efetivo,
        'liquido': liquido,
        'imposto': imposto,
        'saldo_remanescente': float(lote.saldo_bruto),
    }

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

def serializar_lote_remanescente(lote, data_final):
    """Serializa o lote remanescente sem alterar a semântica financeira exportada."""
    data_efetiva = lote.data_aplicacao if lote.data_aplicacao > data_final else data_final
    return (
        data_efetiva,
        lote.saldo_bruto,
        lote.id,
        {
            'data_base_fiscal': lote.data_base_fiscal,
            'fator_acumulado_inicial': float(lote.fator_acumulado),
            'taxa_base_cdi': lote.taxa_base_cdi,
            'taxa_bonus_cdi': lote.taxa_bonus_cdi,
            'dias_bonus': lote.dias_bonus,
            'principal_remanescente': float(getattr(lote, 'principal_remanescente', lote.valor_inicial)),
            'investimento': str(getattr(lote, 'investimento', '') or ''),
            'investimento_ausente_na_origem': bool(getattr(lote, 'investimento_ausente_na_origem', False)),
        }
    )

def calcular_saldo_atual_lotes(lotes, data_saldo):
    """
    Consolida o saldo atual dos lotes já atualizados pelos rendimentos acumulados.
    Não altera os lotes; apenas expõe de forma explícita o cálculo final.
    """
    lotes_validos = [l for l in lotes if not l.esgotado and l.saldo_bruto > VALOR_MINIMO_LOTE_ATIVO]
    detalhes = []
    saldo_bruto_total = 0.0
    saldo_liquido_total = 0.0

    for lote in lotes_validos:
        saldo_bruto = float(round(lote.saldo_bruto, 2))
        fator_liquido = lote.get_fator_liquido(data_saldo)
        saldo_liquido = float(round(saldo_bruto * fator_liquido, 2))
        detalhes.append({
            'id_lote': lote.id,
            'data_aplicacao': lote.data_aplicacao,
            'data_base_fiscal': lote.data_base_fiscal,
            'saldo_bruto': saldo_bruto,
            'fator_liquido': float(fator_liquido),
            'saldo_liquido': saldo_liquido,
            'fator_acumulado': float(lote.fator_acumulado),
            'taxa_base_cdi': float(lote.taxa_base_cdi),
            'taxa_bonus_cdi': float(lote.taxa_bonus_cdi),
            'dias_bonus': int(lote.dias_bonus),
        })
        saldo_bruto_total += saldo_bruto
        saldo_liquido_total += saldo_liquido

    return {
        'data_saldo': data_saldo,
        'saldo_bruto_total': float(round(saldo_bruto_total, 2)),
        'saldo_liquido_total': float(round(saldo_liquido_total, 2)),
        'detalhes_lotes': detalhes,
        'num_lotes_ativos': len(lotes_validos),
    }

# =========================================================
# solvers pulp
# =========================================================
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
        dist_prox = distancia_proximo_cliff_ir(dias)
        penalty_cliff = 1.0 if dist_prox <= DIAS_CLIFF_IR else 0.0
        flq = fator_liq[i]

        penalidade = (1.0
                     + (iof * p_iof)
                     + (ir * p_ir)
                     + (dias * p_age)
                     + (flq * p_liq)
                     + (penalty_cliff * p_cliff))
        custos.append(x_vars[i] * penalidade)

    prob += pulp.lpSum(custos)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] == "Optimal":
        return [v.varValue for v in x_vars]
    return [0.0] * len(lotes)

def resolver_pulp_hibrido_5p(lotes, alvo, hoje, params_pen, data_final, bcb_map=None, taxa_proj=None):
    """
    Híbrido 5p = Penalidade 5p + custo de oportunidade (VPL) por lote.

    Por que existia empate com PENALIDADE_5P?
    - A versão antiga multiplicava TODAS as penalidades por um mesmo fator global (projeção),
      o que não altera as razões relativas entre lotes. Resultado: solução idêntica.

    Esta versão inclui um termo **por lote** que penaliza sacar de um lote que tende a ter
    maior valor líquido futuro (oportunidade de manter aplicado até `data_final`).
    """
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

        dist_prox = distancia_proximo_cliff_ir(dias)
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

# =========================================================
# scoring econômico
# =========================================================
def get_score_economico(lote, data_hoje, dias_cliff=10, penalizar_iof=True):
    dias = (data_hoje - lote.data_base_fiscal).days
    if penalizar_iof and dias < 30:
        return 1e9 + (30 - dias)

    fator = lote.get_fator_liquido(data_hoje)
    if fator <= 0.001:
        return 1e9

    custo_fiscal = 1.0 / fator
    penalidade_cliff = 0.0

    for threshold, info in sorted(IR_FAIXAS.items()):
        if dias < threshold:
            dias_ate_threshold = threshold - dias
            if dias_ate_threshold <= dias_cliff:
                ratio_lucro = max(0.0, 1.0 - (1.0 / lote.fator_acumulado)) if lote.fator_acumulado > 1 else 0.0
                delta_ir = info['delta']
                ganho_relativo = ratio_lucro * delta_ir
                urgencia = (dias_cliff - dias_ate_threshold + 1) / dias_cliff
                penalidade_cliff = ganho_relativo * urgencia * 20.0
            break

    return custo_fiscal + penalidade_cliff

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

# =========================================================
# engine de simulação
# =========================================================
def rodar_estrategia(nome, aportes_in, contas_in, params_opt=None, bcb_map=None, taxa_proj=None, data_referencia=None):
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

    d_ini = min([x[0] for x in aportes]) if aportes else DATA_REFERENCIA
    d_fim = max([x[0] for x in contas]) if contas else DATA_REFERENCIA
    if data_referencia is not None:
        d_fim = min(d_fim, data_referencia)
    horizonte_proj_dias = HORIZONTE_PROJECAO_DIAS
    d_proj = max(d_fim + timedelta(days=horizonte_proj_dias), d_fim)

    data_atual = d_ini
    lotes_pool = []
    lotes_ativos = []
    log = []
    evento_financeiro_global = 1
    valor_contas_total = 0.0
    valor_nao_coberto = 0.0
    contas_nao_cobertas = 0

    while data_atual <= d_fim:
        novos = aportes_por_data.get(data_atual, [])
        for dt, val, id_l, meta in novos:
            investimento_ausente_na_origem = bool((meta or {}).get('investimento_ausente_na_origem', False))
            if (
                data_referencia is not None
                and investimento_ausente_na_origem
                and dt == data_referencia
            ):
                continue
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
                    dist_prox = distancia_proximo_cliff_ir(dias)
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

    return saldo_final, pd.DataFrame(log), lotes_pool, {
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
    }

# =========================================================
# 08. OTIMIZAÇÃO E VALIDAÇÃO
# =========================================================
dados_aportes_g = []
dados_contas_g = []
mapa_bcb_g = {}

def reduzir_contas_treinamento(contas_raw, max_contas=None):
    if max_contas is None:
        max_contas = TREINAMENTO_MAX_CONTAS_PADRAO
    if not contas_raw or len(contas_raw) <= max_contas:
        return contas_raw
    contas_ord = sorted(contas_raw, key=lambda x: x[0])
    step = max(1, int(np.ceil(len(contas_ord) / max_contas)))
    amostra = contas_ord[::step]
    if contas_ord[-1] not in amostra:
        amostra.append(contas_ord[-1])
    return sorted(amostra, key=lambda x: x[0])

def escolher_perfil_auto(num_contas, num_lotes, tempo_alvo_min):
    carga = (num_contas * 1.0) + (num_lotes * 1.5)
    if tempo_alvo_min <= TREINAMENTO_AUTO_TEMPO_ALVO_CURTO_MAX:
        return 'rapido', f"tempo-alvo curto ({tempo_alvo_min} min)"
    if carga > TREINAMENTO_AUTO_CARGA_MEDIA_MIN and tempo_alvo_min <= 15:
        return 'rapido', f"carga alta ({carga:.0f}) para tempo-alvo {tempo_alvo_min} min"
    if carga > TREINAMENTO_AUTO_CARGA_ALTA_MIN and tempo_alvo_min <= 25:
        return 'balanceado', f"carga muito alta ({carga:.0f}) para tempo-alvo {tempo_alvo_min} min"
    if tempo_alvo_min >= TREINAMENTO_AUTO_TEMPO_ALVO_LONGO_MIN and carga < TREINAMENTO_AUTO_CARGA_BAIXA_MAX:
        return 'profundo', f"tempo-alvo amplo ({tempo_alvo_min} min) e carga moderada ({carga:.0f})"
    return 'balanceado', f"equilíbrio padrão (carga={carga:.0f}, tempo-alvo={tempo_alvo_min} min)"

def objective_pulp_wrapper_5p(vetor_params):
    params_dict = {
        'peso_iof': vetor_params[0],
        'peso_ir': vetor_params[1],
        'peso_idade': vetor_params[2],
        'peso_liq': vetor_params[3],
        'peso_cliff': vetor_params[4]
    }
    _, _, _, stats = rodar_estrategia(
        "PENALIDADE_5P",
        dados_aportes_g,
        dados_contas_g,
        params_opt=params_dict,
        bcb_map=mapa_bcb_g
    )
    return -stats.get('saldo_liquido_final', 0.0)

def treinar_genetica_profundo(aportes_raw, contas_raw, maxiter=300, popsize=80, genes_iniciais=None):
    print(f">>> [GENÉTICA PROFUNDA] Iniciando com {maxiter} gerações, população {popsize}...")
    res = preparar_dados_vetorizados(aportes_raw, contas_raw)
    lotes_v, lotes_base_fiscal_v, vals_v, contas_dias, contas_vals, cache_uteis, _, lotes_taxa_base, lotes_taxa_bonus, lotes_dias_bonus = res
    if lotes_v is None:
        return np.array([10.0, 10.0, 0.0, 10.0, 50.0])
    args_sim = (
        lotes_v,
        lotes_base_fiscal_v,
        vals_v,
        contas_dias,
        contas_vals,
        cache_uteis,
        lotes_taxa_base,
        lotes_taxa_bonus,
        lotes_dias_bonus,
    )
    bounds_ai = OPT_GEN_BOUNDS

    init_population = None
    if genes_iniciais is not None:
        print(f"    -> Usando genes iniciais: {genes_iniciais}")
        score_inicial = sim_numba_core(genes_iniciais, *args_sim)
        print(f"    -> Saldo inicial: R$ {-score_inicial:,.2f}")
        n_clones = max(OPT_GEN_MIN_CLONES, popsize // OPT_GEN_DIVISOR_POPSIZE_CLONES)
        n_variacoes = popsize - n_clones
        init_population = []
        for _ in range(n_clones):
            init_population.append(genes_iniciais.copy())
        for _ in range(n_variacoes):
            variacao = genes_iniciais + np.random.normal(OPT_GEN_RUIDO_GAUSSIANO_MEDIA, OPT_GEN_RUIDO_GAUSSIANO_DESVIO, genes_iniciais.shape[0]) * genes_iniciais
            variacao = np.clip(variacao, [b[0] for b in bounds_ai], [b[1] for b in bounds_ai])
            init_population.append(variacao)
        init_population = np.array(init_population)

    res_ai = differential_evolution(
        sim_numba_core,
        bounds_ai,
        args=args_sim,
        strategy=OPT_GEN_STRATEGY,
        maxiter=maxiter,
        popsize=popsize,
        workers=OPT_GEN_WORKERS,
        updating=OPT_GEN_UPDATING,
        seed=OPT_GEN_SEED,
        init=init_population if init_population is not None else OPT_GEN_INIT_SEM_POPULACAO_INICIAL
    )
    print(f"    -> Melhor saldo: R$ {-res_ai.fun:,.2f}")
    if genes_iniciais is not None:
        melhoria = -res_ai.fun - (-score_inicial)
        print(f"    -> Melhoria: R$ {melhoria:,.2f}")
    return res_ai.x

def treinar_penalidade_5p(aportes_raw, contas_raw, bcb_map_ref, maxiter=200, popsize=60, params_iniciais=None):
    print(f">>> [PENALIDADE 5P] Iniciando com {maxiter} gerações...")
    global dados_aportes_g, dados_contas_g, mapa_bcb_g
    dados_aportes_g = aportes_raw
    dados_contas_g = contas_raw
    mapa_bcb_g = bcb_map_ref

    bounds_pulp = OPT_PEN_BOUNDS

    init_population = None
    if params_iniciais is not None:
        p_array = np.array([params_iniciais['peso_iof'], params_iniciais.get('peso_ir',0), params_iniciais['peso_idade'], params_iniciais.get('peso_liq',0), params_iniciais['peso_cliff']])
        score_inicial = -objective_pulp_wrapper_5p(p_array)
        print(f"    -> Saldo inicial: R$ {score_inicial:,.2f}")
        n_clones = max(OPT_PEN_MIN_CLONES, popsize // OPT_PEN_DIVISOR_POPSIZE_CLONES)
        n_variacoes = popsize - n_clones
        init_population = []
        for _ in range(n_clones):
            init_population.append(p_array.copy())
        for _ in range(n_variacoes):
            variacao = p_array + np.random.normal(OPT_PEN_RUIDO_GAUSSIANO_MEDIA, OPT_PEN_RUIDO_GAUSSIANO_DESVIO, p_array.shape[0]) * np.abs(p_array)
            variacao = np.clip(variacao, [b[0] for b in bounds_pulp], [b[1] for b in bounds_pulp])
            init_population.append(variacao)
        init_population = np.array(init_population)

    res_pulp = differential_evolution(
        objective_pulp_wrapper_5p,
        bounds_pulp,
        strategy=OPT_PEN_STRATEGY,
        maxiter=maxiter,
        popsize=popsize,
        workers=OPT_PEN_WORKERS,
        updating=OPT_PEN_UPDATING,
        seed=OPT_PEN_SEED,
        init=init_population if init_population is not None else OPT_PEN_INIT_SEM_POPULACAO_INICIAL
    )
    best_params = {
        'peso_iof': res_pulp.x[0],
        'peso_ir': res_pulp.x[1],
        'peso_idade': res_pulp.x[2],
        'peso_liq': res_pulp.x[3],
        'peso_cliff': res_pulp.x[4]
    }
    print(f"    -> Melhor saldo: R$ {-res_pulp.fun:,.2f}")
    return best_params

def salvar_parametros(arquivo, genes, params_pen, tipo='5p'):
    dados = {
        'genes': genes.tolist(),
        'penalidade': params_pen,
        'tipo': tipo
    }
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2)
    print(f">>> Parâmetros salvos em {arquivo}")

def carregar_parametros(arquivo, fallback_url=None):
    """Carrega parâmetros (genes/penalidade) de um JSON local; se não existir, tenta baixar do Drive.

    - Se fallback_url for um link do tipo '...uc?export=download&id=...', usa direto.
    - Se for link do tipo '.../file/d/<ID>/view...', extrai o ID e converte.
    - Se for um ID puro, converte para URL de download.
    """
    if Path(arquivo).exists():
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            print(f">>> Parâmetros carregados do arquivo local: {arquivo}")
            return np.array(dados['genes']), dados['penalidade'], dados.get('tipo', '5p')
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")

    if not fallback_url:
        return None, None, None

    print(f">>> Arquivo local não encontrado. Tentando fallback do Drive.")
    try:
        if "uc?export=download&id=" in str(fallback_url):
            download_url = str(fallback_url)
        else:
            m = re.search(r'/d/([a-zA-Z0-9_-]+)', str(fallback_url))
            if not m:
                m = re.search(r'id=([a-zA-Z0-9_-]+)', str(fallback_url))
            file_id = m.group(1) if m else str(fallback_url).strip()
            download_url = gdrive_uc_download(file_id)

        headers = {"User-Agent": REDE_USER_AGENT_DOWNLOAD}
        response = requests.get(download_url, headers=headers, timeout=REDE_TIMEOUT_DOWNLOAD_SEGUNDOS, verify=REDE_VERIFICAR_SSL)
        response.raise_for_status()

        tmp = str(BASE_DIR_ATIVA / _normalizar_nome_arquivo_json(_cfg_get_required_any([["arquivos", "parametros_5p"], ["arquivos", "melhores_parametros_5p"]])))
        with open(tmp, "wb") as f:
            f.write(response.content)

        with open(tmp, "r", encoding="utf-8") as f:
            dados = json.load(f)

        print(">>> Parâmetros carregados do fallback.")
        return np.array(dados['genes']), dados['penalidade'], dados.get('tipo', '5p')
    except Exception as e:
        print(f" -> [AVISO] Falha ao carregar fallback de parâmetros: {e}")
        return None, None, None

def validacao_walk_forward(aportes, contas, competidores_params,
                           bcb_map=None, taxa_proj=None, n_splits=4, contas_por_estrategia=None):
    print("\n" + "="*70)
    print("VALIDAÇÃO WALK-FORWARD ROBUSTA")
    print("="*70)

    if not contas:
        print("  -> Sem contas para validar.")
        return {}

    contas_ord_ref = sorted(contas, key=lambda x: x[0])
    n_total_ref = len(contas_ord_ref)
    if n_total_ref < max(12, n_splits * 2):
        print(f"  -> Dados insuficientes para validação robusta ({n_total_ref} contas).")
        return {}

    tamanho_teste_ref = max(1, n_total_ref // (n_splits + 1))
    print(f"  Total contas (referência): {n_total_ref} | Splits: {n_splits} | Janela teste ref: {tamanho_teste_ref}\n")

    resultados_wf = {}
    for nome, params in competidores_params:
        try:
            contas_base = (contas_por_estrategia or {}).get(nome, contas)
            contas_ord = sorted(contas_base, key=lambda x: x[0])
            n_total = len(contas_ord)
            if n_total < max(12, n_splits * 2):
                print(f"  {nome:<20} [AVISO] contas insuficientes ({n_total})")
                continue
            tamanho_teste = max(1, n_total // (n_splits + 1))

            liq_adj_treino = []
            liq_adj_teste = []

            for i in range(1, n_splits + 1):
                fim_teste = n_total - (n_splits - i) * tamanho_teste
                ini_teste = max(1, fim_teste - tamanho_teste)
                contas_treino = contas_ord[:ini_teste]
                contas_teste = contas_ord[ini_teste:fim_teste]
                if not contas_treino or not contas_teste:
                    continue

                _, _, _, stats_tr = rodar_estrategia(
                    nome, aportes, contas_treino,
                    params_opt=params, bcb_map=bcb_map,
                    taxa_proj=taxa_proj
                )
                _, _, _, stats_te = rodar_estrategia(
                    nome, aportes, contas_teste,
                    params_opt=params, bcb_map=bcb_map,
                    taxa_proj=taxa_proj
                )
                liq_adj_treino.append(stats_tr.get('saldo_liquido_final', 0.0) - stats_tr.get('valor_nao_coberto', 0.0))
                liq_adj_teste.append(stats_te.get('saldo_liquido_final', 0.0) - stats_te.get('valor_nao_coberto', 0.0))

            if not liq_adj_teste:
                continue

            ef_treino = float(np.mean(liq_adj_treino))
            ef_teste = float(np.mean(liq_adj_teste))
            delta_ef = ((ef_treino - ef_teste) / (abs(ef_treino) + 1e-9)) * 100.0
            cv_liq = float(np.std(liq_adj_teste) / (abs(np.mean(liq_adj_teste)) + 1e-9))
            score_robustez = 100.0 - max(0.0, delta_ef) - (cv_liq * 25.0)

            resultados_wf[nome] = {
                'ef_treino': ef_treino,
                'ef_teste': ef_teste,
                'delta_ef': delta_ef,
                'cv_liquido_teste': cv_liq,
                'score_robustez': score_robustez,
                'saldo_liquido_teste_medio': float(np.mean(liq_adj_teste)),
            }
            status = "⚠️ overfit" if delta_ef > 2.0 else "✓ ok"
            print(f"  {nome:<20} LiqAj tr={ef_treino:,.2f} | LiqAj te={ef_teste:,.2f} | "
                  f"Δ%={delta_ef:.2f} | CVliq={cv_liq:.3f} | robustez={score_robustez:.2f} | n={n_total} | {status}")
        except Exception as e:
            print(f"  {nome:<20} [ERRO] {e}")

    if resultados_wf:
        print("\n  Top robustez:")
        for nome, data in sorted(resultados_wf.items(), key=lambda x: x[1]['score_robustez'], reverse=True)[:5]:
            print(f"   - {nome}: score={data['score_robustez']:.2f}, saldo_liq_teste={data['saldo_liquido_teste_medio']:,.2f}")

    return resultados_wf

def _score_liquido_ajustado(stats, saldo):
    return stats.get('saldo_liquido_final', saldo) - stats.get('valor_nao_coberto', 0.0)

def _escolher_modo_treino_por_objetivo(
    nome_estrategia,
    params_base,
    dados_aportes,
    contas_agr,
    contas_ind,
    mapa_bcb,
    taxa_proj,
):
    try:
        saldo_agr_t, _, _, stats_agr_t = rodar_estrategia(
            nome_estrategia, dados_aportes, contas_agr,
            params_opt=params_base, bcb_map=mapa_bcb, taxa_proj=taxa_proj
        )
        saldo_ind_t, _, _, stats_ind_t = rodar_estrategia(
            nome_estrategia, dados_aportes, contas_ind,
            params_opt=params_base, bcb_map=mapa_bcb, taxa_proj=taxa_proj
        )
        score_agr_t = _score_liquido_ajustado(stats_agr_t, saldo_agr_t)
        score_ind_t = _score_liquido_ajustado(stats_ind_t, saldo_ind_t)
        return ('individual', contas_ind) if score_ind_t > score_agr_t else ('agrupado', contas_agr)
    except Exception:
        return 'agrupado', contas_agr

# =========================================================
# 09. EXECUÇÃO PRINCIPAL
# =========================================================
if __name__ == "__main__":
    print("\n>>> OTIMIZADOR FINANCEIRO DEEP - VERSÃO MESCLADA FINAL v14.0 <<<\n")

    try:
        MAPA_BCB, TAXA_PROJ = obter_historico_bcb(date(2025,1,1))
    except Exception as e:
        print(f"Aviso BCB: {e}")
        MAPA_BCB = {}
        TAXA_PROJ = TAXA_DIA_BASE

    baixar_planilha_google()
    INVESTIMENTOS_NORM.update(carregar_investimentos())
    globals()['TAXA_BASE_DEFAULT'] = obter_taxa_base_referencia_futura(TAXA_BASE_DEFAULT)

    try:
        dados_aportes, dados_contas_agr, dados_contas_ind, LOG_PASSADO, ESTADO_LOTES_PASSADO = carregar_dados_excel_detalhado()
        if not dados_aportes:
            print("Erro: Sem dados de aportes.")
            exit()
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        import traceback
        traceback.print_exc()
        exit()

    valores_originais = carregar_valores_originais_lotes(NOME_ARQUIVO_LOCAL)

    print("OPÇÕES DE TREINAMENTO")
    print("1. Modo rápido (carregar parâmetros salvos)")
    print("2. Modo profundo (executar otimizações - pode levar HORAS)")
    print("3. Modo refinamento (otimizar a partir de parâmetros existentes)")
    opcao = input("Escolha (1/2/3): ").strip()
    if not opcao:
        opcao = MODO_TREINAMENTO_PADRAO

    perfil_treino = PERFIL_TREINO_PADRAO
    if opcao in ['2', '3']:
        print("\nPerfis de treino:")
        print("  r = rápido (≈ menor tempo, boa aproximação)")
        print("  b = balanceado (padrão recomendado)")
        print("  p = profundo (máxima busca, mais lento)")
        print("  a = auto (decide por contas/lotes + tempo-alvo)")
        p = input("Escolha perfil (r/b/p/a): ").strip().lower()
        if not p:
            p = PERFIL_TREINO_AUTO_OPCAO if PERFIL_TREINO_PADRAO == "auto" else {"rapido": "r", "balanceado": "b", "profundo": "p", "auto": PERFIL_TREINO_AUTO_OPCAO}.get(PERFIL_TREINO_PADRAO, "b")
        if p == 'r':
            perfil_treino = 'rapido'
        elif p == 'p':
            perfil_treino = 'profundo'
        elif p == 'a':
            try:
                tempo_alvo = int(input("Tempo-alvo de treino em minutos (ex: 10): ").strip())
            except Exception:
                tempo_alvo = TEMPO_ALVO_AUTO_PADRAO_MINUTOS
            perfil_treino, motivo = escolher_perfil_auto(
                num_contas=len(dados_contas_agr),
                num_lotes=len(dados_aportes),
                tempo_alvo_min=max(TREINAMENTO_TEMPO_ALVO_MINIMO_ABSOLUTO, tempo_alvo)
            )
            print(f" -> Modo AUTO selecionou perfil '{perfil_treino}' ({motivo}).")

    cfg_treino = TREINAMENTO_PERFIS[perfil_treino]

    BEST_GENES_5p = None
    BEST_PARAMS_5p = None

    if opcao in ['1', '3']:
        g5, p5, t5 = carregar_parametros(PARAM_FILE_5P, fallback_url=FALLBACK_PARAM_URL_5P)
        if g5 is not None:
            print(f"✓ Parâmetros 5p carregados")
            BEST_GENES_5p = g5
            BEST_PARAMS_5p = p5
        else:
            print("Arquivo 5p não encontrado e fallback falhou.")

        if opcao == '1':
            print("✓ Modo rápido: usando parâmetros salvos.\n")
        else:
            print("✓ Parâmetros base carregados para refinamento.\n")

    if opcao == '2' or opcao == '3':
        if opcao == '2':
            print("\n>>> INICIANDO TREINAMENTO PROFUNDO (do zero) <<<\n")
            genes_iniciais_5p = None
            params_iniciais_5p = None
        else:
            print("\n>>> INICIANDO REFINAMENTO (a partir de parâmetros existentes) <<<\n")
            genes_iniciais_5p = BEST_GENES_5p
            params_iniciais_5p = BEST_PARAMS_5p

        contas_treino_opt = reduzir_contas_treinamento(
            dados_contas_agr,
            max_contas=cfg_treino['max_contas_treino']
        )
        contas_treino_ind_opt = reduzir_contas_treinamento(
            dados_contas_ind,
            max_contas=cfg_treino['max_contas_treino']
        )
        if len(contas_treino_opt) != len(dados_contas_agr):
            print(f" -> Treino acelerado (agr): contas reduzidas de {len(dados_contas_agr)} para {len(contas_treino_opt)}")
        if len(contas_treino_ind_opt) != len(dados_contas_ind):
            print(f" -> Treino acelerado (ind): contas reduzidas de {len(dados_contas_ind)} para {len(contas_treino_ind_opt)}")

        modo_treino_5p, contas_treino_5p = _escolher_modo_treino_por_objetivo(
            'GENETICA_5P',
            genes_iniciais_5p if genes_iniciais_5p is not None else np.array([10.0, 10.0, 0.0, 10.0, 50.0]),
            dados_aportes,
            contas_treino_opt,
            contas_treino_ind_opt,
            MAPA_BCB,
            TAXA_PROJ,
        )

        BEST_GENES_5p = treinar_genetica_profundo(
            dados_aportes, contas_treino_5p,
            maxiter=cfg_treino['gen_maxiter'], popsize=cfg_treino['gen_popsize'],
            genes_iniciais=genes_iniciais_5p
        )

        BEST_PARAMS_5p = treinar_penalidade_5p(
            dados_aportes, contas_treino_5p, MAPA_BCB,
            maxiter=cfg_treino['pen_maxiter'], popsize=cfg_treino['pen_popsize'],
            params_iniciais=params_iniciais_5p
        )

        if BEST_GENES_5p is not None and BEST_PARAMS_5p is not None:
            salvar_parametros(PARAM_FILE_5P, BEST_GENES_5p, BEST_PARAMS_5p, tipo='5p')

    if BEST_GENES_5p is None:
        BEST_GENES_5p = np.array([10.0, 10.0, 0.0, 10.0, 50.0])
    if BEST_PARAMS_5p is None:
        BEST_PARAMS_5p = {'peso_iof': 100.0, 'peso_ir': 0.0, 'peso_idade': 0.1, 'peso_liq': 0.0, 'peso_cliff': 1000.0}

    print("\n>>> TESTE DE AGRUPAMENTO (REFERÊNCIA) <<<")
    print("[1/2] Testando: AGRUPADO POR DIA...")
    saldo_agr, _, _, stats_agr = rodar_estrategia("GENETICA_5P", dados_aportes, dados_contas_agr,
                                                  params_opt=BEST_GENES_5p, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ)
    print(f"   -> Saldo Bruto: R$ {saldo_agr:,.2f} | Saldo Líquido: R$ {stats_agr.get('saldo_liquido_final', 0.0):,.2f} | Não Coberto: R$ {stats_agr.get('valor_nao_coberto', 0.0):,.2f}")

    print("[2/2] Testando: INDIVIDUAL...")
    saldo_ind, _, _, stats_ind = rodar_estrategia("GENETICA_5P", dados_aportes, dados_contas_ind,
                                                  params_opt=BEST_GENES_5p, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ)
    print(f"   -> Saldo Bruto: R$ {saldo_ind:,.2f} | Saldo Líquido: R$ {stats_ind.get('saldo_liquido_final', 0.0):,.2f} | Não Coberto: R$ {stats_ind.get('valor_nao_coberto', 0.0):,.2f}")

    score_agr_ref = _score_liquido_ajustado(stats_agr, saldo_agr)
    score_ind_ref = _score_liquido_ajustado(stats_ind, saldo_ind)
    modo_ref = "individual" if score_ind_ref > score_agr_ref else "agrupado"
    ganho_ref = abs(score_ind_ref - score_agr_ref)
    print(f"\n-> Referência GENETICA_5P: {modo_ref.upper()} (diferença ajustada de R$ {ganho_ref:.2f})")

    modo_analise_forcado = modo_ref
    print("\nOPÇÃO DE MODO PARA A ANÁLISE FINAL")
    print("-" * 60)
    print(f" -> Modo recomendado pelo teste de agrupamento: {modo_ref}")
    print(f" -> Modo da análise final aplicado automaticamente: {modo_analise_forcado}")

    print("\n" + "-" * 60)
    print("COMPETIÇÃO FINAL (modo global definido pela referência)")
    print("-" * 60 + "\n")

    competidores = [
        ("PENALIDADE_5P", BEST_PARAMS_5p),
        ("HIBRIDO_5P", BEST_PARAMS_5p),
        ("ECONOMICA_VPL", None),
        ("ECONOMICA_CLIFF", None),
        ("HEURISTICA", None),
        ("GENETICA_5P", BEST_GENES_5p),
    ]

    ranking = []
    contas_por_estrategia = {}

    total_sacado_passado = {}
    total_resgatado_passado = 0.0
    total_imposto_passado = 0.0
    for entrada in LOG_PASSADO:
        lote_id = entrada['Lote']
        total_sacado_passado[lote_id] = total_sacado_passado.get(lote_id, 0) + entrada['Bruto']
        total_resgatado_passado += float(entrada.get('Liquido', 0.0))
        total_imposto_passado += float(entrada.get('Imposto', 0.0))

    for nome, params in competidores:
        print(f" -> {nome}...")
        t0 = time.time()
        try:
            resultado_agr = rodar_estrategia(
                nome, dados_aportes, dados_contas_agr,
                params_opt=params, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ
            )
            resultado_ind = rodar_estrategia(
                nome, dados_aportes, dados_contas_ind,
                params_opt=params, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ
            )

            if modo_analise_forcado == 'individual':
                contas_exec = dados_contas_ind
                modo_exec = 'individual'
                saldo, df_log, lotes_finais, stats = resultado_ind
            else:
                contas_exec = dados_contas_agr
                modo_exec = 'agrupado'
                saldo, df_log, lotes_finais, stats = resultado_agr

            contas_por_estrategia[nome] = contas_exec
            data_final = max((c[0] for c in contas_exec), default=DATA_REFERENCIA)

            saldo_liquido_ajustado = _score_liquido_ajustado(stats, saldo)

            ranking.append({
                "Estratégia": nome,
                "Modo": modo_exec,
                "Saldo Final (R$)": saldo,
                "Saldo Líquido (R$)": round(stats.get('saldo_liquido_final', 0.0), 2),
                "Saldo Líquido Ajustado (R$)": round(saldo_liquido_ajustado, 2),
                "Total Resgatado (R$)": stats['total_resgatado_liquido'],
                "Imposto Total (R$)": stats['total_imposto'],
                "Total Resgatado c/ Passado (R$)": round(stats['total_resgatado_liquido'] + total_resgatado_passado, 2),
                "Imposto Total c/ Passado (R$)": round(stats['total_imposto'] + total_imposto_passado, 2),
                "Valor Não Coberto (R$)": round(stats.get('valor_nao_coberto', 0.0), 2),
                "Contas Não Cobertas": int(stats.get('contas_nao_cobertas', 0)),
                "Eficiência Fiscal (%)": round(stats.get('eficiencia_fiscal', 0.0), 2),
                "Riqueza Total (R$)": round(stats.get('riqueza_total', 0.0), 2),
                "NPV Riqueza (R$)": round(stats.get('npv_riqueza', 0.0), 2),
                "Lotes Usados": stats['num_lotes_usados'],
                "Total Lotes": stats['total_lotes'],
                "Tempo (s)": round(time.time() - t0, 2)
            })

            if not df_log.empty:
                arquivo = TEMPLATE_RESULTADO_ESTRATEGIA.format(estrategia=nome.lower(), modo=modo_exec)
                with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
                    df_log_passado = pd.DataFrame(LOG_PASSADO) if LOG_PASSADO else pd.DataFrame()
                    df_log_total = pd.concat([df_log_passado, df_log], ignore_index=True)

                    if not df_log_total.empty:
                        if 'Sequencia Saque' in df_log_total.columns:
                            df_log_total['Sequencia Saque Real'] = df_log_total['Sequencia Saque']
                        if 'Evento Financeiro' in df_log_total.columns:
                            df_log_total['Evento Financeiro Real'] = df_log_total['Evento Financeiro']

                        colunas_ordenacao = ['Data']
                        if 'Ordem Processamento' in df_log_total.columns:
                            colunas_ordenacao.append('Ordem Processamento')
                        if 'Status Lote Ordem' in df_log_total.columns:
                            colunas_ordenacao.append('Status Lote Ordem')
                        if 'Saldo Remanescente' in df_log_total.columns:
                            colunas_ordenacao.append('Saldo Remanescente')
                        if 'Evento Financeiro Real' in df_log_total.columns:
                            colunas_ordenacao.append('Evento Financeiro Real')
                        elif 'Evento Financeiro' in df_log_total.columns:
                            colunas_ordenacao.append('Evento Financeiro')

                        df_log_total = df_log_total.sort_values(colunas_ordenacao, kind='stable').reset_index(drop=True)

                        chaves_grupo = [c for c in ['Data', 'Conta', 'Ordem Processamento'] if c in df_log_total.columns]
                        if chaves_grupo:
                            df_log_total['Sequencia Saque'] = (
                                df_log_total.groupby(chaves_grupo, sort=False).cumcount() + 1
                            )
                        elif 'Sequencia Saque' in df_log_total.columns:
                            df_log_total['Sequencia Saque'] = np.arange(1, len(df_log_total) + 1)

                        if 'Evento Financeiro' in df_log_total.columns:
                            df_log_total['Evento Financeiro'] = np.arange(1, len(df_log_total) + 1)

                    colunas_auxiliares_extrato = [
                        c for c in [
                            'Ordem Processamento',
                            'Evento Financeiro',
                            'Sequencia Saque Real',
                            'Evento Financeiro Real',
                            'Status Lote Ordem',
                            'Status Lote',
                        ] if c in df_log_total.columns
                    ]

                    colunas_contexto_auditoria = [
                        c for c in [
                            'Data', 'Conta', 'Lote', 'Bruto', 'Imposto', 'Liquido', 'Saldo Remanescente', 'Sequencia Saque'
                        ] if c in df_log_total.columns
                    ]

                    colunas_extrato_publico = [c for c in df_log_total.columns if c not in colunas_auxiliares_extrato]
                    df_extrato_publico = df_log_total[colunas_extrato_publico].copy()

                    df_extrato_auditoria = pd.DataFrame()
                    if colunas_auxiliares_extrato:
                        colunas_auditoria = []
                        for c in colunas_contexto_auditoria + colunas_auxiliares_extrato:
                            if c in df_log_total.columns and c not in colunas_auditoria:
                                colunas_auditoria.append(c)
                        df_extrato_auditoria = df_log_total[colunas_auditoria].copy()

                    df_extrato_publico.to_excel(writer, sheet_name=ABA_EXTRATO, index=False)
                    if not df_extrato_auditoria.empty:
                        df_extrato_auditoria.to_excel(writer, sheet_name=ABA_AUDITORIA_EXTRATO, index=False)

                    carteira = []
                    total_liquido_carteira = 0.0
                    for l in lotes_finais:
                        if l.saldo_bruto > VALOR_MINIMO_LOTE_ATIVO:
                            fator_liq = l.get_fator_liquido(data_final)
                            liq_est = round(l.saldo_bruto * fator_liq, 2)
                            total_liquido_carteira += liq_est
                            dias = (data_final - l.data_base_fiscal).days
                            taxa_ret = ((l.saldo_bruto + l.total_bruto_sacado) / l.valor_inicial) if l.valor_inicial > 0 else 1.0
                            carteira.append({
                                "Lote ID": l.id,
                                "Data Aplicação": l.data_aplicacao,
                                "Dias de Vida": dias,
                                "Valor Inicial": l.valor_inicial,
                                "Saldo Bruto": round(l.saldo_bruto, 2),
                                "Líquido Estimado": liq_est,
                                "Vezes Usado": l.vezes_usado,
                                "Total Bruto Sacado": round(l.total_bruto_sacado, 2),
                                "Taxa Retorno": round(taxa_ret, 4),
                                "Taxa Base CDI (%)": round(l.taxa_base_cdi * 100, 0),
                                "Taxa Bônus CDI (%)": round(l.taxa_bonus_cdi * 100, 0) if l.taxa_bonus_cdi > 0 else 0,
                                "Dias Bônus": l.dias_bonus,
                            })
                    pd.DataFrame(carteira).to_excel(writer, sheet_name=ABA_CARTEIRA_FINAL, index=False)
                    pd.DataFrame([{
                        'Saldo Líquido Final (Stats)': round(stats.get('saldo_liquido_final', 0.0), 2),
                        'Soma Líquido Estimado Carteira': round(total_liquido_carteira, 2),
                        'Diferença': round(stats.get('saldo_liquido_final', 0.0) - total_liquido_carteira, 2),
                    }]).to_excel(writer, sheet_name=ABA_RESUMO, index=False)

                    try:
                        _, _, lotes_hoje, _ = rodar_estrategia(
                            nome, dados_aportes, contas_exec,
                            params_opt=params, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ,
                            data_referencia=DATA_REFERENCIA
                        )
                        df_relatorio_atual = gerar_relatorio_situacao_atual(
                            estado_lotes_passado=ESTADO_LOTES_PASSADO,
                            log_passado=LOG_PASSADO,
                            valores_originais=valores_originais,
                            mapa_bcb=MAPA_BCB,
                            data_referencia=DATA_REFERENCIA,
                        )
                        if not df_relatorio_atual.empty:
                            df_relatorio_atual.to_excel(writer, sheet_name=ABA_SITUACAO_ATUAL, index=False)

                        df_switch_diagnostico = gerar_switch_diagnostico(
                            df_situacao_atual=df_relatorio_atual,
                            contas_exec=contas_exec,
                            investimentos_norm=INVESTIMENTOS_NORM,
                            mapa_bcb=MAPA_BCB,
                            data_referencia=DATA_REFERENCIA,
                            config=config,
                        )
                        if not df_switch_diagnostico.empty:
                            df_switch_diagnostico.to_excel(writer, sheet_name=ABA_SWITCH_DIAGNOSTICO, index=False)

                        df_switch_execucao = gerar_switch_execucao_v2(
                            df_situacao_atual=df_relatorio_atual,
                            contas_exec=contas_exec,
                            investimentos_norm=INVESTIMENTOS_NORM,
                            mapa_bcb=MAPA_BCB,
                            data_referencia=DATA_REFERENCIA,
                            config=config,
                        )
                        if not df_switch_execucao.empty:
                            df_switch_execucao.to_excel(writer, sheet_name=ABA_SWITCH_EXECUCAO, index=False)
                    except Exception as e:
                        print(f"   [AVISO] Erro ao gerar relatório atual para {nome}: {e}")

                print(f"    Modo: {modo_exec} | Salvo: {arquivo}")

        except Exception as e:
            print(f"   [ERRO] {nome}: {e}")

    resultados_wf = validacao_walk_forward(
        dados_aportes, dados_contas_agr, competidores,
        bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ,
        n_splits=cfg_treino.get('wf_splits', 4),
        contas_por_estrategia=contas_por_estrategia
    )

    print("\n" + "=" * 100)
    print("RANKING FINAL - TODAS AS ESTRATÉGIAS")
    print("=" * 100)
    if ranking:
        df_res = pd.DataFrame(ranking)
        for col_saldo in ['Saldo Líquido Ajustado (R$)', 'Saldo Líquido (R$)', 'Saldo Final (R$)']:
            if col_saldo in df_res.columns:
                break
        else:
            for col_saldo in df_res.columns:
                if 'Saldo' in col_saldo or 'saldo' in col_saldo:
                    break
            else:
                raise KeyError('Nenhuma coluna de saldo encontrada no ranking.')
        robustez_map = {k: v.get('score_robustez', AVALIACAO_WF_ROBUSTEZ_DEFAULT) for k, v in (resultados_wf or {}).items()}
        df_res['Robustez WF'] = df_res['Estratégia'].map(lambda n: robustez_map.get(n, AVALIACAO_WF_ROBUSTEZ_DEFAULT))
        df_res['Score Final'] = df_res[col_saldo] * (AVALIACAO_RANKING_PESO_SALDO + AVALIACAO_RANKING_PESO_ROBUSTEZ * (df_res['Robustez WF'] / 100.0))
        df_res = df_res.sort_values(by=['Score Final', col_saldo], ascending=False)
        base_saldo = df_res[df_res['Estratégia'] == 'HEURISTICA'][col_saldo].values[0] if 'HEURISTICA' in df_res['Estratégia'].values else None
        print(f"\n{'Estratégia':<22} {'Modo':<10} {'Saldo Líq Aj.':>14} {'Saldo Líq':>12} {'Saldo Bruto':>14} {'Não Coberto':>13} {'WF':>7} {'Score':>12} {'Lotes':>10} {'Tempo':>8} {'Ganho %':>10}")
        print("-" * 172)
        for _, row in df_res.iterrows():
            ganho = ((row[col_saldo] - base_saldo) / base_saldo * 100) if base_saldo else 0
            print(f"{row['Estratégia']:<22} {row.get('Modo', '-'):<10} {row.get('Saldo Líquido Ajustado (R$)', row.get('Saldo Líquido (R$)', 0)):>14,.2f} {row.get('Saldo Líquido (R$)', 0):>12,.2f} {row.get('Saldo Final (R$)', 0):>14,.2f} {row.get('Valor Não Coberto (R$)', 0):>13,.2f} {row.get('Robustez WF', 0):>7.2f} {row.get('Score Final', 0):>12,.2f} {row['Lotes Usados']:>4}/{row['Total Lotes']:<4} {row['Tempo (s)']:>8.2f} {ganho:>9.2f}%")

        if resultados_wf:
            print("\nResumo de robustez (top 5):")
            for nome, d in sorted(resultados_wf.items(), key=lambda x: x[1]['score_robustez'], reverse=True)[:5]:
                print(f" - {nome:<20} score={d['score_robustez']:.2f} | deltaEF={d['delta_ef']:.2f} | CVliq={d['cv_liquido_teste']:.3f}")

        print("\n" + "=" * 100)
        print("SITUAÇÃO ATUAL - MELHOR ESTRATÉGIA")
        print("=" * 100)
        melhor_estrategia = df_res.iloc[0]['Estratégia']
        for nome, params in competidores:
            if nome == melhor_estrategia:
                contas_exec = contas_por_estrategia.get(nome, dados_contas_agr)
                _, _, _, _ = rodar_estrategia(
                    nome, dados_aportes, contas_exec,
                    params_opt=params, bcb_map=MAPA_BCB, taxa_proj=TAXA_PROJ,
                    data_referencia=DATA_REFERENCIA
                )
                df_situacao_atual = gerar_relatorio_situacao_atual(
                    estado_lotes_passado=ESTADO_LOTES_PASSADO,
                    log_passado=LOG_PASSADO,
                    valores_originais=valores_originais,
                    mapa_bcb=MAPA_BCB,
                    data_referencia=DATA_REFERENCIA,
                )
                if df_situacao_atual.empty:
                    print(f"\nSituação atual da estratégia {melhor_estrategia}: sem dados para exibir.")
                else:
                    print(f"\nSituação atual da estratégia {melhor_estrategia}:")
                    colunas_exibir = [
                        'Lote ID', 'Carteira', 'Data Aplicação', 'Data Base Fiscal', 'Dias Corridos até Hoje',
                        'Dias Úteis até Hoje', 'Valor Original (R$)', 'Total Líquido Sacado (R$)',
                        'Saldo Bruto Atual (R$)', 'Saldo Líquido Atual (R$)', 'Patrimônio Líquido até Hoje (R$)',
                        'Ganho da Otimização vs Dinheiro Parado (R$)'
                    ]
                    colunas_exibir = [c for c in colunas_exibir if c in df_situacao_atual.columns]
                    df_print = df_situacao_atual[colunas_exibir].copy()
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 220):
                        print(df_print.to_string(index=False))
                break
    else:
        print("Nenhuma estratégia foi executada com sucesso.")

    print("\n✅ Otimização concluída!")

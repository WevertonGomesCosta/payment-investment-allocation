# =========================================================
# 00. BOOTSTRAP E AMBIENTE
# =========================================================

import sys
import subprocess
import warnings
from datetime import date, timedelta, datetime
from decimal import Decimal, ROUND_HALF_UP
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
import numpy as np
import pandas as pd
import copy
import json
import os
from pathlib import Path
import re
import pulp
import itertools
import unicodedata
from importlib import metadata as importlib_metadata

def instalar_dependencias():
    required = {'pandas', 'numpy', 'openpyxl', 'workalendar', 'requests', 'pulp'}
    try:
        installed = {dist.metadata['Name'].lower() for dist in importlib_metadata.distributions() if dist.metadata.get('Name')}
        missing = required - installed
    except Exception:
        missing = required
    if missing:
        print(f"Instalando dependências: {missing}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *sorted(missing)])

instalar_dependencias()

from workalendar.america import Brazil
warnings.filterwarnings("ignore")

# =========================================================
# 01. CONFIG, CONTRATO E RESOLUÇÃO
# =========================================================

def _extrair_file_id_google(url: str):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', str(url or ''))
    return match.group(1) if match else None

def _baixar_url_para_arquivo(url: str, nome_destino: str, *, usar_confirmacao_drive: bool = False):
    try:
        import requests
        session = requests.Session()
        response = session.get(url, stream=True, timeout=30, verify=False)
        if usar_confirmacao_drive:
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    response = session.get(url, params={'confirm': value}, stream=True, timeout=30, verify=False)
                    break
        response.raise_for_status()
        with open(nome_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True, None
    except Exception as e:
        return False, e

def baixar_planilha_google():
    print(f">>> [DOWNLOAD] Iniciando download da planilha...")
    file_id = _extrair_file_id_google(LINK_GOOGLE_SHEETS)
    if not file_id:
        print("   Link do Google Sheets inválido.")
        return False
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    ok, err = _baixar_url_para_arquivo(url, NOME_ARQUIVO_LOCAL)
    if ok:
        print(f"   Sucesso! Arquivo salvo como {NOME_ARQUIVO_LOCAL}.")
        return True
    print(f"   [ERRO] Falha no download: {err}")
    return False

def baixar_arquivo_drive(url, nome_destino):
    file_id = _extrair_file_id_google(url)
    if not file_id:
        print(f"   Link do Drive inválido: {url}")
        return False
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    ok, err = _baixar_url_para_arquivo(download_url, nome_destino, usar_confirmacao_drive=True)
    if ok:
        print(f"   Arquivo baixado: {nome_destino}")
        return True
    print(f"   [ERRO] Falha ao baixar {url}: {err}")
    return False

# =========================================================
# 02. POLÍTICAS E UTILITÁRIOS CENTRAIS
# =========================================================

def data_hoje_referencia():
    if ZoneInfo is not None:
        try:
            return datetime.now(ZoneInfo("America/Sao_Paulo")).date()
        except Exception:
            pass
    return datetime.now().date()

def _caminhos_base_projeto():
    bases = []
    try:
        bases.append(Path(__file__).resolve().parent)
    except NameError:
        pass
    bases.append(Path.cwd().resolve())

    vistos = set()
    saida = []
    for base in bases:
        if not base:
            continue
        chave = str(base)
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(base)
    return saida

def _localizar_arquivo(nome_arquivo: str):
    if not nome_arquivo:
        return None

    caminho = Path(nome_arquivo)
    candidatos = []
    if caminho.is_absolute():
        candidatos.append(caminho)
    else:
        for base in _caminhos_base_projeto():
            candidatos.append(base / nome_arquivo)
            candidatos.append(base / 'code' / nome_arquivo)

    vistos = set()
    for cand in candidatos:
        chave = str(cand)
        if chave in vistos:
            continue
        vistos.add(chave)
        if cand.exists():
            return cand.resolve()
    return None

def _resolver_config_path():
    candidatos = []

    env_cfg = os.environ.get("CONFIG_PATH")
    if env_cfg:
        candidatos.append(Path(env_cfg))

    for base in _caminhos_base_projeto():
        candidatos.extend([
            base / 'config_atualizado.json',
            base / 'code' / 'config_atualizado.json',
            base / 'config.json',
            base / 'code' / 'config.json',
            base / 'config_links.json',
            base / 'code' / 'config_links.json',
        ])

    vistos = set()
    for caminho in candidatos:
        try:
            caminho = Path(caminho).expanduser()
            chave = str(caminho.resolve()) if caminho.exists() else str(caminho)
            if chave in vistos:
                continue
            vistos.add(chave)
            if caminho.exists():
                return caminho.resolve()
        except Exception:
            continue

    return None


def carregar_config():
    caminho = _resolver_config_path()
    if caminho is None:
        print("[AVISO] Nenhum arquivo de configuração encontrado. Usando defaults mínimos.")
        return {}, None

    try:
        data = json.loads(caminho.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError("O arquivo de configuração não contém um objeto JSON.")
        return data, caminho
    except Exception as e:
        print(f"[AVISO] Falha ao carregar config em {caminho}: {e}")
        return {}, caminho

def _cfg_get(path, default=None):
    cur = CONFIG
    for chave in path:
        if not isinstance(cur, dict) or chave not in cur:
            return default
        cur = cur[chave]
    return cur

def _cfg_get_any(paths, default=None):
    for path in paths:
        valor = _cfg_get(path, None)
        if valor is not None:
            return valor
    return default

def _cfg_get_required_any(paths):
    valor = _cfg_get_any(paths, default=None)
    if valor is None:
        txt = " OU ".join(" > ".join(p) for p in paths)
        raise RuntimeError(f"Nenhuma chave obrigatória encontrada no config: {txt}")
    return valor

def nome_aba(chave, default=None):
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
    mapa_norm = {str(c).strip().lower(): c for c in cols_reais}

    try:
        aliases = aliases_coluna(secao, chave)
    except Exception:
        if required:
            raise
        return None

    for alias in aliases:
        alias_norm = str(alias).strip().lower()
        if alias_norm in mapa_norm:
            return mapa_norm[alias_norm]

    if required:
        raise KeyError(
            f"Coluna não encontrada para {secao}/{chave}. "
            f"Aliases tentados: {aliases}. Colunas disponíveis: {cols_reais}"
        )
    return None

def _iterar_candidatos_arquivo(nome_arquivo: str, extras=None):
    vistos = set()
    if extras:
        for item in extras:
            if item is None:
                continue
            caminho = Path(item)
            chave = str(caminho.resolve()) if caminho.exists() else str(caminho)
            if chave in vistos:
                continue
            vistos.add(chave)
            yield caminho

    localizado = _localizar_arquivo(nome_arquivo)
    if localizado is not None:
        chave = str(localizado)
        if chave not in vistos:
            vistos.add(chave)
            yield localizado

    for base in _caminhos_base_projeto():
        for caminho in (base / nome_arquivo, base / 'code' / nome_arquivo):
            chave = str(caminho.resolve()) if caminho.exists() else str(caminho)
            if chave in vistos:
                continue
            vistos.add(chave)
            yield caminho

def _resolver_arquivo_excel_local():
    global NOME_ARQUIVO_LOCAL
    if len(sys.argv) >= 2 and sys.argv[1].lower().endswith(('.xlsx', '.xlsm', '.xls')):
        NOME_ARQUIVO_LOCAL = sys.argv[1]

    caminho = _localizar_arquivo(NOME_ARQUIVO_LOCAL)
    if caminho is None:
        print(f"Arquivo {NOME_ARQUIVO_LOCAL} não encontrado. Tentando download...")
        if not baixar_planilha_google():
            raise FileNotFoundError(f"Falha ao baixar a planilha: {NOME_ARQUIVO_LOCAL}")
        caminho = _localizar_arquivo(NOME_ARQUIVO_LOCAL) or Path(NOME_ARQUIVO_LOCAL).resolve()
    else:
        caminho = Path(caminho).resolve()

    NOME_ARQUIVO_LOCAL = str(caminho)
    return caminho

def ler_aba_excel(nome_aba: str) -> pd.DataFrame:
    return pd.read_excel(_resolver_arquivo_excel_local(), sheet_name=nome_aba)
CONFIG, CONFIG_PATH = carregar_config()

CONFIG_LINKS = CONFIG
CONFIG_LINKS_PATH = CONFIG_PATH

GOOGLE_CFG = _cfg_get(["google_drive"], {}) if isinstance(CONFIG, dict) else {}
PATHS_CFG = _cfg_get(["paths"], {}) if isinstance(CONFIG, dict) else {}
DOWNLOADS_CFG = _cfg_get(["downloads"], {}) if isinstance(CONFIG, dict) else {}
EXEC_CFG = _cfg_get(["execucao"], _cfg_get(["execution"], {})) if isinstance(CONFIG, dict) else {}
SIM_CFG = _cfg_get(["simulacao"], _cfg_get(["simulation"], {})) if isinstance(CONFIG, dict) else {}
SWITCH_CFG = _cfg_get(["switching"], {}) if isinstance(CONFIG, dict) else {}

GOOGLE_SHEETS_FILE_ID = _cfg_get(["google_drive", "sheets_file_id"], "17Rbdi74kVuXm8tqto3TUP19BVRXMjvqe")
GOOGLE_SHEETS_EDIT_BASE = _cfg_get(["urls", "google_sheets_edit_base"], "https://docs.google.com/spreadsheets/d/{file_id}/edit")

if GOOGLE_SHEETS_FILE_ID:
    if "{file_id}" in str(GOOGLE_SHEETS_EDIT_BASE):
        LINK_GOOGLE_SHEETS = str(GOOGLE_SHEETS_EDIT_BASE).format(file_id=GOOGLE_SHEETS_FILE_ID)
    else:
        LINK_GOOGLE_SHEETS = f"{str(GOOGLE_SHEETS_EDIT_BASE).rstrip('/')}/{GOOGLE_SHEETS_FILE_ID}/edit"
else:
    LINK_GOOGLE_SHEETS = None

sheets_file_id = GOOGLE_SHEETS_FILE_ID

NOME_ARQUIVO_LOCAL = _cfg_get_required_any([
    ["arquivos", "planilha"],
    ["paths", "excel_local"],
])

CACHE_BCB_FILE = _cfg_get_required_any([
    ["arquivos", "cache_bcb"],
    ["paths", "cache_bcb"],
])

RESULTADO_OTIMIZADOR_FIXO = _cfg_get_any([
    ["paths", "resultado_otimizador_fixo"],
], default=None)

PARAM_5P_FIXO = _cfg_get_any([
    ["arquivos", "parametros_5p"],
    ["paths", "param_5p_fixo"],
], default="melhores_parametros_5p.json")

fallback_bcb_file_id = GOOGLE_CFG.get('fallback_bcb_file_id', '1B-xAeSXVzB8fEj5RJbbK17W-wWRAlXVn')
fallback_param_5p_file_id = GOOGLE_CFG.get('fallback_param_5p_file_id', '1x2NXINcmzFHHINewQLkhwCflAsjUMEGf')
FALLBACK_BCB_URL = DOWNLOADS_CFG.get('fallback_bcb_url') or f"https://drive.google.com/file/d/{fallback_bcb_file_id}/view?usp=sharing"
FALLBACK_PARAM_URL_3P = DOWNLOADS_CFG.get('fallback_param_3p_url', 'https://drive.google.com/file/d/1sEWjE840c2NxNKyYcveaMD2iWGiNL3lp/view?usp=sharing')
FALLBACK_PARAM_URL_5P = DOWNLOADS_CFG.get('fallback_param_5p_url') or f"https://drive.google.com/file/d/{fallback_param_5p_file_id}/view?usp=sharing"

PARAMS_HIBRIDO = None
PLANO_PAGAMENTOS_EXTERNO = None
ORIGEM_PLANO_PAGAMENTOS = None
MODO_EXECUCAO_FUTURO = str(EXEC_CFG.get('modo_execucao_futuro', 'rigido_plano_externo'))
AUTO_REBAIXAR_MODO_SE_PLANO_INCOMPATIVEL = bool(EXEC_CFG.get('auto_rebaixar_plano_incompativel', True))
MODO_FALLBACK_PLANO_INCOMPATIVEL = str(EXEC_CFG.get('modo_fallback_plano_incompativel', 'dinamico'))
EXIBIR_DESCRICAO_MODO = bool(EXEC_CFG.get('exibir_descricao_modo', True))

MODOS_EXECUCAO_FUTURO_INFO = {
    'dinamico': 'Ignora o plano externo na execução das contas futuras e deixa o motor local decidir pagamentos e switches.',
    'rigido_plano_externo': 'Tenta reproduzir o Extrato do arquivo externo conta a conta; quando faltar saldo ou o lote não existir, registra desvio e ajusta.',
    'rigido_melhor_data': 'Usa a mesma lógica do plano externo, mas reancora cada switch na melhor data encontrada no diagnóstico antes de rodar o futuro.',
}

DIAGNOSTICO_MODO_EXECUCAO = {
    'modo_solicitado': None,
    'modo_efetivo': None,
    'houve_rebaixamento': False,
    'motivos_rebaixamento': [],
    'plano_externo_carregado': False,
    'origem_plano_externo': None,
    'observacao': '',
}

PRODUTOS_GLOBAIS_SIMULACAO = []

# =========================================================
# 03. PRODUTOS E CARTEIRA
# =========================================================

def normalizar_modo_execucao_futuro(valor):
    txt = str(valor or '').strip().lower()
    aliases = {
        'dinamico': 'dinamico',
        'dynamic': 'dinamico',
        'rigido_plano_externo': 'rigido_plano_externo',
        'plano_externo_rigido': 'rigido_plano_externo',
        'rigido': 'rigido_plano_externo',
        'rigido_melhor_data': 'rigido_melhor_data',
        'melhor_data': 'rigido_melhor_data',
        'rigido_com_melhor_data': 'rigido_melhor_data',
    }
    return aliases.get(txt, 'rigido_plano_externo')

MODO_EXECUCAO_FUTURO = normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)

ABA_GASTOS            = nome_aba("despesas", "Todos os Gastos")
ABA_INVENTARIO        = nome_aba("lotes", "Inventário de Lotes")
ABA_CARTEIRA          = nome_aba("carteira", "Carteira")
ABA_APORTES           = nome_aba("aportes", "Aportes")

CDI_ANUAL             = float(_cfg_get_any([
    ["premissas_mercado", "cdi_anual_modelo"],
    ["simulation", "cdi_anual"],
], default=0.1490))
PRODUTO_PADRAO = None  # inicializado após carregar a Carteira
TAXA_DIA_BASE         = ((1 + CDI_ANUAL) ** (1 / 252)) - 1
IOF_TABLE             = np.array([
    1.00, 0.96, 0.93, 0.90, 0.86, 0.83, 0.80, 0.76, 0.73, 0.70,
    0.66, 0.63, 0.60, 0.56, 0.53, 0.50, 0.46, 0.43, 0.40,
    0.36, 0.33, 0.30, 0.26, 0.23, 0.20, 0.16, 0.13, 0.10, 0.06, 0.03,
])

TAXA_ALTA             = 1.30    # multiplicador para primeiros 30 dias (produto padrão)
TAXA_BAIXA            = 1.03    # multiplicador após 30 dias (produto padrão)
TAXA_BASE_DEFAULT     = float(_cfg_get_any([["defaults_lote", "taxa_base_cdi"]], default=TAXA_BAIXA))
TAXA_BONUS_DEFAULT    = float(_cfg_get_any([["defaults_lote", "taxa_bonus_cdi"]], default=0.0))
DIAS_BONUS_DEFAULT    = int(_cfg_get_any([["defaults_lote", "dias_bonus"]], default=0))

SWITCHING_LIMIAR_GANHO = float(SWITCH_CFG.get('limiar_ganho_pct', 0.0001))

EXCLUIR_PRODUTOS_REGEX = [r"\bitau\b.*\b100%\b", r"cdb\s*itau\s*100"]
MIN_TAXA_BASE_PARA_SWITCH = float(SWITCH_CFG.get('min_taxa_base_para_switch', 1.01))
HORIZONTE_EXTRA_DIAS   = int(SIM_CFG.get('horizonte_extra_dias', 365))

HORIZONTE_ALOCACAO_DIAS = int(SIM_CFG.get('horizonte_alocacao_dias', 180))
HORIZONTE_MINIMO_DIAS = int(SIM_CFG.get('horizonte_minimo_dias', 30))
SWITCH_BUSCA_DIAS = 45  # busca diária por melhor data de switch
PERMITIR_SWITCH_ANTES_30_DIAS = False
REOTIMIZAR_POOL_SWITCH_NO_FUTURO = True
PERMITIR_SPLIT_LOTE = True  # permite dividir um lote em múltiplos produtos respeitando limites
TOP_N_ALOCACAO = 4  # quantos produtos no máximo por lote (quando split ativo)
MOSTRAR_TOP_SWITCH_CONSOLE = 2  # quantidade de alternativas exibidas por lote no console
EXIBIR_ALERTAS_FALTA_CAIXA = False  # reduz ruído de contas não cobertas no console

ORDEM_PROCESSAMENTO_SENTINELA = int(_cfg_get(["execucao", "ordem_processamento_sentinela"], 10**12))

def _normalizar_conta_processamento(conta):
    data = conta[0]
    valor = float(conta[1]) if len(conta) > 1 else 0.0
    desc = str(conta[2]) if len(conta) > 2 else ""
    lote1 = str(conta[3]).strip() if len(conta) > 3 and conta[3] is not None else ""
    lote2 = str(conta[4]).strip() if len(conta) > 4 and conta[4] is not None else ""
    ordem = int(conta[5]) if len(conta) > 5 and conta[5] is not None else ORDEM_PROCESSAMENTO_SENTINELA
    return data, valor, desc, lote1, lote2, ordem

def ordenar_contas_processamento(contas):
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

class Produto:
    def capacidade_aporte(self, valor: float) -> float:
        try:
            v=float(valor)
        except Exception:
            return 0.0
        vmin=float(getattr(self,'valor_min',0.0) or 0.0)
        vmax=float(getattr(self,'valor_max',1e18) or 1e18)
        if v < vmin:
            return 0.0
        return max(0.0, min(v, vmax))

    def aceita_aporte(self, valor: float) -> bool:
        return self.capacidade_aporte(valor) >= float(valor or 0.0) - 1e-9

    """Produto simples (CDB, LCI, LCA, etc.)"""
    def __init__(self, nome: str, taxa_base: float, taxa_bonus: float = None,
                 dias_bonus: int = 0, prazo_dias: int = 0, carencia_dias: int = 0,
                 isento_ir: bool = False, valor_min: float = 0, valor_max: float = 1e12,
                 ativo: bool = True, somente_combo: bool = False):
        self.nome         = nome
        self.taxa_base    = taxa_base          # multiplicador do CDI (ex: 1.5)
        self.taxa_bonus   = taxa_bonus if taxa_bonus is not None else taxa_base
        self.dias_bonus   = dias_bonus
        self.prazo_dias   = prazo_dias         # 0 = sem prazo (perpétuo)
        self.carencia_dias= carencia_dias
        self.isento_ir    = isento_ir
        self.valor_min    = valor_min
        self.valor_max    = valor_max
        self.ativo        = ativo               # Se ainda pode ser usado para novas aplicações

    def taxa_dia(self, idade: int) -> float:
        mult = self.taxa_bonus if idade < self.dias_bonus else self.taxa_base
        return float(mult)

class ComboProduto:
    def __init__(self, nome: str, produto_base: Produto, produto_bonus: Produto,
                 razao_base: float = 2.0, razao_bonus: float = 1.0, ativo: bool = True, somente_combo: bool = False):
        self.nome          = nome
        self.produto_base  = produto_base
        self.produto_bonus = produto_bonus
        self.razao_base    = razao_base
        self.razao_bonus   = razao_bonus
        self.valor_min     = produto_base.valor_min + produto_bonus.valor_min
        self.valor_max     = min(produto_base.valor_max, produto_bonus.valor_max) * (razao_base + razao_bonus) / razao_base
        self.ativo         = ativo

        try:
            w_sum = float(self.razao_base + self.razao_bonus)
            self.taxa_base = (float(self.produto_base.taxa_base) * self.razao_base + float(self.produto_bonus.taxa_base) * self.razao_bonus) / w_sum
            tb_base = float(getattr(self.produto_base, 'taxa_bonus', self.produto_base.taxa_base) or self.produto_base.taxa_base)
            tb_bon  = float(getattr(self.produto_bonus,'taxa_bonus', self.produto_bonus.taxa_base) or self.produto_bonus.taxa_base)
            self.taxa_bonus = (tb_base * self.razao_base + tb_bon * self.razao_bonus) / w_sum
        except Exception:
            self.taxa_base = 1.0
            self.taxa_bonus = 1.0
    def aceita_aporte(self, valor: float) -> bool:
        vb, vx = self.dividir_valor(float(valor or 0.0))
        if vb <= 0 and vx <= 0:
            return False
        return (self.produto_base.aceita_aporte(vb) if vb > 0 else True) and (self.produto_bonus.aceita_aporte(vx) if vx > 0 else True)

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

def taxa_base_efetiva(prod) -> float:
    if prod is None:
        return 1.0
    try:
        if isinstance(prod, ComboProduto):
            rb = float(getattr(prod, 'razao_base', 2.0) or 2.0)
            rx = float(getattr(prod, 'razao_bonus', 1.0) or 1.0)
            tb = float(getattr(getattr(prod, 'produto_base', None), 'taxa_base', 1.0) or 1.0)
            tx = float(getattr(getattr(prod, 'produto_bonus', None), 'taxa_base', 1.0) or 1.0)
            den = (rb + rx) if (rb + rx) > 0 else 1.0
            return (rb * tb + rx * tx) / den
    except Exception:
        pass
    try:
        return float(getattr(prod, 'taxa_base', 1.0) or 1.0)
    except Exception:
        return 1.0

def _to_float_br(valor, default=0.0):
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return default
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)
    txt = str(valor).strip()
    if not txt:
        return default
    txt = txt.replace('R$', '').replace(' ', '')
    if ',' in txt and '.' in txt:
        txt = txt.replace('.', '').replace(',', '.')
    elif ',' in txt:
        txt = txt.replace(',', '.')
    try:
        return float(txt)
    except Exception:
        return default

def _normalizar_nome_texto(valor: str) -> str:
    txt = str(valor or "").strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", txt)

def _resolver_colunas_carteira(df: pd.DataFrame) -> dict:
    cols = {
        'nome': resolver_coluna(df, 'carteira', 'nome'),
        'taxa_base': resolver_coluna(df, 'carteira', 'taxa_base'),
        'taxa_bonus': resolver_coluna(df, 'carteira', 'taxa_bonus', required=False),
        'dias_bonus': resolver_coluna(df, 'carteira', 'dias_bonus', required=False),
        'prazo_dias': resolver_coluna(df, 'carteira', 'prazo_dias', required=False),
        'carencia_dias': resolver_coluna(df, 'carteira', 'carencia_dias', required=False),
        'liquidez_dias': resolver_coluna(df, 'carteira', 'liquidez_dias', required=False),
        'isento_ir': resolver_coluna(df, 'carteira', 'isento_ir', required=False),
        'aplicacao_minima': resolver_coluna(df, 'carteira', 'aplicacao_minima', required=False),
        'aplicacao_maxima': resolver_coluna(df, 'carteira', 'aplicacao_maxima', required=False),
        'ativo': resolver_coluna(df, 'carteira', 'ativo', required=False),
        'tipo': resolver_coluna(df, 'carteira', 'tipo', required=False),
        'indexador': resolver_coluna(df, 'carteira', 'indexador', required=False),
        'fgc': resolver_coluna(df, 'carteira', 'fgc', required=False),
        'observacoes': resolver_coluna(df, 'carteira', 'observacoes', required=False),
        'banco_emissor': resolver_coluna(df, 'carteira', 'banco_emissor', required=False),
        'risco_real': resolver_coluna(df, 'carteira', 'risco_real', required=False),
        'max_usos': resolver_coluna(df, 'carteira', 'max_usos', required=False),
        'somente_combo': resolver_coluna(df, 'carteira', 'somente_combo', required=False),
        'produto_base': resolver_coluna(df, 'carteira', 'produto_base', required=False),
        'produto_bonus': resolver_coluna(df, 'carteira', 'produto_bonus', required=False),
        'ratio_base': resolver_coluna(df, 'carteira', 'ratio_base', required=False),
        'ratio_bonus': resolver_coluna(df, 'carteira', 'ratio_bonus', required=False),
        'produto_id': resolver_coluna(df, 'carteira', 'produto_id', required=False),
    }

    cols['prazo'] = cols['prazo_dias']
    cols['carencia'] = cols['carencia_dias']
    cols['valor_min'] = cols['aplicacao_minima']
    cols['valor_max'] = cols['aplicacao_maxima']
    cols['obs'] = cols['observacoes']
    cols['banco'] = cols['banco_emissor']
    cols['risco'] = cols['risco_real']

    cols['isento'] = cols['isento_ir']
    cols['minimo'] = cols['aplicacao_minima']
    cols['maximo'] = cols['aplicacao_maxima']
    cols['base'] = cols['produto_base']
    cols['bonus'] = cols['produto_bonus']

    if not cols['minimo']:
        raise ValueError("Coluna obrigatória de aplicação mínima não encontrada na aba Carteira.")

    return cols

def _parse_bool_planilha(valor, verdadeiros=('SIM', 'S', 'TRUE', '1', 'ATIVO', 'ISENTO')):
    if pd.isna(valor):
        return False
    return str(valor).upper().strip() in verdadeiros

def _parse_prazo_dias(valor):
    if pd.isna(valor):
        return 0
    txt = str(valor).strip()
    match = re.search(r'(\d+)', txt)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+\.?\d*)', txt)
    if match and 'ano' in txt.lower():
        return int(float(match.group(1)) * 365)
    return 0

def _criar_produto_simples(row, cols):
    nome = str(row[cols['nome']]).strip()
    taxa_base_val = _to_float_br(str(row[cols['taxa_base']]).replace('%', ''), default=0.0)
    taxa_base = taxa_base_val / 100.0
    taxa_bonus = taxa_base
    dias_bonus = 0
    if cols['taxa_bonus'] and pd.notna(row.get(cols['taxa_bonus'])):
        taxa_bonus_val = _to_float_br(str(row[cols['taxa_bonus']]).replace('%', ''), default=taxa_base_val)
        taxa_bonus = taxa_bonus_val / 100.0
    if cols['dias_bonus'] and pd.notna(row.get(cols['dias_bonus'])):
        dias_bonus = int(row[cols['dias_bonus']])
    prazo_dias = _parse_prazo_dias(row.get(cols['prazo'])) if cols['prazo'] else 0
    carencia_dias = _parse_prazo_dias(row.get(cols['carencia'])) if cols['carencia'] else 0
    isento = _parse_bool_planilha(row.get(cols['isento']), verdadeiros=('SIM', 'S', 'TRUE', '1', 'ISENTO')) if cols['isento'] else False
    valor_min = _to_float_br(row[cols['minimo']], default=0.0)
    valor_max = _to_float_br(row.get(cols['maximo']), default=1e12) if cols['maximo'] else 1e12
    ativo = _parse_bool_planilha(row.get(cols['ativo'])) if cols['ativo'] else True
    for _rx in EXCLUIR_PRODUTOS_REGEX:
        if re.search(_rx, nome, flags=re.IGNORECASE):
            ativo = False
            break
    return Produto(
        nome=nome, taxa_base=taxa_base, taxa_bonus=taxa_bonus, dias_bonus=dias_bonus,
        prazo_dias=prazo_dias, carencia_dias=carencia_dias, isento_ir=isento,
        valor_min=valor_min, valor_max=valor_max, ativo=ativo,
    )

def _resolver_combo_por_nome(nome_combo: str, produtos_simples: dict):
    nome_norm = _normalizar_nome_texto(nome_combo)

    def _find_produto_by_pred(pred):
        for nm, produto in produtos_simples.items():
            if isinstance(produto, Produto) and pred(_normalizar_nome_texto(nm), produto):
                return produto
        return None

    if 'combo' in nome_norm and 'picpay' in nome_norm and '100-115' in nome_norm:
        base = _find_produto_by_pred(lambda nm, p: 'picpay' in nm and '100' in nm and 'combo' not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: 'picpay' in nm and '115' in nm and 'combo' not in nm)
        return base, bonus
    if 'combo' in nome_norm and 'picpay' in nome_norm and '100-120' in nome_norm and ('6 meses' in nome_norm or '6meses' in nome_norm or '180' in nome_norm):
        base = _find_produto_by_pred(lambda nm, p: ('6 meses' in nm or '6meses' in nm) and '100' in nm and 'cdi' in nm and 'combo' not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: ('6 meses' in nm or '6meses' in nm) and '120' in nm and 'picpay' in nm and 'combo' not in nm)
        return base, bonus
    if 'combo' in nome_norm and 'picpay' in nome_norm and '100-120' in nome_norm and ('3 meses' in nome_norm or '3meses' in nome_norm or '90' in nome_norm):
        base = _find_produto_by_pred(lambda nm, p: ('3 meses' in nm or '3meses' in nm) and '100' in nm and 'cdi' in nm and 'combo' not in nm)
        bonus = _find_produto_by_pred(lambda nm, p: ('3 meses' in nm or '3meses' in nm) and '120' in nm and 'picpay' in nm and 'combo' not in nm)
        return base, bonus
    return None, None

def _carregar_produtos_da_carteira(df, cols):
    produtos_simples = {}
    combos = []
    for _, row in df.iterrows():
        nome = str(row[cols['nome']]).strip()
        if not nome:
            continue
        eh_combo = (cols['tipo'] and pd.notna(row.get(cols['tipo'])) and 'combo' in str(row[cols['tipo']]).lower()) or 'combo' in nome.lower()
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
        nome = str(row[cols['nome']]).strip()
        ativo = _parse_bool_planilha(row.get(cols['ativo'])) if cols['ativo'] else True
        base_prod = bonus_prod = None
        if cols['base'] and cols['bonus'] and row.get(cols['base']) and row.get(cols['bonus']):
            base_prod = produtos_simples.get(str(row[cols['base']]).strip())
            bonus_prod = produtos_simples.get(str(row[cols['bonus']]).strip())
        if base_prod is None or bonus_prod is None:
            base_prod, bonus_prod = _resolver_combo_por_nome(nome, produtos_simples)
        if isinstance(base_prod, Produto) and isinstance(bonus_prod, Produto):
            produtos_simples[nome] = ComboProduto(nome, base_prod, bonus_prod, ativo=ativo)
        else:
            print(f"   Aviso: Combo '{nome}' não pôde ser resolvido de forma exata. Verifique se os produtos base/bônus existem na Carteira com nomes consistentes.")
    return produtos_simples

def carregar_carteira() -> list:
    aba_carteira = nome_aba('carteira', ABA_CARTEIRA)
    df = ler_aba_excel(aba_carteira)
    print(f"[CHECK] Aba '{aba_carteira}': linhas={len(df)} | colunas={list(df.columns)}")
    df.columns = [str(c).strip() for c in df.columns]
    cols = _resolver_colunas_carteira(df)
    produtos_simples, combos = _carregar_produtos_da_carteira(df, cols)
    produtos_simples = _carregar_combos_da_carteira(combos, cols, produtos_simples)
    return list(produtos_simples.values())

# =========================================================
# 04. CDI E CALENDÁRIO
# =========================================================

def obter_historico_bcb(data_inicial_str='01/01/2025'):
    print(">>> Obtendo histórico CDI do BCB...")
    if Path(CACHE_BCB_FILE).exists():
        try:
            with open(CACHE_BCB_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            mapa = {
                datetime.strptime(k, '%Y-%m-%d').date(): v
                for k, v in cache['mapa'].items()
            }
            ultima_data_cache = max(mapa.keys())
            hoje = data_hoje_referencia()
            if (hoje - ultima_data_cache).days <= 2:
                print(f"    Cache válido: {len(mapa)} dias (até {ultima_data_cache})")
                return mapa, cache.get('ultima', TAXA_DIA_BASE)
            else:
                print(f"    Cache desatualizado (última: {ultima_data_cache})")
        except Exception as e:
            print(f"    Cache inválido: {e}")

    try:
        import requests
        hoje = data_hoje_referencia()
        url = (
            "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
            f"?formato=json&dataInicial={data_inicial_str}&dataFinal={hoje.strftime('%d/%m/%Y')}"
        )
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        r.raise_for_status()
        dados = r.json()
        if not dados:
            print("    API retornou lista vazia. Tentando fallback...")
            raise ValueError("No data")
        mapa = {}
        ultima = TAXA_DIA_BASE
        for item in dados:
            dt = datetime.strptime(item['data'], '%d/%m/%Y').date()
            taxa = float(item['valor']) / 100.0
            mapa[dt] = 1.0 + taxa
            ultima = taxa
        cache = {
            'mapa': {k.strftime('%Y-%m-%d'): v for k, v in mapa.items()},
            'ultima': ultima,
            'data_atualizacao': hoje.strftime('%Y-%m-%d'),
        }
        with open(CACHE_BCB_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        print(f"    BCB OK: {len(mapa)} dias carregados.")
        return mapa, ultima
    except Exception as e:
        print(f"    API BCB falhou: {e}")

    print("    Tentando fallback do Drive...")
    fallback_file = 'cdi_fallback.xlsx'
    if baixar_arquivo_drive(FALLBACK_BCB_URL, fallback_file):
        try:
            df = pd.read_excel(fallback_file)
            if 'data' not in df.columns or 'valor' not in df.columns:
                print("    Fallback: colunas 'data' e 'valor' não encontradas. Usando CDI fixo.")
                return {}, TAXA_DIA_BASE
            mapa = {}
            ultima = TAXA_DIA_BASE
            for _, row in df.iterrows():
                try:
                    dt = pd.to_datetime(row['data']).date()
                    taxa = float(row['valor']) / 100.0
                    mapa[dt] = 1.0 + taxa
                    ultima = taxa
                except:
                    continue
            if mapa:
                data_atual = min(mapa.keys())
                data_final = data_hoje_referencia()
                while data_atual <= data_final:
                    if data_atual not in mapa:
                        mapa[data_atual] = 1.0 + TAXA_DIA_BASE
                    data_atual += timedelta(days=1)
                print(f"    Fallback OK: {len(mapa)} dias.")
                return mapa, ultima
            else:
                print("    Fallback não contém dados válidos.")
        except Exception as e:
            print(f"    Erro ao processar fallback: {e}")

    print("    Usando CDI fixo para todos os dias.")
    return {}, TAXA_DIA_BASE

cal = Brazil()

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

def gerar_dias_sem_rendimento_bancario(ano_ini=2015, ano_fim=2035):
    dias = set()
    for ano in range(ano_ini, ano_fim + 1):
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

# =========================================================
# 05. DADOS OPERACIONAIS E REPLAY DO PASSADO
# =========================================================

def _lote_nao_investivel_mesmo_dia(lote, data_ref):
    produto = getattr(lote, 'produto', None)
    investimento_nome = str(getattr(produto, 'nome', '-') if produto is not None else '-').strip()
    return (
        investimento_nome in {'', '-', '—', '–'}
        and getattr(lote, 'data_aplicacao', None) == data_ref
    )

def simular_passado(aportes_raw: list, contas_pagas: list, bcb_map: dict, lote_produto: dict, data_referencia_snapshot: date = None):
    params_hibrido_passado, origem_params_hibrido_passado = carregar_parametros_hibrido_5p_passado()
    print(f">>> [PASSADO-HIBRIDO] parâmetros locais carregados de: {origem_params_hibrido_passado}")

    lotes_por_id = {}
    for aporte in aportes_raw:
        if len(aporte) >= 5:
            d, val, lid, _ja_aplicado, nao_disponivel_para_aporte = aporte[:5]
        else:
            d, val, lid, _ja_aplicado = aporte[:4]
            nao_disponivel_para_aporte = False
        lid = str(lid).strip()
        produto_lote = lote_produto.get(lid)
        taxa_base_lote = float(getattr(produto_lote, 'taxa_base', TAXA_BASE_DEFAULT) if produto_lote is not None else TAXA_BASE_DEFAULT)
        taxa_bonus_lote = float(getattr(produto_lote, 'taxa_bonus', TAXA_BONUS_DEFAULT) if produto_lote is not None else TAXA_BONUS_DEFAULT)
        dias_bonus_lote = int(getattr(produto_lote, 'dias_bonus', DIAS_BONUS_DEFAULT) if produto_lote is not None else DIAS_BONUS_DEFAULT)
        if nao_disponivel_para_aporte and produto_lote is None:
            taxa_base_lote = 0.0
            taxa_bonus_lote = 0.0
            dias_bonus_lote = 0
        meta_lote = {
            'produto': produto_lote,
            'investimento': getattr(produto_lote, 'nome', '-') if produto_lote is not None else '-',
            'data_base_fiscal': d,
            'fator_acumulado_inicial': 1.0,
            'taxa_base_cdi': taxa_base_lote,
            'taxa_bonus_cdi': taxa_bonus_lote,
            'dias_bonus': dias_bonus_lote,
            'principal_remanescente': float(val),
            'carencia_ate': (d + timedelta(days=int(getattr(produto_lote, 'carencia_dias', 0) or 0))) if produto_lote is not None and int(getattr(produto_lote, 'carencia_dias', 0) or 0) > 0 else None,
            'nao_disponivel_para_aporte': bool(nao_disponivel_para_aporte),
        }
        lote = criar_lote_de_aporte(d, val, lid, meta_lote)
        lote.nao_disponivel_para_aporte = bool(nao_disponivel_para_aporte)
        lote.data_efetiva_snapshot_lote = d
        lotes_por_id[lid] = lote

    contas_pagas = ordenar_contas_processamento(contas_pagas)
    log_passado = []
    tolerancia_zeramento = max(float(globals().get('VALOR_MINIMO_LOTE_ATIVO', 0.01) or 0.01), 5.0)
    if not lotes_por_id:
        return [], [], pd.DataFrame(), pd.DataFrame()
    if not contas_pagas:
        lotes_final = list(lotes_por_id.values())
        data_snapshot = data_referencia_snapshot or min(getattr(l, 'data_aplicacao', None) for l in lotes_final)
        estado_lotes_passado = pd.DataFrame([serializar_lote_remanescente(l, data_snapshot) for l in lotes_final])
        return lotes_final, [], estado_lotes_passado, pd.DataFrame()

    data_inicial = min(l.data_aplicacao for l in lotes_por_id.values())
    ultima_conta_paga = max(c[0] for c in contas_pagas)
    data_final = max(ultima_conta_paga, data_referencia_snapshot) if data_referencia_snapshot is not None else ultima_conta_paga
    contas_por_data = {}
    for conta in contas_pagas:
        contas_por_data.setdefault(conta[0], []).append(conta)

    data_atual = data_inicial
    while data_atual <= data_final:
        contas_do_dia = contas_por_data.get(data_atual, [])
        lotes_legados_explicitos_do_dia = {
            str(lid).strip()
            for conta in contas_do_dia
            for lid in _normalizar_conta_processamento(conta)[3:5]
            if lid and str(lid).strip().lower() != 'nan'
        }

        if is_dia_rendimento(data_atual, bcb_map):
            lotes_para_capitalizar_antes = [l for l in lotes_por_id.values() if str(getattr(l, 'id', '')).strip() not in lotes_legados_explicitos_do_dia]
            atualizar_saldo_lotes_no_dia(lotes_para_capitalizar_antes, data_atual, bcb_map, TAXA_DIA_BASE)
            for l in lotes_para_capitalizar_antes:
                if not l.esgotado and l.saldo_bruto > 0 and l.data_aplicacao <= data_atual:
                    l.data_efetiva_snapshot_lote = data_atual

        lotes_usados_no_dia, lotes_nao_investiveis_usados_no_mesmo_dia = set(), set()
        for conta_item in contas_do_dia:
            data, valor, desc, lote1, lote2, ordem_processamento = _normalizar_conta_processamento(conta_item)
            falta = float(valor)
            lotes_usados = [str(l).strip() for l in (lote1, lote2) if l and str(l).strip().lower() != 'nan']
            lotes_usados_set = set(lotes_usados)
            disponiveis = [
                l for l in lotes_por_id.values()
                if not l.esgotado and float(getattr(l, 'saldo_bruto', 0.0) or 0.0) > 0.01
                and getattr(l, 'data_aplicacao', data_atual) <= data_atual
                and not (getattr(l, 'carencia_ate', None) and data_atual < getattr(l, 'carencia_ate'))
            ]
            disponiveis_admissiveis = [l for l in disponiveis if str(getattr(l, 'id', '')).strip() in lotes_usados_set] if lotes_usados_set else list(disponiveis)
            saques_planejados = []
            if not lotes_usados_set and params_hibrido_passado is not None and disponiveis_admissiveis:
                valores_otimos = resolver_hibrido_5p(disponiveis_admissiveis, float(falta), data_atual, params_hibrido_passado, data_final, bcb_map, TAXA_DIA_BASE)
                saques_planejados = [(l, min(float(v), float(l.saldo_bruto)), 'hibrido') for l, v in zip(disponiveis_admissiveis, valores_otimos) if float(v or 0.0) > VALOR_MINIMO_RESGATE_BRUTO]
            else:
                saques_planejados = [(lotes_por_id[id_lote], None, 'legacy') for id_lote in lotes_usados if id_lote in lotes_por_id and not lotes_por_id[id_lote].esgotado]

            for l, val_b, modo_saque in saques_planejados:
                if falta <= 0.001:
                    break
                lotes_usados_no_dia.add(l.id)
                if _lote_nao_investivel_mesmo_dia(l, data_atual):
                    lotes_nao_investiveis_usados_no_mesmo_dia.add(l.id)
                if modo_saque == 'legacy':
                    valor_liquido_alvo = min(_money_round_half_up(float(falta)), _money_round_half_up(float(l.valor_liquido_hoje(data_atual) or 0.0)))
                    if valor_liquido_alvo <= 0:
                        continue
                    movimento = executar_saque_lote(l, valor_liquido_alvo, data_atual)
                else:
                    fator = l.get_fator_liquido(data_atual)
                    if fator <= 0:
                        continue
                    valor_liquido_alvo = min(round(float(val_b) * float(fator), 2), round(float(falta), 2))
                    movimento = executar_saque_lote(l, valor_liquido_alvo, data_atual)
                if movimento is None:
                    continue

                falta -= float(movimento['liquido'])
                l.data_efetiva_snapshot_lote = data_atual
                log_passado.append({
                    'Data': data_atual,
                    'Conta': desc,
                    'Lote': l.id,
                    'Saldo Antes': float(movimento['saldo_antes']),
                    'Bruto': float(movimento['bruto']),
                    'Imposto': float(movimento['imposto']),
                    'Liquido': float(movimento['liquido']),
                    'Dias Corridos': (data_atual - l.data_aplicacao).days,
                    'Dias Úteis': contar_dias_rendimento(l.data_aplicacao, data_atual, bcb_map),
                    'Saldo Remanescente': float(movimento['saldo_remanescente']),
                })

        if is_dia_rendimento(data_atual, bcb_map) and lotes_legados_explicitos_do_dia:
            lotes_para_capitalizar_depois = [
                l for l in lotes_por_id.values()
                if str(getattr(l, 'id', '')).strip() in lotes_legados_explicitos_do_dia
                and str(getattr(l, 'id', '')).strip() not in lotes_usados_no_dia
                and not getattr(l, 'esgotado', False)
                and float(getattr(l, 'saldo_bruto', 0.0) or 0.0) > 0.0
                and getattr(l, 'data_aplicacao', data_atual) <= data_atual
            ]
            atualizar_saldo_lotes_no_dia(lotes_para_capitalizar_depois, data_atual, bcb_map, TAXA_DIA_BASE)
            for l in lotes_para_capitalizar_depois:
                l.data_efetiva_snapshot_lote = data_atual

        for lote_id_force in lotes_nao_investiveis_usados_no_mesmo_dia:
            lforce = lotes_por_id.get(lote_id_force)
            if lforce is None:
                continue
            lforce.saldo_bruto = 0.0
            lforce.principal_remanescente = 0.0
            lforce.esgotado = True
            lforce.data_efetiva_snapshot_lote = data_atual

        for lote_id_trunc in lotes_usados_no_dia:
            ltr = lotes_por_id.get(lote_id_trunc)
            if ltr is None:
                continue
            if float(getattr(ltr, 'saldo_bruto', 0.0) or 0.0) <= tolerancia_zeramento:
                ltr.saldo_bruto = 0.0
                ltr.principal_remanescente = 0.0
                ltr.esgotado = True
                ltr.data_efetiva_snapshot_lote = data_atual

        data_atual += timedelta(days=1)

    lotes_final = list(lotes_por_id.values())
    estado_lotes_passado = pd.DataFrame([serializar_lote_remanescente(l, data_final) for l in lotes_final])
    return lotes_final, log_passado, estado_lotes_passado, pd.DataFrame()

def _ingestao_passado(produtos_dict, hoje):
    df_inv = ler_aba_excel(ABA_INVENTARIO)
    print(f"\n[CHECK] Aba '{ABA_INVENTARIO}': linhas={len(df_inv)} | colunas={list(df_inv.columns)}")
    col_id = 'Lote (ID)' if 'Lote (ID)' in df_inv.columns else 'ID'
    df_inv = df_inv.dropna(subset=[col_id, 'Data Aplicação', 'Valor Original']).copy()

    def _classificar_investimento_inventario(valor):
        if pd.isna(valor):
            return '', False
        txt = str(valor).strip()
        if txt in {'-', '—', '–'}:
            return '', True
        if txt.lower() in {'', 'none', 'nan'}:
            return '', False
        return txt, False

    lote_produto, aportes_raw = {}, []
    for _, row in df_inv.iterrows():
        lote_id = str(row[col_id]).strip()
        produto_nome, nao_disponivel_para_aporte = _classificar_investimento_inventario(row.get('Investimento'))
        lote_produto[lote_id] = produtos_dict.get(produto_nome) if produto_nome else None
        aportes_raw.append((
            pd.to_datetime(row['Data Aplicação']).date(),
            float(row['Valor Original']),
            lote_id,
            bool(produto_nome),
            bool(nao_disponivel_para_aporte),
        ))

    aba_gastos = nome_aba('despesas', ABA_GASTOS)
    df_gastos = ler_aba_excel(aba_gastos)
    print(f"[CHECK] Aba '{aba_gastos}': linhas={len(df_gastos)} | colunas={list(df_gastos.columns)}")
    df_gastos.columns = [str(c).strip() for c in df_gastos.columns]
    col_data = resolver_coluna(df_gastos, 'despesas', 'data')
    col_valor = resolver_coluna(df_gastos, 'despesas', 'valor')
    col_desc = resolver_coluna(df_gastos, 'despesas', 'descricao', required=False) or '__descricao_padrao__'
    col_pago = resolver_coluna(df_gastos, 'despesas', 'pago', required=False)
    col_lote1 = resolver_coluna(df_gastos, 'despesas', 'lote_usado_1', required=False)
    col_lote2 = resolver_coluna(df_gastos, 'despesas', 'lote_usado_2', required=False)
    if col_desc == '__descricao_padrao__':
        df_gastos[col_desc] = 'Despesa Diversa'
    df_gastos[col_data] = pd.to_datetime(df_gastos[col_data], errors='coerce').dt.date
    df_gastos[col_valor] = pd.to_numeric(df_gastos[col_valor], errors='coerce')
    df_gastos = df_gastos.dropna(subset=[col_data, col_valor]).copy()

    def _valor_lote(row, col):
        if col is None:
            return ''
        v = row.get(col, '')
        if pd.isna(v):
            return ''
        s = str(v).strip()
        return '' if s.lower() in {'', 'nan', 'none'} else s

    contas_pagas, contas_nao_pagas = [], []
    for ordem, (_, row) in enumerate(df_gastos.iterrows(), start=1):
        conta = (row[col_data], float(row[col_valor]), str(row.get(col_desc, ''))[:100], _valor_lote(row, col_lote1), _valor_lote(row, col_lote2), ordem)
        pago = str(row.get(col_pago, '')).upper().strip() == 'OK' if col_pago is not None else False
        if pago and conta[0] <= hoje:
            contas_pagas.append(conta)
        elif (not pago) and conta[0] >= hoje:
            contas_nao_pagas.append(conta)

    contas_pagas = ordenar_contas_processamento(contas_pagas)
    contas_nao_pagas = ordenar_contas_processamento(contas_nao_pagas)
    data_referencia_snapshot = min(hoje, max(c[0] for c in contas_pagas) + timedelta(days=1)) if contas_pagas else hoje
    return lote_produto, aportes_raw, contas_pagas, contas_nao_pagas, data_referencia_snapshot

def _montar_snapshot_passado(lotes_todos, lote_produto, aportes_raw, data_referencia_snapshot):
    lotes_extra = []
    for aporte in aportes_raw:
        if len(aporte) >= 5:
            data_apl, valor, lote_id, ja_aplicado, nao_disponivel_para_aporte = aporte[:5]
        else:
            data_apl, valor, lote_id, ja_aplicado = aporte[:4]
            nao_disponivel_para_aporte = False
        if ja_aplicado or nao_disponivel_para_aporte:
            continue
        novo = Lote(lote_id, max(data_apl, data_referencia_snapshot), float(valor), produto=None, pendente_aporte=True)
        novo.nao_disponivel_para_aporte = False
        lotes_extra.append(novo)
    lotes_todos = list(lotes_todos) + lotes_extra
    for lote in lotes_todos:
        if lote.id in lote_produto:
            lote.produto = lote_produto[lote.id]
    lotes_passados = [l for l in lotes_todos if l.saldo_bruto > 0.01 and l.data_aplicacao <= data_referencia_snapshot and not getattr(l, 'pendente_aporte', False)]
    lotes_futuros = [l for l in lotes_todos if (l.data_aplicacao > data_referencia_snapshot or getattr(l, 'pendente_aporte', False)) and not getattr(l, 'nao_disponivel_para_aporte', False)]
    return lotes_passados, lotes_futuros

def carregar_inventario_e_gastos(produtos: list, bcb_map: dict):
    produtos_dict = {p.nome: p for p in produtos}
    hoje = data_hoje_referencia()
    lote_produto, aportes_raw, contas_pagas, contas_nao_pagas, data_referencia_snapshot = _ingestao_passado(produtos_dict, hoje)
    print("\n>>> Simulando pagamentos passados...")
    lotes_todos, log_passado, estado_lotes_passado, _ = simular_passado(aportes_raw, contas_pagas, bcb_map, lote_produto, data_referencia_snapshot=data_referencia_snapshot)
    lotes_passados, lotes_futuros = _montar_snapshot_passado(lotes_todos, lote_produto, aportes_raw, data_referencia_snapshot)
    return lotes_passados, lotes_futuros, contas_nao_pagas, log_passado, data_referencia_snapshot, estado_lotes_passado

# =========================================================
# 06. SWITCHING SHADOW E RECONCILIAÇÃO
# =========================================================

def _money_round_half_up(valor: float) -> float:
    return float(Decimal(str(float(valor or 0.0))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

dinheiro_round = _money_round_half_up

def obter_data_fiscal_liquido_relatorio(mapa_bcb, data_fiscal_relatorio, data_base_fiscal):
    data_fiscal = max((d for d in (mapa_bcb or {}) if d <= data_fiscal_relatorio), default=data_fiscal_relatorio)
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
        'Nao Disponivel para Aporte': bool(getattr(lote, 'nao_disponivel_para_aporte', False)),
        'meta': {
            'carencia_ate': getattr(lote, 'carencia_ate', None),
            'produto_isento_ir': bool(getattr(prod, 'isento_ir', False) if prod is not None else False),
            'data_efetiva_snapshot_lote': data_efetiva_lote,
            'nao_disponivel_para_aporte': bool(getattr(lote, 'nao_disponivel_para_aporte', False)),
        }
    }

def obter_data_referencia_relatorio_local(mapa_bcb, data_referencia=None):
    return data_hoje_referencia() if data_referencia is None else data_referencia

def listar_datas_economicas_relatorio(data_snapshot_lote, data_referencia_efetiva, bcb_map=None, data_aplicacao=None):
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

def reconstruir_lote_para_relatorio(st, produtos_por_nome=None):
    nome_label = str(st.get('Investimento', '-') or '-').strip()
    data_aplic = st.get('Data Aplicação')
    data_base_fiscal = st.get('Data Base Fiscal') or data_aplic
    valor_inicial = float(st.get('Valor Inicial', 0.0) or 0.0)
    fator_acum = float(st.get('Fator Acumulado', 1.0) or 1.0)
    principal_rem = float(st.get('Principal Remanescente', valor_inicial) or valor_inicial)
    carencia_ate = st.get('Carência Até')

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
    if lote is None or getattr(lote, 'esgotado', False):
        return lote

    data_snapshot_lote = getattr(lote, 'data_efetiva_snapshot_lote', None)
    if data_snapshot_lote is None:
        data_snapshot_lote = data_corte_passado
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

ORACLE_SITUACAO_ATUAL_2026_03_23 = {
    "Lote 4000 fev.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 6630,64 fev.": {"bruto_esperado": 3207.18, "liquido_esperado": 3192.61},
    "Lote 4124,75 fev.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 5400 fev.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 10342 fev.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 2063,11 fev.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 3000 mar. V": {"bruto_esperado": 3053.53, "liquido_esperado": 3024.89},
    "Lote 3000 mar. B": {"bruto_esperado": 3049.66, "liquido_esperado": 3021.94},
    "Lote 1000 mar.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 900 mar.": {"bruto_esperado": 0.00, "liquido_esperado": 0.00},
    "Lote 8500 mar.": {"bruto_esperado": 8641.61, "liquido_esperado": 8608.16},
}

VALOR_MINIMO_LOTE_ATIVO = globals().get('VALOR_MINIMO_LOTE_ATIVO', 0.01)
VALOR_MINIMO_RESGATE_BRUTO = globals().get('VALOR_MINIMO_RESGATE_BRUTO', 0.01)

def acumular_saques_por_lote(log_passado):
    total_sacado_bruto = {}
    total_sacado_liquido = {}
    for x in (log_passado or []):
        if not isinstance(x, dict):
            continue
        lote_id = str(x.get('Lote') or x.get('Lote ID') or '').strip()
        if not lote_id:
            continue
        bruto = x.get('Bruto Sacado', x.get('Bruto', 0.0)) or 0.0
        liquido = x.get('Liquido Sacado', x.get('Liquido', 0.0)) or 0.0
        total_sacado_bruto[lote_id] = float(total_sacado_bruto.get(lote_id, 0.0)) + float(bruto)
        total_sacado_liquido[lote_id] = float(total_sacado_liquido.get(lote_id, 0.0)) + float(liquido)
    return total_sacado_bruto, total_sacado_liquido

def gerar_relatorio_situacao_atual(
    lotes_hoje,
    estado_lotes_passado,
    log_passado,
    valores_originais,
    mapa_bcb,
    data_referencia=None,
):
    if data_referencia is None:
        data_referencia = data_hoje_referencia()

    data_referencia_efetiva = obter_data_referencia_relatorio_local(mapa_bcb, data_referencia)

    estado_rows = (
        estado_lotes_passado.to_dict('records')
        if isinstance(estado_lotes_passado, pd.DataFrame)
        else list(estado_lotes_passado or [])
    )
    if not estado_rows:
        return pd.DataFrame()

    total_sacado_bruto_passado, total_sacado_liquido_passado = acumular_saques_por_lote(log_passado or [])
    data_corte_passado = max(
        (x.get('Data') for x in (log_passado or []) if isinstance(x, dict) and x.get('Data') is not None),
        default=None
    )
    if data_corte_passado is None:
        data_corte_passado = min(
            pd.to_datetime(st.get('Data Base Fiscal', st.get('Data Aplicação')), errors='coerce').date()
            for st in estado_rows
            if not pd.isna(pd.to_datetime(st.get('Data Base Fiscal', st.get('Data Aplicação')), errors='coerce'))
        )

    produtos_por_nome = {}
    for p in globals().get('PRODUTOS_GLOBAIS_SIMULACAO', []) or []:
        nome = str(getattr(p, 'nome', '') or '').strip()
        if nome:
            produtos_por_nome[nome] = p
    for l in lotes_hoje or []:
        prod = getattr(l, 'produto', None)
        nome = str(getattr(prod, 'nome', '') or '').strip()
        if prod is not None and nome:
            produtos_por_nome[nome] = prod

    relatorio = []
    for st in estado_rows:
        lote_id = str(st.get('Lote ID', '')).strip()
        if not lote_id:
            continue

        dt_apl = pd.to_datetime(st.get('Data Aplicação', st.get('Data Base Fiscal')), errors='coerce')
        dt_base = pd.to_datetime(st.get('Data Base Fiscal', st.get('Data Aplicação')), errors='coerce')
        if pd.isna(dt_apl) or pd.isna(dt_base):
            continue

        data_aplicacao_original = dt_apl.date()
        data_base_fiscal = dt_base.date()

        lotex = reconstruir_lote_para_relatorio(st, produtos_por_nome)
        if lotex is None:
            continue

        lotex = atualizar_lote_reconstruido_ate_data(
            lotex,
            data_corte_passado,
            data_referencia_efetiva,
            mapa_bcb or {}
        )

        saldo_bruto_atual = dinheiro_round(float(max(getattr(lotex, 'saldo_bruto', 0.0) or 0.0, 0.0)))

        data_fiscal_relatorio = data_referencia_efetiva
        if data_corte_passado is not None and data_corte_passado > data_fiscal_relatorio:
            data_fiscal_relatorio = data_corte_passado

        data_fiscal_para_liquido = obter_data_fiscal_liquido_relatorio(
            mapa_bcb,
            data_fiscal_relatorio,
            data_base_fiscal
        )

        saldo_liquido_atual = dinheiro_round(
            float(calcular_liquido_atual_relatorio(lotex, saldo_bruto_atual, data_fiscal_para_liquido) or 0.0)
        )

        val_orig = float(valores_originais.get(lote_id, st.get('Valor Inicial', 0.0) or 0.0))
        total_sacado_bruto = float(total_sacado_bruto_passado.get(lote_id, 0.0) or 0.0)
        total_sacado_liquido = float(total_sacado_liquido_passado.get(lote_id, 0.0) or 0.0)

        dias_hoje = (data_fiscal_relatorio - data_base_fiscal).days
        dias_uteis_hoje = contar_dias_rendimento(data_base_fiscal, data_fiscal_relatorio, mapa_bcb)
        patrimonio_liquido_ate_hoje = dinheiro_round(saldo_liquido_atual + total_sacado_liquido)
        saldo_se_dinheiro_ficasse_parado = max(val_orig - total_sacado_liquido, 0.0)
        ganho_otimizacao_vs_dinheiro_parado = dinheiro_round(saldo_liquido_atual - saldo_se_dinheiro_ficasse_parado)
        rent_bruta = ((saldo_bruto_atual + total_sacado_bruto) / val_orig - 1) * 100 if val_orig > 0 else 0.0
        rent_liquida = (patrimonio_liquido_ate_hoje / val_orig - 1) * 100 if val_orig > 0 else 0.0

        relatorio.append({
            "Lote ID": lote_id,
            "Carteira": str(getattr(lotex, 'investimento', st.get('Investimento', '-')) or '-'),
            "Data Aplicação": data_aplicacao_original,
            "Data Base Fiscal": data_base_fiscal,
            "Dias Corridos até Hoje": dias_hoje,
            "Dias Úteis até Hoje": dias_uteis_hoje,
            "Valor Original (R$)": dinheiro_round(val_orig),
            "Total Bruto Sacado (R$)": dinheiro_round(total_sacado_bruto),
            "Total Líquido Sacado (R$)": dinheiro_round(total_sacado_liquido),
            "Saldo Bruto Atual (R$)": saldo_bruto_atual,
            "Saldo Líquido Atual (R$)": saldo_liquido_atual,
            "Patrimônio Líquido até Hoje (R$)": patrimonio_liquido_ate_hoje,
            "Ganho da Otimização vs Dinheiro Parado (R$)": ganho_otimizacao_vs_dinheiro_parado,
            "Rendimento Bruto Acumulado (%)": round(rent_bruta, 2),
            "Rendimento Líquido Acumulado (%)": round(rent_liquida, 2),
            "_obj_lote_relatorio": lotex,
        })

    df_relatorio_atual = pd.DataFrame(relatorio)
    if df_relatorio_atual.empty:
        return df_relatorio_atual

    total_row = {
        "Lote ID": "TOTAL",
        "Carteira": np.nan,
        "Data Aplicação": np.nan,
        "Data Base Fiscal": np.nan,
        "Dias Corridos até Hoje": np.nan,
        "Dias Úteis até Hoje": np.nan,
        "Valor Original (R$)": dinheiro_round(df_relatorio_atual["Valor Original (R$)"].sum()),
        "Total Bruto Sacado (R$)": dinheiro_round(df_relatorio_atual["Total Bruto Sacado (R$)"].sum()),
        "Total Líquido Sacado (R$)": dinheiro_round(df_relatorio_atual["Total Líquido Sacado (R$)"].sum()),
        "Saldo Bruto Atual (R$)": dinheiro_round(df_relatorio_atual["Saldo Bruto Atual (R$)"].sum()),
        "Saldo Líquido Atual (R$)": dinheiro_round(df_relatorio_atual["Saldo Líquido Atual (R$)"].sum()),
        "Patrimônio Líquido até Hoje (R$)": dinheiro_round(df_relatorio_atual["Patrimônio Líquido até Hoje (R$)"].sum()),
        "Ganho da Otimização vs Dinheiro Parado (R$)": dinheiro_round(df_relatorio_atual["Ganho da Otimização vs Dinheiro Parado (R$)"].sum()),
        "Rendimento Bruto Acumulado (%)": np.nan,
        "Rendimento Líquido Acumulado (%)": np.nan,
        "_obj_lote_relatorio": None,
    }

    df_relatorio_atual = pd.concat([df_relatorio_atual, pd.DataFrame([total_row])], ignore_index=True)
    return df_relatorio_atual

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

# =========================================================
# 07. NÚCLEO FINANCEIRO
# =========================================================

def _taxa_ir(dias: int, isento: bool = False) -> float:
    if isento:
        return 0.0
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15

def _taxa_iof(dias: int) -> float:
    if dias < 30:
        return float(IOF_TABLE[dias])
    return 0.0

def _fator_liquido(fator_acumulado: float, dias_vida: int, isento: bool = False) -> float:
    if fator_acumulado <= 1.0:
        return 1.0
    iof = _taxa_iof(dias_vida)
    ir  = _taxa_ir(dias_vida, isento)
    ratio_lucro  = 1.0 - (1.0 / fator_acumulado)
    taxa_efetiva = iof + (1 - iof) * ir
    return 1.0 - ratio_lucro * taxa_efetiva

def criar_lote_de_aporte(dt, val, id_l, meta=None):
    meta = meta or {}
    produto_meta = meta.get('produto')
    lote = Lote(
        id_l, dt, val,
        produto=produto_meta,
        carencia_ate=meta.get('carencia_ate', None),
        data_base_fiscal=meta.get('data_base_fiscal', dt),
        fator_acumulado_inicial=meta.get('fator_acumulado_inicial', 1.0),
        taxa_base_cdi=meta.get('taxa_base_cdi', TAXA_BASE_DEFAULT),
        taxa_bonus_cdi=meta.get('taxa_bonus_cdi', TAXA_BONUS_DEFAULT),
        dias_bonus=meta.get('dias_bonus', DIAS_BONUS_DEFAULT),
        principal_remanescente_inicial=meta.get('principal_remanescente', meta.get('principal_remanescente_inicial', float(val))),
    )
    lote.investimento = str(meta.get('investimento', getattr(produto_meta, 'nome', '') or '') or '')
    lote.nao_disponivel_para_aporte = bool(meta.get('nao_disponivel_para_aporte', False))
    if getattr(lote, 'investimento', '') == '' and produto_meta is not None:
        lote.investimento = str(getattr(produto_meta, 'nome', '') or '')
    if meta.get('produto_isento_ir', None) is not None and produto_meta is None:
        lote.produto_isento_ir = bool(meta.get('produto_isento_ir'))
    return lote

def atualizar_saldo_lotes_no_dia(lotes_ativos, data_atual, bcb_map=None, taxa_proj=None):
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
        if getattr(lote, 'esgotado', False) or float(getattr(lote, 'saldo_bruto', 0.0) or 0.0) <= 0.0:
            continue
        lote.atualizar_juros(data_atual, taxa_dia)

def executar_saque_lote(lote, valor_liquido_alvo, data_atual):
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
        'lote': lote,
        'saldo_antes': saldo_antes,
        'fator_liquido': float(fator),
        'bruto': efetivo,
        'liquido': liquido,
        'imposto': imposto,
        'saldo_remanescente': float(lote.saldo_bruto),
    }

class Lote:
    def __init__(self, id_lote, data_aplicacao: date, valor_inicial: float,
                 produto: Produto = None,
                 carencia_ate: date = None, data_base_fiscal: date = None,
                 fator_acumulado_inicial: float = 1.0, pendente_aporte: bool = False,
                 principal_remanescente_inicial: float = None,
                 taxa_base_cdi: float = None, taxa_bonus_cdi: float = None, dias_bonus: int = None):

        self.id                 = str(id_lote).strip()
        self.data_aplicacao     = data_aplicacao
        self.data_base_fiscal   = data_base_fiscal or data_aplicacao
        self.valor_inicial      = float(valor_inicial)
        self.saldo_bruto        = float(valor_inicial)
        self.fator_acumulado    = max(1.0, float(fator_acumulado_inicial))
        self.principal_remanescente = float(
            self.valor_inicial if principal_remanescente_inicial is None else principal_remanescente_inicial
        )
        self.esgotado           = False
        self.vezes_usado        = 0
        self.total_bruto_sacado = 0.0
        self.total_imposto_pago = 0.0
        self.total_liquido_sacado = 0.0
        self.produto            = produto
        self.carencia_ate       = carencia_ate
        self.historico_switches = []            # [(data, nome_produto, valor_liquido)]
        self.switch_agendado    = None          # (data_switch: date, produto_alvo: Produto)
        self.switch_plano       = None          # plano de split do switch: [(Produto|ComboProduto, valor_liquido)]

        taxa_base_prod = float(getattr(produto, 'taxa_base', TAXA_BASE_DEFAULT) or TAXA_BASE_DEFAULT) if produto is not None else TAXA_BASE_DEFAULT
        taxa_bonus_prod = float(getattr(produto, 'taxa_bonus', taxa_base_prod) or taxa_base_prod) if produto is not None else TAXA_BONUS_DEFAULT
        dias_bonus_prod = int(getattr(produto, 'dias_bonus', DIAS_BONUS_DEFAULT) or DIAS_BONUS_DEFAULT) if produto is not None else DIAS_BONUS_DEFAULT

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
        if self.taxa_bonus_cdi > 0.0 and idade < self.dias_bonus:
            mult = self.taxa_bonus_cdi
        else:
            mult = self.taxa_base_cdi
        fator_dia = (1.0 + taxa_diaria_decimal) ** mult
        self.saldo_bruto = _money_round_half_up(self.saldo_bruto * fator_dia)
        self.fator_acumulado *= fator_dia

    def get_fator_liquido(self, data_resgate: date) -> float:
        dias_vida = (data_resgate - self.data_base_fiscal).days
        if dias_vida < 0:
            return 0.0
        if self.saldo_bruto <= 0:
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
            self.esgotado    = True
            self.vezes_usado += 1
            self.total_bruto_sacado += sacado
            return sacado
        if self.saldo_bruto <= 0:
            return 0.0
        valor_bruto       = _money_round_half_up(float(valor_bruto))
        sacado            = valor_bruto
        saldo_antes       = max(float(self.saldo_bruto), 0.0)
        proporcao_sacada  = min(max((valor_bruto / saldo_antes), 0.0), 1.0) if saldo_antes > 0 else 1.0
        principal_sacado  = round(float(getattr(self, 'principal_remanescente', self.valor_inicial)) * proporcao_sacada, 10)
        self.principal_remanescente = max(
            round(float(getattr(self, 'principal_remanescente', self.valor_inicial)) - principal_sacado, 10),
            0.0
        )
        self.saldo_bruto  = _money_round_half_up(self.saldo_bruto - valor_bruto)
        self.vezes_usado        += 1
        self.total_bruto_sacado += sacado
        return sacado

    def resgatar_total(self, data_resgate: date):
        bruto = self.saldo_bruto
        if bruto <= 0:
            return 0.0, 0.0
        fator   = self.get_fator_liquido(data_resgate)
        liquido = bruto * fator
        imposto = bruto - liquido
        self.saldo_bruto            = 0.0
        self.principal_remanescente = 0.0
        self.esgotado               = True
        self.vezes_usado           += 1
        self.total_bruto_sacado    += bruto
        self.total_imposto_pago    += imposto
        self.total_liquido_sacado  += liquido
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
                l_base = Lote(base_id, data_switch, val_base, produto=novo_produto.produto_base,
                              carencia_ate=carencia_base, data_base_fiscal=data_switch)
                novos.append(l_base)
            if val_bonus > 0:
                bonus_id = f"{self.id}_sw_bonus_{data_switch.strftime('%Y%m%d')}"
                carencia_bonus = None
                if novo_produto.produto_bonus.carencia_dias > 0:
                    carencia_bonus = data_switch + timedelta(days=novo_produto.produto_bonus.carencia_dias)
                l_bonus = Lote(bonus_id, data_switch, val_bonus, produto=novo_produto.produto_bonus,
                               carencia_ate=carencia_bonus, data_base_fiscal=data_switch)
                novos.append(l_bonus)
            return novos
        else:
            novo_id = f"{self.id}_sw_{data_switch.strftime('%Y%m%d')}"
            carencia_ate = None
            if novo_produto.carencia_dias > 0:
                carencia_ate = data_switch + timedelta(days=novo_produto.carencia_dias)
            novo_lote = Lote(
                id_lote          = novo_id,
                data_aplicacao   = data_switch,
                valor_inicial    = liquido,
                produto          = novo_produto,
                carencia_ate     = carencia_ate,
                data_base_fiscal = data_switch,
            )
            return [novo_lote]

# =========================================================
# 08. OTIMIZAÇÃO E VALIDAÇÃO
# =========================================================

SWITCH_MIN_UPGRADE_REL = 0.0   # 0.0 = exige apenas taxa_destino > taxa_origem

SWITCH_MIN_HOLD_DIAS = 30

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
                        p_novo = _escolher_produto_rolagem(valor_liq, d)
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

def gerar_top_planos_alocacao(data_ref: date, total_liq: float, produtos: list, bcb_map: dict, contas_fut: list, top_k: int = 6):
    total_liq = float(total_liq)
    if total_liq <= 0.01:
        return []

    candidatos = []
    for p in produtos:
        if not getattr(p, 'ativo', True):
            continue
        if getattr(p, 'somente_combo', False):
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
        return sum(simular_valor_final_produto(pp, data_ref, vv, data_ref + timedelta(days=365), bcb_map, produtos_rolagem=produtos)
                   for pp, vv in pl if vv > 0.01)

    planos = []

    pl_best, _, _ = alocar_lote_por_otimizacao(data_ref, data_ref, total_liq, produtos, bcb_map, contas_fut, foco_rendimento=True, max_produtos=3)
    if pl_best:
        planos.append(pl_best)

    for p in candidatos[:10]:
        if p.aceita_aporte(total_liq):
            planos.append([(p, total_liq)])

    top = candidatos[:12]
    for p in top:
        vmax = float(getattr(p, 'valor_max', 1e18) or 1e18)
        vmin = float(getattr(p, 'valor_min', 0.0) or 0.0)
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

def estimar_liquido_lote_sem_pagamentos(lote, data_ref, bcb_map=None):
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

IR_FAIXAS = {
    180:  {'delta': 0.025},
    360:  {'delta': 0.025},
    720:  {'delta': 0.025},
    9999: {'delta': 0.000},
}

def get_score_economico(lote: Lote, data_hoje: date, dias_cliff: int = 10) -> float:
    dias = (data_hoje - lote.data_aplicacao).days
    if dias < 30:
        return 1e9 + (30 - dias)

    fator = lote.get_fator_liquido(data_hoje)
    if fator <= 0.001:
        return 1e9

    custo_fiscal     = 1.0 / fator
    penalidade_cliff = 0.0
    for threshold, info in sorted(IR_FAIXAS.items()):
        if dias < threshold:
            dias_ate = threshold - dias
            if dias_ate <= dias_cliff:
                ratio_lucro = max(0.0, 1.0 - (1.0 / lote.fator_acumulado)) if lote.fator_acumulado > 1 else 0.0
                urgencia    = (dias_cliff - dias_ate + 1) / dias_cliff
                penalidade_cliff = ratio_lucro * info['delta'] * urgencia * 20.0
            break

    return custo_fiscal + penalidade_cliff

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
        score = simular_valor_final_produto(p, data_aporte, 1000.0, data_aporte + timedelta(days=365), bcb_map, produtos_rolagem=produtos)
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
            v = simular_valor_final_produto(pp, data_aporte, vv, data_aporte + timedelta(days=365), bcb_map, produtos_rolagem=produtos)
            if v <= -1e17:
                return -1e18
            total += v
        return total

    def _aloc_taxa_alta():
        candidatos_taxa = sorted(candidatos, key=lambda x: (float(score_map.get(x, 0.0) or 0.0), float(getattr(x, 'taxa_base', 1.0) or 1.0)), reverse=True)
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

    limite_prod = (max_produtos if max_produtos is not None else TOP_N_ALOCACAO)
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

            conc = (ja / max(valor, 1.0))
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

def _gerar_artefatos_diagnostico_switching(base_lotes_cenarios, contas, produtos, bcb_map, hoje,
                                           planos_pool_switch, *, gerar_diagnosticos_switching=False,
                                           gerar_comparativo_validacao=False):
    diag_datas, diag_planos = [], []
    df_comparativo_validacao = pd.DataFrame()

    precisa_base_diag = bool(gerar_diagnosticos_switching or gerar_comparativo_validacao)
    if precisa_base_diag:
        try:
            diag_datas, diag_planos, _ = gerar_diagnostico_switches_portfolio(
                base_lotes_cenarios, contas, produtos, bcb_map, hoje, janela_datas=7, top_k=5
            )
            if gerar_diagnosticos_switching and (diag_datas or diag_planos):
                print("\n>>> Diagnóstico de switches gerado (veja abas Diagnostico_*)")
                df_dd = pd.DataFrame(diag_datas)
                if not df_dd.empty:
                    top_escolha = df_dd[df_dd['Data Avaliada'] == df_dd['Data Escolhida']].copy()
                    if not top_escolha.empty:
                        top_escolha.sort_values(['Lote ID', 'Rank (Data)'], inplace=True)
                        for _, r in top_escolha.head(5).iterrows():
                            print(f"   [DIAG-DATA] {r['Lote ID']} | escolhida {r['Data Escolhida']} | rank {int(r['Rank (Data)'])} | Δ R$ {float(r['Delta vs Escolhida']):,.2f}")
        except Exception as e:
            print(f"   [WARN] Falha ao gerar diagnóstico de switches: {e}")
            diag_datas, diag_planos = [], []

    if gerar_comparativo_validacao:
        try:
            df_comparativo_validacao = _gerar_comparativo_validacao_switching(
                base_lotes_cenarios, contas, produtos, bcb_map, hoje, planos_pool_switch, diag_datas, diag_planos
            )
            if not df_comparativo_validacao.empty:
                print("\n>>> Comparativo de validação gerado (aba Comparativo_Validacao)")
                top = df_comparativo_validacao.sort_values('Riqueza Final', ascending=False).head(3)
                for _, r in top.iterrows():
                    print(f"   [VALID] {r['Cenário']}: riqueza R$ {r['Riqueza Final']:,.2f} | Δ vs atual R$ {r.get('Δ vs Plano Atual', 0.0):,.2f}")
        except Exception as e:
            print(f"   [WARN] Falha ao gerar comparativo de validação: {e}")
            df_comparativo_validacao = pd.DataFrame()

    return diag_datas, diag_planos, df_comparativo_validacao

def _ajustar_decisoes_switch_para_pooling(decisoes_sw, lotes_por_id, produtos, contas, bcb_map, hoje):
    grupos_sw = {}
    for lid, (d_sw, _p_sw, _ganho) in list(decisoes_sw.items()):
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
        for lid in sorted(ids, key=lambda x: lotes_por_id[x].saldo_bruto if x in lotes_por_id else 0.0, reverse=True):
            lobj = lotes_por_id.get(lid)
            if lobj is None:
                continue
            val = lobj.saldo_bruto
            escolha = next((k for k, (p_alvo, disp) in enumerate(bucket) if disp + 0.01 >= val and p_alvo.aceita_aporte(val)), None)
            if escolha is None:
                candidatos_ok = [b for b in bucket if b[0].aceita_aporte(val)]
                if candidatos_ok:
                    decisoes_sw[lid] = (d_sw, max(candidatos_ok, key=lambda b: float(getattr(b[0], 'taxa_base', 1.0) or 1.0))[0], decisoes_sw[lid][2])
                continue
            p_alvo, disp = bucket[escolha]
            bucket[escolha][1] = max(0.0, disp - val)
            decisoes_sw[lid] = (d_sw, p_alvo, decisoes_sw[lid][2])
    return decisoes_sw

def _alinhar_decisoes_switch_para_data_pool(decisoes_sw, analise_switch, produtos, hoje):
    validacao_pool = []
    datas_futuras = [d for (_lid, (d, _p, _g)) in decisoes_sw.items() if d != hoje]
    data_pool_ref = None
    if datas_futuras:
        cont = {}
        for d in datas_futuras:
            cont[d] = cont.get(d, 0) + 1
        data_pool_ref = max(cont, key=cont.get)

    if data_pool_ref is None:
        return decisoes_sw, validacao_pool

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
    return decisoes_sw, validacao_pool

def _calcular_metricas_switch_relatorio(lote, data_sw, produtos, bcb_map, hoje, contas, liquido_sw=None):
    horizonte_fim = hoje + timedelta(days=365)
    try:
        valor_terminal_sem_switch = float(simular_valor_final_produto(
            lote.produto, hoje, float(lote.saldo_bruto), horizonte_fim, bcb_map, produtos_rolagem=produtos
        ))
    except Exception:
        valor_terminal_sem_switch = float(lote.saldo_bruto)

    if liquido_sw is None:
        try:
            liquido_sw = float(max(0.0, estimar_liquido_lote_sem_pagamentos(lote, data_sw, bcb_map)))
        except Exception:
            liquido_sw = 0.0

    valor_terminal_com_switch = 0.0
    plano_top = None
    if liquido_sw > 0.01:
        try:
            contas_fut_sw = [c for c in contas if c[0] >= data_sw]
            planos_top = gerar_top_planos_alocacao(data_sw, liquido_sw, produtos, bcb_map, contas_fut_sw, top_k=1)
            plano_top = planos_top[0] if planos_top else None
        except Exception:
            plano_top = None

    if plano_top:
        for pp, vv in plano_top:
            try:
                valor_terminal_com_switch += float(simular_valor_final_produto(
                    pp, data_sw, float(vv), horizonte_fim, bcb_map, produtos_rolagem=produtos
                ))
            except Exception:
                valor_terminal_com_switch += float(vv)
    else:
        valor_terminal_com_switch = float(liquido_sw)

    return {
        'liquido_estimado_switch': float(liquido_sw),
        'valor_terminal_sem_switch': float(valor_terminal_sem_switch),
        'valor_terminal_com_switch': float(valor_terminal_com_switch),
        'ganho_financeiro_puro_lote': float(valor_terminal_com_switch - valor_terminal_sem_switch),
        'plano_top': plano_top,
    }
def _montar_eventos_e_plano_switching(df_switch_view, decisoes_sw, melhores_por_lote, lotes_por_id, contas, produtos, bcb_map, hoje):
    console_linhas = []
    plano_switches = []
    switches_agendados = 0
    switches_hoje_exec = 0
    lotes_novos_hoje = []

    for _, row_atual in df_switch_view.iterrows():
        lote_id = str(row_atual.get('Lote ID', '')).strip()
        if not lote_id:
            continue
        carteira_nome = str(row_atual.get('Carteira', '-') or '-')
        saldo_bruto_atual = float(row_atual.get('Saldo Bruto Atual (R$)', 0.0) or 0.0)
        saldo_liquido_atual = float(row_atual.get('Saldo Líquido Atual (R$)', 0.0) or 0.0)
        linha_base = (
            f"    - Lote {lote_id}: {carteira_nome} | "
            f"bruto atual R$ {saldo_bruto_atual:,.2f} | "
            f"líquido atual R$ {saldo_liquido_atual:,.2f} | "
        )
        ocultar_lote_nao_aportado = (
            carteira_nome.strip() == '-' and abs(saldo_bruto_atual) < 0.005 and abs(saldo_liquido_atual) < 0.005
        )
        if ocultar_lote_nao_aportado and lote_id not in decisoes_sw:
            continue
        if lote_id not in decisoes_sw:
            info = melhores_por_lote.get(lote_id)
            if info:
                delta_cart = float(info.get('Delta Riqueza Carteira', 0.0) or 0.0)
                ganho_puro = info.get('Ganho Financeiro Puro Lote')
                ganho_puro_txt = f" | ganho puro lote R$ {float(ganho_puro):,.2f}" if ganho_puro is not None else ""
                console_linhas.append(
                    linha_base
                    + f"manter. melhor candidato seria {info['Produto Candidato']} em {info['Data Switch']} "
                    + f"(Δ carteira R$ {delta_cart:,.2f}{ganho_puro_txt})"
                )
            else:
                console_linhas.append(linha_base + "manter. (sem candidato viável)")
            continue

        data_sw, prod_alvo, ganho = decisoes_sw[lote_id]
        lobj = lotes_por_id.get(lote_id)
        liq_est = saldo_liquido_atual
        ganho_puro_lote = None
        if lobj is not None:
            try:
                liq_est = float(estimar_liquido_lote_sem_pagamentos(lobj, data_sw, bcb_map))
            except Exception:
                liq_est = max(0.0, saldo_liquido_atual)
            try:
                met_sw = _calcular_metricas_switch_relatorio(lobj, data_sw, produtos, bcb_map, hoje, contas, liquido_sw=liq_est)
                ganho_puro_lote = float(met_sw.get('ganho_financeiro_puro_lote', 0.0) or 0.0)
            except Exception:
                ganho_puro_lote = None
        valor_aplicar = saldo_liquido_atual if data_sw == hoje else liq_est
        ganho_puro_txt = f" | ganho puro lote R$ {float(ganho_puro_lote):,.2f}" if ganho_puro_lote is not None else ""

        if data_sw == hoje:
            console_linhas.append(
                linha_base
                + f"SWITCH HOJE -> {prod_alvo.nome} | aplicar ~R$ {valor_aplicar:,.2f} | Δ carteira R$ {ganho:,.2f}{ganho_puro_txt}"
            )
            plano_switches.append({
                'Data': hoje,
                'Origem': lote_id,
                'Produto': prod_alvo.nome,
                'Valor': round(valor_aplicar, 2),
                'Delta_Riqueza_Carteira': round(float(ganho), 2),
                'Ganho_Financeiro_Puro_Lote': round(float(ganho_puro_lote), 2) if ganho_puro_lote is not None else None,
                'Tipo': 'Switch',
            })
            if lobj is None or not prod_alvo.ativo:
                if lobj is None:
                    console_linhas.append("      (lote não ativo no motor de switching, sem execução real)")
                elif not prod_alvo.ativo:
                    console_linhas.append("      (produto inativo, ignorado)")
                continue
            novos = lobj.switch_para(prod_alvo, hoje)
            lotes_novos_hoje.extend(novos)
            switches_hoje_exec += 1
            continue

        console_linhas.append(
            linha_base
            + f"AGENDAR {data_sw} -> {prod_alvo.nome} | aplicar ~R$ {valor_aplicar:,.2f} | Δ carteira R$ {ganho:,.2f}{ganho_puro_txt}"
        )
        plano_switches.append({
            'Data': data_sw,
            'Origem': lote_id,
            'Produto': prod_alvo.nome,
            'Valor': round(valor_aplicar, 2),
            'Ganho_Estimado': round(ganho, 2),
            'Delta_Riqueza_Carteira': round(float(ganho), 2),
            'Ganho_Financeiro_Puro_Lote': round(float(ganho_puro_lote), 2) if ganho_puro_lote is not None else None,
            'Tipo': 'Switch',
        })
        if lobj is not None:
            lobj.switch_agendado = (data_sw, prod_alvo)
            if liq_est > 0.01:
                contas_fut_sw = [c for c in contas if c[0] >= data_sw]
                planos_top = gerar_top_planos_alocacao(data_sw, liq_est, produtos, bcb_map, contas_fut_sw, top_k=1)
                lobj.switch_plano = planos_top[0] if planos_top else None
        switches_agendados += 1

    return {
        'console_linhas': console_linhas,
        'plano_switches': plano_switches,
        'switches_agendados': switches_agendados,
        'switches_hoje_exec': switches_hoje_exec,
        'lotes_novos_hoje': lotes_novos_hoje,
    }

def _montar_planos_pool_switch(lotes_passados, contas, produtos, bcb_map, hoje):
    planos_pool_switch = {}
    console_pool = []

    grupos_agendados = {}
    for lote in lotes_passados:
        if not lote.esgotado and lote.switch_agendado is not None:
            d_sw, _ = lote.switch_agendado
            grupos_agendados.setdefault(d_sw, []).append(lote)

    for d_sw, lotes_d in sorted(grupos_agendados.items(), key=lambda x: x[0]):
        if len(lotes_d) < 2:
            continue
        total_liq = sum(
            max(0.0, estimar_liquido_lote_sem_pagamentos(lx, d_sw, bcb_map))
            for lx in lotes_d
        )
        if total_liq <= 0.01:
            continue
        contas_fut_d = [c for c in contas if c[0] >= d_sw]
        aloc_pool, top_pool, _ = alocar_lote_por_otimizacao(
            hoje, d_sw, total_liq, produtos, bcb_map, contas_fut_d, foco_rendimento=True, max_produtos=3
        )
        if not aloc_pool:
            continue

        planos_pool_switch[d_sw] = (float(total_liq), list(aloc_pool))
        console_pool.append(f"\n  [POOL SWITCH {d_sw}] {len(lotes_d)} lote(s) | líquido consolidado R$ {total_liq:,.2f}")
        for i, (pp, vv) in enumerate(aloc_pool, 1):
            if isinstance(pp, ComboProduto):
                vb, vx = pp.dividir_valor(vv)
                console_pool.append(
                    f"     {i:>2}. Combo {pp.nome:<24} total R$ {vv:>10,.2f} | base R$ {vb:>9,.2f} | bônus R$ {vx:>9,.2f}"
                )
            else:
                taxa = float(getattr(pp, 'taxa_base', 1.0) or 1.0) * 100.0
                console_pool.append(
                    f"     {i:>2}. {pp.nome:<30} R$ {vv:>10,.2f} | taxa {taxa:>6.2f}% CDI"
                )
        if top_pool:
            console_pool.append(f"       TOP pool: {top_pool}")

    return planos_pool_switch, console_pool

def _consolidar_plano_switches_final(plano_switches, planos_pool_switch):
    plano_switches_final = []
    datas_pool = set(planos_pool_switch.keys())

    for item in plano_switches:
        if item.get('Data') not in datas_pool:
            plano_switches_final.append(item)

    for d_sw, pool_info in sorted(planos_pool_switch.items(), key=lambda x: x[0]):
        _total_liquido_pool, aloc = pool_info
        for prod_sw, val_sw in aloc:
            nome_sw = prod_sw.nome if hasattr(prod_sw, 'nome') else str(prod_sw)
            plano_switches_final.append({
                'Data': d_sw,
                'Origem': 'POOL',
                'Produto': nome_sw,
                'Valor': round(float(val_sw), 2),
                'Ganho_Estimado': None,
                'Tipo': 'Switch-POOL',
            })

    return plano_switches_final

def _avaliar_switching_e_diagnosticos(lotes_passados, lotes_futuros, contas, produtos, bcb_map, hoje, estado_lotes_passado_snapshot=None, log_passado=None, data_referencia_snapshot=None, *, gerar_diagnosticos_switching=False, gerar_comparativo_validacao=False, verbose_switching=True):
    print("\n>>> Avaliando switching para lotes existentes...")
    for lote in lotes_passados:
        if lote.saldo_bruto > 0.01:
            lote.esgotado = False
        if lote.produto is None:
            lote.produto = PRODUTO_PADRAO

    if estado_lotes_passado_snapshot is None or log_passado is None:
        df_situacao_atual = pd.DataFrame()
    else:
        try:
            estado_rows = estado_lotes_passado_snapshot.to_dict('records') if isinstance(estado_lotes_passado_snapshot, pd.DataFrame) else list(estado_lotes_passado_snapshot or [])
            valores_originais = {str(st.get('Lote ID', '')).strip(): float(st.get('Valor Inicial', 0.0) or 0.0) for st in estado_rows if str(st.get('Lote ID', '')).strip()}
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
        lotes_passados, contas, produtos, bcb_map, hoje, max_iter=12, min_ganho_abs=5.0, verbose=verbose_switching
    )
    print(f">>> [SWITCH-OPT] riqueza baseline R$ {riqueza_base:,.2f} -> final R$ {riqueza_final:,.2f}")

    lotes_por_id = {l.id: l for l in lotes_passados}
    decisoes_sw = _ajustar_decisoes_switch_para_pooling(decisoes_sw, lotes_por_id, produtos, contas, bcb_map, hoje)
    decisoes_sw, validacao_pool = _alinhar_decisoes_switch_para_data_pool(decisoes_sw, analise_switch, produtos, hoje)

    melhores_por_lote = {}
    for a in analise_switch:
        lid = a.get('Lote ID')
        sf = float(a.get('Score Final', 0.0) or 0.0)
        if lid not in melhores_por_lote or sf > melhores_por_lote[lid]['Score Final']:
            melhores_por_lote[lid] = {
                'Score Final': sf,
                'Produto Candidato': a.get('Produto Candidato'),
                'Data Switch': a.get('Data Switch'),
                'Delta Riqueza Carteira': a.get('Ganho Estimado', 0.0),
                'Ganho Financeiro Puro Lote': None,
            }

    for lid, info in melhores_por_lote.items():
        lobj = lotes_por_id.get(lid)
        data_sw = info.get('Data Switch')
        if lobj is None or not data_sw:
            continue
        try:
            met_sw = _calcular_metricas_switch_relatorio(lobj, data_sw, produtos, bcb_map, hoje, contas)
            info['Ganho Financeiro Puro Lote'] = float(met_sw.get('ganho_financeiro_puro_lote', 0.0) or 0.0)
        except Exception:
            info['Ganho Financeiro Puro Lote'] = None

    df_switch_view = df_situacao_atual.copy() if isinstance(df_situacao_atual, pd.DataFrame) else pd.DataFrame()
    if not df_switch_view.empty and 'Lote ID' in df_switch_view.columns:
        df_switch_view = df_switch_view[df_switch_view['Lote ID'].astype(str) != 'TOTAL'].copy()
        if 'Data Aplicação' in df_switch_view.columns:
            datas_aplic = pd.to_datetime(df_switch_view['Data Aplicação'], errors='coerce')
            df_switch_view = df_switch_view[datas_aplic.dt.date <= hoje].copy()
        cols_ord = [c for c in ['Data Aplicação', 'Lote ID'] if c in df_switch_view.columns]
        if cols_ord:
            df_switch_view = df_switch_view.sort_values(cols_ord).reset_index(drop=True)

    plano_operacional = _montar_eventos_e_plano_switching(df_switch_view, decisoes_sw, melhores_por_lote, lotes_por_id, contas, produtos, bcb_map, hoje)
    lotes_passados.extend(plano_operacional['lotes_novos_hoje'])
    planos_pool_switch, console_pool = _montar_planos_pool_switch(lotes_passados, contas, produtos, bcb_map, hoje)
    plano_switches_final = _consolidar_plano_switches_final(plano_operacional['plano_switches'], planos_pool_switch)
    for linha in plano_operacional['console_linhas']:
        print(linha)
    for linha in console_pool:
        print(linha)
    _imprimir_resumo_consolidado_switches(plano_switches_final)

    todos_lotes_pre = lotes_passados + lotes_futuros
    diag_datas, diag_planos, df_comparativo_validacao = _gerar_artefatos_diagnostico_switching(
        todos_lotes_pre,
        contas,
        produtos,
        bcb_map,
        hoje,
        planos_pool_switch,
        gerar_diagnosticos_switching=gerar_diagnosticos_switching,
        gerar_comparativo_validacao=gerar_comparativo_validacao,
    )
    return {
        'lotes_passados': lotes_passados,
        'lotes_futuros': lotes_futuros,
        'planos_pool_switch': planos_pool_switch,
        'plano_switches_final': plano_switches_final,
        'df_situacao_atual': df_situacao_atual,
        'switches_agendados': plano_operacional['switches_agendados'],
        'switches_hoje_exec': plano_operacional['switches_hoje_exec'],
        'analise_switch': analise_switch,
        'validacao_pool': validacao_pool,
        'diag_datas': diag_datas,
        'diag_planos': diag_planos,
        'df_comparativo_validacao': df_comparativo_validacao,
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
        return {'Cenário': nome, 'Riqueza Final': float(riqueza), 'Saldo Líquido Final': float(met.get('saldo_final', 0.0)), 'Imposto Pago': float(met.get('imposto_total', 0.0)), 'Total Resgatado': float(met.get('total_resgatado', 0.0)), 'Switches Executados': int(met.get('switches_exec', 0)), 'Detalhes': f"Data={det['Data']} | Pool={det['Lotes Pool']} | LiqEst={det['Liquido Pool Est.']:.2f} | MinAlvo={det['Min alvo']:.2f}"}

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
                print(f">>> [SWITCH-OPT] parada na iteração {it}: melhor Δ carteira R$ {melhor_ganho:,.2f} < limiar R$ {min_ganho_abs:,.2f}")
            break

        agenda_atual[melhor_lote_id] = melhor_acao
        riqueza_atual = melhor_riqueza
        if verbose:
            print(f">>> [SWITCH-OPT] it {it}: aplica {melhor_lote_id} -> {melhor_acao[1].nome} em {melhor_acao[0]} | Δ carteira R$ {melhor_ganho:,.2f} | riqueza R$ {riqueza_atual:,.2f}")

    riqueza_final = _simular_riqueza_carteira(lotes_base, contas, bcb_map, hoje, produtos, agenda_atual) if agenda_atual else riqueza_base
    decisoes = _decisoes_switch_marginais(lotes_base, contas, produtos, bcb_map, hoje, agenda_atual, riqueza_base, riqueza_final)

    df_a = pd.DataFrame(analise)
    if not df_a.empty:
        df_a.sort_values(['iter', 'ganho_portfolio'], ascending=[True, False], inplace=True)
        analise = df_a.to_dict('records')

    return decisoes, analise, riqueza_base, riqueza_final

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
    candidatos_locais = _listar_candidatos_parametros('melhores_parametros_5p.json')

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
        destino = Path('/content/melhores_parametros_5p_download.json') if Path('/content').exists() else Path(f'melhores_parametros_5p_download_{idx}.json')
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

def _gerar_df_consolidado(df, group_cols, value_col='Valor'):
    if df is None or df.empty:
        return pd.DataFrame()
    return (df.groupby(group_cols, as_index=False)[value_col].sum()
              .sort_values([group_cols[0], value_col], ascending=[True, False]))

def _montar_df_diagnostico_modo_execucao(stats=None):
    diag = dict(DIAGNOSTICO_MODO_EXECUCAO or {})
    modo_solicitado = diag.get('modo_solicitado') or str(EXEC_CFG.get('modo_execucao_futuro', MODO_EXECUCAO_FUTURO or ''))
    modo_efetivo = diag.get('modo_efetivo') or normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO)
    houve_rebaixamento = bool(diag.get('houve_rebaixamento')) or (modo_solicitado and modo_efetivo and normalizar_modo_execucao_futuro(modo_solicitado) != modo_efetivo)
    motivos = diag.get('motivos_rebaixamento') or []
    plano_carregado = diag.get('plano_externo_carregado')
    if plano_carregado is None:
        plano_carregado = bool(PLANO_PAGAMENTOS_EXTERNO)
    origem_plano = diag.get('origem_plano_externo') or ORIGEM_PLANO_PAGAMENTOS
    observacao = diag.get('observacao') or MODOS_EXECUCAO_FUTURO_INFO.get(modo_efetivo, '')
    modo_rigido_ativo = (modo_efetivo == 'rigido_plano_externo')
    requer_plano_externo = modo_rigido_ativo
    execucao_futura_realizada = bool(stats) and str((stats or {}).get('modo_runner', '')) != 'sem_simulacao_futura'
    if not modo_rigido_ativo:
        fallback_por_ausencia_plano = 'Não se aplica'
        leitura_status = 'Modo rígido inativo.'
    elif plano_carregado:
        fallback_por_ausencia_plano = 'Não'
        leitura_status = 'Modo rígido ativo com plano externo efetivamente carregado.'
    elif execucao_futura_realizada:
        fallback_por_ausencia_plano = 'Sim'
        leitura_status = 'Modo rígido ativo sem plano externo carregado; fallback operacional aplicado por ausência de plano.'
    else:
        fallback_por_ausencia_plano = 'Não executado'
        leitura_status = 'Modo rígido ativo sem plano externo efetivamente carregado; como não houve simulação futura, nenhum fallback foi executado.'
    return pd.DataFrame([{
        'modo_solicitado': modo_solicitado,
        'modo_efetivo': modo_efetivo,
        'modo_rigido_ativo': 'Sim' if modo_rigido_ativo else 'Não',
        'requer_plano_externo': 'Sim' if requer_plano_externo else 'Não',
        'houve_rebaixamento': 'Sim' if houve_rebaixamento else 'Não',
        'motivos_rebaixamento': '; '.join(motivos),
        'plano_externo_carregado': 'Sim' if plano_carregado else 'Não',
        'origem_plano_externo': origem_plano,
        'fallback_por_ausencia_plano': fallback_por_ausencia_plano,
        'execucao_futura_realizada': 'Sim' if execucao_futura_realizada else 'Não',
        'observacao': observacao,
        'leitura_status': leitura_status,
    }])

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

def _montar_df_switches_consolidados(plano_switches):
    if plano_switches is None or plano_switches.empty:
        return pd.DataFrame()
    cols = ['Data', 'Produto']
    df = plano_switches.copy()
    for c in ['Valor', 'Delta_Riqueza_Carteira', 'Ganho_Financeiro_Puro_Lote']:
        if c not in df.columns:
            df[c] = 0.0
    if 'Origem' not in df.columns:
        df['Origem'] = None
    out = (df.groupby(cols, as_index=False)
             .agg(
                 Valor=('Valor', 'sum'),
                 Delta_Riqueza_Carteira=('Delta_Riqueza_Carteira', 'sum'),
                 Ganho_Financeiro_Puro_Lote=('Ganho_Financeiro_Puro_Lote', 'sum'),
                 Qtd_Switches=('Origem', lambda s: int(s.notna().sum()))
             )
             .sort_values(['Data', 'Valor'], ascending=[True, False]))
    for c in ['Valor', 'Delta_Riqueza_Carteira', 'Ganho_Financeiro_Puro_Lote']:
        out[c] = out[c].astype(float).round(2)
    return out
def _montar_df_resumo_exportacao(*, stats, situacao_atual, situacao_final, plano_aportes, plano_switches, diagnostico_modo):
    atual = situacao_atual if isinstance(situacao_atual, pd.DataFrame) else pd.DataFrame(situacao_atual or [])
    final = situacao_final if isinstance(situacao_final, pd.DataFrame) else pd.DataFrame(situacao_final or [])
    aportes = plano_aportes if isinstance(plano_aportes, pd.DataFrame) else pd.DataFrame(plano_aportes or [])
    switches = plano_switches if isinstance(plano_switches, pd.DataFrame) else pd.DataFrame(plano_switches or [])
    diag_row = (diagnostico_modo.iloc[0].to_dict() if isinstance(diagnostico_modo, pd.DataFrame) and not diagnostico_modo.empty else {})

    def _col_valor(df, candidatos):
        return next((c for c in candidatos if c in df.columns), None)

    def _sum_col(df, candidatos):
        col = _col_valor(df, candidatos)
        return round(float(df[col].fillna(0).sum()), 2) if col else 0.0

    resumo = [
        {'Bloco': 'Geral', 'Indicador': 'Data de Referência', 'Valor': str(data_hoje_referencia())},
        {'Bloco': 'Geral', 'Indicador': 'Modo Solicitado', 'Valor': diag_row.get('modo_solicitado') or ''},
        {'Bloco': 'Geral', 'Indicador': 'Modo Efetivo', 'Valor': diag_row.get('modo_efetivo') or ''},
        {'Bloco': 'Geral', 'Indicador': 'Plano Externo Carregado', 'Valor': diag_row.get('plano_externo_carregado') or ''},

        {'Bloco': 'Estado Atual', 'Indicador': 'Qtd Lotes', 'Valor': int(len(atual))},
        {'Bloco': 'Estado Atual', 'Indicador': 'Saldo Bruto Total (R$)', 'Valor': _sum_col(atual, ['Saldo Bruto Atual (R$)', 'Saldo Bruto'])},
        {'Bloco': 'Estado Atual', 'Indicador': 'Saldo Líquido Total (R$)', 'Valor': _sum_col(atual, ['Saldo Líquido Atual (R$)', 'Saldo Líquido'])},

        {'Bloco': 'Estado Final/Planejado', 'Indicador': 'Qtd Lotes', 'Valor': int(len(final))},
        {'Bloco': 'Estado Final/Planejado', 'Indicador': 'Saldo Bruto Total (R$)', 'Valor': _sum_col(final, ['Saldo Bruto Atual', 'Saldo Bruto Atual (R$)', 'Saldo Bruto'])},
        {'Bloco': 'Estado Final/Planejado', 'Indicador': 'Saldo Líquido Total (R$)', 'Valor': _sum_col(final, ['Saldo Líquido Atual', 'Saldo Líquido Atual (R$)', 'Saldo Líquido'])},

        {'Bloco': 'Planejamento', 'Indicador': 'Qtd Aportes Planejados', 'Valor': int(len(aportes))},
        {'Bloco': 'Planejamento', 'Indicador': 'Valor Total Aportes Planejados (R$)', 'Valor': round(float(aportes['Valor'].fillna(0).sum()), 2) if 'Valor' in aportes.columns else 0.0},
        {'Bloco': 'Planejamento', 'Indicador': 'Qtd Switches Planejados', 'Valor': int(len(switches))},
        {'Bloco': 'Planejamento', 'Indicador': 'Valor Total Switches Planejados (R$)', 'Valor': round(float(switches['Valor'].fillna(0).sum()), 2) if 'Valor' in switches.columns else 0.0},
        {'Bloco': 'Planejamento', 'Indicador': 'Δ Carteira Total Switches (R$)', 'Valor': round(float(switches['Delta_Riqueza_Carteira'].fillna(0).sum()), 2) if 'Delta_Riqueza_Carteira' in switches.columns else 0.0},
        {'Bloco': 'Planejamento', 'Indicador': 'Ganho Puro Total Switches (R$)', 'Valor': round(float(switches['Ganho_Financeiro_Puro_Lote'].fillna(0).sum()), 2) if 'Ganho_Financeiro_Puro_Lote' in switches.columns else 0.0},
    ]
    if stats:
        for k in ['riqueza', 'total_resgatado', 'saldo_liquido']:
            if k in stats:
                resumo.append({'Bloco': 'Métricas do Runner', 'Indicador': k, 'Valor': stats.get(k)})
    return pd.DataFrame(resumo)
def _exportar_resultados_excel(arquivo_saida, *, produtos, stats, extrato_df, log_passado, df_relatorio, snapshot_lotes_atuais, artefatos_switching, df_diagnostico_modo=None):
    to_df = lambda valor: valor if isinstance(valor, pd.DataFrame) else pd.DataFrame(valor or [])
    diagnostico_modo = df_diagnostico_modo if df_diagnostico_modo is not None and not getattr(df_diagnostico_modo, 'empty', True) else _montar_df_diagnostico_modo_execucao(stats=stats)
    carteira_rows = [{
        'Nome': p.nome,
        'Tipo': 'Combo',
        'Base': p.produto_base.nome,
        'Bonus': p.produto_bonus.nome,
        'Min (R$)': p.valor_min,
        'Max (R$)': p.valor_max,
        'Ativo': 'Sim' if p.ativo else 'Não'
    } if isinstance(p, ComboProduto) else {
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
    } for p in produtos]
    plano_aportes = to_df(artefatos_switching.get('plano_aportes'))
    plano_switches = to_df(artefatos_switching.get('plano_switches_final'))
    situacao_atual = to_df(artefatos_switching.get('df_situacao_atual'))
    resumo_df = _montar_df_resumo_exportacao(
        stats=stats,
        situacao_atual=situacao_atual,
        situacao_final=to_df(df_relatorio),
        plano_aportes=plano_aportes,
        plano_switches=plano_switches,
        diagnostico_modo=diagnostico_modo,
    )
    abas = [
        ('Extrato Futuro', to_df(extrato_df), 0),
        ('Extrato Passado', pd.DataFrame(log_passado or []), 0),
        ('Situação Atual', situacao_atual, 0),
        ('Situação Final', to_df(df_relatorio), 0),
        ('Analise_Switch', to_df(artefatos_switching.get('analise_switch')), 0),
        ('Validacao_Pooling', to_df(artefatos_switching.get('validacao_pool')), 0),
        ('Plano_Aportes', plano_aportes, 0),
        ('Aportes_Consolidados', _gerar_df_consolidado(plano_aportes, ['Data', 'Produto']), 0),
        ('Plano_Switches', plano_switches, 0),
        ('Switches_Consolidados', _montar_df_switches_consolidados(plano_switches), 0),
        ('Switches_Detalhados', to_df((stats or {}).get('switches_detalhados', [])), 0),
        ('Execucao_Plano_Externo', to_df((stats or {}).get('execucao_plano_externo', [])), 0),
        ('Desvios_Plano_Externo', to_df((stats or {}).get('desvios_plano_externo', [])), 0),
        ('Fallbacks_Plano_Externo', to_df((stats or {}).get('fallbacks_plano_externo', [])), 0),
        ('Diagnostico_Datas', to_df(artefatos_switching.get('diag_datas')), 0),
        ('Diagnostico_Planos', to_df(artefatos_switching.get('diag_planos')), 0),
        ('Comparativo_Validacao', to_df(artefatos_switching.get('df_comparativo_validacao', pd.DataFrame())), 0),
        ('Diagnostico_Modo', diagnostico_modo, 0),
        ('Resumo', resumo_df, 0),
        ('Carteira', pd.DataFrame(carteira_rows), 0),
    ]
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        for nome_aba, df, startrow in abas:
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=nome_aba, index=False, startrow=startrow)

def _imprimir_resumo_consolidado_switches(plano_switches_final):
    if not plano_switches_final:
        return
    print("\n    Resumo consolidado de switches planejados (um por lote; valores líquidos estimados):")
    df_sw_console = pd.DataFrame(plano_switches_final)
    if df_sw_console.empty:
        return
    for col in ['Valor', 'Delta_Riqueza_Carteira', 'Ganho_Financeiro_Puro_Lote']:
        if col not in df_sw_console.columns:
            df_sw_console[col] = 0.0
    df_cons = (df_sw_console.groupby(['Data', 'Produto'], as_index=False)
               [['Valor', 'Delta_Riqueza_Carteira', 'Ganho_Financeiro_Puro_Lote']].sum()
               .sort_values(['Data', 'Valor'], ascending=[True, False]))
    for _, rr in df_cons.iterrows():
        print(
            f"      - {rr['Data']} | {rr['Produto']:<24} | aplicar R$ {float(rr['Valor']):>10,.2f}"
            f" | Δ carteira R$ {float(rr['Delta_Riqueza_Carteira']):>9,.2f}"
            f" | ganho puro lote R$ {float(rr['Ganho_Financeiro_Puro_Lote']):>9,.2f}"
        )

def _switch_detalhe_dict(data_cur, lote_origem, produto_origem, taxa_origem, taxa_destino,
                         bruto_resgatado, liquido_resgatado, imposto_resgate, parte,
                         produto_destino, valor_parte, soma_partes, diff_total,
                         combo_total=None, combo_razao=None, combo_produto_base=None,
                         combo_produto_bonus=None, combo_base=None, combo_bonus=None,
                         valor_planejado_total=None, valor_executado_total=None,
                         status_execucao=None, motivo_desvio=None):
    return {
        "Data": data_cur,
        "Lote_Origem": lote_origem,
        "Produto_Origem": produto_origem,
        "Taxa_Origem": round(float(taxa_origem), 6) if taxa_origem is not None else None,
        "Taxa_Destino": round(float(taxa_destino), 6) if taxa_destino is not None else None,
        "Bruto_Resgatado": round(float(bruto_resgatado), 2) if bruto_resgatado is not None else None,
        "Liquido_Resgatado": round(float(liquido_resgatado), 2) if liquido_resgatado is not None else None,
        "Imposto_Resgate": round(float(imposto_resgate), 2) if imposto_resgate is not None else None,
        "Parte": parte,
        "Produto_Destino": produto_destino,
        "Valor_Parte": round(float(valor_parte), 2),
        "Combo_Total": round(float(combo_total), 2) if combo_total is not None else None,
        "Combo_Razao": combo_razao,
        "Combo_Produto_Base": combo_produto_base,
        "Combo_Produto_Bonus": combo_produto_bonus,
        "Combo_Base": round(float(combo_base), 2) if combo_base is not None else None,
        "Combo_Bonus": round(float(combo_bonus), 2) if combo_bonus is not None else None,
        "Soma_Partes": round(float(soma_partes), 2),
        "Diff_Total": round(float(diff_total), 2),
        "Valor_Planejado_Total": round(float(valor_planejado_total), 2) if valor_planejado_total is not None else None,
        "Valor_Executado_Total": round(float(valor_executado_total), 2) if valor_executado_total is not None else None,
        "Status_Execucao": status_execucao,
        "Motivo_Desvio": motivo_desvio,
    }

# =========================================================
# 09. EXECUÇÃO PRINCIPAL
# =========================================================

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
            produto_ref, data_cur, valor_base, data_fim, bcb_map_global if 'bcb_map_global' in globals() else {},
            produtos_rolagem=(PRODUTOS_GLOBAIS_SIMULACAO or [])
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

def _ordenar_lotes_para_pagamento(lotes_disponiveis, data_cur: date, data_fim: date, ids_preferidos=None):
    ids_preferidos = set(str(x).strip() for x in (ids_preferidos or []) if str(x).strip())
    ranqueados = []
    for l in lotes_disponiveis:
        custo = _fator_oportunidade_lote(l, data_cur, data_fim)
        bonus_pref = -1e-9 if str(l.id).strip() in ids_preferidos else 0.0
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
        ordenados = _ordenar_lotes_para_pagamento(disponiveis, data_ref, data_fim, ids_preferidos=ids_preferidos)

        for l in ordenados:
            if falta <= 0.001:
                break
            falta = _sacar_do_lote(l, falta)

        if falta > 0.01 and EXIBIR_ALERTAS_FALTA_CAIXA:
            print(f"  ⚠  Falta R$ {falta:.2f} para pagar conta {desc} em {data_ref} (pré-switch)")

def _modo_execucao_futuro_requer_diag_datas():
    return normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO) == 'rigido_melhor_data'

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

def _imprimir_metricas_simulacao_futura(stats):
    print(f"\n    Riqueza final:        R$ {stats['riqueza']:>15,.2f}")
    print(f"    Saldo líquido final:  R$ {stats['saldo_liquido']:>15,.2f}")
    print(f"    Total resgatado:      R$ {stats['total_resgatado']:>15,.2f}")
    print(f"    Imposto pago:         R$ {stats['total_imposto']:>15,.2f}")
    print(f"    Switches executados:  {stats['switches_exec']}")
    print(f"    Partes/lotes criados por switch: {stats.get('switches_partes_criadas', 0)}")

def _montar_relatorio_final_lotes(todos_lotes, data_ref_relatorio):
    relatorio = []
    for l in todos_lotes:
        if l.saldo_bruto > 0 or l.vezes_usado > 0:
            fl = l.get_fator_liquido(data_ref_relatorio) if l.saldo_bruto > 0 else 0.0
            liq_hoje = round(l.saldo_bruto * fl, 2)
            bruto_total = l.saldo_bruto + l.total_bruto_sacado
            rent_b = (bruto_total / l.valor_inicial - 1) * 100 if l.valor_inicial > 0 else 0
            rent_l = ((liq_hoje + l.total_liquido_sacado) / l.valor_inicial - 1) * 100 if l.valor_inicial > 0 else 0
            sw_info = '; '.join(f"{d} → {n} (R${v:,.2f})" for d, n, v in l.historico_switches) if l.historico_switches else '—'
            relatorio.append({
                'Lote ID': l.id,
                'Produto': l.produto.nome if l.produto else 'Padrão',
                'Data Aplicação': l.data_aplicacao,
                'Valor Inicial': round(l.valor_inicial, 2),
                'Saldo Bruto Atual': round(l.saldo_bruto, 2),
                'Saldo Líquido Atual': liq_hoje,
                'Total Bruto Sacado': round(l.total_bruto_sacado, 2),
                'Total Líquido Sacado': round(l.total_liquido_sacado, 2),
                'Rentabilidade Bruta %': round(rent_b, 4),
                'Rentabilidade Líquida %': round(rent_l, 4),
                'Vezes Usado': l.vezes_usado,
                'Switches': sw_info,
            })
    return pd.DataFrame(relatorio)

def _taxa_efetiva_produto_simulacao(prod) -> float:
    if prod is None:
        return 1.0
    if isinstance(prod, ComboProduto):
        rb = float(getattr(prod, 'razao_base', 2.0) or 2.0)
        rx = float(getattr(prod, 'razao_bonus', 1.0) or 1.0)
        tb = float(getattr(getattr(prod, 'produto_base', None), 'taxa_base', 1.0) or 1.0)
        tx = float(getattr(getattr(prod, 'produto_bonus', None), 'taxa_base', 1.0) or 1.0)
        den = (rb + rx) if (rb + rx) > 0 else 1.0
        return (rb * tb + rx * tx) / den
    return float(getattr(prod, 'taxa_base', 1.0) or 1.0)

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
    if normalizar_modo_execucao_futuro(MODO_EXECUCAO_FUTURO) != 'rigido_plano_externo':
        return falta, False
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

def _executar_fallback_hibrido_conta(data_cur, desc, falta, disponiveis, data_fim, bcb_map, log, fallbacks_plano_externo):
    if not (falta > 0.001 and disponiveis and PARAMS_HIBRIDO is not None):
        return falta, False
    disponiveis_rest = [l for l in disponiveis if not l.esgotado and l.saldo_bruto > 0.01]
    if not disponiveis_rest:
        return falta, False
    valores_otimos = resolver_hibrido_5p(disponiveis_rest, float(falta), data_cur, PARAMS_HIBRIDO, data_fim, bcb_map, TAXA_DIA_BASE)
    if not any(v and v > 0.01 for v in valores_otimos):
        return falta, False
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

def _executar_fallback_heuristico_conta(data_cur, desc, falta, disponiveis, log, fallbacks_plano_externo):
    if not (falta > 0.001 and disponiveis):
        return falta, False
    disponiveis.sort(key=lambda l: get_score_economico(l, data_cur))
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
    usou_otimizacao = usou_plano_rigido
    usou_plano_externo = usou_plano_rigido

    if not plano_rigido_encontrado:
        falta, usou_baseline = _executar_plano_externo_baseline_conta(data_cur, desc, falta, disponiveis, log)
        usou_plano_externo = usou_plano_externo or usou_baseline
        usou_otimizacao = usou_otimizacao or usou_baseline

    falta, usou_hibrido = _executar_fallback_hibrido_conta(
        data_cur, desc, falta, disponiveis, data_fim, bcb_map, log, fallbacks_plano_externo
    )
    usou_otimizacao = usou_otimizacao or usou_hibrido

    falta, usou_heuristica = _executar_fallback_heuristico_conta(
        data_cur, desc, falta, disponiveis, log, fallbacks_plano_externo
    )

    if falta > 0.01 and EXIBIR_ALERTAS_FALTA_CAIXA:
        print(f"  ⚠  Falta R$ {falta:.2f} para pagar conta {desc} em {data_cur}")

    return {
        'falta': falta,
        'usou_otimizacao': usou_otimizacao,
        'usou_plano_externo': usou_plano_externo,
        'usou_heuristica': usou_heuristica,
    }

def _processar_juros_do_dia(data_cur, lotes_ativos, bcb_map):
    atualizar_saldo_lotes_no_dia(lotes_ativos, data_cur, bcb_map, TAXA_DIA_BASE)

def _calcular_metricas_futuro(lotes_ativos, novos_lotes, switches_detalhados, data_inicio, data_fim):
    saldo_bruto = sum(l.saldo_bruto for l in lotes_ativos)
    saldo_liquido = sum(l.saldo_bruto * l.get_fator_liquido(data_fim) for l in lotes_ativos if not l.esgotado)
    total_resgatado = sum(l.total_liquido_sacado for l in lotes_ativos)
    total_imposto = sum(l.total_imposto_pago for l in lotes_ativos)
    riqueza = total_resgatado + saldo_liquido
    num_lotes_ativos_final = sum(1 for l in lotes_ativos if l.saldo_bruto > 0.01 and not l.esgotado)
    num_lotes_relatorio = sum(1 for l in lotes_ativos if (l.saldo_bruto > 0.01 or l.total_bruto_sacado > 0.01 or l.valor_inicial > 0.01))
    switches_exec_reais = len({
        str(r.get('Lote_Origem')) for r in switches_detalhados
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
    novos_lotes = []
    log = []
    switches_detalhados = []
    execucao_plano_externo = []
    desvios_plano_externo = []
    fallbacks_plano_externo = []
    data_cur = data_inicio

    while data_cur <= data_fim:
        _processar_juros_do_dia(data_cur, lotes_ativos, bcb_map)

        for conta in contas_por_data.get(data_cur, []):
            _data_c, valor_conta, desc = conta[:3]
            _processar_conta_futura(
                data_cur, valor_conta, desc, lotes_ativos, data_fim, bcb_map, log,
                execucao_plano_externo, desvios_plano_externo, fallbacks_plano_externo
            )

        if planos_pool_switch and data_cur in planos_pool_switch:
            lotes_switch_dia = [l for l in lotes_ativos if (not l.esgotado and l.switch_agendado and l.switch_agendado[0] == data_cur)]
            for l in lotes_switch_dia:
                try:
                    fl_est = l.get_fator_liquido(data_cur)
                    liq_est = max(0.0, l.saldo_bruto * fl_est)
                except Exception:
                    liq_est = max(0.0, l.saldo_bruto)
                if liq_est <= 0.01:
                    continue
            total_liquido_pool, aloc_pool = planos_pool_switch[data_cur]
            lotes_switch_dia = [l for l in lotes_ativos if (not l.esgotado and l.switch_agendado and l.switch_agendado[0] == data_cur)]
            if lotes_switch_dia and total_liquido_pool > 0.01:
                origem_ids = ", ".join(l.id for l in lotes_switch_dia)
                taxa_origem_pool = 0.0
                pesos = []
                for l in lotes_switch_dia:
                    try:
                        liq_est = max(0.0, l.saldo_bruto * l.get_fator_liquido(data_cur))
                    except Exception:
                        liq_est = max(0.0, l.saldo_bruto)
                    pesos.append((l, liq_est))
                den = sum(v for _, v in pesos) or 1.0
                taxa_origem_pool = sum((_taxa_efetiva_produto_simulacao(l.produto) * v) for l, v in pesos) / den
                total_plano_pool = sum(float(v) for _, v in aloc_pool)
                for j, (pp, vv) in enumerate(aloc_pool, 1):
                    vv = round(float(vv), 2)
                    if vv <= 0.00:
                        continue
                    if isinstance(pp, ComboProduto):
                        vb, vx = pp.dividir_valor(vv)
                        vb = round(float(vb), 2); vx = round(float(vx), 2)
                        switches_detalhados.append({'Data': data_cur,'Lote_Origem': f'POOL[{origem_ids}]','Produto_Origem': 'POOL','Taxa_Origem': round(float(taxa_origem_pool), 6),'Taxa_Destino': round(float(_taxa_efetiva_produto_simulacao(pp)), 6),'Bruto_Resgatado': None,'Liquido_Resgatado': round(float(total_liquido_pool), 2),'Imposto_Resgate': None,'Parte': j,'Produto_Destino': pp.nome,'Valor_Parte': vv,'Combo_Total': vv,'Combo_Razao': f'{pp.razao_base:.0f}:{pp.razao_bonus:.0f}','Combo_Produto_Base': pp.produto_base.nome,'Combo_Produto_Bonus': pp.produto_bonus.nome,'Combo_Base': vb,'Combo_Bonus': vx,'Soma_Partes': round(float(total_plano_pool), 2),'Diff_Total': round(float(total_liquido_pool) - float(total_plano_pool), 2)})
                    else:
                        switches_detalhados.append({'Data': data_cur,'Lote_Origem': f'POOL[{origem_ids}]','Produto_Origem': 'POOL','Taxa_Origem': round(float(taxa_origem_pool), 6),'Taxa_Destino': round(float(_taxa_efetiva_produto_simulacao(pp)), 6),'Bruto_Resgatado': None,'Liquido_Resgatado': round(float(total_liquido_pool), 2),'Imposto_Resgate': None,'Parte': j,'Produto_Destino': pp.nome,'Valor_Parte': vv,'Combo_Total': None,'Combo_Razao': None,'Combo_Produto_Base': None,'Combo_Produto_Bonus': None,'Combo_Base': None,'Combo_Bonus': None,'Soma_Partes': round(float(total_plano_pool), 2),'Diff_Total': round(float(total_liquido_pool) - float(total_plano_pool), 2)})
                for l in lotes_switch_dia:
                    l.esgotado = True
                    l.saldo_bruto = 0.0
                    l.switch_agendado = None
                for i, (prod, val) in enumerate(aloc_pool):
                    if isinstance(prod, ComboProduto):
                        vb, vx = prod.dividir_valor(val)
                        if vb > 0:
                            nb = Lote(f"POOLSW_{data_cur.strftime('%Y%m%d')}_{i}_B", data_cur, vb, produto=prod.produto_base, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.produto_base.carencia_dias)) if prod.produto_base.carencia_dias > 0 else None)
                            novos_lotes.append(nb); lotes_ativos.append(nb)
                        if vx > 0:
                            nx = Lote(f"POOLSW_{data_cur.strftime('%Y%m%d')}_{i}_X", data_cur, vx, produto=prod.produto_bonus, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.produto_bonus.carencia_dias)) if prod.produto_bonus.carencia_dias > 0 else None)
                            novos_lotes.append(nx); lotes_ativos.append(nx)
                    else:
                        nn = Lote(f"POOLSW_{data_cur.strftime('%Y%m%d')}_{i}", data_cur, val, produto=prod, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.carencia_dias)) if prod.carencia_dias > 0 else None)
                        novos_lotes.append(nn); lotes_ativos.append(nn)

        for l in lotes_ativos:
            if l.esgotado or l.switch_agendado is None:
                continue
            data_sw, prod_alvo = l.switch_agendado
            if data_sw == data_cur:
                try:
                    fl_est = l.get_fator_liquido(data_cur)
                    liq_est = max(0.0, l.saldo_bruto * fl_est)
                except Exception:
                    fl_est = 1.0
                    liq_est = max(0.0, l.saldo_bruto)
                bruto_pre = float(l.saldo_bruto)
                if verbose:
                    print(f"   [SWITCH] {data_cur} | Lote {l.id} | bruto R$ {l.saldo_bruto:,.2f} | liq_est R$ {liq_est:,.2f} | {l.produto.nome if l.produto else 'Padrão'} → {prod_alvo.nome}")
                if not prod_alvo.ativo:
                    print(f"      Aviso: Produto alvo inativo. Ignorado.")
                    l.switch_agendado = None
                    continue
                liquido_sw, imposto_sw = l.resgatar_total(data_cur)
                if liquido_sw <= 0.01:
                    l.switch_agendado = None
                    continue
                contas_fut = [c for c in contas_ord if c[0] >= data_cur]
                def _scale_plano(plano_ref, total_liq):
                    if not plano_ref:
                        return []
                    soma = sum(float(v) for _, v in plano_ref if float(v) > 0.0)
                    if soma <= 0.01:
                        return []
                    fator = float(total_liq) / soma
                    return [(pp, float(v) * fator) for pp, v in plano_ref]
                aloc_sw = []
                if getattr(l, 'switch_plano', None):
                    aloc_sw = _scale_plano(l.switch_plano, liquido_sw)
                    ok = True
                    for pp, vv in aloc_sw:
                        vv = float(vv)
                        if vv <= 0.01:
                            continue
                        if not getattr(pp, 'ativo', True) or not pp.aceita_aporte(vv):
                            ok = False; break
                    if not ok:
                        aloc_sw = []
                if not aloc_sw:
                    aloc_sw, _, _ = alocar_lote_por_otimizacao(data_cur, data_cur, liquido_sw, produtos, bcb_map, contas_fut, foco_rendimento=True, max_produtos=3)
                if not aloc_sw:
                    aloc_sw = [(prod_alvo, liquido_sw)]
                if aloc_sw:
                    total_plano = sum(float(v) for _, v in aloc_sw)
                    diff_plano = float(liquido_sw) - float(total_plano)
                    origem_nome = l.produto.nome if l.produto else 'Padrão'
                    if verbose:
                        print(f"      [SPLIT] total_liq R$ {liquido_sw:,.2f} | partes {len(aloc_sw)} | soma_partes R$ {total_plano:,.2f} | diff R$ {diff_plano:,.2f}")
                    acumulado = 0.0
                    for j, (pp, vv) in enumerate(aloc_sw, 1):
                        vv = round(float(vv), 2)
                        if vv <= 0.00:
                            continue
                        acumulado = round(acumulado + vv, 2)
                        restante = round(float(liquido_sw) - acumulado, 2)
                        if abs(restante) < 0.005:
                            restante = 0.0
                        if isinstance(pp, ComboProduto):
                            vb, vx = pp.dividir_valor(vv)
                            vb = round(float(vb), 2); vx = round(float(vx), 2)
                            if verbose:
                                print(f"         - Parte {j}: Combo {pp.nome} total R$ {vv:,.2f} (2:1) => base R$ {vb:,.2f} | bônus R$ {vx:,.2f} | restante R$ {restante:,.2f}")
                            switches_detalhados.append({'Data': data_cur,'Lote_Origem': l.id,'Produto_Origem': origem_nome,'Taxa_Origem': round(float(_taxa_efetiva_produto_simulacao(l.produto)), 6),'Taxa_Destino': round(float(_taxa_efetiva_produto_simulacao(pp)), 6),'Bruto_Resgatado': round(float(bruto_pre), 2),'Liquido_Resgatado': round(float(liquido_sw), 2),'Imposto_Resgate': round(float(imposto_sw), 2),'Parte': j,'Produto_Destino': pp.nome,'Valor_Parte': vv,'Combo_Total': vv,'Combo_Razao': f'{pp.razao_base:.0f}:{pp.razao_bonus:.0f}','Combo_Produto_Base': pp.produto_base.nome,'Combo_Produto_Bonus': pp.produto_bonus.nome,'Combo_Base': vb,'Combo_Bonus': vx,'Soma_Partes': round(float(total_plano), 2),'Diff_Total': round(float(liquido_sw) - float(total_plano), 2)})
                        else:
                            vmax_pp = float(getattr(pp, 'valor_max', 1e18) or 1e18)
                            vmin_pp = float(getattr(pp, 'valor_min', 0.0) or 0.0)
                            lim_txt = f" (min {vmin_pp:,.0f} / max {vmax_pp:,.0f})" if (vmax_pp < 1e17 or vmin_pp > 0) else ""
                            if verbose:
                                print(f"         - Parte {j}: {pp.nome} R$ {vv:,.2f}{lim_txt} | restante R$ {restante:,.2f}")
                            switches_detalhados.append({'Data': data_cur,'Lote_Origem': l.id,'Produto_Origem': origem_nome,'Taxa_Origem': round(float(_taxa_efetiva_produto_simulacao(l.produto)), 6),'Taxa_Destino': round(float(_taxa_efetiva_produto_simulacao(pp)), 6),'Bruto_Resgatado': round(float(bruto_pre), 2),'Liquido_Resgatado': round(float(liquido_sw), 2),'Imposto_Resgate': round(float(imposto_sw), 2),'Parte': j,'Produto_Destino': pp.nome,'Valor_Parte': vv,'Combo_Total': None,'Combo_Razao': None,'Combo_Produto_Base': None,'Combo_Produto_Bonus': None,'Combo_Base': None,'Combo_Bonus': None,'Soma_Partes': round(float(total_plano), 2),'Diff_Total': round(float(liquido_sw) - float(total_plano), 2)})
                for i_al, (prod, val) in enumerate(aloc_sw):
                    if val <= 0.01:
                        continue
                    if isinstance(prod, ComboProduto):
                        vb, vx = prod.dividir_valor(val)
                        if vb > 0:
                            nb = Lote(f"{l.id}_sw_{data_cur.strftime('%Y%m%d')}_{i_al}_B", data_cur, vb, produto=prod.produto_base, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.produto_base.carencia_dias)) if prod.produto_base.carencia_dias > 0 else None)
                            novos_lotes.append(nb); lotes_ativos.append(nb)
                        if vx > 0:
                            nx = Lote(f"{l.id}_sw_{data_cur.strftime('%Y%m%d')}_{i_al}_X", data_cur, vx, produto=prod.produto_bonus, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.produto_bonus.carencia_dias)) if prod.produto_bonus.carencia_dias > 0 else None)
                            novos_lotes.append(nx); lotes_ativos.append(nx)
                    else:
                        nn = Lote(f"{l.id}_sw_{data_cur.strftime('%Y%m%d')}_{i_al}", data_cur, val, produto=prod, data_base_fiscal=data_cur, carencia_ate=(data_cur + timedelta(days=prod.carencia_dias)) if prod.carencia_dias > 0 else None)
                        novos_lotes.append(nn); lotes_ativos.append(nn)
                l.switch_agendado = None
        data_cur += timedelta(days=1)

    return pd.DataFrame(log), _calcular_metricas_futuro(lotes_ativos, novos_lotes, switches_detalhados, data_inicio, data_fim)

def _carregar_snapshot_inicial(produtos, bcb_map):
    print("\n>>> Carregando inventário e simulando passado...")
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

def _alocar_aportes_iniciais(lotes_passados, lotes_futuros, produtos, bcb_map, contas, hoje):
    if contas:
        processar_contas_do_dia(lotes_passados, contas, hoje)
    lotes_passados = [l for l in lotes_passados if getattr(l, 'saldo_bruto', 0.0) > 0.01 and not getattr(l, 'esgotado', False)]
    contas_apos_data_referencia = [c for c in contas if c[0] != hoje]

    def _exibir_data_aporte(data_apl):
        if data_apl <= hoje:
            return True
        prox_ano = hoje.year + (1 if hoje.month == 12 else 0)
        prox_mes = 1 if hoje.month == 12 else hoje.month + 1
        return (data_apl.year, data_apl.month) in {(hoje.year, hoje.month), (prox_ano, prox_mes)}

    print("\n>>> ALOCANDO LOTES (futuros e passados sem produto)...")
    print("    (Consolidado por data com foco em maior rendimento dentro das regras de mínimo/máximo)")

    candidatos = []
    for l in lotes_passados:
        if getattr(l, 'saldo_bruto', 0.0) > 0.01 and getattr(l, 'produto', None) is None and not getattr(l, 'nao_disponivel_para_aporte', False):
            candidatos.append(l)
    for l in lotes_futuros:
        if getattr(l, 'saldo_bruto', 0.0) > 0.01 and getattr(l, 'produto', None) is None and not getattr(l, 'nao_disponivel_para_aporte', False):
            candidatos.append(l)

    por_data = {}
    for l in candidatos:
        por_data.setdefault(l.data_aplicacao, []).append(l)

    plano_aportes = []
    lotes_futuros_out = [l for l in lotes_futuros if getattr(l, 'produto', None) is not None]
    lotes_passados_out = [l for l in lotes_passados if getattr(l, 'produto', None) is not None]
    datas_ocultas = 0

    for data_apl in sorted(por_data):
        grupo = [l for l in por_data[data_apl] if getattr(l, 'saldo_bruto', 0.0) > 0.01 and not getattr(l, 'esgotado', False)]
        if not grupo:
            continue
        valor_total = round(sum(float(l.saldo_bruto) for l in grupo), 2)
        if valor_total <= 0.01:
            continue

        aloc, top_mercado, _ = alocar_lote_por_otimizacao(hoje, data_apl, valor_total, produtos, bcb_map, contas_apos_data_referencia, foco_rendimento=True, max_produtos=2)
        exibir_console = _exibir_data_aporte(data_apl)
        if not exibir_console and data_apl > hoje:
            datas_ocultas += 1

        if exibir_console:
            print(f"\n  [DATA {data_apl}] {len(grupo)} lote(s) | consolidado R$ {valor_total:,.2f}")
        if aloc:
            for i, (prod, valor) in enumerate(aloc, start=1):
                if exibir_console:
                    print(f"      {i}. {prod.nome:<30} R$ {valor:>10,.2f} | taxa {float(getattr(prod, 'taxa_base', 0.0) or 0.0):.2f}% CDI")
                plano_aportes.append({'Data': data_apl, 'Produto': prod.nome, 'Valor': round(float(valor), 2)})
            if exibir_console and top_mercado:
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
        elif exibir_console:
            print("      ⚠ Nenhum plano viável encontrado.")

        if aloc:
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

    if datas_ocultas:
        print(f"\n    ... {datas_ocultas} data(s) futura(s) de aporte além do próximo mês foram ocultadas na exibição.")

    lotes_passados = [l for l in lotes_passados_out if getattr(l, 'saldo_bruto', 0.0) > 0.01 and l.data_aplicacao <= hoje]
    lotes_futuros = [l for l in lotes_futuros_out if getattr(l, 'saldo_bruto', 0.0) > 0.01 and l.data_aplicacao > hoje]
    return lotes_passados, lotes_futuros, pd.DataFrame(plano_aportes), contas_apos_data_referencia

def executar_runner_principal(*, executar_futuro=False, exportar_excel=True,
                              arquivo_saida='simulacao_switching_completo_resultado.xlsx',
                              gerar_diagnosticos_switching=False,
                              gerar_comparativo_validacao=False, verbose_switching=True):
    print("=" * 74)
    print("SIMULADOR FINANCEIRO V29 - INICIALIZAÇÃO")
    print("=" * 74)
    hoje = data_hoje_referencia()
    print(f"Config carregada: {'SIM' if CONFIG_LINKS else 'NÃO'}")
    if CONFIG_LINKS_PATH is not None:
        print(f"Arquivo config: {CONFIG_LINKS_PATH}")
    print(f"Arquivo Excel padrão: {NOME_ARQUIVO_LOCAL}")
    print(f"Cache BCB: {CACHE_BCB_FILE}")
    print(f"Modo de execução: {MODO_EXECUCAO_FUTURO}")
    print(f"Data de referência: {hoje}")
    print("\n>>> [SETUP] Verificando arquivo Excel...")
    print(f" -> Planilha em uso: {_resolver_arquivo_excel_local()}")
    print("\n>>> [BCB] Carregando histórico CDI diário...")
    bcb_map, ultima_taxa = obter_historico_bcb()
    print(f" -> Dias CDI carregados: {len(bcb_map)} | última taxa base: {float(ultima_taxa):.8f}")
    print("\n>>> [CARTEIRA] Carregando produtos...")
    produtos = carregar_carteira()
    if not produtos:
        raise RuntimeError("Nenhum produto encontrado na aba Carteira.")
    print(f" -> {len(produtos)} produto(s) carregado(s).")
    global PRODUTO_PADRAO, PRODUTOS_GLOBAIS_SIMULACAO
    PRODUTOS_GLOBAIS_SIMULACAO = list(produtos)
    ativos = [p for p in produtos if getattr(p, 'ativo', True)]
    PRODUTO_PADRAO = max(ativos, key=lambda p: float(getattr(p, 'taxa_base', 0.0) or 0.0)) if ativos else produtos[0]
    print(f" -> Produto padrão definido: {getattr(PRODUTO_PADRAO, 'nome', 'N/D') if PRODUTO_PADRAO is not None else 'N/D'}")

    executar_futuro = bool(executar_futuro)
    gerar_diagnosticos_switching = bool(gerar_diagnosticos_switching or (executar_futuro and _modo_execucao_futuro_requer_diag_datas()))
    gerar_comparativo_validacao = bool(gerar_comparativo_validacao)

    snapshot = _carregar_snapshot_inicial(produtos, bcb_map)
    lotes_passados, lotes_futuros, plano_aportes, contas_apos_data_referencia = _alocar_aportes_iniciais(
        snapshot['lotes_passados'], snapshot['lotes_futuros'], produtos, bcb_map, snapshot['contas'], hoje,
    )
    artefatos_switching = _avaliar_switching_e_diagnosticos(
        lotes_passados, lotes_futuros, contas_apos_data_referencia, produtos, bcb_map, hoje,
        snapshot.get('estado_lotes_passado_snapshot'), snapshot.get('log_passado'), snapshot.get('data_referencia_snapshot'),
        gerar_diagnosticos_switching=gerar_diagnosticos_switching,
        gerar_comparativo_validacao=gerar_comparativo_validacao,
        verbose_switching=verbose_switching,
    )
    artefatos_switching['plano_aportes'] = plano_aportes
    resultado = {'status': 'runner_switching_concluido', 'artefatos_switching': artefatos_switching, 'snapshot': snapshot, 'hoje': hoje}
    if not executar_futuro:
        if exportar_excel:
            stats_sem_futuro = {
                'modo_runner': 'sem_simulacao_futura',
                'data_referencia': str(hoje),
                'switches_agendados': artefatos_switching.get('switches_agendados', 0),
                'switches_hoje_exec': artefatos_switching.get('switches_hoje_exec', 0),
            }
            _exportar_resultados_excel(
                arquivo_saida, produtos=produtos, stats=stats_sem_futuro, extrato_df=pd.DataFrame(),
                log_passado=snapshot.get('log_passado'), df_relatorio=snapshot.get('snapshot_lotes_atuais'),
                snapshot_lotes_atuais=snapshot.get('snapshot_lotes_atuais'), artefatos_switching=artefatos_switching,
                df_diagnostico_modo=_montar_df_diagnostico_modo_execucao(stats=stats_sem_futuro),
            )
            resultado['arquivo_saida'] = arquivo_saida
        print("\n>>> Runner principal concluído sem simulação futura.")
        print("    - Snapshot e switching processados.")
        if exportar_excel:
            print(f"    - Resultados exportados em: {arquivo_saida}")
        if gerar_diagnosticos_switching or gerar_comparativo_validacao:
            print("    - Diagnósticos/validações opcionais executados conforme configuração do runner.")
        return resultado

    print("\n>>> Iniciando simulação futura (dia a dia)...")
    todos_lotes = _aplicar_modo_execucao_futuro_final(copy.deepcopy(artefatos_switching['lotes_passados'] + artefatos_switching['lotes_futuros']), artefatos_switching, contas_apos_data_referencia, produtos, bcb_map)
    extrato_df, stats = simular_futuro(
        todos_lotes, contas_apos_data_referencia, bcb_map, data_inicio=hoje, produtos=produtos,
        planos_pool_switch=artefatos_switching.get('planos_pool_switch', {}),
    )
    _imprimir_metricas_simulacao_futura(stats)
    data_ref_relatorio = stats.get('data_referencia_relatorio', stats.get('data_fim', hoje))
    resultado_futuro = {
        'todos_lotes': todos_lotes,
        'extrato_df': extrato_df,
        'stats': stats,
        'df_relatorio': _montar_relatorio_final_lotes(todos_lotes, data_ref_relatorio),
        'data_ref_relatorio': data_ref_relatorio,
    }
    resultado.update({'status': 'runner_completo', 'resultado_futuro': resultado_futuro, 'extrato_df': extrato_df, 'stats': stats, 'arquivo_saida': None})
    if not exportar_excel:
        print("\n>>> Simulação futura concluída sem exportação Excel.")
        return resultado

    print("\n>>> Gerando relatório final dos lotes...")
    _exportar_resultados_excel(
        arquivo_saida, produtos=produtos, stats=stats, extrato_df=extrato_df,
        log_passado=snapshot.get('log_passado'), df_relatorio=resultado_futuro['df_relatorio'],
        snapshot_lotes_atuais=snapshot.get('snapshot_lotes_atuais'), artefatos_switching=artefatos_switching,
        df_diagnostico_modo=_montar_df_diagnostico_modo_execucao(stats=stats),
    )
    resultado['arquivo_saida'] = arquivo_saida
    print(f"\n>>> Resultados salvos em: {arquivo_saida}")
    print(f"    Switches executados hoje: {artefatos_switching.get('switches_hoje_exec', 0)}")
    print(f"    Switches agendados (futuro): {artefatos_switching.get('switches_agendados', 0)}")
    print(f"    Switches reais (resumo): {stats.get('switches_exec', 0)} (partes criadas: {stats.get('switches_partes_criadas', 0)})")
    print("\n✅  Simulação concluída!\n")
    return resultado

if __name__ == "__main__":
    executar_runner_principal()

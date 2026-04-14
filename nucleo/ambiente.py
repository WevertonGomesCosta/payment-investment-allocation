"""Bootstrap compartilhado e neutro do ambiente do projeto.

Este módulo concentra apenas responsabilidades já auditadas como comuns ou
seguras neste estágio:

- detecção da raiz do repositório;
- configuração seletiva de warnings de rede;
- verificação e instalação opcional de dependências por import real;
- resolução de timezone operacional;
- determinação central da data de referência da análise.

Ele não implementa regras financeiras, fiscais, de pagamento ou de switching.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import warnings
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Mapping, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

DEPENDENCIAS_NUCLEO = {
    "pandas": "pandas",
    "numpy": "numpy",
    "openpyxl": "openpyxl",
    "python-dateutil": "dateutil",
}

GRUPOS_OPCIONAIS = {
    "financeiro": {
        "requests": "requests",
        "pulp": "pulp",
        "workalendar": "workalendar",
    },
    "otimizacao": {
        "scipy": "scipy",
        "numba": "numba",
    },
}


@dataclass(slots=True)
class ContextoExecucao:
    raiz_repositorio: Path
    diretorio_dados: Path
    timezone_nome: str
    em_colab: bool
    data_referencia: date
    warnings_configurados: bool = False
    relatorio_dependencias: dict[str, list[str]] = field(default_factory=dict)


def detectar_raiz_repositorio(caminho_inicial: Optional[Path] = None) -> Path:
    atual = (caminho_inicial or Path(__file__).resolve()).parent
    ancoras = {
        "README.md",
        "requirements.txt",
        "payment-investment-allocation.Rproj",
    }
    for candidato in [atual, *atual.parents]:
        if any((candidato / ancora).exists() for ancora in ancoras):
            return candidato.resolve()
    return atual.resolve()


def ambiente_em_colab() -> bool:
    return "google.colab" in sys.modules


def configurar_warnings_rede() -> bool:
    """Suprime apenas o warning esperado de HTTPS sem verificação SSL."""
    try:
        import urllib3
        from urllib3.exceptions import InsecureRequestWarning
    except Exception:
        return False

    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    urllib3.disable_warnings(InsecureRequestWarning)
    return True


def _mesclar_dependencias(grupos_extras: Optional[Iterable[str]] = None) -> dict[str, str]:
    dependencias = dict(DEPENDENCIAS_NUCLEO)
    for grupo in grupos_extras or []:
        if grupo not in GRUPOS_OPCIONAIS:
            raise ValueError(f"Grupo de dependências desconhecido: {grupo!r}")
        dependencias.update(GRUPOS_OPCIONAIS[grupo])
    return dependencias


def verificar_dependencias(grupos_extras: Optional[Iterable[str]] = None) -> dict[str, list[str]]:
    dependencias = _mesclar_dependencias(grupos_extras)
    instaladas: list[str] = []
    ausentes: list[str] = []

    for nome_pip, nome_import in dependencias.items():
        try:
            importlib.import_module(nome_import)
            instaladas.append(nome_pip)
        except Exception:
            ausentes.append(nome_pip)

    return {"instaladas": sorted(instaladas), "ausentes": sorted(ausentes)}


def instalar_dependencias(dependencias_ausentes: Iterable[str], silencioso: bool = True) -> list[str]:
    pacotes = sorted(set(dependencias_ausentes))
    if not pacotes:
        return []

    comando = [sys.executable, "-m", "pip", "install", *pacotes]
    if silencioso:
        comando.append("--quiet")
    subprocess.check_call(comando)
    return pacotes


def resolver_timezone(nome_timezone: str):
    if ZoneInfo is None:
        return None
    try:
        return ZoneInfo(nome_timezone)
    except Exception:
        return None


def obter_data_referencia(config: Optional[Mapping[str, object]] = None, *, timezone_nome: Optional[str] = None) -> date:
    cfg = dict(config or {})
    execucao_cfg = cfg.get("execucao", {}) if isinstance(cfg.get("execucao"), dict) else {}

    valor_config = execucao_cfg.get("data_referencia_simulacao")
    if valor_config not in (None, ""):
        if isinstance(valor_config, datetime):
            return valor_config.date()
        if isinstance(valor_config, date):
            return valor_config
        try:
            return datetime.fromisoformat(str(valor_config)).date()
        except Exception as erro:
            raise ValueError(
                f"execucao/data_referencia_simulacao inválida: {valor_config!r}. Use ISO 8601 (YYYY-MM-DD)."
            ) from erro

    nome = timezone_nome or str(execucao_cfg.get("timezone") or "America/Sao_Paulo")
    tz = resolver_timezone(nome)
    try:
        return datetime.now(tz).date() if tz is not None else datetime.now().date()
    except Exception:
        return datetime.now().date()


def bootstrap_ambiente(
    config: Optional[Mapping[str, object]] = None,
    *,
    grupos_extras: Optional[Iterable[str]] = None,
    instalar_automaticamente: Optional[bool] = None,
    silencioso: bool = True,
) -> ContextoExecucao:
    cfg = dict(config or {})
    ambiente_cfg = cfg.get("ambiente", {}) if isinstance(cfg.get("ambiente"), dict) else {}
    execucao_cfg = cfg.get("execucao", {}) if isinstance(cfg.get("execucao"), dict) else {}

    raiz = detectar_raiz_repositorio()
    diretorio_dados = (raiz / "dados") if (raiz / "dados").exists() else (raiz / "data")
    timezone_nome = str(execucao_cfg.get("timezone") or "America/Sao_Paulo")

    if instalar_automaticamente is None:
        instalar_automaticamente = bool(ambiente_cfg.get("instalar_dependencias_automaticamente", False))

    relatorio = verificar_dependencias(grupos_extras=grupos_extras)
    if relatorio["ausentes"] and instalar_automaticamente:
        instalar_dependencias(relatorio["ausentes"], silencioso=silencioso)
        relatorio = verificar_dependencias(grupos_extras=grupos_extras)

    return ContextoExecucao(
        raiz_repositorio=raiz,
        diretorio_dados=diretorio_dados,
        timezone_nome=timezone_nome,
        em_colab=ambiente_em_colab(),
        data_referencia=obter_data_referencia(cfg, timezone_nome=timezone_nome),
        warnings_configurados=configurar_warnings_rede(),
        relatorio_dependencias=relatorio,
    )

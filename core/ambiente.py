"""Bootstrap compartilhado do ambiente do projeto.

Este módulo consolida a lógica mínima e segura de ambiente que era duplicada
entre os dois scripts-base. Nesta etapa inicial ele cobre apenas:

- detecção de ambiente local/Colab;
- configuração seletiva de warnings de rede;
- verificação opcional de dependências por import real;
- instalação opcional de dependências ausentes;
- resolução de timezone padrão.

Ele NÃO aplica ainda regras de negócio financeiras, fiscais ou de simulação.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - fallback para ambientes antigos
    ZoneInfo = None  # type: ignore


CORE_DEPENDENCIES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "openpyxl": "openpyxl",
    "python-dateutil": "dateutil",
}

OPTIONAL_DEPENDENCY_GROUPS = {
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
class RuntimeContext:
    """Resumo do bootstrap aplicado ao ambiente."""

    repo_root: Path
    data_dir: Path
    timezone_name: str
    in_colab: bool
    warnings_configured: bool = False
    dependency_report: dict[str, list[str]] = field(default_factory=dict)


def detectar_repo_root(start_path: Optional[Path] = None) -> Path:
    """Detecta a raiz do repositório a partir do caminho informado.

    A busca sobe diretórios até encontrar um arquivo de referência do projeto.
    """
    current = (start_path or Path(__file__).resolve()).parent
    anchors = {"README.md", "requirements.txt", "payment-investment-allocation.Rproj"}

    for candidate in [current, *current.parents]:
        if any((candidate / anchor).exists() for anchor in anchors):
            return candidate
    return current


def ambiente_em_colab() -> bool:
    return "google.colab" in sys.modules


def configurar_warnings_rede() -> bool:
    """Suprime apenas warnings conhecidos de HTTPS sem verificação SSL."""
    try:
        import urllib3
        from urllib3.exceptions import InsecureRequestWarning
    except Exception:
        return False

    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    urllib3.disable_warnings(InsecureRequestWarning)
    return True


def _merge_dependency_groups(extra_groups: Optional[Iterable[str]] = None) -> dict[str, str]:
    deps = dict(CORE_DEPENDENCIES)
    for group in extra_groups or []:
        if group not in OPTIONAL_DEPENDENCY_GROUPS:
            raise ValueError(f"Grupo de dependências desconhecido: {group!r}")
        deps.update(OPTIONAL_DEPENDENCY_GROUPS[group])
    return deps


def verificar_dependencias(extra_groups: Optional[Iterable[str]] = None) -> dict[str, list[str]]:
    """Verifica dependências por import real, não por metadados de pacote."""
    deps = _merge_dependency_groups(extra_groups)
    installed: list[str] = []
    missing: list[str] = []

    for pip_name, import_name in deps.items():
        try:
            importlib.import_module(import_name)
            installed.append(pip_name)
        except Exception:
            missing.append(pip_name)

    return {"installed": sorted(installed), "missing": sorted(missing)}


def instalar_dependencias(missing: Iterable[str], quiet: bool = True) -> list[str]:
    """Instala dependências ausentes via pip e retorna a lista instalada."""
    missing = sorted(set(missing))
    if not missing:
        return []

    cmd = [sys.executable, "-m", "pip", "install", *missing]
    if quiet:
        cmd.append("--quiet")
    subprocess.check_call(cmd)
    return missing


def resolver_timezone(timezone_name: str):
    """Resolve o timezone padrão do projeto quando ZoneInfo está disponível."""
    if ZoneInfo is None:
        return None
    try:
        return ZoneInfo(timezone_name)
    except Exception:
        return None


def bootstrap_ambiente(
    config: Optional[Mapping[str, object]] = None,
    *,
    extra_groups: Optional[Iterable[str]] = None,
    instalar_automaticamente: Optional[bool] = None,
    quiet: bool = True,
) -> RuntimeContext:
    """Aplica o bootstrap mínimo compartilhado do projeto.

    Parameters
    ----------
    config:
        Configuração carregada do projeto. Opcional nesta etapa.
    extra_groups:
        Grupos adicionais de dependências a verificar.
    instalar_automaticamente:
        Força a instalação automática. Quando ``None``, tenta ler a flag do
        config em ``ambiente.instalar_dependencias_automaticamente``.
    quiet:
        Controla verbosidade do pip.
    """
    repo_root = detectar_repo_root()
    data_dir = repo_root / "data"
    timezone_name = "America/Sao_Paulo"

    if isinstance(config, Mapping):
        timezone_name = (
            config.get("execucao", {}) if isinstance(config.get("execucao", {}), Mapping) else {}
        ).get("timezone", timezone_name)
        if instalar_automaticamente is None:
            instalar_automaticamente = (
                config.get("ambiente", {}) if isinstance(config.get("ambiente", {}), Mapping) else {}
            ).get("instalar_dependencias_automaticamente", False)

    if instalar_automaticamente is None:
        instalar_automaticamente = False

    dependency_report = verificar_dependencias(extra_groups=extra_groups)
    if dependency_report["missing"] and instalar_automaticamente:
        instalar_dependencias(dependency_report["missing"], quiet=quiet)
        dependency_report = verificar_dependencias(extra_groups=extra_groups)

    return RuntimeContext(
        repo_root=repo_root,
        data_dir=data_dir,
        timezone_name=timezone_name,
        in_colab=ambiente_em_colab(),
        warnings_configured=configurar_warnings_rede(),
        dependency_report=dependency_report,
    )

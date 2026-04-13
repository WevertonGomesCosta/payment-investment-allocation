"""Carregamento e resolução do config canônico do projeto."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


DEFAULT_PREFERRED_CONFIG = "config_atualizado.json"
DEFAULT_FALLBACK_CONFIG = "config.json"


@dataclass(slots=True)
class ConfigBundle:
    """Objeto leve com o config carregado e seus caminhos resolvidos."""

    path: Path
    project_root: Path
    data_dir: Path
    payload: dict[str, Any]


def discover_project_root(start_path: Optional[Path] = None) -> Path:
    current = (start_path or Path(__file__).resolve()).parent
    anchors = {"README.md", "requirements.txt", "payment-investment-allocation.Rproj"}

    for candidate in [current, *current.parents]:
        if any((candidate / anchor).exists() for anchor in anchors):
            return candidate
    return current


def resolve_config_path(
    project_root: Optional[Path] = None,
    explicit_path: Optional[str | Path] = None,
    preferred_name: str = DEFAULT_PREFERRED_CONFIG,
    fallback_name: str = DEFAULT_FALLBACK_CONFIG,
) -> Path:
    """Resolve o caminho do config canônico do projeto."""
    if explicit_path is not None:
        path = Path(explicit_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Config explícito não encontrado: {path}")
        return path

    root = (project_root or discover_project_root()).resolve()
    candidates = [
        root / "data" / preferred_name,
        root / preferred_name,
        root / "data" / fallback_name,
        root / fallback_name,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    tried = "\n - ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"Nenhum config encontrado. Caminhos testados:\n - {tried}")


def load_config(
    explicit_path: Optional[str | Path] = None,
    project_root: Optional[Path] = None,
) -> ConfigBundle:
    """Carrega o config canônico e retorna metadados úteis."""
    root = (project_root or discover_project_root()).resolve()
    path = resolve_config_path(project_root=root, explicit_path=explicit_path)

    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    return ConfigBundle(
        path=path,
        project_root=root,
        data_dir=root / "data",
        payload=payload,
    )


def get_nested(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Acesso seguro a chaves aninhadas do config."""
    current: Any = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current

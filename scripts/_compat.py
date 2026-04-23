from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_module_entrypoint(module: str) -> None:
    raiz = _repo_root()
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))
    runpy.run_module(module, run_name="__main__")

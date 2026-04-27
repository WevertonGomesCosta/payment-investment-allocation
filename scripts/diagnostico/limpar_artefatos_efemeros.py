"""Limpeza oficial de artefatos efêmeros pré-release.

Remove:
- diretórios __pycache__;
- arquivos *.pyc;
- arquivos *.pyo.

Uso:
    python scripts/diagnostico/limpar_artefatos_efemeros.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:
    from _bootstrap import RAIZ


def limpar_artefatos_efemeros(raiz: Path = RAIZ) -> dict[str, int]:
    removidos_dirs = 0
    removidos_arquivos = 0

    for caminho in sorted(raiz.rglob("__pycache__"), reverse=True):
        if caminho.is_dir():
            shutil.rmtree(caminho, ignore_errors=True)
            removidos_dirs += 1

    for padrao in ("*.pyc", "*.pyo"):
        for caminho in sorted(raiz.rglob(padrao)):
            if caminho.is_file():
                caminho.unlink(missing_ok=True)
                removidos_arquivos += 1

    return {
        "diretorios_pycache_removidos": removidos_dirs,
        "arquivos_bytecode_removidos": removidos_arquivos,
    }


def main() -> int:
    resumo = limpar_artefatos_efemeros(RAIZ)
    print("=== LIMPEZA DE ARTEFATOS EFEMEROS ===")
    print(f"diretorios_pycache_removidos: {resumo['diretorios_pycache_removidos']}")
    print(f"arquivos_bytecode_removidos: {resumo['arquivos_bytecode_removidos']}")
    print("status: limpeza_concluida")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

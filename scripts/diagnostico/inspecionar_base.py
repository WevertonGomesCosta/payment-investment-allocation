"""Atalho de execução para inspecionar a baseline atual."""

from __future__ import annotations

try:
    from scripts.diagnostico._bootstrap import RAIZ
except ModuleNotFoundError:  # execução direta
    from _bootstrap import RAIZ

from aplicacao.console.principal import main


if __name__ == "__main__":
    main()

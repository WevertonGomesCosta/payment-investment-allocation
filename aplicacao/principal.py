"""Wrapper de compatibilidade para o ponto de entrada principal."""
from __future__ import annotations
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
from aplicacao.console.principal import main

if __name__ == "__main__":
    main()

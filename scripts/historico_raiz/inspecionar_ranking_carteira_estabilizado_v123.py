"""Wrapper de compatibilidade para inspecionar o ranking estabilizado da Carteira."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from scripts.diagnostico.inspecionar_ranking_carteira_estabilizado_v123 import main

if __name__ == '__main__':
    main()

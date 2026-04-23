"""Wrapper de compatibilidade para inspecionar heurística conjunta parcial do bloco crítico."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from scripts.diagnostico.inspecionar_heuristica_conjunta_parcial_bloco_critico import main


if __name__ == '__main__':
    raise SystemExit(main())

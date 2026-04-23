"""Wrapper de compatibilidade para inspeção do contrato mínimo da Frente F1."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from scripts.diagnostico.inspecionar_contrato_f1 import main


if __name__ == '__main__':
    raise SystemExit(main())

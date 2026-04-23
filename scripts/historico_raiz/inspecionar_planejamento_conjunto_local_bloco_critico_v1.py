"""Wrapper de compatibilidade para inspecionar o planejamento conjunto local do bloco crítico."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from scripts.diagnostico.inspecionar_planejamento_conjunto_local_bloco_critico_v1 import main


if __name__ == '__main__':
    raise SystemExit(main())

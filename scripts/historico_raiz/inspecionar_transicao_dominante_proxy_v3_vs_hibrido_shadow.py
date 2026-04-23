"""Wrapper de compatibilidade para inspecionar transicao dominante proxy v3 vs hibrido shadow."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from scripts.diagnostico.inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow import main


if __name__ == "__main__":
    raise SystemExit(main())

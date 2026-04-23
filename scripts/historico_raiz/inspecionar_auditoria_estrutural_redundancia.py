from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from scripts.diagnostico.inspecionar_auditoria_estrutural_redundancia import main


if __name__ == '__main__':
    raise SystemExit(main())

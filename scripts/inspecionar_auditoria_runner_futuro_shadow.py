from __future__ import annotations

import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from scripts.diagnostico.inspecionar_auditoria_runner_futuro_shadow import main


if __name__ == '__main__':
    raise SystemExit(main())

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.diagnostico.inspecionar_mapa_absorcao_legado import main


if __name__ == '__main__':
    raise SystemExit(main())

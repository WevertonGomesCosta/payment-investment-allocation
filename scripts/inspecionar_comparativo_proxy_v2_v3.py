from __future__ import annotations

import runpy
import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

if __name__ == '__main__':
    runpy.run_module('scripts.diagnostico.inspecionar_comparativo_proxy_v2_v3', run_name='__main__')

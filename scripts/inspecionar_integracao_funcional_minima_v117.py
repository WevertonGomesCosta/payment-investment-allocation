from __future__ import annotations

from pathlib import Path
import runpy
import sys

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]
ALVO = RAIZ_REPOSITORIO / 'scripts' / 'diagnostico' / 'inspecionar_integracao_funcional_minima_v117.py'
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

if __name__ == '__main__':
    runpy.run_path(str(ALVO), run_name='__main__')

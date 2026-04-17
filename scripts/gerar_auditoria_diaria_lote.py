"""Wrapper de compatibilidade para a auditoria diária de lote."""
from __future__ import annotations
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
from scripts.auditoria.gerar_auditoria_diaria_lote import main

if __name__ == "__main__":
    main()

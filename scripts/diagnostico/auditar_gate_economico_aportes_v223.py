"""Script canônico V223 para gate econômico dos aportes planejados.

Mantém compatibilidade com `auditar_gate_economico_aportes_v220.py`.
"""
from __future__ import annotations

try:
    from scripts.diagnostico.auditar_gate_economico_aportes_v220 import main
except ModuleNotFoundError:
    from auditar_gate_economico_aportes_v220 import main

if __name__ == "__main__":
    raise SystemExit(main())

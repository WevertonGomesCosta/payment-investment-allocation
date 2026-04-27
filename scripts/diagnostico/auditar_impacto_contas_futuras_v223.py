"""Script canônico V223 para auditoria de impacto sobre contas futuras.

Mantém compatibilidade com `auditar_impacto_contas_futuras_v217.py`.
"""
from __future__ import annotations

try:
    from scripts.diagnostico.auditar_impacto_contas_futuras_v217 import main
except ModuleNotFoundError:
    from auditar_impacto_contas_futuras_v217 import main

if __name__ == "__main__":
    raise SystemExit(main())

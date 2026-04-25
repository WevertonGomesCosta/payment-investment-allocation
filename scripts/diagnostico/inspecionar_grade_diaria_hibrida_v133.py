"""Script legado bloqueado pela governança de saídas V203.

O conteúdo original foi preservado em:
    scripts/historico_saida_propria_v203/diagnostico_original/inspecionar_grade_diaria_hibrida_v133.py

Este arquivo permanece no caminho antigo apenas para impedir que rotinas
legadas com saída própria sejam executadas como se fossem oficiais.
"""
from __future__ import annotations

import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
for _parent in _THIS.parents:
    if (_parent / "nucleo").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from scripts.diagnostico._governanca_saida import bloquear_script_legado


MOTIVO = (
    "Script diagnóstico legado com geração própria de console/arquivo, "
    "sem autoridade operacional após a criação da camada única "
    "nucleo.saida_canonica na V202."
)
ALTERNATIVA = (
    "Use scripts/operacional/gerar_planilha_operacional.py ou "
    "nucleo.saida_canonica.construir_saida_canonica(...)."
)


def main() -> int:
    return bloquear_script_legado(__file__, motivo=MOTIVO, alternativa=ALTERNATIVA)


if __name__ == "__main__":
    raise SystemExit(main())

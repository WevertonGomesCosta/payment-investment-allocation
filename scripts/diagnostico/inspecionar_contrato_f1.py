"""Inspeciona o contrato mínimo da Frente F1 sem tocar no motor financeiro."""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
if str(RAIZ_REPOSITORIO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPOSITORIO))

from nucleo.caixa_recebidos_auditaveis import (
    obter_contrato_minimo_caixa_recebidos,
    validar_contrato_minimo_caixa_recebidos,
)


def main() -> int:
    erros = validar_contrato_minimo_caixa_recebidos()
    contrato = obter_contrato_minimo_caixa_recebidos()

    print('=== CONTRATO MÍNIMO F1 ===')
    print(f"frente: {contrato['frente']}")
    print(f"nome: {contrato['nome']}")
    print(f"escopo_etapa_atual: {contrato['escopo_etapa_atual']}")
    print(f"estruturas: {len(contrato['estruturas'])}")
    if erros:
        print(f'status: FALHA ({len(erros)} problema(s))')
        for erro in erros:
            print(f'- {erro}')
        return 1
    print('status: OK')
    print(json.dumps(contrato, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

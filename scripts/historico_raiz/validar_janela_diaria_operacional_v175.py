from __future__ import annotations

import json
from datetime import date
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from nucleo.runner_validacao_diaria_operacional_v175 import rodar_validacao_diaria_operacional_v175


def main() -> None:
    raiz = RAIZ
    resultado = rodar_validacao_diaria_operacional_v175(
        raiz_repositorio=raiz,
        data_inicio=date(2026, 4, 23),
        data_fim=date(2026, 5, 23),
        limite_candidatos_por_data=8,
        cap_fontes_destino=3,
    )
    saida = raiz / 'saidas' / 'validacao_diaria_operacional_v175_2026-04-23_2026-05-23.json'
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Arquivo gerado: {saida}')
    print(json.dumps(resultado.get('resumo') or {}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

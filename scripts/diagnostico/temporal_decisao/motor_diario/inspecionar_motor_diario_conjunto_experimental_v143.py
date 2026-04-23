from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from nucleo.motor_diario_conjunto_experimental_v143 import rodar_motor_diario_conjunto_experimental_v143


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    saida = rodar_motor_diario_conjunto_experimental_v143(
        raiz_repositorio=raiz,
        data_inicio=date(2026, 4, 21),
        data_fim=date(2026, 5, 6),
        limite_candidatos_por_data=24,
        cap_fontes_destino=5,
    )
    destino = raiz / 'saidas' / 'diagnostico' / 'motor_diario_conjunto_experimental_v143_2026-04-21_2026-05-06.json'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(destino)


if __name__ == '__main__':
    main()

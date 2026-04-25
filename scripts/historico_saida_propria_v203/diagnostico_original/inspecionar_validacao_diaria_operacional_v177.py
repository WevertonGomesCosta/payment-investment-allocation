from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from nucleo.runner_validacao_diaria_operacional_v177 import rodar_validacao_diaria_operacional_v177


RAIZ = Path(__file__).resolve().parents[2]


def main() -> None:
    resultado = rodar_validacao_diaria_operacional_v177(
        raiz_repositorio=RAIZ,
        data_inicio=date(2026, 4, 23),
        data_fim=date(2026, 5, 23),
        limite_candidatos_por_data=8,
        cap_fontes_destino=3,
    )
    saida = RAIZ / 'saidas' / 'validacao_diaria_operacional_v177_2026-04-23_2026-05-23.json'
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(saida)


if __name__ == '__main__':
    main()

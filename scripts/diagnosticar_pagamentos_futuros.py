from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from diagnostico_futuro import diagnosticar_pagamentos_futuros
from pipeline_fase1 import executar_pipeline_inicial


def _to_records(df, limit: int | None = None):
    if df is None or df.empty:
        return []
    if limit is not None:
        df = df.head(limit)
    out = []
    for row in df.to_dict(orient="records"):
        converted = {}
        for key, value in row.items():
            if hasattr(value, "isoformat"):
                converted[key] = value.isoformat()
            else:
                converted[key] = value
        out.append(converted)
    return out


def main() -> None:
    config_path = ROOT / "config" / "config_minimo_v1.json"
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)
    diagnostico = diagnosticar_pagamentos_futuros(estado)

    payload = {
        "resumo": diagnostico.resumo,
        "datas_criticas": _to_records(
            diagnostico.timeline.loc[
                diagnostico.timeline["deficit_sem_resgate_centavos"] > 0,
                [
                    "data",
                    "caixa_depois_sem_resgate_centavos",
                    "deficit_sem_resgate_centavos",
                    "resgates_realizados_centavos",
                    "caixa_depois_com_resgate_centavos",
                    "saldo_investido_liquido_pos_dia_centavos",
                ],
            ],
            limit=20,
        ),
        "resgates_sugeridos": _to_records(diagnostico.resgates, limit=30),
        "candidatos_primeira_data_critica": _to_records(diagnostico.candidatos_primeira_data_critica, limit=10),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

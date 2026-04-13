from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from pipeline_fase1 import executar_pipeline_inicial
from politica_conjunta_switching import diagnosticar_politica_conjunta_switching


def _json_safe(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    rows = []
    for row in df.to_dict(orient="records"):
        rows.append({k: _json_safe(v) for k, v in row.items()})
    return rows


def main() -> None:
    config_path = ROOT / "config" / "config_minimo_v1.json"
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)
    resultado = diagnosticar_politica_conjunta_switching(estado)

    payload = {
        "resumo": resultado.resumo,
        "comparacao_base": resultado.comparacao_base,
        "switchings": _records(resultado.switchings),
        "resgates": _records(resultado.resgates),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

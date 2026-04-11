from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from comparacao_switching_resgates import comparar_switching_vs_resgates
from pipeline_fase1 import executar_pipeline_inicial


def _json_safe(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _records(df, limit: int | None = None):
    if df is None or df.empty:
        return []
    if limit is not None:
        df = df.head(limit)
    out = []
    for row in df.to_dict(orient="records"):
        out.append({k: _json_safe(v) for k, v in row.items()})
    return out


def main() -> None:
    config_path = ROOT / "config" / "config_minimo_v1.json"
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)
    resultado = comparar_switching_vs_resgates(estado)

    payload = {
        "resumo": resultado.resumo,
        "comparacao_por_data": _records(resultado.comparacao_por_data, limit=100),
        "top_candidatos_por_data": _records(resultado.top_candidatos_por_data, limit=100),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

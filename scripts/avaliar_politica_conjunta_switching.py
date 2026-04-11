from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline_fase1 import executar_pipeline_inicial
from politica_conjunta_switching import diagnosticar_politica_conjunta_switching, diagnosticar_sensibilidade_top_k_switching


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


def _parse_topks(args: list[str]) -> tuple[int, ...]:
    out = []
    for a in args:
        try:
            out.append(int(a))
        except ValueError:
            continue
    return tuple(out) if out else (1,)


def main() -> None:
    config_path = ROOT / "config" / "config_minimo_v1.json"
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")
    topks = _parse_topks(sys.argv[2:])

    _, estado = executar_pipeline_inicial(config_path, workbook_path=workbook_path)

    if len(topks) == 1:
        resultado = diagnosticar_politica_conjunta_switching(estado, top_k_switch_por_data=topks[0])
        payload = {
            "resumo": resultado.resumo,
            "comparacao_base": resultado.comparacao_base,
            "switchings": _records(resultado.switchings),
            "resgates": _records(resultado.resgates),
        }
    else:
        resultado = diagnosticar_sensibilidade_top_k_switching(estado, top_ks=topks)
        payload = {
            "resumo": resultado.resumo,
            "sensibilidade": _records(resultado.sensibilidade),
            "switchings_recomendado": _records(resultado.melhor_switchings),
            "resgates_recomendado": _records(resultado.melhor_resgates),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

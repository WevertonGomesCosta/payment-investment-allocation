from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from diagnostico_futuro import obter_datas_criticas_sem_resgate
from motor_switching import gerar_candidatos_switching_datas_criticas, gerar_candidatos_switching_por_data
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
    criticas = obter_datas_criticas_sem_resgate(estado)
    primeira_data = None
    primeira_deficit = None
    candidatos_primeira = None
    if not criticas.empty:
        primeira_data = criticas.iloc[0]["data"]
        primeira_deficit = int(criticas.iloc[0]["deficit_sem_resgate_centavos"])
        candidatos_primeira = gerar_candidatos_switching_por_data(
            estado=estado,
            data_critica=primeira_data,
            deficit_centavos=primeira_deficit,
        )
    else:
        candidatos_primeira = None

    todos = gerar_candidatos_switching_datas_criticas(estado=estado)

    payload = {
        "qtd_datas_criticas": int(len(criticas)),
        "qtd_candidatos_total": int(len(todos)),
        "primeira_data_critica": primeira_data.isoformat() if primeira_data is not None else None,
        "deficit_primeira_data_centavos": primeira_deficit,
        "resumo_por_data": _to_records(criticas[["data", "deficit_sem_resgate_centavos"]], limit=50) if not criticas.empty else [],
        "candidatos_primeira_data": _to_records(candidatos_primeira, limit=25),
        "candidatos_top_geral": _to_records(todos, limit=50),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

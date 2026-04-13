from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from baseline_guardrails import compare_candidate_to_baseline, load_baseline_reference, save_report  # noqa: E402
from pipeline_fase1 import executar_pipeline_inicial  # noqa: E402
from politica_conjunta_switching import diagnosticar_politica_conjunta_switching  # noqa: E402


def _json_safe(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _records(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    return [{k: _json_safe(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def main() -> None:
    workbook_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/mnt/data/dados_financeiros.xlsx")
    candidate_output = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO_ROOT / "outputs" / "bonus_block_candidate.json"
    report_output = Path(sys.argv[3]) if len(sys.argv) > 3 else REPO_ROOT / "outputs" / "bonus_block_baseline_report.json"

    _, estado = executar_pipeline_inicial(REPO_ROOT / "config" / "config_minimo_v1.json", workbook_path=workbook_path)
    resultado = diagnosticar_politica_conjunta_switching(estado)

    payload = {
        "resumo": resultado.resumo,
        "comparacao_base": resultado.comparacao_base,
        "switchings": _records(resultado.switchings),
        "resgates": _records(resultado.resgates),
    }
    candidate_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    baseline = load_baseline_reference(REPO_ROOT / "config" / "baseline_v2_oficial.json")
    report = compare_candidate_to_baseline(baseline, payload)
    save_report(report, report_output)

    status = "APPROVED" if report.approved_for_official_line else "REJECTED"
    print(f"Candidate saved to: {candidate_output}")
    print(f"Baseline comparison status: {status}")
    print(f"Report saved to: {report_output}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.baseline_guardrails import (  # noqa: E402
    compare_candidate_to_baseline,
    load_baseline_reference,
    load_json,
    save_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida um refinamento candidato contra a baseline oficial v2.",
    )
    parser.add_argument(
        "candidate_json",
        help="Arquivo JSON da política candidata (espera estrutura com campo 'resumo').",
    )
    parser.add_argument(
        "--baseline",
        default=str(REPO_ROOT / "config" / "baseline_v2_oficial.json"),
        help="Arquivo JSON com a baseline oficial.",
    )
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "outputs" / "baseline_comparison_report.json"),
        help="Arquivo JSON de saída para o relatório de comparação.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    baseline = load_baseline_reference(args.baseline)
    candidate_payload = load_json(args.candidate_json)
    report = compare_candidate_to_baseline(baseline, candidate_payload)
    save_report(report, args.output)

    status = "APPROVED" if report.approved_for_official_line else "REJECTED"
    print(f"Baseline comparison status: {status}")
    print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()

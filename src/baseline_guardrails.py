from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BaselineAcceptanceRules:
    require_full_payment_coverage: bool = True
    require_terminal_wealth_not_below_baseline: bool = True
    require_same_horizon: bool = True
    allow_more_switchings: bool = True
    allow_more_redemptions: bool = True


@dataclass(frozen=True)
class BaselineReference:
    baseline_name: str
    source_policy: str
    reference_summary: dict[str, Any]
    acceptance_rules: BaselineAcceptanceRules
    informational_metrics: list[str]


@dataclass(frozen=True)
class BaselineCheck:
    name: str
    passed: bool
    message: str
    baseline_value: Any
    candidate_value: Any


@dataclass(frozen=True)
class BaselineComparisonReport:
    baseline_name: str
    baseline_policy: str
    candidate_policy: str
    approved_for_official_line: bool
    checks: list[BaselineCheck]
    baseline_summary: dict[str, Any]
    candidate_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checks"] = [asdict(check) for check in self.checks]
        return payload


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_baseline_reference(path: str | Path) -> BaselineReference:
    payload = load_json(path)
    return BaselineReference(
        baseline_name=payload["baseline_name"],
        source_policy=payload["source_policy"],
        reference_summary=payload["reference_summary"],
        acceptance_rules=BaselineAcceptanceRules(**payload["acceptance_rules"]),
        informational_metrics=payload.get("informational_metrics", []),
    )


def extract_summary(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    if "resumo" in candidate_payload:
        return candidate_payload["resumo"]
    return candidate_payload


def _check_bool(name: str, expected: bool, actual: bool, required: bool) -> BaselineCheck:
    passed = (actual is expected) if required else True
    message = f"{name}: expected {expected}, got {actual}."
    if not required:
        message = f"{name}: informational only. expected {expected}, got {actual}."
    return BaselineCheck(name=name, passed=passed, message=message, baseline_value=expected, candidate_value=actual)


def compare_candidate_to_baseline(
    baseline: BaselineReference,
    candidate_payload: dict[str, Any],
) -> BaselineComparisonReport:
    candidate_summary = extract_summary(candidate_payload)
    baseline_summary = baseline.reference_summary
    rules = baseline.acceptance_rules

    checks: list[BaselineCheck] = []

    if rules.require_same_horizon:
        checks.append(
            BaselineCheck(
                name="same_horizon",
                passed=(candidate_summary.get("horizonte_final") == baseline_summary.get("horizonte_final")),
                message=(
                    f"same_horizon: expected {baseline_summary.get('horizonte_final')}, "
                    f"got {candidate_summary.get('horizonte_final')}."
                ),
                baseline_value=baseline_summary.get("horizonte_final"),
                candidate_value=candidate_summary.get("horizonte_final"),
            )
        )

    checks.append(
        _check_bool(
            name="full_payment_coverage",
            expected=bool(baseline_summary.get("cobertura_total_viavel", True)),
            actual=bool(candidate_summary.get("cobertura_total_viavel", False)),
            required=rules.require_full_payment_coverage,
        )
    )

    baseline_wealth = int(baseline_summary.get("riqueza_final_politica_conjunta_centavos", 0))
    candidate_wealth = int(candidate_summary.get("riqueza_final_politica_conjunta_centavos", 0))
    wealth_passed = candidate_wealth >= baseline_wealth if rules.require_terminal_wealth_not_below_baseline else True
    checks.append(
        BaselineCheck(
            name="terminal_wealth_not_below_baseline",
            passed=wealth_passed,
            message=(
                f"terminal_wealth_not_below_baseline: baseline={baseline_wealth}, candidate={candidate_wealth}."
            ),
            baseline_value=baseline_wealth,
            candidate_value=candidate_wealth,
        )
    )

    for metric in baseline.informational_metrics:
        checks.append(
            BaselineCheck(
                name=f"informational::{metric}",
                passed=True,
                message=f"informational metric {metric}",
                baseline_value=baseline_summary.get(metric),
                candidate_value=candidate_summary.get(metric),
            )
        )

    approved = all(check.passed for check in checks if not check.name.startswith("informational::"))
    return BaselineComparisonReport(
        baseline_name=baseline.baseline_name,
        baseline_policy=baseline.source_policy,
        candidate_policy=str(candidate_summary.get("politica", "UNKNOWN")),
        approved_for_official_line=approved,
        checks=checks,
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
    )


def save_report(report: BaselineComparisonReport, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

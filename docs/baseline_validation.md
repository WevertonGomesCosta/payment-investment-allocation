# Baseline Validation Rules

## Official line

The **official development line** of the project is anchored to the **v2 official baseline**.

A candidate refinement may only replace the official line if it satisfies the baseline guardrails.

## Required guardrails

A candidate policy must satisfy all required checks below:

1. **same horizon**
   - the candidate must be evaluated on the same horizon used by the official baseline.

2. **full payment coverage**
   - the candidate must keep full future payment coverage feasible.

3. **terminal wealth not below baseline**
   - the candidate must not reduce terminal wealth relative to the official baseline.

## Informational metrics

These metrics are tracked for interpretation, but do not automatically reject a candidate on their own:

- number of switching dates
- number of switching events
- number of redemption events
- gain versus the underlying redemption-only policy

## Current baseline reference

The current official baseline is stored in:

- `config/baseline_v2_oficial.json`

## Validation script

Use the validation script below to compare any future candidate policy against the baseline:

```bash
python scripts/validar_refinamento_contra_baseline_v2.py /path/to/candidate_policy.json
```

This produces a comparison report in `outputs/baseline_comparison_report.json` by default.

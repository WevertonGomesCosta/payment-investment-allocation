# Next Stage Opened on Top of v2

## Active continuation line

All next development should start from the **v2 official baseline**.

## Immediate development focus

Refine the global intertemporal policy only when the refinement can beat v2 on the main criterion:

- full payment coverage remains feasible
- terminal wealth improves relative to v2
- lot-level auditability is preserved

## Not active as baseline

- v5 remains documented as an experimental methodological branch
- switching bundles/conjuntos remain non-priority until stronger evidence appears

## First concrete task of the new front

The first mandatory task in the new front is to validate every candidate refinement against the official v2 baseline before promoting it into the official line.

This rule is now materialized in:

- `config/baseline_v2_oficial.json`
- `src/baseline_guardrails.py`
- `scripts/validar_refinamento_contra_baseline_v2.py`

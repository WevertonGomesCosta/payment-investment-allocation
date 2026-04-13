# Methodology

## Core idea

The project is based on individual financial lots as the central unit of analysis.

Each lot may:

- remain free,
- become invested,
- be partially consumed,
- be fully consumed,
- be preserved for future liquidity needs.

## Historical and prospective split

A model cutoff date (`data_corte_modelo`) separates:

- already executed historical events,
- future events subject to prospective diagnosis and later decision logic.

## Current implemented methodological steps

1. Load minimal configuration.
2. Read workbook sheets.
3. Normalize expenses, lots, and portfolio products.
4. Infer the model cutoff date.
5. Reconstruct historical lot consumption.
6. Build the prospective state.
7. Price invested positions.
8. Diagnose future payment coverage.
9. Select candidate redemptions.
10. Apply an intertemporal redemption policy.
11. Materialize canonical switching contracts and invariants.

## Switching semantics formalized in this phase

This phase defines switching as a distinct operation from redemption.

A valid individual switching contract must:

- start from a lot in `INVESTIDO_ATUAL`,
- have positive liquid transferable value,
- respect the lot switching eligibility date,
- preserve lineage between origin lot and projected destination lot,
- use an active destination product,
- reject destination products that are `Somente_Combo`,
- reject explicit `Combo` destination products until combo-aware logic is added,
- respect destination minimum and maximum application constraints,
- preserve financial conservation.

Two contract types are currently formalized:

- `INDIVIDUAL_TOTAL`
- `INDIVIDUAL_PARCIAL`

At this stage, switching bundles/conjuntos remain out of scope.

## Current methodological limitations

The current implementation does not yet solve a global optimization problem. It provides an auditable incremental decision framework.

Switching policy is still contract-first: contracts and invariant checks are materialized, but a full joint policy with redemptions is still deferred.


## Baseline decision

The project currently freezes **v2** as the official baseline because it produced the strongest terminal-wealth result among the validated joint-policy variants while keeping full payment coverage feasible. More conservative variants such as **v5** remain useful as methodological references, but they are not the active continuation line.


## Remaining-bonus dominance restriction for switching

A switching candidate must be rejected when the origin product still has a remaining bonus window that dominates the destination over a comparable horizon.

Operationally, the engine now:
- computes remaining bonus days for the origin lot at the switching date;
- projects the origin over that remaining bonus window;
- projects the destination over the same window, starting at the switching date;
- blocks switching whenever the origin still dominates the destination during that comparable bonus period.

This restriction is structural and applies before the economic comparison between keep, redeem, and switch.


Programmatic structural-dominance of the origin portfolio now replaces any fixed lot-level switching block.

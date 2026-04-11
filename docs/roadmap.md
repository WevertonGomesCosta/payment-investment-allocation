# Roadmap

## Phase 1 - Methodological base

- minimal config loader
- workbook loading
- normalization
- historical reconstruction
- pricing engine
- future payment diagnosis
- redemption candidate policy
- switching contracts and invariants

## Phase 2 - Switching layer

- generate switching candidates
- compare redemption vs switching
- introduce minimal switching diagnostics
- validate destinations and combo restrictions more deeply

## Phase 3 - Joint decision policy

- combine redemption and switching policies
- preserve future liquidity under joint decisions
- improve lot-level opportunity cost logic

## Phase 4 - Global allocation engine

- expand to intertemporal joint optimization
- evaluate terminal value consistently across combined strategies

## Phase 5 - Reporting and publication

- stable outputs
- stronger auditing layer
- public-facing documentation and examples


## Current bridge step before joint policy

- compare switching candidates against current redemptions on critical dates
- identify dates where switching fully substitutes or partially improves a redemption
- only then integrate switching into the intertemporal policy


## New incremental step

- integrate switching into the intertemporal policy using a conservative same-day rule
- apply switching before redemptions only when it improves the remaining invested position after covering the deficit


- completed: hardened intertemporal evaluation for the joint redemption + switching policy using horizon replay after each critical date


## Near-term refinement

- evaluate small `top_k_switch_por_data` sensitivity values (e.g., 1 vs 2 vs 3)
- keep the smallest value that preserves terminal wealth while controlling computational cost


## Current note

The current switching layer now includes materiality filtering and dominant-lot preservation. Immediate next steps should prioritize stronger global policy logic before opening switching bundles.

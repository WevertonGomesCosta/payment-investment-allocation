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

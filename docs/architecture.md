# Architecture

## Current architectural principle

The repository is intentionally organized around a small methodological core.

Current modules:

- `config_loader.py`: loads and validates the minimal project configuration
- `carregamento.py`: reads the workbook sheets
- `normalizacao.py`: normalizes raw sheets into model-ready dataframes
- `reconstrucao_historica.py`: reconstructs lot usage and initializes the prospective state
- `motor_precificacao.py`: prices invested lots under simplified market assumptions
- `diagnostico_futuro.py`: evaluates future payment coverage and liquidity pressure
- `motor_resgates.py`: selects candidate redemptions and applies the current policy
- `motor_switching.py`: defines switching contracts, invariant checks, and minimum economic comparison between keep, redeem, and switch
- `politica_conjunta_switching.py`: integrates switching into the intertemporal replay by allowing switching before same-day redemptions on critical dates

## Current separation of concerns

- input reading is isolated from normalization,
- normalization is isolated from historical replay,
- pricing is isolated from payment diagnostics,
- redemption policy is isolated from workbook parsing,
- switching contracts are isolated from the later joint policy layer.

## Deferred layers

These layers are explicitly postponed:

- switching bundle/conjunto policy,
- joint decision engine,
- global optimization,
- production-grade export and reporting.


### Hardened joint policy evaluation

The current joint policy no longer accepts switching based only on same-day balance improvements. Candidate switching actions are now re-evaluated through the remaining horizon, using the current redemption policy on future critical dates before accepting the local decision.


## Hardened joint switching policy

The current joint switching policy evaluates the remaining horizon before accepting a switch, applies a materiality filter to avoid marginal operations, tests a small set of switching sizes, and preserves future balance on the dominant lot through a reserve heuristic.

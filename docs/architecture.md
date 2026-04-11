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

## Current separation of concerns

- input reading is isolated from normalization,
- normalization is isolated from historical replay,
- pricing is isolated from payment diagnostics,
- redemption policy is isolated from workbook parsing.

## Deferred layers

These layers are explicitly postponed:

- switching policy,
- joint decision engine,
- global optimization,
- production-grade export and reporting.

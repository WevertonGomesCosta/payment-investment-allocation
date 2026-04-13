# payment-investment-allocation

Baseline repository for the incremental unification of two financial scripts:

- a **payment/redemption optimizer**;
- a **switching allocator** for invested and available lots.

The project goal is to evolve into a single auditable system for **allocation of received cash to payments and investments**, jointly considering:

- future expenses with scheduled payment dates;
- lots already invested, lots marked with `-`, and lots still available;
- portfolio products with rates, bonus rates, maturity, lock-up, and liquidity constraints;
- individual and combined switching decisions;
- the best product and the best date for a new allocation or switching event;
- the joint interaction between payment coverage and investment/switching choices;
- the final objective of **maximizing terminal net wealth with financially correct calculations**.

## Current Repository Status

This repository is now being used as the **official baseline for controlled versioning**.

At the current stage, the repository is intentionally minimal and contains:

- the project metadata files;
- the current financial workbook;
- the current canonical configuration file;
- the dependency list;
- the project file used in the local development environment.

This means the repository is currently acting as a **baseline container** for the next modularization steps, before the full source tree is organized.

## Current Baseline

- **Baseline name:** V1
- **Repository role:** official base for the next controlled derivations (`v2`, `v3`, ...)
- **Development policy:** every update should generate a complete zipped repository version
- **Current objective:** prepare the repository structure and documentation before extracting shared modules from the two original scripts

## Canonical Inputs

The project currently uses the files stored in `data/` as the working baseline:

- `data/config_atualizado.json`
- `data/dados_financeiros.xlsx`

These files are the current canonical inputs for the first repository reorganization steps.

## Operational Scope of the Project

The unified project should ultimately support:

1. canonical loading of configuration and workbook data;
2. normalization of sheets and columns;
3. reconstruction of historical lot usage;
4. valuation of lots over time;
5. payment coverage analysis;
6. economically consistent redemption selection;
7. switching analysis for invested and available lots;
8. joint scenario evaluation across payments, redemptions, new allocations, and switching;
9. comparison of scenarios under a terminal net wealth objective.

## Current Repository Structure

```text
payment-investment-allocation/
├── .editorconfig
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── payment-investment-allocation.Rproj
├── requirements.txt
└── data/
    ├── config_atualizado.json
    └── dados_financeiros.xlsx
```

## Planned Next Structural Phase

The next implementation phase is expected to introduce a modular source tree similar to:

```text
payment-investment-allocation/
├── app/
├── core/
├── motores/
├── estrategias/
├── adapters/
├── scripts/
├── tests/
├── outputs/
└── data/
```

This structure is not yet fully materialized in the repository and should only be added in controlled future versions.

## Design Principles

The repository should evolve under these principles:

- **single canonical config**;
- **single canonical data interpretation**;
- **lot-by-lot traceability**;
- **financial and fiscal auditability**;
- **incremental modularization**;
- **controlled versioning by repository snapshot**;
- **no deep structural corrections before the core unification is stable**.

## Versioning Policy

All future updates should follow this pattern:

- `v1` = current baseline after repository alignment;
- `v2`, `v3`, ... = next controlled derivations;
- each update must be returned as a **full repository `.zip` package**.

## Immediate Next Step

After this V1 baseline alignment, the next task is to inspect the two original scripts section by section and extract the first shared modules, starting from:

- environment/bootstrap;
- config loading;
- workbook loading;
- normalization/canonicalization.

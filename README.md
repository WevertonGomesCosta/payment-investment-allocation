# payment-investment-allocation

Controlled repository for the incremental unification of two financial scripts:

- a payment/redemption optimizer;
- a switching allocator for invested and available lots.

The long-term objective is to evolve this baseline into a single auditable project for
joint allocation of received cash across payments, investments, and switching decisions,
maximizing terminal net wealth under financially correct rules.

## Current Repository Status

This repository is the official controlled baseline for the modular unification effort.

**Current version:** V2

At this stage, the repository now contains:

- the canonical workbook and config under `data/`;
- the first shared Python modules extracted from the two original scripts;
- a minimal application entry point for baseline inspection;
- placeholder directories for the next controlled modularization steps.

## Canonical Inputs

The working baseline currently uses:

- `data/config_atualizado.json`
- `data/dados_financeiros.xlsx`

These files remain the canonical starting point for the first structural migration steps.

## What Was Added in V2

V2 creates the first modular layer without touching the deep financial core yet.

New shared modules:

- `core/ambiente.py`
  - selective network warning handling;
  - environment detection;
  - dependency verification and optional installation;
  - timezone/bootstrap context.

- `core/config_loader.py`
  - repository root discovery;
  - canonical config path resolution;
  - JSON config loading;
  - safe nested config access.

- `core/io_planilha.py`
  - canonical workbook path resolution;
  - workbook loading;
  - initial sheet loading;
  - initial column canonicalization based on config aliases.

Minimal application entry point:

- `app/main.py`

This entry point only inspects the baseline and prints a structured summary of the
current config and workbook. It does **not** run payment optimization, switching,
simulation, or financial reconciliation yet.

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
├── app/
│   └── main.py
├── core/
│   ├── __init__.py
│   ├── ambiente.py
│   ├── config_loader.py
│   └── io_planilha.py
├── motores/
│   └── __init__.py
├── estrategias/
│   └── __init__.py
├── adapters/
│   └── __init__.py
├── scripts/
│   └── inspecionar_baseline.py
├── tests/
├── data/
│   ├── config_atualizado.json
│   ├── dados_financeiros.xlsx
│   ├── raw/
│   │   └── .gitkeep
│   ├── interim/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── outputs/
│   └── .gitkeep
└── reports/
    └── .gitkeep
```

## Minimal Usage

Create or activate your Python environment and install the current requirements:

```bash
pip install -r requirements.txt
```

Run the baseline inspection entry point from the repository root:

```bash
python app/main.py
```

or:

```bash
python scripts/inspecionar_baseline.py
```

The command prints:

- resolved repository root;
- resolved config path;
- resolved workbook path;
- dependency report;
- workbook sheet names;
- initial workbook summary.

## Design Principles Maintained

This repository still follows the controlled migration policy:

- single canonical config;
- single canonical workbook interpretation;
- incremental modularization;
- lot-level auditability as a future invariant;
- no deep structural corrections before core unification is stable;
- full zipped repository delivery at each version.

## What V2 Does Not Change Yet

V2 deliberately does **not** implement or rewrite:

- financial core calculations;
- tax logic;
- IOF/IR reconciliation;
- payment ranking;
- switching ranking;
- joint scenario evaluation;
- historical lot reconstruction.

Those layers should be migrated in later controlled versions.

## Immediate Next Structural Step

The next controlled version should focus on expanding the shared core around:

- canonical sheet/block loading;
- initial entity contracts for lots, expenses, and products;
- basic validation/reporting of critical sheet columns;
- preparation for the first migration of payment and switching domain logic.

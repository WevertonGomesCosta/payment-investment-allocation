# Contributing

## Scope

This repository is currently in a methodological phase. Contributions should preserve:

- lot-level traceability,
- clear separation between historical and prospective states,
- auditable financial logic,
- incremental architectural evolution.

## Basic workflow

1. Create a dedicated branch from `main`.
2. Keep changes focused on a single concern.
3. Do not commit real financial workbooks or private data.
4. Update documentation when changing contracts or methodology.
5. Run a basic syntax check before opening a pull request.

## Commit style

Recommended prefixes:

- `feat:` new functionality
- `fix:` bug fix
- `refactor:` internal restructuring
- `docs:` documentation updates
- `test:` tests and validation utilities

## Data policy

Never commit:

- real spreadsheets,
- personal financial data,
- output files derived from sensitive workbooks.

Use placeholders, `.gitkeep`, or anonymized examples only.

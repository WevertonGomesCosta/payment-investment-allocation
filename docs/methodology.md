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

## Current methodological limitations

The current implementation does not yet solve a global optimization problem. It provides an auditable incremental decision framework.

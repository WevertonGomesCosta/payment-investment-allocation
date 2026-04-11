# Payment-Investment Allocation

A Python project for **lot-based liquidity allocation** across future payments, invested positions, and liquidity-constrained redemption decisions.

## Overview

This repository implements an incremental methodological framework for:

- reconstructing historical lot usage,
- initializing a prospective financial state,
- pricing invested positions under simplified market assumptions,
- diagnosing future payment coverage,
- selecting redemption candidates,
- applying an intertemporal redemption policy with future-preservation logic.

The project is built around the principle that each financial lot should be tracked individually, both economically and operationally, to support auditable decisions involving:

- paid and future expenses,
- received and invested lots,
- portfolio products with different liquidity profiles,
- future redemption pressure,
- preservation of terminal value.

## Current Stage

The repository is currently in an **incremental methodological phase**.

At this stage, the implemented scope includes:

- workbook loading and minimal configuration,
- schema normalization,
- historical reconstruction of paid expenses and consumed lots,
- initialization of the prospective financial state,
- pricing of invested lots under simplified market assumptions,
- diagnosis of future payment coverage,
- candidate redemption selection,
- an intertemporal redemption policy.
- canonical switching contracts and invariants for the next methodological layer.

The following components are intentionally postponed to later phases:

- switching policy execution,
- joint allocation between redemptions and reallocation,
- portfolio optimization,
- global intertemporal search,
- full production export pipeline.

## Core Problem

The project addresses a joint financial decision problem in which future payments must be covered while preserving as much terminal wealth as possible.

The system must decide, over time:

- when current free cash is sufficient,
- when future free lots are enough,
- when invested positions must be redeemed,
- which invested lot is economically less costly to redeem,
- how current redemption choices affect future liquidity pressure.

## Current Implemented Components

Source modules currently included:

- `src/tipos.py`
- `src/config_loader.py`
- `src/estado.py`
- `src/carregamento.py`
- `src/normalizacao.py`
- `src/reconstrucao_historica.py`
- `src/motor_precificacao.py`
- `src/pipeline_fase1.py`
- `src/diagnostico_futuro.py`
- `src/motor_resgates.py`
- `src/motor_switching.py`

Scripts currently included:

- `scripts/inspecionar_estado_inicial.py`
- `scripts/diagnosticar_pagamentos_futuros.py`
- `scripts/selecionar_resgates_candidatos.py`
- `scripts/avaliar_politica_resgates_intertemporal.py`

## Repository Structure

```text
payment-investment-allocation/
├── README.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .gitattributes
├── pyproject.toml
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
├── config/
│   └── config_minimo_v1.json
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── scripts/
├── src/
├── tests/
└── outputs/
```

## Input Data

The current implementation expects an Excel workbook with three main sheets:

- `Todos os Gastos`
- `Inventário de Lotes`
- `Carteira`

These sheets are normalized internally into model-ready structures.

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place the workbook locally

The real workbook should **not** be committed to the repository. Place it in a local path and pass it explicitly to the scripts.

### 3. Run the initial inspection

```bash
python scripts/inspecionar_estado_inicial.py /path/to/dados_financeiros.xlsx
```

### 4. Diagnose future payments

```bash
python scripts/diagnosticar_pagamentos_futuros.py /path/to/dados_financeiros.xlsx
```

### 5. Inspect candidate redemptions

```bash
python scripts/selecionar_resgates_candidatos.py /path/to/dados_financeiros.xlsx
```

### 6. Evaluate the intertemporal redemption policy

```bash
python scripts/avaliar_politica_resgates_intertemporal.py /path/to/dados_financeiros.xlsx
```

## Methodological Notes

This repository currently prioritizes:

- traceability by financial lot,
- explicit historical reconstruction,
- separation between historical and prospective states,
- auditable decision logic,
- incremental implementation.

## Current Limitations

This is not yet a full global optimizer.

At the current stage, the project still uses simplified assumptions for:

- taxation in some historical replay situations,
- cost modeling for certain financial products,
- combo product handling,
- switching execution policy,
- fully integrated long-horizon optimization.

## Documentation

Additional notes are available in:

- `docs/architecture.md`
- `docs/methodology.md`
- `docs/data_dictionary.md`
- `docs/roadmap.md`
- `docs/switching_contracts.md`
- `docs/github_repository_setup.md`

## Roadmap

- harden historical financial reconciliation,
- refine intertemporal redemption policy,
- deepen switching candidate generation,
- compare redemption vs switching under real critical dates,
- implement joint decision policy,
- expand auditing and reporting.

## License

MIT

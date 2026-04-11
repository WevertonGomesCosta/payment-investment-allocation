# Lot-Based Liquidity Allocation

A Python project for lot-based cashflow allocation across future payments, invested positions, and liquidity-constrained redemption decisions.

## Overview

This repository implements a methodological framework for reconstructing historical lot usage, diagnosing future payment coverage, and supporting intertemporal redemption decisions under financial and liquidity constraints.

The project is built around the idea that each financial lot must be tracked individually, both economically and operationally, in order to support auditable decisions involving:

- paid and future expenses,
- received and invested lots,
- portfolio products with different liquidity profiles,
- future redemption pressure,
- preservation of terminal value.

## Current Project Stage

The repository is currently in an **incremental methodological phase**.

At this stage, the project already includes:

- workbook loading and minimal configuration,
- schema normalization,
- historical reconstruction of paid expenses and consumed lots,
- initialization of the prospective financial state,
- pricing of invested lots under simplified market assumptions,
- diagnosis of future payment coverage,
- candidate redemption selection,
- an intertemporal redemption policy with future-preservation logic.

The following components are intentionally postponed to later phases:

- switching policy,
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

- `config_loader.py`
- `carregamento.py`
- `normalizacao.py`
- `reconstrucao_historica.py`
- `motor_precificacao.py`
- `diagnostico_futuro.py`
- `motor_resgates.py`

## Repository Structure

See the `src/`, `scripts/`, `docs/`, and `config/` folders for implementation and documentation details.

## Input Data

The current implementation expects an Excel workbook with three main sheets:

- `Todos os Gastos`
- `Inventário de Lotes`
- `Carteira`

These sheets are normalized internally into model-ready structures.

## Methodological Notes

This repository currently prioritizes:

- traceability by financial lot,
- explicit historical reconstruction,
- separation between historical and prospective states,
- auditable decision logic,
- incremental implementation.

## How to Run

1. Place the workbook in the expected local path.
2. Adjust `config/config_minimo_v1.json` if needed.
3. Run the inspection and diagnostic scripts from `scripts/`.

## Current Limitations

This is not yet a full global optimizer.

At the current stage, the project still uses simplified assumptions for:

- taxation in some historical replay situations,
- cost modeling for certain financial products,
- combo product handling,
- switching decisions,
- fully integrated long-horizon optimization.

## Roadmap

- harden historical financial reconciliation,
- refine intertemporal redemption policy,
- add switching candidate generation,
- compare redemption vs switching,
- implement joint decision policy,
- expand auditing and reporting.

## License

MIT
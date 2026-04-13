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
- an intertemporal redemption policy,
- switching contracts and invariants,
- switching candidate generation on critical dates,
- switching-versus-redemption comparison on critical dates,
- the hardened joint redemption + switching policy (**v2 official baseline**).

The following components are intentionally postponed to later phases:

- switching bundles/conjuntos,
- stronger global intertemporal optimization,
- portfolio-level search beyond the current heuristic layer,
- full production export pipeline.

## Official Baseline

The **official project baseline** is now the **v2 hardened joint policy**:

- policy name: `intertemporal_com_switching_previo_e_reavaliacao_do_horizonte`
- objective criterion: **maximize terminal wealth under full payment coverage**
- status: **official baseline for future development**

The later **v5 global refinement** remains documented as an **experimental methodological branch**. It improved policy discipline, timing, and partial-switch sizing, but it did **not** outperform v2 on terminal wealth in the real workbook replay. Therefore, future development should start from **v2**, while selectively reusing useful ideas from v5 when they improve v2 without reducing the main economic objective.

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
- `src/comparacao_switching_resgates.py`
- `src/politica_conjunta_switching.py`

Scripts currently included:

- `scripts/inspecionar_estado_inicial.py`
- `scripts/diagnosticar_pagamentos_futuros.py`
- `scripts/selecionar_resgates_candidatos.py`
- `scripts/avaliar_politica_resgates_intertemporal.py`
- `scripts/gerar_candidatos_switching.py`
- `scripts/comparar_switching_vs_resgates.py`
- `scripts/avaliar_politica_conjunta_switching.py`

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
- `docs/baselines.md`


## Baseline Validation

All future refinements must be compared against the **official v2 baseline** before entering the official line.

The repository now includes:

- `config/baseline_v2_oficial.json`
- `src/baseline_guardrails.py`
- `scripts/validar_refinamento_contra_baseline_v2.py`
- `docs/baseline_validation.md`

A refinement is only allowed into the official line if it preserves full payment coverage and does not reduce terminal wealth relative to the official v2 baseline.

## Roadmap

- preserve **v2** as the official baseline for all next development steps,
- selectively reincorporate only the useful ideas from v5 when they improve v2,
- strengthen the global intertemporal policy on top of v2,
- decide whether switching bundles/conjuntos are still justified after that,
- expand auditing and reporting.

## License

MIT


## Hardened Intertemporal Evaluation

The joint redemption + switching policy now validates candidate switching actions by replaying the remaining horizon after the current critical date. In this phase, the policy evaluates the strongest switching candidate per critical date to keep the intertemporal replay computationally tractable while preserving lot-level auditability.


- Switching now includes a programmatic structural-dominance check on the origin portfolio, replacing any fixed lot-level blocking.


## Workbook operacional principal

O repositório inclui um gerador programático do workbook operacional principal da baseline v2.

Arquivos principais:
- `src/exportacao_workbook_operacional_principal.py`
- `scripts/gerar_workbook_operacional_principal_v2.py`

Saída esperada:
- `outputs/workbook_operacional_principal_v2.xlsx`

Esse workbook foi reconstruído para ficar mais enxuto e orientado à validação prática, incluindo:
- histórico de pagamentos realizados
- recebidos/lotes e aportes em carteira
- plano futuro de pagamentos
- switchings propostos
- switchings agrupados
- justificativa resumida de switching
- carteira final operacional
- conferência geral


## Execução do workbook operacional principal

Com os exemplos do repositório:
```bash
python scripts/gerar_workbook_operacional_principal_v2.py
```

Com caminhos explícitos:
```bash
python scripts/gerar_workbook_operacional_principal_v2.py \
  --raw examples/dados_financeiros.xlsx \
  --reference examples/resultado_economica_cliff_agrupado.xlsx \
  --switchings examples/full_end_to_end_confirmation_v2_switchings.csv \
  --resgates examples/full_end_to_end_confirmation_v2_resgates.csv \
  --timeline examples/full_end_to_end_confirmation_v2_timeline.csv \
  --output outputs/workbook_operacional_principal_v2.xlsx
```


### Resumo no console
Ao final da execução do gerador principal, o script também imprime um resumo curto no console com:
- quantidade de pagamentos históricos e futuros
- quantidade de datas críticas
- quantidade de switchings e resgates oficiais
- primeira e última data crítica
- riqueza terminal base
- riqueza terminal oficial v2
- ganho total vs base


### Resumo detalhado no console
Além do resumo executivo, o script principal agora imprime:
- tabela de lotes/recebidos em carteira com saldo bruto, saldo líquido, dias corridos e dias úteis
- tabela de switchings oficiais com motivo
- tabela de switchings agrupados para explicar a fragmentação em vários dias


### Console em tabelas menores
As saídas detalhadas do console foram divididas em subtabelas menores para facilitar leitura no Git Bash:
- lotes ativos: identificação e valores
- lotes esgotados: identificação e valores
- switchings por evento: identificação e valores/motivo
- switchings agrupados: identificação e valores/fragmentação


## Classificação operacional dos lotes
O gerador do workbook e o resumo do console usam o **Inventário de Lotes** como fonte primária para:
- `Valor_Original`
- `Data_Aplicacao`
- `Investimento`
- classe do lote

A data de referência é **hoje em Brasília** (`America/Sao_Paulo`).

Classes operacionais:
- `INVESTIDOS_ATUAIS`
- `LIVRES_DISPONIVEIS`
- `LIVRES_FUTUROS`
- `BLOQUEADOS_JA_GASTOS` (`Investimento == "-"`)

A planilha de referência é usada apenas como apoio para saldos reconstruídos.

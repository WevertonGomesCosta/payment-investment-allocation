# Switching Contracts and Invariants

## Scope

This document defines the canonical semantics for **individual switching** before the project introduces a joint liquidity policy.

## Supported operation types

- `INDIVIDUAL_TOTAL`
- `INDIVIDUAL_PARCIAL`

## Origin eligibility

A lot can originate a switching contract only if:

- `status_lote == INVESTIDO_ATUAL`
- `flag_pode_switchar == True`
- `valor_liquido_resgatavel_centavos > 0`
- `data_switching >= data_elegivel_switching`
- the origin portfolio can be traced by `id_carteira_atual`

## Destination eligibility

A destination product is valid only if:

- `flag_ativa == True`
- destination is different from origin
- transferred value is positive
- transferred value respects minimum and maximum application constraints
- destination is not `Somente_Combo`
- destination product type is not `Combo` in this phase

## Financial invariants

Any switching contract must preserve:

- no artificial creation of value
- no duplicated lot ownership
- explicit origin and destination identifiers
- explicit transfer date
- auditable transferred value

Operationally, the contract is interpreted as:

`origin liquid value = transferred value + explicit losses/costs + residual origin value`

## Lineage invariants

The minimum lineage fields are:

- `id_lote_origem`
- `id_carteira_origem`
- `id_carteira_destino`
- `data_switching`
- `tipo_switching`
- `valor_liquido_transferido_centavos`
- `id_lote_destino_previsto`

## Economic comparison

The current contract layer supports a minimum comparison across three actions:

- keep
- redeem
- switch

The comparison is based on terminal value under the current simplified pricing assumptions.

## Out of scope

This document does not yet define:

- switching bundles/conjuntos
- combo-aware switching destination logic
- global optimization
- full joint switching + redemption policy


## Additional invariant: remaining-bonus dominance

Code: `SW_ORIGEM_BONUS_REMANESCENTE_DOMINANTE`

If the origin still has remaining bonus days and the origin dominates the destination over that comparable remaining-bonus window, switching must be blocked.

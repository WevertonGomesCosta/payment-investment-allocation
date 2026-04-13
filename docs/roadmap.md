# Roadmap

## Official baseline

- **Baseline oficial congelada:** `v2`
- política: `intertemporal_com_switching_previo_e_reavaliacao_do_horizonte`
- critério principal: **maximizar riqueza terminal com cobertura total dos pagamentos**

## Experimental branch retained for reference

- `v5` remains as an experimental methodological branch
- it improved timing discipline and dominant-lot preservation
- it did not beat `v2` on terminal wealth in the real workbook replay
- useful ideas from `v5` may be reincorporated later only if they improve `v2`

## Next development stage opened on top of v2

### Stage A - strengthen the global intertemporal policy

- start every new experiment from the **v2** baseline
- improve timing and partial-switch sizing only when the change improves terminal wealth relative to v2
- preserve lot-level lineage and payment feasibility as hard constraints
- keep `top_k_switch_por_data = 1` as default unless evidence changes

### Stage B - reassess whether switching bundles are still needed

- revisit switching conjunto only after stronger global-policy experiments on top of v2
- require evidence of material expected gain before opening that front

### Stage C - expand global allocation logic

- evaluate richer intertemporal joint optimization only after v2-based policy refinements stabilize

## Earlier completed phases

### Phase 1 - Methodological base

- minimal config loader
- workbook loading
- normalization
- historical reconstruction
- pricing engine
- future payment diagnosis
- redemption candidate policy

### Phase 2 - Switching layer

- canonical switching contracts and invariants
- switching candidate generation on critical dates
- redemption versus switching comparison on real critical dates

### Phase 3 - Joint decision policy

- switching-aware intertemporal policy
- hardened horizon replay after critical dates
- official baseline decision: **v2 kept, v5 archived as experimental**

## Baseline governance now in force

Before any future refinement becomes official, it must pass the baseline guardrails against v2:

- same horizon
- full payment coverage
- terminal wealth not below the official baseline


- Completed: full end-to-end confirmation against the official v2 baseline with the programmatic origin-dominance rule enabled.

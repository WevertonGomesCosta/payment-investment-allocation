# Baselines

## Official baseline

### v2

- status: **official baseline**
- policy: `intertemporal_com_switching_previo_e_reavaliacao_do_horizonte`
- reason: highest terminal wealth among the validated joint-policy variants on the real workbook replay
- use: all new development should branch conceptually from this version

## Experimental methodological branch

### v5

- status: experimental / analytical branch
- policy: `intertemporal_global_com_switching_previo_timing_e_fracionamento`
- contribution: stronger timing discipline, dynamic reserve logic, and dominant-lot preservation ideas
- limitation: underperformed v2 on terminal wealth in the real workbook replay
- use: source of ideas for later selective reincorporation, not the active baseline

## Decision rule going forward

Any new policy refinement should be accepted into the official line only if it improves the v2 baseline on the main project criterion:

- full payment coverage remains feasible
- terminal wealth is not reduced
- lot-level auditability is preserved

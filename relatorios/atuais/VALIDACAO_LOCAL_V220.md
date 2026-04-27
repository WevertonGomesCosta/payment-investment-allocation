# VALIDAÇÃO LOCAL — V220

## Validação inicial aplicada sobre os CSVs reais da V217

```text
delta_patrimonio_terminal_proxy: -211.93
delta_perda_terminal_total: 211.93
delta_penalidade_estrategica_total: 3810.19
delta_deficit_total: 0.00
status_gate_economico_v220: BLOQUEADO_GATE_ECONOMICO_V220
cenario_final_v220: sem_aportes_planejados
lotes_classificados: 8
```

A validação inicial usa os CSVs reais V217 porque são o insumo que demonstrou a piora econômica do cenário com aporte.

Comando reprodutível:

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
```

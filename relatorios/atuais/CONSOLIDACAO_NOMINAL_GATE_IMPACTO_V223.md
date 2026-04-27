# CONSOLIDAÇÃO NOMINAL DO IMPACTO E GATE ECONÔMICO — V223

## Status

`V223_CANDIDATA_DIAGNOSTICA_PRE_BASELINE`

A V223 usa a V222 como candidata diagnóstica validada e consolida os nomes operacionais dos scripts sem quebrar compatibilidade com os nomes históricos.

## Scripts canônicos

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v223.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v223.py --real
python scripts/diagnostico/auditoria_final_pre_baseline_v223.py
```

## Compatibilidade preservada

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
python scripts/diagnostico/auditar_gate_economico_aportes_v220.py --real
```

## Correção de higiene

A geração de CSVs de alertas vazios passa a preservar cabeçalho, especialmente para:

```text
impacto_contas_futuras_v223_alertas_real.csv
```

## Regra econômica preservada

A V223 não altera a regra econômica da V220/V222.

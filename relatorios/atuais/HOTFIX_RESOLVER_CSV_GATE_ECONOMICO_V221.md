# HOTFIX V221 — RESOLVER DE CSVs DO GATE ECONÔMICO

## Status
`V221_CANDIDATA_DIAGNOSTICA_NAO_PROMOVIDA`

## Problema
Na V220, o comando histórico:

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
```

gerou CSVs com prefixo da versão corrente:

```text
impacto_contas_futuras_v220_*.csv
```

mas o gate econômico ainda procurava `impacto_contas_futuras_v217_*.csv`.

## Correção
`auditar_gate_economico_aportes_v220.py` agora procura os CSVs nesta ordem:

```text
impacto_contas_futuras_{VERSAO_BASELINE}_*.csv
impacto_contas_futuras_v220_*.csv
impacto_contas_futuras_v217_*.csv
```

## Escopo negativo
Não altera regra econômica, cálculo de dias, idade fiscal nem motor principal.

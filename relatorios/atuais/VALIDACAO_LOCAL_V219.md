# VALIDAÇÃO LOCAL — V219

## Status

`V219_CANDIDATA_DIAGNOSTICA_NAO_PROMOVIDA`

## Comandos executados

```bash
python scripts/diagnostico/auditar_calculo_dias_lotes_v219.py
python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado observado — auditoria V219

```text
CSV: saidas/diagnostico/auditoria_calculo_dias_lotes_v219_real.csv
CSV: saidas/diagnostico/auditoria_lote_5680_abr_v219_real.csv
CSV: saidas/diagnostico/auditoria_idade_fiscal_lotes_v219_real.csv
CSV: saidas/diagnostico/auditoria_calculo_dias_duplicacoes_v219.csv
=== AUDITORIA CALCULO DIAS LOTES V219 ===
versao: V219
data_referencia: 2026-04-27
lotes_auditados: 16
lotes_com_idade_fiscal_auditada: 16
lote_5680_abr_linhas: 1
lote_5680_abr_dias_corridos_v219: 13
lote_5680_abr_dias_uteis_v219: 8
lote_5680_abr_dias_recebimento_ate_aplicacao: 8
lote_5680_abr_data_referencia_usada: 2026-04-27
duplicacoes_criticas: 0
status: calculo_dias_e_idade_fiscal_canonico_v219_validado
```

## Resultado observado — release checker

```text
OK - release baseline validado para V219
```

## Observação de ambiente

O interpretador emitiu um aviso interno de warmup de spreadsheet runtime em `stderr`, mas os dois comandos retornaram código 0 e os arquivos CSV esperados foram gerados. Esse aviso é externo ao código do projeto.

## Artefatos gerados

- `saidas/diagnostico/auditoria_calculo_dias_lotes_v219_real.csv`
- `saidas/diagnostico/auditoria_lote_5680_abr_v219_real.csv`
- `saidas/diagnostico/auditoria_idade_fiscal_lotes_v219_real.csv`
- `saidas/diagnostico/auditoria_calculo_dias_duplicacoes_v219.csv`

## Decisão

```text
V219_VALIDADA_COMO_CORRECAO_DE_REPRODUTIBILIDADE_E_IDADE_FISCAL
NAO_PROMOVER_BASELINE
```

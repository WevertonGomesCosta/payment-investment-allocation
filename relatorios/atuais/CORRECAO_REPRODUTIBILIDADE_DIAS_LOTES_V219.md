# CORREÇÃO DE REPRODUTIBILIDADE E IDADE FISCAL DOS LOTES — V219

## Status

`V219_CANDIDATA_DIAGNOSTICA_NAO_PROMOVIDA`

A V219 usa a V218 como candidata diagnóstica e não promove baseline. O objetivo é tornar a correção de dias dos lotes reprodutível e remover a duplicação fiscal local no alocador.

## Alterações

1. Mantém `nucleo.calendario_financeiro.calcular_dias_lote(...)` como fonte única para os campos visuais:
   - `Dias corridos`;
   - `Dias úteis`.

2. Adiciona o módulo fiscal central:

```text
nucleo/fiscal_lotes.py
```

com:

```text
calcular_idade_fiscal_lote(...)
aliquota_ir_regressiva_renda_fixa(...)
calcular_aliquota_ir_lote(...)
```

3. Substitui o cálculo local no alocador:

```text
data_pagamento/data_aplicacao + date.today()
```

por:

```text
calcular_idade_fiscal_lote(data_aplicacao, data_pagamento)
aliquota_ir_regressiva_renda_fixa(dias)
```

4. Adiciona auditoria reprodutível:

```bash
python scripts/diagnostico/auditar_calculo_dias_lotes_v219.py
```

## Regra preservada

```text
Dias corridos/Dias úteis visuais ≠ idade fiscal
```

- Campos visuais continuam centralizados em `calcular_dias_lote(...)`.
- Idade fiscal fica centralizada em `fiscal_lotes.py`.

## Decisão

A V219 corrige higiene/reprodutibilidade e centralização fiscal, mas ainda não deve ser promovida como baseline. A próxima etapa deve retomar o gate econômico dos aportes planejados usando os dias e a idade fiscal corrigidos.

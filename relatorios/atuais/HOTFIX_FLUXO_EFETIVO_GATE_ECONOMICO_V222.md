# HOTFIX V222 — FLUXO EFETIVO DO GATE ECONÔMICO

## Status

`V222_CANDIDATA_DIAGNOSTICA_NAO_PROMOVIDA`

## Problema

A V221 adicionou o resolver de CSVs, mas ele ficou fora do fluxo efetivo do script. O `main()` ainda montava caminhos rígidos para:

```text
impacto_contas_futuras_v217_*.csv
```

Por isso, mesmo após gerar:

```text
impacto_contas_futuras_v221_*.csv
```

o gate ainda retornava mensagem de CSV ausente.

## Correção

A V222 substitui o fluxo de leitura do gate por:

```text
_carregar_csvs_impacto()
→ _resolver_csv_impacto("resumo")
→ _resolver_csv_impacto("comparativo_pagamentos")
→ _resolver_csv_impacto("lotes_planejados")
```

A ordem de busca agora é:

```text
impacto_contas_futuras_{VERSAO_BASELINE}_*.csv
impacto_contas_futuras_v222_*.csv
impacto_contas_futuras_v221_*.csv
impacto_contas_futuras_v220_*.csv
impacto_contas_futuras_v217_*.csv
```

## Escopo negativo

- Não altera a regra econômica.
- Não altera cálculo de dias.
- Não altera idade fiscal.
- Não promove baseline.

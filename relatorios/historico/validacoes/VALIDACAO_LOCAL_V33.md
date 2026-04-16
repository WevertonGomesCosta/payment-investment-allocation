# VALIDACAO LOCAL V33

Validação local executada com sucesso na derivação V33.

## Comandos executados

- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`

## Evidências principais

- limiar operacional de resolução fixado em `R$ 0,20` no config;
- resíduos `<= R$ 0,20` passaram a ser classificados como `resolvido por limiar`;
- nova organização da auditoria:
  - tabela de itens resolvidos por limiar;
  - tabela de itens pendentes `> limiar` com `data`, `conta` e `lote`;
  - tabela causal detalhada apenas dos pendentes.

## Resultado da classificação dos resíduos

- `2` resíduos resolvidos por limiar:
  - `Lote 7800 abr.` → `R$ 0,09`
  - `Lote 2063,11 fev.` → `R$ 0,04`
- `5` resíduos pendentes para validação:
  - `despesa_auto_00037` → `R$ 0,71`
  - `despesa_auto_00014` → `R$ 0,68`
  - `Lote 3600 abr.` → `R$ 3,19`
  - `Lote 4000 fev.` → `R$ 0,49`
  - `Lote 4124,75 fev.` → `R$ 0,38`

## Deltas críticos vs. app em 15/04/2026

- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
- `Lote 8500 mar.`: bruto `-0,08`, líquido `-0,06`

## Observação metodológica

Nesta derivação o limiar de `R$ 0,20` foi usado para resolução operacional da auditoria residual. Os casos acima desse limiar permanecem preservados para validação manual antes de qualquer regra corretiva adicional.

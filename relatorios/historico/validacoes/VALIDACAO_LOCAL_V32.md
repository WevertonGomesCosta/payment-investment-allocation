# VALIDACAO LOCAL V32

Validação local executada com sucesso na derivação V32.

## Comandos executados

- `python -m compileall aplicacao nucleo`
- `python scripts/inspecionar_base.py`
- `python aplicacao/principal.py`

## Evidências principais

- `data_referencia_simulacao` fixada em `2026-04-15` no config para manter a execução alinhada à auditoria dos apps;
- nova seção no console: `AUDITORIA DETALHADA DOS RESÍDUOS DE SAQUE/ARREDONDAMENTO`;
- classificação causal dos 7 resíduos remanescentes:
  - 2 casos de `teto líquido do lote no esgotamento`;
  - 2 casos de `remanescente por rendimento histórico`;
  - 2 casos de `saldo residual após saque líquido-alvo`;
  - 1 caso de `micro-saldo centesimal pós-saques`.

## Deltas críticos vs. app em 15/04/2026

- `Lote 6630,64 fev.`: bruto `+0,11`, líquido `+0,21`
- `Lote 3000 mar. V`: bruto `-0,02`, líquido `-0,01`
- `Lote 3000 mar. B`: bruto `-0,08`, líquido `-0,06`
- `Lote 8500 mar.`: bruto `-0,08`, líquido `-0,06`

## Observação metodológica

Nesta derivação não foi aplicada nenhuma regra de zeramento por materialidade. O objetivo foi apenas rastrear a origem dos resíduos antes de qualquer decisão corretiva.

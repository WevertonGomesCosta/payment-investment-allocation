# VALIDAÇÃO LOCAL V47

## Execução realizada
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

## Resultado
A baseline executou sem erro após a substituição do `cache_bcb.json`.

## Auditoria do cache
- `data_atualizacao`: `2026-04-16`
- `meta.data_final`: `2026-04-16`
- última data com fator disponível no mapa: `2026-04-15`
- `taxa_projecao`: `0.0`
- mudança de fator observada a partir de `2026-03-19`: de `1.00055131` para `1.00054266`

## Situação atual dos lotes ativos validada
- `Lote 6630,64 fev.`: bruto `2854.13`, líquido `2835.21`, saldo rem. `2770.06`
- `Lote 3000 mar. V`: bruto `3119.00`, líquido `3092.22`, saldo rem. `3000.00`
- `Lote 3000 mar. B`: bruto `3115.05`, líquido `3089.16`, saldo rem. `3000.00`
- `Lote 8500 mar.`: bruto `8725.69`, líquido `8694.49`, saldo rem. `8587.00`
- `Lote 5680 abr.`: bruto `4760.73`, líquido `4753.41`, saldo rem. `4752.99`

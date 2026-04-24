# Auditoria da chave experimental com tau em 2026-05-04

Baseline: V148
Versão experimental: V149

## Contrato experimental
Mantém os 7 primeiros critérios canônicos intactos e, no empate, compara patrimônio_terminal_proxy - tau * custo_operacional.

## Base
- Patrimônio terminal proxy do `pay_only`: **R$ 25.456,76**
- Custo operacional do `pay_only`: **9.0**

## Regra atual
- Vencedor: **pay_only** | rotulo `` | fontes — | patrimônio **R$ 25.456,76** | custo operacional **9.0**

## Tau = 9,5
- Vencedor: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | fontes Lote 7000 mai., Lote 3000 mar. V | patrimônio **R$ 25.499,07** | custo operacional **11.0**
- Quantidade de switching promovidos vs base: **33**
- Melhor 3k-only promovido: `Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)` | fontes Lote 3000 mar. V | delta patrimônio **R$ 10,58** | delta custo operacional **1.0** | ganho/op **10.580000**
- Caso `Lote 7000 mai. -> MP 120%` promovido: sim | delta patrimônio **R$ 23,87** | delta custo operacional **1.0** | ganho/op **23.870000**

## Tau = 10,0
- Vencedor: **switch_then_pay** | rotulo `Lote 7000 mai. + Lote 3000 mar. V -> CDB XP 150%` | fontes Lote 7000 mai., Lote 3000 mar. V | patrimônio **R$ 25.499,07** | custo operacional **11.0**
- Quantidade de switching promovidos vs base: **28**
- Melhor 3k-only promovido: `Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)` | fontes Lote 3000 mar. V | delta patrimônio **R$ 10,58** | delta custo operacional **1.0** | ganho/op **10.580000**
- Caso `Lote 7000 mai. -> MP 120%` promovido: sim | delta patrimônio **R$ 23,87** | delta custo operacional **1.0** | ganho/op **23.870000**

# FLUXO PAGAMENTOS TERMINAL RECORTE CURTO V138

- Objetivo: integrar o `alocador_pagamentos_terminal_v1` ao fluxo oficial de um recorte curto real de pagamentos e validar, em dados do projeto, quando ele escolhe saldo disponível, lote não aportado, lote aportado ou cenário com switching elegível.

## Resumo do recorte

- intervalo: `2026-04-21` → `2026-05-21`
- pagamentos avaliados: **13**
- dias com pagamento: **9**
- pagamentos com switching elegível promovível disponível: **3**
- pagamentos que efetivamente escolheram switching: **2**
- pagamentos cobertos integralmente: **13**
- déficit total do recorte: **R$ 0.00**

## Contagem por fonte escolhida

- `cenario_switching_elegivel`: **2**
- `combinacao_minima_fontes`: **5**
- `lote_aportado`: **6**

## Leitura técnica

- O fluxo já está usando o alocador em dados reais do projeto, comparando fontes contratuais de pagamento e cenário com switching elegível filtrado pelo comparador híbrido.
- Esta validação ainda é de recorte curto e integração funcional; ela não fecha o modelo final de pagamentos, mas já mostra quais fontes dominam no estado real da baseline.

## Exemplos auditados

- `2026-04-29` | `despesa_auto_00069` | `lote_aportado` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-04` | `despesa_auto_00070` | `combinacao_minima_fontes` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-06` | `despesa_auto_00072` | `cenario_switching_elegivel` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-06` | `despesa_auto_00071` | `cenario_switching_elegivel` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-08` | `despesa_auto_00073` | `combinacao_minima_fontes` | cobertura `True` | déficit `R$ 0.00`
- `2026-05-10` | `despesa_auto_00074` | `combinacao_minima_fontes` | cobertura `True` | déficit `R$ 0.00`

## Pagamentos com switching promovível disponível

- `2026-05-04` | `despesa_auto_00070` | cenário `Lote 7000 mai. -> Mercado Pago Cofrinho 120% CDI (Meli+)` | fonte escolhida `combinacao_minima_fontes` | aplicado `False`
- `2026-05-06` | `despesa_auto_00072` | cenário `Lote 5680 mai. + Lote 7000 mai. + Lote 3600 mai. -> Combo PicPay 100-120 3m` | fonte escolhida `cenario_switching_elegivel` | aplicado `True`
- `2026-05-06` | `despesa_auto_00071` | cenário `Lote 5680 mai._ap_2026-05-06 + Lote 7000 mai._ap_2026-05-06 + Lote 3600 mai._ap_2026-05-06 -> CDB XP 150%` | fonte escolhida `cenario_switching_elegivel` | aplicado `True`

## Pagamentos que efetivamente acionaram switching

- `2026-05-06` | `despesa_auto_00072` | `Lote 5680 mai. + Lote 7000 mai. + Lote 3600 mai. -> Combo PicPay 100-120 3m`
- `2026-05-06` | `despesa_auto_00071` | `Lote 5680 mai._ap_2026-05-06 + Lote 7000 mai._ap_2026-05-06 + Lote 3600 mai._ap_2026-05-06 -> CDB XP 150%`

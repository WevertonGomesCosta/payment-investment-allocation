# FLUXO PAGAMENTOS TERMINAL RECORTE AMPLO V142

- Objetivo: expandir a integração do `alocador_pagamentos_terminal_v1` para um recorte real maior de pagamentos e medir, em fluxo completo, como H1–H3 alteram as escolhas entre `lote_aportado`, `lote_nao_aportado`, `combinacao_minima_fontes` e `cenario_switching_elegivel`.
- Baseline de origem: `V141`.
- Observação operacional: a auditoria comparativa V142 usou teto controlado de candidatos de switching por data para manter o recorte maior executável sem alterar o contrato central do alocador.

## Resumo do recorte

- intervalo: `2026-04-21` → `2026-06-10`
- pagamentos avaliados: **20**
- dias com pagamento: **13**

## Fluxo com H1–H3 ativas

- patrimônio líquido terminal proxy: **R$ 29933.35**
- perda terminal agregada: **R$ 0.00**
- custo fiscal imediato total: **R$ 65.79**
- custo operacional total: **20.00**
- switching efetivamente escolhido: **7** pagamentos

## Fluxo com H1–H3 neutralizadas

- patrimônio líquido terminal proxy: **R$ 29933.35**
- perda terminal agregada: **R$ 0.00**
- custo fiscal imediato total: **R$ 76.57**
- custo operacional total: **23.00**
- switching efetivamente escolhido: **7** pagamentos

## Efeito agregado de H1–H3 no fluxo completo

- Δ patrimônio líquido terminal proxy: **R$ 0.00**
- Δ perda terminal agregada: **R$ 0.00**
- Δ custo fiscal imediato: **R$ -10.78**
- Δ custo operacional: **-3.00**
- Δ pagamentos que escolheram switching: **0**
- pagamentos com tipo/fonte alterados no fluxo: **6**

## Contagem das escolhas foco com H1–H3 ativas

- `cenario_switching_elegivel`: **7**
- `combinacao_minima_fontes`: **9**
- `lote_aportado`: **4**

## Casos alterados no fluxo completo

- `2026-05-06` | `despesa_auto_00071` | `cenario_switching_elegivel -> cenario_switching_elegivel` | sem H1–H3: `cenario_switching_elegivel` | com H1–H3: `cenario_switching_elegivel`
- `2026-05-08` | `despesa_auto_00073` | `cenario_switching_elegivel -> cenario_switching_elegivel` | sem H1–H3: `cenario_switching_elegivel` | com H1–H3: `cenario_switching_elegivel`
- `2026-05-11` | `despesa_auto_00075` | `combinacao_minima_fontes -> lote_aportado` | sem H1–H3: `combinacao_minima_fontes` | com H1–H3: `lote_aportado`
- `2026-05-12` | `despesa_auto_00076` | `combinacao_minima_fontes -> lote_aportado` | sem H1–H3: `combinacao_minima_fontes` | com H1–H3: `lote_aportado`
- `2026-06-10` | `despesa_auto_00086` | `combinacao_minima_fontes -> lote_aportado` | sem H1–H3: `combinacao_minima_fontes` | com H1–H3: `lote_aportado`
- `2026-06-10` | `despesa_auto_00087` | `combinacao_minima_fontes -> lote_aportado` | sem H1–H3: `combinacao_minima_fontes` | com H1–H3: `lote_aportado`

## Leitura técnica

- A comparação foi feita em fluxo completo com e sem H1–H3 no mesmo recorte real.
- O foco permaneceu em patrimônio líquido terminal proxy, sem substituir a métrica terminal principal por score auxiliar.
- Nesta rodada, o ganho relevante é observar se H1–H3 mudam a trajetória de fonte escolhida e se isso altera patrimônio terminal, custo fiscal e uso de switching em sequência real de pagamentos.

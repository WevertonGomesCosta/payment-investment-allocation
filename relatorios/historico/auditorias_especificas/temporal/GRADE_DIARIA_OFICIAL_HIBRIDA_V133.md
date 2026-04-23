# Grade diária oficial com comparador híbrido — V133

- Objetivo: integrar o `comparador_hibrido_switching_v1` ao fluxo oficial da grade diária, para que o melhor cenário do dia seja emitido como `vencedor terminal`, `vencedor híbrido aceitável` ou `baseline`, sem promoção automática de `vencedor operacional`.

- Dias auditados: 21
- Resultados avaliados: 382
- Dias com vencedor lexicográfico bloqueado: 21
- Dias promovidos com switching: 5
- Dias promovidos com baseline: 16
- Dias em que a promoção oficial diferiu do vencedor lexicográfico: 5

## Contagem das classes oficiais promovidas

- vencedor_terminal: 5

## Melhor cenário oficial por dia

| Data | Vencedor lexicográfico | Classe lex | Bloqueado | Melhor cenário oficial | Classe oficial | Origem | Δ perda terminal | Δ déficit | Δ patrimônio proxy |
|---|---|---|---|---|---|---|---:|---:|---:|
| 2026-04-30 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -234.56 | -450.12 | 2167.56 |
| 2026-05-01 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -228.79 | -450.12 | 2156.02 |
| 2026-05-02 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -223.02 | -450.12 | 2144.48 |
| 2026-05-03 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -217.25 | -450.12 | 2132.94 |
| 2026-05-04 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -211.48 | -450.12 | 2121.40 |
| 2026-05-05 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-06 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-07 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-08 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-09 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-10 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-11 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-12 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-13 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-14 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-15 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-16 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-17 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-18 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-19 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-20 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |

## Leitura técnica

- O vencedor lexicográfico continua sendo registrado para auditoria, mas não define mais a promoção oficial do dia quando cai como `vencedor_operacional`.
- Se existir cenário `vencedor_terminal` ou `vencedor_hibrido_aceitavel`, ele passa a ser o melhor cenário oficial do dia.
- Se não existir cenário promovível, o consolidado oficial passa a emitir explicitamente `baseline_sem_switching` como melhor cenário do dia.


# Avaliação diária parametrizada da janela crítica — V130

- Objetivo: rerodar a janela `2026-04-30` a `2026-05-20` com parâmetros de produto corrigidos, eliminando falsos positivos de ticket mínimo e máximo.
- Dias auditados: 21.
- Cenários parametrizados simulados: 382.
- Cenários vencedores no cenário conjunto: 211.

## Conclusões centrais

- O bug do `CDB XP 150%` abaixo de R$ 10 mil deixa de contaminar a janela: os cenários individuais e agrupados abaixo do mínimo não entram mais na simulação.
- O `CDB XP 150%` continua aparecendo apenas quando o agrupamento realmente ultrapassa o ticket mínimo do produto.
- A janela vencedora permanece viva após a correção de parâmetros, mas sua composição muda: o curto prazo passa a favorecer mais `Mercado Pago Cofrinho 120% CDI (Meli+)`, `CDB BMG Escalonado - até 109% CDI - 5 anos`, `CDB Sofisa 105%` e os combos PicPay do que o Tesouro como destino dominante.

## Resumo por dia

| Data | Ações elegíveis do planejador | Cenários parametrizados |
|---|---:|---:|
| 2026-04-30 | 25 | 38 |
| 2026-05-01 | 25 | 38 |
| 2026-05-02 | 25 | 38 |
| 2026-05-03 | 25 | 38 |
| 2026-05-04 | 25 | 38 |
| 2026-05-05 | 25 | 39 |
| 2026-05-06 | 25 | 39 |
| 2026-05-07 | 15 | 15 |
| 2026-05-08 | 15 | 15 |
| 2026-05-09 | 15 | 15 |
| 2026-05-10 | 15 | 15 |
| 2026-05-11 | 15 | 15 |
| 2026-05-12 | 15 | 15 |
| 2026-05-13 | 5 | 3 |
| 2026-05-14 | 5 | 3 |
| 2026-05-15 | 5 | 3 |
| 2026-05-16 | 5 | 3 |
| 2026-05-17 | 5 | 3 |
| 2026-05-18 | 5 | 3 |
| 2026-05-19 | 5 | 3 |
| 2026-05-20 | 5 | 3 |

## Melhor cenário vencedor por dia

| Data | Família | Cenário | Destino | Valor total alocado | Δ déficit | Δ patrimônio proxy |
|---|---|---|---|---:|---:|---:|
| 2026-04-30 | individual_integral_parametrizado | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 948.52 |
| 2026-05-01 | individual_integral_parametrizado | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 942.34 |
| 2026-05-02 | individual_integral_parametrizado | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 936.16 |
| 2026-05-03 | individual_integral_parametrizado | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 929.98 |
| 2026-05-04 | individual_integral_parametrizado | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 923.82 |
| 2026-05-05 | agrupado_integral_parametrizado | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 4111.79 | -1972.07 | 1166.68 |
| 2026-05-06 | agrupado_integral_parametrizado | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 4111.79 | -1972.07 | 1156.70 |
| 2026-05-13 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3658.54 | -2353.40 |
| 2026-05-14 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3658.54 | -2353.40 |
| 2026-05-15 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3658.54 | -2353.40 |
| 2026-05-16 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3923.34 | -2531.69 |
| 2026-05-17 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3923.34 | -2531.69 |
| 2026-05-18 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3923.34 | -2531.69 |
| 2026-05-19 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3923.34 | -2531.69 |
| 2026-05-20 | individual_integral_parametrizado | Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 5507.13 | -3923.34 | -2531.69 |

## Agrupamentos vencedores únicos

| Cenário agrupado | Destino | 1ª data | Última data | Dias vencedores | Melhor Δ déficit | Melhor Δ patrimônio proxy |
|---|---|---|---|---:|---:|---:|
| Lote 3000 mar. V + Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 2026-04-30 | 2026-05-06 | 7 | -478.64 | 998.13 |
| Lote 3000 mar. V + Lote 8500 mar. -> Combo PicPay 100-120 6m | Combo PicPay 100-120 6m | 2026-04-30 | 2026-05-06 | 7 | -478.64 | 998.13 |
| Lote 3000 mar. V + Lote 8500 mar. -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-04-30 | 2026-05-06 | 7 | -478.64 | 994.68 |
| Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 2230.60 |
| Lote 3000 mar. B + Lote 3000 mar. V -> CDB BMG Escalonado - até 109% CDI - 5 anos | CDB BMG Escalonado - até 109% CDI - 5 anos | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 2197.45 |
| Lote 3000 mar. B + Lote 3000 mar. V -> CDB Sofisa 105% | CDB Sofisa 105% | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 2197.45 |
| Lote 3000 mar. B + Lote 3000 mar. V -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 2072.98 |
| Lote 3000 mar. B + Lote 3000 mar. V -> Combo PicPay 100-120 6m | Combo PicPay 100-120 6m | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 2072.98 |
| Lote 3000 mar. B + Lote 3000 mar. V -> Tesouro Selic 2029 | Tesouro Selic 2029 | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 1997.20 |
| Lote 3000 mar. B + Lote 3000 mar. V -> CDB Neon Cofrinho Escalonado - 100% a 113% CDI | CDB Neon Cofrinho Escalonado - 100% a 113% CDI | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 1397.80 |
| Lote 3000 mar. B + Lote 3000 mar. V -> CDB BMG Super Poupança | CDB BMG Super Poupança | 2026-04-30 | 2026-05-06 | 7 | -1972.07 | 1323.86 |
| Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 115% CDI | Mercado Pago Cofrinho 115% CDI | 2026-05-05 | 2026-05-06 | 2 | -1972.07 | 858.02 |
| Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | CDB XP 150% | 2026-04-30 | 2026-05-04 | 5 | -450.12 | 2167.56 |
| Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 2026-04-30 | 2026-05-06 | 7 | -1950.12 | 2194.75 |
| Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> Combo PicPay 100-120 6m | Combo PicPay 100-120 6m | 2026-04-30 | 2026-05-06 | 7 | -1950.12 | 2194.75 |
| Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-05 | 2026-05-06 | 2 | -1950.12 | 1211.85 |
| Lote 3000 mar. B + Lote 8500 mar. -> Combo PicPay 100-120 3m | Combo PicPay 100-120 3m | 2026-05-05 | 2026-05-06 | 2 | -1449.53 | 907.32 |
| Lote 3000 mar. B + Lote 8500 mar. -> Combo PicPay 100-120 6m | Combo PicPay 100-120 6m | 2026-05-05 | 2026-05-06 | 2 | -1449.53 | 907.32 |
| Lote 3000 mar. B + Lote 8500 mar. -> Mercado Pago Cofrinho 120% CDI (Meli+) | Mercado Pago Cofrinho 120% CDI (Meli+) | 2026-05-05 | 2026-05-06 | 2 | -1449.53 | 914.64 |

## Leitura técnica

- Os cenários só entram na simulação quando passam pela validação de aplicação mínima/máxima do produto de destino.
- Ticket individual inválido deixa de gerar cenário; ticket agrupado só entra quando o valor total combinado atinge o mínimo do produto.
- A leitura correta da janela agora é: vencedores reais da métrica central, já livres dos falsos positivos de ticket mínimo.


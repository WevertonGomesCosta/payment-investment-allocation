# Comparador híbrido de switching — V132

## Objetivo

Classificar cada cenário diário como `vencedor operacional`, `vencedor terminal`, `vencedor híbrido aceitável` ou `dominado pelo baseline`, bloqueando a promoção automática de switchings que piorem patrimônio líquido terminal frente ao baseline.

## Contagem agregada das classes

- vencedor_operacional: 186
- vencedor_terminal: 25
- vencedor_hibrido_aceitavel: 0
- dominado_pelo_baseline: 171

- cenários bloqueados para promoção automática: 357
- dias em que o vencedor lexicográfico foi bloqueado: 21
- dias com promoção híbrida diferente do vencedor lexicográfico: 5

## Leitura principal

- `vencedor_operacional`: melhora a métrica central atual, mas piora materialmente o patrimônio terminal frente ao baseline; deve ficar bloqueado para promoção automática.
- `vencedor_terminal`: melhora materialmente o patrimônio terminal sem piora operacional material; é o candidato preferencial para promoção.
- `vencedor_hibrido_aceitavel`: vence ou permanece competitivo sem piora terminal material; é aceitável quando não existir vencedor terminal superior.

## Resumo diário

| Data | Vencedor lexicográfico | Classe | Bloqueado | Promoção híbrida | Classe promoção | Δ perda terminal promoção | Δ déficit promoção | Δ patrimônio promoção |
|---|---|---|---|---|---|---:|---:|---:|
| 2026-04-30 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -234.56 | -450.12 | 2167.56 |
| 2026-05-01 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -228.79 | -450.12 | 2156.02 |
| 2026-05-02 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -223.02 | -450.12 | 2144.48 |
| 2026-05-03 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -217.25 | -450.12 | 2132.94 |
| 2026-05-04 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | -211.48 | -450.12 | 2121.40 |
| 2026-05-05 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-06 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-07 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-08 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-09 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-10 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-11 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-12 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-13 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-14 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-15 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-16 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-17 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-18 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-19 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-20 | Lote 8500 mar. -> Combo PicPay 100-120 3m | vencedor_operacional | Sim | baseline_sem_switching | baseline | 0.00 | 0.00 | 0.00 |

## Caso crítico já conhecido

- O cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` permanece classificado como `vencedor_operacional` no bloco 2026-05-13 a 2026-05-20, portanto fica bloqueado para promoção automática no comparador híbrido.

# Simulação central controlada em horizonte mais longo — V124

- Objetivo: rerodar a simulação central controlada em horizonte mais longo usando o ranking Carteira-only estabilizado como fonte de destinos do `planejador_switching_temporal_v1`.
- Escopo: comparar o baseline sem switching com os melhores candidatos positivos do planejador, um por lote, já no cenário conjunto com pagamentos.
- Fonte de destinos: `contexto_baseline.ranking_carteira.quadro_destinos_switch`.

## Síntese executiva

- Horizonte de **60 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).
- Horizonte de **90 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).
- Horizonte de **120 dias**: melhor cenário = **switching_controlado_top4** (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`).

Achado central: após a correção do ranqueamento, surgem destinos melhores que Tesouro no planejador, mas na simulação central longa apenas o switching do `Lote 6630,64 fev.` para `Mercado Pago Cofrinho 120% CDI (Meli+)` continua vencedor — e ainda assim de forma marginal, sem ganho material sobre o baseline.

## Resultados por horizonte

### Horizonte 60 dias
- Janela: 2026-04-20 → 2026-06-19
- Pagamentos no recorte: 25
- Destinos elegíveis considerados: 12
- Switchings elegíveis no planejador: 26
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Vetor do melhor cenário: `(6.0, 12009.59, 10.0, 874.12, 9876.43, 0.0, 0.0, 4.0)`

#### Candidatos controlados no cenário conjunto
- `Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`
  - continua vencedor central = `True`
  - vitória material = `False`
  - ganho no planejador = `0.01`
  - Δ perda terminal vs baseline = `-0.01`
  - Δ déficit vs baseline = `0.0`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `0.03`
- `Lote 8500 mar. -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `27.28`
  - Δ perda terminal vs baseline = `-25.86`
  - Δ déficit vs baseline = `21.95`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `25.86`
- `Lote 3000 mar. B -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `67.45`
  - Δ perda terminal vs baseline = `-64.70`
  - Δ déficit vs baseline = `28.52`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `254.08`
- `Lote 3000 mar. V -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `66.63`
  - Δ perda terminal vs baseline = `-64.73`
  - Δ déficit vs baseline = `29.41`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `254.24`

### Horizonte 90 dias
- Janela: 2026-04-20 → 2026-07-19
- Pagamentos no recorte: 35
- Destinos elegíveis considerados: 12
- Switchings elegíveis no planejador: 34
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Vetor do melhor cenário: `(12.0, 18423.77, 20.0, 1685.87, 9876.43, 0.0, 0.0, 4.0)`

#### Candidatos controlados no cenário conjunto
- `Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`
  - continua vencedor central = `True`
  - vitória material = `False`
  - ganho no planejador = `0.01`
  - Δ perda terminal vs baseline = `-0.01`
  - Δ déficit vs baseline = `0.0`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `0.04`
- `Lote 8500 mar. -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `52.90`
  - Δ perda terminal vs baseline = `-55.33`
  - Δ déficit vs baseline = `21.95`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `55.33`
- `Lote 3000 mar. B -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `116.60`
  - Δ perda terminal vs baseline = `-65.51`
  - Δ déficit vs baseline = `28.52`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `349.58`
- `Lote 3000 mar. V -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `115.80`
  - Δ perda terminal vs baseline = `-65.55`
  - Δ déficit vs baseline = `29.41`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `349.82`

### Horizonte 120 dias
- Janela: 2026-04-20 → 2026-08-18
- Pagamentos no recorte: 50
- Destinos elegíveis considerados: 12
- Switchings elegíveis no planejador: 35
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Vetor do melhor cenário: `(19.0, 33297.95, 35.0, 2497.59, 9876.43, 0.0, 0.0, 4.0)`

#### Candidatos controlados no cenário conjunto
- `Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`
  - continua vencedor central = `True`
  - vitória material = `False`
  - ganho no planejador = `0.01`
  - Δ perda terminal vs baseline = `-0.01`
  - Δ déficit vs baseline = `0.0`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `0.05`
- `Lote 8500 mar. -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `79.21`
  - Δ perda terminal vs baseline = `-84.80`
  - Δ déficit vs baseline = `21.95`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `84.80`
- `Lote 3000 mar. B -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `166.52`
  - Δ perda terminal vs baseline = `-66.30`
  - Δ déficit vs baseline = `28.52`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `445.06`
- `Lote 3000 mar. V -> CDB XP 150%`
  - continua vencedor central = `False`
  - vitória material = `False`
  - ganho no planejador = `165.77`
  - Δ perda terminal vs baseline = `-66.37`
  - Δ déficit vs baseline = `29.41`
  - Δ violações protegida vs baseline = `0.0`
  - Δ patrimônio proxy vs baseline = `445.40`

## Conclusões

- A correção do ranking mudou o universo de destinos vencedores do planejador: Tesouro deixou de dominar e surgiram `Mercado Pago Cofrinho 120% CDI (Meli+)` e `CDB XP 150%` como principais alternativas.
- Porém, no cenário conjunto, os switchings para `CDB XP 150%` não sobreviveram: embora melhorem a perda terminal local, pioram déficit líquido total e preservação de pagamentos.
- O único switching que continuou vencedor nos três horizontes foi `Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`.
- Mesmo esse caso foi apenas marginal: a diferença contra o baseline ficou em centésimos na perda terminal e no patrimônio proxy, com déficit e violação de `PROTEGIDA` inalterados.
- Portanto, após a correção do ranqueamento, o projeto passa a ter um candidato plausível de switching longo, mas ainda não um conjunto robusto de switchings materialmente superiores ao baseline.

# Auditoria multihorizonte de cenários de tempo — V125

- Objetivo: ampliar a auditoria temporal do cenário conjunto, saindo dos horizontes isolados de 60/90/120 dias e testando uma grade mais rica de janelas.
- Pergunta central: quais switchings continuam vencedores quando a janela temporal muda de forma relevante, e se essa vitória é material ou apenas marginal.
- Fonte de destinos: `contexto_baseline.ranking_carteira.quadro_destinos_switch`.
- Execução desta auditoria: consolidada a partir de **rodadas segmentadas por horizonte**, para evitar ruído operacional de uma execução monolítica muito pesada no ambiente atual.

## Grade temporal auditada

- 30, 45, 60, 75, 90, 120, 150, 180, 210, 240, 270 e 360 dias.

## Síntese executiva

- O único horizonte com vitória **material** de switching foi **30 dias**, com `Lote 3000 mar. V -> CDB XP 150%`.
- Houve vitórias **marginais** em: `60d`, `75d`, `90d`, `120d`, `150d`, `180d`, `210d` e `360d`.
- O baseline sem switching venceu em: `45d`, `240d` e `270d`.

Achado central: o tempo realmente muda o ranking dos cenários, mas não de forma monotônica. O projeto não mostra uma transição simples do tipo “quanto mais horizonte, mais switching”. O que aparece é um regime instável: um ganho material muito curto, uma longa faixa de ganhos marginais/empates técnicos e janelas em que o baseline volta a dominar.

## Resultado por horizonte

### Horizonte 30 dias
- Janela: `2026-04-20 → 2026-05-20`
- Pagamentos no recorte: `13`
- Switchings elegíveis no planejador: `21`
- Melhor cenário central: `switching_controlado_top2` (`Lote 3000 mar. V -> CDB XP 150%`)
- Leitura: **vitória material**
- Δ perda terminal vs baseline: `-64.83`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+130.17`

### Horizonte 45 dias
- Janela: `2026-04-20 → 2026-06-04`
- Pagamentos no recorte: `16`
- Switchings elegíveis no planejador: `21`
- Melhor cenário central: `baseline_sem_switching`
- Leitura: o ganho curto de 30 dias não se sustenta quando entram mais pagamentos.

### Horizonte 60 dias
- Janela: `2026-04-20 → 2026-06-19`
- Pagamentos no recorte: `25`
- Switchings elegíveis no planejador: `26`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.03`

### Horizonte 75 dias
- Janela: `2026-04-20 → 2026-07-04`
- Pagamentos no recorte: `27`
- Switchings elegíveis no planejador: `31`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.04`

### Horizonte 90 dias
- Janela: `2026-04-20 → 2026-07-19`
- Pagamentos no recorte: `35`
- Switchings elegíveis no planejador: `34`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.04`

### Horizonte 120 dias
- Janela: `2026-04-20 → 2026-08-18`
- Pagamentos no recorte: `50`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.05`

### Horizonte 150 dias
- Janela: `2026-04-20 → 2026-09-17`
- Pagamentos no recorte: `63`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> CDB XP 150%`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.06`

### Horizonte 180 dias
- Janela: `2026-04-20 → 2026-10-17`
- Pagamentos no recorte: `78`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.07`

### Horizonte 210 dias
- Janela: `2026-04-20 → 2026-11-16`
- Pagamentos no recorte: `91`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> Mercado Pago Cofrinho 120% CDI (Meli+)`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.02`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.09`

### Horizonte 240 dias
- Janela: `2026-04-20 → 2026-12-16`
- Pagamentos no recorte: `105`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `baseline_sem_switching`
- Leitura: o baseline volta a dominar mesmo após longa janela de diluição do custo fiscal.

### Horizonte 270 dias
- Janela: `2026-04-20 → 2027-01-15`
- Pagamentos no recorte: `116`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `baseline_sem_switching`
- Leitura: reforça que maior horizonte não implica melhor política de switching no cenário conjunto.

### Horizonte 360 dias
- Janela: `2026-04-20 → 2027-04-15`
- Pagamentos no recorte: `149`
- Switchings elegíveis no planejador: `35`
- Melhor cenário central: `switching_controlado_top4` (`Lote 6630,64 fev. -> CDB XP 150%`)
- Leitura: **vitória marginal**
- Δ perda terminal vs baseline: `-0.01`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+0.12`

## Interpretação metodológica

- **30 dias**: surge um ganho material de switching (`Lote 3000 mar. V -> CDB XP 150%`), mas esse ganho é muito sensível ao recorte curto e não se mantém quando a janela incorpora mais pagamentos.
- **45 dias**: o baseline já volta a dominar. Isso mostra que o ganho de 30 dias não é uma regra robusta; ele depende da composição local do bloco de contas.
- **60 a 210 dias**: o único vencedor recorrente é `Lote 6630,64 fev.`, alternando entre `Mercado Pago 120% CDI` e `CDB XP 150%`, mas sempre de forma marginal, com diferença em centésimos e sem melhora de déficit.
- **240 a 270 dias**: o baseline volta a vencer. Isso reforça que o horizonte por si só não garante ganho estrutural de switching.
- **360 dias**: reaparece uma vitória marginal de `Lote 6630,64 fev. -> CDB XP 150%`, ainda sem materialidade suficiente para justificar promoção operacional automática.

## Conclusão operacional

- O tempo precisa entrar como dimensão explícita da análise, mas **não basta aumentar o horizonte** para justificar switching.
- Hoje o repositório mostra três regimes distintos:
  1. **ganho curto e material, porém instável** (30 dias);
  2. **ganho marginal recorrente** (`Lote 6630,64 fev.` em múltiplos horizontes);
  3. **dominância do baseline** em janelas intermediárias e longas específicas (`45d`, `240d`, `270d`).
- Portanto, a próxima evolução correta é construir um avaliador temporal por grade, e não continuar inferindo política final a partir de 3 ou 4 horizontes isolados.

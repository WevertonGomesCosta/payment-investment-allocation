# Auditoria de parâmetros de produtos no switching — V129

- Objetivo: verificar se o switching diário está respeitando parâmetros reais dos produtos de destino, em especial ticket mínimo/máximo, antes de continuar a expansão temporal.
- Escopo desta rodada: auditoria estrutural do bug de elegibilidade e reavaliação focal da janela diária crítica de `2026-04-30` a `2026-05-02` usando os 5 produtos mais bem ranqueados da `Carteira`.

## Achado estrutural principal

O fluxo temporal da V128 **não estava considerando corretamente o ticket mínimo do produto de destino**. O problema tinha duas fontes:

1. parsing monetário inconsistente da coluna `Aplicação_Mínima` da aba `Carteira`;
2. geração de cenários vencedores sem validação final do **valor total efetivamente alocado** contra o ticket do destino.

Isso afetava diretamente o caso do `CDB XP 150%`, que vinha aparecendo como destino vencedor mesmo quando o valor migrado não atingia o mínimo de R$ 10.000,00.

## Top 5 destinos ranqueados auditados

| Rank | Produto | Aplicação mínima | Aplicação máxima | Retorno proxy aa | Liquidez | Carência |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Mercado Pago Cofrinho 120% CDI (Meli+) | 1.00 | 10000.00 | 16.80 | 0 | 0 |
| 2 | CDB BMG Escalonado - até 109% CDI - 5 anos | 50.00 | 0.00 | 14.70 | 0 | 0 |
| 3 | CDB Sofisa 105% | 1.00 | 0.00 | 14.70 | 0 | 0 |
| 4 | Combo PicPay 100-120 3m | 300.00 | 0.00 | 16.80 | 0 | 0 |
| 5 | Combo PicPay 100-120 6m | 300.00 | 0.00 | 16.80 | 0 | 0 |

## Evidência concreta do bug da V128 no `CDB XP 150%`

Data auditada: `2026-04-30`.

| Cenário antigo recorrente | Valor migrado estimado | Mínimo do produto | Ticket válido? |
|---|---:|---:|---|
| Lote 3000 mar. V | 3071.88 | 10000.00 | Não |
| Lote 3000 mar. B + Lote 3000 mar. V | 6141.58 | 10000.00 | Não |
| Lote 3000 mar. V + Lote 8500 mar. | 8579.01 | 10000.00 | Não |
| Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. | 11648.71 | 10000.00 | Sim |

Leitura:
- os cenários individuais e agrupados que vinham puxando a janela vencedora para o `CDB XP 150%` eram, em sua maioria, **inválidos por ticket**;
- apenas o agrupamento `3000 mar. B + 3000 mar. V + 8500 mar.` ultrapassa o mínimo de R$ 10.000,00.

## Reavaliação focal da janela crítica com parâmetros corretos

Foi feita uma reavaliação focal dos cenários **diários** entre `2026-04-30` e `2026-05-02`, restringindo o universo aos **5 destinos mais bem ranqueados** da `Carteira` e exigindo elegibilidade real por ticket.

### Melhores vencedores observados após a correção

| Data | Melhor cenário parametrizado | Destino | Valor total | Δ déficit vs baseline | Δ patrimônio proxy vs baseline |
|---|---|---|---:|---:|---:|
| 2026-04-30 | Lote 3000 mar. V | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 948.52 |
| 2026-05-01 | Lote 3000 mar. V | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 942.34 |
| 2026-05-02 | Lote 3000 mar. V | Mercado Pago Cofrinho 120% CDI (Meli+) | 2542.09 | -500.59 | 936.16 |

Próximos melhores destinos, ainda vencedores, mas abaixo do Mercado Pago 120%:
- `CDB BMG Escalonado - até 109% CDI - 5 anos`;
- `CDB Sofisa 105%`;
- `Combo PicPay 100-120 3m`;
- `Combo PicPay 100-120 6m`.

## Conclusões metodológicas

1. O questionamento sobre parâmetros do produto estava correto: a V128 promovia destinos sem respeitar integralmente o ticket mínimo.
2. O `CDB XP 150%` não pode mais ser tratado como destino automaticamente elegível para os lotes de ~3k e para os agrupamentos que ficam abaixo de R$ 10.000,00.
3. Depois da correção, os destinos top-ranqueados da `Carteira` passam a dominar a janela curta auditada, com destaque para `Mercado Pago Cofrinho 120% CDI (Meli+)`.
4. Isso **não prova ainda** que esses destinos curtos dominarão no horizonte mais longo; prova apenas que, na janela diária crítica em que o XP 150% aparecia, o ranking correto com parâmetros válidos muda a decisão ótima local.
5. O próximo passo correto é absorver essa validação de ticket no fluxo principal da grade diária e só então rerodar a janela vencedora completa `2026-04-30` a `2026-05-20` e, depois, o horizonte longo.

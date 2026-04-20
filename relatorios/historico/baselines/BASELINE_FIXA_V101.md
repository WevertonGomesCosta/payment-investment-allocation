# Baseline fixa V101

## Escopo da V101

A V101 preserva a baseline funcional da V100, mantém a saída operacional do console e do extrato futuro já aprovadas, preserva a auditoria temporal explícita sobre a `decisao_local_v1` e adiciona uma camada de reescolha dinâmica pós-quebra para recomputar a fonte dos pagamentos futuros que deixam de ser coerentes sequencialmente, sem reabrir o solver global.

## O que a V101 altera

- adiciona a camada `reescolha_dinamica_pos_quebra`, separada do motor principal;
- preserva a auditoria temporal da V100 e passa a recomputar a melhor fonte local entre os lotes remanescentes quando a sugestão original quebra na sequência;
- amplia o `Extrato futuro` com colunas dinâmicas finais e adiciona a aba `Reescolha dinâmica`;
- adiciona uma nova seção dedicada no console principal para resumir reescolhas, mudanças efetivas de fonte e falhas remanescentes.

## O que a V101 não altera

- não reabre o solver global;
- não reabre o runner shadow como método governante;
- não altera o método local governante (`decisao_local_v1 + proxy v3`);
- não altera o replay do passado nem a estrutura oficial do fluxo principal.

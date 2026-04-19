# Baseline fixa V102

## Escopo da V102

A V102 preserva a baseline funcional da V101, mantém a saída operacional do console e do extrato futuro já aprovadas, preserva a auditoria temporal e a reescolha dinâmica pós-quebra, e adiciona uma camada de recomputação sequencial preventiva que recalcula a melhor fonte a cada pagamento futuro com saldos residuais atualizados.

## O que a V102 altera

- adiciona a camada `recomputacao_sequencial_preventiva`, separada do motor principal;
- recalcula continuamente a melhor fonte local em vez de só reagir depois da quebra;
- registra trocas preventivas antes da quebra e trocas por inviabilidade da fonte original;
- amplia o `Extrato futuro` com colunas sequenciais e adiciona a aba `Recomputação sequencial`.

## O que a V102 não altera

- não reabre o solver global;
- não reabre o runner shadow como método governante;
- não altera o método local governante (`decisao_local_v1 + proxy v3`);
- não altera o replay do passado nem a estrutura oficial do fluxo principal.

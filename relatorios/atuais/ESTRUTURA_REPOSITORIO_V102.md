# Estrutura do repositório V102

## Camada nova da V102

A V102 preserva as camadas intermediárias introduzidas na V100 e V101 — auditoria temporal da `decisao_local_v1` e reescolha dinâmica pós-quebra — e adiciona uma terceira camada separada, de `recomputacao_sequencial_preventiva`, que recalcula a melhor fonte a cada pagamento futuro usando estado residual atualizado.

## Papel da V102

A nova camada usa a mesma materialização de candidatos da decisão local v1, mas substitui continuamente os saldos disponíveis por estados sequenciais já abatidos. Assim, a V102 distingue mudança preventiva de fonte, mudança por inviabilidade da fonte original e casos em que nem a recomputação sequencial encontra cobertura integral.

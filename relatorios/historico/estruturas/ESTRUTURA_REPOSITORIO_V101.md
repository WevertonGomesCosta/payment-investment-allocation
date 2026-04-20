# Estrutura do repositório V101

## Camada nova da V101

A V101 preserva a camada intermediária introduzida na V100 — a auditoria temporal da `decisao_local_v1` — e adiciona uma segunda camada separada, de `reescolha_dinamica_pos_quebra`, que recomputa a melhor fonte local quando a sugestão original deixa de ser coerente na sequência.

## Papel da V101

A nova camada usa a mesma materialização de candidatos da decisão local v1, mas substitui apenas os saldos disponíveis por estados dinâmicos já abatidos na sequência. Quando a fonte original ainda cobre integralmente o pagamento, ela é mantida. Quando não cobre, a reescolha dinâmica é acionada e a melhor fonte local entre os lotes remanescentes é recomputada sem abrir solver global.

# Baseline fixa V100

## Escopo da V100

A V100 preserva a baseline funcional da V99, mantém a saída operacional do console e do extrato futuro já aprovadas e adiciona uma auditoria temporal explícita sobre a `decisao_local_v1`, com depleção cumulativa dos lotes sugeridos na fotografia da data de referência.

## O que a V100 altera

- adiciona o módulo `nucleo/auditoria_temporal_decisao_local.py`;
- carrega a auditoria temporal como parte do `ContextoBaseline`;
- adiciona uma nova seção no console principal para distinguir cobertura local da coerência sequencial futura;
- amplia o `Extrato futuro` com colunas temporais e cria a aba `Auditoria temporal`;
- adiciona script diagnóstico próprio para a auditoria temporal da decisão local.

## O que a V100 não altera

- não altera o método governante (`decisao_local_v1` + `proxy econômico v3`);
- não reabre o runner shadow como método operacional;
- não adiciona solver global, multifonte governante ou switching ao fluxo principal;
- não altera a leitura local já aprovada do console e da planilha, apenas a complementa com uma camada temporal separada.

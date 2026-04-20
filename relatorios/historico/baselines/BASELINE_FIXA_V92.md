# Baseline fixa V92

## Escopo da V92

A V92 preserva integralmente a baseline funcional imediatamente anterior e abre o benchmark shadow do runner de simulação futura do Script 2 correto, sem migrar o runner legado bruto para o fluxo principal.

## O que a V92 altera

- nova camada diagnóstica `benchmark_runner_futuro_shadow`;
- comparação reproduzível entre o runner shadow futuro e a decisão local vigente;
- atualização da identidade da baseline e da documentação vigente.

## O que a V92 não altera

- motor financeiro;
- replay;
- `proxy v3` congelado;
- runners legados como orquestradores do fluxo principal.

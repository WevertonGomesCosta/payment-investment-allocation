# Baseline fixa V91

## Escopo da V91

A V91 preserva integralmente a baseline funcional imediatamente anterior e corrige a etapa de promoção do arquivo temporário usado no download da planilha financeira. A correção evita falso `PermissionError` no Windows ao validar o `.xlsx` baixado antes de sobrescrever `dados/dados_financeiros.xlsx`.

## O que a V91 altera

- validação do arquivo baixado com fechamento explícito do handle do `pd.ExcelFile`;
- tratamento específico de `PermissionError` na promoção do arquivo temporário para a planilha canônica;
- atualização da identidade da baseline e da documentação vigente.

## O que a V91 não altera

- motor financeiro;
- replay;
- `proxy v3` congelado;
- benchmarks shadow e auditorias diagnósticas.

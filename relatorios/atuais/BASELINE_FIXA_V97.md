# Baseline fixa V97

## Escopo da V97

A V97 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e adiciona ao console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos.

## O que a V97 altera

- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.

## O que a V97 não altera

- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V95.

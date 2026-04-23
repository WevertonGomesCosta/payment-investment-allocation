# Camada de scripts

## Contrato estrutural V154

- `scripts/diagnostico/`: localização canônica dos scripts de inspeção, consolidação e auditoria diagnóstica.
- `scripts/auditoria/`: geração de auditorias formais e artefatos de apoio.
- `scripts/operacional/`: rotinas operacionais e artefatos finais.
- `scripts/`: wrappers de compatibilidade para execução legada sem alterar contratos antigos.

## Regra de baixo risco

Antes de reorganizar o simulador central, a consolidação em `scripts/` deve preservar o comportamento externo: mover a implementação canônica para a subpasta temática e manter um wrapper plano no diretório raiz.


## Agrupamento temático adicional V155

- `scripts/diagnostico/temporal_decisao/`: fronteira canônica para auditorias de motor diário, pós-vencimento, valoração/`tau` e bloco crítico.
- wrappers legados continuam em `scripts/diagnostico/` e `scripts/`.

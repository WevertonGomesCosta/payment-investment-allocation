# 04_decisao_rd09a.md — RD-2026-04-28-09A

## Decisão final

**CONTRATO_EXAUSTAO_REMANESCENTES_APROVADO_COM_RESTRICOES**

## Fundamentação

1. A RD-08 identificou lotes com baixa folga operacional, especialmente `Lote 3600 mai.` e `Lote 3000 mar. B`.
2. A RD-09 confirmou a necessidade de monitoramento, mas também mostrou que lote sugerido e lote reserva precisam ser separados.
3. Remanescentes baixos positivos podem e devem virar candidatos formais de alocação futura, desde que respeitem o contrato econômico.
4. A exaustão residual não pode ser manual nem ad hoc.
5. A função objetivo oficial permanece sendo o patrimônio líquido terminal.
6. O critério de redução de fragmentação só pode atuar como critério secundário em empate econômico ou diferença materialmente irrelevante.

## Restrições

- Não houve alteração de motor.
- Não houve alteração da lógica de pagamentos.
- Não houve alteração da lógica de switching.
- Não houve alteração da função objetivo.
- Não houve alteração de dados oficiais.
- Não houve alteração de cache BCB/CDI.
- Não houve alteração da saída canônica.
- Não houve alteração de `requirements.txt`.

## Próxima microetapa recomendada

Implementar uma análise local/protótipo de candidatos `combinacao_exaustao_residual`, sem promoção automática, apenas para listar:

1. pagamento futuro candidato;
2. lote residual;
3. valor residual usado;
4. fonte complementar;
5. cobertura integral;
6. saldo final;
7. diferença econômica estimada;
8. decisão: promover, rejeitar ou manter baseline.

## Critério para implementação futura

A implementação só deve ser promovida se não gerar cobertura parcial, saldo negativo, violação de liquidez/carência/fiscalidade/cronologia ou perda material de patrimônio terminal.

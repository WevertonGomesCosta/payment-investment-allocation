# Contrato suplementar de validação diária orientada ao objetivo final — V176

Este documento complementa `CONTRATO_OPERACIONAL_PROJETO.md` e existe para evitar regressões de interpretação entre:

- o **contrato executável vigente** da baseline;
- e o **objetivo final do projeto**, que continua sendo o critério correto para validar saídas user-facing de pagamentos e switching.

## 1. Regra de leitura obrigatória

1. Toda validação diária user-facing deve ser interpretada contra o **objetivo final do projeto**: maximizar patrimônio líquido terminal com auditabilidade por lote/fonte.
2. Uma saída resumida que não exponha componentes reais dos pagamentos, fontes efetivas e cenários de switching não é suficiente para validação manual.
3. O fato de uma camada vigente ainda ser limitada não autoriza apresentar uma saída simplificada como se ela já representasse o motor conjunto final.

## 2. Guardrails obrigatórios de não regressão

4. Nenhum lote ou recebido futuro pode aparecer como **operacionalmente disponível** antes do dia corrente da validação.
5. O runner diário deve avançar por **dia 0, dia +1, dia +2, ...**, e não apenas por dias com pagamento.
6. Switching deve ser avaliado diariamente, inclusive em dias sem pagamento.
7. Lotes pós-vencimento que se tornam caixa ou ficam elegíveis no dia correto devem aparecer explicitamente no estado diário e competir nas decisões.
8. Saídas de pagamento devem expor:
   - fonte principal escolhida;
   - componentes reais utilizados;
   - quadro auditável de fontes candidatas relevantes;
   - custo fiscal, perda terminal e penalidades relevantes.
9. Saídas de switching devem expor:
   - ações candidatas do dia;
   - cenários classificados;
   - classe híbrida;
   - promovibilidade;
   - deltas contra o baseline;
   - e eventos concretos do cenário.

## 3. O que a validação diária ainda não prova sozinha

10. Mesmo com runner diário reformado, a validação não prova, sozinha, que o espaço de busca já cobre todas as combinações desejadas pelo objetivo final.
11. O runner diário serve para:
   - auditabilidade;
   - detecção de regressões temporais;
   - conferência por lote/fonte;
   - e inspeção da qualidade da competição local entre pagar, manter e trocar.
12. A expansão do espaço de busca continua sendo uma frente própria e posterior.

## 4. Casos obrigatórios de auditoria manual

13. Lotes monitorados de auditoria, como os blocos `Lote 3000 mar. V` e `Lote 3000 mar. B`, devem aparecer de forma verificável no runner diário.
14. Pagamentos de maior valor e pagamentos protegidos devem ser conferidos com o quadro completo de componentes do pagamento vencedor.
15. Sempre que o runner retornar zero switching promovido em janela material, a saída diária deve permitir distinguir entre:
   - ausência real de oportunidade;
   - espaço de busca insuficiente;
   - bloqueio pelo comparador híbrido;
   - ou limitação da baseline vigente.

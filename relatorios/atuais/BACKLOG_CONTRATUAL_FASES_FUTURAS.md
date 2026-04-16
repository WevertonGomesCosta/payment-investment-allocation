# Backlog contratual das fases futuras

Este documento reúne o que **ainda não é cobrável** da baseline atual, mas continua sendo parte do objetivo estratégico do projeto.

## 1. Modelo conjunto completo

1. Unificar de forma plena pagamentos, aportes, saldo disponível, recebidos futuros e switching em uma única decisão conjunta.
2. Fazer a decisão emergir de cenários integrados, e não de blocos independentes.

## 2. Função-objetivo e avaliação terminal

3. Implementar avaliação econômica por patrimônio líquido terminal com penalizações por risco/liquidez.
4. Formalizar a regra fiscal terminal híbrida dos lotes remanescentes.
5. Trabalhar com múltiplos horizontes, incluindo horizonte principal e horizontes adicionais de sensibilidade.

## 3. Decisão híbrida entre caixa disponível e resgate

6. Implementar critério econômico explícito para decidir entre usar saldo disponível e resgatar lote.
7. Substituir decisões locais simplistas por regra auditável de score econômico ou equivalente.

## 4. Recebidos futuros e auditoria de recebidos

8. Abrir camada auditável de recebidos com bruto/líquido, destino do valor e vínculo com pagamentos/aplicações.
9. Tratar recebidos futuros de forma contingente, podendo virar caixa disponível ou candidato imediato à alocação em carteira.

## 5. Saídas finais ainda não abertas

10. Evoluir o `.xlsx` para contemplar, quando a etapa for aberta:
    - auditoria formal de pagamentos;
    - auditoria formal de recebidos com bruto/líquido;
    - recomendação final por cenário integrado.

## 6. Switching e busca mais pesada

11. Abrir switching econômico híbrido por lote e por grupos de lotes.
12. Só depois disso abrir solver, MILP ou buscas mais pesadas, preservando auditabilidade.

## 7. Parametrização intradiária mais explícita

13. Tornar a precedência intradiária entre recebidos e pagamentos no mesmo dia uma regra central, explícita e auditável no `config`.
14. Registrar essa ordem na trilha de eventos quando a camada correspondente for aberta.

## 8. Critério de entrada no contrato executável

15. Um item deste backlog só deve migrar para o contrato executável quando estiver:
    - implementado de forma observável;
    - validado localmente;
    - documentado de forma estável.

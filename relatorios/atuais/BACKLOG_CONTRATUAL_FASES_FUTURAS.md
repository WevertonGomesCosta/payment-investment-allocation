# Backlog contratual das fases futuras

Este documento reúne o que **ainda não é cobrável** da baseline atual, mas continua sendo parte do objetivo estratégico do projeto.

## 1. Modelo conjunto completo

1. Unificar de forma plena pagamentos, aportes, saldo disponível, recebidos futuros e switching em uma única decisão conjunta.
2. Fazer a decisão emergir de cenários integrados, e não de blocos independentes.

## 2. Função-objetivo e avaliação terminal

3. Implementar avaliação econômica por patrimônio líquido terminal com penalizações por risco/liquidez.
4. Formalizar a regra fiscal terminal híbrida dos lotes remanescentes.
5. Trabalhar com múltiplos horizontes, incluindo horizonte principal e horizontes adicionais de sensibilidade.

## 3. Continuação da Frente F1

6. Refinar `saldo_disponivel_geral` para além da agregação de fontes explícitas, incluindo caixa não explicitado por recebido quando essa camada for aberta.
7. Refinar `recebido_auditavel` com leitura por evento e trilha mais explícita de destino observado versus destino elegível.
8. Projetar financeiramente o valor das fontes até cada data de pagamento, substituindo a fotografia da data de referência quando essa frente for aberta.
9. Abrir a regra local v1 entre saldo disponível, caixa pré-aplicação, recebidos e resgate.
10. Expor a trilha correspondente no console e no `.xlsx`.

## 4. Saídas finais ainda não abertas

11. Evoluir o `.xlsx` para contemplar, quando a etapa for aberta:
    - auditoria formal de pagamentos;
    - auditoria formal de recebidos com bruto/líquido;
    - recomendação final por cenário integrado.

## 5. Switching e busca mais pesada

12. Abrir switching econômico híbrido por lote e por grupos de lotes.
13. Só depois disso abrir solver, MILP ou buscas mais pesadas, preservando auditabilidade.

## 6. Parametrização intradiária mais explícita

14. Tornar a precedência intradiária entre recebidos e pagamentos no mesmo dia uma regra central, explícita e auditável no `config`.
15. Registrar essa ordem na trilha de eventos quando a camada correspondente for aberta.

## 7. Critério de entrada no contrato executável

16. Um item deste backlog só deve migrar para o contrato executável quando estiver:
    - implementado de forma observável;
    - validado localmente;
    - documentado de forma estável.

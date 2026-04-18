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
8. Projetar financeiramente o valor das fontes até cada `data_pagamento`, substituindo a fotografia da data de referência quando essa frente for aberta.
9. Abrir `multifonte v1` **somente** se surgir evidência concreta de que a cobertura/qualidade da decisão monofonte vigente se tornou insuficiente.
10. Expor a trilha correspondente no console e no `.xlsx` quando a etapa respectiva for aberta.

## 4. Migração restante de scripts originais

11. O mapa de absorção legado dos Scripts 1 e 2 já foi aberto na V77 e deve orientar as próximas migrações.
12. Priorizar apenas scripts legados que tragam regras ausentes sobre:
    - precedência intradiária entre recebido e pagamento;
    - lógica por evento de pagamento/recebido;
    - projeção econômica até a data do pagamento;
    - switching legado com regra de negócio material ainda não migrada.
13. Não migrar scripts redundantes, apenas auxiliares ou sem regra de negócio nova.
14. Prioridade imediata de legado após a V75: switching econômico legado em modo shadow/auditoria e benchmark do `resolver_hibrido_5p`, sem incorporação bruta do restante da infraestrutura legada.

## 5. Saídas finais ainda não abertas

14. Evoluir o `.xlsx` para contemplar, quando a etapa for aberta:
    - auditoria formal de pagamentos;
    - auditoria formal de recebidos com bruto/líquido;
    - recomendação final por cenário integrado.

## 6. Switching e busca mais pesada

15. Abrir switching econômico híbrido por lote e por grupos de lotes.
16. Só depois disso abrir solver, MILP ou buscas mais pesadas, preservando auditabilidade.

## 7. Parametrização intradiária mais explícita

17. Tornar a precedência intradiária entre recebidos e pagamentos no mesmo dia uma regra central, explícita e auditável no `config`.
18. Registrar essa ordem na trilha de eventos quando a camada correspondente for aberta.

## 8. Critério de entrada no contrato executável

19. Um item deste backlog só deve migrar para o contrato executável quando estiver:
    - implementado de forma observável;
    - validado localmente;
    - documentado de forma estável.


15. Prioridade imediata pós-V77/V78: auditoria comparativa entre `proxy v3` vigente e benchmark shadow do `resolver_hibrido_5p`, antes de qualquer tentativa de acoplamento funcional do benchmark ao fluxo principal.

# Contrato-alvo V117 — `alocador_pagamentos_terminal_v1` + `planejador_switching_temporal_v1`

## 1. Status da V117

1. A V117 é uma **camada contratual/de desenho arquitetural** da próxima etapa central do projeto.
2. Ela **não** substitui a V108 como baseline central executável.
3. Ela **não** promove a V116 a motor final.
4. A V117 existe para congelar a interface mínima da próxima implementação, evitando que a frente central volte a derivar para recomendações locais por conta sem integração ao objetivo terminal.

---

## 2. Pergunta central que a V117 precisa responder

> Em cada data relevante da timeline, qual combinação de decisões entre manter, aportar, switchar, resgatar lote aportado, usar lote não aportado, usar saldo disponível ou combinar fontes preserva melhor o patrimônio líquido terminal do cenário, respeitando cobertura, liquidez, carência, tributação e governança operacional?

---

## 3. Princípio de modelagem

5. O projeto deixa de ser orientado exclusivamente por evento de pagamento e passa a ser orientado por **timeline global de eventos relevantes**.
6. O switching passa a ser tratado como **decisão temporal autônoma**, escolhida na melhor data econômica viável e não subordinada apenas ao vencimento da conta.
7. O pagamento passa a ser tratado como **decisão de financiamento da obrigação**, comparando fontes alternativas pela perda de patrimônio líquido terminal.
8. As duas decisões continuam acopladas e devem operar sobre o mesmo estado global do sistema.

---

## 4. Núcleos mínimos da V117

### 4.1 `planejador_switching_temporal_v1`

9. O `planejador_switching_temporal_v1` deve gerar, para cada lote elegível, um conjunto pequeno e auditável de transições candidatas no tempo.
10. Cada transição candidata deve especificar, no mínimo:
   - lote_origem;
   - tipo_origem (`aportado` ou `nao_aportado`);
   - data_evento;
   - destino;
   - valor_bruto_estimado;
   - valor_liquido_estimado;
   - custo_fiscal_estimado;
   - impacto_esperado_em_liquidez;
   - motivo_economico.
11. O planejador deve considerar datas candidatas derivadas de:
   - data de referência;
   - datas de recebidos futuros;
   - datas de vencimento de pagamentos;
   - datas de fim de carência;
   - datas de liquidez relevante;
   - datas de mudança material de atratividade entre carteiras.
12. O planejador não deve gerar busca exaustiva irrestrita; ele deve gerar um conjunto controlado de alternativas por lote/data, auditável e compatível com heurística ou beam search leve.

### 4.2 `alocador_pagamentos_terminal_v1`

13. O `alocador_pagamentos_terminal_v1` deve decidir, para cada pagamento, qual fonte ou combinação mínima de fontes financiará a obrigação no estado já afetado pelas decisões temporais anteriores.
14. As fontes candidatas mínimas são:
   - `saldo_disponivel`;
   - `recebido_nao_aportado`;
   - `lote_aportado`;
   - `combinacao_minima`;
   - `sem_fonte_viavel`.
15. Quando houver `lote_aportado` ou `recebido_nao_aportado`, a decisão deve indicar explicitamente:
   - lote_id;
   - data de resgate/uso;
   - valor bruto usado;
   - valor líquido usado;
   - impacto fiscal estimado;
   - impacto terminal estimado.
16. O alocador não deve escolher a fonte pela menor perda local instantânea; deve escolher a fonte pela **menor perda de patrimônio líquido terminal** dentro da métrica central do projeto.

---

## 5. Timeline global obrigatória

17. A V117 exige uma timeline global mínima com eventos ordenados por data e precedência intradiária parametrizada.
18. A timeline deve suportar, no mínimo, os seguintes tipos de evento:
   - `referencia`;
   - `recebido`;
   - `switching`;
   - `aporte`;
   - `pagamento`;
   - `fim_carencia`;
   - `liquidez_relevante`;
   - `marco_fiscal`.
19. Quando múltiplos eventos ocorrerem no mesmo dia, a ordem intradiária deve continuar sendo governada pelo `config`.

---

## 6. Estado global mínimo

20. O estado global compartilhado entre os dois módulos deve conter, no mínimo:
   - saldo disponível geral;
   - recebidos futuros e recebidos já disponíveis não aportados;
   - inventário de lotes aportados com saldo bruto/líquido e base fiscal;
   - pagamentos futuros com classe operacional;
   - restrições de liquidez e carência;
   - produtos elegíveis da Carteira;
   - registro de decisões já aplicadas;
   - horizonte de avaliação terminal.
21. O estado deve ser atualizável evento a evento, preservando rastreabilidade completa por lote/fonte.

---

## 7. Ações candidatas mínimas por data

22. Em cada data relevante, o simulador central deve poder comparar pelo menos as seguintes ações candidatas:
   - manter estado atual;
   - aportar lote não aportado em produto elegível;
   - switchar lote aportado para produto elegível;
   - pagar com saldo disponível;
   - pagar com lote não aportado ainda não aplicado;
   - pagar com resgate de lote aportado;
   - pagar com combinação mínima entre fontes;
   - declarar `sem_fonte_viavel`.
23. O sistema deve permitir que uma decisão de switching ocorra em data anterior ao pagamento e altere o conjunto de fontes disponíveis para pagamentos futuros.

---

## 8. Comparador central mínimo da V117

24. A V117 deve continuar subordinada à `METRICA_CANONICA_MINIMA_CENTRAL.md`.
25. A comparação entre ações ou cenários deve preservar, no mínimo, esta hierarquia:
   1. minimizar violações de pagamentos `PROTEGIDA`;
   2. minimizar déficit líquido total;
   3. minimizar número de pagamentos sem cobertura integral;
   4. maximizar patrimônio líquido terminal;
   5. minimizar destruição estratégica de lotes relevantes;
   6. minimizar fragmentação residual e piora evitável de liquidez futura.
26. Quando o alocador comparar fontes para um único pagamento, ele deve fazê-lo com **look-ahead suficiente** para refletir essa hierarquia sobre a trajetória futura, e não apenas sobre a conta atual.

---

## 9. Regras específicas do `planejador_switching_temporal_v1`

27. O planejador deve avaliar switching tanto para lotes aportados quanto para lotes não aportados elegíveis à aplicação.
28. Para lote não aportado, a decisão deve distinguir explicitamente entre:
   - manter como caixa para pagamentos futuros próximos;
   - aportar imediatamente em carteira melhor;
   - postergar aporte para data mais eficiente.
29. Para lote aportado, a decisão deve distinguir explicitamente entre:
   - manter posição atual;
   - resgatar para pagamento;
   - switchar total;
   - switchar parcial, quando contratualmente permitido.
30. O planejador deve registrar sempre a justificativa econômica resumida da escolha da data.

---

## 10. Regras específicas do `alocador_pagamentos_terminal_v1`

31. O alocador deve comparar, para cada pagamento, fontes monofonte e combinação mínima, mas sem abrir multifonte irrestrito nesta etapa.
32. A combinação mínima deve permanecer controlada, auditável e economicamente justificável.
33. A decisão final por pagamento deve informar, no mínimo:
   - pagamento_id;
   - data_pagamento;
   - fonte_principal;
   - fonte_reserva, se houver;
   - lote_principal, se houver;
   - lote_reserva, se houver;
   - necessidade de switching prévio;
   - data do switching, se houver;
   - cobertura estimada;
   - impacto terminal incremental estimado;
   - motivo resumido da decisão.
34. O alocador deve preservar pagamentos protegidos antes de perseguir ganhos locais de retorno.

---

## 11. Interface entre os dois módulos

35. O `planejador_switching_temporal_v1` deve devolver um conjunto ordenado de **ações candidatas temporais**.
36. O `alocador_pagamentos_terminal_v1` deve consumir o estado resultante dessas ações e decidir a melhor fonte para cada obrigação.
37. O `simulador_central_eventos_v1`, quando aberto, deverá ser o executor comum das duas camadas.
38. O `avaliador_cenarios_conjuntos_v1`, quando aberto, deverá comparar cenários completos resultantes do plano temporal e da política de pagamentos.

---

## 12. Artefatos auditáveis mínimos esperados

39. A implementação futura deve gerar, no mínimo:
   - trilha de eventos por data;
   - auditoria de decisões de switching por lote e data;
   - auditoria de pagamentos com fonte principal e reserva;
   - impacto terminal incremental por decisão;
   - motivo resumido e rastreável da escolha.

---

## 13. O que ainda fica fora da V117

40. Continuam fora do escopo da V117:
   - solver global pesado completo;
   - multifonte irrestrito em todos os pagamentos;
   - otimização exaustiva sobre todas as datas e todos os produtos;
   - promoção automática de qualquer camada local anterior.

---

## 14. Critério de sucesso da próxima implementação

41. A implementação que materializar a V117 só poderá ser considerada bem-sucedida se: 
   - reduzir ou não piorar violações de `PROTEGIDA`;
   - melhorar a coerência entre switching e pagamentos;
   - aumentar a auditabilidade da decisão por lote/data/fonte;
   - produzir ganho terminal defendável sem depender de inflação local de switching.

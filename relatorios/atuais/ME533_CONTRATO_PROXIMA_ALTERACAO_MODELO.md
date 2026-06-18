# ME-533 — contrato formal da próxima alteração do modelo matemático e decisão econômica

## 1. Identificação formal

- **Frente:** ME-533.
- **Título:** contrato formal da próxima alteração do modelo matemático e decisão econômica.
- **Repositório:** `WevertonGomesCosta/payment-investment-allocation`.
- **Branch:** `me533-contrato-proxima-alteracao-modelo`.
- **PR:** #548.
- **Natureza:** contrato declarativo pré-implementação.
- **Tipo de mudança:** documental/contratual.
- **Alteração econômica nesta ME:** não.

## 2. Contexto

A sequência ME-531C/D/E estabilizou a saída observável oficial:

- métricas oficiais preservadas: `Rend. líq.`, `Rend. líq. motor`, `Dif. teórica`;
- métricas auxiliares removidas: `Rend. aux. calibrado`, `Dif. aux. calibrada`;
- contrato final de abas XLSX congelado em cinco abas oficiais;
- estrutura temporária `Auditoria Replay` removida da saída oficial;
- Etapas 9, 10 e 11 mantidas aprovadas.

A ME-532 confirmou prontidão arquitetural para retomar uma frente de modelagem/decisão econômica, desde que a próxima implementação preserve os contratos estabilizados de saída, paridade e governança.

A ME-533, portanto, não implementa modelo. Ela define o contrato que deverá reger uma próxima ME de implementação decisória.

## 3. Objetivo da ME-533

Criar um contrato técnico para orientar a próxima alteração do modelo matemático/decisão econômica, explicitando:

1. camadas que poderão ser alteradas;
2. função objetivo inferida do projeto;
3. restrições obrigatórias;
4. decisões que poderão mudar em implementação futura;
5. invariantes que não poderão mudar sem contrato próprio;
6. métricas de comparação antes/depois;
7. critérios de sucesso;
8. critérios de rejeição.

## 4. Camadas candidatas à próxima alteração

A próxima ME de implementação poderá atuar, com contrato explícito, nas seguintes camadas decisórias ou pré-decisórias.

| Camada | Pode ser alterada na próxima implementação? | Condição contratual |
|---|---:|---|
| Motor temporal conjunto | Sim | Deve preservar rastreabilidade por evento, lote, fonte e data. |
| Score/ranking | Sim | Deve preservar separação entre universo econômico/ranking e renderização. |
| Seleção de fontes para pagamento | Sim | Deve respeitar saldo, carência, liquidez, fiscalidade e cobertura de obrigações. |
| Decisão `pay_only` vs `switch_then_pay` | Sim | Deve explicar ganho econômico líquido e efeito nos pagamentos. |
| Liquidez | Sim | Deve ser tratada como restrição explícita, não como ajuste de saída. |
| Carência | Sim | Deve impedir uso de fonte/lote inelegível. |
| Imposto | Sim | Deve preservar ou versionar regras fiscais no núcleo. |
| Patrimônio terminal | Sim | Deve ser métrica central de comparação antes/depois. |
| Gates | Sim | Devem bloquear inconsistências econômicas e contratuais. |
| Console | Não | Continua observável, não decisório. |
| XLSX | Não | Continua observável, não decisório. |
| Etapa 10 | Não nesta frente decisória | Continua validação de paridade da renderização. |
| Etapa 11 | Não nesta frente decisória | Continua governança pós-paridade, sem remoção automática. |

## 5. Função objetivo inferida

A função objetivo operacional atual pode ser descrita como:

> maximizar o patrimônio líquido terminal, garantindo cobertura das obrigações obrigatórias e respeitando restrições de liquidez, carência, fiscalidade, saldo disponível, materialidade e governança.

A próxima implementação deverá tratar explicitamente os seguintes componentes:

1. **Patrimônio líquido terminal:** principal métrica de resultado econômico.
2. **Cobertura de obrigações:** pagamentos obrigatórios devem ser cobertos na data contratual, quando houver pacote viável.
3. **Liquidez:** decisões devem preservar capacidade de pagamento futuro e não usar recursos bloqueados.
4. **Carência:** lotes em carência não podem ser usados como fonte de pagamento ou switching fora do contrato.
5. **Fiscalidade:** imposto, líquido sacado e líquido residual devem ser calculados na camada de núcleo.
6. **Rastreabilidade:** toda decisão deve ser explicável por data, lote, fonte, produto e evento.
7. **Governança:** renderização, paridade e resíduos não podem alterar decisão econômica.

## 6. Restrições obrigatórias

A próxima implementação deve respeitar, no mínimo, as restrições abaixo.

### 6.1. Pagamentos

- Não atrasar pagamentos contratualmente obrigatórios.
- Não antecipar pagamentos sem regra explícita aprovada.
- Não transformar obrigação bloqueada em obrigação coberta por artefato de renderização.
- Não remover obrigação do horizonte para melhorar métrica econômica.
- Não alterar data de pagamento sem contrato próprio.

### 6.2. Saldos e fontes

- Não gerar saldo negativo.
- Não usar lote/fonte inexistente.
- Não usar lote sem saldo suficiente, salvo regra multifonte explícita.
- Não usar recurso futuro como caixa presente sem materialização formal.
- Não usar console ou XLSX como fonte de saldo.

### 6.3. Liquidez e carência

- Respeitar carência do produto/lote.
- Respeitar bloqueios de liquidez.
- Preservar elegibilidade temporal da fonte.
- Distinguir lote disponível, lote reservado, lote bloqueado e lote futuro.

### 6.4. Fiscalidade

- Calcular imposto no núcleo, não na renderização.
- Preservar distinção entre bruto, imposto e líquido.
- Não melhorar patrimônio terminal por omissão fiscal.
- Manter rastreabilidade do imposto por lote/fonte/evento.

### 6.5. Resíduos e materialidade

- Respeitar regra vigente de materialidade/resíduo.
- Não usar resíduo submaterial para justificar decisão econômica material.
- Não transformar normalização de resíduo em ganho patrimonial.
- Não reabrir `Auditoria Replay` como aba ou saída oficial.

### 6.6. Pagamento monofonte/multifonte

- Preservar o contrato vigente de pagamento monofonte ou multifonte.
- Em caso de multifonte, respeitar o limite contratual de resíduo por conta/dia.
- Não pulverizar pagamentos em fontes irrelevantes para criar ganho artificial.

## 7. Decisões que poderão mudar na próxima implementação

A próxima ME de implementação poderá modificar resultados econômicos desde que declare a alteração pretendida e prove sua consistência.

Decisões potencialmente mutáveis:

1. **Lote escolhido para pagamento.**
2. **Fonte escolhida para pagamento.**
3. **Uso de pagamento monofonte ou multifonte, conforme contrato vigente.**
4. **Escolha entre `pay_only` e `switch_then_pay`.**
5. **Destino de sobras de recebidos.**
6. **Ranking efetivo de produtos para switching/aporte.**
7. **Uso ou reserva de fontes futuras.**
8. **Alocação entre liquidez e rentabilidade.**
9. **Priorização entre menor imposto imediato e maior patrimônio terminal.**
10. **Bloqueio ou liberação de candidato econômico por gate.**

Qualquer mudança deve ser acompanhada de comparação antes/depois e justificativa econômica.

## 8. Invariantes que não podem mudar sem contrato próprio

Os itens abaixo ficam congelados para a próxima fase, salvo abertura de contrato específico.

### 8.1. Saída oficial

- Abas XLSX oficiais exatamente:
  - `Extrato Passado`;
  - `Extrato Futuro`;
  - `Switching`;
  - `Carteira`;
  - `Situação Atual`.
- Ausência de aba `Auditoria Replay`.
- Ausência de bloco final de `Auditoria Replay` no console.
- Console e XLSX como renderizações, não como fonte decisória.

### 8.2. Métricas oficiais

- Preservar `Rend. líq.`.
- Preservar `Rend. líq. motor`.
- Preservar `Dif. teórica`.
- Não reintroduzir `Rend. aux. calibrado`.
- Não reintroduzir `Dif. aux. calibrada`.
- Não criar nova métrica oficial sem contrato próprio.

### 8.3. Etapas formais

- Etapa 9 continua produzindo `PacoteSaidaObservavelOficial`.
- Etapa 10 continua recebendo `PacoteSaidaObservavelOficial` e produzindo `ResultadoParidadeRenderizacaoOficial`.
- Etapa 11 continua recebendo exclusivamente `ResultadoParidadeRenderizacaoOficial` como entrada formal de estado.
- Inventários e diagnósticos continuam auxiliares não decisórios.
- Governança continua sem remoção automática.

### 8.4. Identidade e rastreabilidade

- Preservar identidade de PR/ME nos artefatos gerados.
- Preservar manifesto de execução.
- Preservar SHA256 do XLSX operacional quando houver execução oficial.
- Preservar rastreabilidade por evento, lote, fonte, produto, data e obrigação.

## 9. Métricas de comparação antes/depois

A próxima implementação deverá comparar, no mínimo, as seguintes métricas entre baseline e proposta.

| Métrica | Interpretação | Uso na decisão |
|---|---|---|
| Patrimônio líquido terminal | Resultado econômico agregado | Métrica principal de otimização. |
| Obrigações cobertas | Quantidade e valor de pagamentos atendidos | Não pode piorar sem justificativa contratual. |
| Obrigações bloqueadas | Quantidade, valor e motivo de bloqueio | Deve ser explicado caso mude. |
| Número de switchings | Grau de movimentação operacional | Deve ser compatível com ganho líquido e governança. |
| Impostos pagos | Custo fiscal realizado | Deve ser medido por lote/fonte/evento. |
| Liquidez residual | Capacidade de cobertura posterior | Deve ser preservada conforme restrições. |
| Rendimento líquido observado | Resultado líquido por lote/fonte | Métrica de auditoria econômica. |
| `Rend. líq. motor` | Resultado simulado pelo motor | Deve permanecer conceitualmente consistente. |
| `Dif. teórica` | Diferença observada vs motor | Deve permanecer interpretável. |
| Impacto por lote/fonte | Explicação granular da mudança | Necessário para auditoria de decisões. |
| Divergências Etapa 10 | Paridade de renderização | Deve permanecer zero em divergência material. |
| Resíduos Etapa 11 | Governança pós-paridade | Não pode virar autorização automática. |

## 10. Critérios de sucesso da próxima ME de implementação

A próxima ME de implementação será aprovada somente se atender simultaneamente aos critérios abaixo.

1. **Ganho ou preservação justificada de patrimônio terminal.**
2. **Nenhuma quebra de pagamento obrigatório.**
3. **Nenhuma quebra de saldo, liquidez ou carência.**
4. **Nenhum uso de lote inelegível.**
5. **Nenhuma regressão fiscal material não explicada.**
6. **Etapas 9, 10 e 11 aprovadas.**
7. **Diferenças econômicas explicáveis por evento/lote/fonte.**
8. **Paridade console/XLSX preservada.**
9. **Saída oficial mantida no contrato de cinco abas.**
10. **Métricas oficiais preservadas.**
11. **Ausência de métricas auxiliares removidas.**
12. **Ausência de `Auditoria Replay` na saída oficial.**
13. **Manifesto e identidade formal coerentes com PR/ME.**
14. **Nenhuma mudança econômica causada por renderização.**

## 11. Critérios de rejeição

A próxima ME de implementação deve ser rejeitada se qualquer condição abaixo ocorrer.

1. Pagamento obrigatório passa a ocorrer fora da data contratual.
2. Pagamento é antecipado sem contrato explícito.
3. Obrigação coberta passa a bloqueada sem justificativa econômica e contratual.
4. Saldo negativo é produzido.
5. Lote inexistente ou inelegível é usado.
6. Carência é violada.
7. Liquidez é violada.
8. Imposto é omitido ou deslocado para renderização.
9. Console ou XLSX passa a alimentar decisão.
10. Etapa 10 é reprovada.
11. Etapa 11 é reprovada.
12. Métrica auxiliar removida é reintroduzida.
13. `Auditoria Replay` reaparece na saída oficial.
14. Contrato de abas é alterado sem ME própria.
15. Melhora econômica decorre de artefato de renderização, arredondamento não contratual ou supressão de obrigação.
16. A mudança não é rastreável por evento, lote, fonte e data.

## 12. Forma esperada da próxima implementação

A próxima ME de implementação deve apresentar:

1. contrato da mudança decisória específica;
2. hipótese econômica testável;
3. baseline antes da alteração;
4. saída depois da alteração;
5. comparação quantitativa antes/depois;
6. explicação de diferenças por lote/fonte/evento;
7. validação das Etapas 9, 10 e 11;
8. confirmação de invariantes preservados;
9. decisão objetiva: aprovar, reprovar ou aprovar com ressalva.

## 13. Proibições desta ME-533

Esta ME-533 não autoriza e não executa:

- alteração de código executável;
- alteração de dados financeiros;
- alteração de cache BCB;
- alteração de XLSX de saída;
- alteração de console;
- alteração das Etapas 9, 10 ou 11;
- implementação de novo modelo;
- alteração de `Rend. líq.`, `Rend. líq. motor` ou `Dif. teórica`;
- criação de nova métrica oficial;
- reintrodução de `Auditoria Replay`;
- mudança em pagamentos, switching, ranking, gates ou decisão econômica.

## 14. Parecer final

A ME-533 define o contrato formal mínimo para que a próxima frente possa implementar alteração decisória com segurança.

**Decisão:** a próxima implementação de modelo somente deve começar após este contrato estar aprovado e mergeado.

**Natureza da próxima frente esperada:** implementação controlada em camada decisória, provavelmente no motor temporal conjunto, score/ranking, seleção de fontes ou decisão `pay_only` versus `switch_then_pay`.

**Condição de avanço:** qualquer alteração econômica deve apresentar comparação antes/depois e manter aprovadas as Etapas 9, 10 e 11.

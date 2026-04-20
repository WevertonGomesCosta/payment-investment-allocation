# Contrato operacional executável do projeto `payment-investment-allocation`

Este documento define o que pode ser cobrado **agora** da baseline vigente e separa formalmente:

- a **frente central do projeto**, que deve voltar a conduzir a evolução principal do repositório;
- a **trilha experimental local do bloco crítico**, que permanece como sandbox metodológico auditável.

Este contrato não deve misturar regras executáveis correntes com backlog estratégico, changelog histórico ou hipóteses experimentais ainda não promovidas.

---

## 1. Escopo e status da baseline atual

1. A baseline documental vigente do repositório experimental é a **V113**.
2. A **baseline principal da frente central permanece V108** até promoção explícita de nova camada.
3. A V113 adiciona `alocacao_intradiaria_pacote_v1` como experimento central intradiário, sem promoção automática.
4. A V106 executa o saneamento contratual do repositório; a **V107** implementa a primeira camada da frente central; a **V108** recalibra essa camada com penalidade explícita de escassez futura para `PROTEGIDA`, prioridade intraclasse no mesmo dia e fallback auditável de “sem fonte viável”.
5. A V108 preserva a V105 como **baseline experimental local** do bloco crítico e mantém a V106 como marco contratual de separação de trilhas.
6. A V113 não reabre a trilha local do bloco crítico; atua apenas como camada experimental intradiária sobre a frente central.
4. O contrato executável deve descrever apenas o que já está implementado e observável na baseline, separando o que é núcleo principal do que é experimento local.
5. Regras futuras, metas estratégicas e camadas ainda não abertas permanecem em `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`.

---

## 2. Objetivo final do projeto

6. O objetivo final do projeto é construir um **motor conjunto, auditável e economicamente coerente** para:
   - pagamentos;
   - recebidos;
   - aportes;
   - e futuras decisões de switching.
7. Esse motor deve operar sobre a mesma base de dados e o mesmo `config`, com rastreabilidade por lote.
8. A decisão final do projeto deve buscar **maximizar o patrimônio líquido terminal**, respeitando:
   - cobertura dos pagamentos;
   - restrições de liquidez e carência;
   - tributação;
   - precedência intradiária parametrizada;
   - preservação de pagamentos protegidos;
   - auditabilidade completa por lote/fonte.
9. O projeto **não** tem como objetivo final otimizar isoladamente um único pagamento ou uma única janela local sem reconexão com o cenário conjunto.

---

## 3. Governança do repositório

10. O repositório-base oficial é `payment-investment-allocation`.
11. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial.
12. O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas do repositório diretamente na raiz.
13. Todo o projeto deve permanecer em português.
14. Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.
15. A checagem de release em `scripts/diagnostico/verificar_release_baseline.py` é gate obrigatório antes das entregas.
16. O pacote final não deve incluir artefatos temporários como `__pycache__`, `.pyc`, logs brutos auxiliares, caches efêmeros não oficiais ou saídas redundantes de versões antigas.
17. O mapa vigente de absorção legado dos Scripts 1 e 2 deve ser consultado antes de qualquer migração de regra de negócio ainda ausente.
18. O mapa vigente de absorção da execução principal do Script 2 deve ser consultado antes de qualquer tentativa de migração do runner legado ou da competição final entre estratégias.

---

## 4. Separação formal das trilhas do projeto

### 4.1 Frente central do projeto

19. A **frente central** é a única trilha autorizada a conduzir a evolução principal do motor do projeto.
20. A frente central inclui, no mínimo:
   - `caixa_recebidos_auditaveis`;
   - `fonte_elegivel_pagamento`;
   - `saldo_disponivel_geral`;
   - `decisao_local_v1`;
   - `auditoria_temporal_decisao_local`;
   - `reescolha_dinamica_pos_quebra`;
   - e a futura `recomputacao_sequencial_central_v1`.
21. A frente central deve ser governada por uma **métrica canônica mínima central**, e não por âncoras locais isoladas.
22. A frente central é a única trilha que pode ser promovida à condição de motor principal do projeto.

### 4.2 Trilha experimental local do bloco crítico

23. A trilha experimental local permanece ativa, mas fica formalmente rebaixada a **sandbox metodológico**.
24. Fazem parte dessa trilha, no estado atual:
   - `heuristica_conjunta_parcial_bloco_critico`;
   - `planejamento_conjunto_local_bloco_critico_v1`;
   - `microplanejamento_conjunto_bloco_critico_v2`.
25. Essa trilha pode:
   - provar hipóteses locais;
   - medir trade-offs;
   - gerar subrotinas reaproveitáveis;
   - apoiar auditorias comparativas.
26. Essa trilha **não** pode governar o motor principal sem promoção explícita.
27. Nenhuma camada dessa trilha pode virar baseline principal apenas por melhorar localmente um bloco curto ou um evento-âncora.

---

## 5. Critério de promoção de experimento local para a frente central

28. Uma camada da trilha experimental local só pode ser promovida se cumprir simultaneamente:
   - melhora ou não piora da métrica canônica mínima central;
   - não violação de pagamentos `PROTEGIDA` em relação à baseline central de referência;
   - ganho auditável fora do bloco local, ou justificativa econômica suficiente na métrica central;
   - compatibilidade com rastreabilidade por lote/fonte;
   - documentação explícita do trade-off aceito.
29. Melhoria exclusivamente local de cobertura de um evento-âncora **não** é condição suficiente para promoção.

---

## 6. Métrica canônica mínima central

30. A métrica canônica mínima central passa a ser documento oficial do repositório em `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`.
31. A futura `recomputacao_sequencial_central_v1` deve ser governada por essa métrica.
32. Até nova decisão explícita, a comparação central mínima deve seguir a ordenação hierárquica abaixo:

1. minimizar violações de pagamentos `PROTEGIDA`;
2. minimizar déficit líquido total dos pagamentos;
3. minimizar número de pagamentos sem cobertura integral;
4. maximizar patrimônio líquido terminal proxy do cenário;
5. minimizar destruição estratégica de lotes relevantes;
6. minimizar fragmentação residual e deterioração desnecessária da liquidez futura.

33. Quando for necessário comparar cenários de forma programática, essa métrica deve ser materializada como comparador lexicográfico ou score equivalente auditável, preservando a mesma hierarquia.
34. Nenhuma camada central futura deve ser avaliada apenas por excesso local, âncora local ou score proxy instantâneo.

---

## 7. F1 e camada monofonte vigente

35. A baseline mantém como contrato vigente da F1:
   - `recebido_auditavel`;
   - `fonte_elegivel_pagamento`;
   - `saldo_disponivel_geral`;
   - `decisao_local_v1`.
36. A `decisao_local_v1` permanece monofonte e auditável nesta etapa.
37. A F1 continua a usar o `proxy econômico v3` como critério vigente de decisão local, até nova evidência concreta.
38. A F1 não implica, por si só:
   - decisão econômica final do projeto;
   - solver global;
   - decisão multifonte oficial do motor principal;
   - integração conjunta completa com switching.

---

## 8. Camadas temporais e sequenciais atualmente abertas

39. A baseline mantém e reconhece como observáveis:
   - `auditoria_temporal_decisao_local`;
   - `reescolha_dinamica_pos_quebra`.
40. Essas camadas têm papel auditável e de diagnóstico de trajetória.
41. A futura `recomputacao_sequencial_central_v1` deverá evoluir a partir dessa base, mas já governada pela métrica canônica mínima central.
42. Enquanto essa camada central não existir, as camadas temporais/sequenciais atuais não devem ser confundidas com o motor conjunto final.

---

## 9. Camadas shadow e diagnósticas preservadas

43. A baseline mantém as camadas:
   - `switching_shadow_reconciliacao`;
   - `switching_economico_shadow`;
   - `resolver_hibrido_5p_shadow`;
   - `benchmark_agrupado_individual_shadow`;
   - `benchmark_runner_futuro_shadow`.
44. Todas essas camadas permanecem diagnósticas nesta etapa.
45. Nenhuma delas substitui automaticamente a decisão vigente do fluxo principal.
46. O runner shadow do Script 2 continua apenas diagnóstico e não deve ser promovido sem nova decisão explícita e evidência suficiente.

---

## 10. Classes operacionais de pagamentos

47. A classificação operacional de pagamentos em `PROTEGIDA`, `SEMIPROTEGIDA` e `FLEXIVEL`, quando usada, deve servir como camada de governança e restrição explícita.
48. Nenhuma política central futura pode piorar pagamentos `PROTEGIDA` sem regra contratual nova e explícita.
49. Políticas experimentais que sacrifiquem pagamentos `SEMIPROTEGIDA` ou `FLEXIVEL` devem permanecer na trilha experimental até passarem pelo critério de promoção definido neste contrato.

---

## 11. O que continua fora do contrato executável

50. Ainda não fazem parte do contrato executável principal:
   - solver global completo;
   - decisão conjunta final de pagamentos + aportes + switching;
   - competição final entre estratégias legadas e motor principal;
   - switching operacional acoplado à frente central;
   - promoção automática das políticas V103–V105.
51. Esses itens só podem ser abertos por etapa posterior explicitamente auditada e documentada.

---

## 12. Hierarquia documental oficial

52. A documentação vigente deve ficar concentrada em `relatorios/atuais/`.
53. Relatórios de versões anteriores devem permanecer preservados em `relatorios/historico/`, organizados por tipo documental.
54. O arquivo `relatorios/INDICE_RELATORIOS.md` deve ser tratado como mapa oficial de navegação documental.
55. O README deve refletir a baseline vigente e a separação formal entre frente central e trilha experimental local.

---

## 13. Regra de foco do projeto a partir da V108

56. A partir da V106, o foco principal do projeto volta a ser a construção do motor conjunto e auditável orientado pela métrica canônica mínima central.
57. O bloco crítico 20/04/2026–20/05/2026 permanece como laboratório local, mas deixa de ser o eixo central de evolução do repositório.
58. Novas iterações locais só devem ser abertas se estiverem explicitamente conectadas a hipótese nova relevante para a frente central.


## 14. Recomputação sequencial central v1

57. A `recomputacao_sequencial_central_v1` passa a ser a primeira camada executável da frente central após o saneamento contratual.
58. Ela deve recalcular a melhor fonte a cada pagamento com estado residual atualizado e comparador governado pela métrica canônica mínima central.
59. Enquanto não houver nova decisão explícita, a `recomputacao_sequencial_central_v1` não substitui o solver global nem promove automaticamente políticas experimentais locais.


58. A V108 adiciona reserva mínima implícita para `PROTEGIDA` futura, prioridade intraclasse operacional no mesmo dia e fallback auditável de “sem fonte viável” dentro da `recomputacao_sequencial_central_v1`.
59. A V108 continua sem solver global completo e deve ser interpretada como calibração da frente central, não como camada final do motor conjunto.

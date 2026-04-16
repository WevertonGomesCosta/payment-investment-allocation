# Contrato operacional do projeto `payment-investment-allocation`

Este documento consolida o mapa oficial de regras da fase atual do projeto.
Ele deve servir como referência estável para reavaliações da baseline,
auditorias dos scripts-base e futuras evoluções do repositório.

## 1. Governança do projeto

1. O repositório-base oficial é `payment-investment-allocation`.
2. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial (`v1`, `v2`, `v3`, ...).
3. O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas do repositório diretamente na raiz.
4. Todo o projeto deve permanecer em português.
5. A baseline atual é a V43.

## 2. Objetivo central do sistema

6. O projeto deve unificar os dois scripts-base em um modelo conjunto de alocação de recebidos para pagamentos e investimentos.
7. O sistema deve integrar otimização de pagamentos/gastos, aporte/alocação em carteira, switching entre lotes/produtos e análise conjunta de patrimônio/rendimento líquido final.
8. A função-objetivo principal do modelo conjunto deve ser o patrimônio líquido terminal com penalizações por risco/liquidez.

## 3. Regra metodológica principal de auditoria

9. A divisão física dos módulos dos scripts-base não é confiável como fronteira semântica.
10. A unidade oficial de análise é a responsabilidade real da função, e não o módulo onde ela aparece.
11. Antes de criar, migrar, renomear ou consolidar qualquer função, devemos sempre revisar blocos equivalentes dos dois scripts, mapear responsabilidade real, identificar complementaridades/duplicações/divergências, revisar o que já existe no repositório e só então decidir o que manter, unificar, mover, excluir ou adiar.

## 4. Regras de entrada de dados

12. O script deve ler somente estas três abas primárias: `Carteira`, `Todos os Gastos` e `Inventário de Lotes`.
13. Toda estrutura adicional necessária deve ser criada internamente pelo script, e não lida como entrada primária.
14. Aportes e ligações gasto-lote devem ser tratados como estruturas derivadas internamente.

## 5. Regras sobre lotes e estado financeiro

15. Os dados incluem gastos passados, recebidos passados, pagamentos feitos com lotes já aportados, pagamentos feitos com lotes não aportados já consumidos e lotes não aportados ainda disponíveis.
16. Lotes não aportados ainda disponíveis devem ser considerados para alocação na melhor carteira disponível, isoladamente ou em combinação parcial/total com outros lotes/aportes já realizados.
17. A modelagem de estados de lote não pode ser binária; ela deve comportar, no mínimo: lote aportado ativo, aportado parcialmente resgatado, aportado exaurido, não aportado disponível, não aportado consumido e lote derivado de combinação, resgate, aporte ou switching.
18. Semântica formal do campo `Investimento` em `Inventário de Lotes`:
    - com nome de produto = lote aportado/associado;
    - em branco = lote não aportado disponível somente se a data do lote for atual ou passada em relação à data de referência da análise;
    - em branco com data futura = recebido futuro ainda não disponível hoje, elegível apenas a partir da sua data;
    - `Investimento = "-"` = lote não aportado já consumido/exaurido, que não deve voltar como candidato de alocação sem regra explícita de reclassificação.
19. Todo produto deve ter uma identificação canônica interna única, mesmo que precise ser gerada internamente a partir da aba `Carteira`.

## 6. Regras sobre projeções futuras

20. A base contém projeções futuras de gastos e de recebidos.
21. Essas projeções são parte essencial da finalidade analítica do script.
22. A análise deve ser simultaneamente histórica, situacional e prospectiva.

## 7. Regra de modelo conjunto e recíproco

23. A modelagem deve ser conjunta e recíproca: a análise de switching depende da otimização dos pagamentos, e a otimização dos pagamentos depende simultaneamente das decisões de aporte e switching.
24. Pagamento, aporte e switching não podem ser tratados como processos independentes.
25. A decisão correta deve emergir de um cenário integrado.

## 8. Regras sobre o `config`

26. O `config` é a fonte central e obrigatória de configuração do projeto.
27. Tudo o que já está no `config` deve sair do código como constante duplicada, fallback paralelo desnecessário, regra hardcoded indevida ou parametrização redundante.
28. O `config` pode e deve ser alterado, expandido, simplificado, reorganizado, limpo ou reestruturado sempre que isso for a melhor alternativa técnica, eficiente e auditável.
29. Quando houver conflito entre uma regra global do `config` e um comportamento explicitamente definido para um produto canônico, prevalece a regra específica do produto, e a regra global fica como fallback.

## 9. Regra crítica sobre cálculo de rendimento

30. O cálculo atual de rendimento dos dois scripts não deve ser tratado como verdade consolidada.
31. Toda implementação de rendimento deve ser auditada, comparada entre scripts, comparada com os apps bancários e calibrada para ficar o mais próxima possível da realidade observada.
32. O cálculo de rendimento deve ser tratado como hipótese operacional auditável, não como regra fechada.
33. O rendimento dos lotes deve considerar explicitamente todos os resgates/retiradas para pagamentos ao longo do tempo, de modo que o valor remanescente continue rendendo e o novo rendimento seja calculado sobre o saldo após cada resgate.

## 10. Regras de temporalidade e decisão intradiária

34. A precedência intradiária entre recebidos e pagamentos no mesmo dia deve ficar parametrizada no `config`, permitindo cenários diferentes de ordem de eventos.
35. Essa ordem precisa ser tratada como parte crítica da simulação.

## 11. Regra sobre horizonte-base da análise

36. A análise conjunta deve usar múltiplos horizontes, com um horizonte principal ancorado na projeção já existente na base e horizontes adicionais de sensibilidade/avaliação mais longa.

## 12. Regra sobre critério entre saldo disponível e resgate

37. A decisão entre usar saldo disponível e resgatar lote deve seguir uma regra híbrida com score econômico.
38. O sistema não deve depender apenas de um critério local como menor imposto ou menor custo de oportunidade.

## 13. Regra sobre recebidos futuros ainda não aportados

39. Recebidos futuros ainda não aportados devem entrar no modelo de forma contingente, podendo atuar como caixa disponível na data do recebimento ou como candidatos imediatos à alocação em carteira.
40. Essa escolha deve depender da necessidade de pagamento do dia e da melhor decisão econômica no cenário conjunto.

## 14. Regras de auditabilidade e saídas

41. No console e no arquivo final `.xlsx`, o sistema deve exibir, para todos os recebidos relevantes, valor bruto e valor líquido de forma auditável.
42. Para cada pagamento, o sistema deve indicar explicitamente de qual lote saiu o valor resgatado ou se o pagamento foi feito com saldo disponível.
43. Quando houver pagamentos e recebidos no mesmo dia, o sistema deve decidir e registrar auditavelmente se o pagamento será feito com o valor recebido ainda não aportado ou com resgate de lote já aportado.
44. A saída do console também deve ser organizada, de fácil legibilidade e entendimento, evitando excesso de colunas por tabela/bloco; quando necessário, a informação deve ser dividida em mais de uma tabela para o mesmo bloco, preservando colunas fixas e rastreáveis, como a identificação do lote.

## 15. Escopo mínimo obrigatório do `.xlsx` final

45. O arquivo final `.xlsx` deve conter, no mínimo:
    - aba de extrato/eventos;
    - aba de auditoria de pagamentos;
    - aba de auditoria de recebidos com bruto/líquido;
    - aba de recomendação final por cenário;
    - aba de situação atual, cobrindo o passado até a data presente.

## 16. Regra fiscal terminal dos lotes remanescentes

46. A avaliação fiscal terminal dos lotes remanescentes deve seguir uma lógica híbrida, dependendo do tipo de comparação e do cenário.

## 17. Granularidade principal do switching

47. A granularidade do switching deve ser híbrida, permitindo decisões individuais por lote e decisões agregadas/conjuntas por grupos de lotes.

## 18. Estratégia principal de geração de cenários

48. A geração de cenários deve seguir uma estratégia híbrida, começando por abordagens simples e funcionais e refinando depois com busca mais pesada.
49. Na fase inicial, devem ser priorizadas estratégias simples e eficientes como `cliff`, `VPL` e heurísticas simples e auditáveis.
50. Modelos mais pesados, como MILP e buscas mais sofisticadas, ficam para etapa posterior, depois que o script estiver funcional.

## 19. Regras sobre informações de produto e validação incremental

51. Informações relevantes de comportamento de produto não devem ser interpretadas a partir de texto livre em `Observações` como regra principal do motor; quando forem materialmente importantes, devem ser formalizadas em colunas estruturadas na aba `Carteira` e/ou no `config`, ficando `Observações` apenas como apoio humano/documental.
52. Cada etapa do projeto deve ser acompanhada de instruções claras de execução local e de uma validação mínima observável no console e/ou nos artefatos gerados, permitindo teste incremental na máquina do usuário.
53. Auditorias intermediárias podem ser mantidas, resumidas ou desativadas conforme continuem úteis, mas deve existir sempre um caminho explícito para validar a etapa implementada.

## 20. Artefatos proibidos no pacote final

**20.1. Regra principal**  
O repositório entregue em cada versão não deve incluir artefatos de execução local ou temporários, como `__pycache__`, arquivos `.pyc`, logs brutos auxiliares, caches efêmeros e arquivos de validação não oficiais.

**20.2. Regra de empacotamento**  
O pacote final deve conter apenas artefatos documentais e operacionais oficiais da versão.

## 21. Regras de arquitetura e evolução da baseline

54. Antes de cada entrega de nova versão do repositório, a etapa implementada deve ser executada e validada localmente no ambiente disponível, com identificação e correção prévia dos bugs observáveis, para que o usuário receba o repositório com a menor necessidade de ajuste posterior possível dentro do escopo da etapa.
55. Não devemos abrir domínio profundo antes da auditoria correspondente.
56. A V11 deve ser tratada como baseline fixa de referência, podendo evoluir apenas por alterações futuras validadas de forma organizada.
57. O fluxo correto de evolução continua sendo: auditar, mapear responsabilidade real, reavaliar a baseline atual e implementar apenas o que estiver sustentado pela auditoria.

## Observação final

Este contrato pode evoluir futuramente, mas qualquer alteração deve ser validada de forma organizada antes de ser incorporada ao projeto.


## Atualização metodológica da V21

- a aba `Carteira` passa a ser o **universo único** de produtos do projeto;
- a filtragem de candidatos deve ser feita **programaticamente no script**, servindo apenas ao motor;
- a triagem do motor passa a usar um **score v1 multicritério**, contextual ao cenário, apenas como triagem preliminar proxy;
- aplicação mínima, carência e liquidez devem ser avaliadas contextualmente ao cenário;
- confiabilidade operacional permanece fora do score principal nesta fase.


## Atualização metodológica da V22

A V22 abre apenas o núcleo financeiro mínimo do bloco 07, preservando a separação entre matemática financeira base do lote e camadas posteriores de solver, replay, switching econômico, otimização e relatório financeiro atual.


## Atualização metodológica da V23

A V23 abre o replay controlado do passado sobre o núcleo financeiro mínimo já implementado, reconciliando pagamentos históricos apenas com lotes explicitamente informados, sem abrir switching econômico, score econômico final, solver ou relatório financeiro atual.


## Atualização metodológica da V24

A V24 reforça o replay controlado do passado para consumir explicitamente lotes históricos não aportados marcados com `-` na coluna `Investimento`, além de permitir resolução auditável de aliases históricos quando o lote informado na despesa divergir do identificador presente no inventário, desde que a correspondência estrutural seja suficientemente forte.


## Atualização operacional V26

A baseline passa a suportar cache diário do CDI do BCB para auditoria e replay, com janela iniciando no primeiro dia do mês do primeiro pagamento/recebido até a data de referência. Na indisponibilidade da série diária, o sistema deve fazer fallback controlado para a taxa de modelo, sem interromper a execução local.


## Atualização operacional V38

### Regra canônica de disponibilidade temporal do lote

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.


## 22. Hierarquia documental oficial

58. A documentação operacional vigente deve ficar concentrada em `relatorios/atuais/`.
59. Relatórios de versões anteriores devem permanecer preservados em `relatorios/historico/`, organizados por tipo documental.
60. O arquivo `relatorios/INDICE_RELATORIOS.md` deve ser tratado como o mapa oficial de navegação da documentação.
61. O `README.md` deve apontar apenas para os documentos vigentes e para o índice documental, evitando listar relatórios históricos no nível principal.

## Atualização operacional V39

### Limpeza documental ampliada da baseline

A V39 consolida a documentação ativa em `relatorios/atuais/`, move a trilha histórica para `relatorios/historico/` e elimina artefatos temporários proibidos do pacote final, como `__pycache__` e arquivos `.pyc`. Essa reorganização não altera a lógica financeira do projeto; ela apenas reduz ruído operacional e melhora a navegabilidade da baseline.


## Atualização operacional V43

### Limpeza ampliada do pacote e atualização da base canônica

A V43 consolida a limpeza do repositório ao manter apenas a documentação vigente em `relatorios/atuais/`, mover documentos ativos antigos para `relatorios/historico/`, remover resíduos temporários e atualizar `dados/dados_financeiros.xlsx` como base canônica atual do projeto. A geração operacional corrente passa a usar `saidas/relatorio_operacional_v43.xlsx` como artefato oficial da versão quando a planilha é produzida localmente.

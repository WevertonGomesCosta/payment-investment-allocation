# Contrato operacional mestre do projeto `payment-investment-allocation` — V179

Este documento passa a ser o **contrato operacional mestre vigente** do projeto.

Ele consolida a governança operacional do repositório em torno da **V179**, absorvendo explicitamente o modelo oficial do projeto e rebaixando documentos anteriores como **V108** e **V117** a **contexto histórico/documental intermediário**, sem força normativa principal.

Este contrato deve ser lido em conjunto com:

- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`
- `relatorios/atuais/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`
- `relatorios/atuais/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`

Quando houver conflito entre documentos:

1. prevalece este **Contrato Operacional Mestre**;
2. em seguida, o **Modelo Matemático Estatístico-Financeiro Oficial V179**;
3. depois, os contratos suplementares de validação diária e pós-vencimento/gate;
4. por fim, auditorias, relatórios de baseline e documentos históricos.

---

## 1. Status normativo e escopo vigente

1. A baseline documental e metodológica vigente do projeto é a **V179**.
2. O núcleo normativo atual do projeto é composto por:
   - este `CONTRATO_OPERACIONAL_PROJETO.md`;
   - `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`;
   - `CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`;
   - `CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`.
3. O projeto deve ser interpretado como um **motor conjunto diário de decisão financeira**, e não como uma coleção de heurísticas independentes de pagamento, switching, runner ou diagnóstico.
4. Este contrato não deve misturar:
   - regras vigentes do projeto;
   - backlog futuro;
   - changelog histórico;
   - hipóteses locais experimentais ainda não promovidas.
5. Metas futuras e frentes ainda não abertas continuam em `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`.

---

## 2. Objetivo final do projeto

6. O objetivo final do projeto é construir um **motor conjunto, auditável e economicamente coerente** para decidir, dia a dia, sobre:
   - pagamentos;
   - uso de saldo disponível;
   - uso de lotes aportados;
   - uso de lotes vencidos e normalizados;
   - switching entre produtos;
   - manutenção ou não ação.
7. A decisão do dia deve buscar **maximizar o patrimônio líquido terminal líquido**, respeitando simultaneamente:
   - pagamento obrigatório das contas do dia;
   - restrições de disponibilidade temporal;
   - liquidez;
   - carência;
   - tributação;
   - regras dos produtos;
   - precedência intradiária do pacote escolhido;
   - auditabilidade completa por lote, fonte, conta e pacote.
8. O projeto não tem como objetivo final otimizar isoladamente:
   - uma única conta;
   - um único lote;
   - um único switching;
   - uma única janela local sem reconexão ao cenário conjunto do dia.

---

## 3. Modelo decisório vigente

9. A unidade decisória oficial do projeto é o **dia `t`**.
10. Em cada dia `t`, o motor deve primeiro verificar se existem contas com vencimento no dia.
11. Se não houver contas no dia, os pacotes factíveis são apenas:
    - `no_action`;
    - `switch_only`.
12. Se houver contas no dia, os pacotes factíveis são apenas:
    - `pay_only`;
    - `switch_then_pay`;
    - `pay_then_switch`.
13. A decisão do dia deve comparar os pacotes factíveis sobre o **mesmo estado econômico do dia**, usando o mesmo critério terminal e a mesma governança de desempate.
14. O modelo matemático oficial do projeto é o documento `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`, que passa a ser o anexo metodológico normativo deste contrato.

---

## 4. Regras obrigatórias de pagamento

15. A data da planilha é a data correta de pagamento da conta.
16. O projeto não deve considerar:
    - atraso de pagamento;
    - antecipação de pagamento;
    - não pagamento;
    - pagamento parcial da conta.
17. Cada conta do dia deve ser paga **integralmente no próprio dia**.
18. O pagamento do dia deve ser resolvido **conjuntamente** sobre o conjunto das contas com vencimento em `t`.
19. O pagamento combinatório de uma ou mais contas do dia é permitido, mas deve obedecer à seguinte regra operacional global:
    - se apenas uma fonte for usada no pagamento do dia, tudo certo;
    - se múltiplas fontes forem usadas no pagamento do dia, então **no máximo uma** dessas fontes pode terminar a fase de pagamento com residual positivo;
    - todas as demais fontes usadas devem zerar nessa fase.
20. Essa regra vale para o conjunto dos pagamentos do dia, e não apenas por conta isolada.
21. O objetivo operacional dessa regra é evitar pulverização desnecessária de resíduos e preservar simplicidade operacional compatível com o uso real dos recursos.

---

## 5. Regras obrigatórias de elegibilidade e pós-vencimento

22. O motor não deve começar diretamente do conjunto bruto de recursos como conjunto elegível.
23. Antes da otimização, o projeto deve derivar explicitamente:
    - fontes elegíveis para pagamento;
    - fontes elegíveis para switching.
24. Essa filtragem deve ocorrer antes da comparação dos pacotes do dia.
25. Uma fonte só pode entrar como elegível se passar pelos filtros de:
    - disponibilidade temporal;
    - liquidez/resgate;
    - carência de retirada ou saída;
    - regras operacionais do produto.
26. Se um lote venceu em `t` ou antes, ele deixa de ser tratado como lote aportado ativo e passa a ser tratado como **fonte disponível do dia**.
27. Se um lote vence depois de `t`, ele não pode ser tratado como disponível por vencimento.
28. O tratamento de pós-vencimento deve ser parte do estado econômico do dia e não apenas uma camada de auditoria posterior.

---

## 6. Regras obrigatórias de switching

29. O projeto adota somente três formas de switching:
    - **individual**;
    - **agrupado combinatório**;
    - **integral**.
30. O agrupado deve ser realmente combinatório, e não apenas junção simples ou heurística nominal de poucos casos fixos.
31. O integral deve ser interpretado como o **maior grupo factível elegível do pacote do dia**, após filtros de disponibilidade, liquidez, carência, ticket e compatibilidade com o produto destino.
32. Uma mesma fonte não pode participar de mais de um switching no mesmo dia.
33. Uma mesma fonte pode:
    - participar da fase de pagamento;
    - e depois, com o residual, participar de um único switching.
34. No pacote `pay_then_switch`, o switching deve atuar sobre o residual pós-pagamento elegível.
35. No pacote `switch_then_pay`, o switching deve atuar sobre o conjunto elegível pré-pagamento.
36. A distinção entre pré-pagamento e pós-pagamento é obrigatória tanto na modelagem quanto na implementação.

---

## 7. Valoração, rendimento e critério econômico

37. O projeto deve usar explicitamente o submodelo de rendimento e valoração dos lotes já validado no repositório e alinhado à saída do console.
38. Esse submodelo é parte do contrato vigente porque fornece, no mínimo:
    - valor economicamente disponível da fonte no dia;
    - valor terminal líquido de manter;
    - valor terminal líquido dos grupos em switching;
    - custo de oportunidade de usar a fonte em pagamento.
39. O critério econômico do pagamento não é “menor taxa nominal”.
40. O critério correto é usar a fonte ou combinação de fontes com **menor custo de oportunidade terminal líquido**, respeitando as restrições operacionais do pacote do dia.
41. O critério econômico do switching também deve ser comparado pelo efeito terminal líquido, e não por ganho local isolado.

---

## 8. Conservação de valor e residual mantido

42. A conservação de valor faz parte do núcleo normativo do modelo.
43. O termo de valor mantido deve permanecer no modelo, com interpretação de **residual final mantido ao fim do pacote**.
44. No pacote `pay_then_switch`, o switching atua integralmente sobre o residual elegível da fonte: o residual entra inteiro ou não entra.
45. O projeto não deve permitir fracionamento livre do switching sobre o residual.
46. O residual final do pacote precisa permanecer auditável por lote/fonte.

---

## 9. Cronologia intradiária oficial

47. A cronologia intradiária do dia deve ser congelada e respeitada pela implementação.
48. Todo pacote do dia deve começar por:
    - incorporar recebidos disponíveis no dia;
    - normalizar lotes vencidos em `t`.
49. Depois disso:
    - `no_action` apenas mantém o estado;
    - `switch_only` executa o switching vencedor e fecha o estado;
    - `pay_only` paga integralmente as contas e fecha o estado;
    - `switch_then_pay` executa switching, depois paga e então fecha o estado;
    - `pay_then_switch` paga, depois executa switching sobre o residual e então fecha o estado.
50. Um recurso só pode ser usado em uma etapa se ele já existir economicamente naquela etapa.

---

## 10. Convenções de governança obrigatórias

51. O contrato congela quatro convenções de governança transversal:
    - arredondamento;
    - horizonte principal e sensibilidades;
    - hierarquia de desempate;
    - convenção intradiária de disponibilidade.

### 10.1. Arredondamento

52. O documento formal e a implementação devem congelar uma política uniforme de arredondamento monetário a centavos.
53. A política deve ser aplicada de forma consistente para:
    - pagamentos;
    - impostos;
    - residuais;
    - valores líquidos;
    - comparação entre pacotes.

### 10.2. Horizonte principal e sensibilidades

54. O projeto deve operar com um **horizonte principal `H`** para a decisão base.
55. Sensibilidades adicionais devem ser tratadas como auditoria ou análise complementar, salvo regra explícita em contrário.

### 10.3. Hierarquia de desempate

56. Quando dois pacotes tiverem valor terminal praticamente equivalente, a decisão deve obedecer à seguinte hierarquia documental de desempate:
    1. maior valor terminal líquido;
    2. maior liquidez residual útil;
    3. menor número de fontes usadas no pagamento do dia;
    4. menor número de switchings executados;
    5. menor complexidade operacional global.

### 10.4. Disponibilidade intradiária

57. Recursos incorporados em `t` entram no estado antes da decisão do pacote do dia.
58. Recursos só podem ser consumidos por uma etapa se já estiverem economicamente disponíveis naquela etapa.

---

## 11. Validação diária user-facing

59. Toda camada user-facing de validação diária deve ser compatível com este contrato mestre e com o modelo oficial V179.
60. Não deve ser aceita saída diária que:
    - oculte os componentes reais do pagamento vencedor;
    - oculte as fontes candidatas do pagamento;
    - oculte as ações e cenários de switching do dia;
    - apresente lotes futuros ou ilíquidos como elegíveis antes da hora;
    - apresente inconsistência entre decisão econômica, execução e monitoramento do estado.
61. A validação diária deve permanecer subordinada aos contratos suplementares vigentes (`V176` e `V177`), mas esses contratos suplementares não substituem o núcleo deste contrato mestre.

---

## 12. Governança do repositório

62. O repositório-base oficial é `payment-investment-allocation`.
63. Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial.
64. O `.zip` deve abrir sem pasta interna raiz, com arquivos e pastas diretamente na raiz do pacote.
65. Todo o projeto deve permanecer em português.
66. Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.
67. A checagem de release em `scripts/diagnostico/verificar_release_baseline.py` permanece gate obrigatório antes das entregas.
68. O pacote final não deve incluir artefatos efêmeros como `__pycache__`, `.pyc`, logs brutos auxiliares, caches não oficiais e saídas redundantes temporárias.
69. O índice oficial de navegação documental é `relatorios/INDICE_RELATORIOS.md`.

---

## 13. Hierarquia documental vigente

70. A hierarquia documental vigente do projeto passa a ser:
    1. `CONTRATO_OPERACIONAL_PROJETO.md` — contrato mestre vigente;
    2. `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md` — anexo metodológico oficial;
    3. contratos suplementares vigentes (`V176` e `V177`);
    4. auditorias e validações vigentes;
    5. backlog contratual;
    6. documentos históricos.
71. O `README.md` e o `LEIA-ME_OPERACIONAL.md` devem refletir essa hierarquia.

---

## 14. Rebaixamento explícito de V117 e V108 a contexto histórico

72. Os documentos V117 e V108 deixam de ser referência normativa principal do projeto.
73. Eles permanecem preservados por rastreabilidade histórica, contextual e arquitetural, mas passam a ser lidos apenas como:
    - contexto intermediário de evolução do motor;
    - registro de baseline histórica;
    - documentação auxiliar de transição.
74. Em particular:
    - `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`;
    - `CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`;
    - `RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
   não devem mais ser usados como base normativa principal para novas decisões de implementação.
75. Havendo conflito entre qualquer documento histórico e este contrato mestre, prevalece este contrato mestre.

---

## 15. Definição operacional final do contrato mestre

76. O projeto deve ser interpretado, a partir da V179, como um motor diário conjunto de decisão financeira, auditável por lote, fonte, conta e pacote, ancorado no modelo matemático estatístico-financeiro oficial da V179.
77. Qualquer nova implementação central do projeto deve derivar diretamente deste contrato mestre e do modelo oficial V179.
78. Nenhuma nova camada central deve ser aberta com base em contratos históricos intermediários sem reconciliação explícita com a V179.

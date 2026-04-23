# Contrato operacional mestre do projeto `payment-investment-allocation` — V181

Este documento passa a ser o **documento mestre vigente** do projeto `payment-investment-allocation`.

Ele deve servir simultaneamente como:

- referência normativa principal do projeto nas conversas futuras;
- base metodológica e operacional para novas implementações;
- ponto único de entrada para leitura do estado atual do repositório;
- registro histórico condensado da evolução das baselines centrais até a V179/V180;
- camada de governança superior em relação ao modelo oficial, suplementos e documentos históricos.

A partir da V181, este contrato deixa de ser apenas um resumo curto das regras vigentes e passa a ser um **contrato mestre completo, atual e historicamente contextualizado**.

---

## 1. Finalidade e função normativa

### 1.1. Função normativa principal

Este contrato define o que deve ser considerado **vigente**, **obrigatório** e **interpretativamente prioritário** no projeto.

Sempre que houver dúvida entre documentos, implementações, versões antigas, relatórios intermediários ou heurísticas locais, a leitura correta deve começar por este contrato mestre.

### 1.2. Função histórica controlada

Este contrato também registra, no próprio corpo principal, as principais baselines históricas e sua função na evolução do projeto, para evitar regressões futuras e perda de contexto em outros chats.

### 1.3. Escopo normativo

Este contrato cobre:

- objetivo final do projeto;
- unidade de decisão do motor;
- regras de pagamento;
- regras de elegibilidade;
- regras de pós-vencimento;
- regras de switching;
- modelo econômico e critério terminal;
- validação diária user-facing;
- convenções de governança;
- hierarquia documental;
- lugar das baselines históricas.

---

## 2. Hierarquia documental vigente

A hierarquia documental do projeto passa a ser:

1. `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`  
   **Contrato mestre vigente**.
2. `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`  
   **Anexo metodológico oficial**, subordinado ao contrato mestre.
3. `relatorios/atuais/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md` e `relatorios/atuais/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`  
   **Suplementos vigentes**, subordinados ao contrato mestre e ao modelo oficial.
4. Auditorias e validações vigentes (`V175`, `V176`, `V177`, `V178` e posteriores)  
   **Camada de verificação e evidência**.
5. `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`  
   **Camada de backlog**, sem poder normativo principal.
6. Documentos históricos (como `V117`, `V108` e afins)  
   **Camada histórica preservada**, sem força normativa principal.

Quando houver conflito:

- prevalece este contrato mestre;
- depois, o modelo oficial;
- depois, os suplementos vigentes;
- depois, as auditorias e validações vigentes;
- por fim, o material histórico.

---

## 3. Baseline vigente e núcleo normativo atual

### 3.1. Baseline vigente

A baseline documental e metodológica vigente do projeto é a **V179**, consolidada e governada pela reescrita contratual da **V180** e pela ampliação histórica/documental da **V181**.

### 3.2. Núcleo normativo atual

O núcleo normativo atual do projeto é composto por:

- este `CONTRATO_OPERACIONAL_PROJETO.md`;
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`;
- `CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`;
- `CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`.

### 3.3. Interpretação correta do projeto

O projeto deve ser interpretado como um **motor conjunto diário de decisão financeira**, e não como uma coleção de heurísticas independentes de:

- pagamento;
- switching;
- recomputação;
- runner;
- auditoria;
- impressão de saída.

---

## 4. Linha histórica condensada das baselines centrais

Esta seção existe para manter o contrato mestre útil em outros chats sem depender de releitura de muitas conversas passadas.

### 4.1. Camada histórica antiga — V108

A V108 foi uma baseline importante para a frente central porque consolidou uma camada operacional relevante do motor, especialmente na evolução da recomputação e das decisões por pagamento.  
Ela permanece relevante como **marco histórico de estabilidade central**, mas **não** deve mais ser lida como referência normativa principal do projeto.

### 4.2. Camada contratual intermediária — V117

A V117 foi importante para formalizar o “motor conjunto temporal” e a relação entre:

- alocador de pagamentos terminal;
- planejador de switching temporal;
- simulador central;
- runner de análise.

Ela permanece relevante como **contrato intermediário histórico**, útil para rastrear a transição da arquitetura antiga para a arquitetura atual.  
No entanto, a V117 já não descreve completamente o modelo final aprovado e, portanto, não deve orientar novas implementações como norma principal.

### 4.3. Marco estrutural local — V174

A V174 consolidou o congelamento estrutural local da frente de switching dentro do simulador central.  
Ela é importante porque marca o ponto em que a reorganização local de baixo risco foi considerada suficientemente madura.

### 4.4. Marco de validação diária — V176 e V177

A V176 formalizou a validação diária orientada ao objetivo final e melhorou a auditabilidade das saídas.  
A V177 corrigiu dois pontos cruciais:

- materialização/auditabilidade pós-vencimento dos lotes críticos;
- gate de execução do switching promovível em dias sem pagamento.

### 4.5. Marco de reexecução com dados/cache atualizados — V178

A V178 confirmou que, após atualização do cache BCB e reexecução, o gargalo remanescente já não era mais a defasagem dos dados, mas sim a política decisória em dias com pagamento.

### 4.6. Marco metodológico oficial — V179

A V179 formalizou o **modelo matemático estatístico-financeiro oficial** do projeto.  
Esse é o marco metodológico principal atualmente vigente.

### 4.7. Marco contratual de hierarquia — V180

A V180 reescreveu o contrato operacional em formato de contrato mestre alinhado ao modelo oficial, rebaixando V117/V108 a contexto histórico.

### 4.8. Marco de ampliação histórica do contrato — V181

A V181 amplia o contrato mestre para que ele seja:

- completo;
- atual;
- historicamente contextualizado;
- e útil como referência principal em conversas futuras.

---

## 5. Objetivo final do projeto

O objetivo final do projeto é construir um **motor conjunto, diário, auditável e economicamente coerente** para decidir, em cada dia `t`, sobre:

- pagamentos obrigatórios do dia;
- uso de saldo disponível;
- uso de lotes aportados;
- uso de lotes vencidos e normalizados para disponibilidade;
- switching entre produtos;
- manutenção ou não ação.

A decisão do dia deve buscar **maximizar o patrimônio líquido terminal líquido**, respeitando simultaneamente:

- pagamento obrigatório das contas do dia;
- restrições de disponibilidade temporal;
- liquidez;
- carência;
- tributação;
- regras dos produtos;
- precedência intradiária do pacote escolhido;
- auditabilidade completa por lote, fonte, conta e pacote.

O projeto **não** tem como objetivo final otimizar isoladamente:

- uma única conta;
- um único lote;
- um único switching;
- uma única janela local desconectada do estado global do dia.

---

## 6. Unidade de decisão vigente

### 6.1. Unidade decisória

A unidade decisória oficial do projeto é o **dia `t`**.

### 6.2. Condição inicial do dia

Em cada dia `t`, o motor deve primeiro verificar se existem contas com vencimento no dia.

### 6.3. Pacotes factíveis

Se não houver contas no dia, os pacotes factíveis são apenas:

- `no_action`;
- `switch_only`.

Se houver contas no dia, os pacotes factíveis são apenas:

- `pay_only`;
- `switch_then_pay`;
- `pay_then_switch`.

### 6.4. Comparação no mesmo estado

A decisão do dia deve comparar os pacotes factíveis sobre o **mesmo estado econômico do dia**, usando:

- o mesmo critério terminal;
- a mesma governança de desempate;
- a mesma cronologia intradiária oficial.

---

## 7. Regras obrigatórias de pagamento

### 7.1. Data de pagamento

A data da planilha é a data correta de pagamento da conta.

### 7.2. Restrições duras de pagamento

O projeto não deve considerar:

- atraso de pagamento;
- antecipação de pagamento;
- não pagamento;
- pagamento parcial da conta.

### 7.3. Pagamento integral

Cada conta do dia deve ser paga **integralmente no próprio dia**.

### 7.4. Resolução conjunta das contas do dia

O pagamento do dia deve ser resolvido **conjuntamente** sobre o conjunto das contas com vencimento em `t`.

### 7.5. Regra operacional global do residual no pagamento do dia

O pagamento combinatório de uma ou mais contas do dia é permitido, mas deve obedecer à seguinte regra operacional global:

- se apenas uma fonte for usada no pagamento do dia, tudo certo;
- se múltiplas fontes forem usadas no pagamento do dia, então **no máximo uma** dessas fontes pode terminar a fase de pagamento com residual positivo;
- todas as demais fontes usadas devem zerar nessa fase.

Essa regra vale para o **conjunto dos pagamentos do dia**, e não por conta isolada.

### 7.6. Objetivo operacional da regra

O objetivo dessa regra é:

- evitar pulverização desnecessária de resíduos;
- preservar simplicidade operacional;
- reduzir fragmentação artificial de lotes;
- manter a decisão econômica compatível com o uso real dos recursos.

---

## 8. Elegibilidade prévia e pós-vencimento

### 8.1. Filtragem antes da otimização

O motor não deve começar diretamente do conjunto bruto de recursos como conjunto elegível.

Antes da otimização, o projeto deve derivar explicitamente:

- fontes elegíveis para pagamento;
- fontes elegíveis para switching.

### 8.2. Filtros obrigatórios

Uma fonte só pode entrar como elegível se passar pelos filtros de:

- disponibilidade temporal;
- liquidez/resgate;
- carência de retirada ou saída;
- regras operacionais do produto.

### 8.3. Regra de pós-vencimento

Se um lote venceu em `t` ou antes, ele deixa de ser tratado como lote aportado ativo e passa a ser tratado como **fonte disponível do dia**.

Se um lote vence depois de `t`, ele não pode ser tratado como disponível por vencimento.

### 8.4. Status normativo do pós-vencimento

O tratamento de pós-vencimento é parte do **estado econômico do dia** e não apenas uma camada de auditoria posterior.

---

## 9. Regras obrigatórias de switching

### 9.1. Formas permitidas

O projeto adota somente três formas de switching:

- **individual**;
- **agrupado combinatório**;
- **integral**.

### 9.2. Agrupado combinatório

O agrupado deve ser realmente combinatório, e não apenas junção simples ou heurística nominal de poucos casos fixos.

### 9.3. Integral

O integral deve ser interpretado como o **maior grupo factível elegível do pacote do dia**, após filtros de:

- disponibilidade;
- liquidez;
- carência;
- ticket;
- compatibilidade com o produto destino.

### 9.4. Limites por fonte

Uma mesma fonte não pode participar de mais de um switching no mesmo dia.

### 9.5. Pagamento e switching na mesma fonte

Uma mesma fonte pode:

- participar da fase de pagamento;
- e depois, com o residual, participar de um único switching.

### 9.6. Distinção entre pré e pós pagamento

No pacote `pay_then_switch`, o switching deve atuar sobre o residual pós-pagamento elegível.

No pacote `switch_then_pay`, o switching deve atuar sobre o conjunto elegível pré-pagamento.

A distinção entre pré-pagamento e pós-pagamento é obrigatória tanto na modelagem quanto na implementação.

---

## 10. Valoração, rendimento e critério econômico

### 10.1. Submodelo de rendimento e valoração

O projeto deve usar explicitamente o submodelo de rendimento e valoração dos lotes já validado no repositório e alinhado à saída do console.

### 10.2. Função contratual do submodelo de rendimento

Esse submodelo é parte do contrato vigente porque fornece, no mínimo:

- valor economicamente disponível da fonte no dia;
- valor terminal líquido de manter;
- valor terminal líquido dos grupos em switching;
- custo de oportunidade de usar a fonte em pagamento.

### 10.3. Critério econômico do pagamento

O critério econômico do pagamento **não** é “menor taxa nominal”.

O critério correto é usar a fonte ou combinação de fontes com **menor custo de oportunidade terminal líquido**, respeitando as restrições operacionais do pacote do dia.

### 10.4. Critério econômico do switching

O critério econômico do switching também deve ser comparado pelo efeito terminal líquido, e não por ganho local isolado.

---

## 11. Conservação de valor e residual mantido

### 11.1. Status normativo da conservação de valor

A conservação de valor faz parte do núcleo normativo do modelo.

### 11.2. Valor mantido

O termo de valor mantido deve permanecer no modelo, com interpretação de **residual final mantido ao fim do pacote**.

### 11.3. Residual no `pay_then_switch`

No pacote `pay_then_switch`, o switching atua integralmente sobre o residual elegível da fonte: o residual entra inteiro ou não entra.

### 11.4. Proibição de fracionamento livre do switching residual

O projeto não deve permitir fracionamento livre do switching sobre o residual.

### 11.5. Auditabilidade do residual

O residual final do pacote precisa permanecer auditável por lote/fonte.

---

## 12. Cronologia intradiária oficial

### 12.1. Regra geral

A cronologia intradiária do dia deve ser congelada e respeitada pela implementação.

### 12.2. Etapas iniciais comuns

Todo pacote do dia deve começar por:

- incorporar recebidos disponíveis no dia;
- normalizar lotes vencidos em `t`.

### 12.3. Ordem por pacote

Depois disso:

- `no_action` apenas mantém o estado;
- `switch_only` executa o switching vencedor e fecha o estado;
- `pay_only` paga integralmente as contas e fecha o estado;
- `switch_then_pay` executa switching, depois paga e então fecha o estado;
- `pay_then_switch` paga, depois executa switching sobre o residual e então fecha o estado.

### 12.4. Disponibilidade por etapa

Um recurso só pode ser usado em uma etapa se ele já existir economicamente naquela etapa.

---

## 13. Convenções de governança obrigatórias

O contrato congela quatro convenções de governança transversal:

- arredondamento;
- horizonte principal e sensibilidades;
- hierarquia de desempate;
- convenção intradiária de disponibilidade.

### 13.1. Arredondamento

O documento formal e a implementação devem congelar uma política uniforme de arredondamento monetário a centavos.

A política deve ser aplicada de forma consistente para:

- pagamentos;
- impostos;
- residuais;
- valores líquidos;
- comparação entre pacotes.

### 13.2. Horizonte principal e sensibilidades

O projeto deve operar com um **horizonte principal `H`** para a decisão base.

Sensibilidades adicionais devem ser tratadas como auditoria ou análise complementar, salvo regra explícita em contrário.

### 13.3. Hierarquia de desempate

Quando dois pacotes tiverem valor terminal praticamente equivalente, a decisão deve obedecer à seguinte hierarquia documental de desempate:

1. maior valor terminal líquido;
2. maior liquidez residual útil;
3. menor número de fontes usadas no pagamento do dia;
4. menor número de switchings executados;
5. menor complexidade operacional global.

### 13.4. Disponibilidade intradiária

Recursos incorporados em `t` entram no estado antes da decisão do pacote do dia.

Recursos só podem ser consumidos por uma etapa se já estiverem economicamente disponíveis naquela etapa.

---

## 14. Validação diária user-facing

Toda camada user-facing de validação diária deve ser compatível com:

- este contrato mestre;
- o modelo oficial V179;
- os suplementos vigentes.

Não deve ser aceita saída diária que:

- oculte os componentes reais do pagamento vencedor;
- oculte as fontes candidatas do pagamento;
- oculte as ações e cenários de switching do dia;
- apresente lotes futuros ou ilíquidos como elegíveis antes da hora;
- apresente inconsistência entre decisão econômica, execução e monitoramento do estado.

A validação diária permanece subordinada aos contratos suplementares vigentes (`V176` e `V177`), mas esses contratos suplementares não substituem o núcleo deste contrato mestre.

---

## 15. Governança do repositório

O repositório-base oficial é `payment-investment-allocation`.

Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial.

O `.zip` deve abrir sem pasta interna raiz, com arquivos e pastas diretamente na raiz do pacote.

Todo o projeto deve permanecer em português.

Antes de cada entrega, a etapa implementada deve ser executada e validada localmente no ambiente disponível.

A checagem de release em `scripts/diagnostico/verificar_release_baseline.py` permanece gate obrigatório antes das entregas.

O pacote final não deve incluir artefatos efêmeros como `__pycache__`, `.pyc`, logs brutos auxiliares, caches não oficiais e saídas redundantes temporárias.

O índice oficial de navegação documental é `relatorios/INDICE_RELATORIOS.md`.

---

## 16. Leitura histórica preservada

### 16.1. Status dos documentos históricos

Os documentos V117 e V108 deixam de ser referência normativa principal do projeto.

Eles permanecem preservados por rastreabilidade histórica, contextual e arquitetural.

### 16.2. Função dos históricos preservados

Esses documentos devem ser lidos apenas como:

- contexto intermediário de evolução do motor;
- registro de baselines históricas;
- material de comparação para auditorias de regressão;
- apoio para entender decisões antigas já superadas.

### 16.3. Documentos explicitamente rebaixados

São explicitamente rebaixados a contexto histórico:

- `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`;
- `CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`;
- `RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`.

---

## 17. Relação entre contrato mestre e modelo oficial

O documento `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md` permanece como **anexo metodológico normativo** deste contrato.

A leitura correta é:

- este contrato define o que é vigente, obrigatório e interpretativamente prioritário;
- o modelo oficial define a formulação matemática e econômico-financeira detalhada que implementa esse contrato.

Se houver divergência aparente entre formulação e governança, prevalece a interpretação definida por este contrato mestre.

---

## 18. Status final da V181

A V181 passa a representar:

- o contrato mestre completo do projeto;
- a referência principal para próximos chats;
- a base documental final antes da derivação da especificação operacional de `resolver_dia(t, E_t)`;
- o ponto único de entrada para leitura do estado normativo e histórico do repositório.


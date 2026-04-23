# CONTRATO OPERACIONAL MESTRE DO PROJETO `payment-investment-allocation` — V183

## 1. Status, função e baseline única

### 1.1. Documento mestre vigente
Este documento é o **Contrato Operacional Mestre vigente** do projeto `payment-investment-allocation`.

### 1.2. Baseline única vigente
A **baseline única vigente** do projeto é a **V183**.

A V183 deve ser tratada simultaneamente como:

- baseline contratual vigente;
- baseline metodológica vigente;
- baseline operacional de referência vigente.

### 1.3. Estrutura normativa da baseline única
Dentro da baseline única V183:

- este contrato é o **documento normativo superior**;
- o arquivo `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md` é o **anexo metodológico vinculante** do projeto;
- implementações, relatórios, runners, auditorias, saídas operacionais e documentos históricos não têm prevalência sobre este contrato nem sobre o anexo metodológico vinculante.

### 1.4. Regra de prevalência
Em caso de divergência entre:

- implementação;
- relatório;
- saída de runner;
- heurística local;
- documento histórico;
- interpretação de conversa anterior;
- output de console;
- arquivo intermediário;

**prevalece este contrato mestre**.

Para formulação matemática, econômica e estatística detalhada, a leitura correta é conjunta:

- este contrato mestre como norma superior;
- o anexo metodológico vinculante como formulação detalhada.

### 1.5. Cláusula de estabilização
O núcleo lógico, econômico e matemático definido por este contrato e por seu anexo metodológico vinculante é tratado como **estabilizado**.

É vedado reabrir sua estrutura em conversas futuras ou em implementações novas sem justificativa explícita de revisão contratual.

---

## 2. Nome canônico e localização dos documentos

### 2.1. Contrato canônico
O arquivo canônico do contrato mestre no repositório é:

`relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`

### 2.2. Anexo metodológico vinculante
O arquivo metodológico vinculante do projeto é:

`relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`

### 2.3. Artefatos versionados
Arquivos com nomes versionados, como exportações, cópias de revisão ou arquivos de congelamento, devem ser tratados apenas como artefatos de:

- exportação;
- revisão;
- auditoria;
- distribuição.

Eles não substituem os arquivos canônicos internos do repositório.

---

## 3. Hierarquia documental vigente

A hierarquia documental vigente do projeto é:

1. `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`  
   **Contrato mestre normativo superior**.
2. `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`  
   **Anexo metodológico vinculante**.
3. Suplementos históricos de validação e auditoria  
   **Documentos auxiliares relevantes, sem prevalência normativa superior**.
4. Auditorias, reexecuções e validações vigentes  
   **Camada de evidência e verificação**.
5. Backlogs e documentos de fases futuras  
   **Camada de planejamento, sem força normativa principal**.
6. Documentos históricos intermediários e antigos  
   **Camada histórica preservada**.

Quando houver conflito:

- prevalece o contrato mestre;
- depois, o anexo metodológico vinculante;
- depois, a evidência de auditoria mais recente compatível com ambos;
- por fim, os documentos históricos.

---

## 4. Status dos documentos anteriores

### 4.1. Documentos históricos preservados
Documentos anteriores são preservados para:

- rastreabilidade;
- auditoria de regressão;
- comparação metodológica;
- compreensão da evolução do projeto.

### 4.2. Sem autonomia normativa
É vedado tratar documentos anteriores como normas autônomas diante da V183.

### 4.3. V176 e V177
Os documentos V176 e V177 permanecem como **suplementos históricos de validação e auditoria**, úteis para:

- rastreabilidade da validação diária;
- correções de pós-vencimento;
- correções de gate de switching;
- comparação de regressão.

Eles não prevalecem sobre este contrato nem sobre o anexo metodológico vinculante.

### 4.4. V117 e V108
Os documentos V117 e V108 permanecem como **histórico útil para auditoria e comparação de regressão**, sem força normativa principal.

---

## 5. Objetivo final do projeto

O objetivo final do projeto é construir um **motor conjunto, diário, auditável e economicamente coerente** que decida, em cada dia \(t\), sobre:

- pagamento das contas do dia;
- uso de saldo disponível;
- uso de lotes aportados;
- uso de lotes vencidos já normalizados;
- switching entre produtos;
- manutenção ou não ação;

com o objetivo de **maximizar o patrimônio líquido terminal líquido** no horizonte principal vigente.

O projeto deve respeitar simultaneamente:

- pagamento obrigatório das contas do dia;
- disponibilidade temporal real;
- liquidez;
- carência;
- tributação;
- regras dos produtos;
- cronologia intradiária do pacote escolhido;
- auditabilidade por lote, fonte, conta, grupo, produto e pacote.

É vedado interpretar o projeto como:

- otimizador isolado de conta;
- planejador de switching separado do estado do dia;
- heurística local sem núcleo econômico;
- runner de auditoria sem função decisória conjunta.

---

## 6. Definições normativas

Para este contrato, os termos abaixo têm significado fixo.

### 6.1. Fonte
É qualquer recurso economicamente utilizável no dia, incluindo:

- saldo disponível geral;
- recebido disponível;
- lote aportado elegível;
- lote vencido já normalizado.

### 6.2. Lote
É a unidade financeira rastreável com identidade própria, histórico, custo fiscal, regras de rendimento e regras de disponibilidade.

### 6.3. Residual
É o valor remanescente de uma fonte ao fim de uma fase ou de um pacote do dia.

### 6.4. Pacote do dia
É a estrutura decisória completa do dia \(t\), dentre os pacotes permitidos por este contrato.

### 6.5. Grupo factível de switching
É o subconjunto de fontes elegíveis que pode ser migrado conjuntamente para um produto destino, respeitando todas as restrições do dia.

### 6.6. Horizonte principal
É o horizonte \(H\) oficialmente adotado para a decisão-base do motor.

### 6.7. Sensibilidade
É análise complementar em horizonte alternativo, sem substituir a decisão-base, salvo regra explícita em contrário.

### 6.8. Saldo disponível geral
Para fins contratuais, o saldo disponível geral é tratado como **uma única fonte lógica**, salvo se o projeto vier a formalizar explicitamente múltiplos saldos operacionais independentes.

### 6.9. Carteira ranqueada oficial
É a carteira resultante da aplicação do módulo oficial de ranking da aba `Carteira`, usada como base obrigatória de priorização de destinos elegíveis.

---

## 7. Unidade oficial de decisão

### 7.1. Unidade temporal
A unidade oficial de decisão do projeto é o **dia \(t\)**.

### 7.2. Condição inicial do dia
Em cada dia \(t\), é obrigatório verificar primeiro se existem contas com vencimento em \(t\).

Defina:

\[
\mathbb I_t^{pay}=
egin{cases}
1, & 	ext{se existe pelo menos uma conta com vencimento em } t \
0, & 	ext{caso contrário}
\end{cases}
\]

com

\[
\mathcal J_t=\{j:	ext{data da conta }j=t\}
\]

### 7.3. Pacotes factíveis
Se \(\mathbb I_t^{pay}=0\), os pacotes factíveis são:

- `no_action`;
- `switch_only`.

Se \(\mathbb I_t^{pay}=1\), os pacotes factíveis são:

- `pay_only`;
- `switch_then_pay`;
- `pay_then_switch`.

### 7.4. Comparação no mesmo estado
É obrigatório comparar os pacotes factíveis sobre o **mesmo estado econômico inicial do dia**, respeitando:

- a mesma valoração;
- a mesma cronologia intradiária;
- a mesma regra de desempate;
- o mesmo horizonte principal.

---

## 8. Regras obrigatórias de pagamento

### 8.1. Data correta
É obrigatório pagar cada conta na data da planilha.

### 8.2. Restrições duras
É vedado considerar:

- atraso;
- antecipação;
- não pagamento;
- pagamento parcial da conta.

### 8.3. Pagamento integral
É obrigatório pagar integralmente cada conta do dia.

### 8.4. Resolução conjunta do dia
É obrigatório resolver o pagamento sobre o **conjunto das contas do dia**, e não conta por conta de forma isolada.

---

## 9. Regra global do residual no pagamento do dia

### 9.1. Regra principal
Se apenas uma fonte for usada no pagamento do dia, não há restrição adicional de residual.

Se múltiplas fontes forem usadas no pagamento do dia, então:

> **no máximo uma** das fontes usadas pode terminar a fase de pagamento com residual positivo.

Todas as demais fontes usadas nessa fase devem zerar.

### 9.2. Escopo
Essa regra vale para o **conjunto dos pagamentos do dia**, e não por conta isolada.

### 9.3. Saldo disponível geral
O saldo disponível geral conta como fonte para essa regra e está sujeito à mesma restrição.

### 9.4. Finalidade
Essa regra existe para:

- evitar pulverização de resíduos;
- simplificar o pagamento do dia;
- reduzir fragmentação artificial de fontes;
- manter operacionalidade coerente com o objetivo econômico.

---

## 10. Universo bruto e elegibilidade prévia

### 10.1. Universo bruto
É obrigatório iniciar de um universo bruto de recursos observáveis no dia, incluindo:

- saldo disponível;
- recebidos disponíveis;
- lotes aportados;
- lotes vencidos;
- lotes futuros;
- demais recursos presentes no estado.

### 10.2. Filtragem prévia
Antes da otimização, é obrigatório derivar explicitamente:

- fontes elegíveis para pagamento;
- fontes elegíveis para switching.

### 10.3. Filtros obrigatórios
Uma fonte só pode ser tratada como elegível se passar por:

- disponibilidade temporal;
- liquidez/resgate;
- carência de retirada ou saída;
- regra operacional do produto;
- restrições específicas aplicáveis.

---

## 11. Regra de pós-vencimento

### 11.1. Regra principal
Se um lote venceu em \(t\) ou antes, ele deixa de ser lote aportado ativo e passa a ser **fonte disponível do dia**.

Formalmente:

\[
m_i \le t \Rightarrow 	ext{fonte disponível do dia}
\]

### 11.2. Regra negativa
É vedado tratar lote com vencimento posterior a \(t\) como disponível por vencimento.

### 11.3. Status normativo
O pós-vencimento é parte do **estado econômico oficial do dia** e não mera camada de auditoria.

---

## 12. Regras obrigatórias de switching

### 12.1. Formas permitidas
É permitido apenas switching nas formas:

- **individual**;
- **agrupado combinatório**;
- **integral**.

### 12.2. Agrupado combinatório
É obrigatório que o agrupado seja realmente combinatório e baseado em grupos factíveis.

### 12.3. Switching integral
Switching integral é o switching do **maior grupo factível elegível para um produto destino específico dentro do pacote do dia**, após filtros de:

- disponibilidade;
- liquidez;
- carência;
- ticket;
- compatibilidade com o produto destino.

### 12.4. Limite por fonte
É vedado que uma fonte participe de mais de um switching no mesmo dia.

### 12.5. Convivência com pagamento
É permitido que uma fonte participe do pagamento e depois, com residual elegível, participe de um único switching.

---

## 13. Distinção obrigatória entre switching pré e pós pagamento

### 13.1. `switch_then_pay`
No pacote `switch_then_pay`, o switching atua sobre o conjunto elegível **pré-pagamento**.

### 13.2. `pay_then_switch`
No pacote `pay_then_switch`, o switching atua sobre o **estado pós-pagamento do dia**, incluindo:

- resíduos das fontes usadas no pagamento;
- fontes elegíveis não utilizadas nessa fase;

salvo restrição explícita em contrário.

Esse estado pós-pagamento deve ser entendido como o conjunto efetivamente remanescente e elegível após a liquidação integral das contas do dia.

### 13.3. Obrigatoriedade
É obrigatório manter essa distinção:

- na formulação;
- na implementação;
- na auditoria;
- na saída diária.

---

## 14. Valoração, rendimento e critério econômico

### 14.1. Submodelo de rendimento obrigatório
É obrigatório usar o submodelo de rendimento e valoração já validado no projeto e alinhado à lógica da saída do console.

### 14.2. Função normativa do submodelo
Esse submodelo fornece, no mínimo:

- valor economicamente disponível da fonte no dia;
- valor terminal líquido de manter;
- valor terminal líquido dos grupos em switching;
- custo de oportunidade do pagamento;
- base econômica para comparação de pacotes.

### 14.3. Critério econômico do pagamento
É obrigatório escolher a fonte ou combinação de fontes pelo **menor custo de oportunidade terminal líquido**, respeitando as restrições operacionais do pacote.

É vedado usar “menor taxa nominal” como critério contratual principal.

### 14.4. Critério econômico do switching
É obrigatório comparar switching pelo efeito terminal líquido, e não por ganho local isolado.

---

## 14-A. Camada oficial de ranqueamento da carteira

### 14-A.1. Natureza
O projeto incorpora uma **camada oficial de ranqueamento da carteira** como **módulo auxiliar vinculante de priorização de destinos**.

### 14-A.2. Função obrigatória
É obrigatório que essa camada:

- produza o ranqueamento oficial dos produtos da aba `Carteira`;
- defina o conjunto priorizado de produtos destino elegíveis para switching;
- alimente a priorização dos destinos considerados pelo motor diário;
- permaneça coerente com os artefatos oficiais exportados para validação.

### 14-A.3. Relação com o motor diário
É obrigatório que o motor diário trate o ranqueamento da carteira como base oficial de priorização do universo de destinos.

É vedado selecionar destinos de switching de forma desconectada da camada oficial de ranqueamento da carteira, salvo justificativa operacional explícita, auditável e compatível com este contrato.

### 14-A.4. Papel metodológico
Essa camada:

- **não substitui** o motor diário de decisão;
- **não substitui** o comparador de pacotes do dia;
- **não substitui** o objetivo terminal do projeto.

Seu papel é:

- priorizar destinos;
- estruturar a leitura oficial da carteira;
- apoiar a triagem de produtos elegíveis;
- reforçar a auditabilidade da decisão.

### 14-A.5. Relação com a aba `Carteira`
A aba **Carteira** do arquivo final oficial deve refletir a **carteira ranqueada oficial do projeto**, incluindo, no mínimo:

- score;
- ranking;
- elegibilidade;
- informações relevantes para priorização de destinos;
- informações relevantes para validação manual.

---

## 15. Conservação de valor e residual mantido

### 15.1. Conservação de valor
A conservação de valor integra o núcleo normativo do projeto.

### 15.2. Valor mantido
O termo de valor mantido é obrigatório e representa o **residual final mantido** ao fim do pacote.

### 15.3. Residual no `pay_then_switch`
No pacote `pay_then_switch`, o switching atua integralmente sobre o residual elegível:

- o residual entra inteiro;
- ou não entra.

### 15.4. Vedação ao fracionamento livre
É vedado fracionar livremente o switching sobre o residual.

### 15.5. Auditabilidade
É obrigatório manter auditabilidade do residual final por lote e por fonte.

---

## 16. Cronologia intradiária oficial

### 16.1. Regra geral
A cronologia intradiária do dia fica **normativamente congelada**.

### 16.2. Ordem inicial comum
Todo pacote do dia deve começar nesta ordem obrigatória:

1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\).

### 16.3. Ordem por pacote

#### `no_action`
3. manter o estado.

#### `switch_only`
3. executar o switching vencedor;  
4. fechar o estado do dia.

#### `pay_only`
3. pagar integralmente as contas do dia;  
4. fechar o estado do dia.

#### `switch_then_pay`
3. executar switching sobre o conjunto pré-pagamento;  
4. pagar integralmente as contas do dia no estado pós-switching;  
5. fechar o estado do dia.

#### `pay_then_switch`
3. pagar integralmente as contas do dia;  
4. construir o estado pós-pagamento;  
5. executar switching sobre o estado pós-pagamento;  
6. fechar o estado do dia.

### 16.4. Disponibilidade por etapa
É vedado usar recurso em etapa na qual ele ainda não exista economicamente.

---

## 17. Convenções de governança obrigatórias

### 17.1. Arredondamento
Fica congelada a seguinte política oficial:

- arredondamento monetário a centavos;
- arredondamento decimal **half-up**;
- aplicação consistente em:
  - pagamentos,
  - impostos,
  - valores líquidos,
  - residuais,
  - comparação econômica final.

É permitido usar maior precisão intermediária internamente, desde que a camada contratual e auditável feche em centavos com half-up.

### 17.2. Horizonte principal e sensibilidades
O projeto opera com um **horizonte principal \(H\)** para a decisão-base.

Sensibilidades:

- são permitidas;
- são complementares;
- não substituem a decisão-base;
- salvo regra explícita em contrário.

### 17.3. Hierarquia de desempate
Quando dois pacotes forem praticamente equivalentes, isto é:

\[
|Z_t^{(k_1)} - Z_t^{(k_2)}| \le arepsilon
\]

com \(arepsilon\) definido no `config` vigente como **parâmetro contratualmente único por baseline e auditável**, a decisão deve obedecer à seguinte ordem:

1. maior valor terminal líquido;
2. maior liquidez residual útil;
3. menor número de fontes usadas no pagamento do dia;
4. menor número de switchings executados;
5. menor complexidade operacional global.

### 17.4. Disponibilidade intradiária
Recursos incorporados em \(t\) entram no estado antes da decisão do pacote.

Recursos só podem ser consumidos por uma etapa se estiverem economicamente disponíveis naquela etapa.

---

## 18. Validação diária user-facing

A camada user-facing de validação diária deve ser compatível com:

- este contrato mestre;
- o anexo metodológico vinculante;
- a baseline única vigente.

É vedado aceitar saída diária que:

- oculte os componentes reais do pagamento vencedor;
- oculte as fontes candidatas do pagamento;
- oculte candidatos e cenários de switching;
- apresente lotes futuros ou ilíquidos como elegíveis antes da hora;
- apresente inconsistência entre decisão, execução e monitoramento do estado.

---

## 19. Governança das saídas operacionais, console e arquivos gerados

### 19.1. Princípio geral
As saídas operacionais do projeto devem ser:

- auditáveis;
- não redundantes;
- não duplicadas sem função;
- legíveis para validação humana;
- consistentes com a baseline vigente;
- estratificadas por finalidade.

É vedado gerar múltiplas saídas que repitam a mesma informação sem diferença clara de propósito.

### 19.2. Regra de não redundância
Cada camada de saída deve ter uma função principal única.

É vedado que:

- console;
- markdown;
- json;
- excel;
- logs auxiliares;

repitam o mesmo conteúdo no mesmo nível de detalhe sem justificativa operacional explícita.

Quando duas saídas coexistirem, deve ser possível identificar claramente:

- qual é a saída resumida;
- qual é a saída detalhada;
- qual é a saída oficial de auditoria;
- qual é apenas apoio diagnóstico.

### 19.3. Função do console
O console é a **camada de leitura operacional rápida**.

É obrigatório que o console priorize:

- data de referência e janela analisada;
- origem dos dados e status da obtenção;
- pagamentos do dia;
- componentes reais do pagamento;
- pacote vencedor do dia;
- switching promovido e/ou executado;
- lotes críticos monitorados;
- mensagens essenciais de validação.

É vedado usar o console como despejo bruto de estruturas extensas, repetitivas ou de baixa utilidade para leitura humana.

### 19.4. Função do markdown
O markdown é a **camada de auditoria humana estruturada**.

É obrigatório que o markdown:

- resuma a execução;
- organize os dias auditados;
- destaque decisões vencedoras;
- preserve rastreabilidade textual de lotes, contas, grupos e produtos.

### 19.5. Função do JSON
O JSON é a **camada detalhada, estruturada e machine-readable**.

É permitido que o JSON tenha maior detalhamento do que o console e o markdown, desde que:

- seja coerente com eles;
- não os contradiga;
- não substitua a necessidade de resumo humano.

### 19.6. Arquivo final oficial para validação e manipulação
É obrigatório gerar um **arquivo final em formato `.xlsx`** nas **execuções oficiais de validação, auditoria e entrega**, para facilitar:

- manipulação;
- leitura;
- auditoria;
- validação manual.

Em microexecuções internas de teste, o `.xlsx` pode ser dispensado, desde que isso não comprometa a auditabilidade da etapa.

### 19.7. Abas obrigatórias do arquivo `.xlsx`
O arquivo final `.xlsx` deve conter, no mínimo, as seguintes abas, com esta grafia, salvo revisão contratual explícita:

- **Extrato Passado**
- **Extrato Futuro**
- **Switching**
- **Carteira**
- **Situação Atual**

É vedado consolidar essas camadas em uma única aba quando isso prejudicar legibilidade, validação ou rastreabilidade.

### 19.8. Função das abas obrigatórias
As abas devem servir, respectivamente, para:

- **Extrato Passado**: rastrear e validar eventos e movimentos já ocorridos;
- **Extrato Futuro**: rastrear e validar projeções e decisões à frente;
- **Switching**: explicitar candidatos, decisões, grupos e resultados de switching;
- **Carteira**: refletir a carteira oficial ranqueada do projeto, incluindo score, ranking, elegibilidade e informações relevantes para priorização de destinos de switching e validação manual;
- **Situação Atual**: resumir o estado operacional presente para leitura rápida e conferência.

### 19.9. Arquivos auxiliares
Logs, diagnósticos e arquivos auxiliares só devem ser gerados quando tiverem função clara de:

- auditoria de regressão;
- depuração controlada;
- validação metodológica;
- checagem de release.

É vedado promover arquivos auxiliares ao mesmo status de artefatos oficiais sem necessidade contratual explícita.

### 19.10. Regra de unicidade informacional
Cada informação essencial do projeto deve possuir uma camada principal de referência:

- leitura rápida → console;
- leitura auditável humana → markdown;
- leitura estruturada completa → json;
- manipulação e validação operacional → `.xlsx`;
- regra e norma → contrato mestre e anexo metodológico vinculante.

É vedado deixar informação crítica espalhada sem camada principal identificável.

### 19.11. Regra de legibilidade
As saídas oficiais devem favorecer:

- validação humana rápida;
- comparação entre dias;
- comparação entre pacotes;
- identificação explícita de lotes, contas, produtos e grupos;
- interpretação econômica direta.

É vedado priorizar completude bruta às custas da legibilidade operacional.

---

## 20. Governança do repositório

### 20.1. Repositório oficial
O repositório-base oficial é `payment-investment-allocation`.

### 20.2. Entrega e versionamento
Cada atualização deve ser entregue como repositório completo em `.zip`, com versionamento sequencial.

### 20.3. Estrutura do `.zip`
O `.zip` deve abrir sem pasta interna raiz, com os arquivos e pastas diretamente na raiz.

### 20.4. Idioma
É obrigatório manter o projeto em português.

### 20.5. Validação pré-entrega
É obrigatório executar e validar localmente a etapa implementada antes de cada entrega.

### 20.6. Gate de release
A checagem de release permanece gate obrigatório.

### 20.7. Artefatos efêmeros
É vedado incluir no pacote final artefatos efêmeros como:

- `__pycache__`
- `.pyc`
- logs auxiliares temporários
- caches não oficiais
- saídas redundantes não oficiais

### 20.8. Índice oficial
O índice oficial de navegação documental é `relatorios/INDICE_RELATORIOS.md`.

---

## 21. Histórico preservado

### 21.1. Status
Documentos históricos permanecem preservados, sem força normativa autônoma.

### 21.2. Uso permitido
Eles servem para:

- rastreabilidade;
- auditoria de regressão;
- compreensão da evolução do projeto;
- comparação metodológica histórica.

### 21.3. Exemplos
São históricos preservados, entre outros:

- contratos V117;
- referências V108;
- suplementos V176 e V177;
- demais documentos intermediários superados pela baseline única vigente.

---

## 22. Relação entre contrato mestre e modelo metodológico

O arquivo `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md` permanece como **anexo metodológico vinculante** do projeto.

A leitura correta é:

- este contrato define a norma superior;
- o anexo metodológico detalha a formulação matemática, econômica e estatística vinculada a esta norma;
- ambos coexistem dentro da baseline única V183, sem competição normativa entre si.

---

## 23. Status final da V183

A V183 representa a baseline única vigente do projeto e a referência principal para sua continuidade contratual, metodológica e operacional.

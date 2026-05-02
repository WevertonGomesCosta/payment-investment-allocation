# MODELO MATEMÁTICO ESTATÍSTICO-FINANCEIRO FINAL DO PROJETO `payment-investment-allocation`

## 1. Natureza do modelo

O projeto adota um **modelo diário, estático, conjunto e condicionado ao estado observado no dia \(t\)**.

Em cada dia \(t\), o modelo:

1. verifica se existem contas com vencimento em \(t\);
2. deriva, a partir do universo bruto de recursos, as fontes elegíveis para pagamento e para switching;
3. atualiza e valora economicamente cada lote/fonte disponível;
4. constrói e compara os pacotes factíveis do dia;
5. escolhe o pacote que maximiza o **patrimônio líquido terminal líquido** no horizonte principal \(H\).

O modelo é:

- **matemático**, por ser um problema de otimização com restrições;
- **financeiro**, por incorporar retorno, fiscalidade, liquidez, carência, vencimento e custo de oportunidade;
- **estatístico**, porque os parâmetros terminais, penalizações, proxies e fatores econômicos são parametrizados a partir do estado observado e das regras dos produtos.

---

## 2. Objetivo central

O objetivo central do modelo é:

\[
\max \; \text{Patrimônio Líquido Terminal Líquido}
\]

respeitando simultaneamente:

- pagamento obrigatório e integral das contas do dia;
- disponibilidade temporal real dos recursos;
- liquidez;
- carência;
- fiscalidade;
- regras dos produtos;
- cronologia intradiária do pacote escolhido;
- auditabilidade por lote, fonte, conta, grupo, produto e pacote.

---

## 3. Estrutura lógica do dia \(t\)

### 3.1. Condição inicial: existência de contas no dia

Defina:

\[
\mathbb I_t^{pay}=
\begin{cases}
1, & \text{se existe pelo menos uma conta com vencimento em } t \\
0, & \text{caso contrário}
\end{cases}
\]

com

\[
\mathcal J_t=\{j:\text{data da conta }j=t\}
\]

Então:

- se \(\mathbb I_t^{pay}=0\), o dia é sem pagamento;
- se \(\mathbb I_t^{pay}=1\), o dia é com pagamento obrigatório.

Essa verificação entra **antes** de qualquer resolução detalhada.

### 3.2. Pacotes factíveis do dia

Se \(\mathbb I_t^{pay}=0\):

\[
\mathcal K_t=
\{\text{no\_action},\text{switch\_only}\}
\]

Se \(\mathbb I_t^{pay}=1\):

\[
\mathcal K_t=
\{\text{pay\_only},\text{switch\_then\_pay},\text{pay\_then\_switch}\}
\]

A decisão ótima do dia é:

\[
k_t^\star=\arg\max_{k\in\mathcal K_t} Z_t^{(k)}
\]

Cada pacote decisório deve ser entendido como uma **trajetória completa de transição de estado**, e não como uma decisão local isolada.

A decisão ótima compara trajetórias completas derivadas do mesmo estado inicial do dia.

---

## 3-A. Parâmetros operacionais oficiais

Além dos parâmetros econômicos e fiscais do modelo, a configuração operacional oficial incorpora parâmetros operacionais explícitos que condicionam interpretação, auditoria e execução do motor.

Defina:

- \(\delta_{res}=0{,}20\): limiar operacional de resíduo resolvido por lote;
- \(\delta_{ativo}=0{,}20\): valor mínimo para considerar um lote residual como ativo para fins operacionais;
- \(\delta_{mon}=0{,}01\): tolerância monetária fina para comparações e cobertura.

### 3-A.1. Interpretação do limiar de resíduo resolvido

Um lote com valor residual monetário \(R_i\), após arredondamento oficial do projeto, é tratado como **resolvido/zerado operacionalmente** quando:

\[
R_i \le \delta_{res}
\]

com, na configuração operacional oficial:

\[
\delta_{res}=0{,}20
\]

### 3-A.2. Interpretação do valor mínimo de lote ativo

Um lote residual só deve permanecer como lote ativo relevante para fins operacionais quando:

\[
R_i > \delta_{ativo}
\]

com, na configuração operacional oficial:

\[
\delta_{ativo}=0{,}20
\]

### 3-A.3. Interpretação da tolerância monetária fina

A tolerância monetária fina do modelo é usada para verificações estritas de cobertura, comparação e consistência local:

\[
\delta_{mon}=0{,}01
\]

Ela **não substitui** o limiar operacional de resíduo resolvido; ambos têm funções distintas.

---

## 4. Estado econômico do dia

Defina o estado inicial do dia \(t\) como:

\[
\mathcal E_t=(\mathcal U_t,\mathcal J_t,\mathcal P_t,\Theta_t)
\]

onde:

- \(\mathcal U_t\): universo bruto de recursos observáveis no dia;
- \(\mathcal J_t\): conjunto de contas com vencimento em \(t\);
- \(\mathcal P_t\): conjunto de produtos destino elegíveis;
- \(\Theta_t\): parâmetros econômicos, fiscais, operacionais e de rendimento do dia.

---

## 4-A. Estado temporal conjunto

Defina o estado econômico-financeiro intradiário como:

\[
S_{t,r}
\]

em que \(t\) é a data e \(r\) é a etapa intradiária.

O estado \(S_{t,r}\) contém, no mínimo:

- fontes disponíveis;
- lotes ativos;
- lotes bloqueados;
- lotes migrados;
- lotes sintéticos pós-switching;
- recebidos disponíveis;
- pagamentos pendentes;
- pagamentos liquidados;
- saldos residuais;
- restrições operacionais vigentes.

Pagamentos e switchings devem ser resolvidos sobre o mesmo estado temporal conjunto.

É vedado que pagamentos e switchings sejam calculados em trilhas independentes e reconciliados posteriormente em camada de saída.

---

## 4-B. Pacotes como trajetórias de transição

Cada pacote \(k\) define uma sequência ordenada de transições:

\[
S_{t,0} \rightarrow S_{t,1}^{(k)} \rightarrow \cdots \rightarrow S_{t,R_k}^{(k)}
\]

A decisão ótima deve ser escolhida pela comparação entre trajetórias completas:

\[
k_t^\star = \arg\max_{k \in \mathcal K_t} Z\left(S_{t,R_k}^{(k)}\right)
\]

sujeita às restrições de liquidez, carência, disponibilidade temporal, cobertura integral dos pagamentos, conservação de valor, fiscalidade, risco, penalizações e auditabilidade.

---

## 4-C. Ledger canônico do motor

O motor deve produzir um ledger canônico \(L_t^{(k)}\) para cada pacote viável \(k\):

\[
L_t^{(k)} = ledger\left(S_{t,0}, k\right)
\]

Esse ledger registra eventos materializados, fontes consumidas, switchings efetivados, lotes criados, saldos antes/depois, impostos, liquidez, bloqueios e impacto terminal.

As saídas operacionais são renderizações do ledger do pacote escolhido:

\[
Output_t = render\left(L_t^{(k_t^\star)}\right)
\]

A saída operacional não é uma nova otimização, reconciliação ou correção decisória.

---

## 5. Universo bruto e filtragem operacional

### 5.1. Universo bruto de recursos

\[
\mathcal U_t
\]

inclui, entre outros:

- saldo disponível geral;
- recebidos já disponíveis;
- lotes aportados;
- lotes vencidos;
- lotes futuros ainda indisponíveis;
- demais recursos financeiros presentes no estado.

### 5.2. Fontes elegíveis para pagamento

Antes da otimização, o modelo deriva:

\[
\mathcal S_t^{pay}=
\{i\in\mathcal U_t: A_i^{pay}(t)=1\}
\]

onde \(A_i^{pay}(t)=1\) apenas se a fonte for:

- temporalmente disponível no dia;
- elegível por liquidez/resgate;
- elegível por carência de retirada;
- compatível com a regra operacional do produto.

Formalmente:

\[
A_i^{pay}(t)=1
\iff
\text{disponibilidade temporal}
\land
\text{liquidez/resgate}
\land
\text{carência de retirada satisfeita}
\land
\text{regra operacional satisfeita}
\]

### 5.3. Fontes elegíveis para switching antes do pagamento

O modelo também deriva:

\[
\mathcal S_{t,\mathrm{pre}}^{sw}=
\{i\in\mathcal U_t: A_i^{sw}(t)=1\}
\]

onde \(A_i^{sw}(t)=1\) apenas se a fonte for:

- disponível para movimentação no dia;
- elegível por liquidez de saída;
- elegível por carência de saída;
- compatível com switching na regra do produto.

Formalmente:

\[
A_i^{sw}(t)=1
\iff
\text{disponibilidade temporal}
\land
\text{elegibilidade para movimentação}
\land
\text{carência de saída satisfeita}
\land
\text{regra de switching satisfeita}
\]

---

## 6. Regra de pós-vencimento

A regra correta de pós-vencimento é:

\[
m_i \le t
\;\Rightarrow\;
i \text{ deixa de ser lote aportado ativo e passa a ser fonte disponível do dia}
\]

Logo:

- se \(m_i \le t\), a fonte entra como disponível no dia;
- se \(m_i > t\), ela não entra por vencimento.

O pós-vencimento é parte do **estado econômico oficial do dia** e não apenas uma camada de auditoria posterior.

---

## 7. Submodelo de rendimento e valoração dos lotes

Este submodelo integra formalmente o modelo final.

### 7.1. Valor bruto do lote

Para cada lote \(i\), seja \(V_i^{br}(d)\) o valor bruto do lote no fim do dia \(d\).

Quando \(d\) é elegível para rendimento do lote:

\[
V_i^{br}(d)=V_i^{br}(d-1)\cdot g_i(d)
\]

onde \(g_i(d)\) é o fator diário do lote, derivado do submodelo oficial de rendimento e valoração do projeto.

Quando o dia não é elegível para rendimento:

\[
V_i^{br}(d)=V_i^{br}(d-1)
\]

Essa elegibilidade respeita:

- data de recebimento/aplicação;
- regra de rendimento do produto;
- calendário financeiro aplicável;
- convenção já validada no repositório.

### 7.2. Valor líquido do lote

\[
V_i^{liq}(t)=V_i^{br}(t)\cdot \phi_i(t)
\]

onde \(\phi_i(t)\) incorpora:

- IOF, quando aplicável;
- IR regressivo, quando aplicável;
- isenção, quando aplicável.

### 7.3. Uso no modelo principal

O submodelo de rendimento fornece diretamente:

- \(B_i(t)\): valor economicamente disponível da fonte/lote no dia;
- \(K_i^{keep}(t,H)\): valor terminal líquido de manter;
- \(K_{Gp}^{switch}(t,H)\): valor terminal líquido de grupos em switching;
- custos marginais econômicos para pagamento e comparação entre pacotes.

Assim, o rendimento **não é variável de decisão**, mas sim **submodelo determinístico de atualização e valoração**.

---

## 8. Contas do dia

Cada conta \(j\in\mathcal J_t\) possui valor:

\[
D_j(t)
\]

e deve ser paga **integralmente no próprio dia \(t\)**.

O modelo **não admite**:

- atraso;
- antecipação;
- não pagamento;
- pagamento parcial da conta.

Portanto, para todo \(j\in\mathcal J_t\):

\[
\sum_{i\in\mathcal S_t^{pay}} q_{ij}^{(k)} = D_j(t)
\]

---

## 9. Pagamento combinatório com restrição global de residual do dia

### 9.1. Variáveis de pagamento

\[
q_{ij}^{(k)} \ge 0
\]

representa o valor da fonte \(i\) usado para pagar a conta \(j\) no pacote \(k\).

Defina o total usado da fonte \(i\) na fase de pagamento do dia:

\[
Q_i^{(k)}=\sum_{j\in\mathcal J_t} q_{ij}^{(k)}
\]

### 9.2. Binária de uso da fonte no pagamento do dia

\[
a_i^{(k)}\in\{0,1\}
\]

com a ligação:

\[
Q_i^{(k)} \le B_i(t)\, a_i^{(k)}
\]

Então:

- \(a_i^{(k)}=1\): a fonte participou do pagamento do dia;
- \(a_i^{(k)}=0\): a fonte não participou.

### 9.3. Residual da fonte após pagamento

\[
R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}
\]

### 9.4. Binária de sobrevivência residual após pagamento

\[
r_i^{(k)}\in\{0,1\}
\]

onde:

- \(r_i^{(k)}=1\): a fonte participou do pagamento e terminou a fase de pagamento com residual operacionalmente positivo;
- \(r_i^{(k)}=0\): caso contrário.

Com \(R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}\), a ligação correta é:

\[
R_i^{pay,(k)} \le \delta_{res} + \bigl(B_i(t)-\delta_{res}\bigr)\, r_i^{(k)} + M(1-a_i^{(k)})
\]

\[
R_i^{pay,(k)} \ge (\delta_{res}+\delta_{mon})\, r_i^{(k)} - M(1-a_i^{(k)})
\]

\[
r_i^{(k)} \le a_i^{(k)}
\]

onde:

- \(M\) é uma constante grande suficiente;
- \(\delta_{res}=0{,}20\) é o limiar operacional de resíduo resolvido;
- \(\delta_{mon}=0{,}01\) é a tolerância monetária fina.

Interpretação:

- se \(a_i^{(k)}=0\), a fonte não participou do pagamento do dia;
- se \(a_i^{(k)}=1\) e \(r_i^{(k)}=0\), então o residual pós-pagamento é tratado como operacionalmente resolvido, isto é, \(R_i^{pay,(k)} \le \delta_{res}\);
- se \(a_i^{(k)}=1\) e \(r_i^{(k)}=1\), então o residual é operacionalmente positivo, isto é, \(R_i^{pay,(k)} > \delta_{res}\).

---

## 9-A. Definição contratual-operacional de residual positivo

Para fins do modelo, o residual de uma fonte após a fase de pagamento é:

\[
R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}
\]

Um residual é considerado **positivo** apenas quando, após aplicação da convenção oficial de arredondamento monetário do projeto:

\[
R_i^{pay,(k)} > \delta_{res}
\]

com, na configuração operacional oficial:

\[
\delta_{res}=0{,}20
\]

Consequentemente:

- se \(R_i^{pay,(k)} \le 0{,}20\), o residual é tratado como **resolvido/zerado operacionalmente**;
- se \(R_i^{pay,(k)} > 0{,}20\), a fonte é tratada como **sobrevivente residual** ao fim da fase de pagamento.

Essa definição governa diretamente a regra global do residual do dia.

### 9.5. Regra operacional global do dia

Defina o número de fontes usadas no pagamento do dia:

\[
N_t^{pay,(k)}=\sum_{i\in\mathcal S_t^{pay}} a_i^{(k)}
\]

A regra operacional final é:

- se \(N_t^{pay,(k)}=1\), tudo certo;
- se \(N_t^{pay,(k)}\ge 2\), então **no máximo uma** das fontes usadas no pagamento do dia pode terminar essa fase com residual positivo.

A restrição formal é:

\[
\sum_{i\in\mathcal S_t^{pay}} r_i^{(k)} \le 1
\]

Interpretação:
- várias fontes podem ser usadas para pagar o conjunto das contas do dia;
- mas, ao fim da fase de pagamento, no máximo uma fonte usada pode sobreviver com residual;
- todas as demais fontes usadas devem zerar nessa fase.

---

## 10. Produtos destino

Defina:

\[
\mathcal P_t
\]

como o conjunto dos produtos elegíveis para receber switching no dia.

Cada produto \(p\in\mathcal P_t\) possui:

- \(K_p^{new}(t,H)\): valor terminal líquido por unidade aplicada em \(t\);
- \(TicketMin_p\), \(TicketMax_p\);
- liquidez;
- carência;
- regras operacionais.

---

## 10-A. Camada oficial de ranqueamento da carteira

O modelo incorpora uma **camada oficial de ranqueamento da carteira** como **módulo auxiliar vinculante de priorização de destinos**.

Essa camada tem a função de:

- ordenar os produtos da aba `Carteira` por score estabilizado;
- produzir o subconjunto priorizado de produtos destino elegíveis;
- alimentar a construção do conjunto de produtos destino considerados pelo motor diário;
- fornecer parâmetros auxiliares de priorização e triagem dos destinos de switching.

Essa camada **não substitui** o comparador diário por pacotes e **não altera** o objetivo principal de maximização do patrimônio líquido terminal líquido. Sua função é **auxiliar, vinculante e preparatória**, restringindo e priorizando o universo de destinos economicamente considerados.

### 10-A.1. Natureza da camada de ranking

A camada de ranqueamento da carteira é definida a partir do módulo estabilizado de ranking existente no repositório, aplicado sobre a aba `Carteira`.

Ela produz, para cada produto elegível \(p\), atributos auxiliares incluindo ao menos:

- \(Score_p\): score consolidado do produto na carteira;
- \(Rank_p\): posição relativa do produto no ranqueamento oficial;
- \(ProxyTerm_p\): proxy terminal do destino;
- parâmetros auxiliares de liquidez, carência, ticket mínimo, ticket máximo e retorno proxy.

### 10-A.2. Relação obrigatória com o conjunto de destinos elegíveis

Defina:

\[
\mathcal P_t^{rank}
\]

como o conjunto de produtos priorizados pela camada oficial de ranqueamento da carteira no dia \(t\).

O conjunto efetivamente considerado pelo motor diário deve ser **derivado** dessa camada oficial. Formalmente:

\[
\mathcal P_t \subseteq \mathcal P_t^{rank}
\]

e, em termos normativos, produtos fora de \(\mathcal P_t^{rank}\) **não devem entrar na geração ordinária de cenários**, salvo justificativa operacional explícita, auditável e compatível com o contrato e o modelo oficiais.

Assim, \(\mathcal P_t\) deve ser construído a partir de \(\mathcal P_t^{rank}\) após aplicação dos filtros operacionais do dia, incluindo:

- disponibilidade;
- elegibilidade contratual;
- liquidez;
- carência;
- ticket;
- compatibilidade com o pacote e com o estado do dia.

### 10-A.3. Papel no modelo diário

A camada oficial de ranqueamento da carteira pode ser usada para:

- priorização dos produtos destino;
- triagem computacional de candidatos;
- ordenação de destinos no processo de geração de cenários;
- desempates secundários de baixa diferença terminal;
- organização auditável da saída da carteira.

É vedado usar essa camada como substituta do comparador diário de pacotes.

### 10-A.4. Relação com a função objetivo

O ranqueamento da carteira **não redefine** a função objetivo do problema diário.

A função objetivo principal continua sendo a maximização do patrimônio líquido terminal líquido. O ranking da carteira atua apenas como:

- módulo auxiliar vinculante de priorização;
- camada de organização do universo de destinos;
- estrutura de apoio à triagem e à auditabilidade.

### 10-A.5. Relação com a auditabilidade

A camada de ranqueamento da carteira deve permanecer auditável e coerente com:

- a aba `Carteira`;
- os artefatos oficiais de saída;
- os destinos efetivamente considerados pelo motor;
- os campos exportados para validação manual.

---

## 11. Formas de switching adotadas

O modelo usa somente três formas de switching:

1. **individual**: grupo unitário;
2. **agrupado combinatório**: grupo com duas ou mais fontes;
3. **integral**: maior grupo factível elegível do pacote do dia.

---

## 12. Grupos de switching

### 12.1. Antes do pagamento

\[
\mathcal G_{t,\mathrm{pre}} \subseteq 2^{\mathcal S_{t,\mathrm{pre}}^{sw}}
\]

### 12.2. Depois do pagamento

No pacote `pay_then_switch`, o conjunto residual elegível é:

\[
\mathcal S_{t,\mathrm{post}}^{sw,(k)}=
\{i: R_i^{pay,(k)} > \delta_{res} \text{ e a fonte permanece elegível para switching}\}
\]

e os grupos possíveis são:

\[
\mathcal G_{t,\mathrm{post}}^{(k)} \subseteq 2^{\mathcal S_{t,\mathrm{post}}^{sw,(k)}}
\]

---

## 13. Definição formal de switching integral

**Switching integral** = switching do **maior grupo factível elegível para um produto destino específico dentro do pacote do dia**, após filtros de:

- disponibilidade;
- liquidez;
- carência;
- ticket;
- compatibilidade com o produto destino.

---

## 13-A. Factibilidade explícita do pacote `switch_then_pay`

O pacote `switch_then_pay` só pode ser considerado factível se, **após a aplicação do switching** e respeitando as restrições de liquidez, carência, ticket, produto destino e cronologia intradiária, o conjunto remanescente de recursos economicamente disponíveis ainda permitir a liquidação integral das contas do dia.

Formalmente, seja \(\mathcal E_t^{sw}\) o estado do dia após a execução do switching pré-pagamento. O pacote `switch_then_pay` só é factível se existir uma alocação de pagamento tal que:

\[
\sum_{i\in\mathcal S^{pay}(\mathcal E_t^{sw})} q_{ij}^{(k)} = D_j(t)
\qquad \forall j\in\mathcal J_t
\]

onde \(\mathcal S^{pay}(\mathcal E_t^{sw})\) é o conjunto de fontes ainda economicamente disponíveis para pagamento no estado pós-switching.

Se essa condição falhar, o pacote deve ser classificado como **inviável** e excluído da comparação do dia.

---

## 14. Variáveis de switching

\[
z_{Gp}^{(k)}\in\{0,1\}
\]

indica que o grupo \(G\) é migrado para o produto \(p\) no pacote \(k\).

Valor alocado ao produto:

\[
y_p^{(k)} = \sum_G B_G^{liq,(k)}(t)\, z_{Gp}^{(k)}
\]

onde \(B_G^{liq,(k)}(t)\) é o valor líquido migrável do grupo no pacote \(k\).

---

## 14-A. Estados operacionais de switching

Todo switching avaliado pelo modelo deve possuir estado operacional explícito:

- candidato;
- rejeitado;
- promovido;
- materializado;
- consumido em pagamento;
- bloqueado.

Switching candidato representa oportunidade avaliada, mas não fonte de pagamento.

Switching promovido representa decisão selecionada pelo motor, mas só se torna fonte de pagamento quando materializado no estado temporal.

Switching materializado representa transição efetiva de estado e pode criar fonte/lote sintético disponível, respeitada a cronologia intradiária do pacote.

---

## 14-B. Campos candidatos e campos operacionais

Campos operacionais do modelo só podem receber eventos, fontes, lotes e saldos materializados.

Informações candidatas, estimadas ou diagnósticas devem ser representadas em campos próprios e não podem preencher campos operacionais.

Produto destino e ganho estimado de switching não equivalem a lote pós-switching materializado.

---

## 15. Convivência entre pagamento e switching

Uma fonte pode:

- participar da fase de pagamento;
- e depois, com o residual, participar de um único switching.

A restrição correta é:

\[
\sum_{p\in\mathcal P_t}\sum_{G\ni i} z_{Gp}^{(k)} \le 1
\qquad \forall i
\]

---

## 16. Conservação de valor refinada

\[
Q_i^{(k)} + S_i^{sw,(k)} + s_i^{(k)} = B_i(t)
\]

onde:

- \(Q_i^{(k)}\): valor usado em pagamento;
- \(S_i^{sw,(k)}\): valor comprometido em switching;
- \(s_i^{(k)}\): **residual final mantido** ao final do pacote.

### 16.1. Restrição adicional sem fracionamento de switching no residual

No pacote `pay_then_switch`:

\[
R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}
\]

e o switching atua integralmente sobre o residual. Logo:

\[
S_i^{sw,(k)} \in \{0,\; R_i^{pay,(k)}\}
\]

No pacote `switch_then_pay`, a fonte elegível pré-pagamento entra integralmente no grupo ou não entra.

### 16.2. Interpretação final da conservação de valor no residual

A conservação de valor por fonte continua sendo:

\[
Q_i^{(k)} + S_i^{sw,(k)} + s_i^{(k)} = B_i(t)
\]

No pacote `pay_then_switch`, o switching atua integralmente sobre o residual elegível. Mas, para fins operacionais e auditáveis, o residual final relevante deve ser interpretado à luz do limiar \(\delta_{res}\). Assim, resíduos de até R$ 0,20 são tratados como resolvidos/zerados operacionalmente.

---

## 17. Elegibilidade temporal e operacional

Pagamento:

\[
q_{ij}^{(k)} \le A_i^{pay}(t)\,B_i(t)
\]

Switching:

\[
\sum_{p}\sum_{G\ni i} z_{Gp}^{(k)} \le A_i^{sw}(t)
\]

Assim:

- fonte futura não entra;
- fonte em carência de retirada não entra em pagamento;
- fonte em carência de saída não entra em switching.

---

## 18. Ticket mínimo e máximo

\[
TicketMin_p\, w_p^{(k)} \le y_p^{(k)} \le TicketMax_p\, w_p^{(k)}
\]

com

\[
w_p^{(k)}\in\{0,1\}
\]

---

## 19. Ordem intradiária por pacote

### `no_action`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\);
3. manter o estado.

### `switch_only`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\);
3. materializar o switching vencedor;
4. fechar o estado do dia.

### `pay_only`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\);
3. pagar integralmente as contas do dia;
4. fechar o estado do dia.

### `switch_then_pay`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\);
3. materializar switching sobre \(\mathcal S_{t,\mathrm{pre}}^{sw}\);
4. pagar integralmente as contas do dia no estado pós-switching materializado;
5. fechar o estado do dia.

### `pay_then_switch`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em \(t\);
3. pagar integralmente as contas do dia;
4. construir \(\mathcal S_{t,\mathrm{post}}^{sw,(k)}\);
5. materializar switching sobre o estado pós-pagamento;
6. fechar o estado do dia.

---

## 20. Função objetivo

Para cada pacote \(k\), a função objetivo é avaliada sobre o estado final da trajetória:

\[
\max Z\left(S_{t,R_k}^{(k)}\right)
\]

com

\[
Z_t^{(k)}
=
\sum_i K_i^{keep}(t,H)\, s_i^{(k)}
+
\sum_{p\in\mathcal P_t} K_p^{new}(t,H)\, y_p^{(k)}
-
\sum_i \tau_i\!\bigl(Q_i^{(k)}\bigr)
-
\sum_G\sum_{p\in\mathcal P_t} \tau_G^{(k)} z_{Gp}^{(k)}
-
\lambda_{liq}\Psi_{liq}^{(k)}
-
\lambda_{conc}\Psi_{conc}^{(k)}
-
\lambda_{ops}\Psi_{ops}^{(k)}
\]

onde:

- \(K_i^{keep}(t,H)\): valor terminal líquido de manter a fonte;
- \(K_p^{new}(t,H)\): valor terminal líquido da nova alocação;
- \(\tau_i,\tau_G\): fiscalidade/custos;
- \(\Psi\): penalidades de liquidez, concentração e operacionalidade.

---

## 21. Critério econômico do pagamento

O pagamento deve usar a fonte ou combinação de fontes com menor custo de oportunidade terminal líquido.

Para uma fonte \(i\):

\[
MC_i^{pay}(t)=
\frac{
K_i^{keep}(t,H)-K_i^{after\,pay}(t,H)
}{
\text{valor usado}
}
\]

O mesmo raciocínio vale para combinações de fontes.

O modelo **não** escolhe simplesmente “o lote de menor taxa nominal”.  
Ele escolhe a alternativa de menor perda terminal líquida.

---

## 22. Separação entre modelo conceitual e política computacional

No nível conceitual:

\[
\mathcal G_{t,\mathrm{pre}} \subseteq 2^{\mathcal S_{t,\mathrm{pre}}^{sw}}
\qquad\text{e}\qquad
\mathcal G_{t,\mathrm{post}}^{(k)} \subseteq 2^{\mathcal S_{t,\mathrm{post}}^{sw,(k)}}
\]

Na implementação, a enumeração poderá ser triada de forma controlada, por exemplo:

- grupos unitários;
- pares;
- alguns grupos triplos candidatos;
- grupo integral;
- grupos ranqueados preliminarmente por score econômico.

Essa triagem **não altera** a definição conceitual do problema; ela apenas controla o custo computacional.

---

## 22-A. Vedação à decisão em camadas de saída

As saídas do modelo devem ser renderizações do ledger canônico do pacote escolhido.

Camadas de apresentação, planilhas, consoles, relatórios, validadores de exibição e objetos observáveis não podem escolher fonte, lote, pacote, cobertura, status, data de switching, destino de switching, lote pós-switching, saldo antes, consumo ou saldo depois.

Qualquer divergência observada na saída deve ser tratada como falha do estado temporal conjunto ou do ledger, não como oportunidade de reconciliação visual posterior.

---

## 23. Definição final consolidada

> Em cada dia \(t\), o modelo verifica se existem contas com vencimento em \(t\), constrói um estado temporal conjunto, incorpora recebidos disponíveis, normaliza lotes vencidos, deriva fontes elegíveis para pagamento e switching e compara os pacotes factíveis como trajetórias completas de transição de estado. Se não houver contas, compara `no_action` e `switch_only`. Se houver contas, compara `pay_only`, `switch_then_pay` e `pay_then_switch`. No pacote `switch_then_pay`, o pagamento consome o estado pós-switching materializado. No pacote `pay_then_switch`, o switching consome o estado pós-pagamento materializado. O motor produz um ledger canônico de eventos para o pacote escolhido, e as saídas operacionais são apenas renderizações desse ledger. Campos operacionais só podem conter fontes, lotes, switchings e saldos materializados. A escolha ótima maximiza o patrimônio líquido terminal líquido, considerando custo de oportunidade, fiscalidade, liquidez, carência, vencimento, regras dos produtos, conservação de valor e auditabilidade.

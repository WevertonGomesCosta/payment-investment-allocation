# Modelo matemático estatístico-financeiro oficial — V179

## 1. Finalidade

Este documento formaliza o modelo matemático estatístico-financeiro oficial do projeto `payment-investment-allocation`.

O modelo existe para, em cada dia `t`, decidir conjuntamente pagamentos e switching sob o mesmo estado econômico do dia, com o objetivo de maximizar o patrimônio líquido terminal líquido no horizonte principal do projeto.

Este documento consolida a formulação final aprovada para:
- decisão diária por pacotes;
- pagamento obrigatório e integral na data da planilha;
- filtragem prévia por disponibilidade, liquidez e carência;
- pós-vencimento como reclassificação para fonte disponível do dia;
- switching apenas nas formas individual, agrupado combinatório e integral;
- pagamento conjunto do dia com restrição operacional de residual;
- valoração de lotes pelo mesmo submodelo de rendimento já validado na saída do console.

---

## 2. Objetivo do modelo

Em cada dia `t`, o modelo deve escolher o pacote de decisão economicamente superior, maximizando o patrimônio líquido terminal líquido no horizonte principal `H`, respeitando restrições operacionais, fiscais, temporais e de produto.

Formalmente, a decisão ótima do dia é dada por:

\[
k_t^\star = \arg\max_{k\in\mathcal K_t} Z_t^{(k)}
\]

onde `k` é um pacote factível do dia e `Z_t^{(k)}` é o valor terminal líquido do pacote.

---

## 3. Estrutura lógica do dia `t`

### 3.1. Existência de contas no dia

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

Se `\mathbb I_t^{pay}=0`, o dia é sem pagamento.

Se `\mathbb I_t^{pay}=1`, o dia é com pagamento obrigatório.

### 3.2. Pacotes factíveis do dia

Se não houver contas no dia:

\[
\mathcal K_t=
\{\text{no\_action},\text{switch\_only}\}
\]

Se houver contas no dia:

\[
\mathcal K_t=
\{\text{pay\_only},\text{switch\_then\_pay},\text{pay\_then\_switch}\}
\]

---

## 4. Estado econômico do dia

Defina o estado do dia como:

\[
\mathcal E_t=(\mathcal U_t,\mathcal J_t,\mathcal P_t,\Theta_t)
\]

onde:
- `\mathcal U_t`: universo bruto de recursos observáveis no dia;
- `\mathcal J_t`: contas com vencimento em `t`;
- `\mathcal P_t`: produtos destino elegíveis;
- `\Theta_t`: parâmetros econômicos, fiscais, operacionais e de rendimento do dia.

---

## 5. Universo bruto e filtragem operacional

### 5.1. Universo bruto

\[
\mathcal U_t
\]

Inclui saldo disponível, recebidos disponíveis, lotes aportados, lotes vencidos, lotes futuros ainda indisponíveis e demais recursos financeiros presentes no estado.

### 5.2. Fontes elegíveis para pagamento

\[
\mathcal S_t^{pay}=\{i\in\mathcal U_t: A_i^{pay}(t)=1\}
\]

com

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

\[
\mathcal S_{t,\mathrm{pre}}^{sw}=\{i\in\mathcal U_t: A_i^{sw}(t)=1\}
\]

com

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

Essa filtragem é anterior à otimização.

---

## 6. Regra de pós-vencimento

A regra correta é:

\[
m_i \le t
\;\Rightarrow\;
i \text{ deixa de ser lote aportado ativo e passa a ser fonte disponível do dia}
\]

Logo:
- se `m_i\le t`, a fonte entra como disponível;
- se `m_i>t`, não entra por vencimento.

---

## 7. Submodelo de rendimento e valoração dos lotes

O modelo inclui explicitamente o submodelo de rendimento e valoração dos lotes já validado no projeto e alinhado à saída do console.

### 7.1. Valor bruto do lote

Para cada lote `i`, seja `V_i^{br}(d)` o valor bruto no fim do dia `d`.

Quando `d` é elegível para rendimento do lote:

\[
V_i^{br}(d)=V_i^{br}(d-1)\cdot g_i(d)
\]

onde `g_i(d)` é o fator diário do lote segundo a lógica validada no projeto.

Quando o dia não é elegível para rendimento:

\[
V_i^{br}(d)=V_i^{br}(d-1)
\]

### 7.2. Valor líquido do lote

\[
V_i^{liq}(t)=V_i^{br}(t)\cdot \phi_i(t)
\]

onde `\phi_i(t)` incorpora IOF, IR regressivo ou isenção, conforme a regra do produto.

### 7.3. Uso no modelo principal

O submodelo de rendimento fornece:
- `B_i(t)`: valor economicamente disponível no dia;
- `K_i^{keep}(t,H)`: valor terminal líquido de manter;
- `K_{Gp}^{switch}(t,H)`: valor terminal líquido do grupo em switching;
- custos marginais econômicos para pagamento e comparação de pacotes.

---

## 8. Contas do dia

Cada conta `j\in\mathcal J_t` tem valor:

\[
D_j(t)
\]

e deve ser paga integralmente no próprio dia `t`.

Logo:

\[
\sum_{i\in\mathcal S_t^{pay}} q_{ij}^{(k)} = D_j(t)
\qquad \forall j\in\mathcal J_t
\]

O modelo não admite atraso, antecipação, não pagamento ou pagamento parcial da conta.

---

## 9. Pagamento combinatório com restrição global de residual do dia

### 9.1. Variáveis de pagamento

\[
q_{ij}^{(k)} \ge 0
\]

representa o valor da fonte `i` usado para pagar a conta `j` no pacote `k`.

Defina o total usado da fonte `i` na fase de pagamento do dia:

\[
Q_i^{(k)}=\sum_{j\in\mathcal J_t} q_{ij}^{(k)}
\]

### 9.2. Binária de uso da fonte no pagamento do dia

\[
a_i^{(k)}\in\{0,1\}
\]

com ligação:

\[
Q_i^{(k)} \le B_i(t)\, a_i^{(k)}
\]

### 9.3. Residual da fonte após pagamento

\[
R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}
\]

### 9.4. Binária de sobrevivência residual após pagamento

\[
r_i^{(k)}\in\{0,1\}
\]

onde `r_i^{(k)}=1` quando a fonte participou do pagamento e terminou essa fase com residual positivo.

Ligações:

\[
R_i^{pay,(k)} \le B_i(t)\, r_i^{(k)} + M(1-a_i^{(k)})
\]

\[
r_i^{(k)} \le a_i^{(k)}
\]

### 9.5. Regra operacional global do dia

Defina o número de fontes usadas no pagamento do dia:

\[
N_t^{pay,(k)}=\sum_{i\in\mathcal S_t^{pay}} a_i^{(k)}
\]

A regra operacional final é:
- se `N_t^{pay,(k)}=1`, tudo certo;
- se `N_t^{pay,(k)}\ge 2`, então no máximo uma das fontes usadas no pagamento do dia pode terminar essa fase com residual positivo.

A restrição formal é:

\[
\sum_{i\in\mathcal S_t^{pay}} r_i^{(k)} \le 1
\]

---

## 10. Produtos destino

\[
\mathcal P_t
\]

é o conjunto dos produtos elegíveis para receber switching no dia.

Cada produto `p\in\mathcal P_t` possui:
- `K_p^{new}(t,H)`: valor terminal líquido por unidade aplicada em `t`;
- `TicketMin_p`, `TicketMax_p`;
- liquidez;
- carência;
- regras operacionais.

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
\{i: R_i^{pay,(k)} > 0 \text{ e a fonte permanece elegível para switching}\}
\]

e os grupos possíveis são:

\[
\mathcal G_{t,\mathrm{post}}^{(k)} \subseteq 2^{\mathcal S_{t,\mathrm{post}}^{sw,(k)}}
\]

---

## 13. Definição formal de switching integral

**Switching integral** = switching do maior grupo factível elegível do pacote do dia, após filtros de disponibilidade, liquidez, carência, ticket e compatibilidade com o produto destino.

---

## 14. Variáveis de switching

\[
z_{Gp}^{(k)}\in\{0,1\}
\]

indica que o grupo `G` é migrado para o produto `p` no pacote `k`.

Valor alocado ao produto:

\[
y_p^{(k)} = \sum_G B_G^{liq,(k)}(t)\, z_{Gp}^{(k)}
\]

---

## 15. Convivência entre pagamento e switching

Uma fonte pode participar da fase de pagamento e depois, com o residual, participar de um único switching.

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
- `Q_i^{(k)}`: valor usado em pagamento;
- `S_i^{sw,(k)}`: valor comprometido em switching;
- `s_i^{(k)}`: residual final mantido ao final do pacote.

### Restrição adicional sem fracionamento de switching no residual

No pacote `pay_then_switch`:

\[
R_i^{pay,(k)} = B_i(t)-Q_i^{(k)}
\]

e o switching atua integralmente sobre o residual. Logo:

\[
S_i^{sw,(k)} \in \{0,\; R_i^{pay,(k)}\}
\]

No pacote `switch_then_pay`, a fonte elegível pré-pagamento entra integralmente no grupo ou não entra.

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

Assim, fonte futura não entra; fonte em carência de retirada não entra em pagamento; fonte em carência de saída não entra em switching.

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
2. normalizar lotes vencidos em `t`;
3. manter o estado.

### `switch_only`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em `t`;
3. executar o switching vencedor;
4. fechar o estado do dia.

### `pay_only`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em `t`;
3. pagar integralmente as contas do dia;
4. fechar o estado do dia.

### `switch_then_pay`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em `t`;
3. executar switching sobre `\mathcal S_{t,\mathrm{pre}}^{sw}`;
4. pagar integralmente as contas do dia no estado pós-switching;
5. fechar o estado do dia.

### `pay_then_switch`
1. incorporar recebidos disponíveis do dia;
2. normalizar lotes vencidos em `t`;
3. pagar integralmente as contas do dia;
4. construir `\mathcal S_{t,\mathrm{post}}^{sw,(k)}`;
5. executar switching sobre o residual;
6. fechar o estado do dia.

---

## 20. Função objetivo

Para cada pacote `k`:

\[
\max Z_t^{(k)}
\]

com

\[
Z_t^{(k)}=
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

---

## 21. Critério econômico do pagamento

O pagamento deve usar a fonte ou combinação de fontes com menor custo de oportunidade terminal líquido.

Para uma fonte `i`:

\[
MC_i^{pay}(t)=
\frac{
K_i^{keep}(t,H)-K_i^{after\,pay}(t,H)
}{
\text{valor usado}
}
\]

O mesmo raciocínio vale para combinações de fontes.

---

## 22. Separação entre modelo conceitual e política computacional

No nível conceitual:

\[
\mathcal G_{t,\mathrm{pre}} \subseteq 2^{\mathcal S_{t,\mathrm{pre}}^{sw}}
\qquad\text{e}\qquad
\mathcal G_{t,\mathrm{post}}^{(k)} \subseteq 2^{\mathcal S_{t,\mathrm{post}}^{sw,(k)}}
\]

Na implementação, a enumeração será triada de forma controlada, por exemplo:
- grupos unitários;
- pares;
- alguns grupos triplos candidatos;
- grupo integral;
- grupos ranqueados preliminarmente por score econômico.

---

## 23. Convenções de governança

### 23.1. Convenção de arredondamento

O documento formal do modelo deve congelar explicitamente:
- arredondamento monetário a centavos;
- etapa de arredondamento para valores de pagamento, imposto, residual e valoração líquida;
- política uniforme de arredondamento para comparação entre pacotes.

### 23.2. Horizonte principal e sensibilidades

A decisão operacional do modelo usa um horizonte principal `H`.

Sensibilidades adicionais devem ser tratadas como camadas de auditoria ou análise complementar, salvo regra explícita em contrário.

### 23.3. Hierarquia de desempate

Quando dois pacotes tiverem valor terminal praticamente equivalente, o desempate deve seguir hierarquia documental explícita, priorizando menor complexidade operacional e melhor liquidez residual, sem alterar o núcleo matemático.

### 23.4. Convenção intradiária de disponibilidade

Recursos incorporados em `t` entram no estado antes da decisão do pacote do dia. Um recurso só pode ser usado em uma etapa se já existir economicamente naquela etapa, obedecendo estritamente à cronologia intradiária do pacote escolhido.

---

## 24. Definição final oficial

> Em cada dia `t`, o modelo primeiro verifica se existem contas com vencimento em `t`. Em seguida, a partir do universo bruto de recursos, deriva os conjuntos elegíveis para pagamento e para switching, já filtrados por disponibilidade temporal, liquidez, resgate e carência. Todos os lotes vencidos em `t` ou antes são reclassificados como fontes disponíveis do dia. A valoração econômica de cada lote/fonte usa o mesmo submodelo de rendimento e valoração já validado no projeto e alinhado à saída do console. Se não houver contas, o modelo compara `no_action` e `switch_only`. Se houver contas, compara `pay_only`, `switch_then_pay` e `pay_then_switch`. Dentro de cada pacote, resolve conjuntamente o pagamento integral das contas do dia e o switching permitido apenas nas formas individual, agrupado combinatório e integral. No conjunto dos pagamentos do dia, se múltiplas fontes forem usadas, então no máximo uma delas pode terminar a fase de pagamento com residual positivo; todas as demais fontes usadas devem zerar nessa fase. A escolha ótima do dia é a que maximiza o patrimônio líquido terminal líquido, considerando custo de oportunidade, fiscalidade, liquidez, carência, vencimento e regras dos produtos.

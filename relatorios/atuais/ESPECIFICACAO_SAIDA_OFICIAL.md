# ESPECIFICAÇÃO DA SAÍDA OFICIAL — V189

## 1. Finalidade

Este documento consolida a **especificação oficial da camada observável do projeto**.

Seu objetivo é fechar, antes da derivação de `resolver_dia(t, E_t)`, o contrato prático de saída que deverá ser respeitado por:

- console;
- markdown;
- json;
- arquivo oficial `.xlsx`.

Esta especificação **não altera** o contrato mestre, o modelo matemático estatístico-financeiro, o núcleo econômico nem a estrutura diária por pacotes congelada.

---

## 2. Princípio geral

A camada observável do projeto é organizada em quatro níveis com papéis distintos:

- **console** → leitura operacional rápida;
- **markdown** → auditoria humana estruturada;
- **json** → estrutura completa machine-readable;
- **.xlsx** → manipulação, conferência e validação manual.

É vedado que essas camadas concorram entre si sem função diferenciada.

---

## 3. Contrato do console

O console é a **camada de leitura operacional rápida**.

### 3.1. Cabeçalho obrigatório

Toda execução oficial deve apresentar, no mínimo:

- baseline vigente;
- data de referência;
- janela analisada;
- origem dos dados;
- status do cache/BCB;
- caminho da planilha carregada;
- caminho dos artefatos gerados.

### 3.2. Bloco diário obrigatório

Para cada dia da janela analisada, o console deve mostrar:

- data;
- existência ou não de contas no dia;
- pacotes avaliados;
- pacote vencedor;
- status dos demais pacotes:
  - perdedor;
  - inviável;
  - não aplicável.

### 3.3. Bloco do pagamento vencedor

Quando houver contas no dia, o console deve mostrar um quadro curto com:

- conta;
- valor da conta;
- fonte/lote usado;
- valor usado por fonte;
- saldo antes;
- residual após pagamento;
- indicação explícita da fonte residual sobrevivente, quando existir;
- flag de “resíduo resolvido” quando residual \(\le\) R$ 0,20.

### 3.4. Bloco de ranking relevante da carteira

O console deve mostrar apenas uma **amostra operacional do ranking da carteira**, com foco nos destinos relevantes do dia.

Campos mínimos:

- rank;
- produto;
- score;
- proxy terminal;
- liquidez;
- carência;
- ticket mínimo;
- status:
  - elegível;
  - inelegível;
  - fora do recorte do dia.

### 3.5. Bloco de switchings candidatos/classificados

O console deve mostrar um quadro resumido com os switchings do dia, incluindo:

- id do cenário;
- tipo:
  - individual;
  - agrupado combinatório;
  - integral;
- grupo de origem;
- destino;
- valor bruto;
- valor líquido estimado;
- status:
  - elegível;
  - promovível;
  - executado;
  - rejeitado;
  - inviável;
- motivo resumido da rejeição/inviabilidade.

### 3.6. Bloco de lotes críticos

Quando houver lotes críticos, o console deve mostrar um quadro curto com:

- lote;
- produto;
- data de vencimento;
- valor atual;
- status no dia:
  - ativo;
  - vencido-normalizado;
  - usado em pagamento;
  - usado em switching;
  - residual.

### 3.7. Bloco de inconsistências

Quando existirem inconsistências temporais, elegibilidades bloqueadas ou pacotes inviáveis, o console deve mostrar mensagens curtas e explícitas.

---

## 4. Contrato do `.xlsx`

O `.xlsx` é o **artefato oficial de manipulação, conferência e validação manual**.

### 4.1. Abas obrigatórias

O arquivo oficial `.xlsx` deve conter, no mínimo, as seguintes abas, com esta grafia:

- **Extrato Passado**
- **Extrato Futuro**
- **Switching**
- **Carteira**
- **Situação Atual**

### 4.2. Aba “Extrato Passado”

Função: rastrear e validar eventos e movimentos já ocorridos.

Campos mínimos:

- data;
- tipo de evento;
- conta/evento;
- fonte/lote;
- valor bruto;
- valor líquido;
- imposto;
- saldo antes;
- saldo depois;
- observação operacional.

### 4.3. Aba “Extrato Futuro”

Função: rastrear projeções e decisões prospectivas.

Campos mínimos:

- data;
- contas do dia;
- pacote vencedor;
- fontes previstas para pagamento;
- residual previsto;
- switching previsto;
- destino previsto;
- observações de factibilidade.

### 4.4. Aba “Switching”

Função: concentrar a trilha oficial dos switchings.

Campos mínimos:

- data;
- id do cenário;
- tipo do switching;
- fontes do grupo;
- destino;
- valor bruto;
- valor líquido estimado;
- elegibilidade;
- classificação;
- status final;
- motivo de rejeição, quando houver;
- ganho/perda terminal estimado.

### 4.5. Aba “Carteira”

Função: refletir a **carteira oficial ranqueada**.

Campos mínimos:

- rank;
- produto;
- score;
- proxy terminal;
- retorno proxy;
- liquidez;
- carência;
- aplicação mínima;
- aplicação máxima;
- elegibilidade;
- status operacional;
- flag de relevância para switching.

### 4.6. Aba “Situação Atual”

Função: oferecer leitura rápida do estado presente.

Campos mínimos:

- fonte/lote;
- produto;
- valor atual;
- valor líquido;
- vencimento;
- status;
- observação resumida.

---

## 5. Contrato do markdown

O markdown é a **camada de auditoria humana estruturada**.

Ele deve conter:

- cabeçalho da execução;
- resumo da janela;
- dias auditados;
- pacote vencedor por dia;
- quadro resumido de pagamentos;
- quadro resumido de switchings;
- amostra do ranking relevante da carteira;
- inconsistências e inviabilidades relevantes.

---

## 6. Contrato do JSON

O JSON é a **camada detalhada, estruturada e machine-readable**.

Ele deve incluir, por dia:

- estado inicial;
- fontes elegíveis;
- produtos elegíveis;
- ranking relevante usado;
- pacotes avaliados;
- factibilidade;
- pagamento vencedor detalhado;
- switchings candidatos/classificados;
- estado final.

---

## 7. Papel do ranqueamento da carteira na saída

O ranqueamento correto da carteira deve aparecer em duas camadas:

- **console** → amostra relevante do dia;
- **.xlsx** → visão oficial completa da aba `Carteira`.

O JSON preserva a versão completa e estruturada.

---

## 8. Papel dos switchings na saída

Os switchings devem aparecer em três níveis:

- **console** → resumo curto dos principais candidatos, classificado vencedor e executado;
- **.xlsx** → trilha auditável completa na aba `Switching`;
- **json** → estrutura detalhada dos cenários considerados ou triados.

---

## 9. Regra de unicidade informacional

Cada informação essencial do projeto deve possuir uma camada principal de referência:

- leitura rápida do dia → **console**;
- auditoria humana resumida → **markdown**;
- estrutura completa → **json**;
- manipulação e validação operacional → **.xlsx**;
- regra e metodologia → **contrato + modelo**.

---

## 10. Schema mínimo que `resolver_dia(t, E_t)` deverá devolver

A futura especificação de `resolver_dia` deverá nascer compatível com esta camada observável.

Retorno mínimo por dia:

- `data`;
- `tem_contas_no_dia`;
- `estado_inicial_resumido`;
- `fontes_elegiveis_pagamento`;
- `fontes_elegiveis_switching`;
- `produtos_destino_rankeados_relevantes`;
- `pacotes_avaliados`;
- `pacote_vencedor`;
- `pagamento_vencedor`;
- `switchings_candidatos`;
- `switching_classificado`;
- `switching_executado`;
- `inconsistencias_e_inviabilidades`;
- `estado_final_resumido`.

---

## 11. Decisão metodológica

A especificação de `resolver_dia(t, E_t)` deve ser derivada **somente após** a consolidação desta camada observável, para evitar retrabalho na interface de retorno e nos artefatos oficiais.

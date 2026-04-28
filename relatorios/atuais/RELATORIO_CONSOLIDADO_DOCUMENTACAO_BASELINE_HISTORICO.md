# Relatório consolidado — histórico de documentação de baseline

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/documentacao_baseline/` em um único relatório atual, preservando a trilha documental de baseline sem manter arquivos granulares.

- Arquivos consolidados: 6
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/documentacao_baseline/AMPLIACAO_CONTRATO_MESTRE_V181.md` | 27 | Ampliação do contrato mestre — V181 |
| `relatorios/historico/documentacao_baseline/CONGELAMENTO_CONTRATO_MESTRE_V183.md` | 13 | CONGELAMENTO DO CONTRATO MESTRE — V183 |
| `relatorios/historico/documentacao_baseline/CONGELAMENTO_MODELO_OFICIAL_V182.md` | 5 | Congelamento do modelo oficial — V182 |
| `relatorios/historico/documentacao_baseline/FORMALIZACAO_MODELO_OFICIAL_V179.md` | 18 | Formalização do modelo oficial — V179 |
| `relatorios/historico/documentacao_baseline/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md` | 867 | MODELO MATEMÁTICO ESTATÍSTICO-FINANCEIRO FINAL DO PROJETO `payment-investment-allocation` |
| `relatorios/historico/documentacao_baseline/REESCRITA_CONTRATO_MESTRE_V180.md` | 32 | Reescrita do contrato mestre — V180 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Baseline | Histórico documental de baseline preservado em forma consolidada. |
| Governança | Registros antigos deixam de competir visualmente com os documentos atuais. |
| Rastreabilidade | Trechos iniciais dos documentos originais foram preservados. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/documentacao_baseline/AMPLIACAO_CONTRATO_MESTRE_V181.md`

- Título: Ampliação do contrato mestre — V181
- Linhas originais: 27

<details>
<summary>Trecho inicial preservado</summary>

```text
# Ampliação do contrato mestre — V181
## Objetivo
Ampliar o contrato mestre da V180 para que ele deixe de ser apenas normativo e curto, passando a funcionar também como:
- referência principal para próximos chats;
- base documental final do projeto;
- registro histórico condensado das baselines centrais;
- ponto único de entrada para leitura do estado atual do repositório.
## Mudanças centrais
1. O contrato mestre passou a incorporar uma linha histórica resumida das baselines centrais (`V108`, `V117`, `V174`, `V176`, `V177`, `V178`, `V179`, `V180`, `V181`).
2. A hierarquia documental ficou explícita no corpo principal.
3. O contrato passou a distinguir melhor:
   - contrato mestre vigente;
   - modelo oficial;
   - suplementos vigentes;
   - auditorias e validações;
   - backlog;
   - documentos históricos.
4. O documento foi ampliado para servir de referência em outros chats sem obrigar releitura de múltiplos arquivos prévios.
```

</details>

### `relatorios/historico/documentacao_baseline/CONGELAMENTO_CONTRATO_MESTRE_V183.md`

- Título: CONGELAMENTO DO CONTRATO MESTRE — V183
- Linhas originais: 13

<details>
<summary>Trecho inicial preservado</summary>

```text
# CONGELAMENTO DO CONTRATO MESTRE — V183
A V183 promove o texto contratual revisado a contrato mestre canônico do projeto.
## Resultado
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md` passa a refletir a baseline única vigente V183.
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md` passa a ser referenciado explicitamente como anexo metodológico vinculante.
- A hierarquia documental, a governança de saídas e a camada oficial de ranqueamento da carteira permanecem preservadas.
## Status
Contrato mestre congelado sem mudanças estruturais adicionais.
```

</details>

### `relatorios/historico/documentacao_baseline/CONGELAMENTO_MODELO_OFICIAL_V182.md`

- Título: Congelamento do modelo oficial — V182
- Linhas originais: 5

<details>
<summary>Trecho inicial preservado</summary>

```text
# Congelamento do modelo oficial — V182
A V182 congela o arquivo `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md` com a microcorreção final na ligação algébrica da binária de sobrevivência residual ao limiar operacional de R$ 0,20.
A partir desta versão, o modelo é tratado como texto metodológico final congelado da baseline vigente.
```

</details>

### `relatorios/historico/documentacao_baseline/FORMALIZACAO_MODELO_OFICIAL_V179.md`

- Título: Formalização do modelo oficial — V179
- Linhas originais: 18

<details>
<summary>Trecho inicial preservado</summary>

```text
# Formalização do modelo oficial — V179
A V179 formaliza o modelo matemático estatístico-financeiro oficial do projeto em `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`, sem alterar o núcleo matemático previamente aprovado.
## Conteúdo formalizado
- objetivo terminal líquido;
- decisão diária por pacotes;
- pagamento obrigatório e integral na data da planilha;
- filtragem prévia por disponibilidade, liquidez, resgate e carência;
- pós-vencimento como fonte disponível do dia;
- submodelo de rendimento e valoração alinhado à saída do console;
- pagamento combinatório com restrição global de residual do dia;
- switching apenas nas formas individual, agrupado combinatório e integral;
- separação entre switching pré e pós pagamento;
- convenções de governança para arredondamento, horizonte, desempate e cronologia intradiária.
## Escopo desta versão
Esta versão é documental. Não altera o núcleo de cálculo nem a lógica executável do repositório.
```

</details>

### `relatorios/historico/documentacao_baseline/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`

- Título: MODELO MATEMÁTICO ESTATÍSTICO-FINANCEIRO FINAL DO PROJETO `payment-investment-allocation`
- Linhas originais: 867

<details>
<summary>Trecho inicial preservado</summary>

```text
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
```

</details>

### `relatorios/historico/documentacao_baseline/REESCRITA_CONTRATO_MESTRE_V180.md`

- Título: Reescrita do contrato mestre — V180
- Linhas originais: 32

<details>
<summary>Trecho inicial preservado</summary>

```text
# Reescrita do contrato mestre — V180
## Objetivo
A V180 reescreve `CONTRATO_OPERACIONAL_PROJETO.md` como contrato mestre vigente do projeto, alinhado explicitamente ao modelo oficial V179 e às regras consolidadas no chat de revisão contratual.
## Mudanças centrais
1. A V179 passa a ser a baseline documental e metodológica vigente do projeto.
2. O contrato operacional deixa de tomar V108/V117 como base normativa principal.
3. O modelo oficial V179 passa a ser anexo metodológico normativo do contrato mestre.
4. O contrato passa a explicitar como regras vigentes:
   - decisão diária por pacotes;
   - pagamento obrigatório e integral na data da planilha;
   - filtragem prévia por disponibilidade, liquidez, resgate e carência;
   - pós-vencimento como fonte disponível do dia;
   - switching apenas nas formas individual, agrupado combinatório e integral;
   - regra global do dia para residual na fase de pagamento;
   - cronologia intradiária por pacote;
   - convenções de governança documental.
5. V117 e V108 permanecem preservados apenas como contexto histórico/documental intermediário.
## Arquivos ajustados
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/documentacao_baseline/` pode ser removida se os documentos granulares não tiverem autoridade normativa ativa superior aos documentos atuais.

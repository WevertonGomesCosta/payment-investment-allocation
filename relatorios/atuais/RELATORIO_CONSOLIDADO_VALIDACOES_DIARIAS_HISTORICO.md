# Relatório consolidado — histórico de validações diárias

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/validacoes_diarias/` em um único relatório atual, preservando a trilha de validações diárias sem manter arquivos granulares.

- Arquivos consolidados: 8
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Linhas | Título |
|---|---:|---|
| `relatorios/historico/validacoes_diarias/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md` | 30 | Contrato suplementar — pós-vencimento e gate de switching diário (V177) |
| `relatorios/historico/validacoes_diarias/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md` | 51 | Contrato suplementar de validação diária orientada ao objetivo final — V176 |
| `relatorios/historico/validacoes_diarias/CORRECAO_POS_VENCIMENTO_GATE_SWITCHING_V177.md` | 25 | Correção da materialização pós-vencimento e do gate de execução diária — V177 |
| `relatorios/historico/validacoes_diarias/REORGANIZACAO_VALIDACAO_DIARIA_V176.md` | 31 | Reorganização do projeto e reforma do runner diário — V176 |
| `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V175_2026-04-23_2026-05-23.md` | 44 | Validação diária operacional V175 (2026-04-23 a 2026-05-23) |
| `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V176_2026-04-23_2026-05-23.md` | 20 | Validação diária operacional V176 |
| `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V177_2026-04-23_2026-05-23.md` | 10 | Validação diária operacional — V177 |
| `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V178_2026-04-23_2026-05-23.md` | 72 | Atualização de cache/dados e reexecução da análise — V178 |

## Interpretação consolidada

| Tema | Informação preservada |
|---|---|
| Validação diária | Histórico de execuções e auditorias diárias preservado em forma consolidada. |
| Runner diário | Registros ligados ao runner de validação diária permanecem rastreáveis. |
| Pagamentos e switching | Evidências históricas relacionadas à validação diária do fluxo de pagamentos/switching foram preservadas. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/validacoes_diarias/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`

- Título: Contrato suplementar — pós-vencimento e gate de switching diário (V177)
- Linhas originais: 30

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato suplementar — pós-vencimento e gate de switching diário (V177)
## Objetivo
Fixar duas invariantes operacionais para evitar regressões na validação diária:
1. lotes normalizados por pós-vencimento devem permanecer auditáveis no próprio dia da conversão e nos dias seguintes;
2. em dias sem pagamento, o melhor cenário diário promovível de switching deve ser executado pelo runner de validação, e não neutralizado por uma comparação posterior de pacote.
## Invariantes obrigatórias
### 1) Pós-vencimento auditável
Quando `_normalizar_lote_pos_vencimento_no_dia(...)` converter um lote aportado em recebido disponível:
- o runner diário deve registrar o item em `lotes_normalizados_pos_vencimento`;
- o lote monitorado deve continuar visível em `lotes_monitorados`;
- `valor_relevante` deve refletir `valor_disponivel` quando `valor_liquido_resgatavel` não existir;
- `origem_pos_vencimento` e `data_vencimento_origem` devem permanecer auditáveis.
### 2) Gate de switching diário promovível
Em dias sem pagamento:
- se existir `melhor_cenario_promovivel` com `promovivel_hibrido=True`,
- e existir pacote `switch_only` correspondente,
- o runner diário deve executar esse pacote como vencedor do dia.
Esse override é restrito aos dias sem pagamento nesta versão. Em dias com pagamento, a comparação entre `pay_only` e `switch_then_pay` permanece ativa.
```

</details>

### `relatorios/historico/validacoes_diarias/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`

- Título: Contrato suplementar de validação diária orientada ao objetivo final — V176
- Linhas originais: 51

<details>
<summary>Trecho inicial preservado</summary>

```text
# Contrato suplementar de validação diária orientada ao objetivo final — V176
Este documento complementa `CONTRATO_OPERACIONAL_PROJETO.md` e existe para evitar regressões de interpretação entre:
- o **contrato executável vigente** da baseline;
- e o **objetivo final do projeto**, que continua sendo o critério correto para validar saídas user-facing de pagamentos e switching.
## 1. Regra de leitura obrigatória
1. Toda validação diária user-facing deve ser interpretada contra o **objetivo final do projeto**: maximizar patrimônio líquido terminal com auditabilidade por lote/fonte.
2. Uma saída resumida que não exponha componentes reais dos pagamentos, fontes efetivas e cenários de switching não é suficiente para validação manual.
3. O fato de uma camada vigente ainda ser limitada não autoriza apresentar uma saída simplificada como se ela já representasse o motor conjunto final.
## 2. Guardrails obrigatórios de não regressão
4. Nenhum lote ou recebido futuro pode aparecer como **operacionalmente disponível** antes do dia corrente da validação.
5. O runner diário deve avançar por **dia 0, dia +1, dia +2, ...**, e não apenas por dias com pagamento.
6. Switching deve ser avaliado diariamente, inclusive em dias sem pagamento.
7. Lotes pós-vencimento que se tornam caixa ou ficam elegíveis no dia correto devem aparecer explicitamente no estado diário e competir nas decisões.
8. Saídas de pagamento devem expor:
   - fonte principal escolhida;
   - componentes reais utilizados;
   - quadro auditável de fontes candidatas relevantes;
   - custo fiscal, perda terminal e penalidades relevantes.
```

</details>

### `relatorios/historico/validacoes_diarias/CORRECAO_POS_VENCIMENTO_GATE_SWITCHING_V177.md`

- Título: Correção da materialização pós-vencimento e do gate de execução diária — V177
- Linhas originais: 25

<details>
<summary>Trecho inicial preservado</summary>

```text
# Correção da materialização pós-vencimento e do gate de execução diária — V177
## Correções aplicadas
1. `nucleo/runner_validacao_diaria_operacional_v177.py` passou a expor:
   - `lotes_normalizados_pos_vencimento`;
   - `recebidos_ativados_no_dia`;
   - `gate_execucao_switching_diario`;
   - `lotes_monitorados` com `valor_disponivel`, `origem_pos_vencimento` e `data_vencimento_origem`.
2. Em dias sem pagamento, o runner agora promove `switch_only` quando existir `melhor_cenario_promovivel`.
## Evidência objetiva
### 2026-04-23
- melhor cenário promovível: `Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)`;
- gate: `override_promovivel_sem_pagamento`;
- switching executado: `True`.
### 2026-05-04
- `lotes_normalizados_pos_vencimento` passou a registrar explicitamente os dois lotes `3000 mar.`;
- `lotes_monitorados` passou a mostrar `valor_relevante` e `valor_disponivel` corretos após o vencimento.
## Observação metodológica
A V177 altera a trajetória da janela curta porque o switching promovível de 2026-04-23 passa a ser efetivamente executado. Por isso, dias posteriores não devem ser comparados diretamente com a V176 sem considerar essa nova trajetória.
```

</details>

### `relatorios/historico/validacoes_diarias/REORGANIZACAO_VALIDACAO_DIARIA_V176.md`

- Título: Reorganização do projeto e reforma do runner diário — V176
- Linhas originais: 31

<details>
<summary>Trecho inicial preservado</summary>

```text
# Reorganização do projeto e reforma do runner diário — V176
## Objetivo da V176
A V176 reorganiza a camada documental e a validação diária para evitar regressões entre:
- o contrato executável mínimo da baseline vigente;
- e o objetivo final do projeto, que continua sendo a referência correta para validar pagamentos e switching.
## O que foi feito
1. Foi adicionado o contrato suplementar `CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`.
2. Foi adicionada a auditoria `AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md`.
3. O `README.md`, o `LEIA-ME_OPERACIONAL.md` e o `INDICE_RELATORIOS.md` foram atualizados para destacar essa leitura obrigatória.
4. Foi criado o runner `nucleo/runner_validacao_diaria_operacional_v176.py`.
5. Foi criado o script `scripts/diagnostico/inspecionar_validacao_diaria_operacional_v176.py`.
## Correções materiais do runner em relação à V175
1. A promovibilidade dos cenários passou a usar `promovivel_hibrido` e `escolher_melhor_cenario_promovivel(...)`.
2. O runner agora expõe, por dia:
   - componentes reais do pagamento vencedor;
   - fontes candidatas ordenadas do pagamento;
   - ações candidatas de switching;
   - cenários classificados;
```

</details>

### `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V175_2026-04-23_2026-05-23.md`

- Título: Validação diária operacional V175 (2026-04-23 a 2026-05-23)
- Linhas originais: 44

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação diária operacional V175 (2026-04-23 a 2026-05-23)
## Correções aplicadas
1. **Elegibilidade temporal operacional**
   - `materializar_decisao_local_v1(...)` agora aplica filtro explícito de disponibilidade na data de referência.
   - `carregar_recomputacao_sequencial_central_v1(...)` agora remove candidatos não elegíveis operacionalmente antes da comparação central.
   - `carregar_motor_recomendacao_pagamentos_switching_v1(...)` agora filtra `quadro_fontes` pela disponibilidade operacional na data de referência.
2. **Runner diário de validação**
   - Novo módulo: `nucleo/runner_validacao_diaria_operacional_v175.py`
   - Novo script: `scripts/validar_janela_diaria_operacional_v175.py`
   - Janela validada: `2026-04-23` até `2026-05-23`
## Resultado factual da execução
Resumo do JSON gerado:
- dias no horizonte: **31**
- dias com pagamento: **9**
- dias sem pagamento: **22**
- dias com ações candidatas de switching: **30**
- dias com cenários promovíveis: **0**
- dias com switching executado: **0**
```

</details>

### `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V176_2026-04-23_2026-05-23.md`

- Título: Validação diária operacional V176
- Linhas originais: 20

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação diária operacional V176
- Janela: 2026-04-23 até 2026-05-23
- Dias no horizonte: 31
- Dias com pagamento: 9
- Dias com ações candidatas de switching: 31
- Dias com cenários promovíveis: 25
- Dias com switching executado: 2
- Pagamentos no horizonte: 13
- Inconsistências temporais no estado: 0
## Famílias avaliadas
- agrupado_integral_parametrizado: 54
- individual_integral_parametrizado: 147
## Classes híbridas avaliadas
- dominado_pelo_baseline: 14
- vencedor_terminal: 187
JSON detalhado: `saidas/validacao_diaria_operacional_v176_2026-04-23_2026-05-23.json`
```

</details>

### `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V177_2026-04-23_2026-05-23.md`

- Título: Validação diária operacional — V177
- Linhas originais: 10

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação diária operacional — V177
- Janela: 2026-04-23 a 2026-05-23
- Dias com switching executado: 7
- Dias com normalização pós-vencimento: 2
- Inconsistências temporais no estado: 0
## Dias críticos
- 2026-04-23: switching promovível executado via gate `override_promovivel_sem_pagamento`.
- 2026-05-04: lotes `3000 mar.` normalizados pós-vencimento com trilha auditável explícita.
```

</details>

### `relatorios/historico/validacoes_diarias/VALIDACAO_DIARIA_OPERACIONAL_V178_2026-04-23_2026-05-23.md`

- Título: Atualização de cache/dados e reexecução da análise — V178
- Linhas originais: 72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Atualização de cache/dados e reexecução da análise — V178
## Escopo
- baseline operacional: V177
- repositório atualizado com o novo `dados/cache_bcb.json` e com a nova `dados/dados_financeiros.xlsx` enviada pelo usuário
- reexecução da validação diária: 2026-04-23 até 2026-05-23
- runner utilizado: `nucleo/runner_validacao_diaria_operacional_v177.py`
## Verificação dos insumos
- cache antigo: `data_final=2026-04-18`, `data_atualizacao=2026-04-18`
- cache novo: `data_final=2026-04-23`, `data_atualizacao=2026-04-23`
- novas datas efetivamente incorporadas ao cache: `2026-04-17`, `2026-04-20`, `2026-04-22`
- workbook enviado: idêntico byte a byte ao workbook já presente na V177
## Resultado global da reexecução
- data_inicio: 2026-04-23
- data_fim: 2026-05-23
- dias_no_horizonte: 31
- dias_com_pagamento: 9
- dias_sem_pagamento: 22
- dias_com_acoes_candidatas_switching: 31
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/validacoes_diarias/` pode ser removida se os documentos granulares não tiverem autoridade normativa ativa superior aos documentos atuais.

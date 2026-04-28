# Auditoria de conteúdo — HOTFIX_CONSOLE_IMPORTS_V205

## Objetivo

Comparar o conteúdo de `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md` contra as duas fontes que deram cobertura na auditoria anterior: `relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md` e `relatorios/atuais/LEIA-ME_OPERACIONAL.md`.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta auditoria não executa `git rm`.

## Arquivos comparados

- Alvo: `relatorios\atuais\HOTFIX_CONSOLE_IMPORTS_V205.md`
- Fonte de cobertura: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Fonte de cobertura: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`

## Resultado sintético

- Linhas relevantes avaliadas: 35
- Linhas de prioridade alta: 12
- Linhas seguras: 10
- Linhas com cobertura fraca: 14
- Linhas sem cobertura: 11
- Linhas de prioridade alta sem cobertura suficiente: 10
- Decisão final da auditoria: `NAO_REMOVER_AINDA`
- Justificativa: Há linhas de prioridade alta sem cobertura suficiente nas fontes comparadas.

## Tabela de cobertura linha a linha

| Ordem | Prioridade | Cobertura | Score | Risco | Linha alvo |
|---:|---|---|---:|---|---|
| 1 | `ALTA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | # HOTFIX_CONSOLE_IMPORTS_V205 |
| 2 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.667 | `RISCO_BAIXO_A_MEDIO` | Status: APLICADO |
| 3 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.667 | `RISCO_BAIXO_A_MEDIO` | Base fixa: V204 |
| 4 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.476 | `RISCO_BAIXO_A_MEDIO` | Nova versão: V205 |
| 5 | `MEDIA` | `NAO_COBERTA` | 0.435 | `RISCO_MEDIO` | ## Motivo |
| 6 | `BAIXA` | `COBERTA_FORTE_PARCIAL` | 1.0 | `RISCO_BAIXO` | Ao executar: |
| 7 | `ALTA` | `COBERTA_FRACA_PARCIAL` | 0.455 | `RISCO_ALTO` | python aplicacao/principal.py |
| 8 | `ALTA` | `NAO_COBERTA` | 0.378 | `RISCO_ALTO` | a V204 falhava com: |
| 9 | `ALTA` | `NAO_COBERTA` | 0.411 | `RISCO_ALTO` | NameError: name 'construir_tabela_iof' is not defined |
| 10 | `MEDIA` | `COBERTA_FRACA_PARCIAL` | 0.545 | `RISCO_BAIXO_A_MEDIO` | ## Causa |
| 11 | `ALTA` | `NAO_COBERTA` | 0.339 | `RISCO_ALTO` | Durante a limpeza final de governança da V204, o console teve código morto removido e imports foram reduzidos. Porém, a função ativa: |
| 12 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.513 | `RISCO_BAIXO_A_MEDIO` | _preparar_auditoria_detalhada_residuos(...) |
| 13 | `BAIXA` | `NAO_COBERTA` | 0.438 | `RISCO_MEDIO` | continua usando: |
| 14 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.5 | `RISCO_BAIXO_A_MEDIO` | construir_tabela_iof(...) |
| 15 | `BAIXA` | `COBERTA_FRACA_PARCIAL` | 0.5 | `RISCO_BAIXO_A_MEDIO` | construir_faixas_ir(...) |
| 16 | `ALTA` | `NAO_COBERTA` | 0.429 | `RISCO_ALTO` | Essas funções não estavam mais importadas em: |
| 17 | `ALTA` | `COBERTA_FRACA_PARCIAL` | 0.491 | `RISCO_ALTO` | aplicacao/console/principal.py |
| 18 | `MEDIA` | `COBERTA_FRACA_PARCIAL` | 0.688 | `RISCO_BAIXO_A_MEDIO` | ## Correção aplicada |
| 19 | `ALTA` | `NAO_COBERTA` | 0.395 | `RISCO_ALTO` | Foi restaurado somente o import explícito: |
| 20 | `ALTA` | `NAO_COBERTA` | 0.299 | `RISCO_ALTO` | from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof |
| 21 | `MEDIA` | `COBERTA_FRACA_PARCIAL` | 0.688 | `RISCO_BAIXO_A_MEDIO` | ## Escopo preservado |
| 22 | `BAIXA` | `COBERTA_FORTE_PARCIAL` | 0.857 | `RISCO_BAIXO` | Não foi alterado: |
| 23 | `ALTA` | `COBERTA_FRACA_PARCIAL` | 0.588 | `RISCO_ALTO` | - motor principal; |
| 24 | `BAIXA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | - contrato mestre; |
| 25 | `BAIXA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | - modelo matemático-estatístico-financeiro; |
| 26 | `BAIXA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | - regra de pagamentos; |
| 27 | `BAIXA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | - regra de switching; |
| 28 | `BAIXA` | `COBERTA_EXATA` | 1.0 | `RISCO_BAIXO` | - regra de recebidos/aportes futuros; |
| 29 | `BAIXA` | `COBERTA_FORTE_PARCIAL` | 0.833 | `RISCO_BAIXO` | - camada canônica de saída. |
| 30 | `MEDIA` | `COBERTA_FRACA_PARCIAL` | 0.5 | `RISCO_BAIXO_A_MEDIO` | ## Validação |
| 31 | `BAIXA` | `NAO_COBERTA` | 0.4 | `RISCO_MEDIO` | - análise estática da função: sem nomes globais indefinidos; |
| 32 | `BAIXA` | `NAO_COBERTA` | 0.376 | `RISCO_MEDIO` | - sintaxe Python dos arquivos `.py`: OK; |
| 33 | `ALTA` | `COBERTA_FRACA_PARCIAL` | 0.48 | `RISCO_ALTO` | - release checker: OK — V205. |
| 34 | `MEDIA` | `NAO_COBERTA` | 0.429 | `RISCO_MEDIO` | ## Classificação |
| 35 | `ALTA` | `COBERTA_FORTE_PARCIAL` | 0.868 | `RISCO_BAIXO` | HOTFIX_SEM_ALTERACAO_ECONOMICA |

## Linhas de maior atenção

### Linha 2

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: Status: APLICADO
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

### Linha 3

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: Base fixa: V204
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: - Base funcional fixa de origem: **V200**

### Linha 4

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: Nova versão: V205
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: # Governança estrutural V206

### Linha 5

- Prioridade: `MEDIA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_MEDIO`
- Linha alvo: ## Motivo
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: - motor econômico;

### Linha 7

- Prioridade: `ALTA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: python aplicacao/principal.py
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

### Linha 8

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: a V204 falhava com:
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: Não foram alterados:

### Linha 9

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: NameError: name 'construir_tabela_iof' is not defined
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: - Contrato mestre vigente: **CONTRATO_OPERACIONAL_PROJETO.md**

### Linha 10

- Prioridade: `MEDIA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: ## Causa
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Status

### Linha 11

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: Durante a limpeza final de governança da V204, o console teve código morto removido e imports foram reduzidos. Porém, a função ativa:
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: Essa centralização é estrutural. Ela não altera regra econômica, motor, contrato, modelo oficial nem recebidos/aportes futuros.

### Linha 12

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: _preparar_auditoria_detalhada_residuos(...)
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: - `AUDITORIA_LIMPEZA_RESIDUAL_V201.md`

### Linha 13

- Prioridade: `BAIXA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_MEDIO`
- Linha alvo: continua usando:
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: - contrato mestre;

### Linha 14

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: construir_tabela_iof(...)
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: Console e planilha operacional devem consumir `construir_saida_canonica(...)`, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

### Linha 15

- Prioridade: `BAIXA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: construir_faixas_ir(...)
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: Console e planilha operacional devem consumir `construir_saida_canonica(...)`, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

### Linha 16

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: Essas funções não estavam mais importadas em:
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: ## V216 — frente funcional de aportes futuros

### Linha 17

- Prioridade: `ALTA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: aplicacao/console/principal.py
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: SEM_ALTERACAO_ECONOMICA

### Linha 18

- Prioridade: `MEDIA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: ## Correção aplicada
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

### Linha 19

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: Foi restaurado somente o import explícito:
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: ## V216 — frente funcional de aportes futuros

### Linha 20

- Prioridade: `ALTA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: from nucleo.nucleo_financeiro_minimo import construir_faixas_ir, construir_tabela_iof
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: Console e planilha operacional devem consumir `construir_saida_canonica(...)`, evitando recálculo paralelo de saldo, líquido, imposto, residual, switching e amostras financeiras.

### Linha 21

- Prioridade: `MEDIA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: ## Escopo preservado
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

### Linha 23

- Prioridade: `ALTA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: - motor principal;
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: - motor econômico;

### Linha 30

- Prioridade: `MEDIA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_BAIXO_A_MEDIO`
- Linha alvo: ## Validação
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

### Linha 31

- Prioridade: `BAIXA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_MEDIO`
- Linha alvo: - análise estática da função: sem nomes globais indefinidos;
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: - `ESPECIFICACAO_SAIDA_OFICIAL.md`

### Linha 32

- Prioridade: `BAIXA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_MEDIO`
- Linha alvo: - sintaxe Python dos arquivos `.py`: OK;
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: - Baseline pós-hotfix imediatamente anterior: **V205**

### Linha 33

- Prioridade: `ALTA`
- Cobertura: `COBERTA_FRACA_PARCIAL`
- Risco de remoção: `RISCO_ALTO`
- Linha alvo: - release checker: OK — V205.
- Melhor fonte: `relatorios\atuais\LEIA-ME_OPERACIONAL.md`
- Melhor trecho encontrado: # LEIA-ME operacional — V208

### Linha 34

- Prioridade: `MEDIA`
- Cobertura: `NAO_COBERTA`
- Risco de remoção: `RISCO_MEDIO`
- Linha alvo: ## Classificação
- Melhor fonte: `relatorios\atuais\GOVERNANCA_ESTRUTURAL_V206.md`
- Melhor trecho encontrado: ## Escopo aplicado

## Decisão desta etapa

A decisão documental desta auditoria é `NAO_REMOVER_AINDA`. Mesmo que o arquivo seja classificado como candidato, a remoção deve ocorrer apenas em etapa posterior, com commit próprio e após revisão do relatório gerado.

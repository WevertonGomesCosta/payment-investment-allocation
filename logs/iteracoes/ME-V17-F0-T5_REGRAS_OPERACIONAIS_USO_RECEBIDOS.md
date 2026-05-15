# ME-V17-F0-T5 — Auditoria de regras operacionais para uso diagnóstico de recebidos

## Identificação

- MICROETAPA: V17-F0-T.5
- TIPO: DIAGNÓSTICO / AUDITORIA DE REGRAS OPERACIONAIS
- BASELINE_DE_ENTRADA: 7589e1f
- T4_CONGELADA: sim
- T3_CONGELADA: sim
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Auditar quais regras operacionais precisariam existir antes de transformar qualquer cobertura diagnóstica por recebidos em fonte pagadora oficial.

Esta microetapa não altera fonte oficial, não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não altera motor econômico, não altera recomendador e não altera XLSX oficial.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py
- logs/iteracoes/ME-V17-F0-T5_REGRAS_OPERACIONAIS_USO_RECEBIDOS.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv
- saidas/diagnostico/resumo_auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv
- saidas/diagnostico/matriz_regras_operacionais_uso_recebidos_v17_f0_t5.csv

## Fonte de leitura

- saidas/diagnostico/auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv

## Regras auditadas

- R0: preservar fonte oficial já recomendada por lote.
- R1: definir precedência intradiária de recebidos.
- R2: exigir suficiência temporal competitiva.
- R3: separar fonte diagnóstica de fonte oficial.
- R4: criar ledger oficial de recebidos antes de promoção.
- R5: definir prioridade entre lotes, recebidos e aportes.

## Critérios de validação

Esperado:

- qtd_linhas_t4: 159
- qtd_pagamentos_aprovados_t5: 49
- qtd_pagamentos_sem_lote_t5: 110
- qtd_linhas_auditoria_t5: 159
- qtd_pode_converter_recebido_em_fonte_oficial_sim_t5: 0
- status_geral_t5: auditoria_regras_operacionais_uso_recebidos_gerada

## Restrições

- Não alterar motor econômico.
- Não alterar recomendador.
- Não alterar S.7.
- Não alterar T.0.
- Não alterar T.1.
- Não alterar T.2.
- Não alterar T.3.
- Não alterar T.4.
- Não alterar Q.
- Não alterar dados.
- Não alterar cache.
- Não alterar XLSX oficial.
- Não criar lote sugerido.
- Não criar status operacional oficial.
- Não aprovar pagamento.
- Não trocar fonte oficial dos 49 pagamentos aprovados.
- Não alocar recebido como fonte oficial.
- Não criar aporte planejado.
- Não materializar switching.

## Decisão

A preencher após execução local:

- T5_REGRAS_OPERACIONAIS_AUDITADAS: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- T4_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T6_FORMALIZAR_LEDGER_OFICIAL_DE_RECEBIDOS_SEM_ALTERAR_RECOMENDADOR

## Resultado observado

- fonte_competicao_t4: csv_t4
- qtd_linhas_t4: 159
- qtd_linhas_auditoria_t5: 159
- qtd_pagamentos_aprovados_t5: 49
- qtd_pagamentos_sem_lote_t5: 110
- qtd_mantidos_com_fonte_oficial_lote_t5: 49
- qtd_bloqueados_por_competicao_t5: 13
- qtd_bloqueados_por_intradiario_t5: 3
- qtd_candidatos_diagnosticos_resistentes_t5: 94
- qtd_sem_lote_candidatos_diagnosticos_t5: 94
- qtd_sem_lote_bloqueados_t5: 16
- qtd_pode_converter_recebido_em_fonte_oficial_sim_t5: 0
- qtd_pode_converter_recebido_em_fonte_oficial_nao_t5: 159
- qtd_pagamentos_usando_recebido_mesma_data_t5: 5
- qtd_regras_operacionais_formalizadas_t5: 6
- valor_candidatos_diagnosticos_t5: 61878.42
- valor_bloqueio_competitivo_t5: 9306.62
- status_geral_t5: auditoria_regras_operacionais_uso_recebidos_gerada

## Interpretação operacional

A T.5 formaliza que nenhum pagamento pode ser convertido para fonte oficial por recebidos neste estágio. Mesmo os 94 pagamentos sem lote que resistiram ao cenário competitivo permanecem apenas candidatos diagnósticos, pois ainda faltam ledger oficial de recebidos, separação formal entre fonte diagnóstica e fonte oficial e regra de prioridade entre lotes, recebidos e aportes.

## Achado crítico

- 49 pagamentos já aprovados devem manter fonte oficial por lote.
- 13 pagamentos sem lote ficaram bloqueados por insuficiência temporal competitiva.
- 3 pagamentos sem lote ficaram bloqueados até definição de precedência intradiária.
- 94 pagamentos sem lote ficaram como candidatos diagnósticos resistentes, sem promoção oficial.
- 0 pagamentos podem ser convertidos para fonte oficial por recebidos na T.5.

## Regras formalizadas

- R0: preservar fonte oficial já recomendada por lote.
- R1: definir precedência intradiária de recebidos.
- R2: exigir suficiência temporal competitiva.
- R3: separar fonte diagnóstica de fonte oficial.
- R4: criar ledger oficial de recebidos antes de promoção.
- R5: definir prioridade entre lotes, recebidos e aportes.

## Limite explícito

A T.5 não implementa motor oficial de recebidos, não altera recomendador, não altera XLSX oficial, não aprova pagamentos e não transforma recebidos em fonte pagadora oficial.

## Regressões

- status_geral_t4: auditoria_competicao_recebidos_49_aprovados_gerada
- status_geral_t3: alocacao_conjunta_recebidos_110_sem_lote_gerada
- status_geral_t2: reconciliacao_recebidos_concorrencia_110_sem_lote_gerada
- status_geral_t1: investigacao_fontes_temporais_110_sem_lote_gerada
- status_geral_t0: classificacao_110_sem_lote_gerada
- status_geral_s7i: tabela_operacional_integrada_xlsx
- status_geral_s7j: uso_operacional_tabela_pagamentos_auditado
- status_geral_s7h: tabela_operacional_diagnostica_estavel
- status_geral_s7g: tabela_operacional_pagamentos_gerada
- status_geral_s7f: recomendacoes_futuras_reconciliadas
- principal_py: verde
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- T4_REABERTA: não

# ME-V17-F0-T7 — Auditoria de precedência intradiária dos recebidos

## Identificação

- MICROETAPA: V17-F0-T.7
- TIPO: DIAGNÓSTICO / AUDITORIA DE PRECEDÊNCIA INTRADIÁRIA
- BASELINE_DE_ENTRADA: 45f489f
- T6_CONGELADA: sim
- T5_CONGELADA: sim
- T4_CONGELADA: sim
- T3_CONGELADA: sim
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Auditar os pagamentos cujo ledger diagnóstico T.6 consumiu recebidos na mesma data do pagamento, classificando se dependem de regra de precedência intradiária e se devem permanecer bloqueados.

Esta microetapa não altera fonte oficial, não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não altera motor econômico, não altera recomendador e não altera XLSX oficial.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/auditar_precedencia_intradiaria_recebidos_v17_f0_t7.py
- logs/iteracoes/ME-V17-F0-T7_PRECEDENCIA_INTRADIARIA_RECEBIDOS.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/auditoria_precedencia_intradiaria_recebidos_v17_f0_t7.csv
- saidas/diagnostico/resumo_precedencia_intradiaria_recebidos_v17_f0_t7.csv

## Fonte de leitura

- saidas/diagnostico/ledger_diagnostico_recebidos_v17_f0_t6.csv

## Critérios de validação

Esperado:

- qtd_pagamentos_same_day_t7: 5
- qtd_pode_promover_recebido_pos_t7_sim: 0
- qtd_pode_converter_recebido_t5_sim_em_same_day_t7: 0
- qtd_pagamentos_same_day_candidato_diagnostico_t7: 0
- qtd_pagamentos_same_day_classe_desconhecida_t7: 0
- qtd_inconsistencia_taxonomica_t7: 0
- status_geral_t7: auditoria_precedencia_intradiaria_recebidos_gerada

## Restrições

- Não alterar motor econômico.
- Não alterar recomendador.
- Não alterar S.7.
- Não alterar T.0.
- Não alterar T.1.
- Não alterar T.2.
- Não alterar T.3.
- Não alterar T.4.
- Não alterar T.5.
- Não alterar T.6.
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

- T7_PRECEDENCIA_INTRADIARIA_AUDITADA: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- T4_REABERTA: não
- T5_REABERTA: não
- T6_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T8_FORMALIZAR_CONTRATO_INTRADIARIO_RECEBIDOS_SEM_ALTERAR_RECOMENDADOR

## Resultado observado

- fonte_ledger_t6: csv_ledger_t6
- qtd_linhas_ledger_t6: 179
- qtd_eventos_consumo_t6: 154
- qtd_eventos_consumo_same_day_t7: 5
- qtd_pagamentos_same_day_t7: 5
- qtd_componentes_same_day_t7: 5
- valor_consumo_same_day_t7: 7229.18
- qtd_pagamentos_same_day_fonte_oficial_lote_t7: 2
- qtd_pagamentos_same_day_bloqueio_intradiario_t7: 3
- qtd_pagamentos_same_day_bloqueio_competitivo_t7: 0
- qtd_pagamentos_same_day_candidato_diagnostico_t7: 0
- qtd_pagamentos_same_day_classe_desconhecida_t7: 0
- qtd_inconsistencia_taxonomica_t7: 0
- qtd_pode_promover_recebido_pos_t7_sim: 0
- qtd_pode_converter_recebido_t5_sim_em_same_day_t7: 0
- status_geral_t7: auditoria_precedencia_intradiaria_recebidos_gerada

## Interpretação operacional

A T.7 confirmou que os 5 consumos same-day permanecem bloqueados para qualquer promoção operacional. Dois pagamentos já possuem fonte oficial por lote e três dependem de regra intradiária explícita. Nenhum pagamento same-day foi classificado como candidato diagnóstico, e nenhuma conversão para fonte oficial por recebidos foi autorizada.

## Achado crítico

- 5 pagamentos tiveram consumo diagnóstico de recebido na mesma data do pagamento.
- 2 desses pagamentos já possuem fonte oficial por lote.
- 3 dependem de regra de precedência intradiária.
- 0 podem ser promovidos para uso oficial de recebidos.
- 0 apresentam inconsistência taxonômica.
- 0 pertencem à classe candidato_diagnostico.

## Limite explícito

A T.7 é diagnóstica. Ela não define a precedência intradiária oficial, não altera recomendador, não altera XLSX oficial, não aprova pagamentos e não transforma recebidos em fonte pagadora oficial.

## Regressões

- status_geral_t6: ledger_diagnostico_recebidos_formalizado
- status_geral_t5: auditoria_regras_operacionais_uso_recebidos_gerada
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
- T5_REABERTA: não
- T6_REABERTA: não

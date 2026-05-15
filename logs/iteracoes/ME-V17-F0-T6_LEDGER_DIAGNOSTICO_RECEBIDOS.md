# ME-V17-F0-T6 — Formalização diagnóstica do ledger de recebidos

## Identificação

- MICROETAPA: V17-F0-T.6
- TIPO: DIAGNÓSTICO / FORMALIZAÇÃO DE LEDGER DE RECEBIDOS
- BASELINE_DE_ENTRADA: 89764f5
- T5_CONGELADA: sim
- T4_CONGELADA: sim
- T3_CONGELADA: sim
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Formalizar um ledger diagnóstico de recebidos, com entradas, disponibilidade temporal, consumo contrafactual, saldo remanescente e bloqueios herdados da T.5, sem transformar recebidos em fonte oficial.

Esta microetapa não altera fonte oficial, não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não altera motor econômico, não altera recomendador e não altera XLSX oficial.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py
- logs/iteracoes/ME-V17-F0-T6_LEDGER_DIAGNOSTICO_RECEBIDOS.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/ledger_diagnostico_recebidos_v17_f0_t6.csv
- saidas/diagnostico/resumo_ledger_diagnostico_recebidos_v17_f0_t6.csv
- saidas/diagnostico/resumo_pagamentos_ledger_diagnostico_recebidos_v17_f0_t6.csv

## Fontes de leitura

- dados/dados_financeiros.xlsx — aba Salários
- saidas/diagnostico/auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv
- saidas/diagnostico/auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv

## Convenção diagnóstica

O ledger T.6 registra:

- entrada_recebido_futuro;
- consumo_contrafactual_t4;
- saldo_recebido_apos_evento;
- bloqueios herdados da T.5;
- natureza_fonte_t6 sempre diagnóstica e não oficial.

## Critérios de validação

Esperado:

- qtd_linhas_t4: 159
- qtd_linhas_t5: 159
- qtd_eventos_entrada_recebido_t6: 25
- valor_total_entradas_recebidos_t6: 157474.26
- qtd_recebidos_com_saldo_negativo_t6: 0
- qtd_componentes_parse_error_t6: 0
- qtd_componentes_recebido_inexistente_t6: 0
- qtd_consumos_promovidos_oficialmente_t6: 0
- status_geral_t6: ledger_diagnostico_recebidos_formalizado

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

- T6_LEDGER_DIAGNOSTICO_FORMALIZADO: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- T4_REABERTA: não
- T5_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T7_AUDITAR_PRECEDENCIA_INTRADIARIA_DOS_RECEBIDOS_SEM_ALTERAR_RECOMENDADOR

## Resultado observado

- fonte_competicao_t4: csv_t4
- fonte_regras_t5: csv_t5
- qtd_linhas_t4: 159
- qtd_linhas_t5: 159
- qtd_eventos_ledger_t6: 179
- qtd_eventos_entrada_recebido_t6: 25
- qtd_eventos_consumo_contrafactual_t6: 154
- qtd_recebidos_futuros_no_ledger_t6: 25
- valor_total_entradas_recebidos_t6: 157474.26
- valor_total_consumo_diagnostico_t6: 151979.99
- saldo_final_recebidos_t6: 5494.27
- qtd_recebidos_com_saldo_negativo_t6: 0
- qtd_componentes_parse_error_t6: 0
- qtd_componentes_recebido_inexistente_t6: 0
- qtd_componentes_saldo_negativo_t6: 0
- qtd_pagamentos_com_consumo_diagnostico_t6: 139
- qtd_pagamentos_consumo_same_day_t6: 5
- qtd_consumos_promovidos_oficialmente_t6: 0
- qtd_pagamentos_consumo_fonte_oficial_lote_t6: 41
- qtd_pagamentos_consumo_candidato_diagnostico_t6: 94
- qtd_pagamentos_consumo_bloqueio_competitivo_t6: 1
- qtd_pagamentos_consumo_bloqueio_intradiario_t6: 3
- status_geral_t6: ledger_diagnostico_recebidos_formalizado

## Interpretação operacional

A T.6 formaliza um ledger diagnóstico de recebidos com entradas, consumos contrafactuais e saldos remanescentes. O ledger fecha financeiramente e preserva os bloqueios da T.5. Nenhum consumo foi promovido para fonte oficial.

## Fechamento financeiro

- entradas: 157474.26
- consumo diagnóstico: 151979.99
- saldo final: 5494.27
- conferência: 151979.99 + 5494.27 = 157474.26

## Achado crítico

- O ledger contém 25 eventos de entrada e 154 eventos de consumo contrafactual.
- Há 139 pagamentos com algum consumo diagnóstico.
- Há 5 pagamentos com consumo no mesmo dia do recebimento.
- Há 0 saldos negativos.
- Há 0 componentes com erro de parse.
- Há 0 recebidos inexistentes usados.
- Há 0 consumos promovidos oficialmente.

## Limite explícito

A T.6 é diagnóstica. Ela não implementa motor oficial de recebidos, não altera recomendador, não altera XLSX oficial, não aprova pagamentos e não transforma recebidos em fonte pagadora oficial.

## Regressões

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

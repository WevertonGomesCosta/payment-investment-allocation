# ME-V17-F0-T3 — Teste diagnóstico de alocação conjunta dos recebidos futuros

## Identificação

- MICROETAPA: V17-F0-T.3
- TIPO: DIAGNÓSTICO / SIMULAÇÃO DE ALOCAÇÃO CONJUNTA
- BASELINE_DE_ENTRADA: 01e57de
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Testar, de forma diagnóstica, uma alocação conjunta dos recebidos futuros contra os 110 pagamentos sem lote sugerido.

Esta microetapa não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não altera motor econômico e não altera a recomendação oficial.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/testar_alocacao_conjunta_recebidos_sem_lote_v17_f0_t3.py
- logs/iteracoes/ME-V17-F0-T3_ALOCACAO_CONJUNTA_RECEBIDOS_110_SEM_LOTE.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv
- saidas/diagnostico/resumo_alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv

## Fontes de leitura

- saidas/diagnostico/reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv
- dados/dados_financeiros.xlsx
- aba Salários

## Critérios de validação

Esperado:

- qtd_linhas_t2: 110
- qtd_linhas_alocadas_t3: 110
- qtd_linhas_nao_alocadas_t3: 0
- status_geral_t3: alocacao_conjunta_recebidos_110_sem_lote_gerada

## Restrições

- Não alterar motor econômico.
- Não alterar recomendador.
- Não alterar S.7.
- Não alterar T.0.
- Não alterar T.1.
- Não alterar T.2.
- Não alterar Q.
- Não alterar dados.
- Não alterar cache.
- Não alterar XLSX oficial.
- Não criar lote sugerido.
- Não criar status operacional oficial.
- Não aprovar pagamento.
- Não alocar recebido como fonte oficial.
- Não criar aporte planejado.
- Não materializar switching.

## Decisão

A preencher após execução local:

- T3_ALOCACAO_GERADA: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T4_AUDITAR_COMPETICAO_RECEBIDOS_COM_49_PAGAMENTOS_APROVADOS

## Resultado observado

- fonte_reconciliacao_t2: csv_t2
- qtd_linhas_t2: 110
- qtd_linhas_alocadas_t3: 110
- qtd_linhas_nao_alocadas_t3: 0
- qtd_cobertura_integral_t3: 110
- qtd_cobertura_parcial_t3: 0
- qtd_sem_cobertura_t3: 0
- valor_total_pagamentos_sem_lote_t3: 77185.04
- valor_total_alocado_recebidos_t3: 77185.04
- valor_total_deficit_t3: 0.0
- qtd_pagamentos_usando_recebido_mesma_data_t3: 0
- saldo_recebidos_futuros_nao_alocado_final_t3: 80289.22
- data_primeiro_deficit_alocacao_t3: nenhuma
- status_alocacao_diagnostica_t3: coberto_integralmente_por_recebidos_no_teste_diagnostico
- nivel_evidencia_t3: inferida_moderada
- status_geral_t3: alocacao_conjunta_recebidos_110_sem_lote_gerada

## Interpretação operacional

A T.3 indica que, no teste diagnóstico FIFO restrito aos 110 pagamentos sem lote sugerido, os recebidos futuros cobrem integralmente todos os pagamentos. Isso não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não define fonte oficial, não altera o XLSX oficial e não altera a recomendação oficial.

## Limite explícito

A T.3 não tratou ainda a competição dos recebidos futuros com os 49 pagamentos já aprovados com lote sugerido. Essa competição fica liberada para a T.4 em caráter diagnóstico.

## Regressões

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

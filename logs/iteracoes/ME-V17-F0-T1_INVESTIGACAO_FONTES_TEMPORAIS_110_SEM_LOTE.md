# ME-V17-F0-T1 — Investigação das fontes temporais dos 110 pagamentos sem lote sugerido

## Identificação

- MICROETAPA: V17-F0-T.1
- TIPO: DIAGNÓSTICO / INVESTIGAÇÃO TEMPORAL
- BASELINE_DE_ENTRADA: 0e3ad22
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Investigar, a partir da classificação T.0, quais dos 110 pagamentos sem lote sugerido apresentam evidência temporal associada a recebidos futuros, switching futuro, aporte planejado, saldo temporal cumulativo ou revisão cadastral.

Esta microetapa não aprova pagamento, não cria nova recomendação, não cria aporte, não materializa switching e não altera motor econômico.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/investigar_fontes_temporais_sem_lote_v17_f0_t1.py
- logs/iteracoes/ME-V17-F0-T1_INVESTIGACAO_FONTES_TEMPORAIS_110_SEM_LOTE.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv
- saidas/diagnostico/resumo_investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv

## Fontes de leitura

- saidas/diagnostico/classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv
- dados/dados_financeiros.xlsx
- aba Salários
- aba Switching

## Critérios de validação

Esperado:

- qtd_linhas_t0: 110
- qtd_linhas_investigadas_t1: 110
- qtd_linhas_nao_investigadas_t1: 0
- status_geral_t1: investigacao_fontes_temporais_110_sem_lote_gerada

## Restrições

- Não alterar motor econômico.
- Não alterar recomendador.
- Não alterar S.7.
- Não alterar T.0.
- Não alterar Q.
- Não alterar dados.
- Não alterar cache.
- Não alterar XLSX oficial.
- Não criar lote sugerido.
- Não criar status operacional.
- Não aprovar pagamento.

## Decisão

A preencher após execução local:

- T1_INVESTIGACAO_GERADA: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T2_RECONCILIAR_RECEBIDOS_FUTUROS_COM_CONCORRENCIA_DE_PAGAMENTOS

## Resultado observado

- fonte_classificacao_t0: csv_t0
- qtd_linhas_t0: 110
- qtd_linhas_investigadas_t1: 110
- qtd_linhas_nao_investigadas_t1: 0
- qtd_com_recebido_futuro_ate_data: 110
- qtd_sem_recebido_futuro_ate_data: 0
- qtd_com_switching_futuro_ate_data: 0
- qtd_com_evidencia_aporte_planejado: 0
- hipotese_temporal_t1: recebido_futuro_presente_ate_data_sem_alocacao_conjunta
- nivel_evidencia_t1: inferida_moderada
- status_geral_t1: investigacao_fontes_temporais_110_sem_lote_gerada

## Resumo das hipóteses T.1

- insuficiencia_temporal_explicita / saldo_fallback_positivo_mas_sem_fonte_auditavel / recebido_futuro_presente_ate_data_sem_alocacao_conjunta: 20
- insuficiencia_temporal_explicita / saldo_fallback_zero_ou_negativo / recebido_futuro_presente_ate_data_sem_alocacao_conjunta: 57
- sem_saldo_temporal_auditavel / sem_saldo_temporal_auditavel / recebido_futuro_presente_ate_data_sem_alocacao_conjunta: 33

## Interpretação operacional

A T.1 registra que os 110 pagamentos sem lote sugerido possuem recebidos futuros antes ou até suas datas, mas não valida dependência operacional, fonte auditável, suficiência conjunta, alocação entre pagamentos nem aprovação de pagamento.

## Regressões

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

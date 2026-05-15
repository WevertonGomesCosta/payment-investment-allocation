# ME-V17-F0-T0 — Classificação dos 110 pagamentos futuros sem lote sugerido

## Identificação

- MICROETAPA: V17-F0-T.0
- TIPO: DIAGNÓSTICO / CLASSIFICAÇÃO
- BASELINE_DE_ENTRADA: 57b2744
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Classificar os 110 pagamentos futuros sem lote sugerido em classes operacionais úteis, sem alterar motor econômico, recomendador, exportador, dados, cache, XLSX oficial, CSV canônico S.7-G ou regras econômicas.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/classificar_pagamentos_sem_lote_v17_f0_t0.py
- logs/iteracoes/ME-V17-F0-T0_CLASSIFICACAO_110_SEM_LOTE.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv
- saidas/diagnostico/resumo_classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv

## Fonte operacional

Fonte preferencial:

- saidas/oficial/relatorio_operacional_v225.xlsx
- aba: Tabela Operacional Pagamentos

Fallback:

- saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv

## Critérios de validação

Esperado:

- qtd_linhas_tabela_operacional: 159
- qtd_pagamentos_sem_lote_sugerido: 110
- qtd_sem_lote_classificados: 110
- qtd_sem_lote_nao_classificados: 0
- qtd_sem_lote_com_alerta_explicito: 110
- qtd_sem_lote_sem_alerta_explicito: 0
- status_geral_t0: classificacao_110_sem_lote_gerada

## Decisão

A preencher após execução local:

- T0_CLASSIFICACAO_GERADA: sim
- Q_REABERTA: não
- S7_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T1_INVESTIGAR_FONTES_TEMPORAIS_DOS_110_SEM_LOTE

## Resultado observado

- fonte_tabela_operacional: xlsx
- qtd_linhas_tabela_operacional: 159
- qtd_pagamentos_sem_lote_sugerido: 110
- qtd_sem_lote_com_alerta_explicito: 110
- qtd_sem_lote_sem_alerta_explicito: 0
- qtd_sem_lote_classificados: 110
- qtd_sem_lote_nao_classificados: 0
- qtd_classes_t0: 2
- status_geral_t0: classificacao_110_sem_lote_gerada

## Resumo das classes T.0

- insuficiencia_temporal_explicita / saldo_fallback_positivo_mas_sem_fonte_auditavel: 20
- insuficiencia_temporal_explicita / saldo_fallback_zero_ou_negativo: 57
- sem_saldo_temporal_auditavel / sem_saldo_temporal_auditavel: 33

## Regressões

- status_geral_s7i: tabela_operacional_integrada_xlsx
- status_geral_s7j: uso_operacional_tabela_pagamentos_auditado
- status_geral_s7h: tabela_operacional_diagnostica_estavel
- status_geral_s7g: tabela_operacional_pagamentos_gerada
- status_geral_s7f: recomendacoes_futuras_reconciliadas
- principal_py: verde
- Q_REABERTA: não
- S7_REABERTA: não

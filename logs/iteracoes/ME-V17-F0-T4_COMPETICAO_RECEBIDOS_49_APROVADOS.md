# ME-V17-F0-T4 — Auditoria de competição dos recebidos com os 49 pagamentos aprovados

## Identificação

- MICROETAPA: V17-F0-T.4
- TIPO: DIAGNÓSTICO / AUDITORIA DE COMPETIÇÃO TEMPORAL
- BASELINE_DE_ENTRADA: 9990980
- T3_CONGELADA: sim
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Auditar, de forma diagnóstica, se os recebidos futuros que cobrem os 110 pagamentos sem lote sugerido também competem temporalmente com os 49 pagamentos já aprovados com lote sugerido.

Esta microetapa não altera fonte oficial, não aprova pagamento, não cria lote sugerido, não cria aporte planejado, não materializa switching, não altera motor econômico, não altera recomendador e não altera XLSX oficial.

## Escopo

Arquivos versionáveis desta microetapa:

- scripts/diagnostico/auditar_competicao_recebidos_49_aprovados_v17_f0_t4.py
- logs/iteracoes/ME-V17-F0-T4_COMPETICAO_RECEBIDOS_49_APROVADOS.md

Artefatos diagnósticos não versionáveis:

- saidas/diagnostico/auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv
- saidas/diagnostico/resumo_auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv

## Fontes de leitura

- saidas/diagnostico/alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv
- saidas/oficial/relatorio_operacional_v225.xlsx
- aba Tabela Operacional Pagamentos
- dados/dados_financeiros.xlsx
- aba Salários

## Convenção diagnóstica

A T.4 simula uma competição contrafactual dos recebidos futuros usando ordenação temporal FIFO.

Na mesma data, a prioridade diagnóstica adotada é:

1. pagamentos já aprovados oficialmente com lote;
2. pagamentos sem lote testados na T.3.

Essa convenção é conservadora para testar se os 110 pagamentos sem lote ainda resistem quando os 49 pagamentos aprovados também consomem, de forma contrafactual, o pool de recebidos.

## Critérios de validação

Esperado:

- qtd_linhas_t3: 110
- qtd_pagamentos_aprovados_t4: 49
- qtd_pagamentos_sem_lote_t4: 110
- qtd_linhas_competicao_t4: 159
- status_geral_t4: auditoria_competicao_recebidos_49_aprovados_gerada

## Restrições

- Não alterar motor econômico.
- Não alterar recomendador.
- Não alterar S.7.
- Não alterar T.0.
- Não alterar T.1.
- Não alterar T.2.
- Não alterar T.3.
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

- T4_COMPETICAO_GERADA: sim
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T5_AUDITAR_REGRAS_OPERACIONAIS_PARA_USO_DIAGNOSTICO_DE_RECEBIDOS

## Resultado observado

- fonte_alocacao_t3: csv_t3
- qtd_linhas_t3: 110
- qtd_pagamentos_aprovados_t4: 49
- qtd_pagamentos_sem_lote_t4: 110
- qtd_linhas_competicao_t4: 159
- valor_total_aprovados_t4: 102826.35
- valor_total_sem_lote_t4: 77185.04
- valor_total_competicao_t4: 180011.39
- qtd_aprovados_cobertura_integral_t4: 33
- qtd_sem_lote_cobertura_integral_t4: 97
- deficit_total_aprovados_t4: 19681.98
- deficit_total_sem_lote_t4: 8349.42
- saldo_recebidos_futuros_nao_alocado_final_t4: 5494.27
- qtd_pagamentos_usando_recebido_mesma_data_t4: 5
- data_primeiro_deficit_competicao_t4: 2026-05-15
- data_primeiro_deficit_sem_lote_t4: 2026-08-20
- status_geral_t4: auditoria_competicao_recebidos_49_aprovados_gerada

## Interpretação operacional

A T.4 indica que a suficiência observada na T.3 era válida apenas no recorte isolado dos 110 pagamentos sem lote. Quando os 49 pagamentos já aprovados também entram, de forma contrafactual, na fila FIFO dos recebidos futuros, a cobertura integral dos 110 sem lote cai para 97 pagamentos.

Isso não invalida os 49 pagamentos aprovados, pois eles continuam oficialmente recomendados com lotes. A T.4 não troca fonte oficial, não aprova novos pagamentos e não altera recomendador.

## Achado crítico

- T.3 isolada: 110/110 pagamentos sem lote cobertos.
- T.4 competitiva: 97/110 pagamentos sem lote cobertos.
- Primeiro déficit dos sem lote em cenário competitivo: 2026-08-20.
- Há 5 pagamentos usando recebido na mesma data no teste competitivo, exigindo tratamento intradiário antes de qualquer uso operacional.

## Limite explícito

A T.4 é contrafactual e diagnóstica. Ela mede competição temporal pelo pool de recebidos, mas não define fonte pagadora oficial e não altera a tabela operacional oficial.

## Regressões

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

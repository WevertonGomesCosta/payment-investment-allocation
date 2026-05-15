# ME-V17-F0-S7I_INTEGRACAO_TABELA_OPERACIONAL_XLSX

## 1. Identificação
- MICROETAPA=V17-F0-S.7-I
- BASELINE_DE_ENTRADA_ESPERADA=5d34889
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=9814aded5939dbcc8bb5fd2450e9cdd4613078b7
- Q_REABERTA=nao

## 2. Objetivo
- integrar tabela operacional de pagamentos ao XLSX oficial como aba diagnóstica.

## 3. Arquivos alterados/criados
- exportador/gerador XLSX alterado: nucleo/gerar_planilha_operacional.py
- auditor S.7-I criado: scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py
- log S.7-I criado: logs/iteracoes/ME-V17-F0-S7I_INTEGRACAO_TABELA_OPERACIONAL_XLSX.md
- XLSX gerado, não versionado: indisponível no ambiente atual (falha do fluxo canônico por erro_csv_s6_ausente_sem_recomposicao_segura)

## 4. Nome da aba criada
- nome_aba_tabela_operacional=Tabela Operacional Pagamentos

## 5. Preservação das abas oficiais
- abas_oficiais_preservadas=nao_avaliavel_sem_xlsx
- abas_oficiais_ausentes=nao_avaliavel_sem_xlsx

## 6. Schema e linhas
- linhas=nao_avaliavel_sem_xlsx
- colunas=nao_avaliavel_sem_xlsx
- colunas_ausentes=nao_avaliavel_sem_xlsx
- status_aba=falha_integracao_tabela_operacional_xlsx

## 7. Comparação CSV S.7-G vs XLSX
- comparacao_csv_s7g_xlsx=nao_disponivel (xlsx não gerado)

## 8. Sentinelas
- cinco próximos pagamentos=nao_avaliavel_sem_xlsx
- dois alertas explícitos=nao_avaliavel_sem_xlsx

## 9. Contadores operacionais
- aprovados=nao_avaliavel_sem_xlsx
- multifonte=nao_avaliavel_sem_xlsx
- sem_lote=nao_avaliavel_sem_xlsx
- alertas=nao_avaliavel_sem_xlsx
- pos_switching=nao_avaliavel_sem_xlsx

## 10. Regressões
- S.7-H: status_geral_s7h=tabela_operacional_diagnostica_estavel
- S.7-G: status_geral_s7g=tabela_operacional_pagamentos_gerada
- S.7-F: matriz_status=erro_matriz_indisponivel; status_geral_s7f=falha_reconciliacao_s7f
- S.7-D: status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- Q.0: status_geral_integracao=switching_integrado_ok
- Q.1: status_geral_q1=sem_divergencia_observada
- Q.5/Q.5-B/C/D/E: lote_190_mai_no_expandido=sim; lote_3120_mai_no_expandido=sim; status_geral_q5b=consumo_pos_switching_integrado; status_geral_q5c=valoracao_pos_preservada; status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos; status_geral_q5e=ativos_pos_duplicados_consolidados

## 11. Hashes dados/cache
- antes_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- antes_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a
- depois_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- depois_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

## 12. Decisão
- S7I_INTEGRACAO_APROVADA=nao
- TABELA_OPERACIONAL_INTEGRADA_XLSX=nao
- Q_REABERTA=nao
- S7J_LIBERADA=nao

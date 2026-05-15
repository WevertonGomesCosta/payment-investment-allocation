# ME-V17-F0-S7J_AUDITORIA_USO_OPERACIONAL_TABELA_PAGAMENTOS

## 1. Identificação
- MICROETAPA=V17-F0-S.7-J
- BASELINE_DE_ENTRADA_ESPERADA=1055cc4
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=220c16df399cb1ed9f63f0042784c78a081708f6
- Q_REABERTA=nao

## 2. Objetivo
- auditar uso operacional da tabela de pagamentos.

## 3. Fonte da tabela
- fonte_tabela_operacional=indisponivel
- caminho_tabela_operacional=indisponivel
- tabela_operacional_carregada=nao
- observacao: XLSX ausente no ambiente e CSV S.7-G indisponível no momento de execução do S.7-J.

## 4. Visões geradas
- pagamentos aprovados imediatos: nao_gerado_por_fonte_indisponivel
- pagamentos multifonte: nao_gerado_por_fonte_indisponivel
- alertas explícitos: nao_gerado_por_fonte_indisponivel
- pagamentos sem lote sugerido: nao_gerado_por_fonte_indisponivel
- visão "qual lote usar": nao_gerado_por_fonte_indisponivel

## 5. Contadores principais
- aprovados=nao_disponivel
- multifonte=nao_disponivel
- sem_lote=nao_disponivel
- alertas=nao_disponivel
- pos_switching=nao_disponivel

## 6. Sentinelas
- cinco pagamentos aprovados=nao_avaliavel_sem_fonte
- dois alertas explícitos=nao_avaliavel_sem_fonte

## 7. Regressões
- S.7-I: status_geral_s7i=falha_integracao_tabela_operacional_xlsx (ambiente sem XLSX)
- S.7-H: status_geral_s7h=tabela_operacional_diagnostica_estavel
- S.7-G: status_geral_s7g=tabela_operacional_pagamentos_gerada; qtd_linhas_csv_s7g=159
- S.7-F: matriz_status=erro_matriz_indisponivel; status_geral_s7f=falha_reconciliacao_s7f
- S.7-D: status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- Q.0: status_geral_integracao=switching_integrado_ok
- Q.1: status_geral_q1=sem_divergencia_observada
- Q.5/Q.5-B/C/D/E: lote_190_mai_no_expandido=sim; lote_3120_mai_no_expandido=sim; status_geral_q5b=consumo_pos_switching_integrado; status_geral_q5c=valoracao_pos_preservada; status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos; status_geral_q5e=ativos_pos_duplicados_consolidados

## 8. Hashes dados/cache
- antes_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- antes_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a
- depois_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- depois_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

## 9. Decisão
- S7J_AUDITORIA_APROVADA=nao
- USO_OPERACIONAL_TABELA_PAGAMENTOS_VALIDADO=nao
- Q_REABERTA=nao
- S7K_LIBERADA=nao

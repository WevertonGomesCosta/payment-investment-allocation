# ME-V17-F0-S7G1_CORRECAO_VALORES_ALERTAS_TABELA_OPERACIONAL

1. Identificação
- MICROETAPA=V17-F0-S.7-G.1
- BASELINE_DE_ENTRADA_ESPERADA=7b0d154
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=5755fe1
- Q_REABERTA=nao

2. Objetivo
- corrigir escala monetária e classificação de alertas na tabela operacional S.7-G.

3. Problemas corrigidos
- escala monetária incorreta por normalização numérica que removia ponto decimal em valores já numéricos/escala brasileira.
- saldo_pos_pagamento incorreto por consequência direta da escala incorreta dos valores/saldos.
- alertas operacionais não classificados no ramo sem lote sugerido (não incrementava contador de alerta e não mapeava motivo explícito).

4. Arquivos alterados/criados
- scripts/diagnostico/gerar_tabela_operacional_pagamentos_v17_f0_s7g.py (alterado)
- logs/iteracoes/ME-V17-F0-S7G1_CORRECAO_VALORES_ALERTAS_TABELA_OPERACIONAL.md (criado)
- CSV S.7-G gerado não versionado: saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv

5. Indicadores antes/depois da correção
- antes: qtd_pagamentos_operacionais_avaliados=159
- antes: qtd_pagamentos_aprovados_para_pagamento=33
- antes: qtd_pagamentos_aprovados_multifonte=16
- antes: qtd_pagamentos_com_alerta_operacional_justificado=0
- antes: qtd_pagamentos_sem_lote_sugerido=110
- antes: qtd_pagamentos_com_saldo_temporal_insuficiente=0
- antes: qtd_pagamentos_com_lote_pos_switching_valido=14
- antes: qtd_componentes_lote_pos_switching_validos=16
- antes: qtd_pagamentos_multifonte=16
- antes: qtd_componentes_multifonte_total=32
- antes: qtd_linhas_csv_s7g=159
- antes: status_geral_s7g=tabela_operacional_pagamentos_gerada

- depois: qtd_pagamentos_operacionais_avaliados=159
- depois: qtd_pagamentos_aprovados_para_pagamento=33
- depois: qtd_pagamentos_aprovados_multifonte=16
- depois: qtd_pagamentos_com_alerta_operacional_justificado=110
- depois: qtd_pagamentos_sem_lote_sugerido=110
- depois: qtd_pagamentos_com_saldo_temporal_insuficiente=77
- depois: qtd_pagamentos_com_lote_pos_switching_valido=14
- depois: qtd_componentes_lote_pos_switching_validos=16
- depois: qtd_pagamentos_multifonte=16
- depois: qtd_componentes_multifonte_total=32
- depois: qtd_linhas_csv_s7g=159
- depois: status_geral_s7g=tabela_operacional_pagamentos_gerada

6. Amostra corrigida dos 5 próximos pagamentos
- 2026-05-15 | Internet | valor=132.40 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos_pagamento=2978.56
- 2026-05-20 | Cartão Azul | valor=5372.00 | lote=Lote 3120 mai + Lote 3000 mai Neon | status=aprovado_multifonte | acao=pagar_com_fontes_componentes | saldo_pos_pagamento=863.24
- 2026-05-20 | Condomínio | valor=113.31 | lote=Lote 3000 mai Neon | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos_pagamento=3010.97
- 2026-05-30 | Implante Velt | valor=400.00 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos_pagamento=2710.96
- 2026-06-02 | Cartão NU | valor=580.00 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos_pagamento=2530.96

7. Alertas operacionais detectados
- 2026-06-12 | Aluguel | alerta=sem_saldo_temporal_auditavel | status_operacional=alerta_operacional_justificado
- 2026-06-20 | Condomínio | alerta=sem_saldo_temporal_auditavel | status_operacional=alerta_operacional_justificado
- classificação por motivo/status inclui saldo_temporal_insuficiente_cumulativo quando presente em Status recomendação ou Motivo bloqueio lote.

8. Regressões
- S.7-F: status_geral_s7f=recomendacoes_futuras_reconciliadas
- S.7-D: status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- Q.0: status_geral_integracao=switching_integrado_ok; origens_migradas_usadas_indevidamente_total=0
- Q.1: status_geral_q1=sem_divergencia_observada
- Q.5/Q.5-B/C/D/E: lote_190_mai_no_expandido=sim; lote_3120_mai_no_expandido=sim; status_geral_q5b=consumo_pos_switching_integrado; status_geral_q5c=valoracao_pos_preservada; status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos; status_geral_q5e=ativos_pos_duplicados_consolidados

9. Hashes dados/cache
- antes: dados_financeiros.xlsx=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- antes: cache_bcb.json=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a
- depois: dados_financeiros.xlsx=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- depois: cache_bcb.json=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

10. Decisão
- S7G1_CORRECAO_APROVADA=sim
- TABELA_OPERACIONAL_S7G_APROVADA=sim
- Q_REABERTA=nao
- S7H_LIBERADA=sim

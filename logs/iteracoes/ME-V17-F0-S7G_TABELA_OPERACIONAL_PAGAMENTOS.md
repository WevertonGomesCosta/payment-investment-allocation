# ME-V17-F0-S7G_TABELA_OPERACIONAL_PAGAMENTOS

1. Identificação
- MICROETAPA=V17-F0-S.7-G
- BASELINE_DE_ENTRADA_ESPERADA=947c7a2
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=04e82fc
- Q_REABERTA=nao

2. Objetivo
- transformar reconciliação S.7-F em tabela operacional de pagamento.

3. Ajuste semântico
- contagem por pagamento: qtd_pagamentos_com_lote_pos_switching_valido=14; qtd_pagamentos_multifonte=16.
- contagem por componente/fonte: qtd_componentes_lote_pos_switching_validos=16; qtd_componentes_multifonte_total=32.

4. Arquivos criados
- scripts/diagnostico/gerar_tabela_operacional_pagamentos_v17_f0_s7g.py
- logs/iteracoes/ME-V17-F0-S7G_TABELA_OPERACIONAL_PAGAMENTOS.md
- CSV diagnóstico/operacional não versionado: saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv

5. Indicadores S.7-G
- qtd_pagamentos_operacionais_avaliados=159
- qtd_pagamentos_aprovados_para_pagamento=33
- qtd_pagamentos_aprovados_multifonte=16
- qtd_pagamentos_com_alerta_operacional_justificado=0
- qtd_pagamentos_sem_lote_sugerido=110
- qtd_pagamentos_com_fonte_bloqueada=0
- qtd_pagamentos_com_saldo_temporal_insuficiente=0
- qtd_pagamentos_com_lote_pos_switching_valido=14
- qtd_componentes_lote_pos_switching_validos=16
- qtd_pagamentos_multifonte=16
- qtd_componentes_multifonte_total=32
- qtd_lotes_sugeridos_alterados=0
- qtd_status_recomendacao_alterados=0
- qtd_linhas_csv_s7g=159
- csv_s7g=saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv
- status_geral_s7g=tabela_operacional_pagamentos_gerada

6. Amostra da tabela operacional (5 próximos pagamentos)
- 2026-05-15 | Internet | 1324.0 | Lote 3120 mai | aprovado_para_pagamento | pagar_com_lote_sugerido | saldo_pos=309772.0 | alerta=
- 2026-05-20 | Cartão Azul | 53720.0 | Lote 3120 mai + Lote 3000 mai Neon | aprovado_multifonte | pagar_com_fontes_componentes | saldo_pos=569804.0 | alerta=
- 2026-05-20 | Condomínio | 11331.0 | Lote 3000 mai Neon | aprovado_para_pagamento | pagar_com_lote_sugerido | saldo_pos=301097.0 | alerta=
- 2026-05-30 | Implante Velt | 4000.0 | Lote 3120 mai | aprovado_para_pagamento | pagar_com_lote_sugerido | saldo_pos=307096.0 | alerta=
- 2026-06-02 | Cartão NU | 5800.0 | Lote 3120 mai | aprovado_para_pagamento | pagar_com_lote_sugerido | saldo_pos=305296.0 | alerta=

7. Sentinelas
- Lote 190 mai: mantém estado exaurido por saque (S7D: exaurido_por_saque; S7F: exaurido_por_saque_pos_switching), sem promoção indevida a fonte ativa futura.
- Lote 3120 mai: ativo_pos_switching preservado, aparece nas recomendações futuras e pode compor pagamentos aprovados.

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

10. Artefatos não versionados
- CSV S.7-G em saidas/diagnostico
- CSVs diagnósticos dos auditores
- saidas/ e eventuais artefatos transitórios não versionados

11. Decisão
- S7G_TABELA_OPERACIONAL_APROVADA=sim
- Q_REABERTA=nao
- S7H_LIBERADA=sim

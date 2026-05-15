# ME-V17-F0-S7E_AUDITORIA_POS_S7D1_CONGELAMENTO_BASELINE_5D401E1

## 1) Identificação

- MICROETAPA=V17-F0-S.7-E
- TIPO=DOCUMENTAL / AUDITORIA POS-INTEGRACAO
- OBJETIVO=auditar S.7-D.1 pós-integração e congelar baseline operacional atual
- BASELINE_AUDITADA=5d401e1
- BRANCH=main
- Q_REABERTA=nao

## 2) Escopo

- altera_codigo=nao
- altera_motor=nao
- altera_recomendador=nao
- altera_switching=nao
- altera_ranking=nao
- altera_Q=nao
- altera_dados_cache=nao
- cria_log_documental=sim

## 3) Diagnóstico Git

- branch=main
- HEAD=5d401e1e4136f74894a7bdb916bcc3aa3a916a45
- origin/main=5d401e1e4136f74894a7bdb916bcc3aa3a916a45
- working_tree_inicial=limpo
- status_inicial=main...origin/main

## 4) Resultado S.7-D atualizado

- auditor= scripts/diagnostico/auditar_patrimonio_rendimento_lotes_consumidos_v17_f0_s7d.py
- py_compile=ok
- status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- qtd_lotes_com_pagamento_passado_detectado=10
- qtd_lotes_consumidos_com_liq_sacado_zerado_antes=2
- qtd_lotes_consumidos_corrigidos=2
- qtd_lotes_com_patrimonio_liquido_recalculado=10
- qtd_lotes_com_rendimento_liquido_recalculado=10
- qtd_lotes_multifonte_sem_rateio_auditavel=0
- qtd_linhas_extrato_futuro_antes=159
- qtd_linhas_extrato_futuro_depois=159
- qtd_lotes_sugeridos_alterados=0
- qtd_status_recomendacao_alterados=0
- qtd_lotes_com_patr_liq_diferente_de_liq_sac_mais_liq_atual=0
- qtd_lotes_com_rend_liq_diferente_de_patr_liq_menos_orig=0

### Lote 190 mai

- sentinela_lote_190_ok=sim
- sentinela_lote_190_liq_sacado=192.89
- sentinela_lote_190_liq_atual=0.0
- sentinela_lote_190_patr_liq=192.89
- sentinela_lote_190_rend_liq=0.48
- sentinela_lote_190_status=exaurido_por_saque
- extrato_passado_lote_190_presente=sim
- extrato_passado_saldo_remanescente_190=0.0

### Lote 3120 mai

- sentinela_lote_3120_ok=sim
- sentinela_lote_3120_liq_sacado=24.0
- sentinela_lote_3120_liq_atual=3110.96
- sentinela_lote_3120_patr_liq=3134.96
- sentinela_lote_3120_rend_liq=12.43
- sentinela_lote_3120_status=ativo_pos_switching
- sentinela_lote_3120_formula_patr_ok=sim
- sentinela_lote_3120_formula_rend_ok=sim
- extrato_passado_lote_3120_presente=sim
- extrato_passado_saldo_remanescente_3120=3110.96

## 5) Resultado principal.py

- principal_py_executou=sim
- execução_sem_traceback=sim
- saida_operacional_gerada=sim
- data_referencia=2026-05-15
- dados_financeiros=download
- status_obtencao_planilha=ok
- dados_CDI_BCB=cache_local
- status_obtencao_CDI_BCB=cache_atualizado_sem_fetch
- cache_atualizado_para_referencia=sim
- ultima_data_com_fator_no_cache=2026-05-13
- data_confirmada_da_serie=2026-05-13

### Sentinelas no console

- lote_190_console_corrigido=sim
- lote_190_bruto_sac=192.89
- lote_190_liq_sac=192.89
- lote_190_patr_liq=192.89
- lote_190_rend_liq=0.48
- lote_3120_console_corrigido=sim
- lote_3120_bruto_sac=24.00
- lote_3120_liq_sac=24.00
- lote_3120_liq_atual=3110.96
- lote_3120_patr_liq=3134.96
- lote_3120_rend_liq=12.43
- lote_3120_formula_patrimonial=3134.96 = 24.00 + 3110.96
- lote_3120_formula_rendimento=12.43 = 3134.96 - 3122.53

## 6) Resultado XLSX

- caminho_xlsx=saidas/oficial/relatorio_operacional_v225.xlsx
- existe=sim
- aba=Situação Atual
- XLSX_LOTE_190_OK=sim
- XLSX_LOTE_3120_DINAMICO_OK=sim
- XLSX_S7D_OK=sim
- linha_lote_190=['Lote 190 mai', 192.41, 192.89, 192.89, 0, 0, 192.89, 0.48]
- linha_lote_3120=['Lote 3120 mai', 3122.53, 24, 24, 3114.54, 3110.96, 3134.96, 12.43]

## 7) Resultado Q.0/Q.1/Q.5

- Q_REABERTA=nao
- regressao_Q_observada=nao

### Q.0

- auditor=scripts/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.py
- status_geral_integracao=switching_integrado_ok
- pagamentos_usando_lote_pos_switching=14
- lotes_pos_switching_total=4
- origens_migradas_usadas_indevidamente_total=0
- cadeia_decisoria_localizada=sim

### Q.1

- auditor=scripts/diagnostico/auditar_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.py
- fonte_base_operacional_gastos_status=localizada_canonica
- qtd_pagamentos_passados_ok_usando_lote_pos_switching=2
- qtd_pagamentos_passados_pos_switching_presentes_extrato_passado=2
- qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado=0
- qtd_divergencias_baixa_pos_switching=0
- status_geral_q1=sem_divergencia_observada
- q1_alinhado_com_q0=sim
- dados_financeiros_modificado_apos_execucao=nao

### Q.5

- auditor=scripts/diagnostico/auditar_inventario_expandido_pos_switching_v17_f0_q5.py
- qtd_lotes_inventario_original=14
- qtd_lotes_pos_switching_normalizados=4
- qtd_lotes_inventario_expandido=18
- lote_190_mai_no_expandido=sim
- lote_3120_mai_no_expandido=sim
- qtd_lotes_pos_com_schema_valido=4
- qtd_lotes_pos_sem_produto_destino=0
- qtd_lotes_pos_sem_valor=0

### Q.5-B/C/D/E

- auditor=scripts/diagnostico/auditar_consumo_lotes_pos_switching_v17_f0_q5b.py
- qtd_pagamentos_passados_pos_detectados=2
- qtd_pagamentos_passados_pos_com_saldo_antes_preenchido=2
- qtd_pagamentos_passados_pos_com_saldo_remanescente_preenchido=2
- qtd_lotes_pos_exauridos_apos_consumo=1
- qtd_lotes_pos_ativos_com_saldo_abatido=1
- qtd_lotes_pos_com_valoracao_previa_usada=4
- status_geral_q5b=consumo_pos_switching_integrado
- status_geral_q5c=valoracao_pos_preservada
- status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos
- status_geral_q5e=ativos_pos_duplicados_consolidados
- qtd_lotes_pos_ativos_duplicados_emitidos=0
- lote_190_mai_saldo_remanescente=0.0
- lote_3120_mai_saldo_remanescente=3110.96
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

## 8) Hashes dados/cache

- dados/dados_financeiros.xlsx=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- dados/cache_bcb.json=b90d6e2be2f8afd67d6f2c67a05778b21464689abda5e6a00997d5983fdfb28b
- dados_financeiros_preservado=sim
- cache_bcb_preservado=sim

## 9) Estado Git final observado antes do log

- status_final=main...origin/main
- git_diff_stat=vazio
- git_diff_name_only=vazio
- codigo_alterado=nao
- dados_cache_alterados=nao
- xlsx_versionado=nao
- saidas_versionadas=nao

## 10) Decisão

- S7E_AUDITORIA_APROVADA=sim
- BASELINE_5D401E1_CONGELADA=sim
- Q_REABERTA=nao
- PROXIMA_ETAPA_LIBERADA=sim

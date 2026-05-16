# ME-V17-F0-U7-PRE — Auditoria de saldos da saída auxiliar

- MICROETAPA: V17-F0-U.7-PRE
- CLASSE: DIAGNÓSTICO / READ-ONLY / AUDITORIA DE SALDOS
- DATA_EXECUCAO_LOCAL: 2026-05-15 20:52:05
- BASELINE: main pós-merge da PR #336
- MICROETAPA_ANTERIOR: V17-F0-U.6
- STATUS_GERAL_U7PRE: `auditoria_saldos_saida_auxiliar_v17_f0_u7pre_gerada`
- DECISAO_SALDOS_U7PRE: `saldos_nao_aprovados_para_promocao`

## Objetivo

Auditar se os campos `saldo_fonte_considerado` e `saldo_remanescente_diagnostico` da saída auxiliar U.4/U.5/U.6 podem ser usados futuramente como saldo oficial por fonte.

A U.7-PRE não corrige saldos, não altera recomendador oficial, não altera motor econômico, não altera exportador oficial, não altera XLSX oficial, não altera dados/cache, não altera contrato/modelo e não implementa U.7 oficial.

## Fontes lidas

- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u4.xlsx`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_resumo.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_abas.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_campos.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_gates.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_bloqueios.csv`
- `logs\iteracoes\ME-V17-F0-U6_GOVERNANCA_PROMOCAO_SAIDA_AUXILIAR.md`
- `dados\dados_financeiros.xlsx`

## Artefatos diagnósticos locais gerados

- `saidas\diagnostico\auditoria_saldos_saida_auxiliar_v17_f0_u7pre_resumo.csv`
- `saidas\diagnostico\auditoria_saldos_saida_auxiliar_v17_f0_u7pre_linhas.csv`
- `saidas\diagnostico\auditoria_saldos_saida_auxiliar_v17_f0_u7pre_multifonte.csv`
- `saidas\diagnostico\auditoria_saldos_saida_auxiliar_v17_f0_u7pre_referencias.csv`
- `saidas\diagnostico\auditoria_saldos_saida_auxiliar_v17_f0_u7pre_bloqueios.csv`

## Contadores principais

- `qtd_linhas_operacionais_auditadas_u7pre`: `175`
- `qtd_linhas_multifonte_auditadas_u7pre`: `32`
- `qtd_pagamentos_multifonte_u7pre`: `16`
- `qtd_campos_saldo_auditados_u7pre`: `4`
- `qtd_linhas_com_referencia_liquida_real`: `0`
- `qtd_linhas_sem_referencia_liquida_real`: `175`
- `qtd_saldos_compativeis`: `0`
- `qtd_saldos_divergentes`: `0`
- `qtd_linhas_fifo_diagnosticas`: `109`
- `qtd_linhas_pendencia_nao_promovivel`: `1`
- `qtd_campos_saldo_exigem_precondicao_u6`: `4`
- `qtd_divergencias_governanca_u6`: `0`
- `qtd_bloqueios_saldo`: `3`
- `qtd_referencias_aceitas`: `2`
- `qtd_referencias_rejeitadas`: `273`
- `qtd_multifonte_cobertura_divergente`: `0`
- `maior_diferenca_cobertura_multifonte`: `0.0`
- `decisao_saldos_u7pre`: `saldos_nao_aprovados_para_promocao`
- `status_geral_u7pre`: `auditoria_saldos_saida_auxiliar_v17_f0_u7pre_gerada`

## Categorias de saldo em Linhas_Operacionais

- `linha_fifo_diagnostica_nao_promovivel`: `109`
- `linha_pendencia_nao_promovivel`: `1`
- `sem_referencia_liquida_real_auditavel`: `65`

## Referências de saldo líquido real avaliadas

- `dados/dados_financeiros.xlsx` / `aba=Inventário de Lotes`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditar_consumo_lotes_pos_switching_v17_f0_q5b.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5|qtd_colunas_saldo_liquido=3`
- `saidas\diagnostico\auditar_integracao_switching_pagamentos_v17_f0_q0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditar_inventario_expandido_pos_switching_v17_f0_q5.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=8|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_aderencia_contrato_modelo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4_resumo_mensal.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_aportes_planejados_v216_sintetico.csv` / `csv_diagnostico`: aceita=`sim`, motivo=``
- `saidas\diagnostico\auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5`
- `saidas\diagnostico\auditoria_baixa_lotes_pos_switching_pagamentos_v17_f0_q1_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_fluxo_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_funcoes_alvo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_recebidos_futuros.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=7|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_caixa_recebidos_auditaveis_v8_trechos_relevantes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_calculo_dias_duplicacoes_v218.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_calculo_dias_duplicacoes_v219.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_calculo_dias_lotes_v218_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_calculo_dias_lotes_v219_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_casos_A_decisao_local_v16i.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2`
- `saidas\diagnostico\auditoria_casos_A_decisao_local_v16i_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6_casos_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6_fontes_observaveis.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6_por_data.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_auditoria_fontes_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_casos_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_inventario_classificado.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_por_data.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_canonica_v6b_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_fontes_por_pagamento.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_linhas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_motor_recomendacao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_cobertura_temporal_recebidos_v14_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_comparacao_pacotes_diarios.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_consumo_funcional_recebidos_v16b_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_consumo_funcional_recebidos_v16b_casos_sem_saldo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4`
- `saidas\diagnostico\auditoria_consumo_funcional_recebidos_v16b_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contencao_v16c_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16c_casos_A_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16c_ids_comparativo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16c_origem_v16b.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16c_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contencao_v16d_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16d_casos_A_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16d_ids_comparativo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16d_origem_v16d.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16d_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contencao_v16f_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16f_casos_A_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16f_casos_B_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16f_ids_comparativo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16f_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contencao_v16g_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16g_casos_A_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16g_casos_B_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16g_ids_comparativo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16g_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contencao_v16h_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16h_casos_A_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16h_casos_B_status_atual.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16h_ids_comparativo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contencao_v16h_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_atributos_contexto.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_match_23_recebidos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_contexto_real_v11b_quadro_fontes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_quadro_recebidos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_saida_oficial.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_contexto_real_v11b_tentativas_carregamento.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_caso_A_prioridade_decisao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_caso_B_materializacao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_casos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_dataframes_contexto.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_fontes_recebidas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_decisao_materializacao_recebidos_v15_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_divergencias_salarios_recebidos_v17_f0_s1_mensal.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_divergencias_salarios_recebidos_v17_f0_s1_recebidos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_divergencias_salarios_recebidos_v17_f0_s1_salarios.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_fina_ponte_shadow_nan.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_bloqueios_candidatos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_eventos_fluxo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_recebidos_futuros.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_fluxo_recebidos_v9c_trecho_funcao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_gate_switching_casos_revisao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_gate_switching_casos_revisao_v2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_gate_switching_elegiveis_nao_promovidos_v2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_gate_switching_lote_destino.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_gate_switching_lote_destino_v2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_gate_switching_resumo_motivos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_gate_switching_resumo_motivos_v2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_idade_fiscal_lotes_v219_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=15|qtd_colunas_saldo_liquido=2`
- `saidas\diagnostico\auditoria_integracao_pagamento_switching_v1_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_integracao_pagamento_switching_v1_extrato_flags.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4`
- `saidas\diagnostico\auditoria_integracao_pagamento_switching_v1_matriz_por_data.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_integracao_pagamento_switching_v1_motivos_matriz_top.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_integracao_pagamento_switching_v1_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_lacuna_integracao_temporal_v17_f0_s2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_lote_5680_abr_v218_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_lote_5680_abr_v219_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_blocos_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_casos_B.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_fontes_B.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_materializacao_recebidos_ledger_v16_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_matriz_elegibilidade_fontes_v17_f0_s7b.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_matriz_pacotes_motor.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_origem_lote_sugerido_sem_saldo_v4_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_origem_lote_sugerido_sem_saldo_v4_casos_saida.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`referencia_sem_linhas_validas`
- `saidas\diagnostico\auditoria_origem_lote_sugerido_sem_saldo_v4_funcoes_candidatas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_origem_lote_sugerido_sem_saldo_v4_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_origem_lote_sugerido_sem_saldo_v4_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_origem_switchings_promovidos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`erro_leitura:EmptyDataError:No columns to parse from file`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_contexto_retorno.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_fluxo_estatico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_funcoes_candidatas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_materializacao_direta.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_runtime_objetos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pacote_fontes_v11_saida_oficial.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_ponte_matriz_vs_shadow.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_pos_v9_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pos_v9_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_pos_v9_recebidos_futuros.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_pos_v9_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pos_v9b_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_pos_v9b_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_pos_v9b_recebidos_futuros.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_pos_v9b_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_precedencia_intradiaria_recebidos_v17_f0_t7.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_abas_saida.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_chamadas_fluxo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_diagnostico_propagacao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_funcoes_candidatas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_recebidos_futuros.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_propagacao_recebidos_v10_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_ranking_estatico_vs_runtime.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_datas_sem_cobertura.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_funcoes_candidatas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_ocorrencias_codigo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_presenca_abas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_recebidos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=7|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_rastreamento_recebidos_futuros_v7_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`referencia_sem_linhas_validas`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_multifonte.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5|qtd_colunas_saldo_liquido=2`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_reconciliacao_temporal_v17_f0_s0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_reflexo_pos_switching_situacao_atual_v17_f0_q4.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3`
- `saidas\diagnostico\auditoria_reflexo_pos_switching_situacao_atual_v17_f0_q4_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_extrato_campos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=12|qtd_colunas_saldo_liquido=2`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_intersecao_pagamentos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_ledger_campos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_mapa_v13.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`chaves_de_referencia_duplicadas=145`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13b_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13c_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_fontes_v13c_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_campos_auditoria.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_contexto_fontes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_diagnostico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_eventos_relevantes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_funcoes_alvo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_v12_pacote_saida.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saida_canonica_v12_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saida_canonica_v12_saida_oficial.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saldo_temporal_lotes_v3_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_saldo_temporal_lotes_v3_primeiras_quebras.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saldo_temporal_lotes_v3_resumo_lotes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_saldo_temporal_lotes_v3_timeline.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_sem_cobertura_extrato_futuro_v2_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_sem_cobertura_extrato_futuro_v2_casos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_sem_cobertura_extrato_futuro_v2_por_data.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_sem_cobertura_extrato_futuro_v2_por_lote.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_sem_cobertura_extrato_futuro_v2_resumo_causas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_semantica_taxa_positiva_v3_casos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_semantica_taxa_positiva_v3_prioritarios.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_semantica_taxa_positiva_v3_produtos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_semantica_taxa_positiva_v3_tipos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_separacao_previsao_materializacao_v17_f0_s6.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_separacao_previsao_materializacao_v17_f0_s6_resumo_mensal.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_switchings_bloqueados.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_tesouro_ipca_confiabilidade_v4_casos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_tesouro_ipca_confiabilidade_v4_lotes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_tesouro_ipca_confiabilidade_v4_prioridade_modelagem.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_tesouro_ipca_confiabilidade_v4_produtos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_tesouro_ipca_p1_contrato_v5_casos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_tesouro_ipca_p1_contrato_v5_produtos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_tesouro_ipca_p1_contrato_v5_requisitos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_transicao_fonte_promovida_para_sem_saldo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=3`
- `saidas\diagnostico\auditoria_uso_operacional_tabela_pagamentos_v17_f0_s7j.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_7_casos_A_vazados.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=4|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_alertas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_fontes_recebidas_vazados.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_relacao_com_B.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=5|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\auditoria_vazamento_casos_A_v16e_timeline_relevante.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\candidatos_correcao_recomendador_pagamentos_v17_f0_u0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_classes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_matriz.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\debug_gatilhos_lote_sem_saldo_v16i1.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=2|sem_coluna_data_status_referencia`
- `saidas\diagnostico\diagnostico_baixa_resolutividade_abas_shapes.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\diagnostico_baixa_resolutividade_causas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\diagnostico_baixa_resolutividade_detalhe.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2`
- `saidas\diagnostico\diagnostico_baixa_resolutividade_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=7|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\diagnostico_lotes_shadow_vs_situacao.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`referencia_sem_linhas_validas`
- `saidas\diagnostico\diagnostico_switchings_materializados.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`erro_leitura:EmptyDataError:No columns to parse from file`
- `saidas\diagnostico\divergencias_motor_central_extrato_v241_detalhe.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=6|qtd_colunas_saldo_liquido=2`
- `saidas\diagnostico\divergencias_motor_central_extrato_v241_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\exportacao_auxiliar_pagamentos_v17_f0_u4_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\gate_economico_aportes_v220_alertas_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\gate_economico_aportes_v220_comparativo_pagamentos_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=7|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\gate_economico_aportes_v220_decisao_final_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\gate_economico_aportes_v220_lotes_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\gate_economico_aportes_v220_resumo_real.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\gate_equivalencia_switching_v17_f0_o1.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\gate_remocao_ponte_v17_f0_p0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\historico_aportes_planejados_v216_sintetico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0`
- `saidas\diagnostico\investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\ledger_diagnostico_recebidos_v17_f0_t6.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\lotes_planejados_promovidos_v216_sintetico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\matriz_auditoria_console_diagnostico_v216.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\matriz_regras_operacionais_uso_recebidos_v17_f0_t5.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\pagamentos_consumindo_lotes_planejados_v216_sintetico.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\primeira_quebra_causal.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=3|qtd_colunas_saldo_liquido=3`
- `saidas\diagnostico\reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_alocacao_conjunta_recebidos_110_sem_lote_v17_f0_t3.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_auditoria_competicao_recebidos_49_aprovados_v17_f0_t4.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_auditoria_regras_operacionais_uso_recebidos_v17_f0_t5.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_classificacao_110_pagamentos_sem_lote_v17_f0_t0.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\resumo_investigacao_fontes_temporais_110_sem_lote_v17_f0_t1.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\resumo_ledger_diagnostico_recebidos_v17_f0_t6.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_pagamentos_ledger_diagnostico_recebidos_v17_f0_t6.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_precedencia_intradiaria_recebidos_v17_f0_t7.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\resumo_reconciliacao_recebidos_concorrencia_110_sem_lote_v17_f0_t2.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `saidas\diagnostico\tabela_operacional_pagamentos_v17_f0_s7g.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=2`
- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_linhas.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_pagamentos.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0`
- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_resumo.csv` / `csv_diagnostico`: aceita=`nao`, motivo=`qtd_colunas_chave=0|qtd_colunas_saldo_liquido=0|sem_coluna_data_status_referencia`
- `referencias_consolidadas` / `validacao_final`: aceita=`sim`, motivo=``

## Bloqueios e pré-condições

- `linhas_sem_referencia_liquida_real`: qtd=`175`, classificacao=`bloqueante`
- `fifo_diagnostico_nao_promovivel`: qtd=`109`, classificacao=`bloqueante`
- `pendencia_nao_promovivel`: qtd=`1`, classificacao=`bloqueante`

## Interpretação

A decisão `saldos_nao_aprovados_para_promocao` é conservadora. A ausência de referência líquida real inequívoca, a presença de linhas FIFO diagnósticas, a existência de pendências ou qualquer divergência de saldo bloqueiam promoção oficial dos campos de saldo.

## Decisão normativa preservada

- XLSX auxiliar permanece diagnóstico.
- XLSX oficial não é alterado.
- Exportador oficial não é alterado.
- Motor econômico não é alterado.
- Recomendador oficial não é alterado.
- Nenhum saldo é corrigido.
- Nenhum campo de saldo é promovido automaticamente.
- Os 110 pagamentos sem lote sugerido permanecem bloqueados/pendentes.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte FIFO é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- S.7 e T.0–T.8 não são reabertos.

## Restrições preservadas

- `aplicacao/principal.py` não alterado.
- Motor econômico não alterado.
- Recomendador oficial não alterado.
- Exportador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.

## Status

`auditoria_saldos_saida_auxiliar_v17_f0_u7pre_gerada`

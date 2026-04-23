# ORGANIZAÇÃO FUNCIONAL DO REPOSITÓRIO V153

- Baseline operacional acessível no ambiente: `payment-investment-allocation_v151.zip`.
- Objetivo desta etapa: reorganização estrutural de baixo risco, preservando comportamento funcional e preparando refatoração posterior.
- Alterações aplicadas nesta entrega: remoção de `__pycache__` do pacote final e geração de inventário funcional completo por arquivo.

## Critérios adotados

1. Não alterar contratos do núcleo financeiro/pagamentos/switching nesta etapa.
2. Organizar primeiro por responsabilidade real de arquivo antes de mover lógica entre módulos.
3. Preparar uma trilha segura para extrações futuras sem quebrar imports legados.

## Panorama do repositório Python

- Arquivos Python auditados: **176**
- Arquivos no `nucleo/`: **44**
- Arquivos em `scripts/`: **123**
- Arquivos em `aplicacao/`: **9**

## Arquivos prioritários para reorganização funcional

### `nucleo/caixa_recebidos_auditaveis.py`
- Linhas: **2347**
- Funções: **41**
- Classes: CampoContrato, EstruturaContrato, PacoteRecebidosAuditaveis, PacoteFontesElegiveisPagamento, PacoteSaldoDisponivelGeral, PacoteDecisaoLocalV1
- Funções atuais:
  - `_campos_fonte_elegivel` (linha 62)
  - `_campos_recebido_auditavel` (linha 85)
  - `_campos_saldo_disponivel_geral` (linha 100)
  - `_campos_decisao_local_v1` (linha 121)
  - `obter_contrato_minimo_caixa_recebidos` (linha 133)
  - `validar_contrato_minimo_caixa_recebidos` (linha 181)
  - `_slug_recebido` (linha 213)
  - `_recebido_id` (linha 218)
  - `_slug_fonte` (linha 222)
  - `_fonte_id` (linha 227)
  - `_fonte_pagamento_id` (linha 231)
  - `_gastos_por_lote` (linha 235)
  - `_resumir_vinculos_pagamento` (linha 256)
  - `_classificar_recebido` (linha 295)
  - `materializar_recebidos_auditaveis` (linha 355)
  - `_indexar_inventario_por_lote` (linha 443)
  - `_pagamentos_alvo_f1_4` (linha 453)
  - `_linha_base_fonte_pagamento` (linha 468)
  - `_materializar_fontes_de_recebidos_por_pagamento` (linha 520)
  - `_materializar_fontes_de_replay_por_pagamento` (linha 654)
  - `materializar_saldo_disponivel_geral` (linha 742)
  - `_construir_mapa_produtos_proxy` (linha 882)
  - `_valor_float` (linha 901)
  - `_janela_excesso_proxy_v2` (linha 908)
  - `_score_proxy_economico_v2` (linha 912)
  - `_janela_excesso_proxy_v3` (linha 985)
  - `_score_proxy_economico_v3` (linha 989)
  - `_prioridade_tipo_fonte` (linha 1128)
  - `_prioridade_status_origem` (linha 1139)
  - `_janela_excesso_por_proxy` (linha 1150)
  - `_score_proxy_economico_por_versao` (linha 1157)
  - `_label_proxy_version` (linha 1164)
  - `_construir_candidatos_decisao_local_v1` (linha 1169)
  - `_selecionar_candidato_decisao_local_v1` (linha 1232)
  - `materializar_decisao_local_v1` (linha 1324)
  - `auditar_comparativo_proxy_v2_v3` (linha 1423)
  - `materializar_fontes_elegiveis_pagamento` (linha 1568)
  - `auditar_comparativo_proxy_v3_vs_hibrido_shadow` (linha 1675)
  - `auditar_divergencias_residuais_proxy_v3_vs_hibrido_shadow` (linha 1856)
  - `auditar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow` (linha 2012)
  - `auditar_transicao_dominante_proxy_v3_vs_hibrido_shadow` (linha 2165)
- Reorganização recomendada por blocos internos:
  - **contrato e schemas**: `CampoContrato`, `EstruturaContrato`, `Pacote*`, funções `_campos_*`, `obter_*`, `validar_*`
  - **materialização de recebidos/fontes**: `_slug_*`, `_recebido_id`, `_fonte_*`, `_gastos_por_lote`, `materializar_recebidos_auditaveis`, `materializar_fontes_elegiveis_pagamento`, `materializar_saldo_disponivel_geral`
  - **decisão local/proxy**: `_janela_excesso_*`, `_score_proxy_*`, `_prioridade_*`, `_construir_candidatos_decisao_local_v1`, `_selecionar_candidato_decisao_local_v1`, `materializar_decisao_local_v1`
  - **auditorias comparativas**: `auditar_*`

### `nucleo/simulador_central_eventos_v1.py`
- Linhas: **890**
- Funções: **20**
- Funções atuais:
  - `_coerce_date` (linha 18)
  - `_normalizar_proxy_terminal` (linha 33)
  - `_destinos_switch_elegiveis` (linha 43)
  - `_top_destino_switch` (linha 103)
  - `_mapa_produtos_proxy` (linha 108)
  - `_proxy_fallback_lote` (linha 155)
  - `_aliquota_ir_estimada` (linha 161)
  - `_estimar_imposto_resgate` (linha 174)
  - `_projetar_valor_terminal` (linha 183)
  - `_valor_terminal_estimado_lote` (linha 193)
  - `construir_estado_global_recorte_curto_v117` (linha 213)
  - `_politica_pos_vencimento` (linha 346)
  - `_normalizar_lote_pos_vencimento_no_dia` (linha 351)
  - `_ativar_recebidos_futuros_no_dia` (linha 411)
  - `_aplicar_switching_eventos` (linha 441)
  - `_consumir_componentes` (linha 628)
  - `_calcular_metrica` (linha 655)
  - `_patrimonio_terminal_proxy` (linha 693)
  - `simular_cenario_eventos_v1` (linha 704)
  - `rodar_integracao_funcional_minima_v117` (linha 820)
- Reorganização recomendada por blocos internos:
  - **coerção e projeção**: `_coerce_date`, `_normalizar_proxy_terminal`, `_projetar_valor_terminal`, `_valor_terminal_estimado_lote`
  - **construção/normalização do estado**: `construir_estado_global_recorte_curto_v117`, `_politica_pos_vencimento`, `_normalizar_lote_pos_vencimento_no_dia`, `_ativar_recebidos_futuros_no_dia`
  - **execução de eventos**: `_destinos_switch_elegiveis`, `_top_destino_switch`, `_aplicar_switching_eventos`, `_consumir_componentes`
  - **métricas e simulação**: `_calcular_metrica`, `_patrimonio_terminal_proxy`, `simular_cenario_eventos_v1`

### `nucleo/alocador_pagamentos_terminal_v1.py`
- Linhas: **691**
- Funções: **21**
- Classes: FontePagamentoCandidata
- Funções atuais:
  - `_coerce_date` (linha 49)
  - `_safe_float` (linha 64)
  - `_safe_str` (linha 73)
  - `_dias_idade_fonte` (linha 77)
  - `_montar_chave_decisao_final` (linha 83)
  - `_aplicar_heuristicas_script1` (linha 103)
  - `_valor_pagamento` (linha 144)
  - `_normalizar_proxy_terminal` (linha 153)
  - `_score_placeholder` (linha 160)
  - `_horizonte_terminal_dias` (linha 183)
  - `_perda_terminal_por_fonte` (linha 190)
  - `_normalizar_fonte` (linha 195)
  - `_proporcao_utilizada` (linha 205)
  - `_estimar_custo_fiscal_lote` (linha 211)
  - `_fonte_disponivel_na_data` (linha 233)
  - `_impacto_unitario_combo` (linha 244)
  - `_chave_combo_script1` (linha 253)
  - `_iterar_planos_switching` (linha 275)
  - `_plano_switching_promovivel` (linha 289)
  - `_estado_pos_switching` (linha 294)
  - `alocar_pagamento_terminal_v1` (linha 302)
- Reorganização recomendada por blocos internos:
  - **tipos e parsing**: `FontePagamentoCandidata`, `_coerce_date`, `_safe_float`, `_safe_str`
  - **score terminal e fiscal**: `_dias_idade_fonte`, `_valor_pagamento`, `_horizonte_terminal_dias`, `_perda_terminal_por_fonte`, `_estimar_custo_fiscal_lote`
  - **normalização e heurísticas**: `_normalizar_proxy_terminal`, `_normalizar_fonte`, `_aplicar_heuristicas_script1`, `_montar_chave_decisao_final`
  - **integração com switching**: `_iterar_planos_switching`, `_plano_switching_promovivel`, `_estado_pos_switching`

### `nucleo/motor_diario_conjunto_experimental_v143.py`
- Linhas: **549**
- Funções: **11**
- Classes: PacoteDiaResumoV143, DecisaoDiaV143, ResumoMotorV143
- Funções atuais:
  - `_ordenar_pagamentos` (linha 93)
  - `_combinar_metricas` (linha 105)
  - `_remover_pagamentos_ate_dia` (linha 120)
  - `_avaliar_continuacao_neutra` (linha 128)
  - `_melhor_plano_switching_diario_v143` (linha 172)
  - `_executar_pacote_dia` (linha 220)
  - `_chave_pacote` (linha 299)
  - `_chave_pacote_tau` (linha 303)
  - `_selecionar_vencedor_pacote` (linha 322)
  - `_carregar_estado_janela` (linha 328)
  - `rodar_motor_diario_conjunto_experimental_v143` (linha 359)
- Reorganização recomendada por blocos internos:
  - **tipos de saída**: `PacoteDiaResumoV143`, `DecisaoDiaV143`, `ResumoMotorV143`
  - **pré-processamento diário**: `_ordenar_pagamentos`, `_remover_pagamentos_ate_dia`, `_carregar_estado_janela`
  - **avaliação de pacotes**: `_avaliar_continuacao_neutra`, `_executar_pacote_dia`, `_combinar_metricas`
  - **seleção**: `_chave_pacote`, `_chave_pacote_tau`, `_selecionar_vencedor_pacote`, `_melhor_plano_switching_diario_v143`

### `nucleo/planejador_switching_temporal_v1.py`
- Linhas: **493**
- Funções: **9**
- Classes: AcaoSwitchingTemporalCandidata
- Funções atuais:
  - `_coerce_date` (linha 52)
  - `_normalizar_lote` (linha 67)
  - `_aliquota_ir_estimada` (linha 92)
  - `_estimar_custo_fiscal` (linha 105)
  - `_normalizar_proxy_terminal` (linha 114)
  - `_normalizar_retorno_anual` (linha 124)
  - `_projetar_valor_terminal` (linha 140)
  - `_somar_pagamentos_em_janela` (linha 150)
  - `planejar_switching_temporal_v1` (linha 168)
- Reorganização recomendada por blocos internos:
  - **tipos/coerção**: `AcaoSwitchingTemporalCandidata`, `_coerce_date`, `_normalizar_lote`
  - **custo e retorno**: `_aliquota_ir_estimada`, `_estimar_custo_fiscal`, `_normalizar_proxy_terminal`, `_normalizar_retorno_anual`, `_projetar_valor_terminal`
  - **planejamento**: `_somar_pagamentos_em_janela`, `planejar_switching_temporal_v1`

### `aplicacao/console/principal.py`
- Linhas: **747**
- Funções: **13**
- Funções atuais:
  - `_classificar_status_residuo` (linha 32)
  - `_preparar_auditoria_lotes_residuais` (linha 36)
  - `_preparar_auditoria_detalhada_residuos` (linha 90)
  - `_preparar_resumo_auditoria_detalhada_residuos` (linha 187)
  - `_preparar_tabela_lotes_situacao_atual` (linha 208)
  - `_preparar_tabela_recebidos_situacao_atual` (linha 265)
  - `main` (linha 290)
  - `_normalizar_texto_curto` (linha 486)
  - `_preparar_auditoria_metodo_pagamentos` (linha 493)
  - `_extrair_resumo_leitura_decisao` (linha 546)
  - `_calcular_resumo_financeiro_fonte` (linha 560)
  - `_preparar_amostras_pagamentos_console` (linha 607)
  - `_preparar_auditoria_recebimento_vs_aplicacao` (linha 698)
- Reorganização recomendada por blocos internos:
  - **preparação de auditorias e tabelas**: `_preparar_*`
  - **resumos auxiliares**: `_normalizar_texto_curto`, `_extrair_resumo_leitura_decisao`, `_calcular_resumo_financeiro_fonte`
  - **orquestração**: `main` no final do arquivo

## Reorganização imediata aplicada nesta entrega

- Remoção de `__pycache__` do repositório empacotado.
- Geração do inventário funcional completo em `saidas/diagnostico/inventario_funcoes_v153.json`.
- Criação de script reprodutível de inventário funcional.

## Próxima etapa segura recomendada

1. Extrair `caixa_recebidos_auditaveis.py` em quatro módulos mantendo wrapper de compatibilidade.
2. Extrair blocos de seleção do `motor_diario_conjunto_experimental_v143.py` para módulo próprio.
3. Extrair métricas/valoração de `simulador_central_eventos_v1.py` para reduzir risco de flattening futuro.
4. Só depois reorganizar os scripts de diagnóstico por famílias estáveis.

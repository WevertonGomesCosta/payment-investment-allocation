# Índice de Diagnósticos Ativos — ME-POST-GOV-03

## Status pós-classificação decisória

Este índice registra a classificação decisória dos scripts que haviam sido marcados como `TRANSITORIO_PENDENTE` após a ME-POST-GOV-02.

A decisão segue o GOV-01: scripts diagnósticos são transitórios; só permanecem como gates permanentes se forem explicitamente promovidos, estáveis, compatíveis com a rota canônica vigente e sem dependência de APIs removidas, `shadow`, `benchmark`, sentinelas ou `saidas/diagnostico/*` como fonte operacional.

## Gate permanente preservado

| Script | Classe GOV-01 | Decisão |
|---|---|---|
| `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` | `GATE_PERMANENTE` | `MANTER_COMO_GATE_PERMANENTE` |

## Diagnósticos transitórios classificados

Nenhum dos scripts abaixo foi promovido a gate permanente nesta microetapa. Todos permanecem proibidos como insumo operacional, norma superior, compatibilidade artificial ou dependência de `aplicacao/*` e `nucleo/*`.

| Script | Decisão ME-POST-GOV-03 | Justificativa |
|---|---|---|
| `scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de tabela operacional; não é gate permanente |
| `scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de lacunas de salários/recebidos; evidência já deve ser documental |
| `scripts/diagnostico/auditar_classes_divergencias_valores_v17_c10.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de divergências de valores; não deve alimentar runtime |
| `scripts/diagnostico/auditar_comparacao_pacotes_diarios.py` | `REMOVER_IMEDIATAMENTE` | comparador transitório sem classificação de gate permanente |
| `scripts/diagnostico/auditar_competicao_recebidos_49_aprovados_v17_f0_t4.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de competição de recebidos; preservar apenas como evidência se necessário |
| `scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | validação comparativa consumada; resultado deve ficar em log/relatório, não como script ativo |
| `scripts/diagnostico/auditar_divergencias_salarios_recebidos_v17_f0_s1.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de divergências; não é gate permanente |
| `scripts/diagnostico/auditar_duplicidades_code_nucleo_v17_e1_b.py` | `ARQUIVAR_FORA_ROTA_VIVA` | auditoria estrutural histórica; gate vivo já é V4Z |
| `scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | governança de promoção já deve ser evidência documental, não script ativo |
| `scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de lacuna temporal; não deve orientar runtime atual |
| `scripts/diagnostico/auditar_precedencia_intradiaria_recebidos_v17_f0_t7.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de precedência intradiária; decisão contratual deve estar em relatório/log |
| `scripts/diagnostico/auditar_recomendacoes_pagamento_v17_f0_u0.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico de recomendações antes da rota canônica; não promover como gate |
| `scripts/diagnostico/auditar_reconciliacao_temporal_v17_f0_s0.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de reconciliação temporal; não é gate permanente |
| `scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | regras operacionais devem ser preservadas em contrato/log, não em script transitório |
| `scripts/diagnostico/auditar_saida_canonica_v17_a4.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico da saída canônica; não é gate permanente |
| `scripts/diagnostico/auditar_saldos_saida_auxiliar_v17_f0_u7pre.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico auxiliar prévio; não deve permanecer na rota viva |
| `scripts/diagnostico/auditar_semantica_dados_v17_a3.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico semântico histórico; não é gate permanente |
| `scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | separação previsão/materialização deve estar em evidência estática e contrato, não script ativo |
| `scripts/diagnostico/auditar_tabela_operacional_pagamentos_v17_f0_s7h.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de tabela de pagamentos; não é gate permanente |
| `scripts/diagnostico/auditar_transicao_temporal_switching_v17_d0.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de transição temporal/switching; não é gate permanente |
| `scripts/diagnostico/auditar_uso_operacional_tabela_pagamentos_v17_f0_s7j.py` | `ARQUIVAR_FORA_ROTA_VIVA` | diagnóstico histórico de uso operacional; não é gate permanente |
| `scripts/diagnostico/checagem_pos_conflito_current.py` | `REMOVER_IMEDIATAMENTE` | script de conflito transitório e contextual; não deve permanecer em diagnóstico vivo |
| `scripts/diagnostico/classificar_bloqueios_v17_a0_2.py` | `ARQUIVAR_FORA_ROTA_VIVA` | classificador histórico de bloqueios; decisão deve ser evidência estática |
| `scripts/diagnostico/classificar_divergencias_pacote_saida_v17_c4.py` | `ARQUIVAR_FORA_ROTA_VIVA` | classificador histórico de divergências; não é gate permanente |
| `scripts/diagnostico/classificar_pagamentos_sem_lote_v17_f0_t0.py` | `ARQUIVAR_FORA_ROTA_VIVA` | classificador histórico de pagamentos sem lote; não é gate permanente |
| `scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | consolidação de matriz deve ser preservada como relatório/log, não script ativo |
| `scripts/diagnostico/consolidar_plano_migracao_v17_b0.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | plano de migração deve ser documento estático |
| `scripts/diagnostico/construir_taxonomia_v17_a2.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | taxonomia deve estar em documentação, não em script diagnóstico vivo |
| `scripts/diagnostico/desenhar_pacote_orquestrado_pre_saida_v17_b2.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | desenho de pacote deve ser especificação documental |
| `scripts/diagnostico/diagnosticar_baixa_resolutividade_extrato_futuro.py` | `REMOVER_IMEDIATAMENTE` | diagnóstico pontual sem promoção; não pertence à rota viva |
| `scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | explicitação de valores deve ser evidência estática/log |
| `scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py` | `ARQUIVAR_FORA_ROTA_VIVA` | exportador auxiliar diagnóstico; não é fonte operacional canônica |
| `scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | critérios de elegibilidade devem estar formalizados em contrato/log |
| `scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py` | `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | formalização de ledger diagnóstico deve ser evidência estática |
| `scripts/diagnostico/integrar_saida_operacional_pagamentos_multifonte_v17_f0_u3.py` | `ARQUIVAR_FORA_ROTA_VIVA` | integração auxiliar diagnóstica; não promover a runtime sem etapa própria |
| `scripts/diagnostico/investigar_fontes_temporais_sem_lote_v17_f0_t1.py` | `ARQUIVAR_FORA_ROTA_VIVA` | investigação histórica; não é gate permanente |
| `scripts/diagnostico/mapear_pontos_reescolha_v16j0.py` | `REMOVER_IMEDIATAMENTE` | mapeamento exploratório antigo; não pertence à rota viva atual |
| `scripts/diagnostico/reconciliar_recebidos_concorrencia_sem_lote_v17_f0_t2.py` | `ARQUIVAR_FORA_ROTA_VIVA` | reconciliação histórica; não é gate permanente |
| `scripts/diagnostico/testar_alocacao_conjunta_recebidos_sem_lote_v17_f0_t3.py` | `ARQUIVAR_FORA_ROTA_VIVA` | teste exploratório diagnóstico; não é gate permanente |
| `scripts/diagnostico/validar_canonizacao_v17_a1.py` | `ARQUIVAR_FORA_ROTA_VIVA` | validação histórica de canonização; gate vivo é V4Z |
| `scripts/diagnostico/validar_invariantes_extrato_futuro.py` | `ARQUIVAR_FORA_ROTA_VIVA` | validação histórica de invariantes; não promovida a gate permanente |

## Resumo da decisão

| Decisão | Quantidade |
|---|---:|
| `MANTER_COMO_GATE_PERMANENTE` | 1 |
| `ARQUIVAR_FORA_ROTA_VIVA` | 26 |
| `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | 11 |
| `REMOVER_IMEDIATAMENTE` | 4 |
| `PROMOVER_A_GATE_PERMANENTE` | 0 |

## Próxima ação após a ME-POST-GOV-03

Abrir uma microetapa subsequente para aplicar fisicamente as decisões acima, em lotes controlados, sem tocar em `aplicacao/*` ou `nucleo/*`.

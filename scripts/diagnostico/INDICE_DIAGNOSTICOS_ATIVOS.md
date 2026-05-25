# Índice de Diagnósticos Ativos — ME-POST-GOV-04A

## Status pós-remoções imediatas

Este índice registra o estado após a aplicação física das decisões `REMOVER_IMEDIATAMENTE` definidas na ME-POST-GOV-03.

A ME-POST-GOV-04A removeu somente os scripts classificados como `REMOVER_IMEDIATAMENTE`. Nenhum script classificado como `ARQUIVAR_FORA_ROTA_VIVA` ou `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` foi movido, removido ou alterado nesta microetapa.

## Gate permanente preservado

| Script | Classe GOV-01 | Decisão | Estado físico |
|---|---|---|---|
| `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` | `GATE_PERMANENTE` | `MANTER_COMO_GATE_PERMANENTE` | `PRESENTE` |

## Removidos fisicamente na ME-POST-GOV-04A

| Script | Decisão ME-POST-GOV-03 | Estado físico ME-POST-GOV-04A |
|---|---|---|
| `scripts/diagnostico/auditar_comparacao_pacotes_diarios.py` | `REMOVER_IMEDIATAMENTE` | `REMOVIDO` |
| `scripts/diagnostico/checagem_pos_conflito_current.py` | `REMOVER_IMEDIATAMENTE` | `REMOVIDO` |
| `scripts/diagnostico/diagnosticar_baixa_resolutividade_extrato_futuro.py` | `REMOVER_IMEDIATAMENTE` | `REMOVIDO` |
| `scripts/diagnostico/mapear_pontos_reescolha_v16j0.py` | `REMOVER_IMEDIATAMENTE` | `REMOVIDO` |

## Diagnósticos ainda pendentes de aplicação física futura

Os scripts abaixo permanecem fisicamente presentes no namespace `scripts/diagnostico/`, mas seguem proibidos como insumo operacional, norma superior, compatibilidade artificial ou gate permanente sem promoção formal.

### Classificados como `ARQUIVAR_FORA_ROTA_VIVA`

| Script | Estado físico |
|---|---|
| `scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_classes_divergencias_valores_v17_c10.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_competicao_recebidos_49_aprovados_v17_f0_t4.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_divergencias_salarios_recebidos_v17_f0_s1.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_duplicidades_code_nucleo_v17_e1_b.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_precedencia_intradiaria_recebidos_v17_f0_t7.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_recomendacoes_pagamento_v17_f0_u0.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_reconciliacao_temporal_v17_f0_s0.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_saida_canonica_v17_a4.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_saldos_saida_auxiliar_v17_f0_u7pre.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_semantica_dados_v17_a3.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_tabela_operacional_pagamentos_v17_f0_s7h.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_transicao_temporal_switching_v17_d0.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_uso_operacional_tabela_pagamentos_v17_f0_s7j.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/classificar_bloqueios_v17_a0_2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/classificar_divergencias_pacote_saida_v17_c4.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/classificar_pagamentos_sem_lote_v17_f0_t0.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/integrar_saida_operacional_pagamentos_multifonte_v17_f0_u3.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/investigar_fontes_temporais_sem_lote_v17_f0_t1.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/reconciliar_recebidos_concorrencia_sem_lote_v17_f0_t2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/testar_alocacao_conjunta_recebidos_sem_lote_v17_f0_t3.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/validar_canonizacao_v17_a1.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/validar_invariantes_extrato_futuro.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |

### Classificados como `SUBSTITUIR_POR_EVIDENCIA_ESTATICA`

| Script | Estado físico |
|---|---|
| `scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/consolidar_plano_migracao_v17_b0.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/construir_taxonomia_v17_a2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/desenhar_pacote_orquestrado_pre_saida_v17_b2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |
| `scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py` | `PRESENTE_AGUARDA_MICROETAPA_FUTURA` |

## Resumo do estado físico

| Classe | Quantidade |
|---|---:|
| `GATE_PERMANENTE_PRESENTE` | 1 |
| `REMOVER_IMEDIATAMENTE_REMOVIDO` | 4 |
| `ARQUIVAR_FORA_ROTA_VIVA_PENDENTE` | 26 |
| `SUBSTITUIR_POR_EVIDENCIA_ESTATICA_PENDENTE` | 11 |

## Próxima ação

Abrir microetapa futura para aplicar fisicamente o grupo `ARQUIVAR_FORA_ROTA_VIVA` em lotes controlados, sem tocar em `aplicacao/*`, `nucleo/*`, motor ou regra econômica.

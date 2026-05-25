# ME-V17-F0-DIAG1 — Limpeza de diagnósticos legados pós-limpeza bruta

Data: 2026-05-25

## Objetivo

Remover scripts diagnósticos consumados ou incompatíveis após a limpeza bruta das Etapas 1–4, preservando apenas gates permanentes explicitamente classificados.

## Gate permanente preservado

- `scripts/diagnostico/auditar_nucleo_vivo_v4z.py`

## Resumo da classificação

- Scripts classificados: 62
- Scripts removidos: 61
- Scripts mantidos como gate permanente: 1

- AVALIAR_SE_E_GATE_OU_HISTORICO: 2
- REMOVER_CONSUMADO_API_REMOVIDA: 37
- REMOVER_CONSUMADO_MODULO_REMOVIDO: 12
- REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO: 10

## Scripts removidos

- `scripts/diagnostico/auditar_aderencia_arquitetura_7e_v17_e0.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;modulo_matriz_pacotes_diarios
- `scripts/diagnostico/auditar_aderencia_v17_a0_1.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — modulo_motor_morto
- `scripts/diagnostico/auditar_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_casos_A_decisao_local_v16i.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_consumo_lotes_pos_switching_v17_f0_q5b.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_correcao_lote_3120_mai_v4p0a.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;modulo_motor_morto;benchmark_legado
- `scripts/diagnostico/auditar_estrutura_pre_etapa5_v4z2.py` — AVALIAR_SE_E_GATE_OU_HISTORICO — shadow_textual
- `scripts/diagnostico/auditar_fechamento_funcional_etapa4_v4q.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow;benchmark_legado
- `scripts/diagnostico/auditar_fechamento_saneado_etapa4_v4x.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_fronteiras_motor_saida_render_v17_e1_a.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — modulo_motor_morto
- `scripts/diagnostico/auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_inventario_expandido_pos_switching_v17_f0_q5.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_limpeza_controlada_residuos_v4t.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow;benchmark_legado
- `scripts/diagnostico/auditar_limpeza_saida_observavel_residuos_v4w.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_lote_3120_mai_estado_temporal_v4o.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_matriz_pacotes_motor.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;atributos_shadow_contexto;modulo_matriz_pacotes_diarios;benchmark_legado
- `scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_pacote_entrada_resolvida_operacional_v36b.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_pacote_saida_observavel_temporal_v4u.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_pagamentos_realizados_lote_3120_v4p0b.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_patrimonio_rendimento_lotes_consumidos_v17_f0_s7d.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_pos_promocao_gate_etapa2_v35c.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_preenchibilidade_pacote_pre_saida_v17_b3.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — modulo_motor_morto
- `scripts/diagnostico/auditar_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_reflexo_pos_switching_situacao_atual_v17_f0_q4.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow
- `scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;atributos_shadow_contexto;modulo_saida_canonica_ledger_shadow;benchmark_legado
- `scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;atributos_shadow_contexto;benchmark_legado
- `scripts/diagnostico/auditar_validacao_shadow_etapa2_contexto_v34e.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;atributos_shadow_contexto;benchmark_legado
- `scripts/diagnostico/auditoria_origem_switchings_promovidos.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;atributos_shadow_contexto;benchmark_legado
- `scripts/diagnostico/comparar_pacote_pre_saida_saida_canonica_v17_c3.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;atributos_shadow_contexto;benchmark_legado
- `scripts/diagnostico/definir_fonte_verdade_saida_v17_b1.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — modulo_motor_morto
- `scripts/diagnostico/gate_equivalencia_switching_v17_f0_o1.py` — REMOVER_CONSUMADO_MODULO_REMOVIDO — shadow_textual;kwargs_shadow;modulo_motor_morto;benchmark_legado
- `scripts/diagnostico/gate_remocao_ponte_v17_f0_p0.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/gerar_tabela_operacional_pagamentos_v17_f0_s7g.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_normalizacao_lotes_estado_temporal_v4k0.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_pacote_auditoria_temporal_v4g.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_pacote_estado_temporal_v4f.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_pacote_ledger_temporal_operacional_v4e.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_pacote_replay_passado_v4d.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_pacotes_temporais_agregados_saida_v4i.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_saida_canonica_parametro_temporal_shadow_v4n.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_saida_canonica_vs_pacotes_temporais_v4j.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_saida_controlada_temporal_shadow_v4l.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow;benchmark_legado
- `scripts/diagnostico/historico/etapa4/auditar_saida_temporal_shadow_v4k.py` — REMOVER_OU_PRESERVAR_APENAS_RELATORIO_HISTORICO — shadow_textual;kwargs_shadow;modulo_saida_canonica_temporal_shadow;benchmark_legado
- `scripts/diagnostico/priorizar_bloqueios_v17_a0_3.py` — AVALIAR_SE_E_GATE_OU_HISTORICO — shadow_textual
- `scripts/diagnostico/reconciliar_universo_casos_A_v16j0r.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/validar_integracao_switching_saida_v17_c7.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/validar_pacote_orquestrado_pre_saida_v17_c1.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/validar_pacote_orquestrado_pre_saida_v17_c2.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado
- `scripts/diagnostico/validar_ponte_renderizacao_switching_v17_c6.py` — REMOVER_CONSUMADO_API_REMOVIDA — shadow_textual;kwargs_shadow;benchmark_legado

## Regra aplicada

Não reintroduzir compatibilidade no núcleo vivo para scripts diagnósticos legados. Scripts consumados devem ser removidos ou substituídos por evidência estática.

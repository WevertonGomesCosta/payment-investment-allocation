# Índice de Diagnósticos Ativos — pós-GOV-01

## Status

Este índice substitui o índice V17-F0-V.4T, que referenciava diagnósticos V4 já removidos ou não mais pertencentes à rota viva.

Após o adendo `ADENDO_GOV_01_CICLO_VIDA_DIAGNOSTICOS_ARTEFATOS_TEMPORARIOS.md`, nenhum script diagnóstico deve ser tratado como ativo, permanente ou normativo sem classificação explícita.

## Gate permanente preservado

| Script | Classe GOV-01 | Uso permitido |
|---|---|---|
| `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` | `GATE_PERMANENTE` | Gate estrutural pós-limpeza bruta para `nucleo/*.py` e `ContextoOperacionalCanonico` |

## Diagnósticos restantes em avaliação na ME-POST-GOV-02

Os scripts abaixo permanecem no namespace `scripts/diagnostico/` no início da ME-POST-GOV-02, mas **não** são gates permanentes, **não** são fonte operacional e **não** devem ser usados como norma superior ao contrato operacional, ao modelo oficial ou ao GOV-01.

| Script | Classe provisória | Decisão requerida |
|---|---|---|
| `scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_classes_divergencias_valores_v17_c10.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_comparacao_pacotes_diarios.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_competicao_recebidos_49_aprovados_v17_f0_t4.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_divergencias_salarios_recebidos_v17_f0_s1.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_duplicidades_code_nucleo_v17_e1_b.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_precedencia_intradiaria_recebidos_v17_f0_t7.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_recomendacoes_pagamento_v17_f0_u0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_reconciliacao_temporal_v17_f0_s0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_saida_canonica_v17_a4.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_saldos_saida_auxiliar_v17_f0_u7pre.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_semantica_dados_v17_a3.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_tabela_operacional_pagamentos_v17_f0_s7h.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_transicao_temporal_switching_v17_d0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/auditar_uso_operacional_tabela_pagamentos_v17_f0_s7j.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/checagem_pos_conflito_current.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/classificar_bloqueios_v17_a0_2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/classificar_divergencias_pacote_saida_v17_c4.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/classificar_pagamentos_sem_lote_v17_f0_t0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/consolidar_plano_migracao_v17_b0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/construir_taxonomia_v17_a2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/desenhar_pacote_orquestrado_pre_saida_v17_b2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/diagnosticar_baixa_resolutividade_extrato_futuro.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/integrar_saida_operacional_pagamentos_multifonte_v17_f0_u3.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/investigar_fontes_temporais_sem_lote_v17_f0_t1.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/mapear_pontos_reescolha_v16j0.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/reconciliar_recebidos_concorrencia_sem_lote_v17_f0_t2.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/testar_alocacao_conjunta_recebidos_sem_lote_v17_f0_t3.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/validar_canonizacao_v17_a1.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |
| `scripts/diagnostico/validar_invariantes_extrato_futuro.py` | `TRANSITORIO_PENDENTE` | remover, arquivar fora da rota viva ou promover formalmente |

## Regra operacional da ME-POST-GOV-02

1. Não usar diagnósticos transitórios como insumo do runtime.
2. Não reintroduzir compatibilidade artificial em `aplicacao/*` ou `nucleo/*`.
3. Não criar novo gate permanente sem registro explícito em log de microetapa.
4. Não iniciar a próxima frente funcional enquanto houver diagnóstico transitório sem destino decidido.
5. O destino padrão para diagnóstico não promovido é remoção ou arquivamento fora da rota viva, conforme GOV-01.

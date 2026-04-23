# Auditoria da reexecução com cache BCB atualizado — V178

## Síntese executiva
- somente o cache BCB/CDI mudou materialmente; a planilha enviada é idêntica à já embutida na V177.
- a atualização acrescentou fatores diários para 2026-04-17, 2026-04-20 e 2026-04-22.
- a política do motor não mudou com a reexecução: mesmos contadores globais, mesmas escolhas estruturais e mesmos gargalos metodológicos.

## Evidência objetiva
- resumo anterior: {'data_inicio': '2026-04-23', 'data_fim': '2026-05-23', 'dias_no_horizonte': 31, 'dias_com_pagamento': 9, 'dias_sem_pagamento': 22, 'dias_com_acoes_candidatas_switching': 31, 'dias_com_cenarios_promoviveis': 12, 'dias_com_switching_executado': 7, 'dias_com_normalizacao_pos_vencimento': 2, 'pagamentos_no_horizonte': 13, 'pagamentos_com_switching_no_fluxo': 0, 'inconsistencias_temporais_no_estado': 0, 'familias_cenarios_switching_avaliadas': {'individual_integral_parametrizado': 78, 'agrupado_integral_parametrizado': 22}, 'classes_cenarios_hibridos_avaliados': {'vencedor_terminal': 75, 'vencedor_operacional': 7, 'vencedor_hibrido_aceitavel': 1, 'dominado_pelo_baseline': 17}}
- resumo reexecutado: {'data_inicio': '2026-04-23', 'data_fim': '2026-05-23', 'dias_no_horizonte': 31, 'dias_com_pagamento': 9, 'dias_sem_pagamento': 22, 'dias_com_acoes_candidatas_switching': 31, 'dias_com_cenarios_promoviveis': 12, 'dias_com_switching_executado': 7, 'dias_com_normalizacao_pos_vencimento': 2, 'pagamentos_no_horizonte': 13, 'pagamentos_com_switching_no_fluxo': 0, 'inconsistencias_temporais_no_estado': 0, 'familias_cenarios_switching_avaliadas': {'individual_integral_parametrizado': 78, 'agrupado_integral_parametrizado': 22}, 'classes_cenarios_hibridos_avaliados': {'vencedor_terminal': 75, 'vencedor_operacional': 7, 'vencedor_hibrido_aceitavel': 1, 'dominado_pelo_baseline': 17}}

## Efeito numérico principal
- 2026-04-23, lote 3000 mar. V: 3076.18 -> 3074.03
- 2026-04-23, lote 3000 mar. B: 3074.0 -> 3071.85

## Decisão de auditoria
- a V178 deve ser lida como atualização de insumos + reexecução, não como mudança de política do motor.
- os próximos ajustes devem continuar focados no comparador integrado de dias com pagamento.
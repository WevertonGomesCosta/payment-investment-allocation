# Índice de Diagnósticos Ativos — pós V4T

## Ativos de regressão
- auditar_residuos_funcionais_pos_etapa4_v4s.py
- auditar_fechamento_funcional_etapa4_v4q.py
- auditar_correcao_lote_3120_mai_v4p0a.py
- auditar_pagamentos_realizados_lote_3120_v4p0b.py

## Preservados temporariamente
- auditar_lote_3120_mai_estado_temporal_v4o.py
- auditar_lote_3120_mai_replay_vs_saida_v4o0a.py

## Movidos para histórico (historico/etapa4)
- auditar_pacote_replay_passado_v4d.py
- auditar_pacote_ledger_temporal_operacional_v4e.py
- auditar_pacote_estado_temporal_v4f.py
- auditar_pacote_auditoria_temporal_v4g.py
- auditar_pacotes_temporais_agregados_saida_v4i.py
- auditar_saida_canonica_vs_pacotes_temporais_v4j.py
- auditar_normalizacao_lotes_estado_temporal_v4k0.py
- auditar_saida_temporal_shadow_v4k.py
- auditar_saida_controlada_temporal_shadow_v4l.py
- auditar_saida_canonica_parametro_temporal_shadow_v4n.py

## Exigem investigação antes de mover
- auditar_lote_3120_mai_estado_temporal_v4o.py
- auditar_lote_3120_mai_replay_vs_saida_v4o0a.py

## Candidatos à remoção futura
- Scripts em `scripts/diagnostico/historico/etapa4/` após congelamento de regressões e ausência de uso cruzado.

## Governança
Scripts em `historico/etapa4` não devem ser usados por runtime nem importados por caminhos ativos de execução.

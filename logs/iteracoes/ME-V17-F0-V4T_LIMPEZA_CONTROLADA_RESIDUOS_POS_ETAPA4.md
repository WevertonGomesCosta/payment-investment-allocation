# ME-V17-F0-V4T — Limpeza controlada de resíduos pós-Etapa 4

## Objetivo
Executar primeira limpeza controlada do namespace de `scripts/diagnostico` sem alterar motor econômico, `nucleo/`, `aplicacao/` ou abrir Etapa 5.

## Baseline V4S
- 45 funções analisadas em `nucleo/saida_observavel.py`
- 19 com acesso a contexto
- 13 com acesso a replay
- 6 com varredura genérica
- 16 diagnósticos V4
- 20 caminhos shadow classificados
- `qtd_residuos_remover_agora=0`

## Critérios de movimentação
- preservar obrigatórios: V4Q, V4S, V4P0a, V4P0b;
- mover apenas scripts V4 sem evidência de uso/import ativo fora de logs/documentação;
- manter para investigação quando houver risco de regressão sensível (Lote 3120).

## Scripts preservados no namespace ativo
- auditar_residuos_funcionais_pos_etapa4_v4s.py
- auditar_fechamento_funcional_etapa4_v4q.py
- auditar_correcao_lote_3120_mai_v4p0a.py
- auditar_pagamentos_realizados_lote_3120_v4p0b.py

## Scripts movidos para histórico
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

## Scripts mantidos por dúvida/investigação
- auditar_lote_3120_mai_estado_temporal_v4o.py
- auditar_lote_3120_mai_replay_vs_saida_v4o0a.py

## Decisão sobre Etapa 5
- Etapa 5 permanece fechada.
- Próxima microetapa recomendada: `V17-F0-V.4U`.

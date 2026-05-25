# Índice de Diagnósticos Ativos (V17-F0-V.4T)

## Ativos (runtime de regressão)
- `scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py`
- `scripts/diagnostico/auditar_fechamento_funcional_etapa4_v4q.py`
- `scripts/diagnostico/auditar_correcao_lote_3120_mai_v4p0a.py`
- `scripts/diagnostico/auditar_pagamentos_realizados_lote_3120_v4p0b.py`

## Preservados temporariamente
- Diagnósticos V4 ainda usados como suporte de fechamento de Etapa 4.

## Mantidos para investigação
- `scripts/diagnostico/auditar_lote_3120_mai_estado_temporal_v4o.py`
- `scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py`

## Movidos para histórico (`scripts/diagnostico/historico/etapa4/`)
- `auditar_pacote_replay_passado_v4d.py`
- `auditar_pacote_ledger_temporal_operacional_v4e.py`
- `auditar_pacote_estado_temporal_v4f.py`
- `auditar_pacote_auditoria_temporal_v4g.py`
- `auditar_pacotes_temporais_agregados_saida_v4i.py`
- `auditar_saida_canonica_vs_pacotes_temporais_v4j.py`
- `auditar_normalizacao_lotes_estado_temporal_v4k0.py`

## Governança
Scripts em `historico/etapa4` não pertencem ao runtime ativo, mas devem permanecer executáveis para auditoria histórica, incluindo resolução robusta da raiz do repositório.

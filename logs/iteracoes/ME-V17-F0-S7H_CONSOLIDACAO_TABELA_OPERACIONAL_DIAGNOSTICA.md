# ME-V17-F0-S7H_CONSOLIDACAO_TABELA_OPERACIONAL_DIAGNOSTICA

## 1. Identificação
- MICROETAPA=V17-F0-S.7-H
- BASELINE_DE_ENTRADA_ESPERADA=a9107d4
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=00f89ac
- Q_REABERTA=nao

## 2. Objetivo
- consolidar tabela operacional de pagamentos como saída diagnóstica estável.

## 3. Comentário Codex tratado
- P2: ambiguidade do contador `qtd_pagamentos_com_fonte_bloqueada` diante de status operacionais bloqueantes.
- decisão: auditar semântica, não aplicar correção literal em S.7-G nesta microetapa.

## 4. Arquivos criados
- `scripts/diagnostico/auditar_tabela_operacional_pagamentos_v17_f0_s7h.py`
- `logs/iteracoes/ME-V17-F0-S7H_CONSOLIDACAO_TABELA_OPERACIONAL_DIAGNOSTICA.md`
- CSV S.7-G utilizado/gerado e não versionado: `saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv`

## 5. Schema mínimo estável
- qtd_linhas_tabela_operacional=159
- qtd_colunas_tabela_operacional=26
- qtd_colunas_obrigatorias_ausentes=0
- colunas_obrigatorias_ausentes=nenhuma
- decisão: schema estável=sim

## 6. Sentinelas
### 6.1 Cinco próximos pagamentos
- Internet (2026-05-15): valor=132.40, saldo_pos_pagamento=2895.01, origem=extrato_futuro_saldo_remanescente, ok=sim
- Cartão Azul (2026-05-20): valor=5372.00, saldo_pos_pagamento=869.53, origem=extrato_futuro_saldo_remanescente, ok=sim
- Condomínio (2026-05-20): valor=113.31, saldo_pos_pagamento=1205.69, origem=extrato_futuro_saldo_remanescente, ok=sim
- Implante Velt (2026-05-30): valor=400.00, saldo_pos_pagamento=2495.01, origem=extrato_futuro_saldo_remanescente, ok=sim
- Cartão NU (2026-06-02): valor=580.00, saldo_pos_pagamento=1915.01, origem=extrato_futuro_saldo_remanescente, ok=sim

### 6.2 Dois alertas explícitos
- Aluguel (2026-06-12): status=alerta_operacional_justificado, problema=sem_saldo_temporal_auditavel, motivo=saldo_temporal_insuficiente_cumulativo, tipo=explicito, ok=sim
- Condomínio (2026-06-20): status=alerta_operacional_justificado, problema=sem_saldo_temporal_auditavel, motivo=saldo_temporal_insuficiente_cumulativo, tipo=explicito, ok=sim

## 7. Contadores operacionais
- qtd_pagamentos_aprovados_para_pagamento=33
- qtd_pagamentos_aprovados_multifonte=16
- qtd_pagamentos_com_lote_pos_switching_valido=14
- qtd_componentes_lote_pos_switching_validos=16
- qtd_pagamentos_multifonte=16
- qtd_componentes_multifonte_total=32
- qtd_pagamentos_com_alerta_operacional_explicito=110
- qtd_pagamentos_com_alerta_operacional_inferido=0
- qtd_pagamentos_sem_lote_sugerido=110
- qtd_pagamentos_sem_lote_sugerido_sem_alerta_explicito=0
- qtd_pagamentos_com_estado_terminal_bloqueante_explicito=110

## 8. Auditoria semântica dos bloqueios
- qtd_pagamentos_com_fonte_bloqueada=0
- qtd_pagamentos_com_bloqueio_operacional=110
- qtd_pagamentos_com_saldo_temporal_insuficiente=110
- qtd_pagamentos_com_saldo_temporal_insuficiente_explicito=110
- qtd_pagamentos_com_saldo_temporal_insuficiente_inferido=0
- semantica_qtd_pagamentos_com_fonte_bloqueada=fonte_especifica
- fonte_bloqueada_zero_compativel_com_semantica=sim
- contador_bloqueio_operacional_amplo=derivado_no_auditor
- recomendacao_contador_bloqueio_operacional=necessario

## 9. Regressões
- S.7-G: `status_geral_s7g=tabela_operacional_pagamentos_gerada`
- S.7-F: divergência de ambiente (`matriz_status=erro_matriz_indisponivel`; `status_geral_s7f=falha_reconciliacao_s7f`)
- S.7-D: `status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido`
- Q.0: `status_geral_integracao=switching_integrado_ok`
- Q.1: `status_geral_q1=sem_divergencia_observada`
- Q.5/Q.5-B/C/D/E: marcadores esperados preservados

## 10. Hashes dados/cache
- dados_financeiros.xlsx: `ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4` (antes/depois)
- cache_bcb.json: `a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a` (antes/depois)

## 11. Decisão
- S7H_CONSOLIDACAO_APROVADA=sim
- TABELA_OPERACIONAL_DIAGNOSTICA_ESTAVEL=sim
- Q_REABERTA=nao
- S7I_LIBERADA=sim
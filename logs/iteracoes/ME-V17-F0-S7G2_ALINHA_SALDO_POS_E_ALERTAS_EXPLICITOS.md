# ME-V17-F0-S7G2_ALINHA_SALDO_POS_E_ALERTAS_EXPLICITOS

1. Identificação
- MICROETAPA=V17-F0-S.7-G.2
- BASELINE_DE_ENTRADA_ESPERADA=05bc80a
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=4d38def
- Q_REABERTA=nao

2. Objetivo
- alinhar saldo_pos_pagamento ao Extrato Futuro;
- separar alertas explícitos e inferidos;
- ampliar taxonomia de alertas operacionais terminais.

3. Comentário Codex tratado
- P2: taxonomia incompleta de alertas operacionais.

4. Problemas corrigidos
- saldo_pos_pagamento divergente;
- alerta explícito misturado com alerta inferido;
- ausência de separação entre sem_lote_sugerido e alerta explícito;
- taxonomia de alerta limitada a apenas dois estados.

5. Arquivos alterados/criados
- script S.7-G;
- log S.7-G.2;
- CSV S.7-G gerado, não versionado.

6. Indicadores antes/depois da correção
- Antes (script base): sem separação explícito/inferido e sem contadores terminais dedicados.
- Depois:
  - qtd_pagamentos_operacionais_avaliados=159
  - qtd_pagamentos_aprovados_para_pagamento=33
  - qtd_pagamentos_aprovados_multifonte=16
  - qtd_pagamentos_com_alerta_operacional_justificado=110
  - qtd_pagamentos_com_alerta_operacional_explicito=110
  - qtd_pagamentos_com_alerta_operacional_inferido=0
  - qtd_pagamentos_sem_lote_sugerido=110
  - qtd_pagamentos_sem_lote_sugerido_sem_alerta_explicito=0
  - qtd_pagamentos_com_saldo_temporal_insuficiente=110
  - qtd_pagamentos_com_saldo_temporal_insuficiente_explicito=110
  - qtd_pagamentos_com_saldo_temporal_insuficiente_inferido=0
  - qtd_pagamentos_com_estado_terminal_bloqueante_explicito=110
  - qtd_pagamentos_sem_fonte_auditavel=0
  - qtd_pagamentos_switch_then_pay_sem_materializacao=0
  - qtd_pagamentos_fonte_pos_switching_nao_materializada=0
  - qtd_pagamentos_com_lote_pos_switching_valido=14
  - qtd_componentes_lote_pos_switching_validos=16
  - qtd_pagamentos_multifonte=16
  - qtd_componentes_multifonte_total=32
  - status_geral_s7g=tabela_operacional_pagamentos_gerada

7. Amostra corrigida dos 5 próximos pagamentos
- 2026-05-15 | Internet | valor=132.40 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos=2895.01 | origem=extrato_futuro_saldo_remanescente | alerta=nao | tipo=sem_alerta
- 2026-05-20 | Cartão Azul | valor=5372.00 | lote=Lote 3120 mai + Lote 3000 mai Neon | status=aprovado_multifonte | acao=pagar_com_fontes_componentes | saldo_pos=869.53 | origem=extrato_futuro_saldo_remanescente | alerta=nao | tipo=sem_alerta
- 2026-05-20 | Condomínio | valor=113.31 | lote=Lote 3000 mai Neon | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos=1205.69 | origem=extrato_futuro_saldo_remanescente | alerta=nao | tipo=sem_alerta
- 2026-05-30 | Implante Velt | valor=400.00 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos=2495.01 | origem=extrato_futuro_saldo_remanescente | alerta=nao | tipo=sem_alerta
- 2026-06-02 | Cartão NU | valor=580.00 | lote=Lote 3120 mai | status=aprovado_para_pagamento | acao=pagar_com_lote_sugerido | saldo_pos=1915.01 | origem=extrato_futuro_saldo_remanescente | alerta=nao | tipo=sem_alerta

8. Alertas explícitos detectados
- 2026-06-12 | Aluguel | problema=sem_saldo_temporal_auditavel | motivo=saldo_temporal_insuficiente_cumulativo | tipo=explicito
- 2026-06-20 | Condomínio | problema=sem_saldo_temporal_auditavel | motivo=saldo_temporal_insuficiente_cumulativo | tipo=explicito

9. Contadores de alerta explícito/inferido e estados terminais
- explicito=110
- inferido=0
- sem_lote_sugerido_sem_alerta_explicito=0
- saldo_temporal_insuficiente_explicito=110
- saldo_temporal_insuficiente_inferido=0
- estado_terminal_bloqueante_explicito=110
- sem_fonte_auditavel=0
- switch_then_pay_sem_materializacao=0
- fonte_pos_switching_nao_materializada=0

10. Regressões
- S.7-F: divergente no ambiente (matriz_status=erro_matriz_indisponivel; status_geral_s7f=falha_reconciliacao_s7f)
- S.7-D: status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- Q.0: status_geral_integracao=switching_integrado_ok; origens_migradas_usadas_indevidamente_total=0
- Q.1: status_geral_q1=sem_divergencia_observada
- Q.5/B/C/D/E: marcadores esperados preservados

11. Hashes dados/cache
- dados/dados_financeiros.xlsx: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- dados/cache_bcb.json: a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

12. Decisão
- S7G2_CORRECAO_APROVADA=sim
- TABELA_OPERACIONAL_S7G_APROVADA=sim
- Q_REABERTA=nao
- S7H_LIBERADA=sim

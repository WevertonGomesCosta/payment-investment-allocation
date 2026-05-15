# ME-V17-F0-S7I3_REPOE_INVARIANTE_159_LINHAS_AUDITOR_XLSX

## 1. Identificação
- MICROETAPA=V17-F0-S.7-I.3
- BASELINE_DE_ENTRADA_ESPERADA=HEAD atual pós-S.7-I.2; referência local recente: 8917c25, se presente no histórico local
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=3b60428b3480f183d15da276f5e15738cbbe8c13
- Q_REABERTA=nao

## 2. Objetivo
- repor invariante de 159 linhas no status final do auditor S.7-I.

## 3. Comentário Codex tratado
- P1: status_geral_s7i não exigia explicitamente qtd_linhas_aba_tabela_operacional=159.
- risco: falso verde se CSV e XLSX fossem truncados de modo idêntico.

## 4. Correção aplicada
- constante QTD_LINHAS_ESPERADA=159.
- inclusão de qtd_linhas_aba_tabela_operacional == 159 e qtd_linhas_csv_s7g == 159 no gate de aprovação.
- inclusão explícita da métrica qtd_linhas_csv_s7g.
- teste negativo de truncamento em memória (158 linhas) com falha controlada.
- preservação do teste negativo de coluna ausente.
- reutilização da função central _avaliar_tabela_operacional para status normal e cenários negativos.

## 5. Arquivos alterados/criados
- Alterado: scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py
- Criado: logs/iteracoes/ME-V17-F0-S7I3_REPOE_INVARIANTE_159_LINHAS_AUDITOR_XLSX.md
- XLSX/CSV utilizados ou gerados, não versionados: CSV S.7-G disponível; XLSX indisponível no ambiente atual.

## 6. Resultado pós-correção
- qtd_linhas_aba_tabela_operacional: não disponível no cenário atual (sem XLSX).
- qtd_linhas_csv_s7g: nao_disponivel no cenário atual do S.7-I.
- status_geral_s7i: falha_integracao_tabela_operacional_xlsx (sem XLSX).
- teste_negativo_rowcount_* emitido e controlado.
- teste_negativo_coluna_* preservado.

## 7. Indicadores S.7-I
- aba operacional: ausente no ambiente atual.
- linhas: gate reforçado para 159 (aba e CSV).
- colunas: fallback seguro, sem KeyError.
- comparação CSV↔XLSX: protegida.
- sentinelas: protegidas.
- contadores principais: protegidos.

## 8. Regressões
- S.7-H: status_geral_s7h=tabela_operacional_diagnostica_estavel
- S.7-G: status_geral_s7g=tabela_operacional_pagamentos_gerada; qtd_linhas_csv_s7g=159
- S.7-F: matriz_status=erro_matriz_indisponivel; status_geral_s7f=falha_reconciliacao_s7f
- S.7-D: status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- Q.0: status_geral_integracao=switching_integrado_ok
- Q.1: status_geral_q1=sem_divergencia_observada
- Q.5/Q.5-B/C/D/E: lote_190_mai_no_expandido=sim; lote_3120_mai_no_expandido=sim; status_geral_q5b=consumo_pos_switching_integrado; status_geral_q5c=valoracao_pos_preservada; status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos; status_geral_q5e=ativos_pos_duplicados_consolidados

## 9. Hashes dados/cache
- antes_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- antes_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a
- depois_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- depois_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

## 10. Decisão
- S7I3_CORRECAO_APROVADA=sim
- S7I_INTEGRACAO_APROVADA=nao
- TABELA_OPERACIONAL_INTEGRADA_XLSX=nao
- Q_REABERTA=nao
- S7J_LIBERADA=nao

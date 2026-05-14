MICROETAPA: V17-F0-S.7-B.1

1) Diagnóstico Git inicial
- branch/status: ## work
- head curto: 037536f
- topo log: 037536f V17-F0-S.7-B: implementa matriz de elegibilidade de fontes pos S6
- remote: indisponível no ambiente

2) Referência P1/P2 @codex (PR #312)
- P1: leitura de classes S.6 dependia de classe_s6 e não lia classe_politica_s6.
- P2: status_switching de lotes exauridos incompleto.

3) Arquivos alterados
- nucleo/matriz_elegibilidade_fontes_s7b.py
- scripts/diagnostico/auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py
- logs/iteracoes/ME-V17-F0-S7B1_CORRECAO_CLASSES_S6_MATRIZ_ELEGIBILIDADE.md

4) Correções aplicadas
- leitura de coluna S.6: procura sequencial em classe_s6, classe_temporal_s6, classe_politica_s6.
- coluna efetivamente usada nesta execução: classe_politica_s6.
- normalização de classes: trim + lowercase antes da contagem.
- erro explícito se nenhuma coluna existir: erro_coluna_classe_s6_nao_encontrada.
- status_switching de exauridos: inferência por Status + fonte_detalhada + Origem migrada + Evento switching ID.
- contadores no auditor: agora contam somente fontes bloqueadas (classe alvo + elegivel_para_pagamento=nao + pode_ser_lote_sugerido=nao).

5) Resultado S.7-B antes/depois
- antes: qtd_fontes_avaliadas=15; qtd_salarios_previstos_bloqueados=0; qtd_uso_pre_aplicacao_sem_vinculo_bloqueados=0.
- depois: qtd_fontes_avaliadas=47; qtd_salarios_previstos_bloqueados=29; qtd_uso_pre_aplicacao_sem_vinculo_bloqueados=3.

6) Resultado final esperado
- qtd_salarios_previstos_bloqueados=29
- qtd_uso_pre_aplicacao_sem_vinculo_bloqueados=3
- qtd_lacunas_reais_bloqueadas=0
- status_geral_s7b=matriz_elegibilidade_fontes_construida

7) Sentinelas POS
- sentinela_lote_190_nao_elegivel=sim
- sentinela_lote_3120_ativo_pos=sim

8) Regressões Q
- Q.0: switching_integrado_ok
- Q.1: sem_divergencia_observada
- Q.5-A/B/C/D/E: sem regressão observada

9) Hashes dados/cache
- dados_financeiros inicial/final: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4 / ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- cache_bcb inicial/final: 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525 / 70ca1928274d8ee32a86b8c933244c6ddeb50e8a21528dcfb9b1792e17222525
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

10) Smoke
- python aplicacao/principal.py: exit 0

11) Decisão
- S.7B1_CORRECAO_APROVADA=sim
- Q_REABERTA=nao
- S.7C_LIBERADA_PARA_INTEGRACAO_AO_RECOMENDADOR=sim

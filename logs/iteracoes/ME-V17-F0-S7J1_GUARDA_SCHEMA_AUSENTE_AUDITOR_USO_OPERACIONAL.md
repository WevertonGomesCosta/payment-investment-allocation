# ME-V17-F0-S7J1_GUARDA_SCHEMA_AUSENTE_AUDITOR_USO_OPERACIONAL

## 1. Identificação
- MICROETAPA=V17-F0-S.7-J.1
- BASELINE_DE_ENTRADA_ESPERADA=a2b2acf
- BASELINE_OPERACIONAL_CONGELADA=5d401e1
- BASELINE_EFETIVAMENTE_USADA=220c16df399cb1ed9f63f0042784c78a081708f6
- Q_REABERTA=nao

## 2. Objetivo
- proteger auditor S.7-J contra colunas obrigatórias ausentes.

## 3. Comentário Codex tratado
- P1: sort_values(['_data','conta']) podia quebrar com KeyError se conta estivesse ausente.
- risco: auditor detecta schema ausente, mas quebrava antes da falha controlada.

## 4. Correção aplicada
- guarda de schema antes das visões operacionais (schema_ok).
- proteção contra KeyError nos blocos dependentes de colunas obrigatórias.
- teste negativo removendo conta em memória.
- emissão de falha controlada quando schema inválido ou fonte indisponível.

## 5. Comentário Codex não tratado nesta microetapa
- P2 sobre fallback XLSX do auditor S.7-I.
- motivo: fora de escopo; S.7-I não foi alterado.

## 6. Resultado normal
- fonte_tabela_operacional=indisponivel
- qtd_linhas_tabela_operacional=nao_disponivel
- qtd_colunas_obrigatorias_ausentes=nao_disponivel
- contadores principais=nao_disponivel
- sentinelas=nao_disponivel
- status_geral_s7j=falha_uso_operacional_tabela_pagamentos

## 7. Resultado do teste negativo
- teste_negativo_coluna_removida=nao_executado_fonte_indisponivel
- teste_negativo_keyerror=nao
- teste_negativo_coluna_ausente_detectada=nao_executado
- teste_negativo_status_controlado=nao_executado

## 8. Regressões
- S.7-I: sem alteração nesta microetapa.
- S.7-H: sem alteração nesta microetapa.
- S.7-G: sem alteração nesta microetapa.
- S.7-F: regressão ambiental pré-existente (matriz_status=erro_matriz_indisponivel).
- S.7-D/Q.0/Q.1/Q.5: sem alteração nesta microetapa.

## 9. Hashes dados/cache
- antes_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- antes_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a
- depois_dados_financeiros=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- depois_cache_bcb=a7063474ef29cb3f460ceacf42c8fa969dcf93f61602c59fd620dd9fc7ee3e9a

## 10. Decisão
- S7J1_CORRECAO_APROVADA=sim
- S7J_AUDITORIA_APROVADA=nao
- USO_OPERACIONAL_TABELA_PAGAMENTOS_VALIDADO=nao
- Q_REABERTA=nao
- S7K_LIBERADA=nao

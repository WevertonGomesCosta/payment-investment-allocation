# ME-V17-F0-S7C3_HOTFIX_RECURSAO_RECOMPOSICAO_S6

## Diagnóstico
- MICROETAPA=V17-F0-S.7-C.3
- OBJETIVO=remover recomposição recursiva S.6 a partir do fluxo oficial
- COMENTARIO_CODEX_P1=procedente
- CICLO_RECURSIVO_CONFIRMADO=sim

## Evidência do ciclo anterior
- S2_IMPORTA_PRINCIPAL=sim
- PRINCIPAL_CHAMA_S7B=sim
- S7B_CHAMA_S2_ANTES=sim
- CICLO=S7B -> S2 -> principal -> S7B

## Correção aplicada
- Removida recomposição automática via subprocess em _carregar_s6_df().
- Removida dependência de subprocess para SCRIPT_S2/SCRIPT_S4/SCRIPT_S6.
- Quando CSV_S6 está ausente, _carregar_s6_df() agora levanta:
  erro_csv_s6_ausente_sem_recomposicao_segura
- Mantido fail-fast para CSV vazio, coluna de classe ausente e coluna de classe vazia.
- Auditores S.7-B/S.7-C reconhecem o novo erro explícito.

## Confirmação pós-correção
- S7B_CHAMA_S2_DEPOIS=nao
- DATAFRAME_VAZIO_QUANDO_CSV_AUSENTE=nao
- SUBPROCESS_RECURSIVO=nao
- Q_REABERTA=nao
- S.7D_LIBERADA=sim_apos_commit_push_confirmado

## Arquivos alterados
- nucleo/matriz_elegibilidade_fontes_s7b.py
- scripts/diagnostico/auditar_matriz_elegibilidade_fontes_v17_f0_s7b.py
- scripts/diagnostico/auditar_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.py
- logs/iteracoes/ME-V17-F0-S7C3_HOTFIX_RECURSAO_RECOMPOSICAO_S6.md

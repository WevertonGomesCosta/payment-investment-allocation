# ME-V17-F0-U1 — Critérios de elegibilidade operacional para recomendações de pagamento

- MICROETAPA: V17-F0-U.1
- CLASSE: DIAGNÓSTICO / NORMATIVA OPERACIONAL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: 2026-05-15 19:40:27
- BASELINE: main pós-merge da PR #330
- MICROETAPA_ANTERIOR: V17-F0-U.0
- STATUS_GERAL_U1: `criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_gerados`

## Objetivo

Formalizar critérios operacionais para distinguir fonte aprovada, fonte inelegível, fonte em carência, fonte sem liquidez, fonte futura, fonte pós-switching não materializada, candidato FIFO apenas diagnóstico, pagamento sem lote sugerido e pagamento multifonte sem valor explícito por fonte.

A U.1 não altera recomendador, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `U0_PAGAMENTOS`: `159 x 42`
- `U0_FONTES`: `65 x 25`
- `U0_MULTIFONTE`: `16 x 14`
- `U0_CANDIDATOS`: `126 x 9`
- `S7G`: `159 x 26`
- `S7C`: `159 x 79`
- `S7F`: `159 x 16`
- `S7B`: `47 x 30`
- `S7J`: `49 x 15`

## Artefatos diagnósticos gerados

- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_matriz.csv`
- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_resumo.csv`
- `saidas\diagnostico\criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_classes.csv`

## Contadores principais

- `qtd_pagamentos_u1`: `159`
- `qtd_fontes_u1`: `175`
- `qtd_fontes_aprovadas_sem_violacao_dura`: `33`
- `qtd_linhas_fontes_multifonte_pendentes_u2`: `32`
- `qtd_pagamentos_aprovados_sem_bloqueio_duro_inclui_multifonte_pendente`: `49`
- `qtd_pendencias_sem_lote_sugerido`: `110`
- `qtd_candidatos_fifo_apenas_diagnosticos`: `109`
- `qtd_multifonte_sem_valor_resgate_explicito`: `16`
- `qtd_bloqueios_por_carencia`: `0`
- `qtd_bloqueios_por_liquidez`: `0`
- `qtd_bloqueios_por_materializacao`: `0`
- `qtd_bloqueios_por_pos_switching_nao_materializado`: `0`
- `qtd_bloqueios_por_saldo_insuficiente`: `0`
- `qtd_bloqueios_por_precedencia_intradiaria`: `0`
- `qtd_bloqueios_por_competicao_diaria`: `0`
- `qtd_nao_auditaveis`: `0`
- `qtd_casos_prontos_para_u2_multifonte`: `16`
- `qtd_casos_prontos_para_u3_refactibilizacao`: `110`
- `qtd_linhas_classe_fonte_aprovada_sem_violacao_dura`: `33`
- `qtd_linhas_classe_pendencia_multifonte`: `32`
- `qtd_linhas_classe_candidato_fifo`: `109`
- `qtd_linhas_classe_pendencia_sem_lote`: `1`
- `status_geral_u1`: `criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_gerados`

## Classes operacionais

- `candidato_fifo_apenas_diagnostico`: linhas=`109`, pagamentos=`109`
- `fonte_aprovada_sem_violacao_dura`: linhas=`33`, pagamentos=`33`
- `pendencia_multifonte_sem_valor_resgate_explicito`: linhas=`32`, pagamentos=`16`
- `pendencia_sem_lote_sugerido`: linhas=`1`, pagamentos=`1`

## Decisão normativa preservada

Os casos com `candidato_fifo_detectado = sim` permanecem diagnósticos. Eles não são promovidos automaticamente a fonte elegível, fonte aprovada, lote sugerido ou recomendação operacional.

A U.1 preserva a distinção entre:

- fonte aprovada;
- candidato FIFO apenas diagnóstico;
- pendência sem lote sugerido;
- pendência multifonte sem valor explícito por fonte.

## Restrições preservadas

- Motor econômico não alterado.
- Recomendador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.
- T.0–T.8 não reabertos.
- S.7 não reaberta.

## Status

`criterios_elegibilidade_operacional_pagamentos_v17_f0_u1_gerados`

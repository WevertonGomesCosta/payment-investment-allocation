# ME-V17-F0-U3 — Saída operacional diagnóstica de pagamentos com multifonte

- MICROETAPA: V17-F0-U.3
- CLASSE: DIAGNÓSTICO / EXPORTÁVEL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: 2026-05-15 20:03:16
- BASELINE: main pós-merge da PR #332
- MICROETAPA_ANTERIOR: V17-F0-U.2
- STATUS_GERAL_U3: `saida_operacional_pagamentos_multifonte_v17_f0_u3_gerada`

## Objetivo

Integrar a decomposição multifonte da U.2 a uma saída diagnóstica operacional consolidada de pagamentos.

A U.3 não altera recomendador oficial, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `S7G`: `159 x 26`
- `U0_PAGAMENTOS`: `159 x 42`
- `U0_FONTES`: `65 x 25`
- `U1_MATRIZ`: `175 x 29`
- `U2_LINHAS`: `32 x 32`
- `U2_PAGAMENTOS`: `16 x 14`
- `U2_RESUMO`: `15 x 2`

## Artefatos diagnósticos gerados

- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_linhas.csv`
- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_pagamentos.csv`
- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_resumo.csv`

## Contadores principais

- `qtd_pagamentos_u3`: `159`
- `qtd_linhas_operacionais_u3`: `175`
- `qtd_linhas_monofonte_aprovadas`: `33`
- `qtd_linhas_multifonte_decompostas`: `32`
- `qtd_pagamentos_multifonte_decompostos`: `16`
- `qtd_pagamentos_sem_lote_sugerido`: `110`
- `qtd_candidatos_fifo_apenas_diagnosticos`: `109`
- `qtd_sem_lote_sem_candidato_fifo`: `1`
- `qtd_pagamentos_executaveis_operacionalmente_u3`: `49`
- `qtd_pagamentos_bloqueados_u3`: `110`
- `qtd_pagamentos_nao_auditaveis_u3`: `0`
- `soma_valores_pagamentos_unicos_u3`: `180011.39`
- `soma_resgates_operacionais_u3`: `102826.35`
- `soma_resgates_multifonte_u3`: `92587.92`
- `maior_diferenca_cobertura_multifonte_u3`: `0.0`
- `status_geral_u3`: `saida_operacional_pagamentos_multifonte_v17_f0_u3_gerada`

## Classes por origem de linha

- `candidato_fifo_apenas_diagnostico`: linhas=`109`, pagamentos=`109`
- `fonte_monofonte_aprovada_u0_u1`: linhas=`33`, pagamentos=`33`
- `fonte_multifonte_decomposta_u2`: linhas=`32`, pagamentos=`16`
- `pagamento_sem_lote_sugerido`: linhas=`1`, pagamentos=`1`

## Classes por pagamento

- `monofonte_aprovado`: pagamentos=`33`
- `multifonte_decomposto_diagnostico`: pagamentos=`16`
- `sem_lote_com_candidato_fifo_diagnostico`: pagamentos=`109`
- `sem_lote_sugerido`: pagamentos=`1`

## Interpretação operacional

A U.3 consolida os 159 pagamentos originais em 175 linhas operacionais diagnósticas. Os pagamentos multifonte deixam de aparecer apenas como agregados e passam a ter linhas fonte-a-fonte com valor de resgate consumível, herdado da U.2.

A soma dos pagamentos é calculada por pagamento único, não por linha, para evitar dupla contagem dos multifontes.

## Decisão normativa preservada

- Os 110 pagamentos sem lote sugerido permanecem bloqueados/pendentes.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte FIFO é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- A decomposição multifonte permanece diagnóstica.
- S.7 e T.0–T.8 não são reabertos.

## Restrições preservadas

- Motor econômico não alterado.
- Recomendador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.
- Exportador oficial não alterado.

## Status

`saida_operacional_pagamentos_multifonte_v17_f0_u3_gerada`

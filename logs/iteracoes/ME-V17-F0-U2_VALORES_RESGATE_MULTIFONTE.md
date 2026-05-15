# ME-V17-F0-U2 — Valores de resgate por fonte em pagamentos multifonte

- MICROETAPA: V17-F0-U.2
- CLASSE: DIAGNÓSTICO / OPERACIONAL / PAGAMENTOS MULTIFONTE
- DATA_EXECUCAO_LOCAL: 2026-05-15 19:49:39
- BASELINE: main pós-merge da PR #331
- MICROETAPA_ANTERIOR: V17-F0-U.1
- STATUS_GERAL_U2: `valores_resgate_multifonte_v17_f0_u2_gerados`

## Objetivo

Explicitar valores de resgate por fonte para os pagamentos classificados na U.1 como `pendencia_multifonte_sem_valor_resgate_explicito`.

A U.2 não altera recomendador oficial, motor econômico, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `U1_MATRIZ`: `175 x 29`
- `U1_RESUMO`: `23 x 2`
- `U1_CLASSES`: `4 x 3`
- `U0_PAGAMENTOS`: `159 x 42`
- `U0_FONTES`: `65 x 25`
- `U0_MULTIFONTE`: `16 x 14`
- `S7G`: `159 x 26`
- `S7F`: `159 x 16`
- `S7C`: `159 x 79`

## Artefatos diagnósticos gerados

- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_linhas.csv`
- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_pagamentos.csv`
- `saidas\diagnostico\valores_resgate_multifonte_v17_f0_u2_resumo.csv`

## Contadores principais

- `qtd_pagamentos_multifonte_u2`: `16`
- `qtd_linhas_fontes_multifonte_u2`: `32`
- `qtd_pagamentos_multifonte_executaveis`: `16`
- `qtd_pagamentos_multifonte_executaveis_com_residuo_arredondamento`: `0`
- `qtd_pagamentos_multifonte_nao_executaveis_cobertura_insuficiente`: `0`
- `qtd_pagamentos_multifonte_nao_auditaveis`: `0`
- `qtd_linhas_resgate_multifonte_explicitado`: `32`
- `qtd_linhas_resgate_multifonte_com_residuo_arredondamento`: `0`
- `qtd_linhas_resgate_multifonte_com_cobertura_insuficiente`: `0`
- `qtd_linhas_resgate_multifonte_sem_saldo_fonte`: `0`
- `qtd_linhas_resgate_multifonte_sem_valor_calculavel`: `0`
- `maior_diferenca_absoluta_cobertura`: `0.0`
- `soma_valores_pagamentos_multifonte`: `92587.92`
- `soma_resgates_explicitados_u2`: `92587.92`
- `status_geral_u2`: `valores_resgate_multifonte_v17_f0_u2_gerados`

## Classes por pagamento

- `pagamento_multifonte_executavel`: pagamentos=`16`

## Classes por linha fonte-a-fonte

- `resgate_multifonte_explicitado`: linhas=`32`, pagamentos=`16`

## Interpretação operacional

A U.2 restringe a análise aos 16 pagamentos multifonte e às 32 linhas fonte-a-fonte identificadas na U.1. Os valores explicitados são diagnósticos e não promovem alteração na recomendação oficial.

## Decisão normativa preservada

- Os 110 pagamentos sem lote sugerido permanecem fora desta correção.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
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

## Status

`valores_resgate_multifonte_v17_f0_u2_gerados`

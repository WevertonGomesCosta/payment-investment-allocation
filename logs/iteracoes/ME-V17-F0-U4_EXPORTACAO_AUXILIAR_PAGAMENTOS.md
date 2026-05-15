# ME-V17-F0-U4 — Exportação auxiliar controlada da saída operacional de pagamentos

- MICROETAPA: V17-F0-U.4
- CLASSE: DIAGNÓSTICO / EXPORTAÇÃO AUXILIAR CONTROLADA / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: 2026-05-15 20:12:44
- BASELINE: main pós-merge da PR #333
- MICROETAPA_ANTERIOR: V17-F0-U.3
- STATUS_GERAL_U4: `exportacao_auxiliar_pagamentos_v17_f0_u4_gerada`

## Objetivo

Gerar um XLSX auxiliar diagnóstico, baseado exclusivamente nos CSVs da U.3, para tornar a saída operacional de pagamentos consumível visualmente.

A U.4 não altera recomendador oficial, motor econômico, exportador oficial, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `U3_LINHAS`: `175 x 27`
- `U3_PAGAMENTOS`: `159 x 13`
- `U3_RESUMO`: `16 x 2`

## Artefatos diagnósticos locais gerados

- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u4.xlsx`
- `saidas\diagnostico\exportacao_auxiliar_pagamentos_v17_f0_u4_resumo.csv`

## Abas do XLSX auxiliar

- `Resumo_U4`
- `Pagamentos`
- `Linhas_Operacionais`
- `Multifonte`
- `Pendencias`
- `Metadados`

## Contadores principais

- `qtd_pagamentos_u4`: `159`
- `qtd_linhas_operacionais_u4`: `175`
- `qtd_linhas_multifonte_u4`: `32`
- `qtd_pagamentos_multifonte_u4`: `16`
- `qtd_pagamentos_bloqueados_u4`: `110`
- `qtd_pagamentos_executaveis_u4`: `49`
- `qtd_candidatos_fifo_diagnosticos_u4`: `109`
- `soma_valores_pagamentos_unicos_u4`: `180011.39`
- `soma_resgates_operacionais_u4`: `102826.35`
- `soma_resgates_multifonte_u4`: `92587.92`
- `maior_diferenca_cobertura_multifonte_u4`: `0.0`
- `arquivo_xlsx_auxiliar_u4`: `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u4.xlsx`
- `status_geral_u4`: `exportacao_auxiliar_pagamentos_v17_f0_u4_gerada`

## Interpretação operacional

A U.4 promove a saída U.3 apenas para um XLSX auxiliar diagnóstico em `saidas/diagnostico/`. A exportação torna a decomposição operacional consumível, mas não integra o conteúdo ao fluxo oficial.

A aba `Pagamentos` preserva 159 pagamentos únicos. A aba `Linhas_Operacionais` preserva 175 linhas. A aba `Multifonte` preserva 32 linhas fonte-a-fonte e 16 pagamentos. A aba `Pendencias` preserva 110 pagamentos bloqueados/pendentes.

## Decisão normativa preservada

- O XLSX gerado é auxiliar e diagnóstico.
- O XLSX oficial não é alterado.
- O exportador oficial não é alterado.
- O motor econômico não é alterado.
- O recomendador oficial não é alterado.
- Os 110 pagamentos sem lote sugerido permanecem bloqueados/pendentes.
- Os 109 candidatos FIFO permanecem diagnósticos.
- Nenhuma fonte FIFO é promovida automaticamente.
- Nenhum recebido é transformado em fonte oficial.
- S.7 e T.0–T.8 não são reabertos.

## Restrições preservadas

- `aplicacao/principal.py` não alterado.
- Motor econômico não alterado.
- Recomendador oficial não alterado.
- Exportador oficial não alterado.
- XLSX oficial não alterado.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts existentes não alterados.
- Módulos `nucleo/` não alterados.

## Status

`exportacao_auxiliar_pagamentos_v17_f0_u4_gerada`

# ME-V17-F0-U5 — Auditoria de consistência da exportação auxiliar U.4 contra CSVs U.3

- MICROETAPA: V17-F0-U.5
- CLASSE: DIAGNÓSTICO / READ-ONLY / AUDITORIA CRUZADA
- DATA_EXECUCAO_LOCAL: 2026-05-15 20:33:56
- BASELINE: main pós-merge da PR #334
- MICROETAPA_ANTERIOR: V17-F0-U.4
- STATUS_GERAL_U5: `auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_sem_divergencias`

## Objetivo

Auditar se o XLSX auxiliar gerado na U.4 preserva exatamente o conteúdo dos CSVs diagnósticos da U.3, sem perda de linhas, duplicação indevida, alteração de valores, alteração de classes, alteração de flags operacionais ou mudança de chaves.

A U.5 não altera recomendador oficial, motor econômico, exportador oficial, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_linhas.csv`
- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_pagamentos.csv`
- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u3_resumo.csv`
- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u4.xlsx`
- `saidas\diagnostico\exportacao_auxiliar_pagamentos_v17_f0_u4_resumo.csv`

## Artefatos diagnósticos locais gerados

- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_resumo.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_abas.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_divergencias.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_chaves.csv`

## Contadores principais

- `qtd_pagamentos_csv_u3`: `159`
- `qtd_pagamentos_xlsx_u4`: `159`
- `qtd_linhas_csv_u3`: `175`
- `qtd_linhas_xlsx_u4`: `175`
- `qtd_linhas_multifonte_xlsx_u4`: `32`
- `qtd_pagamentos_multifonte_xlsx_u4`: `16`
- `qtd_pendencias_xlsx_u4`: `110`
- `qtd_candidatos_fifo_diagnosticos_xlsx_u4`: `109`
- `qtd_metricas_resumo_u4_csv`: `13`
- `qtd_metricas_resumo_u4_xlsx`: `13`
- `qtd_divergencias_chave`: `0`
- `qtd_divergencias_shape`: `0`
- `qtd_divergencias_valor`: `0`
- `qtd_divergencias_classe`: `0`
- `qtd_divergencias_flags`: `0`
- `qtd_divergencias_resumo`: `0`
- `qtd_divergencias_metadados`: `0`
- `qtd_divergencias_total`: `0`
- `status_geral_u5`: `auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_sem_divergencias`

## Auditoria por aba

- `Pagamentos`: obtida=`159`, esperada=`159`, status=`ok`
- `Linhas_Operacionais`: obtida=`175`, esperada=`175`, status=`ok`
- `Multifonte`: obtida=`32`, esperada=`32`, status=`ok`
- `Pendencias`: obtida=`110`, esperada=`110`, status=`ok`
- `Resumo_U4`: obtida=`13`, esperada=`13`, status=`ok`
- `Metadados`: obtida=`20`, esperada=`n/d`, status=`ok`

## Interpretação

A U.5 compara CSVs U.3, XLSX auxiliar U.4 e resumo U.4. O status `sem_divergencias` só é emitido quando não há divergências de chaves, shapes, valores, classes, flags, resumo ou metadados.

## Decisão normativa preservada

- XLSX auxiliar permanece diagnóstico.
- XLSX oficial não é alterado.
- Exportador oficial não é alterado.
- Motor econômico não é alterado.
- Recomendador oficial não é alterado.
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

`auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_sem_divergencias`

# ME-V17-F0-U0 — Auditoria das recomendações operacionais de pagamento

- MICROETAPA: V17-F0-U.0
- CLASSE: DIAGNÓSTICO / AUDITORIA EXECUTÁVEL / PAGAMENTOS
- DATA_EXECUCAO_LOCAL: 2026-05-15 19:24:25
- BASE_PRIMARIA: `saidas/diagnostico/tabela_operacional_pagamentos_v17_f0_s7g.csv`
- STATUS_GERAL_U0: `auditoria_recomendacoes_pagamento_v17_f0_u0_gerada`

## Objetivo

Auditar se as recomendações atuais de pagamento são operacionalmente executáveis, sem alterar motor, recomendador, XLSX oficial, dados, contrato, modelo, logs anteriores ou scripts existentes.

## Fontes lidas

- `saidas\diagnostico\tabela_operacional_pagamentos_v17_f0_s7g.csv` — fonte primária, 159 pagamentos esperados.
- `saidas\diagnostico\auditoria_integracao_matriz_elegibilidade_pagamentos_v17_f0_s7c.csv` — enriquecimento de elegibilidade, carência, pós-switching e integração.
- `saidas\diagnostico\auditoria_recomendacao_futura_elegibilidade_patrimonio_v17_f0_s7f.csv` — enriquecimento de componentes, saldos e aprovação.
- `saidas\diagnostico\auditoria_matriz_elegibilidade_fontes_v17_f0_s7b.csv` — matriz de elegibilidade de fontes.
- `saidas\diagnostico\auditoria_uso_operacional_tabela_pagamentos_v17_f0_s7j.csv` — auditoria operacional reduzida dos pagamentos aprovados.

## Artefatos diagnósticos gerados

- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_pagamentos.csv`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_fontes.csv`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_multifonte.csv`
- `saidas\diagnostico\auditoria_recomendacoes_pagamento_v17_f0_u0_resumo.csv`
- `saidas\diagnostico\candidatos_correcao_recomendador_pagamentos_v17_f0_u0.csv`

## Contadores principais

- `qtd_pagamentos_auditados`: `159`
- `qtd_pagamentos_com_fonte_recomendada`: `49`
- `qtd_pagamentos_sem_lote_sugerido`: `110`
- `qtd_pagamentos_multifonte`: `16`
- `qtd_pagamentos_multifonte_decompostos_u0`: `16`
- `qtd_pagamentos_multifonte_sem_decomposicao_origem`: `16`
- `qtd_pagamentos_com_lote_em_carencia`: `0`
- `qtd_pagamentos_com_fonte_sem_liquidez`: `0`
- `qtd_pagamentos_com_fonte_futura_indevida`: `0`
- `qtd_pagamentos_com_fonte_pos_switching_nao_materializada`: `0`
- `qtd_pagamentos_com_valor_maior_que_saldo_liquido`: `0`
- `qtd_pagamentos_com_cobertura_parcial`: `0`
- `qtd_pagamentos_com_soma_fontes_divergente`: `0`
- `qtd_sem_lote_com_candidato_fifo_diagnostico`: `109`
- `qtd_pagamentos_nao_auditaveis`: `0`
- `qtd_pagamentos_com_dado_insuficiente`: `0`
- `qtd_violacoes_duras_fontes_aprovadas`: `0`
- `qtd_pendencias_sem_lote_sugerido`: `110`
- `qtd_pendencias_multifonte_sem_valor_resgate_explicito`: `16`
- `qtd_candidatos_correcao_futura`: `126`
- `status_geral_u0`: `auditoria_recomendacoes_pagamento_v17_f0_u0_gerada`

## Interpretação operacional

A U.0 usa a tabela S7G como universo primário dos pagamentos e decompõe os componentes de fonte em uma tabela fonte-a-fonte. Para pagamentos multifonte, a origem atual traz componentes agregados; a U.0 estima o resgate por ordem de componentes apenas para auditoria diagnóstica, sem transformar essa estimativa em regra decisória.

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

`auditoria_recomendacoes_pagamento_v17_f0_u0_gerada`

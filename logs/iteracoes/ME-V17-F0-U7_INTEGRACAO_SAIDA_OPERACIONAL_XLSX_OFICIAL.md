# ME-V17-F0-U7 — Integração da saída operacional de pagamentos ao XLSX oficial

- MICROETAPA: V17-F0-U.7
- CLASSE: IMPLEMENTAÇÃO CONTROLADA / XLSX OFICIAL / SAÍDA OPERACIONAL
- BASELINE: main pós-merge da PR #337
- MICROETAPA_ANTERIOR: V17-F0-U.7-PRE
- STATUS_ESPERADO: `saida_operacional_pagamentos_integrada_xlsx_oficial_v17_f0_u7`

## Objetivo

Integrar ao XLSX oficial, gerado por `nucleo/gerar_planilha_operacional.py`, abas auxiliares operacionais de pagamentos derivadas da saída U.3/U.4 já validada.

A integração entrega utilidade direta sem alterar motor econômico, recomendador oficial, seleção de lotes, regras de switching, contrato, modelo, dados ou cache.

## Arquivos alterados

- `nucleo/gerar_planilha_operacional.py`
- `logs/iteracoes/ME-V17-F0-U7_INTEGRACAO_SAIDA_OPERACIONAL_XLSX_OFICIAL.md`

## Abas novas adicionadas ao XLSX oficial

- `Pagamentos Operacionais`
- `Fontes Pagamento`
- `Multifonte Resgates`
- `Pendencias Pagamentos`
- `Pagamentos Metadados`

## Fontes usadas

- `saidas/diagnostico/saida_operacional_pagamentos_v17_f0_u3_pagamentos.csv`
- `saidas/diagnostico/saida_operacional_pagamentos_v17_f0_u3_linhas.csv`
- `saidas/diagnostico/saida_operacional_pagamentos_v17_f0_u3_resumo.csv`

## Contadores esperados

- `qtd_pagamentos_operacionais`: `159`
- `qtd_linhas_fontes_pagamento`: `175`
- `qtd_linhas_multifonte`: `32`
- `qtd_pagamentos_multifonte`: `16`
- `qtd_pendencias`: `110`

## Governança preservada

- `saldo_fonte_considerado`: excluído das abas operacionais U.7; não oficial.
- `saldo_remanescente_diagnostico`: excluído das abas operacionais U.7; não oficial.
- `campos_saldo_promovidos`: `nao`
- `fifo_promovido`: `nao`
- `pendencias_convertidas_em_recomendacoes`: `nao`
- `decisao_saldos_u7pre`: `saldos_nao_aprovados_para_promocao`

## Restrições preservadas

- `aplicacao/principal.py` não alterado.
- Motor econômico não alterado.
- Recomendador oficial não alterado.
- Regras de alocação não alteradas.
- Regras de switching não alteradas.
- Dados e cache não alterados.
- Contrato e modelo oficial não alterados.
- Logs anteriores não alterados.
- Scripts diagnósticos existentes não alterados.
- FIFO permanece diagnóstico.
- Pendências permanecem bloqueios operacionais.

## Status

`saida_operacional_pagamentos_integrada_xlsx_oficial_v17_f0_u7`

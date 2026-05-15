# ME-V17-F0-U6 — Governança de promoção da saída auxiliar U.4/U.5

- MICROETAPA: V17-F0-U.6
- CLASSE: DIAGNÓSTICO / DOCUMENTAL / GOVERNANÇA
- DATA_EXECUCAO_LOCAL: 2026-05-15 20:40:09
- BASELINE: main pós-merge da PR #335
- MICROETAPA_ANTERIOR: V17-F0-U.5
- STATUS_GERAL_U6: `governanca_promocao_saida_auxiliar_v17_f0_u6_gerada`

## Objetivo

Definir a governança para eventual promoção futura da saída auxiliar U.4/U.5 para integração oficial controlada, sem implementar a integração.

A U.6 classifica abas, campos, gates, bloqueios e pré-condições. A U.6 não altera recomendador oficial, motor econômico, exportador oficial, XLSX oficial, dados, cache, contrato, modelo, logs anteriores ou módulos `nucleo/`.

## Fontes lidas

- `saidas\diagnostico\saida_operacional_pagamentos_v17_f0_u4.xlsx`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_resumo.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_abas.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_divergencias.csv`
- `saidas\diagnostico\auditoria_consistencia_exportacao_auxiliar_v17_f0_u5_chaves.csv`
- `logs\iteracoes\ME-V17-F0-U5_AUDITORIA_CONSISTENCIA_EXPORTACAO_AUXILIAR_U4.md`

## Artefatos diagnósticos locais gerados

- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_resumo.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_abas.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_campos.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_gates.csv`
- `saidas\diagnostico\governanca_promocao_saida_auxiliar_v17_f0_u6_bloqueios.csv`

## Contadores principais

- `qtd_abas_avaliadas_u6`: `6`
- `qtd_campos_avaliados_u6`: `84`
- `qtd_abas_promoviveis_como_auxiliar`: `2`
- `qtd_abas_promoviveis_com_gate`: `3`
- `qtd_abas_manter_diagnostico`: `1`
- `qtd_abas_bloqueadas_para_promocao`: `0`
- `qtd_campos_promoviveis_como_auxiliar`: `24`
- `qtd_campos_promoviveis_com_gate`: `48`
- `qtd_campos_manter_diagnostico`: `8`
- `qtd_campos_bloqueados_para_promocao`: `0`
- `qtd_campos_exigem_precondicao`: `4`
- `qtd_gates_futura_u7`: `10`
- `qtd_bloqueios_precondicoes`: `8`
- `u5_sem_divergencias_confirmado`: `sim`
- `recomendacao_promocao_u6`: `promover_apenas_apos_gates`
- `status_geral_u6`: `governanca_promocao_saida_auxiliar_v17_f0_u6_gerada`

## Governança por aba

- `Resumo_U4`: classificacao=`promovivel_como_auxiliar`, linhas=`13`, campos=`2`
- `Pagamentos`: classificacao=`promovivel_com_gate`, linhas=`159`, campos=`13`
- `Linhas_Operacionais`: classificacao=`promovivel_com_gate`, linhas=`175`, campos=`27`
- `Multifonte`: classificacao=`promovivel_com_gate`, linhas=`32`, campos=`27`
- `Pendencias`: classificacao=`manter_diagnostico`, linhas=`110`, campos=`13`
- `Metadados`: classificacao=`promovivel_como_auxiliar`, linhas=`20`, campos=`2`

## Gates obrigatórios para futura U.7

- `gate_u5_sem_divergencias`: `qtd_divergencias_total = 0`
- `gate_shape_pagamentos`: `Pagamentos = 159`
- `gate_shape_linhas`: `Linhas_Operacionais = 175`
- `gate_shape_multifonte`: `Multifonte = 32 linhas e 16 pagamentos`
- `gate_shape_pendencias`: `Pendencias = 110`
- `gate_multifonte_soma`: `soma_resgates_por_pagamento = valor_pagamento com tolerancia <= 0.01`
- `gate_fifo`: `109 FIFO continuam diagnosticos`
- `gate_saldo`: `saldo oficial apenas com auditoria contra saldo liquido real`
- `gate_metadados`: `baseline, fontes, status, restricoes e data preservados`
- `gate_nao_regressao`: `motor/recomendador/exportador_oficial/contrato/modelo inalterados`

## Bloqueios e pré-condições

- `fifo_diagnostico`: classificacao=`bloqueado_para_promocao_automatica`
- `pendencias`: classificacao=`bloqueado_para_recomendacao`
- `saldo_fonte_considerado`: classificacao=`exige_precondicao`
- `saldo_remanescente_diagnostico`: classificacao=`exige_precondicao`
- `multifonte_recomendador`: classificacao=`bloqueado_para_alterar_recomendador`
- `resumo_u4`: classificacao=`nao_substitui_resumo_oficial`
- `metadados`: classificacao=`obrigatorio_para_promocao_futura`
- `integracao_oficial`: classificacao=`bloqueado_na_u6`

## Interpretação

A U.6 confirma que a saída auxiliar U.4/U.5 pode ser considerada candidata a promoção futura apenas de forma controlada e condicionada a gates. A recomendação desta microetapa é `promover_apenas_apos_gates`.

A U.6 não promove a saída auxiliar ao XLSX oficial. A integração oficial, se aprovada, deve ser tratada em uma U.7 separada.

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
- Campos de saldo exigem pré-condição antes de qualquer uso oficial.
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

`governanca_promocao_saida_auxiliar_v17_f0_u6_gerada`

# ME-V17-F0-QFINAL — Validação integrada pós-Q.5-E

## Identificação

- MICROETAPA: ME-V17-F0-QFINAL
- TIPO: DOCUMENTAL / VALIDAÇÃO INTEGRADA
- CLASSE: FECHAMENTO DA FRENTE Q APÓS Q.5-E
- BASELINE VALIDADA: 044fd65 — Merge pull request #310 from WevertonGomesCosta/codex/auditar-repositorio-iy64fv
- Q.FINAL_APROVADA: sim
- S.7_LIBERADA_PARA_RETOMADA: sim

## Estado Git validado

- Branch local: main
- Estado validado: main...origin/main
- Working tree antes do log: limpo
- Nenhuma alteração de código foi realizada nesta microetapa.

## Comandos executados

- git status --short --branch
- git log --oneline -10
- python -m py_compile nucleo/saida_canonica.py
- python -m py_compile nucleo/inventario_lotes_expandido_pos_switching.py
- python -m py_compile scripts/diagnostico/auditar_inventario_expandido_pos_switching_v17_f0_q5.py
- python -m py_compile scripts/diagnostico/auditar_consumo_lotes_pos_switching_v17_f0_q5b.py
- python -m py_compile scripts/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.py
- python -m py_compile scripts/diagnostico/auditar_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.py
- python scripts/diagnostico/auditar_integracao_switching_pagamentos_v17_f0_q0.py
- python scripts/diagnostico/auditar_baixa_lotes_pos_switching_pagamentos_v17_f0_q1.py
- python scripts/diagnostico/auditar_inventario_expandido_pos_switching_v17_f0_q5.py
- python scripts/diagnostico/auditar_consumo_lotes_pos_switching_v17_f0_q5b.py
- python aplicacao/principal.py
- validação programática do XLSX via pandas
- verificação de hash SHA256 antes/depois para dados/dados_financeiros.xlsx e dados/cache_bcb.json

## Resultado Q.0

- status_geral_integracao=switching_integrado_ok
- origens_migradas_usadas_indevidamente_total=0
- pagamentos_usando_lote_pos_switching=14
- lotes_pos_switching_total=4

## Resultado Q.1

- fonte_base_operacional_gastos_status=localizada_canonica
- qtd_pagamentos_passados_ok_usando_lote_pos_switching=2
- qtd_pagamentos_passados_pos_switching_presentes_extrato_passado=2
- qtd_pagamentos_passados_pos_switching_ausentes_extrato_passado=0
- qtd_divergencias_baixa_pos_switching=0
- status_geral_q1=sem_divergencia_observada
- q1_alinhado_com_q0=sim

## Resultado Q.5-A

- qtd_lotes_inventario_original=14
- qtd_lotes_pos_switching_normalizados=4
- qtd_lotes_inventario_expandido=18
- lote_190_mai_no_expandido=sim
- lote_3120_mai_no_expandido=sim
- qtd_sentinelas_encontradas=2
- qtd_lotes_pos_duplicados_com_inventario_original=0
- qtd_lotes_pos_com_schema_valido=4
- qtd_lotes_pos_sem_produto_destino=0
- qtd_lotes_pos_sem_valor=0

## Resultado Q.5-B/C/D/E

- qtd_pagamentos_passados_pos_detectados=2
- qtd_pagamentos_passados_pos_com_saldo_antes_preenchido=2
- qtd_pagamentos_passados_pos_com_saldo_remanescente_preenchido=2
- qtd_lotes_pos_exauridos_apos_consumo=1
- qtd_lotes_pos_ativos_com_saldo_abatido=1
- qtd_lotes_pos_com_valoracao_previa_usada=4
- status_geral_q5b=consumo_pos_switching_integrado
- status_geral_q5c=valoracao_pos_preservada
- status_geral_q5d=rateio_multifonte_e_duplicidade_pos_protegidos
- status_geral_q5e=ativos_pos_duplicados_consolidados
- qtd_lotes_pos_ativos_duplicados_emitidos=0
- qtd_lotes_pos_ativos_duplicados_consolidados=0
- dados_financeiros_modificado_apos_execucao=nao
- cache_bcb_modificado_apos_execucao=nao

## Validação dos sentinelas

### Lote 190 mai

- Pagamento: 2026-05-13 | Aluguel | 192.89
- Saldo Antes=192.98
- Saldo Remanescente=0.0
- Classificação final: exaurido_por_saque
- Situação: não aparece como ativo com saldo cheio

### Lote 3120 mai

- Pagamento: 2026-05-13 | Pelada | 24.00
- Saldo Antes=3133.41
- Saldo Remanescente=3109.41
- Classificação final: ativo_pos_switching
- Situação: ativo com saldo abatido e valoração preservada

## Validação objetiva do XLSX

Arquivo validado:

- saidas/oficial/relatorio_operacional_v225.xlsx

Colunas observadas na aba Extrato Passado:

- Data
- Conta
- Despesa ID
- Lote
- Saldo Antes
- Bruto
- Imposto
- Líquido
- Saldo Remanescente

Resultado:

- Extrato Passado: aprovado
- Situação Atual: aprovado
- Lote 190 mai: exaurido no XLSX
- Lote 190 mai ativo cheio suspeito: falso
- Lote 3120 mai: ativo_pos_switching com saldo abatido no XLSX
- Resultado final do script: VALIDACAO_XLSX_OK

## Proteção de dados

- Hash inicial dados_financeiros.xlsx: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- Hash final dados_financeiros.xlsx: ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- dados_financeiros_modificado_apos_execucao=nao

- Hash inicial cache_bcb.json: 5c6cf6ff696e231287dd90c371366ae29fd2aafadb3b3054b5e41e82b993e4ad
- Hash final cache_bcb.json: 5c6cf6ff696e231287dd90c371366ae29fd2aafadb3b3054b5e41e82b993e4ad
- cache_bcb_modificado_apos_execucao=nao

## Comentários @codex

- PR #310: sem comentários P1/P2 até a última consulta.
- Estado: sem comentário procedente pendente na frente Q.

## Decisão

- Q.FINAL_APROVADA=sim
- S.7_LIBERADA_PARA_RETOMADA=sim

## Encaminhamento

A frente Q pode ser encerrada. A próxima frente operacional pode retomar a S.7, preservando a integração POS validada nesta microetapa.

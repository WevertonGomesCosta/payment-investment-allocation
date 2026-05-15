# ME-V17-F0-S7D_CORRECAO_PATRIMONIO_RENDIMENTO_LOTES_CONSUMIDOS

## 1) Identificação

- MICROETAPA=V17-F0-S.7-D
- OBJETIVO=corrigir apuração de patrimônio e rendimento líquido de lotes consumidos por pagamentos
- BASELINE_ENTRADA=a05b372
- BASELINE_DESCRICAO=V17-F0-S.7-C.3: remove recomposicao recursiva S6
- BRANCH_EXECUCAO=local/s7d-patrimonio-rendimento

## 2) Diagnóstico do problema

A baixa no Extrato Passado estava correta, mas a Situação Atual não transportava corretamente valores pagos/sacados para alguns lotes.

Sentinelas observadas antes da correção:

### Lote 190 mai

- Status ciclo=exaurido_por_saque
- Líq. sac.=0.00
- Líq. atual=0.00
- Patr. líq.=0.00
- Rend. líq.=-192.41
- Esperado:
  - Líq. sac.≈192.89
  - Patr. líq.≈192.89
  - Rend. líq.≈+0.48

### Lote 3120 mai

- Status ciclo=ativo_pos_switching
- Líq. sac.=0.00
- Líq. atual=3109.41
- Patr. líq.=3109.41
- Rend. líq.=-13.12
- Esperado:
  - Líq. sac.≥24.00
  - Patr. líq.≈3133.41
  - Rend. líq.≈+10.88

## 3) Local corrigido

Arquivo alterado:

- nucleo/saida_observavel.py

Função corrigida:

- somar_valores_sacados_por_lote(contexto, saida=None)

## 4) Regra aplicada

A fórmula final já estava correta:

- Patr. líq. = Líq. sac. + Líq. atual
- Rend. líq. = Patr. líq. - Orig.

A falha estava na agregação de valores sacados.

Correção aplicada:

- incluir saida.extrato_passado como fonte complementar auditável para Bruto sac. e Líq. sac.;
- usar max(valor_existente, valor_do_extrato_passado) para evitar dupla contagem quando replay/recebidos já capturaram o lote;
- preservar a agregação já existente por replay e por recebidos atuais;
- não alterar motor econômico, recomendação, ranking, switching, matriz S.7 ou Q.

## 5) Escopo preservado

- ALTERA_MOTOR_ECONOMICO=nao
- ALTERA_RECOMENDADOR=nao
- ALTERA_LOTE_SUGERIDO=nao
- ALTERA_EXTRATO_FUTURO=nao
- ALTERA_MATRIZ_S7=nao
- ALTERA_SWITCHING=nao
- ALTERA_RANKING=nao
- ALTERA_Q=nao
- ALTERA_DADOS_CACHE=nao

## 6) Validações a registrar

Executar e registrar na auditoria final:

- python -m py_compile nucleo/saida_observavel.py
- python -m py_compile scripts/diagnostico/auditar_patrimonio_rendimento_lotes_consumidos_v17_f0_s7d.py
- python scripts/diagnostico/auditar_patrimonio_rendimento_lotes_consumidos_v17_f0_s7d.py
- python aplicacao/principal.py
- git status --short --branch
- git diff --stat
- git diff --name-only

## 7) Resultado esperado do auditor S.7-D

- status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- sentinela_lote_190_ok=sim
- sentinela_lote_3120_ok=sim
- qtd_lotes_sugeridos_alterados=0
- qtd_status_recomendacao_alterados=0
- qtd_lotes_com_patr_liq_diferente_de_liq_sac_mais_liq_atual=0
- qtd_lotes_com_rend_liq_diferente_de_patr_liq_menos_orig=0

## 8) Decisão

- S.7D_CORRECAO_APROVADA=sim
- Q_REABERTA=nao
- PROXIMA_ETAPA_LIBERADA=sim

## 9) Resultado final observado

- status_geral_s7d=patrimonio_rendimento_lotes_consumidos_corrigido
- sentinela_lote_190_ok=sim
- sentinela_lote_190_liq_sacado=192.89
- sentinela_lote_190_liq_atual=0.0
- sentinela_lote_190_patr_liq=192.89
- sentinela_lote_190_rend_liq=0.48
- sentinela_lote_190_status=exaurido_por_saque
- extrato_passado_saldo_remanescente_190_preservado=sim
- sentinela_lote_3120_ok=sim
- sentinela_lote_3120_liq_sacado=24.0
- sentinela_lote_3120_liq_atual=3109.41
- sentinela_lote_3120_patr_liq=3133.41
- sentinela_lote_3120_rend_liq=10.88
- sentinela_lote_3120_status=ativo_pos_switching
- extrato_passado_saldo_remanescente_3120_preservado=sim
- qtd_lotes_com_patr_liq_diferente_de_liq_sac_mais_liq_atual=0
- qtd_lotes_com_rend_liq_diferente_de_patr_liq_menos_orig=0
- qtd_linhas_extrato_futuro_antes=159
- qtd_linhas_extrato_futuro_depois=159
- qtd_lotes_sugeridos_alterados=0
- qtd_status_recomendacao_alterados=0
- hash_dados_financeiros_xlsx=ca8a81f12f86d8e4023439f67ec84416c0b4242d9274471c0d840454331e58f4
- hash_cache_bcb_json=5c6cf6ff696e231287dd90c371366ae29fd2aafadb3b3054b5e41e82b993e4ad

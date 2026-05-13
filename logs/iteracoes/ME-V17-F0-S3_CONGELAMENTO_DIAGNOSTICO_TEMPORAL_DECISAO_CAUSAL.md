MICROETAPA: V17-F0-S.3
TIPO: DOCUMENTAL / DIAGNÓSTICO / DECISÃO
BASELINE_ENTRADA: c5ccbd0
BASELINE_DESCRICAO: Atualiza dados financeiros e cache BCB para referencia 2026-05-13
BRANCH: main
STATUS: CONGELAMENTO_DIAGNOSTICO_TEMPORAL

## Escopo
- Congelar S.0/S.1/S.2 como frente diagnóstica estabilizada para a base atual.
- Registrar que os dados/cache foram atualizados previamente em commit separado.
- Não promover qualquer correção funcional.
- Não alterar motor, ledger, ranking, saída canônica ou planilha oficial.

## Evidências consolidadas
### S.0
- correcao_aplicada=V17-F0-S.2.2
- fonte_recebidos_auditaveis=quadro_recebidos_auditaveis
- qtd_linhas_recebidos_auditaveis=14
- total_meses_auditados=17
- total_reconciliado_salarios=255885.33
- total_reconciliado_recebidos=69593.22
- total_pagamentos_futuros=183873.65
- status_geral=temporal_com_divergencias_diagnosticadas

### S.1
- correcao_aplicada=V17-F0-S.2.2
- qtd_salarios_canonicos=42
- qtd_recebidos_auditaveis=14
- total_meses_auditados=17
- total_salarios_liquidos=255885.33
- total_recebidos_auditaveis=69593.22
- total_aportes=69593.22
- diferenca_total_salarios_vs_recebidos=186292.11
- diferenca_total_salarios_vs_aportes=186292.11
- principal_causa_observada=lacuna_integracao_temporal
- status_geral=divergencias_decompostas

### S.2
- correcao_aplicada=V17-F0-S.2.3
- qtd_salarios_canonicos=42
- qtd_recebidos_auditaveis=14
- qtd_lotes_inventario=14
- total_meses_auditados=17
- total_linhas_lacuna=42
- total_salarios_liquidos=255885.33
- total_recebidos_auditaveis=69593.22
- total_aportes=69593.22
- diferenca_total_salarios_vs_recebidos=186292.11
- diferenca_total_salarios_vs_aportes=186292.11
- meses_com_lacuna_integracao_temporal=17
- linhas_classe_salario_sem_recebido_e_sem_aporte=29
- linhas_classe_pagamento_sem_fonte_temporal_no_mes=0
- linhas_classe_uso_pre_aplicacao=3
- linhas_classe_diferenca_semantica=6
- principal_classe_lacuna=salario_sem_recebido_e_sem_aporte
- status_geral=lacuna_integracao_decomposta

### Q.0 (gates preservados)
- pagamentos_usando_lote_pos_switching=5
- pagamentos_usando_origem_migrada_apos_switching=0
- origens_migradas_usadas_indevidamente_total=0
- status_geral_integracao=switching_integrado_ok

## Atualização operacional prévia
- commit: c5ccbd0
- mensagem: Atualiza dados financeiros e cache BCB para referencia 2026-05-13
- arquivos atualizados:
  - dados/cache_bcb.json
  - dados/dados_financeiros.xlsx
- a S.3 não altera esses arquivos.

## Interpretação causal
- A diferença total salários vs recebidos/aportes é 186292.11.
- A causa dominante observada em S.1 é lacuna_integracao_temporal.
- A classe dominante em S.2 é salario_sem_recebido_e_sem_aporte, com 29 linhas.
- Há 6 linhas classificadas como diferenca_semantica_salarios_vs_inventario.
- Há 3 linhas com recebido_materializado_com_uso_pre_aplicacao.
- Não há evidência, nesta frente, de bug de switching, pois Q.0 segue switching_integrado_ok.
- Não há evidência suficiente para alterar motor antes de decidir se a lacuna é de cadastro, escopo semântico, materialização de recebidos ou regra temporal de aporte.

## Decisão
- A próxima frente não deve começar corrigindo motor.
- A próxima microetapa deve identificar o ponto causal mínimo da classe dominante: salario_sem_recebido_e_sem_aporte.

## Próxima microetapa recomendada
- V17-F0-S.4 — auditar amostras da classe salario_sem_recebido_e_sem_aporte.

Objetivo da S.4:
- Ler o CSV S.2 e extrair uma tabela curta das 29 linhas da classe dominante, agrupando por mês e salário, para responder:
  - o salário existe apenas na aba Salários?
  - há recebido auditável ausente?
  - há aporte ausente?
  - o mês está fora do horizonte materializado de recebidos/aportes?
  - é diferença de escopo entre salário previsto/canonizado e recebidos efetivamente materializados?
  - a próxima correção deve ser cadastro, integração de recebidos, regra temporal ou apenas documentação semântica?

## Backlog explícito
- Robustez ampla, formatos alternativos de dados e generalizações futuras não devem bloquear a próxima frente causal, salvo se afetarem a base atual, totais, flags, classificações observadas, gates ou execução.

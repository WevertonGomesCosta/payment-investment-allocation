MICROETAPA: V17-F0-S.5
TIPO: DOCUMENTAL / DECISÃO / POLÍTICA TEMPORAL
BASELINE_ENTRADA: b56dbfa
BASELINE_DESCRICAO: V17-F0-S.4.2 recalibra pré-aplicação em S.2 e ancora paths de S.4
BRANCH: main
STATUS: DECISAO_POLITICA_HORIZONTE_MATERIALIZACAO

## Contexto
- S.0/S.1/S.2 foram congelados como diagnóstico temporal.
- S.3 formalizou a causa dominante.
- S.4 auditou a classe dominante `salario_sem_recebido_e_sem_aporte`.
- S.4.1 corrigiu falso uso de pré-aplicação por evidência mensal.
- S.4.2 preservou evidência mensal de pré-aplicação sem vínculo em classe própria e ancorou paths de S.4.
- Após S.4.2, a hipótese dominante permaneceu `fora_do_horizonte_materializado`.
- Portanto, a decisão agora é política temporal, não correção de motor.

## Evidências principais
### S.4 (classe dominante auditada)
- qtd_linhas_classe_dominante=29
- qtd_meses_classe_dominante=13
- total_salarios_classe_dominante=180742.96
- hipotese_causal_dominante=fora_do_horizonte_materializado
- tipo_proxima_acao_dominante=documentar_horizonte_ou_filtrar_previsao
- status_geral=classe_dominante_auditada

### S.2 (totais e decomposição preservados)
- total_salarios_liquidos=255885.33
- total_recebidos_auditaveis=69593.22
- total_aportes=69593.22
- diferenca_total_salarios_vs_recebidos=186292.11
- diferenca_total_salarios_vs_aportes=186292.11
- linhas_classe_salario_sem_recebido_e_sem_aporte=29
- linhas_classe_uso_pre_aplicacao=0
- linhas_classe_uso_pre_aplicacao_sem_vinculo=3
- linhas_classe_diferenca_semantica=6
- principal_classe_lacuna=salario_sem_recebido_e_sem_aporte
- status_geral=lacuna_integracao_decomposta

## Decisão de política
Salários fora do horizonte materializado de recebidos/aportes devem ser tratados como **previsão futura não materializada**, e **não** como falha de motor.

Esses salários devem permanecer auditáveis, mas separados da métrica operacional de lacuna materializada.

A política temporal deve distinguir explicitamente:
- salários previstos/canonizados;
- recebidos auditáveis materializados;
- aportes/inventário materializados;
- pagamentos com necessidade real de fonte temporal;
- `uso_pre_aplicacao_no_mes_sem_vinculo_linha` como evidência temporal que exige rastreio de vínculo, sem alterar a política de horizonte/materialização.

## Consequência prática
Antes de retomar recomendação de lotes/pagamentos:
- diagnósticos operacionais devem separar previsão futura de materialização efetiva;
- totais de lacuna operacional não devem misturar salário previsto fora do horizonte com falha real de recebimento/aporte;
- a decisão de pagamento deve usar apenas fontes materializadas ou explicitamente projetadas por regra aprovada;
- salários previstos fora do horizonte podem continuar visíveis como previsão, mas não devem ser tratados como fonte disponível;
- não há evidência para alterar motor enquanto a divergência estiver explicada por horizonte/materialização.

## Próxima microetapa recomendada
**V17-F0-S.6 — separar salários previstos de salários materializados nos diagnósticos temporais.**

Objetivo da S.6:
- ajustar S.0/S.1/S.2/S.4 ou criar camada auxiliar diagnóstica para separar:
  - `salario_previsto_futuro_nao_materializado`;
  - `salario_materializado_em_recebido`;
  - `salario_materializado_em_aporte`;
  - `lacuna_real_de_integracao`;
  - `uso_pre_aplicacao_no_mes_sem_vinculo_linha`.

A S.6 deve permanecer diagnóstica, salvo necessidade de alteração mínima em scripts diagnósticos conforme política aprovada.

A S.6 deve preservar saída canônica oficial, motor, ledger, ranking, planilha oficial e dados.

## Backlog (mantido)
- P2 PR #287: robustez de colunas alternativas de data em S.1/S.2.
- Robustez ampla de formatos de entrada.
- Melhorias de layout/refatoração não ligadas à política de horizonte.
- Validação posterior do vínculo recebido–salário–lote para casos `uso_pre_aplicacao_no_mes_sem_vinculo_linha`.

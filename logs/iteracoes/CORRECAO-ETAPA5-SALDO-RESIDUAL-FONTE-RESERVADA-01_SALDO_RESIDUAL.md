# CORRECAO-ETAPA5-SALDO-RESIDUAL-FONTE-RESERVADA-01 — saldo residual por fonte reservada

## Contexto

A auditoria diagnóstica da Etapa 5 identificou que pacotes de pagamento podiam ser descartados antes da seleção apenas porque uma fonte já havia sido reservada em data anterior. Essa regra binária levava a decisões `sem_pacote_valido` e, na trajetória interna, ao bloqueio individual com motivo `sem_pacote_valido_para_obrigacao_temporal`.

## Limitação de atualização de branch

O ambiente local iniciou na branch `work`. Não havia branch local/remota `main` disponível para checkout/pull (`git checkout main` falhou com `pathspec 'main' did not match any file(s) known to git`). O histórico local, porém, continha o merge do PR #480 (`63d5244 Merge pull request #480 ...`) como commit mais recente, preservando o baseline funcional esperado para esta frente.

## Regra anterior

Em `selecionar_pacotes_temporais_vencedores(...)`, a seleção mantinha um acumulador `reserva_por_fonte`, mas descartava pacotes de pagamento quando a mesma fonte aparecia novamente após uma reserva anterior. Na prática, a checagem tratava reserva anterior como bloqueio total da fonte, sem avaliar saldo residual referencial.

Efeito observado/esperado:

- pacote com fonte previamente reservada podia ser descartado por `fonte_referencial_ja_reservada_em_data_anterior`;
- a data podia ficar sem pacote vencedor;
- a obrigação aberta era bloqueada na aplicação da trajetória por `sem_pacote_valido_para_obrigacao_temporal`.

## Regra nova

A seleção passa a avaliar saldo residual referencial por `fonte_id`, usando identificador e valor reservável já existentes na Etapa 5:

- fonte sem identificador estável continua descartada;
- fonte sem valor referencial positivo continua descartada;
- fonte com saldo residual zero é descartada por `saldo_residual_referencial_zerado`;
- fonte ou combinação de fontes com saldo residual insuficiente é descartada por `saldo_residual_referencial_insuficiente`;
- fonte com reserva anterior não é descartada se ainda tiver saldo residual suficiente;
- para `pagamento_fonte_unica`, o saldo residual da fonte precisa cobrir o valor do pacote/obrigação;
- para `pagamento_combinacao_fontes`, a soma dos saldos residuais precisa cobrir o valor do pacote/obrigação, com distribuição estável e limitada ao saldo residual de cada fonte;
- `reserva_por_fonte` é atualizado apenas após o pacote vencedor ser selecionado.

## Limites preservados

- Sem alteração de Etapa 4.
- Sem alteração de Etapas 6, 7, 8, 9, 10 ou 11.
- Sem alteração de console, XLSX, contratos, dados, cache, ranking, switching, rendimento, imposto ou carteira.
- Sem promoção de FIFO diagnóstico, U.7 ou saldos diagnósticos.
- Sem criação de módulo, script, sentinela, nova etapa, rota paralela ou API pública.

## Resultado de validação

A validação executada nesta frente deve registrar no encerramento:

- `py_compile` dos módulos existentes;
- execução de `python -B aplicacao/principal.py`;
- contagem final do Extrato Futuro oficial;
- confirmação de que a alteração permanece restrita à Etapa 5 e a este log.

## Validação executada

### Comandos

- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py` — aprovado sem erro.
- `python -B aplicacao/principal.py` — aprovado sem erro.
- `git diff --check` — aprovado sem erro.

### Console oficial

A execução de `python -B aplicacao/principal.py` confirmou:

- Etapa 9 presente (`SAÍDA OBSERVÁVEL OFICIAL — ETAPA 9`);
- Etapa 10 presente (`PARIDADE DA RENDERIZAÇÃO OFICIAL — ETAPA 10`), com `divergências materiais: 0` e ressalva apenas de console não auditado pela própria etapa;
- Etapa 11 presente (`LIMPEZA E DEPRECIAÇÃO CONTROLADA — ETAPA 11`).

Contagem pós-correção no console:

- `qtd_obrigacoes_cobertas`: 47;
- `qtd_obrigacoes_bloqueadas`: 111.

Baseline conhecido antes da correção:

- cobertas: 2;
- bloqueadas: 156.

Resultado observado:

- aumento de 45 obrigações cobertas;
- redução de 45 obrigações bloqueadas.

### Extrato Futuro oficial

A aba `Extrato Futuro` de `saidas/oficial/relatorio_operacional_v225.xlsx` foi aberta com `openpyxl` e possui 158 linhas operacionais. A contagem pós-correção por `Status recomendação` foi:

- `coberta_referencialmente_sem_pagamento_bancario_real`: 47;
- `bloqueada_referencialmente_sem_execucao`: 111.

A contagem por `Motivo bloqueio lote` foi:

- `sem_pacote_valido_para_obrigacao_temporal`: 111;
- vazio/nulo: 47.

Verificações adicionais no Extrato Futuro:

- nenhuma coberta ficou sem `Lote sugerido`;
- nenhuma coberta ficou sem `Pacote do dia`;
- nenhuma bloqueada apresentou lote materializado indevidamente;
- não foram encontradas colunas com `U.7`, `FIFO` ou marcador diagnóstico promovido no Extrato Futuro.

### Interpretação

A correção reduziu bloqueios quando havia saldo residual referencial suficiente. Os bloqueios remanescentes continuam preservados como `sem_pacote_valido_para_obrigacao_temporal`, sem transformar obrigação bloqueada em coberta sem pacote vencedor e sem promover fontes diagnósticas.

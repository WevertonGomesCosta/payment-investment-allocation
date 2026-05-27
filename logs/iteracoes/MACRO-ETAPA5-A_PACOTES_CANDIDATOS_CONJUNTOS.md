# MACRO-ETAPA5-A — Pacotes candidatos conjuntos

## Baseline local usado
- Branch inicial detectada: `work`.
- Branch de trabalho criada: `macro-etapa5-a-pacotes-candidatos-conjuntos`.
- Histórico local (`git log -5 --oneline`) contém o commit esperado da PR #410: `ff3bd2186774845252b361158f889a6cb028f37c`.
- Baseline funcional usada: estado local do workspace com PR #410 presente no histórico.

## Disponibilidade de origin
- `git fetch origin` falhou por ausência/inacessibilidade de remoto `origin` neste ambiente.
- A comparação `origin/main...HEAD` também falhou por ausência de `origin/main`.
- Tratamento aplicado: continuação da implementação com a melhor base local disponível.

## Objetivo
Implementar a geração de pacotes candidatos conjuntos da Etapa 5 em `ResultadoMotorTemporalConjunto.pacotes_temporais_candidatos_por_data`, sem decisão final e sem execução de transições econômicas.

## Arquivos alterados
- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/MACRO-ETAPA5-A_PACOTES_CANDIDATOS_CONJUNTOS.md`

## Estruturas criadas/modificadas
- Evolução do schema de `PacoteTemporalCandidato` para incluir `pagamento_com_recebido` e status permitido `sem_obrigacao`.
- Preenchimento efetivo de `pacotes_temporais_candidatos_por_data` por data do horizonte.
- Auditoria de pacotes candidatos com contagens por tipo/status e validações de aderência ao schema.

## Funções criadas/modificadas
Criadas/evoluídas no módulo:
- `extrair_valor_obrigacao_referencial`
- `extrair_valor_fonte_referencial`
- `extrair_valor_recebido_referencial`
- `montar_fonte_candidata_pacote_temporal`
- `montar_switching_candidato_pacote_temporal`
- `gerar_pacote_sem_obrigacao`
- `gerar_pacote_sem_cobertura`
- `gerar_pacotes_pagamento_fonte_unica`
- `gerar_pacote_pagamento_combinacao_fontes`
- `gerar_pacote_pagamento_com_recebido`
- `gerar_pacotes_switching_integral`
- `gerar_pacotes_switching_mais_pagamento`
- `gerar_pacotes_temporais_candidatos_dia`
- `gerar_pacotes_temporais_candidatos`
- `auditar_pacotes_temporais_candidatos`
- `construir_resultado_motor_temporal_conjunto` atualizado para gerar/auditar pacotes.

## Tipos de pacotes gerados
- `sem_obrigacao`
- `sem_cobertura`
- `pagamento_fonte_unica`
- `pagamento_combinacao_fontes`
- `pagamento_com_recebido`
- `switching_integral_simples`
- `switching_integral_agregado`
- `switching_mais_pagamento`

## Validações executadas
- `git branch --show-current`
- `git status --short`
- `git log -5 --oneline`
- `git fetch origin`
- `git diff --name-only origin/main...HEAD`
- `python -m py_compile nucleo/motor_temporal_conjunto.py`
- `python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py`
- `python -B aplicacao/principal.py`
- `git status --short`

## Falhas de validação
- Falha esperada de ambiente em `git fetch origin` (remoto indisponível).
- Falha derivada em `git diff --name-only origin/main...HEAD` (referência `origin/main` ausente).
- Execução de `python -B aplicacao/principal.py` concluída com sucesso funcional, porém com mensagens de fallback de rede para download externo (sem bloquear a execução).

## Confirmações de escopo
- Não houve alteração em console, XLSX, saída canônica, ledger, dados ou scripts diagnósticos.
- Não foi implementada escolha de pacote vencedor.
- Não foi executado pagamento.
- Não foi promovido/executado switching novo.

## Correções pós-review (PR #411)
- Ajustado `extrair_valor_fonte_referencial` para priorizar `valor_estimado`, com fallback seguro em `valor_disponivel`, `saldo_disponivel`, `saldo`, `valor`.
- Ajustado `montar_fonte_candidata_pacote_temporal` para priorizar chaves canônicas (`fonte_id`, `tipo_fonte`, `origem_canonica`) antes dos fallbacks (`id`, `tipo`, `origem`).
- Ajustado filtro de geração de pacotes de pagamento para ignorar fontes indisponíveis quando:
  - `disponivel_na_referencia == False`; ou
  - `status_temporal == 'indisponivel'`.
- Ajustado `gerar_pacote_sem_cobertura` para considerar ausência de fontes disponíveis (não apenas ausência de fontes listadas).
- Ajustado `montar_switching_candidato_pacote_temporal` para priorizar chaves canônicas (`switching_id`, `lote_origem`, `lote_destino`) com fallback para (`id`, `lote_origem_id`, `lote_destino_id`).
- Ajustado `gerar_pacote_pagamento_com_recebido` para registrar explicitamente os recebidos referenciados em `metadados_auditoria` com `recebido_id` + referência do registro.

# ME-V17-F0-V4Z4 — Prova de equivalência entre contextos sem migrar runtime

```text
MICROETAPA: ME-V17-F0-V4Z4
VERSAO_CANDIDATA: V17-F0-V.4Z4
TIPO: DIAGNOSTICO
CLASSE: PROVA_EQUIVALENCIA_CONTEXTOS_SEM_MIGRAR_RUNTIME
BASELINE_DE_ENTRADA: V17-F0-V.4Z3
BASE_MAIN: 6cb1ea7a907cdcf0a713faf5747337d14e13f3fd
ESCOPO:
  - scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py
  - logs/iteracoes/ME-V17-F0-V4Z4_EQUIVALENCIA_CONTEXTOS.md
ALTERA_APLICACAO_PRINCIPAL: false
ALTERA_CONTEXT_BASELINE: false
ALTERA_RUNTIME: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ALTERA_RANKING: false
ALTERA_XLSX: false
ALTERA_DADOS: false
```

## Objetivo

Criar uma auditoria diagnóstica para comparar `ContextoBaseline` e `ContextoOperacionalCanonico` nos campos comuns que podem sustentar a rota runtime principal, sem migrar `aplicacao/principal.py`.

A V4Z4 não altera runtime e não autoriza Etapa 5. Ela mede a equivalência estrutural entre contextos e, quando houver divergência, classifica se a divergência é apenas documental/metadados ou se possui impacto operacional potencial sobre a rota runtime.

## Campos comparados

```text
pacote_config
execucao
calendario_financeiro
pacote_planilha
pacote_entrada_resolvida
auditoria_pacote_entrada_resolvida
validacao_pre_execucao
carteira_canonica
dados_operacionais
recebidos_auditaveis
fontes_elegiveis_pagamento
saldo_disponivel_geral
cache_cdi
nucleo_financeiro
replay_passado
ranking_carteira
tabela_iof
faixas_ir
```

## Campos com detalhamento específico

O auditor detalha divergências em:

```text
pacote_entrada_resolvida
validacao_pre_execucao
fontes_elegiveis_pagamento
cache_cdi
```

Para cada campo, o auditor classifica a divergência como:

```text
documental
estrutural
operacional
bloqueante
```

A classificação é interpretativa e diagnóstica. Ela não altera runtime nem substitui validação econômica.

## Regra de proteção

O auditor também verifica se `ContextoOperacionalCanonico` permanece sem campos transicionais, incluindo shadows, benchmarks, auditorias shadow e motores transicionais.

## Saídas esperadas

Ao executar sem `--sem-arquivos`, o auditor grava:

```text
relatorios/atuais/auditoria_equivalencia_contextos_v4z4/equivalencia_contextos_v4z4.json
relatorios/atuais/auditoria_equivalencia_contextos_v4z4/resumo_equivalencia_contextos_v4z4.md
```

## Comandos de validação

```bash
python -m py_compile scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py
python scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py --sem-arquivos
```

## Condição de interpretação

- Se `equivalencia_contextos_ok=true`, os contextos são equivalentes em todos os campos comparados.
- Se `equivalencia_contextos_ok=false`, mas `equivalencia_operacional_minima_ok=true`, as divergências detectadas não parecem afetar runtime operacional pelos critérios do auditor.
- Se `equivalencia_operacional_minima_ok=false`, a próxima microetapa deve analisar divergências operacionais antes de qualquer migração.

## Decisão

```text
STATUS: DIAGNOSTICO_APENAS
ETAPA_5: BLOQUEADA
PROXIMA_ACAO: EXECUTAR_AUDITOR_V4Z4_ATUALIZADO_LOCALMENTE_E_ANALISAR_IMPACTO_RUNTIME
```

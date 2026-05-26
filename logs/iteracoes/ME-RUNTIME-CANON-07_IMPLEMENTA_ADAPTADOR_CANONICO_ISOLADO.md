# ME-RUNTIME-CANON-07 — Implementação isolada do adaptador canônico compatível

## Objetivo

Implementar o adaptador canônico compatível para saída canônica em modo isolado, sem ativar no runtime principal, sem alterar `aplicacao/principal.py` e sem substituir `ContextoBaseline`.

## Baseline de entrada

```text
BASELINE: main
HEAD: 8b7e9536382e47357ad74fc51a9685b3dd494dff
ULTIMO_MERGE: PR #376 — ME-RUNTIME-CANON-06 desenho do adaptador canônico de saída
```

## Escopo permitido

```text
nucleo/contexto_saida_canonica_compat.py
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/contexto_baseline.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
nucleo/construir_saida_canonica_v17_c7.py
nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
scripts/diagnostico/*
dados/*
saidas/*
```

A ME-RUNTIME-CANON-07 não altera motor, replay, ledger, ranking, pagamentos, switching, saída canônica oficial, console, XLSX ou regra econômica.

## Alteração aplicada

Criado o módulo:

```text
nucleo/contexto_saida_canonica_compat.py
```

O módulo define:

```text
ComponentesTransicionaisSaidaCanonica
ContextoSaidaCanonicaCompat
construir_contexto_saida_canonica_compat(...)
campos_contexto_saida_canonica_compat()
validar_contexto_saida_canonica_compat(...)
```

## Contrato implementado

O adaptador copia campos já materializados de `ContextoOperacionalCanonico` e exige explicitamente os componentes transicionais ainda necessários à saída canônica legada:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

Esses campos são recebidos por `ComponentesTransicionaisSaidaCanonica` ou por mapping/objeto compatível. Eles não são adicionados a `ContextoOperacionalCanonico`.

## Garantias de isolamento

O módulo novo:

```text
não executa download
não lê planilha
não recalcula motor
não chama replay
não gera XLSX
não altera aplicacao/principal.py
não substitui carregar_contexto_baseline()
não é importado pela rota principal
```

A rota principal continua usando `ContextoBaseline`.

## Decisão

```text
STATUS: ADAPTADOR_CANONICO_COMPATIVEL_IMPLEMENTADO_ISOLADO
ATIVA_RUNTIME_ALTERNATIVO: false
TROCA_CONTEXT_BASELINE: false
ALTERA_APLICACAO_PRINCIPAL: false
ALTERA_SAIDA_CANONICA_OFICIAL: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: validar compilação e depois abrir comparação observável controlada
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Validação isolada opcional do módulo:

```bash
python - <<'PY'
from nucleo.contexto_saida_canonica_compat import campos_contexto_saida_canonica_compat
print(campos_contexto_saida_canonica_compat())
PY
```

## Próxima etapa recomendada

```text
ME-RUNTIME-CANON-08 — comparação observável controlada entre saída por ContextoBaseline e adaptador canônico compatível, sem promover automaticamente.
```

# ME-RUNTIME-CANON-10 — Comparação de componentes internos entre contextos

## Objetivo

Adicionar um utilitário diagnóstico isolado para comparar componentes internos de `ContextoBaseline` e `ContextoOperacionalCanonico` antes da construção da saída canônica.

A microetapa busca localizar o primeiro ponto de divergência entre os contextos, sem corrigir motor, replay, saída canônica ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 73eb479277f2adfb27d0eb6f9b502ce43ea389b7
ULTIMO_MERGE: PR #379 — ME-RUNTIME-CANON-09 diagnostica divergências do contexto compatível
```

## Escopo permitido

```text
nucleo/comparacao_componentes_contextos.py
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

A ME-RUNTIME-CANON-10 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Auditoria da PR #379 e merge

A PR #379 foi auditada como fechamento documental da ME-RUNTIME-CANON-09:

```text
PR: #379
STATUS: aprovada e mergeada
MERGE_COMMIT: 73eb479277f2adfb27d0eb6f9b502ce43ea389b7
ESCOPO: logs/iteracoes/*
ALTERA_RUNTIME: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
```

## Alteração aplicada

Criado o módulo isolado:

```text
nucleo/comparacao_componentes_contextos.py
```

O módulo define:

```text
ResultadoComparacaoComponentesContextos
comparar_componentes_contextos(...)
imprimir_resumo_comparacao_componentes(...)
```

## Componentes comparados por padrão

```text
cache_cdi.serie_cdi
calendario_financeiro
replay_passado.log_passado
replay_passado.lotes_apos_replay
fontes_elegiveis_pagamento
saldo_disponivel_geral
decisao_local_v1
recomputacao_sequencial_central_v1
```

## Garantias de isolamento

O módulo novo:

```text
não altera aplicacao/principal.py
não substitui ContextoBaseline
não promove ContextoSaidaCanonicaCompat
não chama construir_saida_canonica_com_switching_v17_c7(...)
não escreve XLSX oficial
não reexecuta motor
não reexecuta replay
não altera regra econômica
não cria gate permanente
```

## Critério de interpretação

A ME-RUNTIME-CANON-10 não deve corrigir divergências. Ela deve apenas identificar se a primeira divergência nasce em:

```text
cache CDI
calendário financeiro
replay_passado.log_passado
replay_passado.lotes_apos_replay
fontes_elegiveis_pagamento
saldo_disponivel_geral
camadas transicionais decisórias
```

Se `replay_passado.log_passado` ou `replay_passado.lotes_apos_replay` divergirem, não corrigir saída canônica; a próxima microetapa deve isolar a diferença na construção do replay/contexto.

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Validação isolada mínima:

```bash
python - <<'PY'
from nucleo.comparacao_componentes_contextos import ResultadoComparacaoComponentesContextos
print(ResultadoComparacaoComponentesContextos.__name__)
PY
```

Validação comparativa completa:

```bash
python - <<'PY'
from pathlib import Path
from nucleo.contexto_baseline import carregar_contexto_baseline, carregar_contexto_operacional_canonico
from nucleo.comparacao_componentes_contextos import comparar_componentes_contextos, imprimir_resumo_comparacao_componentes

raiz = Path.cwd()
ctx_base = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
ctx_can = carregar_contexto_operacional_canonico(raiz_repositorio=raiz, instalar_automaticamente=False)
resultado = comparar_componentes_contextos(ctx_base, ctx_can)
imprimir_resumo_comparacao_componentes(resultado)
raise SystemExit(0 if resultado.ok else 1)
PY
```

## Decisão

```text
STATUS: COMPARADOR_COMPONENTES_INTERNOS_DISPONIBILIZADO_ISOLADO
ALTERA_RUNTIME_PRINCIPAL: false
ALTERA_SAIDA_CANONICA: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
ETAPA_5_LIBERADA: false
```

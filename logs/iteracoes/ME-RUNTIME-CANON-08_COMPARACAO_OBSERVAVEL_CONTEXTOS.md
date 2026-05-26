# ME-RUNTIME-CANON-08 — Comparação observável controlada entre ContextoBaseline e ContextoSaidaCanonicaCompat

## Objetivo

Desenhar e disponibilizar comparação observável controlada entre a saída gerada pela rota atual com `ContextoBaseline` e uma saída experimental construída via `ContextoSaidaCanonicaCompat`.

A microetapa não promove a rota compatível, não substitui `ContextoBaseline`, não altera `aplicacao/principal.py` e não altera a saída XLSX oficial.

## Baseline de entrada

```text
BASELINE: main
HEAD: 66f0687d679ca51b050af4c934191e1412dc519b
ULTIMO_MERGE: PR #377 — ME-RUNTIME-CANON-07 implementa adaptador canônico isolado
```

## Auditoria pós-merge da ME-RUNTIME-CANON-07

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 8b7e953 -> 66f0687
git status --short: vazio
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Marcadores observáveis preservados:

```text
relatorio_operacional_v225.xlsx: gerado
Patrimônio líquido atual: 79892.30
Rendimento líquido atual: 952.14
Ranking top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
Switchings reais: 4
```

## Escopo permitido

```text
nucleo/comparacao_saida_canonica_compat.py
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

A ME-RUNTIME-CANON-08 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Alteração aplicada

Criado o módulo isolado:

```text
nucleo/comparacao_saida_canonica_compat.py
```

O módulo define:

```text
ResultadoComparacaoSaidaCanonicaCompat
comparar_saida_canonica_baseline_vs_compat(...)
construir_saida_canonica_via_contexto_compat(...)
imprimir_resumo_comparacao(...)
```

## Métricas comparadas

A comparação cobre:

```text
Patrimônio líquido atual
Rendimento líquido atual
Rendimento líquido reconciliado contra recebidos
Ranking top 1
Quantidade de switchings reais
Quantidade de lotes ativos
Quantidade de lotes exauridos
Quantidade de linhas do extrato passado
Quantidade de linhas do extrato futuro
Hash de lotes ativos
Hash de lotes exauridos
Hash de extrato passado
Hash de extrato futuro
Hash de Situação Atual
Hash de switchings
```

## Garantias de isolamento

O módulo novo:

```text
não altera aplicacao/principal.py
não substitui carregar_contexto_baseline()
não escreve XLSX oficial
não grava arquivos de saída
não cria gate permanente
não altera ContextoOperacionalCanonico
não altera ContextoBaseline
não altera saída canônica oficial
não promove automaticamente a rota compatível
```

## Modo de uso isolado recomendado

A validação isolada pode ser feita manualmente por snippet, sem tocar no runtime principal:

```bash
python - <<'PY'
from pathlib import Path
from nucleo.contexto_baseline import carregar_contexto_baseline, carregar_contexto_operacional_canonico
from nucleo.comparacao_saida_canonica_compat import comparar_saida_canonica_baseline_vs_compat, imprimir_resumo_comparacao

raiz = Path.cwd()
ctx_base = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
ctx_can = carregar_contexto_operacional_canonico(raiz_repositorio=raiz, instalar_automaticamente=False)
resultado = comparar_saida_canonica_baseline_vs_compat(ctx_base, ctx_can)
imprimir_resumo_comparacao(resultado)
raise SystemExit(0 if resultado.ok else 1)
PY
```

Esse snippet executa apenas comparação em memória e não altera a rota oficial.

## Decisão

```text
STATUS: COMPARACAO_OBSERVAVEL_CONTROLADA_DISPONIBILIZADA_ISOLADA
EXECUTA_COMPARACAO_NO_RUNTIME_PRINCIPAL: false
PROMOVE_ROTA_COMPAT: false
TROCA_CONTEXT_BASELINE: false
ALTERA_APLICACAO_PRINCIPAL: false
ALTERA_SAIDA_CANONICA_OFICIAL: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: validar comparação isolada e decidir se equivalência observável permite etapa de decisão controlada
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Validação isolada recomendada:

```bash
python - <<'PY'
from nucleo.comparacao_saida_canonica_compat import ResultadoComparacaoSaidaCanonicaCompat
print(ResultadoComparacaoSaidaCanonicaCompat.__name__)
PY
```

Validação comparativa completa recomendada antes do merge:

```bash
python - <<'PY'
from pathlib import Path
from nucleo.contexto_baseline import carregar_contexto_baseline, carregar_contexto_operacional_canonico
from nucleo.comparacao_saida_canonica_compat import comparar_saida_canonica_baseline_vs_compat, imprimir_resumo_comparacao

raiz = Path.cwd()
ctx_base = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
ctx_can = carregar_contexto_operacional_canonico(raiz_repositorio=raiz, instalar_automaticamente=False)
resultado = comparar_saida_canonica_baseline_vs_compat(ctx_base, ctx_can)
imprimir_resumo_comparacao(resultado)
raise SystemExit(0 if resultado.ok else 1)
PY
```

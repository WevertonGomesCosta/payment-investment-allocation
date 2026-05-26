# ME-RUNTIME-CANON-11 — Detalhamento das divergências internas entre contextos

## Objetivo

Adicionar um utilitário diagnóstico isolado para detalhar as divergências internas detectadas pela ME-RUNTIME-CANON-10, começando por:

```text
cache_cdi.serie_cdi
replay_passado.log_passado
replay_passado.lotes_apos_replay
```

A microetapa não corrige motor, replay, saída canônica ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 618390e82bd721965cf522685e388a8a42dc4c24
ULTIMO_MERGE: PR #380 — ME-RUNTIME-CANON-10 compara componentes internos dos contextos
```

## Auditoria pós-merge da ME-RUNTIME-CANON-10

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 73eb479 -> 618390e
git status --short: vazio
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Marcadores da rota oficial preservados:

```text
relatorio_operacional_v225.xlsx: gerado
Patrimônio líquido atual: 79892.30
Rendimento líquido atual: 952.14
Ranking top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
Switchings reais: 4
```

Gate V4Z:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Escopo permitido

```text
nucleo/detalhar_divergencias_componentes_contextos.py
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

A ME-RUNTIME-CANON-11 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Evidência da ME-RUNTIME-CANON-10

A comparação interna retornou:

```text
ok=False
divergencias=6
```

Componentes divergentes:

```text
cache_cdi.serie_cdi
replay_passado.log_passado
replay_passado.lotes_apos_replay
fontes_elegiveis_pagamento
decisao_local_v1
recomputacao_sequencial_central_v1
```

Componentes iguais:

```text
calendario_financeiro
saldo_disponivel_geral
```

## Alteração aplicada

Criado o módulo isolado:

```text
nucleo/detalhar_divergencias_componentes_contextos.py
```

O módulo define:

```text
ResultadoDetalhamentoDivergenciasComponentes
detalhar_divergencias_componentes_contextos(...)
imprimir_detalhamento_divergencias_componentes(...)
```

## Diagnósticos detalhados

O utilitário detalha:

```text
cache_cdi.serie_cdi:
  quantidade de chaves em cada contexto
  chaves ausentes em cada lado
  valores divergentes por data/chave

replay_passado.log_passado:
  número de linhas
  colunas em cada lado
  colunas exclusivas
  divergências por chave operacional e campos divergentes

replay_passado.lotes_apos_replay:
  número de lotes
  IDs amostrados
  divergências por lote e campos divergentes
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

A ME-RUNTIME-CANON-11 não deve corrigir divergências. Ela deve apenas detalhar se a diferença nasce em:

```text
cache CDI
log do replay passado
estado dos lotes após replay
```

Se a diferença aparecer primeiro em `cache_cdi.serie_cdi`, a próxima etapa deve investigar se os dois contextos estão usando materializações distintas da série CDI/cache.

Se a diferença aparecer primeiro em `replay_passado.log_passado`, a próxima etapa deve investigar a construção do replay e não a saída canônica.

Se a diferença aparecer primeiro em `replay_passado.lotes_apos_replay`, a próxima etapa deve investigar estado dos lotes pós-replay antes de qualquer intervenção no XLSX.

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Validação isolada mínima:

```bash
python - <<'PY'
from nucleo.detalhar_divergencias_componentes_contextos import ResultadoDetalhamentoDivergenciasComponentes
print(ResultadoDetalhamentoDivergenciasComponentes.__name__)
PY
```

Validação comparativa completa:

```bash
python - <<'PY'
from pathlib import Path
from nucleo.contexto_baseline import carregar_contexto_baseline, carregar_contexto_operacional_canonico
from nucleo.detalhar_divergencias_componentes_contextos import detalhar_divergencias_componentes_contextos, imprimir_detalhamento_divergencias_componentes

raiz = Path.cwd()
ctx_base = carregar_contexto_baseline(raiz_repositorio=raiz, instalar_automaticamente=False)
ctx_can = carregar_contexto_operacional_canonico(raiz_repositorio=raiz, instalar_automaticamente=False)
resultado = detalhar_divergencias_componentes_contextos(ctx_base, ctx_can)
imprimir_detalhamento_divergencias_componentes(resultado)
raise SystemExit(0 if resultado.ok else 1)
PY
```

## Decisão

```text
STATUS: DETALHADOR_DIVERGENCIAS_COMPONENTES_DISPONIBILIZADO_ISOLADO
ALTERA_RUNTIME_PRINCIPAL: false
ALTERA_SAIDA_CANONICA: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
ETAPA_5_LIBERADA: false
```

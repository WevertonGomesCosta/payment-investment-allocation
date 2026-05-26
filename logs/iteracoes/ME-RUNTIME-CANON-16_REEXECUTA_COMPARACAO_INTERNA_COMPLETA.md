# ME-RUNTIME-CANON-16 — Reexecução da comparação interna completa entre contextos

## Objetivo

Reexecutar a comparação interna completa entre `ContextoBaseline` e `ContextoOperacionalCanonico` após a ME-RUNTIME-CANON-15 ter eliminado a divergência primária em `cache_cdi.serie_cdi`.

Esta microetapa é diagnóstica. Não corrige replay, saída canônica, motor, ranking, pagamentos, switching, ledger, console, XLSX oficial ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 503097e718e8f60c5df266832828a8f3c2c57198
ULTIMO_MERGE: PR #385 — ME-RUNTIME-CANON-15 amplia JanelaConsultaCDI na Etapa 1
```

## Auditoria pós-merge da ME-RUNTIME-CANON-15

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: da2c0f6 -> 503097e
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-16.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis atuais, com cache local atualizado:

```text
relatorio_operacional_v225.xlsx: gerado
Patrimônio líquido atual: 79905.02
Rendimento líquido atual: 964.86
Rendimento líquido atual — reconciliado contra recebidos: 877.86
Ranking top 1: Mercado Pago Cofrinho 120% CDI (Meli+)
Switchings reais: 4
Cache CDI diário: 96 datas
Data inicial da consulta: 2026-01-01
Data final da consulta: 2026-05-26
Última data com fator no cache: 2026-05-22
```

Gate V4Z:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Evidência da ME-RUNTIME-CANON-15

A comparação diagnóstica focada em `cache_cdi.serie_cdi` retornou:

```text
=== COMPARAÇÃO DE COMPONENTES INTERNOS — CONTEXTOS ===
ok=True
divergencias=0
cache_cdi.serie_cdi: igual=True | tipo_base=dict | tipo_can=dict
```

Portanto, a divergência primária de janela CDI foi eliminada.

## Escopo permitido

```text
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
scripts/diagnostico/*
saidas/*
```

A ME-RUNTIME-CANON-16 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Comparação interna completa a reexecutar

Usar o utilitário já existente:

```text
nucleo/comparacao_componentes_contextos.py
```

Componentes da comparação completa:

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

## Interpretação esperada

A comparação deve responder:

```text
1. cache_cdi.serie_cdi permanece equivalente após a ME-15?
2. replay_passado.log_passado ainda diverge?
3. replay_passado.lotes_apos_replay ainda diverge?
4. fontes_elegiveis_pagamento ainda diverge?
5. decisao_local_v1 ainda diverge?
6. recomputacao_sequencial_central_v1 ainda diverge?
```

Se `cache_cdi.serie_cdi` permanecer igual, qualquer divergência residual deve ser classificada como divergência posterior à materialização CDI, provavelmente em replay passado, estado dos lotes, fontes elegíveis ou camadas transicionais decisórias.

## O que esta microetapa não faz

```text
não corrige replay_passado
não corrige lotes_apos_replay
não corrige saida_canonica.py
não corrige saida_observavel.py
não altera motor
não altera regra econômica
não promove ContextoSaidaCanonicaCompat
não substitui ContextoBaseline
não commita dados/cache_bcb.json
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Comparação interna completa:

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

## Critério de decisão

```text
Se ok=True:
  registrar equivalência interna completa e abrir etapa posterior de comparação observável completa antes de qualquer transição.

Se ok=False:
  classificar divergências residuais por componente e abrir próxima microetapa diagnóstica no primeiro componente divergente remanescente.
```

## Decisão

```text
STATUS: COMPARACAO_INTERNA_COMPLETA_SOLICITADA
ALTERA_RUNTIME_PRINCIPAL: false
ALTERA_NUCLEO: false
ALTERA_REPLAY: false
ALTERA_SAIDA_CANONICA: false
ALTERA_MOTOR: false
ALTERA_DADOS: false
ALTERA_REGRA_ECONOMICA: false
PROMOVE_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUI_CONTEXTBASELINE: false
ETAPA_5_LIBERADA: false
```

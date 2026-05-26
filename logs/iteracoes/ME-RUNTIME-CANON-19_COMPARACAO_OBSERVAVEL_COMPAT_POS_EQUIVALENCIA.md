# ME-RUNTIME-CANON-19 — Comparação observável controlada pós-equivalência interna

## Objetivo

Reexecutar, de forma diagnóstica, a comparação observável controlada entre a saída oficial gerada por `ContextoBaseline` e a saída experimental em memória gerada por `ContextoSaidaCanonicaCompat`, agora após a ME-RUNTIME-CANON-15/16 ter comprovado equivalência interna em:

```text
cache_cdi.serie_cdi
calendario_financeiro
replay_passado.log_passado
replay_passado.lotes_apos_replay
fontes_elegiveis_pagamento
saldo_disponivel_geral
```

Esta microetapa não promove a rota compatível, não substitui `ContextoBaseline`, não altera saída canônica oficial, não escreve XLSX alternativo e não altera motor, replay, ledger, ranking, pagamentos, switching ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: fab327d0d937f3255a21053bcbf7c641dc90a92d
ULTIMO_MERGE: PR #388 — ME-RUNTIME-CANON-18 audita consumo dos pacotes decisórios pela saída
```

## Auditoria pós-merge da ME-RUNTIME-CANON-18

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: f6714b4 -> fab327d
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-19.
Não deve ser misturada ao merge desta microetapa.
```

Marcadores observáveis atuais:

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

## Contexto técnico

A ME-RUNTIME-CANON-18 classificou que:

```text
saida_canonica.py consome decisao_local_v1 como dependência observável/transicional do extrato futuro e do fallback auditável de recebido_disponivel.
saida_canonica.py consome recomputacao_sequencial_central_v1 via mapa_central, usado no extrato futuro e no ledger temporal conjunto.
comparacao_saida_canonica_compat.py injeta ambos como ComponentesTransicionaisSaidaCanonica vindos do ContextoBaseline.
```

Portanto, a comparação observável controlada deve testar se o adaptador compatível, recebendo os componentes transicionais explicitamente, preserva a saída observável já que os componentes internos canônicos principais estão equivalentes.

## Comparação observável a executar

Usar o utilitário já existente:

```text
nucleo/comparacao_saida_canonica_compat.py
```

Comando recomendado:

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

## Itens observáveis a comparar

A comparação deve cobrir, no mínimo:

```text
patrimonio_liquido_atual
rendimento_liquido_atual
rendimento_liquido_reconciliado_recebidos
ranking_top1
qtd_switchings_reais
qtd_lotes_ativos
qtd_lotes_exauridos
qtd_extrato_passado
qtd_extrato_futuro
qtd_blocos_situacao_atual
hash_lotes_ativos
hash_lotes_exauridos
hash_extrato_passado
hash_extrato_futuro
hash_situacao_atual
hash_switchings
```

## Interpretação esperada

### Se `ok=True`

```text
A saída observável via ContextoSaidaCanonicaCompat é equivalente à saída baseline em memória.
A próxima etapa segura será uma decisão documental sobre a rota de transição, ainda sem ativar no runtime principal.
```

### Se `ok=False`

```text
As divergências devem ser classificadas por campo observável e por tabela/hash.
A próxima microetapa deve focar no primeiro bloco observável divergente, sem corrigir saída canônica, motor, replay ou regra econômica nesta etapa.
```

## Critérios de validação

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
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

## O que esta microetapa não faz

```text
não altera aplicacao/principal.py
não altera saida_canonica.py
não altera construir_saida_canonica_v17_c7.py
não altera comparacao_saida_canonica_compat.py
não altera contexto_saida_canonica_compat.py
não altera ContextoBaseline
não altera ContextoOperacionalCanonico
não escreve XLSX oficial alternativo
não promove ContextoSaidaCanonicaCompat
não substitui ContextoBaseline
não corrige replay
não altera motor
não altera regra econômica
não commita dados/cache_bcb.json
```

## Decisão

```text
STATUS: COMPARACAO_OBSERVAVEL_CONTROLADA_SOLICITADA
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

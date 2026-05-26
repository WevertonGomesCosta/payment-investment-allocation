# ME-RUNTIME-CANON-09 — Diagnóstico das divergências econômicas do ContextoSaidaCanonicaCompat

## Objetivo

Investigar, de forma diagnóstica e documental, por que `ContextoSaidaCanonicaCompat` ainda produz divergências econômicas em relação à rota oficial com `ContextoBaseline`, especialmente em:

```text
dias úteis
rendimento
imposto
lotes exauridos
extrato passado
Situação Atual
```

Esta microetapa não promove a rota compatível, não substitui `ContextoBaseline`, não altera `aplicacao/principal.py`, não altera saída oficial e não muda regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 661b5d86b4003acf4ac0220c3f71d0d7683c8140
ULTIMO_MERGE: PR #378 — ME-RUNTIME-CANON-08 comparação observável controlada
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

## Auditoria pós-merge da ME-RUNTIME-CANON-08

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 66f0687 -> 661b5d8
git status --short: vazio
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Arquivos adicionados pelo merge da PR #378:

```text
logs/iteracoes/ME-RUNTIME-CANON-08_COMPARACAO_OBSERVAVEL_CONTEXTOS.md
nucleo/comparacao_saida_canonica_compat.py
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

## Evidência da comparação ME-RUNTIME-CANON-08

A comparação completa entre `ContextoBaseline` e `ContextoSaidaCanonicaCompat` retornou:

```text
ok=False
divergencias=7
```

Métricas principais:

```text
patrimonio_liquido_atual: baseline=79892.30 | compat=79568.08
rendimento_liquido_atual: baseline=952.14 | compat=627.92
rendimento_liquido_reconciliado_recebidos: baseline=865.14 | compat=540.92
ranking_top1: baseline=Mercado Pago Cofrinho 120% CDI (Meli+) | compat=Mercado Pago Cofrinho 120% CDI (Meli+)
qtd_switchings_reais: baseline=4 | compat=4
qtd_lotes_ativos: baseline=5 | compat=5
qtd_lotes_exauridos: baseline=13 | compat=13
qtd_extrato_passado: baseline=114 | compat=114
qtd_extrato_futuro: baseline=156 | compat=156
qtd_blocos_situacao_atual: baseline=9 | compat=9
```

Diferença patrimonial:

```text
79892.30 - 79568.08 = 324.22
```

## Divergências observadas

### 1. Extrato passado

A divergência em `hash_extrato_passado` mostrou diferença em pagamentos históricos, especialmente em bruto, imposto, saldo antes e saldo remanescente.

Exemplos:

```text
2026-02-09 | Cartão Azul | Lote 10342 fev.
Bruto: baseline=6021.75 | compat=6014.06
Imposto: baseline=7.69 | compat=0.0
Saldo Antes: baseline=10356.83 | compat=10342.0
Saldo Remanescente: baseline=4335.08 | compat=4327.94
```

```text
2026-02-10 | Cartão PS | Lote 4000 fev.
Bruto: baseline=123.74 | compat=123.44
Imposto: baseline=0.3 | compat=0.0
Saldo Antes: baseline=4011.48 | compat=4000.0
Saldo Remanescente: baseline=3887.74 | compat=3876.56
```

Classificação:

```text
TIPO: divergência econômica real da rota compatível
SINAL: compat não reproduz integralmente rendimento/imposto histórico do replay passado
IMPLICAÇÃO: rota compatível ainda não pode substituir ContextoBaseline
```

### 2. Lotes ativos

A divergência em `hash_lotes_ativos` mostrou diferença material no lote `Lote 5680 abr.`:

```text
Dias úteis: baseline=27 | compat=16
Bruto: baseline=4857.51 | compat=4814.28
Líquido: baseline=4833.99 | compat=4800.49
```

Classificação:

```text
TIPO: divergência de valuation temporal
SINAL: compat calcula idade útil/valoração com janela mais curta para lote ativo antigo
IMPLICAÇÃO: diferença afeta diretamente patrimônio líquido e rendimento atual
```

### 3. Lotes exauridos

A divergência em `hash_lotes_exauridos` mostrou que vários lotes exauridos antigos perdem dias úteis no contexto compatível:

```text
Lote 10342 fev.: Dias úteis baseline=24 | compat=0
Lote 2063,11 fev.: Dias úteis baseline=1 | compat=0
Lote 4000 fev.: Dias úteis baseline=25 | compat=0
Lote 3000 mar. B: Dias úteis baseline=41 | compat=2
Lote 3000 mar. V: Dias úteis baseline=42 | compat=2
```

Classificação:

```text
TIPO: divergência de reconstrução temporal de lotes exauridos/migrados
SINAL: compat não preserva integralmente data-base histórica, último uso ou janela útil usada pela baseline
IMPLICAÇÃO: rota compatível ainda não reproduz idade fiscal/econômica de lotes encerrados
```

### 4. Situação Atual

`hash_situacao_atual` agora cobre todos os blocos da Situação Atual e confirmou divergências reais em:

```text
Lotes ativos — identificação
Lotes ativos — valores e patrimônio
Lotes exauridos — identificação
Lotes exauridos — valores e patrimônio
Origens migradas por switching — reconciliação patrimonial
Patrimônio total dos lotes
```

Classificação:

```text
TIPO: divergência observável completa, não falso positivo de hash parcial
SINAL: a Situação Atual compatível reflete diferenças econômicas reais já vistas em lotes e extrato passado
IMPLICAÇÃO: ME-RUNTIME-CANON-08 funcionou como detector; a equivalência ainda não foi atingida
```

## Análise causal preliminar

### Causa provável 1 — `ContextoOperacionalCanonico` é limpo demais para reproduzir saída legada

`ContextoOperacionalCanonico` contém apenas campos canônicos e não inclui as camadas transicionais históricas que `ContextoBaseline` ainda carrega.

Campos transicionais exclusivos de `ContextoBaseline` relevantes para a rota legada:

```text
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
triagem_motor
```

A ME-RUNTIME-CANON-07 incluiu apenas:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

E isso foi insuficiente para equivalência observável.

### Causa provável 2 — construção independente dos contextos altera objetos derivados

A comparação da ME-RUNTIME-CANON-08 carrega separadamente:

```text
ctx_base = carregar_contexto_baseline(...)
ctx_can = carregar_contexto_operacional_canonico(...)
```

Embora ambos usem os mesmos dados de entrada, os objetos derivados podem divergir por ordem de materialização, componentes transicionais, metadados de cache e side effects internos de construção.

A divergência nos campos de replay sugere que `replay_passado` e/ou seus objetos internos não são observavelmente idênticos entre os dois contextos.

### Causa provável 3 — saída canônica ainda usa replay e calendário de forma sensível ao contexto

`saida_canonica.py` constrói extrato passado a partir de `contexto.replay_passado.log_passado`, agregando bruto, imposto, liquido, saldo antes, saldo remanescente e lote usado. Portanto, qualquer diferença no replay passado se propaga diretamente ao extrato passado.

Além disso, `_construir_lotes_situacao(...)` usa:

```text
contexto.replay_passado
contexto.execucao.data_referencia
contexto.calendario_financeiro
contexto.pacote_config.conteudo
contexto.cache_cdi.serie_cdi
contexto.tabela_iof
contexto.faixas_ir
```

para calcular valor bruto, valor líquido, saldo remanescente, data-base de idade, dias úteis e classificação ativo/exaurido. Pequenas diferenças em qualquer desses insumos produzem as divergências observadas.

### Causa provável 4 — componentes transicionais de pagamento futuro não bastam para replay passado

`decisao_local_v1` e `recomputacao_sequencial_central_v1` explicam parte do extrato futuro e seleção operacional, mas as divergências principais estão em:

```text
extrato_passado
lotes ativos/exauridos
valoração histórica
imposto histórico
idade útil histórica
```

Essas camadas são anteriores à decisão futura e dependem principalmente de replay, calendário, CDI, IOF/IR e atributos internos dos lotes após replay.

## Decisão da ME-RUNTIME-CANON-09

```text
STATUS: DIVERGENCIAS_COMPAT_CLASSIFICADAS
PROMOVER_CONTEXTOSAIDACANONICACOMPAT: false
SUBSTITUIR_CONTEXTBASELINE: false
ALTERAR_APLICACAO_PRINCIPAL: false
ALTERAR_SAIDA_CANONICA_OFICIAL: false
ALTERAR_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
```

## Próxima ação segura

A próxima microetapa deve ser diagnóstica e mais granular:

```text
ME-RUNTIME-CANON-10 — comparar componentes internos de ContextoBaseline vs ContextoOperacionalCanonico antes da saída
```

A comparação deve cobrir, no mínimo:

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

Critério de parada:

```text
Não corrigir saída canônica antes de identificar qual componente interno diverge primeiro.
```

## Validação esperada

Como esta ME-RUNTIME-CANON-09 é documental, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

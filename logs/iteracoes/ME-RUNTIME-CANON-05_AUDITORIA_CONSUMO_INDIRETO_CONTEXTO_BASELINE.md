# ME-RUNTIME-CANON-05 — Auditoria do consumo indireto de ContextoBaseline

## Objetivo

Auditar o consumo indireto dos campos exclusivos de `ContextoBaseline` em `nucleo/saida_canonica.py` e `nucleo/saida_observavel.py`, ainda sem substituir o contexto runtime.

Esta microetapa é exclusivamente diagnóstica/documental. Não altera `aplicacao/*`, `nucleo/*`, motor, replay, ledger, ranking, saída canônica, console, XLSX ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: f909df5450c94e05a17effeb18b936f1b11450b6
ULTIMO_MERGE: PR #374 — ME-RUNTIME-CANON-04 centraliza identidade baseline da S7B
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

## Auditoria pós-merge da ME-RUNTIME-CANON-04

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: f9ea34b -> f909df5
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

## Campos exclusivos de ContextoBaseline herdados da ME-RUNTIME-CANON-02

```text
decisao_local_v1
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
recomputacao_sequencial_central_v1
triagem_motor
```

## Auditoria de `nucleo/saida_canonica.py`

### Consumo direto/indireto observado

`saida_canonica.py` consome o objeto `contexto` de forma ampla. O consumo inclui campos comuns entre `ContextoBaseline` e `ContextoOperacionalCanonico`:

```text
pacote_config
execucao
calendario_financeiro
cache_cdi
carteira_canonica
dados_operacionais
fontes_elegiveis_pagamento
ranking_carteira
replay_passado
tabela_iof
faixas_ir
saldo_disponivel_geral
```

Também há consumo de campos exclusivos ou transicionais de `ContextoBaseline`:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

### Pontos críticos

1. `_quadro_futuro_preferencial(contexto)` depende de `contexto.decisao_local_v1` e de `quadro_decisao_local_v1`. Esse é o ponto de entrada preferencial para o extrato futuro.

2. `_pagamentos_decisao_recebido_disponivel_fallback_auditavel(contexto)` também consulta `decisao_local_v1` para restringir fallback auditável de `recebido_disponivel` apenas aos pagamentos cuja decisão já escolheu esse tipo de fonte.

3. `_mapa_pagamentos_central(contexto)` consome `contexto.recomputacao_sequencial_central_v1.quadro_recomputacao_sequencial_central`, usado como apoio para resumo futuro, ledger temporal e campos observáveis.

4. `_construir_extrato_futuro(contexto)` combina quadro futuro preferencial, fontes elegíveis, recomputação central e ledger temporal. Esse bloco torna a substituição direta por `ContextoOperacionalCanonico` insegura sem adaptador.

5. `_construir_lotes_situacao(contexto)` usa `replay_passado`, `execucao`, `calendario_financeiro`, `pacote_config`, `cache_cdi`, `tabela_iof` e `faixas_ir`; estes campos existem em `ContextoOperacionalCanonico`, mas a saída observável depende da compatibilidade semântica desses objetos, não apenas da presença nominal.

### Classificação

```text
RISCO_SUBSTITUICAO_CONTEXT_BASELINE_EM_saida_canonica.py: alto
CAMPOS_EXCLUSIVOS_CONSUMIDOS: decisao_local_v1; recomputacao_sequencial_central_v1
CAMPOS_EXCLUSIVOS_NAO_OBSERVADOS_COMO_CONSUMIDOS_DIRETAMENTE: auditoria_temporal_decisao_local; reescolha_dinamica_pos_quebra; heuristica_conjunta_parcial_bloco_critico; planejamento_conjunto_local_bloco_critico_v1; microplanejamento_conjunto_bloco_critico_v2; triagem_motor
DECISAO: não substituir contexto sem adaptador compatível
```

## Auditoria de `nucleo/saida_observavel.py`

### Consumo observado

`saida_observavel.py` é majoritariamente dependente de:

```text
saida
pacote_saida_observavel_temporal
contexto.calendario_financeiro
contexto.cache_cdi
```

O módulo exige explicitamente `pacote_saida_observavel_temporal` em vários blocos por meio de `_exigir_pacote_saida_observavel_temporal(...)`.

As funções de renderização usam `contexto` principalmente para:

```text
calcular dias de lote com calendario_financeiro
acessar série CDI via cache_cdi
renderizar lotes consolidados, origens migradas e blocos de situação atual
```

Não foi observado consumo direto dos oito campos exclusivos de `ContextoBaseline` neste módulo durante esta auditoria.

### Classificação

```text
RISCO_SUBSTITUICAO_CONTEXT_BASELINE_EM_saida_observavel.py: médio
MOTIVO: dependência menor de contexto, mas forte dependência de pacote_saida_observavel_temporal e da semântica de saida
CAMPOS_EXCLUSIVOS_CONSUMIDOS_DIRETAMENTE: nenhum observado
DECISAO: não tratar isoladamente; depende da estabilização de saida_canonica.py
```

## Resultado da auditoria

| Módulo | Consome campos exclusivos? | Campo exclusivo crítico | Pode migrar agora? |
|---|---:|---|---:|
| `nucleo/saida_canonica.py` | sim | `decisao_local_v1`, `recomputacao_sequencial_central_v1` | não |
| `nucleo/saida_observavel.py` | não observado diretamente | nenhum direto observado | não isoladamente |

## Decisão

```text
STATUS: CONSUMO_INDIRETO_CONTEXT_BASELINE_AUDITADO
TROCAR_CONTEXT_BASELINE_AGORA: false
CRIAR_ADAPTADOR_AGORA: false
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
```

## Sequência segura revisada

1. `ME-RUNTIME-CANON-06` — desenhar adaptador documental para prover, a partir de `ContextoOperacionalCanonico`, os campos transicionais ainda exigidos por `saida_canonica.py`, sem ativar no runtime.
2. `ME-RUNTIME-CANON-07` — implementar adaptador compatível em modo não usado pela rota principal, com teste de construção isolada.
3. `ME-RUNTIME-CANON-08` — comparar saída gerada por `ContextoBaseline` versus adaptador canônico em shadow documental/local, sem promover automaticamente.
4. `ME-RUNTIME-CANON-09` — só depois avaliar substituição controlada de `carregar_contexto_baseline()`.

## Próxima ação recomendada

A próxima microetapa segura é:

```text
ME-RUNTIME-CANON-06 — desenho do adaptador canônico compatível para saída canônica
```

Essa etapa deve continuar diagnóstica/documental, sem alteração de runtime.

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

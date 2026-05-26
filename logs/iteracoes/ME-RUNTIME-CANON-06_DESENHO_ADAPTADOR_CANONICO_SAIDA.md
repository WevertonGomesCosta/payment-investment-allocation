# ME-RUNTIME-CANON-06 — Desenho documental do adaptador canônico compatível para saída

## Objetivo

Desenhar documentalmente um adaptador canônico compatível para permitir, em microetapa futura, que a saída canônica seja construída a partir de `ContextoOperacionalCanonico` sem substituir imediatamente `ContextoBaseline` na rota principal.

Esta microetapa não implementa adaptador, não ativa runtime alternativo, não altera `aplicacao/*`, não altera `nucleo/*`, não cria script diagnóstico e não muda regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 21668a130990473cbe11b912ee9e5b34ee0e6f0c
ULTIMO_MERGE: PR #375 — ME-RUNTIME-CANON-05 audita consumo indireto do ContextoBaseline
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

## Auditoria pós-merge da ME-RUNTIME-CANON-05

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: f909df5 -> 21668a1
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

## Problema que o adaptador deve resolver

A ME-RUNTIME-CANON-05 confirmou que `nucleo/saida_canonica.py` ainda consome diretamente ou indiretamente campos transicionais de `ContextoBaseline`, principalmente:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

Esses campos não pertencem ao núcleo limpo de `ContextoOperacionalCanonico`, mas ainda alimentam a construção do extrato futuro, fallback auditável de recebido disponível e mapa central de pagamentos.

Portanto, a substituição direta de:

```text
carregar_contexto_baseline()
```

por:

```text
carregar_contexto_operacional_canonico()
```

permanece proibida nesta fase.

## Princípio do adaptador

O adaptador futuro deve ser uma camada explícita, transitória e auditável entre:

```text
ContextoOperacionalCanonico
```

e os consumidores legados ainda dependentes da forma de `ContextoBaseline`.

Ele deve produzir um objeto compatível apenas para a construção de saída canônica, sem se tornar nova fonte normativa e sem preservar indefinidamente dívidas históricas.

Nome documental recomendado:

```text
ContextoSaidaCanonicaCompat
```

Função documental recomendada:

```text
construir_contexto_saida_canonica_compat(contexto_operacional_canonico, componentes_transicionais)
```

## Contrato mínimo do adaptador

### Campos provenientes diretamente de `ContextoOperacionalCanonico`

O adaptador deve repassar sem transformação econômica:

```text
pacote_config
execucao
calendario_financeiro
pacote_planilha
validacao_pre_execucao
carteira_canonica
dados_operacionais
recebidos_auditaveis
fontes_elegiveis_pagamento
saldo_disponivel_geral
cache_cdi
pacote_entrada_resolvida
auditoria_pacote_entrada_resolvida
ranking_carteira
nucleo_financeiro
replay_passado
tabela_iof
faixas_ir
```

### Campos transicionais exigidos por `saida_canonica.py`

O adaptador deve receber explicitamente, ou reconstruir por uma rota futura formalizada, os campos:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

Esses campos devem ser classificados como:

```text
TRANSICIONAL_COMPATIBILIDADE_SAIDA
```

Não devem ser adicionados a `ContextoOperacionalCanonico` sem nova justificativa contratual.

### Campos exclusivos de `ContextoBaseline` sem consumo direto observado na ME-RUNTIME-CANON-05

Os campos abaixo não devem entrar automaticamente no adaptador:

```text
auditoria_temporal_decisao_local
reescolha_dinamica_pos_quebra
heuristica_conjunta_parcial_bloco_critico
planejamento_conjunto_local_bloco_critico_v1
microplanejamento_conjunto_bloco_critico_v2
triagem_motor
```

Só podem ser incluídos se uma microetapa posterior comprovar consumo real pela saída canônica, console ou XLSX.

## Regras de segurança

1. O adaptador não pode alterar dados financeiros, planilha, CDI, replay, ledger, ranking ou decisão econômica.
2. O adaptador não pode chamar download, I/O de planilha ou scripts diagnósticos.
3. O adaptador não pode criar fallback econômico novo.
4. O adaptador não pode substituir `ContextoBaseline` na rota principal sem comparação observável aprovada.
5. O adaptador não pode ser promovido a norma superior ao contrato operacional ou ao modelo oficial.
6. O adaptador deve ser removível após a canonização completa da rota runtime.

## Sequência futura segura

### ME-RUNTIME-CANON-07 — implementação isolada do adaptador

Permitido futuramente:

```text
criar módulo em nucleo/* com adaptador compatível
não usar no runtime principal
não alterar aplicacao/principal.py
não substituir carregar_contexto_baseline()
```

Validação mínima esperada:

```text
py_compile
instanciação isolada do adaptador
checagem de presença dos campos requeridos
sem geração alternativa de XLSX oficial
```

### ME-RUNTIME-CANON-08 — comparação observável controlada

Permitido futuramente:

```text
comparar saída construída com ContextoBaseline vs adaptador canônico compatível
registrar diferenças de campos, totais e tabelas observáveis
não promover automaticamente
```

A comparação deve cobrir, no mínimo:

```text
Patrimônio líquido atual
Rendimento líquido atual
Rendimento líquido reconciliado contra recebidos
ranking top 1
quantidade de switchings reais
lotes ativos e exauridos
extrato passado
extrato futuro
Situação Atual
```

### ME-RUNTIME-CANON-09 — decisão de substituição

Só pode ocorrer se ME-RUNTIME-CANON-08 comprovar equivalência observável ou divergências justificadas e aprovadas.

## Decisão da ME-RUNTIME-CANON-06

```text
STATUS: DESENHO_ADAPTADOR_CANONICO_COMPATIVEL_REGISTRADO
IMPLEMENTA_ADAPTADOR: false
ATIVA_RUNTIME_ALTERNATIVO: false
TROCA_CONTEXT_BASELINE: false
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: ME-RUNTIME-CANON-07_IMPLEMENTACAO_ISOLADA_ADAPTADOR_CANONICO_COMPATIVEL
```

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

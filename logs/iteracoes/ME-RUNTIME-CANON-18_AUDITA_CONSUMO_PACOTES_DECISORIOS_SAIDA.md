# ME-RUNTIME-CANON-18 — Auditoria de consumo dos pacotes decisórios residuais pela saída canônica

## Objetivo

Auditar, de forma diagnóstica/documental, onde a saída canônica e seus comparadores consomem os pacotes decisórios residuais classificados pela ME-RUNTIME-CANON-17:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

Esta microetapa não altera saída canônica, motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: f6714b4783088308de62be30fca88788e277f85e
ULTIMO_MERGE: PR #387 — ME-RUNTIME-CANON-17 classifica pacotes decisórios residuais
```

## Auditoria pós-merge da ME-RUNTIME-CANON-17

Validação local informada pelo usuário:

```text
git checkout main: tentativa com typo inicial `it checkout main`, sem efeito operacional
git pull --ff-only: 0b62a8e -> f6714b4
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-18.
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

## Resultado da auditoria de consumo

### 1. Consumo de `decisao_local_v1` em `saida_canonica.py`

A saída canônica consome `decisao_local_v1` diretamente para montar o quadro futuro preferencial:

```text
_quadro_futuro_preferencial(contexto):
    decisao = getattr(contexto, 'decisao_local_v1', None)
    quadro = getattr(decisao, 'quadro_decisao_local_v1', None)
```

Esse quadro é consumido por `_construir_extrato_futuro(contexto)`. Quando ausente, a função retorna lista vazia.

Classificação:

```text
CONSUMO: direto
CAMADA: extrato_futuro
TIPO: dependência observável da saída futura
CANONIZAÇÃO IMEDIATA: não recomendada sem adaptação explícita
```

### 2. Consumo de `decisao_local_v1` como contenção auditável de fallback

A função `_pagamentos_decisao_recebido_disponivel_fallback_auditavel(contexto)` também consome `decisao_local_v1` para restringir o fallback auditável de `recebido_disponivel` aos pagamentos cuja decisão já escolheu esse tipo de fonte.

Classificação:

```text
CONSUMO: direto
CAMADA: fallback auditável de fonte recebida
TIPO: trava de coerência/evita reclassificação indevida na saída
CANONIZAÇÃO IMEDIATA: não remover sem substituto equivalente
```

### 3. Consumo de `recomputacao_sequencial_central_v1` em `saida_canonica.py`

A saída canônica consome `recomputacao_sequencial_central_v1` para montar `mapa_central`:

```text
_mapa_pagamentos_central(contexto):
    pacote = getattr(contexto, 'recomputacao_sequencial_central_v1', None)
    quadro = getattr(pacote, 'quadro_recomputacao_sequencial_central', None)
```

Esse mapa é passado ao `ledger_temporal_conjunto` e também usado como fonte complementar em `_resumo_futuro(...)` e em múltiplos campos observáveis do extrato futuro.

Classificação:

```text
CONSUMO: direto
CAMADA: extrato_futuro + ledger temporal conjunto
TIPO: componente de recomputação central usado pela saída futura
CANONIZAÇÃO IMEDIATA: não remover sem substituto equivalente
```

### 4. Consumo em `comparacao_saida_canonica_compat.py`

A comparação compatível constrói `ComponentesTransicionaisSaidaCanonica` a partir do `ContextoBaseline`:

```text
componentes = ComponentesTransicionaisSaidaCanonica(
    decisao_local_v1=getattr(contexto_baseline, 'decisao_local_v1'),
    recomputacao_sequencial_central_v1=getattr(contexto_baseline, 'recomputacao_sequencial_central_v1'),
)
```

Depois combina esses campos com `ContextoOperacionalCanonico` via `construir_contexto_saida_canonica_compat(...)` e executa `construir_saida_canonica_com_switching_v17_c7(...)` em memória.

Classificação:

```text
CONSUMO: transicional explícito
CAMADA: comparação observável controlada
TIPO: ponte compatível isolada
CANONIZAÇÃO IMEDIATA: já modelada como componente transicional, não canônico
```

## Diagnóstico consolidado

```text
SAIDA_CANONICA_CONSOME_DECISAO_LOCAL_V1: sim
SAIDA_CANONICA_CONSOME_RECOMPUTACAO_SEQUENCIAL_CENTRAL_V1: sim
CONSUMO_EH_ECONOMICO_PRIMARIO: não
CONSUMO_EH_OBSERVAVEL/TRANSICIONAL: sim
CONTEXTOPERACIONALCANONICO_DEVE_RECEBER_CAMPOS_AGORA: não
CONTEXTOSAIDACANONICACOMPAT_DEVE_CONTINUAR_ISOLADO: sim
```

## Decisão operacional

Os dois pacotes residuais são necessários para a rota de saída atual, mas a dependência é de camada observável/transicional, não de cache, replay ou materialização econômica primária.

Portanto, a rota segura é:

```text
1. não adicionar decisao_local_v1 e recomputacao_sequencial_central_v1 diretamente ao ContextoOperacionalCanonico nesta etapa;
2. manter ContextoSaidaCanonicaCompat como adaptador isolado;
3. criar próxima microetapa para provar se a saída observável via adaptador compatível é equivalente à saída baseline agora que cache/replay/fontes/saldo estão equivalentes;
4. só depois decidir se esses pacotes devem ser encapsulados, substituídos por componentes canônicos derivados ou mantidos como transicionais.
```

## Próxima microetapa recomendada

```text
ME-RUNTIME-CANON-19 — reexecuta comparação observável controlada pós-equivalência interna
```

Objetivo futuro:

```text
Reexecutar a comparação observável entre ContextoBaseline e ContextoSaidaCanonicaCompat depois de cache_cdi, calendário, replay, lotes, fontes e saldo terem ficado equivalentes, verificando se os dois componentes transicionais preservam a saída observável sem promover a rota compatível.
```

## O que esta microetapa não faz

```text
não altera saida_canonica.py
não altera construir_saida_canonica_v17_c7.py
não altera comparacao_saida_canonica_compat.py
não altera contexto_saida_canonica_compat.py
não altera ContextoOperacionalCanonico
não altera ContextoBaseline
não corrige replay
não altera motor
não altera regra econômica
não gera XLSX oficial alternativo
não commita dados/cache_bcb.json
```

## Validação esperada

Como esta microetapa cria apenas este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

## Decisão

```text
STATUS: CONSUMO_PACOTES_DECISORIOS_RESIDUAIS_AUDITADO
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

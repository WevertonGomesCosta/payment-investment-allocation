# ME-RUNTIME-CANON-17 — Classificação funcional dos pacotes decisórios residuais

## Objetivo

Classificar funcionalmente as duas divergências residuais detectadas pela ME-RUNTIME-CANON-16 entre `ContextoBaseline` e `ContextoOperacionalCanonico`:

```text
decisao_local_v1
recomputacao_sequencial_central_v1
```

Esta microetapa é diagnóstica/documental. Não corrige replay, saída canônica, motor, ranking, pagamentos, switching, ledger, console, XLSX oficial ou regra econômica.

## Baseline de entrada

```text
BASELINE: main
HEAD: 0b62a8e8712c95659943b91d0b99ba25171db425
ULTIMO_MERGE: PR #386 — ME-RUNTIME-CANON-16 reexecuta comparação interna completa
```

## Auditoria pós-merge da ME-RUNTIME-CANON-16

Validação local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: 503097e -> 0b62a8e
git status --short: M dados/cache_bcb.json
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Observação operacional:

```text
dados/cache_bcb.json permanece modificado localmente pela atualização BCB/cache.
Essa modificação não pertence à ME-RUNTIME-CANON-17.
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

## Evidência da ME-RUNTIME-CANON-16

A comparação interna completa retornou:

```text
ok=False
divergencias=2
```

Componentes equivalentes:

```text
cache_cdi.serie_cdi: igual=True
calendario_financeiro: igual=True
replay_passado.log_passado: igual=True
replay_passado.lotes_apos_replay: igual=True
fontes_elegiveis_pagamento: igual=True
saldo_disponivel_geral: igual=True
```

Divergências residuais:

```text
decisao_local_v1: igual=False | tipo_base=PacoteDecisaoLocalV1 | tipo_can=None
recomputacao_sequencial_central_v1: igual=False | tipo_base=PacoteRecomputacaoSequencialCentralV1 | tipo_can=None
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

A ME-RUNTIME-CANON-17 não altera motor, replay, ledger, ranking, pagamentos, switching, console, XLSX oficial ou regra econômica.

## Origem dos pacotes residuais

### `decisao_local_v1`

No `ContextoBaseline`, `decisao_local_v1` é materializado por:

```text
materializar_decisao_local_v1(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    data_referencia=contexto_execucao.data_referencia,
    carteira_canonica=carteira_canonica,
)
```

A função é chamada somente depois de materializar:

```text
dados_operacionais
fontes_elegiveis_pagamento
saldo_disponivel_geral
```

Na comparação da ME-16, esses três insumos já estavam equivalentes entre os contextos.

Classificação:

```text
TIPO: pacote decisório derivado/transicional
CAMADA: pós-fontes_elegiveis_pagamento e pós-saldo_disponivel_geral
PERTENCE_AO_CONTEXTOPERACIONALCANONICO_ATUAL: false
CAUSA_DE_DIVERGENCIA_ECONOMICA_PRIMARIA: false
```

### `recomputacao_sequencial_central_v1`

No `ContextoBaseline`, `recomputacao_sequencial_central_v1` é materializado por:

```text
carregar_recomputacao_sequencial_central_v1(
    dados_operacionais,
    fontes_elegiveis_pagamento,
    saldo_disponivel_geral,
    decisao_local_v1,
    replay_passado,
    data_referencia=contexto_execucao.data_referencia,
    tabela_iof=construir_tabela_iof(...),
    faixas_ir=construir_faixas_ir(...),
    carteira_canonica=carteira_canonica,
    proxy_version='v3',
    calendario_financeiro=calendario_financeiro,
    serie_cdi=cache_cdi.serie_cdi,
)
```

Na comparação da ME-16, todos os insumos estruturais e econômicos de base já estavam equivalentes:

```text
cache_cdi.serie_cdi
calendario_financeiro
replay_passado.log_passado
replay_passado.lotes_apos_replay
fontes_elegiveis_pagamento
saldo_disponivel_geral
```

Classificação:

```text
TIPO: pacote de recomputação decisória/transicional
CAMADA: posterior a decisao_local_v1 e replay_passado
PERTENCE_AO_CONTEXTOPERACIONALCANONICO_ATUAL: false
CAUSA_DE_DIVERGENCIA_ECONOMICA_PRIMARIA: false
```

## Consumidores e adaptadores

A rota compatível isolada já reconhece esses dois campos como componentes transicionais:

```text
ComponentesTransicionaisSaidaCanonica:
  decisao_local_v1
  recomputacao_sequencial_central_v1
```

O `ContextoSaidaCanonicaCompat` combina os campos canônicos de `ContextoOperacionalCanonico` com esses dois componentes explicitamente fornecidos de fora.

Interpretação:

```text
A arquitetura já separou os campos canônicos dos componentes transicionais.
Esses pacotes não devem ser inseridos automaticamente no ContextoOperacionalCanonico sem decisão normativa adicional.
```

## Decisão funcional

```text
STATUS: PACOTES_DECISORIOS_RESIDUAIS_CLASSIFICADOS
DECISAO_LOCAL_V1: componente decisório derivado/transicional, posterior a fontes_elegiveis_pagamento e saldo_disponivel_geral
RECOMPUTACAO_SEQUENCIAL_CENTRAL_V1: componente de recomputação decisória/transicional, posterior a decisao_local_v1 e replay_passado
CAUSA_ECONOMICA_PRIMARIA_RESIDUAL: não
CACHE_EQUIVALENTE: sim
REPLAY_EQUIVALENTE: sim
FONTES_EQUIVALENTES: sim
SALDO_EQUIVALENTE: sim
```

## Rota segura de canonização

A rota segura não é promover diretamente `ContextoSaidaCanonicaCompat` nem adicionar esses campos ao `ContextoOperacionalCanonico` sem prova de necessidade.

Sequência recomendada:

```text
1. Auditar se a saída canônica oficial ainda consome diretamente decisao_local_v1 e/ou recomputacao_sequencial_central_v1.
2. Se consumir, identificar campos observáveis derivados desses pacotes.
3. Verificar se esses campos podem ser supridos por fontes já canônicas equivalentes.
4. Se não puderem, criar adaptador transicional explícito fora do ContextoOperacionalCanonico.
5. Só depois reexecutar comparação observável completa.
```

## Próxima microetapa recomendada

```text
ME-RUNTIME-CANON-18 — auditoria de consumo dos pacotes decisórios residuais pela saída canônica
```

Objetivo futuro:

```text
Identificar exatamente onde saida_canonica.py, construir_saida_canonica_v17_c7.py, comparacao_saida_canonica_compat.py e adaptadores relacionados consomem decisao_local_v1 e recomputacao_sequencial_central_v1, sem alterar saída, motor, replay ou regra econômica.
```

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

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

## Decisão

```text
STATUS: CLASSIFICACAO_FUNCIONAL_RESIDUAL_REGISTRADA
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

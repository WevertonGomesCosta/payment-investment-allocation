# ME-RUNTIME-CANON-01 — Auditoria da rota runtime ainda versionada

## Objetivo

Auditar a rota runtime ainda versionada após o fechamento do saneamento diagnóstico pela ME-POST-GOV-05.

A microetapa identifica onde `aplicacao/principal.py` e módulos vivos consomem:

```text
ContextoBaseline
nucleo/construir_saida_canonica_v17_c7.py
nucleo/matriz_elegibilidade_fontes_s7b.py
nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
```

Esta etapa é exclusivamente diagnóstica. Não altera runtime, motor, regra econômica, saída canônica, console, XLSX, `aplicacao/*` ou `nucleo/*`.

## Baseline de entrada

```text
BASELINE: main
HEAD: 9f86546fb46e8d6f93bc974c37909d524b451ac3
ULTIMO_MERGE: PR #370 — ME-POST-GOV-05 fechamento do saneamento diagnóstico
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

## Rotas de consumo identificadas

### 1. `aplicacao/principal.py`

`aplicacao/principal.py` é o ponto de entrada runtime e importa diretamente os quatro componentes de interesse:

```python
from nucleo.contexto_baseline import carregar_contexto_baseline
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.matriz_elegibilidade_fontes_s7b import construir_matriz_elegibilidade_fontes_s7b
from nucleo.integracao_matriz_elegibilidade_pagamentos_s7c import aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c
```

A função `carregar_contexto_e_saida()` executa a sequência:

```text
carregar_contexto_baseline()
construir_saida_canonica_com_switching_v17_c7(contexto_baseline, versao=VERSAO_BASELINE)
construir_matriz_elegibilidade_fontes_s7b(contexto_baseline, data_referencia=saida_canonica.data_referencia)
aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(saida_canonica, matriz)
render_console(contexto_baseline, saida_canonica)
gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

Classificação:

```text
TIPO: consumidor direto da rota versionada
RISCO_RENOMEACAO: alto
RISCO_FUNCIONAL: alto se alterar em lote
ORDEM_SEGURA: não alterar em ME-RUNTIME-CANON-01
```

### 2. `nucleo/contexto_baseline.py`

O arquivo ainda mantém dois artefatos de contexto:

```text
ContextoBaseline
ContextoOperacionalCanonico
```

`ContextoOperacionalCanonico` já é mais limpo e foi criado na frente V4Z, mas o runtime ainda consome `carregar_contexto_baseline()`.

O `ContextoBaseline` agrega campos além do núcleo canônico mínimo, incluindo:

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

Classificação:

```text
TIPO: contexto runtime transicional
RISCO_RENOMEACAO: muito alto
RISCO_FUNCIONAL: muito alto
ACOPLAMENTO: console + XLSX + saída canônica + matriz S7B/S7C
DECISAO: substituir apenas após prova de equivalência dos campos consumidos
```

### 3. `nucleo/construir_saida_canonica_v17_c7.py`

O módulo é pequeno, mas é consumido diretamente pelo runtime:

```text
construir_saida_canonica_com_switching_v17_c7(contexto, versao)
```

Ele chama:

```text
nucleo.saida_canonica.construir_saida_canonica
nucleo.saida_canonica_switching_v17_c7.integrar_switchings_materializados_saida_canonica_v17_f0_p1
```

Classificação:

```text
TIPO: wrapper versionado de saída canônica com switching materializado
RISCO_RENOMEACAO: médio
RISCO_FUNCIONAL: médio-alto
ACOPLAMENTO: saída canônica + switching materializado + principal.py + S7B
DECISAO: canonizar antes de alterar S7B/S7C, mas com teste de equivalência textual/XLSX
```

### 4. `nucleo/matriz_elegibilidade_fontes_s7b.py`

O módulo é versionado e contém acoplamento relevante:

```python
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
```

Mesmo quando `aplicacao/principal.py` já construiu `saida_canonica`, `construir_matriz_elegibilidade_fontes_s7b()` reconstrói internamente a saída:

```text
saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
```

Além disso, contém `VERSAO_BASELINE = "V225"` local, o que cria risco de divergência com `nucleo.identidade_baseline.VERSAO_BASELINE`.

Classificação:

```text
TIPO: módulo versionado de matriz de elegibilidade
RISCO_RENOMEACAO: alto
RISCO_FUNCIONAL: alto
ACOPLAMENTO: reconstrói saída canônica + depende de classe S6 + injeta elegibilidade em pagamentos via S7C
RISCO_PRINCIPAL: dupla construção da saída canônica e baseline hardcoded local
DECISAO: antes de canonizar nome, eliminar reconstrução interna ou aceitar saída já construída como entrada explícita
```

### 5. `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py`

O módulo aplica a matriz ao `saida_canonica.extrato_futuro`, alterando campos observáveis em pagamentos futuros:

```text
Lote sugerido
lote_sugerido_original
componentes_fonte
componentes_bloqueados_ou_ausentes
fonte_normativa_s7c
acao_s7c
elegivel_matriz
pode_ser_lote_sugerido_matriz
motivo_bloqueio_matriz
lote_sugerido_pos_matriz
```

Também aplica bloqueio quando o ledger indica:

```text
sem_saldo_temporal_auditavel
saldo_temporal_insuficiente_cumulativo
```

Classificação:

```text
TIPO: integrador versionado que altera saída observável
RISCO_RENOMEACAO: médio
RISCO_FUNCIONAL: alto se separado da S7B
ACOPLAMENTO: depende semanticamente da matriz S7B e altera extrato_futuro in-place
DECISAO: não canonizar isoladamente; tratar junto ou depois de S7B
```

## Dependências e acoplamentos consolidados

| Componente | Consumidor direto | Entrada principal | Saída/efeito | Risco | Decisão |
|---|---|---|---|---|---|
| `ContextoBaseline` | `aplicacao/principal.py` | config, planilha, CDI, replay, ranking, heurísticas | contexto usado por console, saída e XLSX | muito alto | prova de equivalência antes de substituir |
| `construir_saida_canonica_v17_c7.py` | `aplicacao/principal.py`, S7B | contexto baseline | `PacoteSaidaCanonica` com switching | médio-alto | canonizar wrapper depois de teste de equivalência |
| `matriz_elegibilidade_fontes_s7b.py` | `aplicacao/principal.py` | contexto + data referência + S6 opcional | `DataFrame` de elegibilidade | alto | refatorar assinatura antes de canonizar |
| `integracao_matriz_elegibilidade_pagamentos_s7c.py` | `aplicacao/principal.py` | saída canônica + matriz | mutação de `extrato_futuro` + auditoria | alto | tratar junto da S7B |

## Riscos de canonização

### Risco 1 — migração direta para `ContextoOperacionalCanonico`

O `ContextoOperacionalCanonico` não contém todos os campos do `ContextoBaseline`, especialmente campos heurísticos e intermediários usados indiretamente por console, XLSX ou saída. A troca direta de `carregar_contexto_baseline()` por `carregar_contexto_operacional_canonico()` é arriscada.

Decisão:

```text
NÃO_MIGRAR_CONTEXTO_NO_PRIMEIRO_PASSO
```

### Risco 2 — S7B reconstrói saída canônica

A S7B reconstrói internamente a saída canônica, mesmo após `principal.py` já ter construído a saída. Isso cria acoplamento circular e risco de divergência entre a saída usada na matriz e a saída posteriormente modificada por S7C.

Decisão:

```text
PRIMEIRA_CORRECAO_FUNCIONAL_PROVAVEL: permitir que S7B receba saida_canonica_preconstruida
```

### Risco 3 — `VERSAO_BASELINE = "V225"` local na S7B

A S7B define versão local fixa. Isso é aceitável como estado atual, mas é dívida de canonização porque pode divergir de `nucleo.identidade_baseline.VERSAO_BASELINE`.

Decisão:

```text
REMOVER_HARDCODED_VERSION_EM_MICROETAPA_PROPRIA
```

### Risco 4 — S7C altera `extrato_futuro` in-place

A S7C modifica objetos do `saida_canonica.extrato_futuro`, o que torna a ordem de aplicação relevante para console e XLSX.

Decisão:

```text
NÃO_REORDENAR_S7C_SEM_TESTE_OBSERVAVEL
```

## Ordem segura de canonização

1. `ME-RUNTIME-CANON-02` — Prova de equivalência e inventário de campos consumidos de `ContextoBaseline` por console, XLSX, saída e matriz. Não migrar contexto ainda.
2. `ME-RUNTIME-CANON-03` — Corrigir S7B para receber opcionalmente `saida_canonica_preconstruida`, evitando dupla construção, sem alterar saída observável.
3. `ME-RUNTIME-CANON-04` — Remover `VERSAO_BASELINE = "V225"` local da S7B e usar `nucleo.identidade_baseline.VERSAO_BASELINE` ou argumento explícito.
4. `ME-RUNTIME-CANON-05` — Canonizar wrapper `construir_saida_canonica_v17_c7.py` com nome estável, mantendo alias temporário apenas se necessário e com remoção planejada.
5. `ME-RUNTIME-CANON-06` — Canonizar S7B/S7C como rota estável de elegibilidade de fontes, depois de eliminar hardcoded version e dupla construção.
6. `ME-RUNTIME-CANON-07` — Avaliar troca de `ContextoBaseline` por `ContextoOperacionalCanonico` ou por adaptador canônico compatível.

## Decisão da ME-RUNTIME-CANON-01

```text
STATUS: AUDITORIA_RUNTIME_VERSIONADO_REGISTRADA
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: ME-RUNTIME-CANON-02_PROVA_EQUIVALENCIA_CAMPOS_CONTEXTO_BASELINE
```

## Validação esperada

Como esta microetapa só cria este log, validar com:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

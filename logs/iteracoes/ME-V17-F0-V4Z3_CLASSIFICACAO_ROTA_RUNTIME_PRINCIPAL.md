# ME-V17-F0-V4Z3 — Classificação da rota runtime principal antes da Etapa 5

```text
MICROETAPA: ME-V17-F0-V4Z3
VERSAO_CANDIDATA: V17-F0-V.4Z3
TIPO: DOCUMENTAL / DIAGNOSTICO
CLASSE: CLASSIFICACAO_ROTA_RUNTIME_PRINCIPAL
BASELINE_DE_ENTRADA: V17-F0-V.4Z2
BASE_MAIN: edd501bc05e3e6f61cfb6a0363e14b6649964551
ESCOPO_ESTRITO:
  - aplicacao/principal.py
  - aplicacao/console/principal.py
  - nucleo/contexto_baseline.py
  - nucleo/construir_saida_canonica_v17_c7.py
  - nucleo/matriz_elegibilidade_fontes_s7b.py
  - nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
  - nucleo/gerar_planilha_operacional.py
ALTERA_RUNTIME: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ALTERA_RANKING: false
ALTERA_XLSX: false
ALTERA_CONTEXT_BASELINE: false
ALTERA_DADOS: false
```

## Objetivo

Classificar somente a rota runtime principal antes da Etapa 5, usando as evidências da V4Z2, sem alterar código operacional.

A V4Z3 não abre a Etapa 5. Ela separa as dependências da rota principal em quatro classes:

1. `CANONIZAR`
2. `SUBSTITUIR`
3. `ISOLAR`
4. `MANTER_PROVISORIAMENTE`

## Evidência de entrada

A V4Z2 inventariou 75 arquivos e 839 funções. A rota `aplicacao/principal.py` foi identificada como runtime principal e ainda chama:

```text
aplicacao.console.principal.render_console
nucleo.contexto_baseline.carregar_contexto_baseline
nucleo.construir_saida_canonica_v17_c7.construir_saida_canonica_com_switching_v17_c7
nucleo.matriz_elegibilidade_fontes_s7b.construir_matriz_elegibilidade_fontes_s7b
nucleo.integracao_matriz_elegibilidade_pagamentos_s7c.aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c
nucleo.gerar_planilha_operacional.main
```

A execução local de `python -B aplicacao/principal.py` foi aprovada e gerou `saidas/oficial/relatorio_operacional_v225.xlsx`, mas a rota ainda não está contratualmente limpa para Etapa 5.

## Classificação da rota runtime

| Componente | Papel atual | Classe | Decisão preliminar | Justificativa | Próxima ação segura |
|---|---|---:|---|---|---|
| `aplicacao/principal.py` | Entrypoint runtime | `MANTER_PROVISORIAMENTE` | Manter como runtime principal até substituição controlada | Executa sem traceback e gera XLSX, mas ainda orquestra módulos versionados e contexto transicional | Não alterar na V4Z3; abrir microetapa futura para trocar dependências uma por vez |
| `nucleo/contexto_baseline.py::carregar_contexto_baseline()` | Contexto histórico/transicional usado pelo runtime | `SUBSTITUIR` | Substituir gradualmente por `carregar_contexto_operacional_canonico()` ou por pacote runtime canônico derivado | `ContextoBaseline` ainda contém shadows, benchmarks e campos transicionais; V4Z1 criou contexto limpo mas ele ainda não é usado no runtime | Não trocar agora; criar prova de equivalência antes de migrar `principal.py` |
| `nucleo/construir_saida_canonica_v17_c7.py` | Construção de saída canônica com switching usada pelo runtime | `CANONIZAR` | Promover para nome estável ou substituir por `nucleo/saida_canonica.py` se funcionalmente equivalente | Módulo versionado diretamente consumido pela rota principal | Fazer auditoria comparativa antes de renomear/substituir |
| `nucleo/matriz_elegibilidade_fontes_s7b.py` | Matriz de elegibilidade usada pelo runtime | `SUBSTITUIR` | Remover dependência de CSV/scripts diagnósticos ou rebaixar a diagnóstico | Módulo versionado e com dependência diagnóstica; não deve ser fonte normativa operacional | Mapear entradas reais e produzir fonte canônica sem `saidas/diagnostico/*` |
| `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py` | Integra a matriz S7B ao fluxo de pagamentos | `CANONIZAR` | Promover para nome estável apenas se a matriz S7B for saneada | Módulo versionado diretamente consumido pelo runtime | Tratar junto da S7B; não promover isoladamente |
| `aplicacao/console/principal.py` | Renderização observável no console | `MANTER_PROVISORIAMENTE` | Manter como camada observável enquanto runtime principal continuar validado | Tem resíduos textuais de auditoria/benchmark/shadow, mas é camada de apresentação; não é motor econômico | Separar renderização operacional de seções diagnósticas em etapa futura |
| `nucleo/gerar_planilha_operacional.py` | Geração XLSX oficial | `MANTER_PROVISORIAMENTE` | Manter como saída oficial enquanto `relatorio_operacional_v225.xlsx` for gerado sem erro | Possui termos diagnósticos/shadow/fallback; mas é saída, não decisão econômica | Auditar abas e insumos antes de qualquer refatoração |

## Dependências bloqueantes para Etapa 5

A Etapa 5 permanece bloqueada enquanto a rota runtime principal depender diretamente de:

```text
carregar_contexto_baseline()
construir_saida_canonica_v17_c7.py
matriz_elegibilidade_fontes_s7b.py
integracao_matriz_elegibilidade_pagamentos_s7c.py
```

Essas dependências não precisam ser removidas todas de uma vez. A próxima fase deve promover uma microcorreção por vez, com equivalência observável e execução local de `principal.py` após cada alteração.

## Ordem recomendada de saneamento após V4Z3

1. **V4Z4 — Prova de equivalência do contexto:** comparar `ContextoBaseline` versus `ContextoOperacionalCanonico` para os campos realmente usados pela rota principal, sem migrar runtime.
2. **V4Z5 — Auditoria da saída canônica versionada:** comparar `construir_saida_canonica_v17_c7.py` com `saida_canonica.py` e decidir promoção/substituição.
3. **V4Z6 — Saneamento da matriz S7B/S7C:** remover dependência de CSV diagnóstico ou rebaixar S7B/S7C para diagnóstico fora do runtime.
4. **V4Z7 — Separação console/XLSX:** separar renderização operacional de blocos diagnósticos residuais.
5. **V4Z8 — Gate final pré-Etapa 5:** rodar `principal.py`, auditoria V4Z2 e checar ausência de resíduos bloqueantes na rota runtime.

## Decisão

```text
STATUS: ETAPA_5_BLOQUEADA
V4Z3: CLASSIFICACAO_DOCUMENTAL_APTA
PROXIMA ACAO: V4Z4_PROVA_EQUIVALENCIA_CONTEXTO_SEM_MIGRAR_RUNTIME
```

## Validação esperada

Como a V4Z3 é documental e não altera código, validar com:

```bash
git diff --name-only main...HEAD
```

O diff deve conter apenas:

```text
logs/iteracoes/ME-V17-F0-V4Z3_CLASSIFICACAO_ROTA_RUNTIME_PRINCIPAL.md
```

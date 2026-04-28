# Relatório consolidado — validações históricas V091–V120

## Objetivo

Consolidar a faixa `V091_V120` das validações históricas, preservando validações de runner shadow, primeira quebra, observabilidade do console, recomputação sequencial, heurísticas do bloco crítico, motor de recomendação pagamentos/switching, release checker e integração temporal mínima, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações consolidadas nesta faixa: 24
- Faixa: V091–V120
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das validações

| Versão | Linhas | Título |
|---:|---:|---|
| V91 | 15 | Validação local V91 |
| V92 | 14 | Validação local V92 |
| V93 | 15 | Validação local V93 |
| V94 | 15 | Validação local V94 |
| V95 | 14 | Validação local V95 |
| V96 | 14 | Validação local V96 |
| V97 | 14 | Validação local V97 |
| V98 | 17 | Validação local V98 |
| V99 | 22 | Validação local V99 |
| V100 | 15 | Validação local V100 |
| V101 | 9 | Validação local V101 |
| V103 | 16 | VALIDAÇÃO LOCAL V103 |
| V104 | 14 | VALIDAÇÃO LOCAL V104 |
| V105 | 10 | Validação local V105 |
| V106 | 13 | Validação local V106 |
| V107 | 10 | Validação local V107 |
| V108 | 8 | Validação local V108 |
| V114 | 15 | Validação local V114 |
| V115 | 15 | Validação local V115 |
| V116 | 16 | Validação local V116 |
| V117 | 18 | Validação local V117 |
| V118 | 29 | Validação local V118 |
| V119 | 15 | Validação local V119 |
| V120 | 16 | Validação local V120 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Runner shadow | Benchmark, auditoria e primeira quebra do runner futuro shadow foram preservados. |
| Observabilidade | Amostras de pagamentos passados/futuros e console principal foram registradas. |
| Frente central | Recomputação sequencial, reescolha pós-quebra e heurísticas do bloco crítico foram consolidadas. |
| Motor por pagamento | Motor de recomendação pagamentos/switching foi validado e preservado. |
| Camada temporal | Compilação e integração mínima do planejador, alocador, simulador e avaliador foram registradas. |

## Detalhe por validação

### V91 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V91.md`

- Linhas originais: 15
- Título: Validação local V91

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V91
## Escopo validado
- compilação do repositório;
- geração da planilha operacional;
- execução do script principal;
- checagem mínima de release.
## Resultado
- baseline V91 compilando e executando;
- script principal gerando a saída operacional;
- `release checker` aprovado em estado limpo;
- rotina de download preparada para não manter o arquivo temporário bloqueado após a validação do `.xlsx`.
```

</details>

### V92 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V92.md`

- Linhas originais: 14
- Título: Validação local V92

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V92
## Escopo validado
- compilação do repositório;
- benchmark shadow do runner de simulação futura;
- geração da planilha operacional;
- checagem mínima de release.
## Resultado
- baseline V92 compilando e executando;
- benchmark shadow do runner futuro executando e gerando artefatos;
- `release checker` aprovado em estado limpo.
```

</details>

### V93 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V93.md`

- Linhas originais: 15
- Título: Validação local V93

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V93
## Comandos executados
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V93 compilando e executando;
- auditoria dos casos críticos do runner shadow executando e gerando artefatos;
- release checker aprovado em estado limpo.
```

</details>

### V94 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V94.md`

- Linhas originais: 15
- Título: Validação local V94

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V94
## Comandos executados
- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V94 compilando e executando;
- auditoria dos casos críticos do runner shadow executando e gerando artefatos;
- release checker aprovado em estado limpo.
```

</details>

### V95 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V95.md`

- Linhas originais: 14
- Título: Validação local V95

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V95
## Comandos executados
- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V95 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.
```

</details>

### V96 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V96.md`

- Linhas originais: 14
- Título: Validação local V96

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V96
## Comandos executados
- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V96 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.
```

</details>

### V97 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V97.md`

- Linhas originais: 14
- Título: Validação local V97

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V97
## Comandos executados
- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V97 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.
```

</details>

### V98 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V98.md`

- Linhas originais: 17
- Título: Validação local V98

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V98
## Comandos executados
- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V98 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.
- amostra curta de pagamentos futuros sem coluna de lotes informados;
- leitura técnica curta sem referência à janela de excesso;
```

</details>

### V99 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V99.md`

- Linhas originais: 22
- Título: Validação local V99

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V99
## Comandos executados
- `python aplicacao/console/principal.py`
- `python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`
## Resultado
- baseline V99 compilando e executando;
- console exibindo a seção `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra dos últimos 5 pagamentos realizados e dos próximos 5 pagamentos visível sem alterar a lógica operacional;
- release checker aprovado em estado limpo.
- amostra curta de pagamentos futuros sem coluna de lotes informados;
- leitura técnica curta sem referência à janela de excesso;
- saída do console com amostras de pagamentos enriquecidas com colunas financeiras auditáveis;
- planilha operacional gerada com lote sugerido e colunas financeiras no extrato futuro;
- release checker ajustado para V99.
```

</details>

### V100 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V100.md`

- Linhas originais: 15
- Título: Validação local V100

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V100
## Execuções mínimas realizadas
- `python aplicacao/console/principal.py`;
- `python scripts/operacional/gerar_planilha_operacional.py`;
- `python scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py`;
- `python scripts/diagnostico/verificar_release_baseline.py`.
## Resultado esperado da V100
- console executando com a nova seção de auditoria temporal dos pagamentos futuros;
- extrato futuro contendo colunas locais e temporais lado a lado;
- aba `Auditoria temporal` presente na planilha operacional;
- release checker ajustado para V100.
```

</details>

### V101 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V101.md`

- Linhas originais: 9
- Título: Validação local V101

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V101
## Resultado esperado da V101
- baseline V101 compilando e executando;
- console principal exibindo a nova seção de reescolha dinâmica pós-quebra;
- planilha operacional gerando colunas dinâmicas no `Extrato futuro` e a nova aba `Reescolha dinâmica`;
- diagnóstico dedicado da reescolha dinâmica executando;
- release checker ajustado para V101.
```

</details>

### V103 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V103.md`

- Linhas originais: 16
- Título: VALIDAÇÃO LOCAL V103

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V103
## Validação mínima executada
- `python scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Critérios de aceite desta etapa
- baseline carregando sem alterar o motor principal;
- heurística conjunta parcial restrita ao bloco crítico e sem solver global;
- console exibindo resumo, amostra de trocas preventivas e amostra do planejamento de reservas;
- `Extrato futuro` e aba `Heurística conjunta` gerados com colunas coerentes;
- release checker em `OK`.
```

</details>

### V104 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V104.md`

- Linhas originais: 14
- Título: VALIDAÇÃO LOCAL V104

<details>
<summary>Trecho inicial preservado</summary>

```text
# VALIDAÇÃO LOCAL V104
A V104 foi validada localmente com:
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
Resultados esperados:
- console com nova seção do planejamento conjunto local do bloco crítico;
- `Extrato futuro` e nova aba `Planejamento conjunto` na planilha;
- release checker em `OK`.
```

</details>

### V105 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V105.md`

- Linhas originais: 10
- Título: Validação local V105

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V105
## Comandos principais
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Objetivo da validação
Confirmar que a camada v2 roda sobre a V104, gera comparativo entre políticas do bloco crítico, escolhe uma política final auditável e exporta o resultado para console e planilha.
```

</details>

### V106 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V106.md`

- Linhas originais: 13
- Título: Validação local V106

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V106
## Comandos principais
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Objetivo da validação
Confirmar que a V106:
- mantém o repositório executável;
- atualiza corretamente a identidade da baseline;
- gera a planilha operacional na nova versão documental;
- e mantém o gate de release consistente com a separação formal entre trilha experimental local e frente central.
```

</details>

### V107 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V107.md`

- Linhas originais: 10
- Título: Validação local V107

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V107
## Objetivo
Confirmar que a V107:
- executa console e planilha;
- materializa `recomputacao_sequencial_central_v1`;
- preserva o release checker em estado OK;
- mantém a separação entre frente central e trilha experimental local.
```

</details>

### V108 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V108.md`

- Linhas originais: 8
- Título: Validação local V108

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V108
A V108 deve validar localmente que:
- a `recomputacao_sequencial_central_v1` executa com a nova régua central mínima;
- o console exibe a seção atualizada da frente central;
- a planilha operacional inclui as colunas novas da camada central;
- o gate `verificar_release_baseline.py` fecha em OK após limpeza dos artefatos efêmeros.
```

</details>

### V114 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V114.md`

- Linhas originais: 15
- Título: Validação local V114

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V114
Validações executadas:
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado esperado
- contexto carrega normalmente;
- console exibe seção do motor operacional de pagamentos + switching;
- planilha operacional contém aba `Rec. pgto+switch` e colunas de recomendação no `Extrato futuro`;
- release checker em OK.
```

</details>

### V115 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V115.md`

- Linhas originais: 15
- Título: Validação local V115

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V115
Validações executadas:
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado esperado
- contexto carrega normalmente;
- console continua exibindo a camada operacional por conta;
- planilha operacional é gerada com o nome da baseline V115;
- release checker permanece em OK após a limpeza estrutural.
```

</details>

### V116 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V116.md`

- Linhas originais: 16
- Título: Validação local V116

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V116
## Execuções mínimas realizadas
- `python scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `python scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado observado
- o comparador recalibrado executa normalmente;
- o relatório operacional é gerado com o nome da baseline V116;
- o release checker permanece em `OK`;
- a camada operacional por conta segue separada da baseline central V108.
```

</details>

### V117 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V117.md`

- Linhas originais: 18
- Título: Validação local V117

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V117
## Execuções mínimas realizadas
- `python -m py_compile nucleo/planejador_switching_temporal_v1.py`
- `python -m py_compile nucleo/alocador_pagamentos_terminal_v1.py`
- `python -m py_compile nucleo/simulador_central_eventos_v1.py`
- `python -m py_compile nucleo/avaliador_cenarios_conjuntos_v1.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
## Resultado observado
- os quatro módulos da V117 são importáveis e compilam sem erro;
- o release checker permanece em `OK` com a baseline V117;
- a aplicação principal e a geração da planilha operacional continuam executando normalmente;
- a camada documental/técnica mínima da V117 não altera a lógica econômica vigente.
```

</details>

### V118 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V118.md`

- Linhas originais: 29
- Título: Validação local V118

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V118
## Escopo validado
Validação da primeira integração funcional mínima da camada temporal conjunta.
## Rotinas executadas
- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado observado
- o recorte curto foi executado no horizonte `2026-04-20` a `2026-05-20`;
- foram avaliados 3 cenários:
  - `baseline_sem_switching`;
  - `switching_temporal_top1`;
  - `switching_temporal_top2`;
- o melhor cenário no vetor lexicográfico auditável foi `switching_temporal_top1`;
- os 15 pagamentos do recorte foram cobertos integralmente nos 3 cenários;
- a V118 passou a gerar vetor central auditável e patrimônio terminal proxy por cenário;
```

</details>

### V119 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V119.md`

- Linhas originais: 15
- Título: Validação local V119

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V119
## Execuções mínimas
- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado observado
- a integração curta permaneceu executável;
- o switching deixou de ser apenas proxy estrutural;
- o histórico do cenário passou a registrar custo fiscal realizado, valor migrado, carência/liquidez do destino e valor terminal estimado do lote;
- a baseline V119 permaneceu íntegra no release checker.
```

</details>

### V120 — `relatorios\historico\validacoes\VALIDACAO_LOCAL_V120.md`

- Linhas originais: 16
- Título: Validação local V120

<details>
<summary>Trecho inicial preservado</summary>

```text
# Validação local V120
## Rotinas executadas
- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`
## Resultado observado
- o planejador temporal passou a ranquear por ganho terminal econômico mínimo real estimado;
- no recorte curto, nenhum switching permaneceu elegível após custo fiscal + reprojeção terminal + penalidade incremental de carência/liquidez;
- o cenário vencedor passou a ser o `baseline_sem_switching`;
- a baseline V120 permaneceu íntegra no release checker.
```

</details>

## Decisão desta etapa

A faixa V091–V120 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de validações sejam consolidadas e um índice-mestre final seja criado.

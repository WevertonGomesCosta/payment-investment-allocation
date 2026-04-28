# Relatório consolidado — estruturas históricas V091–V120

## Objetivo

Consolidar a faixa `V091_V120` das estruturas históricas do repositório, preservando a evolução do runner shadow, recomputação sequencial, observabilidade do console, motor de recomendação pagamentos/switching, reorganização estrutural e camada temporal mínima, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 24
- Faixa: V091–V120
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das estruturas

| Versão | Tipo | Linhas | Título |
|---:|---|---:|---|
| V91 | `estrutura_repositorio` | 9 | Estrutura do repositório V91 |
| V92 | `estrutura_repositorio` | 9 | Estrutura do repositório V92 |
| V93 | `estrutura_repositorio` | 9 | Estrutura do repositório V93 |
| V94 | `estrutura_repositorio` | 9 | Estrutura do repositório V94 |
| V95 | `estrutura_repositorio` | 9 | Estrutura do repositório V95 |
| V96 | `estrutura_repositorio` | 9 | Estrutura do repositório V96 |
| V97 | `estrutura_repositorio` | 9 | Estrutura do repositório V97 |
| V98 | `estrutura_repositorio` | 14 | Estrutura do repositório V98 |
| V99 | `estrutura_repositorio` | 19 | Estrutura do repositório V99 |
| V100 | `estrutura_repositorio` | 21 | Estrutura do repositório V100 |
| V101 | `estrutura_repositorio` | 9 | Estrutura do repositório V101 |
| V103 | `estrutura_repositorio` | 17 | ESTRUTURA DO REPOSITÓRIO V103 |
| V104 | `estrutura_repositorio` | 10 | ESTRUTURA DO REPOSITÓRIO V104 |
| V105 | `estrutura_repositorio` | 13 | Estrutura da V105 |
| V106 | `estrutura_repositorio` | 22 | Estrutura da V106 |
| V107 | `estrutura_repositorio` | 15 | Estrutura da V107 |
| V108 | `estrutura_repositorio` | 13 | Estrutura da V108 |
| V114 | `estrutura_repositorio` | 14 | Estrutura repositório V114 |
| V115 | `estrutura_repositorio` | 21 | Estrutura repositório V115 |
| V116 | `estrutura_repositorio` | 19 | Estrutura repositório V116 |
| V117 | `estrutura_repositorio` | 21 | Estrutura repositório V117 |
| V118 | `estrutura_repositorio` | 17 | Estrutura repositório V118 |
| V119 | `estrutura_repositorio` | 15 | Estrutura repositório V119 |
| V120 | `estrutura_repositorio` | 20 | Estrutura repositório V120 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Runner shadow | Estruturas de benchmark e auditoria do runner futuro shadow foram preservadas. |
| Frente central | Recomputação sequencial, reescolha pós-quebra e camadas do bloco crítico foram consolidadas. |
| Observabilidade | Estruturas de amostras de pagamentos passados/futuros no console foram registradas. |
| Motor por pagamento | Estruturas do motor de recomendação pagamentos/switching foram preservadas. |
| Camada temporal | Estrutura mínima do planejador, alocador, simulador e avaliador temporal foi consolidada. |

## Detalhe por estrutura

### V91 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V91.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V91

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V91
## Camada nova da V91
A V91 não abre nova camada funcional. Ela realiza apenas uma correção de execução local na leitura/download da planilha financeira.
## Papel da V91
A baseline elimina uma fragilidade de Windows na promoção do arquivo temporário validado para `dados/dados_financeiros.xlsx`, preservando o restante da arquitetura da V89.
```

</details>

### V92 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V92.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V92

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V92
## Camada nova da V92
A V92 abre a camada `benchmark_runner_futuro_shadow` como absorção diagnóstica inicial do runner de simulação futura do Script 2 correto.
## Papel da V92
A baseline cria uma régua shadow reproduzível para comparar o comportamento do runner futuro legado contra a decisão local vigente, sem migrar o orquestrador legado ao fluxo principal.
```

</details>

### V93 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V93.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V93

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V93
## Camada nova da V93
A V93 abre a camada `auditoria_runner_futuro_shadow` como auditoria diagnóstica dos casos sem cobertura integral do benchmark do runner futuro shadow, com subbloco final dos casos multifonte.
## Papel da V93
A baseline cria uma régua diagnóstica reproduzível para explicar por que o runner futuro shadow perde cobertura integral em massa, sem migrar o runner legado para o fluxo principal.
```

</details>

### V94 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V94.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V94

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V94
## Camada nova da V94
A V94 abre a camada `auditoria_runner_futuro_shadow` como auditoria diagnóstica dos casos sem cobertura integral do benchmark do runner futuro shadow, com subbloco final dos casos multifonte.
## Papel da V94
A baseline cria uma régua diagnóstica reproduzível para explicar por que o runner futuro shadow perde cobertura integral em massa, sem migrar o runner legado para o fluxo principal.
```

</details>

### V95 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V95.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V95

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V95
## Camada nova da V95
A V95 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.
## Papel da V95
A baseline melhora a validação operacional rápida do passado recente e do futuro imediato sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.
```

</details>

### V96 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V96.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V96

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V96
## Camada nova da V96
A V96 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.
## Papel da V96
A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.
```

</details>

### V97 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V97.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V97

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V97
## Camada nova da V97
A V97 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.
## Papel da V97
A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.
```

</details>

### V98 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V98.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 14
- Título: Estrutura do repositório V98

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V98
## Camada nova da V98
A V98 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.
## Papel da V98
A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.
## Ajuste fino da V98
A V98 mantém a estrutura da V97, mas simplifica a leitura da amostra curta de pagamentos futuros para privilegiar apenas os campos úteis à validação humana imediata: lote sugerido, score proxy, status local e leitura técnica temporal.
```

</details>

### V99 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V99.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 19
- Título: Estrutura do repositório V99

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V99
## Camada nova da V99
A V99 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.
## Papel da V99
A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.
## Ajuste fino da V99
A V99 mantém a estrutura da V97, mas simplifica a leitura da amostra curta de pagamentos futuros para privilegiar apenas os campos úteis à validação humana imediata: lote sugerido, score proxy, status local e leitura técnica temporal.
## Ajuste estrutural da V99
A V99 mantém a estrutura da V98, mas passa a projetar no extrato futuro da planilha a mesma camada de auditabilidade financeira já exibida no console, sem abrir solver ou replanejamento temporal.
```

</details>

### V100 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V100.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 21
- Título: Estrutura do repositório V100

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V100
## Camada nova da V100
A V100 introduz uma camada intermediária entre a decisão local e qualquer leitura de plano futuro: a auditoria temporal da `decisao_local_v1`, que reaplica a sequência dos pagamentos sugeridos com depleção cumulativa da mesma fonte ao longo do tempo.
## Papel da V100
A nova camada não substitui o método vigente e não replaneja pagamentos. Seu papel é apenas separar:
- validade local já aprovada;
- coerência sequencial futura;
- primeira quebra por fonte;
- necessidade de reescolha dinâmica após exaustão cumulativa.
## Artefatos novos
- `nucleo/auditoria_temporal_decisao_local.py`;
- `scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py`;
- `scripts/inspecionar_auditoria_temporal_decisao_local.py`;
- nova aba `Auditoria temporal` na planilha operacional V100.
```

</details>

### V101 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V101.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 9
- Título: Estrutura do repositório V101

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura do repositório V101
## Camada nova da V101
A V101 preserva a camada intermediária introduzida na V100 — a auditoria temporal da `decisao_local_v1` — e adiciona uma segunda camada separada, de `reescolha_dinamica_pos_quebra`, que recomputa a melhor fonte local quando a sugestão original deixa de ser coerente na sequência.
## Papel da V101
A nova camada usa a mesma materialização de candidatos da decisão local v1, mas substitui apenas os saldos disponíveis por estados dinâmicos já abatidos na sequência. Quando a fonte original ainda cobre integralmente o pagamento, ela é mantida. Quando não cobre, a reescolha dinâmica é acionada e a melhor fonte local entre os lotes remanescentes é recomputada sem abrir solver global.
```

</details>

### V103 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V103.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 17
- Título: ESTRUTURA DO REPOSITÓRIO V103

<details>
<summary>Trecho inicial preservado</summary>

```text
# ESTRUTURA DO REPOSITÓRIO V103
## Nova camada adicionada
A V103 adiciona a camada `nucleo/heuristica_conjunta_parcial_bloco_critico.py`, acoplada ao `ContextoBaseline` sem alterar o motor principal.
## Novos pontos de integração
- `ContextoBaseline.heuristica_conjunta_parcial_bloco_critico`
- seção `PAGAMENTOS FUTUROS — HEURÍSTICA CONJUNTA PARCIAL (BLOCO CRÍTICO)` no console
- aba `Heurística conjunta` na planilha operacional
- script de diagnóstico `scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
- wrapper de compatibilidade `scripts/inspecionar_heuristica_conjunta_parcial_bloco_critico.py`
## Objetivo estrutural da V103
Criar uma ponte entre a recomputação local sequencial e futuras heurísticas mais globais, atuando apenas no bloco crítico 20/04/2026–20/05/2026 com preservação estratégica de lotes e trocas preventivas.
```

</details>

### V104 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V104.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 10
- Título: ESTRUTURA DO REPOSITÓRIO V104

<details>
<summary>Trecho inicial preservado</summary>

```text
# ESTRUTURA DO REPOSITÓRIO V104
A V104 adiciona a camada `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`, acoplada ao `ContextoBaseline` sem alterar o motor principal.
## Novos pontos estruturais
- `nucleo/planejamento_conjunto_local_bloco_critico_v1.py`
- `scripts/diagnostico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`
- `scripts/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py`
- integração da camada ao console e ao gerador da planilha operacional.
```

</details>

### V105 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V105.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 13
- Título: Estrutura da V105

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura da V105
## Novos arquivos principais
- `nucleo/microplanejamento_conjunto_bloco_critico_v2.py`
- `scripts/diagnostico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
- `scripts/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py`
## Pontos de integração
- `nucleo/contexto_baseline.py`
- `aplicacao/console/principal.py`
- `aplicacao/console/secoes_financeiras.py`
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/diagnostico/verificar_release_baseline.py`
```

</details>

### V106 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V106.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 22
- Título: Estrutura da V106

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura da V106
## Arquivos novos principais
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/BASELINE_FIXA_V106.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V106.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V106.md`
## Arquivos atualizados
- `README.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/INDICE_RELATORIOS.md`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
## Efeito estrutural
A V106 não adiciona nova lógica econômica ao motor. Seu efeito principal é documental e contratual:
- separa oficialmente o que é trilha experimental local do que é frente central;
- formaliza a métrica mínima da futura camada central;
- e realinha a documentação vigente ao estado real do repositório.
```

</details>

### V107 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V107.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 15
- Título: Estrutura da V107

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura da V107
## Arquivos novos/centrais
- `nucleo/recomputacao_sequencial_central_v1.py`
- `scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py`
- `scripts/inspecionar_recomputacao_sequencial_central_v1.py`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V107.md`
- `relatorios/atuais/BASELINE_FIXA_V107.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V107.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V107.md`
## Papel estrutural
A V107 recoloca a evolução do projeto na frente central, sem remover as camadas experimentais locais já existentes.
```

</details>

### V108 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V108.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 13
- Título: Estrutura da V108

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura da V108
Arquivos centrais adicionados/atualizados nesta baseline:
- `nucleo/recomputacao_sequencial_central_v1.py`
- `scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py`
- `scripts/inspecionar_recomputacao_sequencial_central_v1.py`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `relatorios/atuais/BASELINE_FIXA_V108.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V108.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V108.md`
A V108 recalibra a frente central sem remover as camadas experimentais locais já existentes.
```

</details>

### V114 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V114.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 14
- Título: Estrutura repositório V114

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V114
Principais acréscimos:
- `nucleo/motor_recomendacao_pagamentos_switching_v1.py`
- `scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `scripts/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
Integrações:
- `nucleo/contexto_baseline.py`
- `aplicacao/console/principal.py`
- `aplicacao/console/secoes_financeiras.py`
- `scripts/operacional/gerar_planilha_operacional.py`
```

</details>

### V115 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V115.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 21
- Título: Estrutura repositório V115

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V115
Principais ajustes:
- `scripts/diagnostico/_bootstrap.py`
- `relatorios/atuais/REORGANIZACAO_REPOSITORIO_V115.md`
- `relatorios/atuais/BASELINE_FIXA_V115.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V115.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V115.md`
Movimentos estruturais:
- documentos antigos de baseline/validação/estrutura saíram de `relatorios/atuais/` e foram consolidados em `relatorios/historico/`;
- `saidas/operacional/` foi reduzida à saída vigente da baseline;
- diagnósticos foram padronizados com bootstrap compartilhado.
Preservado propositalmente:
- `nucleo/motor_recomendacao_pagamentos_switching_v1.py` como camada operacional por conta;
- wrappers raiz em `scripts/` como compatibilidade;
- documentação V108 da frente central como referência principal do motor conjunto.
```

</details>

### V116 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V116.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 19
- Título: Estrutura repositório V116

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V116
## Arquivos centrais alterados na V116
- `nucleo/motor_recomendacao_pagamentos_switching_v1.py`
- `scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `README.md`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BASELINE_FIXA_V116.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V116.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V116.md`
- `relatorios/atuais/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`
## Observação estrutural
A V116 mantém a organização física da V115. A mudança desta entrega é concentrada no comparador local do motor operacional por conta.
```

</details>

### V117 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V117.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 21
- Título: Estrutura repositório V117

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V117
## Arquivos centrais alterados na V117
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/simulador_central_eventos_v1.py`
- `nucleo/avaliador_cenarios_conjuntos_v1.py`
- `nucleo/__init__.py`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `README.md`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `relatorios/atuais/BASELINE_FIXA_V117.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V117.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V117.md`
## Observação estrutural
A V117 mantém a execução vigente da baseline central e adiciona apenas a camada documental/técnica mínima do futuro motor conjunto temporal. Os documentos estruturais da V116 passam a compor o histórico documental.
```

</details>

### V118 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V118.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 17
- Título: Estrutura repositório V118

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V118
## Arquivos centrais alterados na V118
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `nucleo/simulador_central_eventos_v1.py`
- `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `scripts/inspecionar_integracao_funcional_minima_v117.py`
- `relatorios/atuais/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md`
- `relatorios/atuais/BASELINE_FIXA_V118.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V118.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V118.md`
## Resumo estrutural
A V118 preserva o contrato V117 e adiciona a primeira costura funcional curta entre planejamento temporal de switching, alocação terminal de pagamentos, simulação central de eventos e avaliação de cenários.
```

</details>

### V119 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V119.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 15
- Título: Estrutura repositório V119

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V119
## Arquivos centrais alterados na V119
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/simulador_central_eventos_v1.py`
- `nucleo/alocador_pagamentos_terminal_v1.py`
- `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `relatorios/atuais/BASELINE_FIXA_V119.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V119.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V119.md`
## Síntese estrutural
A V119 preserva o contrato V117 e adiciona a segunda costura funcional curta da camada temporal: a transição econômica mínima real do lote dentro do `simulador_central_eventos_v1`.
```

</details>

### V120 — `relatorios\historico\estruturas\ESTRUTURA_REPOSITORIO_V120.md`

- Tipo: `estrutura_repositorio`
- Linhas originais: 20
- Título: Estrutura repositório V120

<details>
<summary>Trecho inicial preservado</summary>

```text
# Estrutura repositório V120
## Arquivos centrais alterados na V120
- `nucleo/planejador_switching_temporal_v1.py`
- `nucleo/simulador_central_eventos_v1.py`
- `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `scripts/inspecionar_integracao_funcional_minima_v117.py`
- `nucleo/identidade_baseline.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `README.md`
- `relatorios/INDICE_RELATORIOS.md`
- `relatorios/atuais/BASELINE_FIXA_V120.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V120.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V120.md`
- `relatorios/atuais/RECALIBRACAO_PLANEJADOR_SWITCHING_TEMPORAL_V120.md`
## Síntese estrutural
A V120 preserva a integração curta existente e recalibra a triagem do `planejador_switching_temporal_v1` para aproximá-la do critério econômico real mínimo antes da simulação central.
```

</details>

## Decisão desta etapa

A faixa V091–V120 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de estruturas sejam consolidadas e um índice-mestre final seja criado.

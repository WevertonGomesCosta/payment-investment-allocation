# Relatório consolidado — baselines históricas V091–V120

## Objetivo

Consolidar a faixa de baselines históricas `V091_V120`, preservando a transição da governança contratual para a frente central, recomputação sequencial, runner shadow, motor de recomendação pagamentos/switching, reorganização estrutural e camada temporal mínima, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 24
- Faixa: V091–V120
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das baselines

| Versão | Classe preliminar | Linhas | Título |
|---:|---|---:|---|
| V91 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V91 |
| V92 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V92 |
| V93 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V93 |
| V94 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V94 |
| V95 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V95 |
| V96 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V96 |
| V97 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V97 |
| V98 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V98 |
| V99 | `BASELINE_RELEVANTE` | 25 | Baseline fixa V99 |
| V100 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V100 |
| V101 | `BASELINE_RELEVANTE` | 19 | Baseline fixa V101 |
| V103 | `BASELINE_RELEVANTE` | 12 | BASELINE FIXA V103 |
| V104 | `BASELINE_RELEVANTE` | 10 | BASELINE FIXA V104 |
| V105 | `BASELINE_RELEVANTE` | 14 | Baseline fixa V105 |
| V106 | `MARCO_CHAVE_PROVAVEL` | 18 | Baseline fixa V106 |
| V107 | `BASELINE_RELEVANTE` | 10 | Baseline fixa V107 |
| V108 | `BASELINE_RELEVANTE` | 11 | Baseline fixa V108 |
| V114 | `BASELINE_RELEVANTE` | 9 | Baseline fixa V114 |
| V115 | `BASELINE_RELEVANTE` | 14 | Baseline fixa V115 |
| V116 | `BASELINE_RELEVANTE` | 14 | Baseline fixa V116 |
| V117 | `BASELINE_RELEVANTE` | 14 | Baseline fixa V117 |
| V118 | `BASELINE_RELEVANTE` | 33 | Baseline fixa V118 |
| V119 | `BASELINE_RELEVANTE` | 21 | Baseline fixa V119 |
| V120 | `BASELINE_RELEVANTE` | 21 | Baseline fixa V120 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Governança e frente central | Saneamento contratual, métrica canônica e retomada da frente central foram preservados. |
| Recomputação sequencial | Evolução da recomputação central por pagamento e reescolha pós-quebra foi consolidada. |
| Runner shadow e legado | Benchmarks do runner futuro e leitura do Script 2 correto foram preservados. |
| Motor por pagamento | Motor de recomendação pagamentos + switching e calibração local foram preservados. |
| Camada temporal | Contrato e implementação mínima do motor conjunto temporal foram consolidados. |

## Marcos-chave prováveis nesta faixa

| Versão | Título |
|---:|---|
| V106 | Baseline fixa V106 |

## Detalhe por baseline

### V91 — `relatorios\historico\baselines\BASELINE_FIXA_V91.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V91

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V91
## Escopo da V91
A V91 preserva integralmente a baseline funcional imediatamente anterior e corrige a etapa de promoção do arquivo temporário usado no download da planilha financeira. A correção evita falso `PermissionError` no Windows ao validar o `.xlsx` baixado antes de sobrescrever `dados/dados_financeiros.xlsx`.
## O que a V91 altera
- validação do arquivo baixado com fechamento explícito do handle do `pd.ExcelFile`;
- tratamento específico de `PermissionError` na promoção do arquivo temporário para a planilha canônica;
- atualização da identidade da baseline e da documentação vigente.
## O que a V91 não altera
- motor financeiro;
- replay;
- `proxy v3` congelado;
- benchmarks shadow e auditorias diagnósticas.
```

</details>

### V92 — `relatorios\historico\baselines\BASELINE_FIXA_V92.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V92

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V92
## Escopo da V92
A V92 preserva integralmente a baseline funcional imediatamente anterior e abre o benchmark shadow do runner de simulação futura do Script 2 correto, sem migrar o runner legado bruto para o fluxo principal.
## O que a V92 altera
- nova camada diagnóstica `benchmark_runner_futuro_shadow`;
- comparação reproduzível entre o runner shadow futuro e a decisão local vigente;
- atualização da identidade da baseline e da documentação vigente.
## O que a V92 não altera
- motor financeiro;
- replay;
- `proxy v3` congelado;
- runners legados como orquestradores do fluxo principal.
```

</details>

### V93 — `relatorios\historico\baselines\BASELINE_FIXA_V93.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V93

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V93
## Escopo da V93
A V93 preserva integralmente a baseline funcional imediatamente anterior e abre a auditoria dos casos sem cobertura integral do runner futuro shadow, com subbloco final para os 3 casos multifonte, sem migrar o runner legado bruto para o fluxo principal.
## O que a V93 altera
- nova camada diagnóstica `auditoria_runner_futuro_shadow`;
- novos artefatos diagnósticos para casos sem cobertura integral e subbloco multifonte;
- documentação vigente sincronizada com a nova etapa.
## O que a V93 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline.
```

</details>

### V94 — `relatorios\historico\baselines\BASELINE_FIXA_V94.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V94

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V94
## Escopo da V94
A V94 preserva integralmente a baseline funcional imediatamente anterior e abre a auditoria dos casos sem cobertura integral do runner futuro shadow, com subbloco final para os 3 casos multifonte, sem migrar o runner legado bruto para o fluxo principal.
## O que a V94 altera
- nova camada diagnóstica `auditoria_runner_futuro_shadow`;
- novos artefatos diagnósticos para casos sem cobertura integral e subbloco multifonte;
- documentação vigente sincronizada com a nova etapa.
## O que a V94 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline.
```

</details>

### V95 — `relatorios\historico\baselines\BASELINE_FIXA_V95.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V95

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V95
## Escopo da V95
A V95 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e adiciona ao console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos.
## O que a V95 altera
- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.
## O que a V95 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V94.
```

</details>

### V96 — `relatorios\historico\baselines\BASELINE_FIXA_V96.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V96

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V96
## Escopo da V96
A V96 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e adiciona ao console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos.
## O que a V96 altera
- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.
## O que a V96 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V95.
```

</details>

### V97 — `relatorios\historico\baselines\BASELINE_FIXA_V97.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V97

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V97
## Escopo da V97
A V97 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e adiciona ao console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos.
## O que a V97 altera
- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.
## O que a V97 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V95.
```

</details>

### V98 — `relatorios\historico\baselines\BASELINE_FIXA_V98.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V98

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V98
## Escopo da V98
A V98 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e mantém no console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos, refinando a semântica da amostra futura.
## O que a V98 altera
- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.
## O que a V98 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V95.
```

</details>

### V99 — `relatorios\historico\baselines\BASELINE_FIXA_V99.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 25
- Título: Baseline fixa V99

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V99
## Escopo da V99
A V99 preserva integralmente a baseline funcional imediatamente anterior, mantém a auditoria dos casos sem cobertura integral do runner futuro shadow com subbloco final para os 3 casos multifonte e mantém no console uma amostra dos últimos 5 pagamentos já realizados e dos próximos 5 pagamentos, refinando a semântica da amostra futura.
## O que a V99 altera
- nova seção de console `PAGAMENTOS — AMOSTRAS OPERACIONAIS`;
- amostra auditável dos 5 pagamentos mais recentes já executados a partir do `replay_passado.log_passado`;
- amostra auditável dos 5 próximos pagamentos a partir de `dados_operacionais.gastos_canonicos`;
- documentação vigente sincronizada com a nova derivação.
## O que a V99 não altera
- motor financeiro;
- replay passado;
- `proxy econômico v3` congelado;
- fluxo principal da baseline;
- auditoria diagnóstica do runner shadow já aberta na V95.
## Ajuste incremental da V99
A V99 mantém a baseline funcional da V98 e amplia a auditabilidade operacional dos pagamentos, adicionando ao console e ao extrato futuro a leitura de lote sugerido, saldo antes, bruto, imposto, líquido e saldo remanescente.
```

</details>

### V100 — `relatorios\historico\baselines\BASELINE_FIXA_V100.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V100

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V100
## Escopo da V100
A V100 preserva a baseline funcional da V99, mantém a saída operacional do console e do extrato futuro já aprovadas e adiciona uma auditoria temporal explícita sobre a `decisao_local_v1`, com depleção cumulativa dos lotes sugeridos na fotografia da data de referência.
## O que a V100 altera
- adiciona o módulo `nucleo/auditoria_temporal_decisao_local.py`;
- carrega a auditoria temporal como parte do `ContextoBaseline`;
- adiciona uma nova seção no console principal para distinguir cobertura local da coerência sequencial futura;
- amplia o `Extrato futuro` com colunas temporais e cria a aba `Auditoria temporal`;
- adiciona script diagnóstico próprio para a auditoria temporal da decisão local.
## O que a V100 não altera
- não altera o método governante (`decisao_local_v1` + `proxy econômico v3`);
- não reabre o runner shadow como método operacional;
- não adiciona solver global, multifonte governante ou switching ao fluxo principal;
- não altera a leitura local já aprovada do console e da planilha, apenas a complementa com uma camada temporal separada.
```

</details>

### V101 — `relatorios\historico\baselines\BASELINE_FIXA_V101.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 19
- Título: Baseline fixa V101

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V101
## Escopo da V101
A V101 preserva a baseline funcional da V100, mantém a saída operacional do console e do extrato futuro já aprovadas, preserva a auditoria temporal explícita sobre a `decisao_local_v1` e adiciona uma camada de reescolha dinâmica pós-quebra para recomputar a fonte dos pagamentos futuros que deixam de ser coerentes sequencialmente, sem reabrir o solver global.
## O que a V101 altera
- adiciona a camada `reescolha_dinamica_pos_quebra`, separada do motor principal;
- preserva a auditoria temporal da V100 e passa a recomputar a melhor fonte local entre os lotes remanescentes quando a sugestão original quebra na sequência;
- amplia o `Extrato futuro` com colunas dinâmicas finais e adiciona a aba `Reescolha dinâmica`;
- adiciona uma nova seção dedicada no console principal para resumir reescolhas, mudanças efetivas de fonte e falhas remanescentes.
## O que a V101 não altera
- não reabre o solver global;
- não reabre o runner shadow como método governante;
- não altera o método local governante (`decisao_local_v1 + proxy v3`);
- não altera o replay do passado nem a estrutura oficial do fluxo principal.
```

</details>

### V103 — `relatorios\historico\baselines\BASELINE_FIXA_V103.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 12
- Título: BASELINE FIXA V103

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V103
A V103 preserva a baseline funcional imediatamente anterior e adiciona uma **heurística conjunta parcial** focada no bloco crítico entre **20/04/2026** e **20/05/2026**. A nova camada continua sem solver global, usa a `decisao_local_v1` com `proxy v3` como base e introduz planejamento de reservas estratégicas por fonte para testar se a primeira grande quebra estrutural pode ser adiada.
## O que a V103 adiciona
- nova camada `heuristica_conjunta_parcial_bloco_critico`;
- planejamento heurístico de reservas por fonte para o bloco crítico;
- trocas preventivas de lote por preservação estratégica;
- comparação da primeira sem cobertura da heurística com a primeira quebra temporal e com a primeira sem cobertura pós-reescolha;
- nova seção dedicada no console principal;
- novas colunas no `Extrato futuro` e nova aba `Heurística conjunta` na planilha operacional.
```

</details>

### V104 — `relatorios\historico\baselines\BASELINE_FIXA_V104.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 10
- Título: BASELINE FIXA V104

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V104
A V104 preserva a baseline funcional imediatamente anterior e adiciona a camada `planejamento_conjunto_local_bloco_critico_v1`, restrita ao intervalo **20/04/2026–20/05/2026**. Essa camada compara poucas políticas candidatas de consumo e preservação de lotes com objetivo explícito de melhorar a cobertura do **Cartão Azul de 20/05** sem abrir solver global.
## O que a V104 adiciona
- comparação auditável entre políticas candidatas do bloco crítico;
- seleção automática da melhor política local segundo cobertura do evento-âncora, pagamentos cobertos no bloco e déficit total;
- nova trilha operacional do bloco crítico no console e na planilha;
- manutenção integral da auditabilidade das camadas V102 e V103.
```

</details>

### V105 — `relatorios\historico\baselines\BASELINE_FIXA_V105.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 14
- Título: Baseline fixa V105

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V105
A V105 preserva a baseline imediatamente anterior e adiciona a camada `microplanejamento_conjunto_bloco_critico_v2`, restrita ao intervalo **20/04/2026–20/05/2026**.
## Objetivo
- comparar poucas políticas candidatas no bloco crítico;
- embutir multifonte de forma controlada;
- usar reservas explícitas de lotes estratégicos;
- maximizar hierarquicamente a cobertura do **Cartão Azul de 20/05** antes de olhar cobertura do bloco e déficit total.
## Restrições preservadas
- sem solver global completo;
- sem promoção do runner shadow;
- mantendo alta auditabilidade em console, planilha e diagnósticos.
```

</details>

### V106 — `relatorios\historico\baselines\BASELINE_FIXA_V106.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 18
- Título: Baseline fixa V106

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V106
A V106 preserva integralmente a baseline imediatamente anterior em termos de lógica executável e adiciona uma **camada documental/contratual** de saneamento do repositório.
## Objetivo
- separar formalmente a trilha experimental local da frente central do projeto;
- redefinir o eixo principal do repositório no motor conjunto de pagamentos, aportes e switching;
- formalizar a métrica canônica mínima central que vai governar a futura `recomputacao_sequencial_central_v1`.
## Resultado principal
- V103–V105 permanecem como trilha experimental local do bloco crítico;
- a frente central volta a ser o caminho principal de evolução do motor;
- a V106 corrige o contrato operacional, o índice documental e o README para refletir essa separação.
## Restrições preservadas
- sem solver global completo;
- sem promoção automática das camadas locais V103–V105;
- mantendo alta auditabilidade no console, na planilha e nos diagnósticos.
```

</details>

### V107 — `relatorios\historico\baselines\BASELINE_FIXA_V107.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 10
- Título: Baseline fixa V107

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V107
A V107 preserva a governança contratual da V106 e adiciona a primeira camada executável da frente central: `recomputacao_sequencial_central_v1`.
## Propósito
- retomar a frente central do projeto;
- usar a métrica canônica mínima central como régua obrigatória;
- recalcular fontes de pagamento com estado residual atualizado;
- manter V103–V105 como trilha experimental local.
```

</details>

### V108 — `relatorios\historico\baselines\BASELINE_FIXA_V108.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 11
- Título: Baseline fixa V108

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V108
A V108 preserva a governança contratual da V106 e a retomada da frente central da V107, adicionando uma calibração mínima da `recomputacao_sequencial_central_v1`.
## Escopo fixado
- frente central mantida como eixo principal;
- V103–V105 mantidas como trilha experimental local;
- penalidade explícita de escassez futura para `PROTEGIDA`;
- prioridade intraclasse no mesmo dia;
- fallback auditável de “sem fonte viável”.
```

</details>

### V114 — `relatorios\historico\baselines\BASELINE_FIXA_V114.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 9
- Título: Baseline fixa V114

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V114
A V114 adiciona o `motor_recomendacao_pagamentos_switching_v1` ao repositório.
## Status da baseline
- **baseline principal da frente central:** V108
- **baseline do repositório entregue:** V114
- **papel da V114:** camada operacional de recomendação por conta, comparando pagar sem switching, com switching simples e com combinação mínima.
```

</details>

### V115 — `relatorios\historico\baselines\BASELINE_FIXA_V115.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 14
- Título: Baseline fixa V115

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V115
A V115 é uma baseline de **reorganização estrutural e limpeza controlada** do repositório.
## Status da baseline
- **baseline central/contratual da frente principal:** V108
- **baseline operacional por conta preservada:** V114
- **baseline do repositório entregue:** V115
- **papel da V115:** reorganizar documentação, histórico, saídas e bootstrap diagnóstico para recentrar o projeto no motor conjunto final.
## Escopo
A V115 não altera a lógica econômica da frente central nem promove automaticamente a camada operacional por conta a motor final do projeto.
```

</details>

### V116 — `relatorios\historico\baselines\BASELINE_FIXA_V116.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 14
- Título: Baseline fixa V116

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V116
A V116 é uma baseline de **recalibração cirúrgica do comparador local** do `motor_recomendacao_pagamentos_switching_v1`.
## Status da baseline
- **baseline central/contratual da frente principal:** V108
- **baseline estrutural imediatamente anterior:** V115
- **baseline do repositório entregue:** V116
- **papel da V116:** manter a limpeza estrutural da V115 e reduzir inflação local de `switching_simples` com consumo residual temporal por lote e fallback automático para `sem_switching`.
## Escopo
A V116 não promove o motor por conta a motor final do projeto. Ela apenas recalibra uma camada auxiliar local para reduzir recomendações espúrias e melhorar auditabilidade operacional.
```

</details>

### V117 — `relatorios\historico\baselines\BASELINE_FIXA_V117.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 14
- Título: Baseline fixa V117

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V117
A V117 é uma baseline **documental/técnica mínima** voltada à formalização do futuro motor conjunto temporal do projeto.
## Status da baseline
- **baseline central/contratual da frente principal:** V108
- **baseline operacional imediatamente anterior:** V116
- **baseline do repositório entregue:** V117
- **papel da V117:** criar o contrato formal do motor conjunto temporal e os esqueletos executáveis mínimos de `planejador_switching_temporal_v1`, `alocador_pagamentos_terminal_v1`, `simulador_central_eventos_v1` e `avaliador_cenarios_conjuntos_v1`.
## Escopo
A V117 não altera a lógica econômica vigente da baseline central nem promove o motor operacional por conta a motor final. Esta entrega formaliza interfaces e estruturas mínimas para a próxima etapa de integração temporal conjunta.
```

</details>

### V118 — `relatorios\historico\baselines\BASELINE_FIXA_V118.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 33
- Título: Baseline fixa V118

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V118
A V118 é a baseline **funcional mínima** da nova camada temporal do projeto.
## Papel da V118
- preservar a baseline central V108 como referência contratual;
- preservar a V116 como baseline operacional anterior por conta;
- manter o contrato V117 do motor conjunto temporal;
- implementar a **primeira integração funcional mínima** entre:
  - `planejador_switching_temporal_v1`;
  - `alocador_pagamentos_terminal_v1`;
  - `simulador_central_eventos_v1`;
  - `avaliador_cenarios_conjuntos_v1`.
## Estado congelado nesta entrega
- **baseline do repositório entregue:** V118
- **baseline central/contratual principal:** V108
- **baseline operacional anterior por conta:** V116
- **camada central temporal mínima integrada:** V118
## Escopo efetivo da V118
A V118 já executa um recorte curto real de datas críticas, com:
```

</details>

### V119 — `relatorios\historico\baselines\BASELINE_FIXA_V119.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 21
- Título: Baseline fixa V119

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V119
A V119 é a baseline **temporal mínima com transição econômica real simplificada do lote**.
## Papel da V119
A V119 preserva:
- o contrato V117 do motor conjunto temporal;
- a integração funcional mínima da V118;
- a separação entre frente central V108 e camada operacional por conta.
E acrescenta:
- switching com custo fiscal realizado estimado;
- atualização do produto de destino no lote;
- atualização de carência/liquidez do destino;
- projeção terminal simplificada do lote migrado no recorte curto.
## Escopo efetivo da V119
A V119 ainda não é solver global completo.
Ela executa apenas uma transição econômica mínima e auditável no recorte curto da camada temporal.
```

</details>

### V120 — `relatorios\historico\baselines\BASELINE_FIXA_V120.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 21
- Título: Baseline fixa V120

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V120
A V120 é a baseline **temporal mínima recalibrada no planejador de switching**.
## Papel da V120
A V120 preserva:
- o contrato V117 do motor conjunto temporal;
- a frente central V108 como referência contratual;
- a camada operacional V116 como referência local por conta;
- a segunda integração econômica mínima da V119 no simulador.
E acrescenta:
- recalibração do `planejador_switching_temporal_v1`;
- ranqueamento por `ganho_terminal_economico_minimo_estimado`;
- incorporação prévia de custo fiscal, carência incremental e patrimônio terminal reprojetado antes do simulador central.
## Escopo efetivo da V120
A V120 ainda não é solver global completo.
Ela é uma baseline de **triagem temporal economicamente mais coerente**, voltada a evitar envio de switchings estruturalmente ruins ao simulador central.
```

</details>

## Decisão desta etapa

A faixa V091–V120 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de baselines sejam consolidadas e um índice-mestre final seja criado.

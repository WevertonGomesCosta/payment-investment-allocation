# Relatório consolidado — baselines históricas V121–V150

## Objetivo

Consolidar a faixa de baselines históricas `V121_V150`, preservando a expansão multidestino, ranking Carteira-only, simulações multihorizonte, grade diária de switching, parâmetros de produto, comparador híbrido, ativação de lotes futuros, alocador terminal e preparação para absorção de modelos do Script 1, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 19
- Faixa: V121–V150
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das baselines

| Versão | Classe preliminar | Linhas | Título |
|---:|---|---:|---|
| V121 | `BASELINE_RELEVANTE` | 22 | Baseline fixa V121 |
| V122 | `BASELINE_RELEVANTE` | 20 | Baseline fixa V122 |
| V123 | `BASELINE_RELEVANTE` | 3 | V123 |
| V124 | `BASELINE_GRANULAR` | 3 | V124 |
| V125 | `BASELINE_GRANULAR` | 3 | V125 |
| V126 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V126 |
| V127 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V127 |
| V128 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V128 |
| V129 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V129 |
| V130 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V130 |
| V131 | `BASELINE_RELEVANTE` | 3 | Baseline fixa — V131 |
| V132 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V132 |
| V133 | `BASELINE_RELEVANTE` | 5 | Baseline fixa V133 |
| V134 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V134 |
| V135 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V135 |
| V136 | `BASELINE_RELEVANTE` | 3 | Baseline fixa V136 |
| V137 | `BASELINE_RELEVANTE` | 6 | BASELINE FIXA V137 |
| V138 | `BASELINE_RELEVANTE` | 5 | BASELINE FIXA V138 |
| V140 | `BASELINE_RELEVANTE` | 8 | Baseline fixa V140 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Planejador temporal | Expansão multidestino, testes de horizonte longo e simulação central foram preservados. |
| Ranking Carteira-only | Incorporação do ranking estabilizado como fonte de destinos foi consolidada. |
| Grade diária de switching | Avaliações diárias, parametrização de janela crítica e expansão da grade oficial híbrida foram preservadas. |
| Comparador híbrido | Introdução e integração do comparador híbrido como filtro de promoção foram consolidadas. |
| Alocador terminal | Primeira integração do alocador de pagamentos terminal e preparação para modelos do Script 1 foram preservadas. |

## Marcos-chave prováveis nesta faixa

Nenhum marco-chave provável classificado pelo inventário.

## Detalhe por baseline

### V121 — `relatorios\historico\baselines\BASELINE_FIXA_V121.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 22
- Título: Baseline fixa V121

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V121
A V121 é a baseline **temporal mínima expandida para múltiplos destinos elegíveis no planejador de switching**.
## Papel da V121
A V121 preserva:
- o contrato V117 do motor conjunto temporal;
- a frente central V108 como referência contratual;
- a camada operacional V116 como referência local por conta;
- a segunda integração econômica mínima da V119 no simulador;
- a recalibração econômica mínima do planejador introduzida na V120.
E acrescenta:
- expansão do `planejador_switching_temporal_v1` para múltiplos destinos elegíveis por lote;
- comparação multidestino com o mesmo `ganho_terminal_economico_minimo_estimado`;
- identificação explícita de quando o destino padrão falha e nenhum destino alternativo sobrevive economicamente.
## Escopo efetivo da V121
A V121 ainda não é solver global completo.
Ela é uma baseline de **triagem temporal multidestino economicamente mais coerente**, voltada a testar se alternativas ao destino padrão melhoram o cenário antes da simulação central.
```

</details>

### V122 — `relatorios\historico\baselines\BASELINE_FIXA_V122.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 20
- Título: Baseline fixa V122

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V122
A V122 é a baseline **diagnóstica multihorizonte do planejador temporal de switching**.
## Papel da V122
A V122 preserva:
- a frente central V108;
- a camada temporal V117–V121 já integrada;
- a expansão multidestino do `planejador_switching_temporal_v1`.
E acrescenta:
- um teste explícito de horizonte mais longo no planejador;
- uma comparação entre 30, 60, 90 e 120 dias;
- evidência de quando o custo fiscal inicial deixa de dominar completamente o switching.
## Escopo efetivo da V122
A V122 não altera a lógica econômica do simulador central.
Ela acrescenta instrumentação diagnóstica para decidir se o próximo passo deve continuar no planejador ou migrar candidatos positivos para simulação central controlada.
```

</details>

### V123 — `relatorios\historico\baselines\BASELINE_FIXA_V123.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: V123

<details>
<summary>Trecho inicial preservado</summary>

```text
# V123
Baseline fixa focada na incorporação do ranking Carteira-only estabilizado ao projeto principal.
```

</details>

### V124 — `relatorios\historico\baselines\BASELINE_FIXA_V124.md`

- Classe preliminar: `BASELINE_GRANULAR`
- Linhas originais: 3
- Título: V124

<details>
<summary>Trecho inicial preservado</summary>

```text
# V124
Baseline atual após a rerodagem da simulação central controlada em horizonte mais longo usando o ranking Carteira-only estabilizado como fonte de destinos do planejador temporal.
```

</details>

### V125 — `relatorios\historico\baselines\BASELINE_FIXA_V125.md`

- Classe preliminar: `BASELINE_GRANULAR`
- Linhas originais: 3
- Título: V125

<details>
<summary>Trecho inicial preservado</summary>

```text
# V125
Baseline atual após a auditoria multihorizonte do cenário conjunto, expandindo a análise temporal para uma grade mais rica de janelas e verificando quando o switching realmente sobrevive economicamente.
```

</details>

### V126 — `relatorios\historico\baselines\BASELINE_FIXA_V126.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V126

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V126
A V126 formaliza a grade diária de avaliação de data ótima de switching, com comparação condicional por dia e suporte a cenários isolados/agrupados em modo integral e parcial 50%.
```

</details>

### V127 — `relatorios\historico\baselines\BASELINE_FIXA_V127.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V127

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V127
A V127 consolida a exclusão definitiva do switching parcial na grade diária e passa a avaliar apenas cenários integrais individuais e agrupados, com suporte explícito a lotes não aportados disponíveis quando existirem.
```

</details>

### V128 — `relatorios\historico\baselines\BASELINE_FIXA_V128.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V128

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V128
A V128 consolida a continuação da grade diária integral após `2026-05-20` e confirma, no horizonte auditado ampliado até `2026-08-18`, que a janela vencedora iniciada em `2026-04-30` permanece dominante.
```

</details>

### V129 — `relatorios\historico\baselines\BASELINE_FIXA_V129.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V129

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V129
A V129 corrige a leitura/propagação de parâmetros de produto no switching temporal, com foco em aplicação mínima/máxima e auditoria focal da janela crítica.
```

</details>

### V130 — `relatorios\historico\baselines\BASELINE_FIXA_V130.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V130

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V130
A V130 mantém a V129 como baseline lógica e adiciona a rerodagem parametrizada da janela crítica `2026-04-30` a `2026-05-20`, com validação de ticket individual e agrupado no switching diário.
```

</details>

### V131 — `relatorios\historico\baselines\BASELINE_FIXA_V131.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa — V131

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa — V131
A V131 mantém a lógica operacional da V130 e adiciona uma auditoria cirúrgica do bloco `2026-05-13` a `2026-05-20`, mostrando que o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` vence a métrica lexicográfica, mas não o objetivo terminal.
```

</details>

### V132 — `relatorios\historico\baselines\BASELINE_FIXA_V132.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V132

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V132
A V132 introduz o comparador híbrido de switching, que reclassifica cenários diários em vencedor operacional, vencedor terminal, vencedor híbrido aceitável ou dominado pelo baseline, bloqueando promoção automática de cenários que piorem patrimônio terminal.
```

</details>

### V133 — `relatorios\historico\baselines\BASELINE_FIXA_V133.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 5
- Título: Baseline fixa V133

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V133
A V133 promove a integração do comparador híbrido ao fluxo oficial da grade diária.
Mudança central: o consolidado diário oficial deixa de promover automaticamente vencedores apenas operacionais e passa a emitir `vencedor terminal`, `vencedor híbrido aceitável` ou `baseline_sem_switching`.
```

</details>

### V134 — `relatorios\historico\baselines\BASELINE_FIXA_V134.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V134

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V134
A V134 consolida a expansão da grade diária oficial híbrida além de 2026-05-20, com promoção oficial apenas de `vencedor_terminal`, `vencedor_hibrido_aceitavel` ou `baseline_sem_switching`.
```

</details>

### V135 — `relatorios\historico\baselines\BASELINE_FIXA_V135.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V135

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V135
A V135 consolida a auditoria de fechamento da frente temporal. A decisão vigente é **não encerrar ainda** a frente de switching oficial, porque o horizonte ainda não cobre até `2027-03-31` e a base mantém lotes futuros não aportados materialmente relevantes.
```

</details>

### V136 — `relatorios\historico\baselines\BASELINE_FIXA_V136.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 3
- Título: Baseline fixa V136

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V136
A V136 consolida a correção estrutural da ativação dos lotes não aportados futuros no fluxo oficial híbrido. A partir desta versão, esses lotes entram como fontes elegíveis exatamente na data de recebimento.
```

</details>

### V137 — `relatorios\historico\baselines\BASELINE_FIXA_V137.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 6
- Título: BASELINE FIXA V137

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V137
- baseline anterior: V136
- papel da V137: introduzir a primeira versão funcional do `alocador_pagamentos_terminal_v1`
- escopo: comparação entre saldo disponível, lote não aportado, lote aportado, combinação mínima e cenário com switching elegível filtrado pelo comparador híbrido
- status: baseline apta para a próxima etapa de integração com o motor de pagamentos
```

</details>

### V138 — `relatorios\historico\baselines\BASELINE_FIXA_V138.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 5
- Título: BASELINE FIXA V138

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V138
- papel da V138: integrar o `alocador_pagamentos_terminal_v1` ao fluxo oficial de um recorte curto real de pagamentos.
- foco: validar em dados do projeto quando o fluxo escolhe saldo disponível, lote não aportado, lote aportado, combinação mínima ou cenário com switching elegível já filtrado pelo comparador híbrido.
- escopo: integração funcional do alocador ao recorte curto oficial, sem reabrir a frente de auditoria aberta de switching.
```

</details>

### V140 — `relatorios\historico\baselines\BASELINE_FIXA_V140.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 8
- Título: Baseline fixa V140

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V140
A V140 mantém a V139 como baseline estrutural e adiciona o contrato formal de absorção dos modelos do Script 1 na camada de pagamentos.
Nesta etapa:
- não há expansão do bloco real de pagamentos;
- não há nova auditoria ampla de switching;
- o foco é preparar a próxima integração controlada das heurísticas H1–H3 ao `alocador_pagamentos_terminal_v1`.
```

</details>

## Decisão desta etapa

A faixa V121–V150 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que o índice-mestre final das baselines históricas seja criado.

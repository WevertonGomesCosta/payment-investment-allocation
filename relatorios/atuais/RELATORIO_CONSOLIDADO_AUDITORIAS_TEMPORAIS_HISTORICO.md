# Relatório consolidado — auditorias históricas temporais

## Objetivo

Consolidar os documentos históricos de `relatorios/historico/auditorias_especificas/temporal/` em um único relatório atual, preservando a trilha de switching temporal, motor de recomendação, grade diária, avaliação multihorizonte, proxy/híbrido e casos cirúrgicos de lotes sem manter arquivos granulares.

## Regra de autoridade documental

Este relatório preserva valor histórico e rastreabilidade metodológica. Ele não substitui o contrato mestre, o modelo matemático-estatístico-financeiro oficial, a baseline funcional vigente nem os documentos atuais em `relatorios/atuais/`.

- Arquivos consolidados: 15
- Nenhum motor, dado, script operacional ou saída oficial foi alterado nesta consolidação.

## Síntese dos documentos

| Arquivo | Tema classificado | Linhas | Título |
|---|---|---:|---|
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md` | auditoria_temporal_geral | 32 | Auditoria cirúrgica dos 42 casos reaproveitáveis — proxy v3 vs benchmark híbrido shadow |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_CIRURGICA_BLOCO_8500_PICPAY_V131.md` | casos_cirurgicos_lotes | 121 | Auditoria cirúrgica do bloco 2026-05-13 a 2026-05-20 — V131 |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md` | motor_recomendacao_pagamentos_switching | 33 | Auditoria cirúrgica do comparador do `motor_recomendacao_pagamentos_switching_v1` — V116 |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md` | casos_cirurgicos_lotes | 34 | Auditoria fina da transição dominante — Lote 3000 mar. B -> Lote 8500 mar. |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_MULTIHORIZONTE_CENARIOS_TEMPO_V125.md` | planejamento_temporal_multihorizonte | 148 | Auditoria multihorizonte de cenários de tempo — V125 |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_PARAMETROS_PRODUTOS_SWITCHING_V129.md` | parametros_produtos_switching | 64 | Auditoria de parâmetros de produtos no switching — V129 |
| `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md` | comparacao_proxy_hibrido | 51 | Auditoria residual das divergências materiais — proxy v3 vs benchmark híbrido shadow |
| `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V126.md` | grade_diaria_switching | 400 | Avaliação diária da data ótima de switching — V126 |
| `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V127.md` | grade_diaria_switching | 323 | Avaliação diária da data ótima de switching — V127 |
| `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V128.md` | grade_diaria_switching | 315 | Avaliação diária da data ótima de switching — V128 |
| `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_PARAMETRIZADA_JANELA_V130.md` | grade_diaria_switching | 89 | Avaliação diária parametrizada da janela crítica — V130 |
| `relatorios/historico/auditorias_especificas/temporal/EXPANSAO_MULTIDESTINO_PLANEJADOR_SWITCHING_TEMPORAL_V121.md` | planejamento_temporal_multihorizonte | 28 | Expansão multidestino do planejador temporal de switching — V121 |
| `relatorios/historico/auditorias_especificas/temporal/GRADE_DIARIA_OFICIAL_HIBRIDA_V133.md` | grade_diaria_switching | 47 | Grade diária oficial com comparador híbrido — V133 |
| `relatorios/historico/auditorias_especificas/temporal/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md` | auditoria_temporal_geral | 128 | Integração funcional mínima V117/V121 — recorte curto |
| `relatorios/historico/auditorias_especificas/temporal/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md` | motor_recomendacao_pagamentos_switching | 35 | Motor recomendação pagamentos + switching V114 |

## Interpretação consolidada por tema

| Tema | Informação preservada |
|---|---|
| Motor de recomendação pagamentos/switching | Histórico da transição para recomendações por pagamento com switching preservado. |
| Grade diária de switching | Avaliações de data ótima, grade diária e promoção/bloqueio de cenários foram preservadas. |
| Planejamento temporal multihorizonte | Evidências sobre janelas longas, multidestino e multihorizonte foram preservadas. |
| Proxy vs. híbrido | Auditorias sobre divergências entre proxy v3 e comparador híbrido foram preservadas. |
| Casos cirúrgicos de lotes | Auditorias específicas envolvendo lotes críticos foram preservadas. |
| Limpeza | A pasta granular pode ser removida após validação do relatório consolidado. |

## Detalhe consolidado por arquivo

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`

- Tema classificado: `auditoria_temporal_geral`
- Título: Auditoria cirúrgica dos 42 casos reaproveitáveis — proxy v3 vs benchmark híbrido shadow
- Linhas originais: 32

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria cirúrgica dos 42 casos reaproveitáveis — proxy v3 vs benchmark híbrido shadow
## Escopo
Esta auditoria aprofunda **apenas** os casos já classificados na V79 como `potencial_reaproveitamento_proxy_v3`.
Ela **não** altera o fluxo principal e **não** substitui automaticamente o `proxy v3`.
## Objetivo
Separar os 42 casos reaproveitáveis em:
- padrão dominante realmente promissor;
- casos isolados reaproveitáveis;
- prioridades cirúrgicas para eventual auditoria fina futura.
## Leitura metodológica
A ideia desta etapa não é reabrir a decisão local vigente como um todo.
Ela é apenas verificar se o sinal reaproveitável está concentrado em um padrão suficientemente estável para justificar um ajuste fino localizado no futuro.
## Resultado esperado da V80
- identificar a transição dominante dentro dos 42 casos;
- mapear buckets de valor e horizonte mais recorrentes;
- ordenar prioridades cirúrgicas sem misturar esses casos com as divergências estruturais do benchmark híbrido.
## Regra operacional
Até nova evidência concreta:
- o `proxy v3` continua congelado;
- o benchmark híbrido continua shadow;
- qualquer reabertura futura deve partir primeiro dos padrões concentrados nesta auditoria, e não do benchmark como um todo.
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_CIRURGICA_BLOCO_8500_PICPAY_V131.md`

- Tema classificado: `casos_cirurgicos_lotes`
- Título: Auditoria cirúrgica do bloco 2026-05-13 a 2026-05-20 — V131
- Linhas originais: 121

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria cirúrgica do bloco 2026-05-13 a 2026-05-20 — V131
## Objetivo
Verificar se o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` é realmente superior em patrimônio líquido terminal ou se continua vencendo apenas pela prioridade excessiva dada a déficit/cobertura na métrica lexicográfica central.
## Base auditada
- Baseline de execução: **V130**
- Fonte: `grade_diaria_parametrizada_v130_consolidado.json`
- Janela auditada: **2026-05-13** a **2026-05-20**
- Cenários auditados: **24** (3 por dia)
## Resposta objetiva
**Não.** Neste bloco, o cenário `Lote 8500 mar. -> Combo PicPay 100-120 3m` **não é superior em patrimônio líquido terminal** ao baseline.
Ele continua vencendo na métrica central porque:
1. mantém **o mesmo nível** de `violacoes_protegida`;
2. mantém **o mesmo nível** de `pagamentos_sem_cobertura_integral`;
3. reduz materialmente o `deficit_liquido_total`;
mas, ao mesmo tempo:
4. **piora** a `perda_patrimonio_liquido_terminal` em todos os dias;
5. **piora** o `patrimonio_liquido_terminal_proxy` em todos os dias;
6. aumenta `destruicao_estrategica_lotes` e `custo_fiscal_imediato`.
Portanto, a vitória observada no bloco é **lexicográfica**, não **terminal**.
## Vencedor lexicográfico por dia
| Data       | Vencedor lexicográfico                    | Destino                 |   Δ déficit vs baseline |   Δ perda terminal vs baseline |   Δ patrimônio proxy vs baseline |
|:-----------|:------------------------------------------|:------------------------|------------------------:|-------------------------------:|---------------------------------:|
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`

- Tema classificado: `motor_recomendacao_pagamentos_switching`
- Título: Auditoria cirúrgica do comparador do `motor_recomendacao_pagamentos_switching_v1` — V116
- Linhas originais: 33

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria cirúrgica do comparador do `motor_recomendacao_pagamentos_switching_v1` — V116
## Problema observado na V115
O comparador local estava inflando `switching_simples` porque:
1. reutilizava o mesmo lote em muitos pagamentos futuros como se o saldo continuasse íntegro em cada linha;
2. projetava o ganho do shadow até a data do pagamento sem consumir temporalmente a capacidade do lote já recomendada antes;
3. mantinha o switching competitivo mesmo quando a recomendação local anterior já havia esgotado, na prática, a capacidade do lote no horizonte curto.
## Recalibração aplicada na V116
1. foi introduzido **saldo residual temporal por lote** dentro do motor;
2. o ganho projetado do shadow passou a ser **escalado pela fração residual temporal** do lote;
3. quando `switching_simples` é escolhido, o motor passa a registrar **consumo temporal estimado** e a reduzir o saldo residual do lote para os pagamentos seguintes;
4. quando o lote deixa de sustentar o pagamento localmente, o comparador aciona **fallback automático para `sem_switching`**.
## Efeito observado
### Antes da recalibração
- `sem_switching`: 15
- `switching_simples`: 137
- `ganho_liquido_switching_estimado_total`: 486754.97
### Depois da recalibração
- `sem_switching`: 96
- `switching_simples`: 56
- `ganho_liquido_switching_estimado_total`: 18497.61
- `pagamentos_com_fallback_automatico_sem_switching`: 65
## Interpretação
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`

- Tema classificado: `casos_cirurgicos_lotes`
- Título: Auditoria fina da transição dominante — Lote 3000 mar. B -> Lote 8500 mar.
- Linhas originais: 34

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria fina da transição dominante — Lote 3000 mar. B -> Lote 8500 mar.
## Escopo
Esta auditoria aprofunda **apenas** a transição dominante identificada na V80:
`Lote 3000 mar. B -> Lote 8500 mar.`
Ela **não** altera o fluxo principal, **não** substitui o `proxy v3` e **não** acopla o benchmark híbrido ao motor executável.
## Objetivo
Responder se o sinal concentrado da V80 revela uma hipótese localizada realmente útil para eventual refinamento futuro do `proxy v3`, sem reabrir a decisão monofonte como um todo.
## Resultado observado na V81
- casos auditados: **42**
- transição auditada: **`Lote 3000 mar. B -> Lote 8500 mar.`**
- bucket de valor dominante: **`100-250`**
- bucket de horizonte dominante: **`181-365d`**
- descrição dominante: **`Condomínio`**
- delta médio do score comum do `proxy v3`: **-5.0213**
- delta médio de excesso líquido do benchmark vs. decisão vigente: **-2986.39**
- hipótese fina dominante: **pagamentos pequenos ou médios com horizonte entre 91 e 365 dias**
## Leitura metodológica
O sinal fino continua concentrado em pagamentos pequenos ou médios, principalmente no horizonte intermediário. Isso sugere uma hipótese localizada de eventual ajuste futuro, mas **não** justifica reabertura ampla do `proxy v3`.
## Regra operacional
Até nova evidência concreta:
- o `proxy v3` continua congelado;
- o benchmark híbrido continua shadow;
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_MULTIHORIZONTE_CENARIOS_TEMPO_V125.md`

- Tema classificado: `planejamento_temporal_multihorizonte`
- Título: Auditoria multihorizonte de cenários de tempo — V125
- Linhas originais: 148

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria multihorizonte de cenários de tempo — V125
- Objetivo: ampliar a auditoria temporal do cenário conjunto, saindo dos horizontes isolados de 60/90/120 dias e testando uma grade mais rica de janelas.
- Pergunta central: quais switchings continuam vencedores quando a janela temporal muda de forma relevante, e se essa vitória é material ou apenas marginal.
- Fonte de destinos: `contexto_baseline.ranking_carteira.quadro_destinos_switch`.
- Execução desta auditoria: consolidada a partir de **rodadas segmentadas por horizonte**, para evitar ruído operacional de uma execução monolítica muito pesada no ambiente atual.
## Grade temporal auditada
- 30, 45, 60, 75, 90, 120, 150, 180, 210, 240, 270 e 360 dias.
## Síntese executiva
- O único horizonte com vitória **material** de switching foi **30 dias**, com `Lote 3000 mar. V -> CDB XP 150%`.
- Houve vitórias **marginais** em: `60d`, `75d`, `90d`, `120d`, `150d`, `180d`, `210d` e `360d`.
- O baseline sem switching venceu em: `45d`, `240d` e `270d`.
Achado central: o tempo realmente muda o ranking dos cenários, mas não de forma monotônica. O projeto não mostra uma transição simples do tipo “quanto mais horizonte, mais switching”. O que aparece é um regime instável: um ganho material muito curto, uma longa faixa de ganhos marginais/empates técnicos e janelas em que o baseline volta a dominar.
## Resultado por horizonte
### Horizonte 30 dias
- Janela: `2026-04-20 → 2026-05-20`
- Pagamentos no recorte: `13`
- Switchings elegíveis no planejador: `21`
- Melhor cenário central: `switching_controlado_top2` (`Lote 3000 mar. V -> CDB XP 150%`)
- Leitura: **vitória material**
- Δ perda terminal vs baseline: `-64.83`
- Δ déficit vs baseline: `0.0`
- Δ patrimônio proxy vs baseline: `+130.17`
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_PARAMETROS_PRODUTOS_SWITCHING_V129.md`

- Tema classificado: `parametros_produtos_switching`
- Título: Auditoria de parâmetros de produtos no switching — V129
- Linhas originais: 64

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria de parâmetros de produtos no switching — V129
- Objetivo: verificar se o switching diário está respeitando parâmetros reais dos produtos de destino, em especial ticket mínimo/máximo, antes de continuar a expansão temporal.
- Escopo desta rodada: auditoria estrutural do bug de elegibilidade e reavaliação focal da janela diária crítica de `2026-04-30` a `2026-05-02` usando os 5 produtos mais bem ranqueados da `Carteira`.
## Achado estrutural principal
O fluxo temporal da V128 **não estava considerando corretamente o ticket mínimo do produto de destino**. O problema tinha duas fontes:
1. parsing monetário inconsistente da coluna `Aplicação_Mínima` da aba `Carteira`;
2. geração de cenários vencedores sem validação final do **valor total efetivamente alocado** contra o ticket do destino.
Isso afetava diretamente o caso do `CDB XP 150%`, que vinha aparecendo como destino vencedor mesmo quando o valor migrado não atingia o mínimo de R$ 10.000,00.
## Top 5 destinos ranqueados auditados
| Rank | Produto | Aplicação mínima | Aplicação máxima | Retorno proxy aa | Liquidez | Carência |
|---:|---|---:|---:|---:|---:|---:|
| 1 | Mercado Pago Cofrinho 120% CDI (Meli+) | 1.00 | 10000.00 | 16.80 | 0 | 0 |
| 2 | CDB BMG Escalonado - até 109% CDI - 5 anos | 50.00 | 0.00 | 14.70 | 0 | 0 |
| 3 | CDB Sofisa 105% | 1.00 | 0.00 | 14.70 | 0 | 0 |
| 4 | Combo PicPay 100-120 3m | 300.00 | 0.00 | 16.80 | 0 | 0 |
| 5 | Combo PicPay 100-120 6m | 300.00 | 0.00 | 16.80 | 0 | 0 |
## Evidência concreta do bug da V128 no `CDB XP 150%`
Data auditada: `2026-04-30`.
| Cenário antigo recorrente | Valor migrado estimado | Mínimo do produto | Ticket válido? |
|---|---:|---:|---|
| Lote 3000 mar. V | 3071.88 | 10000.00 | Não |
| Lote 3000 mar. B + Lote 3000 mar. V | 6141.58 | 10000.00 | Não |
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md`

- Tema classificado: `comparacao_proxy_hibrido`
- Título: Auditoria residual das divergências materiais — proxy v3 vs benchmark híbrido shadow
- Linhas originais: 51

<details>
<summary>Trecho inicial preservado</summary>

```text
# Auditoria residual das divergências materiais — proxy v3 vs benchmark híbrido shadow
## Escopo
Esta auditoria residual aprofunda apenas os casos de **divergência material** já identificados na comparação entre a `decisao_local_v1` vigente com `proxy econômico v3` e o benchmark shadow do `resolver_hibrido_5p`.
Ela **não** altera o fluxo principal e **não** substitui automaticamente o `proxy v3`.
## Resultado consolidado da V79
- pagamentos comparados: **152**
- divergências materiais: **113**
- casos classificados como **potencial_reaproveitamento_proxy_v3**: **42**
- casos classificados como **divergência estrutural do benchmark híbrido**: **71**
- casos multifonte no benchmark dentro das divergências materiais: **2**
## Leitura metodológica
A auditoria residual confirma que o benchmark híbrido reduz excesso quase sistematicamente, mas que isso não se traduz, na maioria das divergências materiais, em melhora da métrica comum do `proxy v3`.
Portanto, a divergência do benchmark híbrido deve ser lida principalmente como:
1. **régua externa de auditoria**, útil para mostrar trade-offs de excesso;
2. **fonte de possíveis padrões reaproveitáveis**, mas apenas nos casos em que também melhora a métrica comum do `proxy v3`;
3. **não** como evidência suficiente para substituir a decisão monofonte vigente.
## Padrões residuais principais
### 1. Potencial reaproveitamento no proxy v3
Os casos reaproveitáveis concentram-se onde o benchmark muda o lote principal **e** melhora simultaneamente a métrica comum do `proxy v3` e o excesso líquido.
Na V79, esses casos aparecem sobretudo em transições do tipo:
- `Lote 3000 mar. B -> Lote 8500 mar.`
### 2. Divergência estrutural do benchmark híbrido
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V126.md`

- Tema classificado: `grade_diaria_switching`
- Título: Avaliação diária da data ótima de switching — V126
- Linhas originais: 400

<details>
<summary>Trecho inicial preservado</summary>

```text
# Avaliação diária da data ótima de switching — V126
- Objetivo: testar diariamente, desde D0 até o fim do horizonte, qual é a melhor data de switching por lote e por agrupamento, mantendo a análise conjunta até o fim do período.
- Escopo: lotes já investidos, com comparação entre cenários isolados e agrupados, em modo integral e parcial 50%.
- Observação: esta primeira grade cobre isolado, pares entre os 3 lotes mais promissores do dia e grupo total dos candidatos positivos do dia; não faz busca exaustiva de todos os subconjuntos possíveis.
- Execução pesada: o código foi preparado para rodar em blocos e consolidar a grade diária por partes quando o ambiente interativo não suporta o horizonte completo em uma única passagem.
## Janela auditada
- Data de referência: 2026-04-21
- Janela total teórica do horizonte: 2026-04-21 → 2027-03-31
- Janela efetivamente consolidada nesta auditoria: 2026-04-21 → 2026-05-20
- Quantidade de dias consolidados: 30
- Quantidade de pagamentos futuros no horizonte: 149
- Comparação principal: em cada data, o switching é comparado contra o baseline condicional daquela própria data, após a trajetória sem switching até esse ponto.
## Top global de datas/cenários
- 2026-04-30 | isolado_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8519.91, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 95.4
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 780.23
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V127.md`

- Tema classificado: `grade_diaria_switching`
- Título: Avaliação diária da data ótima de switching — V127
- Linhas originais: 323

<details>
<summary>Trecho inicial preservado</summary>

```text
# Avaliação diária da data ótima de switching — V127
- Objetivo: testar diariamente, desde D0 até o fim do horizonte, qual é a melhor data de switching por lote e por agrupamento, mantendo a análise conjunta até o fim do período.
- Escopo: lotes já investidos e, quando existirem, lotes não aportados disponíveis, com comparação entre cenários individuais e agrupados, sempre em modo integral.
- Observação: a grade diária agora cobre todas as combinações integrais entre as melhores ações por fonte do dia, incluindo fontes não aportadas disponíveis quando existirem.
- Execução pesada: o código foi preparado para rodar em blocos e consolidar a grade diária por partes quando o ambiente interativo não suporta o horizonte completo em uma única passagem.
## Janela auditada
- Data de referência: 2026-04-21
- Janela total teórica do horizonte: 2026-04-21 → 2027-03-31
- Janela efetivamente consolidada nesta auditoria: 2026-04-21 → 2026-06-05
- Quantidade de dias consolidados: 46
- Quantidade de pagamentos futuros no horizonte: 149
- Comparação principal: em cada data, o switching é comparado contra o baseline condicional daquela própria data, após a trajetória sem switching até esse ponto.
## Top global de datas/cenários
- 2026-04-30 | individual_integral | Lote 3000 mar. V
  - vencedor central = True
  - vitória material = True
  - vetor = [64.0, 142855.58, 134.0, 8519.91, 10820.3, 0.0, 29.41, 3.0]
  - Δ perda terminal = 95.4
  - Δ déficit = -500.59
  - Δ protegida = 0.0
  - Δ patrimônio proxy = 780.23
  - eventos = [{'lote_origem_id': 'Lote 3000 mar. V', 'produto_destino': 'CDB XP 150%', 'data_acao': '2026-04-30', 'fracao_lote': 1.0, 'ganho_planejador': 448.52}]
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_DATA_OTIMA_SWITCHING_V128.md`

- Tema classificado: `grade_diaria_switching`
- Título: Avaliação diária da data ótima de switching — V128
- Linhas originais: 315

<details>
<summary>Trecho inicial preservado</summary>

```text
# Avaliação diária da data ótima de switching — V128
- Objetivo: continuar a grade diária integral após `2026-05-20`, mantendo apenas `individual_integral` e `agrupado_integral` com todas as combinações elegíveis e estado recursivo após o switching.
- Leitura correta: a data ótima precisa ser buscada dia a dia; depois do dia da troca, o cenário segue até o fim da janela auditada já com a decisão realizada.
- Contrato vigente nesta entrega: sem parcial; com individual integral, agrupado integral e suporte a não aportado quando elegível.
## Janela auditada nesta consolidação
- Data de referência: 2026-04-21
- Horizonte teórico total da base: 2026-04-21 → 2027-03-31
- Horizonte efetivamente auditado nesta entrega: 2026-04-21 → 2026-08-18
- Dias auditados no total: 120
- Dias com cenários gerados pelo planejador: 46
- Dias sem cenários gerados: 74
- Primeira data com cenários: 2026-04-21
- Última data com cenários: 2026-06-05
- Primeira data vencedora: 2026-04-30
- Última data vencedora: 2026-05-20
- Quantidade de pagamentos futuros no horizonte: 149
## Síntese executiva
- A janela vencedora iniciada em `2026-04-30` permanece dominante no horizonte auditado ampliado.
- Depois de `2026-05-20`, nenhum cenário integral continua vencedor contra o baseline condicional do próprio dia.
- Depois de `2026-06-05`, o planejador deixa de gerar cenários integrais elegíveis nesta grade diária auditada.
- Portanto, no horizonte auditado até aqui, a expansão após `2026-05-20` não deslocou a data ótima inicial; ela apenas confirmou o esgotamento progressivo das oportunidades.
## Regimes observados por faixa temporal
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/AVALIACAO_DIARIA_PARAMETRIZADA_JANELA_V130.md`

- Tema classificado: `grade_diaria_switching`
- Título: Avaliação diária parametrizada da janela crítica — V130
- Linhas originais: 89

<details>
<summary>Trecho inicial preservado</summary>

```text
# Avaliação diária parametrizada da janela crítica — V130
- Objetivo: rerodar a janela `2026-04-30` a `2026-05-20` com parâmetros de produto corrigidos, eliminando falsos positivos de ticket mínimo e máximo.
- Dias auditados: 21.
- Cenários parametrizados simulados: 382.
- Cenários vencedores no cenário conjunto: 211.
## Conclusões centrais
- O bug do `CDB XP 150%` abaixo de R$ 10 mil deixa de contaminar a janela: os cenários individuais e agrupados abaixo do mínimo não entram mais na simulação.
- O `CDB XP 150%` continua aparecendo apenas quando o agrupamento realmente ultrapassa o ticket mínimo do produto.
- A janela vencedora permanece viva após a correção de parâmetros, mas sua composição muda: o curto prazo passa a favorecer mais `Mercado Pago Cofrinho 120% CDI (Meli+)`, `CDB BMG Escalonado - até 109% CDI - 5 anos`, `CDB Sofisa 105%` e os combos PicPay do que o Tesouro como destino dominante.
## Resumo por dia
| Data | Ações elegíveis do planejador | Cenários parametrizados |
|---|---:|---:|
| 2026-04-30 | 25 | 38 |
| 2026-05-01 | 25 | 38 |
| 2026-05-02 | 25 | 38 |
| 2026-05-03 | 25 | 38 |
| 2026-05-04 | 25 | 38 |
| 2026-05-05 | 25 | 39 |
| 2026-05-06 | 25 | 39 |
| 2026-05-07 | 15 | 15 |
| 2026-05-08 | 15 | 15 |
| 2026-05-09 | 15 | 15 |
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/EXPANSAO_MULTIDESTINO_PLANEJADOR_SWITCHING_TEMPORAL_V121.md`

- Tema classificado: `planejamento_temporal_multihorizonte`
- Título: Expansão multidestino do planejador temporal de switching — V121
- Linhas originais: 28

<details>
<summary>Trecho inicial preservado</summary>

```text
# Expansão multidestino do planejador temporal de switching — V121
## Objetivo
Expandir o `planejador_switching_temporal_v1` para comparar múltiplos destinos elegíveis por lote usando o mesmo `ganho_terminal_economico_minimo_estimado` introduzido na V120.
## Componentes incorporados
- lista de destinos elegíveis construída a partir da triagem do motor;
- comparação por lote contra até 12 destinos elegíveis no recorte curto;
- exclusão de destino idêntico ao produto de origem do lote;
- ranqueamento econômico único para todos os destinos testados;
- identificação explícita do melhor destino por lote.
## Resultado no recorte curto
No recorte até 2026-05-20, nenhum destino alternativo permaneceu elegível após a expansão multidestino.
Os melhores destinos por lote ficaram, ainda assim, economicamente negativos:
- `Lote 6630,64 fev.` → `Tesouro Educa+ 2027`: `-2.07`;
- `Lote 3000 mar. B` → `Tesouro Educa+ 2027`: `-8.90`;
- `Lote 3000 mar. V` → `Tesouro Educa+ 2027`: `-9.78`;
- `Lote 8500 mar.` → `Tesouro Educa+ 2027`: `-82.98`;
- `Lote 5680 abr.` → `Tesouro Educa+ 2032`: `-0.70`.
## Interpretação
A V121 mostra que o problema do recorte não era apenas a escolha do destino padrão `Tesouro Educa+ 2032`. Mesmo comparando múltiplos destinos elegíveis, nenhum deles sobreviveu economicamente no recorte curto quando custo fiscal, carência e patrimônio terminal reprojetado foram considerados.
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/GRADE_DIARIA_OFICIAL_HIBRIDA_V133.md`

- Tema classificado: `grade_diaria_switching`
- Título: Grade diária oficial com comparador híbrido — V133
- Linhas originais: 47

<details>
<summary>Trecho inicial preservado</summary>

```text
# Grade diária oficial com comparador híbrido — V133
- Objetivo: integrar o `comparador_hibrido_switching_v1` ao fluxo oficial da grade diária, para que o melhor cenário do dia seja emitido como `vencedor terminal`, `vencedor híbrido aceitável` ou `baseline`, sem promoção automática de `vencedor operacional`.
- Dias auditados: 21
- Resultados avaliados: 382
- Dias com vencedor lexicográfico bloqueado: 21
- Dias promovidos com switching: 5
- Dias promovidos com baseline: 16
- Dias em que a promoção oficial diferiu do vencedor lexicográfico: 5
## Contagem das classes oficiais promovidas
- vencedor_terminal: 5
## Melhor cenário oficial por dia
| Data | Vencedor lexicográfico | Classe lex | Bloqueado | Melhor cenário oficial | Classe oficial | Origem | Δ perda terminal | Δ déficit | Δ patrimônio proxy |
|---|---|---|---|---|---|---|---:|---:|---:|
| 2026-04-30 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -234.56 | -450.12 | 2167.56 |
| 2026-05-01 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -228.79 | -450.12 | 2156.02 |
| 2026-05-02 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -223.02 | -450.12 | 2144.48 |
| 2026-05-03 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -217.25 | -450.12 | 2132.94 |
| 2026-05-04 | Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | Lote 3000 mar. B + Lote 3000 mar. V + Lote 8500 mar. -> CDB XP 150% | vencedor_terminal | comparador_hibrido | -211.48 | -450.12 | 2121.40 |
| 2026-05-05 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-06 | Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+) | vencedor_operacional | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-07 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
| 2026-05-08 | Lote 3000 mar. B -> CDB BMG Escalonado - até 109% CDI - 5 anos | dominado_pelo_baseline | Sim | baseline_sem_switching | baseline | baseline | 0.00 | 0.00 | 0.00 |
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md`

- Tema classificado: `auditoria_temporal_geral`
- Título: Integração funcional mínima V117/V121 — recorte curto
- Linhas originais: 128

<details>
<summary>Trecho inicial preservado</summary>

```text
# Integração funcional mínima V117/V121 — recorte curto
- Data de referência: 2026-04-21
- Horizonte: {'data_inicio': '2026-04-21', 'data_fim': '2026-05-21'}
- Critério do planejador temporal: ganho_terminal_economico_minimo_estimado
- Destinos elegíveis considerados por lote: 12
- Candidatos elegíveis de switching: 20
- Melhor cenário atual: switching_temporal_top2
- Vetor lexicográfico: (0.0, 0.0, 0.0, 48.99, 9699.45, 0.0, 29.41, 5.0)
## Melhor destino por lote
### Lote 3000 mar. B
- Melhor destino no recorte: CDB XP 150%
- Rank do destino: 8
- Elegível: True
- Ganho terminal econômico mínimo estimado: 19.08
- Patrimônio terminal origem estimado: 3099.09
- Patrimônio terminal destino estimado: 3118.17
- Custo fiscal estimado: 28.52
- Penalidade carência reprojetada: 0.0
### Lote 3000 mar. V
- Melhor destino no recorte: CDB XP 150%
- Rank do destino: 8
- Elegível: True
```

</details>

### `relatorios/historico/auditorias_especificas/temporal/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md`

- Tema classificado: `motor_recomendacao_pagamentos_switching`
- Título: Motor recomendação pagamentos + switching V114
- Linhas originais: 35

<details>
<summary>Trecho inicial preservado</summary>

```text
# Motor recomendação pagamentos + switching V114
## Papel da V114
A V114 não substitui a baseline principal da frente central (**V108**). Ela adiciona uma camada operacional orientada à pergunta prática do projeto:
> qual lote usar para pagar cada conta e quando vale fazer switching antes do pagamento?
## Estratégias comparadas por conta
Para cada pagamento futuro, o motor compara três famílias:
1. **sem switching**: usar a recomendação central atual sem realocação prévia;
2. **switching simples**: aplicar oportunidade shadow elegível da fonte/lote antes do pagamento;
3. **combinação mínima**: combinar fonte principal e fonte reserva quando isso melhora cobertura.
## Saída operacional principal
A saída central da V114 é um quadro por conta com:
- estratégia recomendada;
- lote recomendado;
- lote reserva;
- necessidade de switching;
- data sugerida;
- origem e destino do switching;
- ganho líquido estimado do switching;
- cobertura esperada;
- motivo da recomendação.
## Governança
- a V108 continua como baseline principal da frente central;
```

</details>

## Decisão sugerida

Após esta consolidação, `relatorios/historico/auditorias_especificas/temporal/` pode ser removida se os documentos granulares não tiverem autoridade ativa superior aos documentos atuais e se o relatório consolidado preservar os achados principais.

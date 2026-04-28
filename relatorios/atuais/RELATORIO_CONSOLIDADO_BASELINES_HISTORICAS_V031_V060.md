# Relatório consolidado — baselines históricas V031–V060

## Objetivo

Consolidar a faixa de baselines históricas `V031_V060`, preservando a evolução de valuation, replay, CDI/cache, situação atual, planilha operacional, saneamento documental e início da Frente F1, sem remover ainda os arquivos granulares de `relatorios/historico/baselines/`.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 21
- Faixa: V031–V060
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das baselines

| Versão | Classe preliminar | Linhas | Título |
|---:|---|---:|---|
| V31 | `BASELINE_RELEVANTE` | 35 | BASELINE FIXA V31 |
| V32 | `BASELINE_RELEVANTE` | 47 | BASELINE FIXA V32 |
| V33 | `BASELINE_RELEVANTE` | 36 | BASELINE FIXA V33 |
| V34 | `BASELINE_RELEVANTE` | 42 | BASELINE FIXA V34 |
| V35 | `BASELINE_RELEVANTE` | 58 | BASELINE FIXA V35 |
| V36 | `BASELINE_RELEVANTE` | 51 | BASELINE FIXA V36 |
| V37 | `BASELINE_RELEVANTE` | 41 | BASELINE FIXA V37 |
| V38 | `BASELINE_RELEVANTE` | 22 | BASELINE FIXA V38 |
| V39 | `BASELINE_RELEVANTE` | 40 | BASELINE FIXA V39 |
| V40 | `BASELINE_RELEVANTE` | 25 | BASELINE FIXA V40 |
| V41 | `BASELINE_RELEVANTE` | 12 | Baseline fixa V41 |
| V42 | `BASELINE_RELEVANTE` | 13 | Baseline fixa V42 |
| V45 | `BASELINE_RELEVANTE` | 14 | Baseline fixa V45 |
| V48 | `BASELINE_RELEVANTE` | 12 | BASELINE FIXA V47 |
| V50 | `BASELINE_RELEVANTE` | 13 | Baseline fixa V50 |
| V51 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V51 |
| V52 | `BASELINE_RELEVANTE` | 23 | Baseline fixa V52 |
| V55 | `BASELINE_RELEVANTE` | 36 | Baseline fixa V55 |
| V58 | `BASELINE_RELEVANTE` | 36 | Baseline fixa V58 |
| V59 | `MARCO_CHAVE_PROVAVEL` | 29 | Baseline fixa V59 |
| V60 | `MARCO_CHAVE_PROVAVEL` | 28 | Baseline fixa V60 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Valuation e data de referência | Correções da convenção de valuation e uso controlado de fator CDI foram preservadas. |
| Replay e resíduos | Auditorias/correções de resíduos, arredondamentos, exaustão e lotes históricos foram consolidadas. |
| Situação atual | Evolução da exibição de lotes ativos/exauridos, bruto/líquido e fechamento econômico foi preservada. |
| Planilha operacional | Consolidação das abas operacionais e limpeza de saída foram registradas. |
| Governança e F1 | Saneamento documental, release checker e abertura inicial da Frente F1 foram preservados. |

## Detalhe por baseline

### V31 — `relatorios\historico\baselines\BASELINE_FIXA_V31.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 35
- Título: BASELINE FIXA V31

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V31
Derivada da V30 para corrigir a convenção de valuation da baseline.
## Escopo aberto nesta versão
- fechamento completo da posição na data de referência;
- fallback controlado do último fator CDI disponível quando o cache não contém o próprio dia da referência;
- extensão dos lotes remanescentes do replay até a data de referência completa;
- reauditoria dos lotes críticos contra os apps;
- reauditoria dos lotes residuais;
- teste de `-1 dia de rendimento` após a correção temporal.
## Ajustes implementados
1. A capitalização diária passou a aceitar fechamento controlado da data de referência com reaproveitamento do último fator CDI disponível.
2. A contagem de dias de rendimento passou a aceitar a mesma convenção de fechamento da referência.
3. O núcleo financeiro mínimo passou a auditar explicitamente o fechamento da referência completa.
4. O replay controlado do passado passou a carregar os lotes remanescentes até a data de referência completa, sem truncar no último evento histórico.
5. O console passou a mostrar:
   - auditoria crítica vs. app com deltas consolidados;
   - amostra do fechamento da referência via fallback CDI;
   - reauditoria dos lotes residuais;
```

</details>

### V32 — `relatorios\historico\baselines\BASELINE_FIXA_V32.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 47
- Título: BASELINE FIXA V32

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V32
Derivada da V31 para aprofundar a auditoria dos resíduos de saque/arredondamento sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.
## Ajustes desta derivação
- fixação explícita de `execucao.data_referencia_simulacao = 2026-04-15` em `dados/config_atualizado.json` para manter a auditoria alinhada às referências dos apps;
- ampliação da auditoria no console com uma nova seção de rastreamento causal dos resíduos no nível do evento histórico;
- manutenção da convenção temporal já corrigida na V31.
## Resultado consolidado da auditoria dos resíduos
### Contas parcialmente cobertas
- `despesa_auto_00014` (`Escola`, 2026-03-13): faltam `R$ 0,68` porque o `Lote 10342 fev.` foi totalmente zerado no evento e o líquido máximo disponível do lote na data foi `R$ 1.367,44`;
- `despesa_auto_00037` (`Cartão Azul`, 2026-03-20): faltam `R$ 0,71` porque o `Lote 5400 fev.` foi totalmente zerado no evento e o líquido máximo disponível do lote na data foi `R$ 4.539,84`.
Leitura: esses dois casos não indicam mais problema de convenção temporal. O déficit aparece no próprio evento histórico de saque e é compatível com teto líquido do lote no esgotamento.
### Micro-saldos remanescentes
#### Remanescente por rendimento histórico
- `Lote 3600 abr.` → `R$ 3,19`
- `Lote 7800 abr.` → `R$ 0,09`
Leitura: ambos são lotes históricos marcados como `nao_aportado_exaurido` que ainda acumularam rendimento até o último uso. O resíduo não nasce do fechamento temporal global.
#### Saldo residual após saque líquido-alvo
- `Lote 4000 fev.` → `R$ 0,49`
```

</details>

### V33 — `relatorios\historico\baselines\BASELINE_FIXA_V33.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 36
- Título: BASELINE FIXA V33

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V33
Derivada da V32 para incorporar o limiar operacional aprovado de `R$ 0,20` na auditoria dos resíduos, sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.
## Ajustes desta derivação
- inclusão explícita de `auditoria.limiar_residuo_resolvido = 0.20` em `dados/config_atualizado.json`;
- atualização de `replay.valor_minimo_lote_ativo = 0.20` para alinhar a noção de lote residual ativo ao limiar operacional aprovado nesta fase;
- reclassificação automática dos resíduos `<= R$ 0,20` como `resolvido por limiar` na auditoria;
- ampliação das tabelas de auditoria para explicitar `data`, `conta` e `lote` dos resíduos ainda pendentes de validação.
## Resultado consolidado após aplicar o limiar
### Resíduos resolvidos por limiar (`<= R$ 0,20`)
- `Lote 7800 abr.` → `R$ 0,09` | último evento: `2026-04-06` | conta: `Faxina Rosa`
- `Lote 2063,11 fev.` → `R$ 0,04` | último evento: `2026-02-09` | conta: `Cartão Azul`
Leitura: esses dois casos passaram a ficar formalmente resolvidos pela regra operacional aprovada, sem necessidade de nova intervenção analítica nesta etapa.
### Resíduos pendentes para validação (`> R$ 0,20`)
#### Contas parcialmente cobertas
- `2026-03-20` | conta `Cartão Azul` | lote `Lote 5400 fev.` | referência `despesa_auto_00037` | resíduo `R$ 0,71`
- `2026-03-13` | conta `Escola` | lote `Lote 10342 fev.` | referência `despesa_auto_00014` | resíduo `R$ 0,68`
Leitura: ambos seguem compatíveis com `teto líquido do lote no esgotamento`.
#### Micro-saldos ainda pendentes
```

</details>

### V34 — `relatorios\historico\baselines\BASELINE_FIXA_V34.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 42
- Título: BASELINE FIXA V34

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V34
Derivada da V33 para aplicar a correção cirúrgica aprovada apenas à classe de lotes históricos `nao_aportado_exaurido`, sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.
## Ajuste desta derivação
- correção da criação de lotes para **preservar taxa explícita igual a `0.0`**, em vez de convertê-la implicitamente para `1.0`;
- efeito prático esperado: lotes históricos `nao_aportado_exaurido` deixam de acumular rendimento indevido no replay;
- nenhuma mudança de regra foi aplicada aos lotes aportados ativos nem à lógica geral de saque.
## Causa raiz encontrada
Os lotes históricos `nao_aportado_exaurido` já eram materializados com `taxa_base_cdi = 0.0`, mas esse zero era perdido na criação do objeto `Lote`, sendo tratado como falsy e substituído por `1.0`.
Isso fazia com que alguns lotes históricos marcados com `Investimento = '-'` ainda rendessem durante o replay, produzindo micro-saldos artificiais.
## Resultado consolidado após a correção
### Casos estruturalmente resolvidos
- `Lote 3600 abr.` → deixou de aparecer como micro-saldo residual de `R$ 3,19`;
- `Lote 7800 abr.` → deixou de aparecer como micro-saldo residual de `R$ 0,09`.
Leitura: os dois casos foram eliminados na origem, sem uso de limiar operacional adicional.
### Resíduos remanescentes após a correção
#### Resolvido por limiar (`<= R$ 0,20`)
- `Lote 2063,11 fev.` → `R$ 0,04`
#### Pendentes para validação (`> R$ 0,20`)
```

</details>

### V35 — `relatorios\historico\baselines\BASELINE_FIXA_V35.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 58
- Título: BASELINE FIXA V35

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V35
Derivada da V34 para aplicar uma correção cirúrgica apenas na transição de taxa bônus para taxa base dos lotes aportados com `Dias_Bonus > 0`, sem abrir solver, switching econômico, score econômico final, relatório financeiro atual ou engine completa.
## Ajuste desta derivação
- a regra de `get_taxa_dia()` deixou de cortar a taxa bônus imediatamente quando `data_base_fiscal + dias_bonus` cai em fim de semana/feriado bancário;
- a nova convenção preserva a taxa bônus no **primeiro dia útil de rendimento** imediatamente posterior ao fim da janela corrida, apenas quando a virada ocorre em dia sem rendimento;
- a regra geral dos lotes sem bônus e dos lotes cuja virada já ocorre em dia útil foi mantida.
## Causa raiz encontrada
A V34 tratava a virada `taxa_bonus_cdi -> taxa_base_cdi` apenas por `idade < dias_bonus`, em dias corridos puros.
No `Lote 5400 fev.`, isso fazia a taxa bônus morrer cedo demais:
- data base fiscal: `2026-02-05`
- `Dias_Bonus`: `30`
- data de corte corrida: `2026-03-07`
- `2026-03-07` caiu em sábado
- o primeiro dia útil de rendimento posterior foi `2026-03-09`
Sem a extensão operacional até `2026-03-09`, o lote chegava subcapitalizado ao resgate de `2026-03-20`.
## Resultado consolidado desta correção
### Revalidação do `Lote 5400 fev.`
#### Evento 1 — `2026-03-13` — `Escola`
```

</details>

### V36 — `relatorios\historico\baselines\BASELINE_FIXA_V36.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 51
- Título: BASELINE FIXA V36

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V36
## Escopo desta derivação
A V36 parte da V35 e aplica apenas correções cirúrgicas necessárias para:
1. aceitar a nova base `dados/dados_financeiros.xlsx` enviada pelo usuário;
2. robustecer a leitura de datas vazias/`NaT` no inventário de lotes;
3. corrigir a indexação regressiva do IOF para resgates curtos;
4. reauditar o `Lote 10342 fev.` com a nova planilha e comparar os eventos críticos contra os comprovantes do app.
## Alterações implementadas
### 1. Leitura robusta de datas vazias
Arquivo: `nucleo/utilitarios_neutros.py`
- `para_data(...)` agora testa `pd.isna(valor)` antes de tratar o valor como `date`/`datetime`.
- Isso evita que `pandas.NaT` seja propagado como data válida e quebre a classificação dos lotes futuros da nova planilha.
### 2. Correção da indexação da tabela regressiva do IOF
Arquivo: `nucleo/nucleo_financeiro_minimo.py`
- a função `_taxa_iof(dias, ...)` passou a usar `dias - 1` como índice efetivo da tabela;
- isso alinha a leitura com a convenção econômica da tabela regressiva brasileira, em que o primeiro dia usa a primeira linha (96%), o sétimo dia usa a sétima linha (76%) etc.;
- o mapeamento anterior subestimava o IOF em resgates curtos.
## Resultado principal da reauditoria
```

</details>

### V37 — `relatorios\historico\baselines\BASELINE_FIXA_V37.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 41
- Título: BASELINE FIXA V37

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V37
## Escopo desta derivação
Esta derivação consolida quatro ajustes operacionais sobre a baseline V36:
1. leitura da nova coluna `Data Recebimento` na aba `Inventário de Lotes`;
2. separação entre **data de recebimento** e **data de aplicação** para o replay histórico;
3. retorno da **data de referência dinâmica** para a data atual da execução;
4. limpeza da saída do console, priorizando apenas auditorias ainda ativas.
## Regra operacional nova
Quando um lote possui `Data Recebimento < Data Aplicação`:
- o lote fica **disponível para pagamentos** a partir de `Data Recebimento`;
- até `Data Aplicação` inclusive, ele é tratado como **caixa pré-aplicação**, sem rendimento e sem tributação de investimento;
- o rendimento do produto começa apenas **após** a data de aplicação;
- a carência do produto passa a bloquear resgates apenas **depois** da data de aplicação.
## Caso motivador
### `Lote 5680 abr.`
- recebimento: `2026-04-06`
- aplicação: `2026-04-14`
- produto: `CDB Neon Planejado 150% CDI - 60 dias`
```

</details>

### V38 — `relatorios\historico\baselines\BASELINE_FIXA_V38.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 22
- Título: BASELINE FIXA V38

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V38
## Escopo desta derivação
Esta derivação consolida a formalização documental da regra geral introduzida na V37 para lotes com `Data Recebimento` e `Data Aplicação` distintas.
## Texto canônico oficial da regra
> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.
## Uso documental
Este texto deve ser tratado como a formulação oficial curta da baseline para:
- relatórios de auditoria;
- README operacional;
- documentação de regras ativas do replay histórico;
- futuras referências sobre disponibilidade temporal de lotes.
## Observação operacional
A regra acima não é específica do `Lote 5680 abr.`. Ela passa a valer como convenção geral do projeto para qualquer lote em que o recebimento anteceda a aplicação.
```

</details>

### V39 — `relatorios\historico\baselines\BASELINE_FIXA_V39.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 40
- Título: BASELINE FIXA V39

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V39
## Escopo desta derivação
Esta derivação consolida uma limpeza documental mais ampla do repositório, sem abrir nova frente econômica nem alterar a lógica financeira já estabilizada na V38.
## Objetivos da limpeza documental
- separar de forma explícita a documentação **vigente** da documentação **histórica**;
- reduzir ruído no diretório `relatorios/`;
- manter a trilha de evolução documental sem perder rastreabilidade;
- alinhar o `README.md`, o contrato operacional e o índice de relatórios à estrutura atual;
- remover artefatos temporários proibidos do pacote final.
## Estrutura documental oficial a partir da V39
- `relatorios/atuais/`
  - documentos vigentes da baseline atual;
  - contrato operacional vigente;
  - validação local mais recente.
- `relatorios/historico/baselines/`
  - versões anteriores de baseline fixa.
- `relatorios/historico/validacoes/`
  - validações locais de versões anteriores.
```

</details>

### V40 — `relatorios\historico\baselines\BASELINE_FIXA_V40.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 25
- Título: BASELINE FIXA V40

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V40
## Escopo desta derivação
Esta derivação consolida uma limpeza adicional da saída operacional do script, reorganiza a apresentação do console, aplica o filtro de materialidade diretamente na tabela de inconsistências do replay e gera a planilha operacional com as abas `Extrato passado`, `Extrato futuro`, `Melhores produtos` e `Situação atual`.
## Ajustes operacionais consolidados
- remoção, da saída principal do console, das auditorias já encerradas de:
  - lotes vs. app;
  - recebimento vs. aplicação;
  - lotes residuais;
- reordenação do `RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS` para logo após a leitura das abas;
- separação dos `Top produtos selecionados` em seção própria no console;
- filtro da tabela de inconsistências do replay para exibir apenas itens **materiais acima do limiar operacional**;
- inclusão da tabela final de lotes ativos com recebimento, aplicação, produto, dias, bruto, líquido e saldo remanescente;
- geração da planilha operacional `.xlsx` em `saidas/relatorio_operacional_v40.xlsx`.
## Regra operacional consolidada
A tabela de inconsistências do replay controlado deve refletir apenas inconsistências materiais acima do limiar operacional vigente. Itens residuais abaixo ou iguais ao limiar continuam registrados internamente para auditoria, mas não devem poluir a saída principal do console nem acionar alerta operacional de inconsistência material.
## Regra canônica mantida da baseline
> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.
```

</details>

### V41 — `relatorios\historico\baselines\BASELINE_FIXA_V41.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 12
- Título: Baseline fixa V41

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V41
## Escopo
A V41 consolida a auditoria da seção **Situação atual — lotes ativos** para eliminar divergência entre console, planilha operacional e cálculo interno.
## Ajustes desta versão
- a tabela de lotes ativos passou a recalcular `Bruto` e `Líquido` explicitamente na `data_referência`, usando `valor_bruto_em_data(...)` e `valor_liquido_em_data(...)`;
- a coluna `Valor original` foi adicionada ao console e à aba `Situação atual`;
- a planilha operacional passou a ser gerada como `relatorio_operacional_v41.xlsx`.
## Regra operacional mantida
A data de referência continua sendo a data atual da execução, com fallback controlado do último fator CDI disponível quando o cache não contiver o próprio dia.
```

</details>

### V42 — `relatorios\historico\baselines\BASELINE_FIXA_V42.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 13
- Título: Baseline fixa V42

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V42
## Escopo
A V42 corrige a divergência da seção **Situação atual — lotes ativos** quando o cache CDI já contém o fator do fechamento útil imediatamente anterior à data de referência.
## Ajustes desta versão
- a situação atual passou a usar uma **data econômica efetiva** para exibição dos lotes ativos;
- quando a série CDI já alcança o fechamento útil imediatamente anterior à data de referência, a saída deixa de extrapolar um dia adicional sobre a data corrente;
- quando a série CDI ainda está atrasada em relação a esse fechamento útil, a saída mantém a foto já bridged pelo fallback anterior;
- a regra foi aplicada tanto no console quanto na aba `Situação atual` da planilha operacional.
## Regra operacional desta versão
A data de referência continua sendo a data atual da execução para contexto operacional. A exibição da **Situação atual** usa a última foto econômica coerente com o fechamento útil disponível, evitando acréscimo indevido de um dia adicional de rendimento quando o cache já contém o último fechamento útil.
```

</details>

### V45 — `relatorios\historico\baselines\BASELINE_FIXA_V45.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 14
- Título: Baseline fixa V45

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V45
## Escopo
A V45 não abre novas camadas econômicas do projeto. Ela saneia o contrato operacional para refletir apenas o que já é executável na baseline e separa, em documento próprio, o backlog contratual das fases futuras.
## Ajustes desta versão
- revisão cirúrgica do contrato operacional vigente;
- remoção de resíduos históricos e metas futuras do contrato executável;
- criação do arquivo `BACKLOG_CONTRATUAL_FASES_FUTURAS.md` para itens ainda não cobráveis da baseline atual;
- atualização do `README.md` e do índice documental para refletir a nova separação;
- atualização da versão exibida pela baseline para `V45`.
## Regra operacional desta versão
A baseline atual deve ser lida com dois níveis documentais distintos: o contrato executável da baseline vigente e o backlog contratual das fases futuras. Itens futuros só voltam ao contrato executável quando estiverem implementados e validados.
```

</details>

### V48 — `relatorios\historico\baselines\BASELINE_FIXA_V48.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 12
- Título: BASELINE FIXA V47

<details>
<summary>Trecho inicial preservado</summary>

```text
# BASELINE FIXA V47
## Objetivo da derivação
Atualizar a baseline V46 com o novo arquivo `dados/cache_bcb.json` enviado pelo usuário e revalidar a situação atual dos lotes com a série CDI mais recente disponível no repositório.
## Mudança principal
- substituição de `dados/cache_bcb.json` pela nova versão com atualização em `2026-04-16` e fator diário disponível até `2026-04-15`;
- manutenção da regra de data de referência corrente com fallback controlado do último fator CDI disponível;
- regeneração da planilha operacional em `saidas/relatorio_operacional_v47.xlsx`.
## Leitura operacional
Com o novo cache, a foto econômica da situação atual passa a considerar mais um dia útil de rendimento para os lotes em aberto quando comparada ao cache anterior, o que afeta principalmente os lotes ainda ativos de fevereiro, março e abril.
```

</details>

### V50 — `relatorios\historico\baselines\BASELINE_FIXA_V50.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 13
- Título: Baseline fixa V50

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V50
A V50 explicita no núcleo financeiro a convenção operacional adotada para rendimento de lotes:
- **dia 0** = data de aplicação, sem rendimento do lote;
- **dia 1 em diante** = o lote já pode render, conforme a série CDI disponível e as regras do produto.
A alteração foi incorporada de forma contextual ao lote, evitando que o dia da aplicação seja marcado ou tratado como dia econômico de rendimento.
## Ajuste V50
A geração da auditoria diária do lote passou a alinhar `Dia rendimento`, `Dias úteis` e `Dias úteis efetivos` à mesma convenção econômica da série CDI.
```

</details>

### V51 — `relatorios\historico\baselines\BASELINE_FIXA_V51.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V51

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V51
A V51 explicita no núcleo financeiro a convenção operacional adotada para rendimento de lotes:
- **dia 0** = data de aplicação, sem rendimento do lote;
- **dia 1 em diante** = o lote já pode render, conforme a série CDI disponível e as regras do produto.
A alteração foi incorporada de forma contextual ao lote, evitando que o dia da aplicação seja marcado ou tratado como dia econômico de rendimento.
## Ajuste V51
A geração da auditoria diária do lote passou a alinhar `Dia rendimento`, `Dias úteis` e `Dias úteis efetivos` à mesma convenção econômica da série CDI.
## Ajuste V51
- reorganização da saída do console: núcleo financeiro e replay controlado divididos em seções de resumo/valuation e amostras; observações da carteira canônica movidas para seção própria.
```

</details>

### V52 — `relatorios\historico\baselines\BASELINE_FIXA_V52.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 23
- Título: Baseline fixa V52

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V52
A V52 explicita no núcleo financeiro a convenção operacional adotada para rendimento de lotes:
- **dia 0** = data de aplicação, sem rendimento do lote;
- **dia 1 em diante** = o lote já pode render, conforme a série CDI disponível e as regras do produto.
A alteração foi incorporada de forma contextual ao lote, evitando que o dia da aplicação seja marcado ou tratado como dia econômico de rendimento.
## Ajuste V52
A geração da auditoria diária do lote passou a alinhar `Dia rendimento`, `Dias úteis` e `Dias úteis efetivos` à mesma convenção econômica da série CDI.
## Ajuste V52
- reorganização da saída do console: núcleo financeiro e replay controlado divididos em seções de resumo/valuation e amostras; observações da carteira canônica movidas para seção própria.
## Ajuste V52
A seção `Situação atual — lotes ativos` foi dividida em duas tabelas: uma para identificação/tempo e outra para valores atuais.
```

</details>

### V55 — `relatorios\historico\baselines\BASELINE_FIXA_V55.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 36
- Título: Baseline fixa V55

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V55
## Objetivo desta versão
Reorganizar estruturalmente todo o repositório sem alterar a base funcional vigente.
## Reorganização aplicada
- separação do ponto de entrada principal em `aplicacao/console/`;
- separação dos scripts por responsabilidade em:
  - `scripts/operacional/`
  - `scripts/auditoria/`
  - `scripts/diagnostico/`
- manutenção de wrappers de compatibilidade nos caminhos antigos:
  - `aplicacao/principal.py`
  - `scripts/gerar_planilha_operacional.py`
  - `scripts/gerar_auditoria_diaria_lote.py`
  - `scripts/inspecionar_base.py`
- centralização das saídas operacionais em `saidas/operacional/`;
- limpeza da documentação vigente em `relatorios/atuais/`, mantendo no diretório atual apenas:
  - contrato operacional executável
  - backlog contratual futuro
```

</details>

### V58 — `relatorios\historico\baselines\BASELINE_FIXA_V58.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 36
- Título: Baseline fixa V58

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V58
## Objetivo desta versão
Derivar a V57 de forma cirúrgica para retirar a auditoria comparativa contra app do fluxo executável e tornar auditável o uso de fallback CDI na situação atual, sem alterar o motor financeiro.
## Reorganização aplicada
- centralização da montagem da baseline em `nucleo/contexto_baseline.py`;
- centralização da identidade da versão e dos nomes de artefatos em `nucleo/identidade_baseline.py`;
- extração do helper de leitura do config em `nucleo/config_utils.py`;
- modularização do console em:
  - `aplicacao/console/common.py`
  - `aplicacao/console/secoes_execucao.py`
  - `aplicacao/console/secoes_canonicas.py`
  - `aplicacao/console/secoes_financeiras.py`
  - `aplicacao/console/secoes_triagem.py`
- manutenção dos wrappers de compatibilidade antigos;
- remoção de resíduos de versionamento hardcoded e do código morto `_resolver_data_economica_situacao_atual`.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V58.
## Critério desta baseline
```

</details>

### V59 — `relatorios\historico\baselines\BASELINE_FIXA_V59.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 29
- Título: Baseline fixa V59

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V59
## Objetivo desta versão
Derivar a V58 de forma cirúrgica para consolidar a higiene operacional/documental da baseline, remover resíduos estruturais do fluxo antigo e adicionar uma checagem mínima automática de release, sem alterar o motor financeiro.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- remoção do ramo residual `menos_1_dia` em `nucleo/contexto_baseline.py`;
- atualização do mapa documental vigente em `relatorios/INDICE_RELATORIOS.md`;
- criação da checagem mínima automática de release em `scripts/diagnostico/verificar_release_baseline.py`;
- manutenção dos wrappers de compatibilidade antigos;
- limpeza da entrega para evitar artefatos efêmeros e saídas redundantes de versões anteriores.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V59.
## Critério desta baseline
A V59 preserva a matemática já validada dos lotes, do replay e da planilha operacional, mas fecha a governança mínima da release para deixar a baseline atual limpa, consistente e auditável como artefato oficial.
## Atualização V59
- limpeza de artefatos efêmeros (`__pycache__` e `.pyc`) do pacote final;
- atualização da documentação vigente para a versão atual;
- remoção do código morto residual associado ao fluxo `menos_1_dia`;
```

</details>

### V60 — `relatorios\historico\baselines\BASELINE_FIXA_V60.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 28
- Título: Baseline fixa V60

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V60
## Objetivo desta versão
Derivar a V59 de forma cirúrgica para abrir apenas a **Etapa 1 da Frente F1**, formalizando o contrato mínimo da nova camada de caixa/recebidos auditáveis e tornando essa etapa observável por documentação e script diagnóstico, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/caixa_recebidos_auditaveis.py` com as estruturas canônicas mínimas da F1;
- criação do script `scripts/diagnostico/inspecionar_contrato_f1.py` e do wrapper `scripts/inspecionar_contrato_f1.py`;
- atualização da documentação vigente para registrar a abertura parcial da F1.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V60. A F1, nesta etapa, é apenas contratual/diagnóstica e não altera console principal, planilha operacional, replay ou valuation.
## Critério desta baseline
A V60 preserva a baseline limpa da V59 e abre somente a camada contratual mínima da F1. O objetivo é criar a base estável para que as próximas etapas possam materializar caixa/recebidos auditáveis e, depois, a decisão local v1 entre saldo disponível e resgate.
## Atualização V60
- formalização da V59 como baseline oficial da nova fase de trabalho;
- manutenção do release checker como gate obrigatório;
- abertura parcial da F1 com contrato mínimo observável;
- inclusão de estruturas canônicas para `fonte_elegivel_pagamento`, `recebido_auditavel` e `decisao_local_v1`.
```

</details>

## Decisão desta etapa

A faixa V031–V060 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de baselines sejam consolidadas e um índice-mestre final seja criado.

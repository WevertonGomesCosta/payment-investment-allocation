# Relatório consolidado — baselines históricas V061–V090

## Objetivo

Consolidar a faixa de baselines históricas `V061_V090`, preservando a evolução da Frente F1, fontes elegíveis, saldo disponível, decisão local, proxy econômico v2/v3, benchmarks shadow, absorção legado, switching econômico shadow e governança documental, sem remover ainda os arquivos granulares.

## Regra de autoridade documental

Este relatório tem valor histórico e de rastreabilidade. Ele não substitui a documentação vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Arquivos consolidados nesta faixa: 28
- Faixa: V061–V090
- Nenhum arquivo granular foi removido nesta etapa.

## Síntese das baselines

| Versão | Classe preliminar | Linhas | Título |
|---:|---|---:|---|
| V61 | `BASELINE_RELEVANTE` | 29 | Baseline fixa V61 |
| V62 | `BASELINE_RELEVANTE` | 29 | Baseline fixa V62 |
| V63 | `BASELINE_RELEVANTE` | 29 | Baseline fixa V63 |
| V64 | `MARCO_CHAVE_PROVAVEL` | 37 | Baseline fixa V64 |
| V65 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V65 |
| V66 | `MARCO_CHAVE_PROVAVEL` | 31 | Baseline fixa V66 |
| V67 | `MARCO_CHAVE_PROVAVEL` | 31 | Baseline fixa V67 |
| V68 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V68 |
| V69 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V69 |
| V71 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V71 |
| V72 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V72 |
| V73 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V73 |
| V74 | `MARCO_CHAVE_PROVAVEL` | 30 | Baseline fixa V74 |
| V75 | `MARCO_CHAVE_PROVAVEL` | 23 | Baseline fixa V75 |
| V76 | `MARCO_CHAVE_PROVAVEL` | 28 | Baseline fixa V76 |
| V77 | `MARCO_CHAVE_PROVAVEL` | 41 | Baseline fixa V77 |
| V78 | `MARCO_CHAVE_PROVAVEL` | 48 | Baseline fixa V78 |
| V79 | `MARCO_CHAVE_PROVAVEL` | 53 | Baseline fixa V79 |
| V80 | `BASELINE_RELEVANTE` | 21 | Baseline fixa V80 |
| V82 | `BASELINE_RELEVANTE` | 21 | Baseline fixa V82 |
| V83 | `BASELINE_RELEVANTE` | 21 | Baseline fixa V83 |
| V84 | `BASELINE_RELEVANTE` | 24 | Baseline fixa V84 |
| V85 | `BASELINE_RELEVANTE` | 24 | Baseline fixa V85 |
| V86 | `BASELINE_RELEVANTE` | 24 | Baseline fixa V86 |
| V87 | `BASELINE_RELEVANTE` | 24 | Baseline fixa V88 |
| V88 | `BASELINE_RELEVANTE` | 24 | Baseline fixa V88 |
| V89 | `BASELINE_RELEVANTE` | 28 | Baseline fixa V89 |
| V90 | `BASELINE_RELEVANTE` | 18 | Baseline fixa V90 |

## Leitura consolidada da faixa

| Tema | Informação preservada |
|---|---|
| Frente F1 | Evolução de recebidos auditáveis, fontes elegíveis e saldo disponível por pagamento foi preservada. |
| Decisão local | Criação e auditoria da `decisao_local_v1` com proxy econômico v2/v3 foram consolidadas. |
| Absorção legado | Mapeamento e absorção inicial dos scripts legados em modo shadow foram preservados. |
| Switching e multifonte shadow | Benchmarks de switching econômico e resolver híbrido foram registrados como histórico, sem promoção automática. |
| Governança documental | Sincronizações documentais e congelamentos intermediários foram preservados. |

## Marcos-chave prováveis nesta faixa

| Versão | Título |
|---:|---|
| V64 | Baseline fixa V64 |
| V65 | Baseline fixa V65 |
| V66 | Baseline fixa V66 |
| V67 | Baseline fixa V67 |
| V68 | Baseline fixa V68 |
| V69 | Baseline fixa V69 |
| V71 | Baseline fixa V71 |
| V72 | Baseline fixa V72 |
| V73 | Baseline fixa V73 |
| V74 | Baseline fixa V74 |
| V75 | Baseline fixa V75 |
| V76 | Baseline fixa V76 |
| V77 | Baseline fixa V77 |
| V78 | Baseline fixa V78 |
| V79 | Baseline fixa V79 |

## Detalhe por baseline

### V61 — `relatorios\historico\baselines\BASELINE_FIXA_V61.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 29
- Título: Baseline fixa V61

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V61
## Objetivo desta versão
Derivar a V60 de forma cirúrgica para abrir a **Etapa 2 da Frente F1**, materializando a primeira estrutura real de caixa/recebidos auditáveis: `recebido_auditavel`, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- ampliação de `nucleo/caixa_recebidos_auditaveis.py` para materializar `recebido_auditavel` a partir do inventário canônico e dos vínculos históricos de gastos;
- inclusão de `recebidos_auditaveis` em `nucleo/contexto_baseline.py` como camada derivada não invasiva;
- criação do script `scripts/diagnostico/inspecionar_recebidos_auditaveis.py` e do wrapper `scripts/inspecionar_recebidos_auditaveis.py`;
- atualização da documentação vigente para registrar a Etapa 2 da F1.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V61. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.
## Critério desta baseline
A V61 preserva a baseline limpa da V60 e abre somente a primeira estrutura real da F1. O objetivo é criar a base estável para que as próximas etapas possam materializar `fonte_elegivel_pagamento` e, depois, abrir a decisão local v1 entre saldo disponível e resgate.
## Atualização V61
- manutenção da V60 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- materialização executável de `recebido_auditavel`;
```

</details>

### V62 — `relatorios\historico\baselines\BASELINE_FIXA_V62.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 29
- Título: Baseline fixa V62

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V62
## Objetivo desta versão
Derivar a V61 de forma cirúrgica para abrir a **Etapa 3 da Frente F1**, materializando a segunda estrutura real de caixa/recebidos auditáveis: `fonte_elegivel_pagamento`, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- ampliação de `nucleo/caixa_recebidos_auditaveis.py` para materializar `fonte_elegivel_pagamento` a partir do inventário canônico, da data de referência corrente, dos recebidos auditáveis e do estado mínimo observável do replay;
- inclusão de `fontes_elegiveis_pagamento` em `nucleo/contexto_baseline.py` como camada derivada não invasiva;
- criação do script `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py` e do wrapper `scripts/inspecionar_fontes_elegiveis_pagamento.py`;
- atualização da documentação vigente para registrar a Etapa 3 da F1.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V62. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.
## Critério desta baseline
A V62 preserva a baseline limpa da V61 e abre somente a segunda estrutura real da F1. O objetivo é criar a base estável para que as próximas etapas possam refinar `fonte_elegivel_pagamento`, abrir uma camada robusta de `saldo_disponivel` e, depois, materializar a decisão local v1 entre saldo disponível e resgate.
## Atualização V62
- manutenção da V61 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- materialização executável de `fonte_elegivel_pagamento`;
```

</details>

### V63 — `relatorios\historico\baselines\BASELINE_FIXA_V63.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 29
- Título: Baseline fixa V63

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V63
## Objetivo desta versão
Derivar a V62 de forma cirúrgica para atualizar o cache BCB/CDI do repositório com o arquivo enviado pelo usuário, regenerando os artefatos correntes sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- substituição de `dados/cache_bcb.json` pelo arquivo de cache BCB/CDI atualizado enviado pelo usuário;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- regeneração do artefato operacional vigente com a nova série CDI explícita até 2026-04-16;
- atualização da documentação vigente para registrar a atualização do cache BCB/CDI.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V63. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.
## Critério desta baseline
A V63 preserva a baseline funcional da V62 e aplica apenas a atualização do cache BCB/CDI, reduzindo a dependência de fallback encadeado na situação atual e mantendo intacta a etapa funcional da F1 já aberta.
## Atualização V63
- manutenção da V62 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- atualização de `dados/cache_bcb.json` com série explícita até 2026-04-16;
- regeneração do `.xlsx` operacional vigente;
```

</details>

### V64 — `relatorios\historico\baselines\BASELINE_FIXA_V64.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 37
- Título: Baseline fixa V64

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V64
## Objetivo desta versão
Derivar a V63 de forma cirúrgica para incluir, na seção `Situação atual` do console e da planilha operacional, a situação atual de todos os recebidos auditáveis, incluindo os exauridos, sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- substituição de `dados/cache_bcb.json` pelo arquivo de cache BCB/CDI atualizado enviado pelo usuário;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- regeneração do artefato operacional vigente com a nova série CDI explícita até 2026-04-16;
- atualização da documentação vigente para registrar a atualização do cache BCB/CDI.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V64. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.
## Critério desta baseline
A V64 preserva a baseline funcional da V63 e amplia a seção `Situação atual` do console e da planilha operacional para incluir todos os recebidos auditáveis, inclusive os exauridos, mantendo intactos o motor financeiro e a etapa funcional da F1 já aberta.
## Atualização V64
- manutenção da V63 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- atualização de `dados/cache_bcb.json` com série explícita até 2026-04-16;
- regeneração do `.xlsx` operacional vigente;
```

</details>

### V65 — `relatorios\historico\baselines\BASELINE_FIXA_V65.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V65

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V65
## Objetivo desta versão
Derivar a V64 de forma cirúrgica para reorganizar a seção `Situação atual` do console e da planilha operacional em blocos explícitos de lotes exauridos e lotes ativos, mantendo a leitura dos recebidos auditáveis, inclusive os exauridos, sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.
## Reorganização aplicada
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- reorganização da seção `Situação atual` do console em blocos de lotes exauridos, lotes ativos e recebidos auditáveis;
- reorganização da aba `Situação atual` da planilha com duas tabelas de lotes exauridos e duas tabelas de lotes ativos;
- atualização da documentação vigente para registrar a nova organização da saída operacional.
## Garantia de compatibilidade
Os comandos canônicos e os comandos antigos continuam executáveis na V65. A F1, nesta etapa, continua fora do fluxo decisório principal; as estruturas derivadas seguem auditáveis por diagnóstico e a saída atual apenas reorganiza a visualização.
## Critério desta baseline
A V65 preserva a baseline funcional da V64 e reorganiza a seção `Situação atual` do console e da planilha operacional em blocos explícitos de lotes exauridos e lotes ativos, mantendo também a leitura de todos os recebidos auditáveis, inclusive os exauridos, sem alterar o motor financeiro.
## Atualização V65
- manutenção da V64 como baseline oficial de partida;
- manutenção do release checker como gate obrigatório;
- divisão da seção `Situação atual` em lotes exauridos e lotes ativos no console;
- divisão da aba `Situação atual` em duas tabelas de lotes exauridos e duas tabelas de lotes ativos;
```

</details>

### V66 — `relatorios\historico\baselines\BASELINE_FIXA_V66.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 31
- Título: Baseline fixa V66

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V66
## Objetivo desta versão
Derivar a V65 de forma cirúrgica para ajustar apenas a camada de exibição e a normalização operacional de resíduos sub-limiar na situação atual, removendo a tabela detalhada de recebidos do console e da planilha operacional, separando o fechamento econômico em aba própria do `.xlsx` e corrigindo o caso do `Lote 4124,75 fev.` que aparecia exaurido com saldo remanescente positivo abaixo do limiar.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- remoção da tabela `situação atual de todos os recebidos (inclui exauridos)` do console e da aba `Situação atual`;
- criação da aba separada `Fechamento econômico atual` no `.xlsx`;
- normalização pós-replay de lotes com saldo bruto residual menor ou igual ao limiar operacional, zerando `saldo_bruto` e `principal_remanescente` e marcando o lote como esgotado;
- ajuste do script de auditoria diária para gerar nomes de arquivo coerentes com o lote informado.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V66. O motor financeiro, a lógica de valuation e a etapa funcional já aberta da F1 continuam preservados; a correção desta versão atua apenas na normalização operacional final de resíduos sub-limiar e na camada de exibição dos artefatos.
## Critério desta baseline
A V66 preserva a baseline funcional da V65 e corrige a inconsistência operacional na situação atual em que um lote já tratado como exaurido pelo limiar ainda aparecia com `Saldo rem` positivo. Ao mesmo tempo, simplifica a leitura dos artefatos correntes removendo a tabela detalhada de recebidos da seção/aba atual e isolando o fechamento econômico da situação atual em aba própria.
## Atualização V66
- manutenção da V65 como baseline oficial de partida;
- manutenção do release checker como gate obrigatório;
- remoção da tabela detalhada de recebidos do console e da planilha;
```

</details>

### V67 — `relatorios\historico\baselines\BASELINE_FIXA_V67.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 31
- Título: Baseline fixa V67

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V67
## Objetivo desta versão
Derivar a V66 de forma cirúrgica para ajustar apenas a semântica da camada F1 ligada aos recebidos/lotes usados antes da aplicação, substituindo o rótulo `misto` por uma classificação operacional mais explicativa, sem alterar o motor financeiro nem a lógica econômica já implementada.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- remoção da tabela `situação atual de todos os recebidos (inclui exauridos)` do console e da aba `Situação atual`;
- criação da aba separada `Fechamento econômico atual` no `.xlsx`;
- normalização pós-replay de lotes com saldo bruto residual menor ou igual ao limiar operacional, zerando `saldo_bruto` e `principal_remanescente` e marcando o lote como esgotado;
- ajuste do script de auditoria diária para gerar nomes de arquivo coerentes com o lote informado.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V67. O motor financeiro, a lógica de valuation e a etapa funcional já aberta da F1 continuam preservados; a correção desta versão atua apenas na normalização operacional final de resíduos sub-limiar e na camada de exibição dos artefatos.
## Critério desta baseline
A V67 preserva a baseline funcional da V66 e melhora a auditabilidade semântica da F1 ao substituir o rótulo `misto` por uma classificação explícita para os casos em que o recebido financiou pagamentos antes da aplicação e foi aportado depois.
## Atualização V67
- manutenção da V66 como baseline oficial de partida;
- substituição do status `misto` por `uso_pre_aplicacao_com_aporte_posterior`;
- substituição do destino `misto` por `pagamento_e_aplicacao`;
```

</details>

### V68 — `relatorios\historico\baselines\BASELINE_FIXA_V68.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V68

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V68
## Objetivo desta versão
Derivar a V67 de forma cirúrgica para abrir a micro-etapa **F1.4**, refinando `fonte_elegivel_pagamento` para uma leitura temporal por **pagamento** e por **data de pagamento**, sem alterar o motor financeiro nem a lógica econômica já implementada.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- refinamento do contrato mínimo da F1 para incluir o contexto `fonte x pagamento`;
- materialização executável de `fonte_elegivel_pagamento` por `pagamento_id` e `data_pagamento`;
- inclusão de colunas auditáveis como `elegivel_na_data_pagamento`, `motivo_bloqueio_temporal`, `data_base_valor` e `metodo_valor_disponivel`;
- atualização do diagnóstico de `fonte_elegivel_pagamento` para a Etapa 4 da F1.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V68. O motor financeiro, a lógica de valuation, o replay histórico e a materialização já aberta de `recebido_auditavel` continuam preservados; a correção desta versão atua apenas na camada F1 de elegibilidade temporal das fontes.
## Critério desta baseline
A V68 preserva a baseline funcional da V67 e aproxima a F1 da futura decisão local v1 ao dizer **quais fontes podem financiar cada pagamento na sua própria data**, ainda sem abrir `saldo_disponivel` geral nem decisão econômica real.
## Atualização V68
- manutenção da V67 como baseline oficial de partida;
- abertura da micro-etapa **F1.4** por refinamento temporal de `fonte_elegivel_pagamento`;
- preservação integral da lógica econômica já implementada;
```

</details>

### V69 — `relatorios\historico\baselines\BASELINE_FIXA_V69.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V69

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V69
## Objetivo desta versão
Derivar a V68 de forma cirúrgica para abrir a micro-etapa **F1.5**, materializando `saldo_disponivel_geral` por pagamento a partir das fontes explícitas já observáveis, sem alterar o motor financeiro nem a lógica econômica já implementada.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- refinamento do contrato mínimo da F1 para incluir `saldo_disponivel_geral` como terceira estrutura real observável;
- materialização executável de `saldo_disponivel_geral` por `pagamento_id` e `data_pagamento`;
- inclusão de metadados auditáveis como `origem_saldo`, `qtd_fontes_componentes`, `restricao_duplicidade_recebidos` e `metodo_saldo`;
- atualização do diagnóstico de `saldo_disponivel_geral` para a Etapa 5 da F1.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V69. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel` e `fonte_elegivel_pagamento` continuam preservados; a correção desta versão atua apenas na camada F1 de saldo geral observável.
## Critério desta baseline
A V69 preserva a baseline funcional da V68 e fecha o universo mínimo de fontes observáveis da F1 ao dizer, para cada pagamento futuro, qual é o `saldo_disponivel_geral` auditável sem duplicar as fontes explícitas já abertas, ainda sem abrir a decisão econômica real.
## Atualização V69
- manutenção da V68 como baseline oficial de partida;
- abertura da micro-etapa **F1.5** por materialização de `saldo_disponivel_geral`;
- preservação integral da lógica econômica já implementada;
```

</details>

### V71 — `relatorios\historico\baselines\BASELINE_FIXA_V71.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V71

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V71
## Objetivo desta versão
Derivar a V71 de forma cirúrgica para abrir a micro-etapa **F1.7**, materializando `decisao_local_v1` com proxy econômico v2 por pagamento sobre a matriz temporal completa (`fonte_elegivel_pagamento` + `saldo_disponivel_geral`), sem alterar o motor financeiro nem integrar a decisão ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- refinamento do contrato mínimo da F1 para incluir `decisao_local_v1` como quarta estrutura real observável;
- materialização executável de `decisao_local_v1` com proxy econômico v2 por `pagamento_id` e `data_pagamento`;
- inclusão de metadados auditáveis como `criterio_decisao`, `custo_economico_proxy`, `valor_disponivel_escolhido` e `pagamento_totalmente_coberto`;
- atualização do diagnóstico de `decisao_local_v1` para a Etapa 7 da F1.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V71. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento` e `saldo_disponivel_geral` continuam preservadas; a correção desta versão atua apenas na camada F1 de decisão local observável.
## Critério desta baseline
A V71 preserva a baseline funcional da V68 e abre a primeira regra executável de escolha local da F1 ao dizer, para cada pagamento futuro, qual fonte seria escolhida pela regra v1 sobre a matriz temporal completa, ainda sem abrir solver, switching ou decisão econômica real otimizada.
## Atualização V71
- manutenção da V71 como baseline oficial de partida;
- abertura da micro-etapa **F1.7** por materialização de `decisao_local_v1` com proxy econômico v2;
- preservação integral da lógica econômica já implementada;
```

</details>

### V72 — `relatorios\historico\baselines\BASELINE_FIXA_V72.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V72

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V72
## Objetivo desta versão
Derivar a V71 de forma cirúrgica para abrir a micro-etapa **F1.8**, materializando `decisao_local_v1` com proxy econômico v3 por pagamento sobre a matriz temporal completa (`fonte_elegivel_pagamento` + `saldo_disponivel_geral`), sem alterar o motor financeiro nem integrar a decisão ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- refinamento do contrato mínimo da F1 para incluir `decisao_local_v1` como quarta estrutura real observável;
- materialização executável de `decisao_local_v1` com proxy econômico v3 por `pagamento_id` e `data_pagamento`;
- inclusão de metadados auditáveis como `criterio_decisao`, `custo_economico_proxy`, `valor_disponivel_escolhido` e `pagamento_totalmente_coberto`;
- atualização do diagnóstico de `decisao_local_v1` para a Etapa 8 da F1.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V72. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento` e `saldo_disponivel_geral` continuam preservadas; a correção desta versão atua apenas na camada F1 de decisão local observável.
## Critério desta baseline
A V72 preserva a baseline funcional da V68 e abre a primeira regra executável de escolha local da F1 ao dizer, para cada pagamento futuro, qual fonte seria escolhida pela regra v1 sobre a matriz temporal completa, ainda sem abrir solver, switching ou decisão econômica real otimizada.
## Atualização V72
- manutenção da V71 como baseline oficial de partida;
- abertura da micro-etapa **F1.8** por materialização de `decisao_local_v1` com proxy econômico v3;
- preservação integral da lógica econômica já implementada;
```

</details>

### V73 — `relatorios\historico\baselines\BASELINE_FIXA_V73.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V73

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V73
## Objetivo desta versão
Derivar a V72 de forma cirúrgica para abrir a **auditoria comparativa proxy econômico v2 vs v3** sobre a mesma base e os mesmos pagamentos, sem alterar o motor financeiro, sem abrir multifonte e sem integrar novas decisões ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- preservação da `decisao_local_v1` com proxy econômico v3 como baseline vigente;
- inclusão de funções reproduzíveis para recalcular a decisão local com proxy v2 e proxy v3 na mesma base;
- inclusão da auditoria comparativa `v2 vs v3` com quadro detalhado de mudanças, deltas sob métricas comuns e artefatos exportáveis;
- inclusão do diagnóstico `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V73. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1` continuam preservados; a correção desta versão atua apenas na camada diagnóstica da F1.
## Critério desta baseline
A V73 preserva a V72 como baseline funcional de decisão local monofonte e adiciona uma auditoria interna para verificar se o proxy v3 gera ganho observável real em relação ao v2 antes de abrir multifonte.
## Atualização V73
- manutenção da V72 como baseline oficial de partida;
- abertura da auditoria comparativa **proxy econômico v2 vs v3**;
- preservação integral da lógica econômica já implementada;
```

</details>

### V74 — `relatorios\historico\baselines\BASELINE_FIXA_V74.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 30
- Título: Baseline fixa V74

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V74
## Objetivo desta versão
Derivar a V73 de forma cirúrgica para executar uma **sincronização documental** do repositório, alinhando contrato operacional, backlog, README e relatórios vigentes ao estado real da baseline, sem alterar o motor financeiro, sem abrir multifonte e sem mexer na decisão local congelada.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- sincronização do `README`, do contrato operacional e do backlog com a realidade da V73;
- congelamento explícito do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência;
- atualização dos relatórios vigentes e do índice documental para a nova baseline.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V74. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1` continuam preservados; a correção desta versão atua apenas na identidade da baseline, na documentação vigente e nos nomes de artefatos.
## Critério desta baseline
A V74 não abre nova frente funcional. Ela consolida documentalmente a V73, fecha a inconsistência entre contrato/backlog/README e o estado real do repositório e prepara o próximo envio seletivo de scripts originais restantes apenas quando trouxerem regra de negócio ainda ausente.
## Atualização V74
- manutenção da V73 como baseline funcional de partida;
- sincronização documental do repositório para refletir o estado real da baseline;
- preservação do `proxy econômico v3` congelado como decisão monofonte vigente;
```

</details>

### V75 — `relatorios\historico\baselines\BASELINE_FIXA_V75.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 23
- Título: Baseline fixa V75

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V75
## Objetivo desta versão
Derivar a V74 de forma cirúrgica para executar um **mapeamento de absorção legado** dos `Script 1.txt` e `Script 2.txt`, alinhando README, contrato, backlog e relatórios vigentes ao estado real do repositório, sem alterar o motor financeiro, sem reabrir o `proxy econômico v3` congelado e sem abrir `multifonte v1`.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do relatório vigente `MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_mapa_absorcao_legado.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog e do índice documental com a realidade da V75;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V75. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na identidade da baseline, na documentação vigente, no diagnóstico do mapa legado e nos nomes de artefatos.
## Critério desta baseline
A V75 não abre nova frente funcional. Ela consolida um mapa de absorção legado para os Scripts 1 e 2, separando o que deve migrar já, o que deve migrar depois, o que não deve migrar e o que já foi substituído pela baseline.
```

</details>

### V76 — `relatorios\historico\baselines\BASELINE_FIXA_V76.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 28
- Título: Baseline fixa V76

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V76
## Objetivo desta versão
Derivar a V75 de forma cirúrgica para abrir a **absorção inicial do switching econômico legado em modo shadow**, adicionando uma camada diagnóstica auditável de comparação `manter vs. trocar` por lote sem acoplamento ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/switching_economico_shadow.py`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog, do índice documental e dos relatórios vigentes com a realidade da V76;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V76. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na abertura da camada shadow de switching econômico legado, na identidade da baseline, na documentação vigente, no diagnóstico novo e nos nomes de artefatos.
## Critério desta baseline
A V76 não executa switching no fluxo principal. Ela materializa uma camada **shadow** que:
- avalia lotes ativos pós-replay;
- compara `manter` vs `switch agora e carregar até o horizonte`;
```

</details>

### V77 — `relatorios\historico\baselines\BASELINE_FIXA_V77.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 41
- Título: Baseline fixa V77

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V77
## Objetivo desta versão
Derivar a V76 de forma cirúrgica para abrir o **benchmark shadow do `resolver_hibrido_5p` legado**, adicionando uma camada diagnóstica auditável de alocação multifonte local por pagamento sem acoplamento ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/switching_economico_shadow.py`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog, do índice documental e dos relatórios vigentes com a realidade da V77;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V77. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na abertura da camada shadow de switching econômico legado, na identidade da baseline, na documentação vigente, no diagnóstico novo e nos nomes de artefatos.
## Critério desta baseline
A V77 não executa switching no fluxo principal. Ela materializa uma camada **shadow** que:
- avalia lotes ativos pós-replay;
- compara `manter` vs `switch agora e carregar até o horizonte`;
```

</details>

### V78 — `relatorios\historico\baselines\BASELINE_FIXA_V78.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 48
- Título: Baseline fixa V78

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V78
## Objetivo desta versão
Derivar a V77 de forma cirúrgica para abrir o **benchmark shadow do `resolver_hibrido_5p` legado**, adicionando uma camada diagnóstica auditável de alocação multifonte local por pagamento sem acoplamento ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/switching_economico_shadow.py`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog, do índice documental e dos relatórios vigentes com a realidade da V78;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V78. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na abertura da camada shadow de switching econômico legado, na identidade da baseline, na documentação vigente, no diagnóstico novo e nos nomes de artefatos.
## Critério desta baseline
A V78 não executa switching no fluxo principal. Ela materializa uma camada **shadow** que:
- avalia lotes ativos pós-replay;
- compara `manter` vs `switch agora e carregar até o horizonte`;
```

</details>

### V79 — `relatorios\historico\baselines\BASELINE_FIXA_V79.md`

- Classe preliminar: `MARCO_CHAVE_PROVAVEL`
- Linhas originais: 53
- Título: Baseline fixa V79

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V79
## Objetivo desta versão
Derivar a V77 de forma cirúrgica para abrir o **benchmark shadow do `resolver_hibrido_5p` legado**, adicionando uma camada diagnóstica auditável de alocação multifonte local por pagamento sem acoplamento ao fluxo principal.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/switching_economico_shadow.py`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog, do índice documental e dos relatórios vigentes com a realidade da V79;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V79. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na abertura da camada shadow de switching econômico legado, na identidade da baseline, na documentação vigente, no diagnóstico novo e nos nomes de artefatos.
## Critério desta baseline
A V79 não executa switching no fluxo principal. Ela materializa uma camada **shadow** que:
- avalia lotes ativos pós-replay;
- compara `manter` vs `switch agora e carregar até o horizonte`;
```

</details>

### V80 — `relatorios\historico\baselines\BASELINE_FIXA_V80.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 21
- Título: Baseline fixa V80

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V80
## Objetivo desta versão
Derivar a V79 de forma cirúrgica para abrir uma **auditoria cirúrgica apenas dos 42 casos reaproveitáveis** identificados na auditoria residual entre o `proxy v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal, sem reabrir o `proxy v3` e sem acoplar o benchmark híbrido.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório;
- criação do diagnóstico `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` e wrapper correspondente;
- abertura de uma auditoria cirúrgica apenas sobre os casos classificados como `potencial_reaproveitamento_proxy_v3`;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V80.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V80. O motor financeiro, o replay, a F1, o `proxy v3`, o switching shadow e o benchmark híbrido shadow continuam preservados; a correção desta versão atua apenas na auditoria diagnóstica adicional e na identidade/documentação da baseline.
## Critério desta baseline
A V80 não reabre o `proxy v3`. Ela materializa apenas uma auditoria cirúrgica dos **42 casos reaproveitáveis**, priorizando padrões, transições dominantes e buckets mais promissores para eventual auditoria fina futura.
```

</details>

### V82 — `relatorios\historico\baselines\BASELINE_FIXA_V82.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 21
- Título: Baseline fixa V82

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V82
## Objetivo desta versão
Derivar a V81 de forma cirúrgica para abrir uma **auditoria fina apenas da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`**, identificada a partir da auditoria cirúrgica dos 42 casos reaproveitáveis entre o `proxy v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal, sem reabrir o `proxy v3` e sem acoplar o benchmark híbrido.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório;
- criação do diagnóstico `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` e wrapper correspondente;
- abertura de uma auditoria fina apenas sobre a transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V82.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V82. O motor financeiro, o replay, a F1, o `proxy v3`, o switching shadow e o benchmark híbrido shadow continuam preservados; a correção desta versão atua apenas na auditoria diagnóstica adicional e na identidade/documentação da baseline.
## Critério desta baseline
A V82 não reabre o `proxy v3`. Ela materializa apenas uma auditoria fina da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`, priorizando descrições, buckets e janela temporal mais promissora para eventual hipótese de ajuste localizado futuro.
```

</details>

### V83 — `relatorios\historico\baselines\BASELINE_FIXA_V83.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 21
- Título: Baseline fixa V83

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V83
## Objetivo desta versão
Derivar a V81 de forma cirúrgica para abrir uma **auditoria fina apenas da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`**, identificada a partir da auditoria cirúrgica dos 42 casos reaproveitáveis entre o `proxy v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal, sem reabrir o `proxy v3` e sem acoplar o benchmark híbrido.
## Ajustes aplicados
- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório;
- criação do diagnóstico `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` e wrapper correspondente;
- abertura de uma auditoria fina apenas sobre a transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V83.
## Garantia de compatibilidade
Os comandos canônicos e antigos continuam executáveis na V83. O motor financeiro, o replay, a F1, o `proxy v3`, o switching shadow e o benchmark híbrido shadow continuam preservados; a correção desta versão atua apenas na auditoria diagnóstica adicional e na identidade/documentação da baseline.
## Critério desta baseline
A V83 não reabre o `proxy v3`. Ela materializa apenas uma auditoria fina da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`, priorizando descrições, buckets e janela temporal mais promissora para eventual hipótese de ajuste localizado futuro.
```

</details>

### V84 — `relatorios\historico\baselines\BASELINE_FIXA_V84.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 24
- Título: Baseline fixa V84

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V84
## Escopo da V84
A V84 preserva integralmente a baseline funcional imediatamente anterior e abre apenas uma **auditoria estrutural de redundância e compatibilidade**.
## O que a V84 adiciona
- relatório vigente da auditoria estrutural;
- diagnóstico reproduzível da auditoria estrutural;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V84.
## O que a V84 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V84
A V84 não é uma refatoração. Ela apenas torna explícitos os pontos de redundância e compatibilidade que passaram a merecer correção futura, sem contaminar a baseline funcional atual.
```

</details>

### V85 — `relatorios\historico\baselines\BASELINE_FIXA_V85.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 24
- Título: Baseline fixa V85

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V85
## Escopo da V85
A V85 preserva integralmente a baseline funcional imediatamente anterior e preserva integralmente a baseline funcional imediatamente anterior e corrige os wrappers raiz quebrados identificados na auditoria estrutural, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow.
## O que a V85 adiciona
- relatório vigente da auditoria estrutural;
- diagnóstico reproduzível da auditoria estrutural;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V85.
## O que a V85 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V85
A V85 não é uma refatoração. Ela apenas torna explícitos os pontos de redundância e compatibilidade que passaram a merecer correção futura, sem contaminar a baseline funcional atual.
```

</details>

### V86 — `relatorios\historico\baselines\BASELINE_FIXA_V86.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 24
- Título: Baseline fixa V86

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V86
## Escopo da V86
A V86 preserva integralmente a baseline funcional imediatamente anterior e preserva integralmente a baseline funcional imediatamente anterior e preserva integralmente a baseline funcional imediatamente anterior e consolida helpers duplicados de baixo risco, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow.
## O que a V86 adiciona
- relatório vigente da auditoria estrutural;
- diagnóstico reproduzível da auditoria estrutural;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V86.
## O que a V86 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V86
A V86 não é uma refatoração. Ela apenas torna explícitos os pontos de redundância e compatibilidade que passaram a merecer correção futura, sem contaminar a baseline funcional atual.
```

</details>

### V87 — `relatorios\historico\baselines\BASELINE_FIXA_V87.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 24
- Título: Baseline fixa V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V88
## Escopo da V88
A V88 preserva integralmente a baseline funcional imediatamente anterior e abre o mapa de absorção da execução principal do Script 2, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow.
## O que a V88 adiciona
- relatório vigente do mapa de absorção da execução principal do Script 2;
- diagnóstico reproduzível desse mapa;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V88.
## O que a V88 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V88
A V88 não migra funcionalmente o runner legado do Script 2. Ela apenas classifica sua orquestração principal em termos de absorção futura controlada.
```

</details>

### V88 — `relatorios\historico\baselines\BASELINE_FIXA_V88.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 24
- Título: Baseline fixa V88

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V88
## Escopo da V88
A V88 preserva integralmente a baseline funcional imediatamente anterior e abre o mapa de absorção da execução principal do Script 2, sem alterar o motor financeiro, o replay, o `proxy v3` congelado ou os benchmarks shadow.
## O que a V88 adiciona
- relatório vigente do mapa de absorção da execução principal do Script 2;
- diagnóstico reproduzível desse mapa;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V88.
## O que a V88 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V88
A V88 não migra funcionalmente o runner legado do Script 2. Ela apenas classifica sua orquestração principal em termos de absorção futura controlada.
```

</details>

### V89 — `relatorios\historico\baselines\BASELINE_FIXA_V89.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 28
- Título: Baseline fixa V89

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V89
## Escopo da V89
A V89 preserva integralmente a baseline funcional imediatamente anterior, atualiza os arquivos canônicos `dados/dados_financeiros.xlsx` e `dados/cache_bcb.json`, ajusta o `.gitignore` e revalida o benchmark shadow agrupado vs individual, sem alterar o motor financeiro, o replay ou o `proxy v3` congelado.
## O que a V89 adiciona
## Atualização da V89
A V89 atualiza os arquivos canônicos `dados/dados_financeiros.xlsx` e `dados/cache_bcb.json`, ajusta o `.gitignore` para ignorar `Script 1.txt`, `Script 2.txt` e `code/`, e revalida o benchmark shadow agrupado vs individual com os dados atualizados.
- relatório vigente do mapa de absorção da execução principal do Script 2;
- diagnóstico reproduzível desse mapa;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V89.
## O que a V89 não altera
- motor financeiro;
- replay;
- `proxy econômico v3` congelado;
- `switching_economico_shadow`;
- `resolver_hibrido_5p_shadow`;
- comportamento operacional da geração da planilha e das auditorias canônicas.
## Papel da V89
A V89 não migra funcionalmente o runner legado do Script 2. Ela apenas classifica sua orquestração principal em termos de absorção futura controlada.
```

</details>

### V90 — `relatorios\historico\baselines\BASELINE_FIXA_V90.md`

- Classe preliminar: `BASELINE_RELEVANTE`
- Linhas originais: 18
- Título: Baseline fixa V90

<details>
<summary>Trecho inicial preservado</summary>

```text
# Baseline fixa V90
## Escopo da V90
A V90 preserva integralmente a baseline funcional imediatamente anterior e corrige a etapa de promoção do arquivo temporário usado no download da planilha financeira. A correção evita falso `PermissionError` no Windows ao validar o `.xlsx` baixado antes de sobrescrever `dados/dados_financeiros.xlsx`.
## O que a V90 altera
- validação do arquivo baixado com fechamento explícito do handle do `pd.ExcelFile`;
- tratamento específico de `PermissionError` na promoção do arquivo temporário para a planilha canônica;
- atualização da identidade da baseline e da documentação vigente.
## O que a V90 não altera
- motor financeiro;
- replay;
- `proxy v3` congelado;
- benchmarks shadow e auditorias diagnósticas.
```

</details>

## Decisão desta etapa

A faixa V061–V090 foi consolidada em relatório único. Os arquivos granulares originais ainda devem permanecer até que todas as faixas de baselines sejam consolidadas e um índice-mestre final seja criado.

# Frente F1 — contrato mínimo de caixa/recebidos auditáveis

## Escopo desta etapa

A Etapa 8 da F1 preserva o **contrato mínimo canônico** da nova camada de caixa/recebidos auditáveis e mantém a quarta estrutura real materializada: `decisao_local_v1` escolhe, por pagamento, uma fonte prioritária observável sobre a matriz temporal completa (`fonte_elegivel_pagamento` + `saldo_disponivel_geral`) usando um `proxy econômico v3` auditável. Nesta etapa, o projeto **não** altera o motor financeiro, **não** abre solver ou switching e **não** integra ainda a decisão ao fluxo principal do console ou da planilha operacional.

## Objetivo

Criar uma base formal, estável e auditável para que as próximas etapas possam materializar:
- fontes elegíveis de pagamento por data e por pagamento;
- saldo disponível geral por pagamento sem duplicar as fontes explícitas já observáveis;
- recebidos auditáveis com destino explícito e vínculo histórico observável;
- decisão local v1 entre saldo disponível, caixa pré-aplicação, recebidos e resgate.

## Estruturas mínimas abertas nesta etapa

### 1. `fonte_elegivel_pagamento`
Representa qualquer fonte economicamente elegível para financiar um pagamento em uma data específica.

Campos mínimos:
- `fonte_pagamento_id`
- `fonte_id`
- `pagamento_id`
- `data_pagamento`
- `tipo_fonte`
- `data_evento`
- `lote_id`
- `recebido_id`
- `produto_key`
- `valor_pagamento`
- `valor_bruto_disponivel`
- `valor_liquido_disponivel`
- `elegivel_na_data_pagamento`
- `origem_status`
- `motivo_bloqueio_temporal`
- `data_base_valor`
- `metodo_valor_disponivel`
- `observacao_auditavel`

**Estado atual:** contratual + materializado a partir do inventário canônico, da data de referência corrente, dos pagamentos futuros/pendentes, dos recebidos auditáveis e do estado mínimo observável do replay. Nesta etapa, a camada ainda não projeta financeiramente o valor das fontes até a data do pagamento.

### 2. `recebido_auditavel`
Representa o recebido com valor, status e destino auditável.

Campos mínimos:
- `recebido_id`
- `data_recebimento`
- `data_aplicacao`
- `valor_bruto`
- `valor_liquido`
- `status_recebido`
- `destino_potencial`
- `pagamento_vinculado_id`
- `lote_destino_id`
- `observacao_auditavel`

**Estado atual:** contratual + materializado a partir do inventário canônico e dos vínculos históricos explícitos da aba `Todos os Gastos`.

### 3. `saldo_disponivel_geral`
Representa o saldo disponível geral observável por pagamento, agregado apenas das fontes explícitas de caixa já abertas na F1.

Campos mínimos:
- `saldo_disponivel_id`
- `pagamento_id`
- `data_pagamento`
- `valor_pagamento`
- `saldo_disponivel_bruto`
- `saldo_disponivel_liquido`
- `saldo_disponivel_elegivel`
- `origem_status`
- `origem_saldo`
- `qtd_fontes_componentes`
- `tipos_fontes_componentes`
- `regra_precedencia_intradiaria`
- `restricao_duplicidade_recebidos`
- `data_base_saldo`
- `metodo_saldo`
- `observacao_auditavel`

**Estado atual:** contratual + materializado por pagamento a partir das fontes explícitas já observáveis (`recebido_disponivel` e `caixa_pre_aplicacao`) sem projetar financeiramente o caixa e sem somar novamente as fontes componentes.

### 4. `decisao_local_v1`
Representa a primeira decisão local executável entre caixa e resgate, com `proxy econômico v3` auditável, ainda sem solver e sem switching.

Campos mínimos:
- `pagamento_id`
- `data_pagamento`
- `fonte_escolhida_id`
- `tipo_fonte_escolhida`
- `criterio_decisao`
- `custo_economico_proxy`
- `observacao_auditavel`

**Estado atual:** contratual + materializado por pagamento a partir de `saldo_disponivel_geral` e `fonte_elegivel_pagamento`, usando um `proxy econômico v3` congelado como critério vigente até nova evidência concreta.

## Fora do escopo nesta etapa

- alterar o motor financeiro;
- alterar replay do passado;
- alterar valuation dos lotes;
- abrir switching econômico;
- integrar a decisão local v1 ao fluxo principal;
- permitir decisão multi-fonte para cobrir um mesmo pagamento;
- projetar financeiramente os saldos das fontes até cada data de pagamento.

## Evidência observável desta etapa

O contrato mínimo pode ser inspecionado diretamente por:

```bash
python scripts/diagnostico/inspecionar_contrato_f1.py
```

A primeira estrutura real da F1 pode ser inspecionada por:

```bash
python scripts/diagnostico/inspecionar_recebidos_auditaveis.py
```

ou pelo wrapper de compatibilidade:

```bash
python scripts/inspecionar_recebidos_auditaveis.py
```

A segunda estrutura real da F1 pode ser inspecionada por:

```bash
python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py
```

ou pelo wrapper de compatibilidade:

```bash
python scripts/inspecionar_fontes_elegiveis_pagamento.py
```

A terceira estrutura real da F1 pode ser inspecionada por:

```bash
python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py
```

ou pelo wrapper de compatibilidade:

```bash
python scripts/inspecionar_saldo_disponivel_geral.py
```

A quarta estrutura real da F1 pode ser inspecionada por:

```bash
python scripts/diagnostico/inspecionar_decisao_local_v1.py
```

ou pelo wrapper de compatibilidade:

```bash
python scripts/inspecionar_decisao_local_v1.py
```

A auditoria comparativa entre `proxy v2` e `proxy v3` pode ser inspecionada por:

```bash
python scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py
```

## Atualização V76

- baseline atualizada para **V76** sem alteração funcional da F1;
- congelamento explícito do `proxy econômico v3` como decisão monofonte vigente;
- manutenção da auditoria comparativa `proxy v2 vs v3` como referência diagnóstica;
- preservação do fluxo principal e do motor financeiro, sem abrir multifonte nesta etapa.


## Observação pós-V76

A V76 abriu uma camada paralela `switching_economico_shadow` para absorção diagnóstica do legado de switching. Essa camada não altera o contrato mínimo da F1 e permanece desacoplada da decisão local monofonte vigente.

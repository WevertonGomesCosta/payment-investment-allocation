# Frente F1 — contrato mínimo de caixa/recebidos auditáveis

## Escopo desta etapa

A Etapa 3 da F1 preserva o **contrato mínimo canônico** da nova camada de caixa/recebidos auditáveis e materializa a segunda estrutura real: `fonte_elegivel_pagamento`. Nesta etapa, o projeto **não** altera o motor financeiro, **não** abre a decisão econômica real e **não** integra ainda a F1 ao fluxo principal do console ou da planilha operacional.

## Objetivo

Criar uma base formal, estável e auditável para que as próximas etapas possam materializar:
- fontes elegíveis de pagamento por data;
- recebidos auditáveis com destino explícito e vínculo histórico observável;
- decisão local v1 entre saldo disponível, caixa pré-aplicação, recebidos e resgate.

## Estruturas mínimas abertas nesta etapa

### 1. `fonte_elegivel_pagamento`
Representa qualquer fonte economicamente elegível para financiar um pagamento em uma data específica.

Campos mínimos:
- `fonte_id`
- `tipo_fonte`
- `data_evento`
- `lote_id`
- `recebido_id`
- `produto_key`
- `valor_bruto_disponivel`
- `valor_liquido_disponivel`
- `origem_status`
- `observacao_auditavel`

**Estado atual:** contratual + materializado a partir do inventário canônico, da data de referência corrente, dos recebidos auditáveis e do estado mínimo observável do replay. Nesta etapa, a camada ainda não materializa um `saldo_disponivel` geral robusto e independente da origem explícita do recebido.

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

### 3. `decisao_local_v1`
Reserva a estrutura da futura decisão local entre caixa e resgate, ainda sem solver e sem switching.

Campos mínimos:
- `pagamento_id`
- `data_pagamento`
- `fonte_escolhida_id`
- `tipo_fonte_escolhida`
- `criterio_decisao`
- `custo_economico_proxy`
- `observacao_auditavel`

**Estado atual:** apenas contratual.

## Fora do escopo nesta etapa

- alterar o motor financeiro;
- alterar replay do passado;
- alterar valuation dos lotes;
- abrir switching econômico;
- integrar a decisão local v1 ao fluxo principal;
- materializar uma camada geral de `saldo_disponivel` sem duplicação ou inconsistência com as fontes explícitas já observáveis.

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

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
- `2026-04-14` | conta `Escola` | lote `Lote 3600 abr.` | resíduo `R$ 3,19` | classe causal: `remanescente por rendimento histórico`
- `2026-03-13` | conta `Aluguel` | lote `Lote 4000 fev.` | resíduo `R$ 0,49` | classe causal: `saldo residual após saque líquido-alvo`
- `2026-03-13` | conta `Escola` | lote `Lote 4124,75 fev.` | resíduo `R$ 0,38` | classe causal: `saldo residual após saque líquido-alvo`

## Implicação operacional desta etapa

Com o limiar de `R$ 0,20` já formalizado, a próxima auditoria pode focar apenas nos 5 itens realmente relevantes, agora com rastreabilidade direta por `data`, `conta` e `lote`.

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

A principal inflação não era econômica, mas **contábil-temporal**: o comparador local estava reaproveitando capacidade do mesmo lote repetidas vezes. A V116 não resolve a reconexão com o cenário conjunto final, mas reduz substancialmente o excesso local e deixa explícito quando a regra volta para `sem_switching` por insuficiência residual temporal.

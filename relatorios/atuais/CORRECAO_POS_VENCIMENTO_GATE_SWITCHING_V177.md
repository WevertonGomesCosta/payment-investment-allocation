# Correção da materialização pós-vencimento e do gate de execução diária — V177

## Correções aplicadas

1. `nucleo/runner_validacao_diaria_operacional_v177.py` passou a expor:
   - `lotes_normalizados_pos_vencimento`;
   - `recebidos_ativados_no_dia`;
   - `gate_execucao_switching_diario`;
   - `lotes_monitorados` com `valor_disponivel`, `origem_pos_vencimento` e `data_vencimento_origem`.

2. Em dias sem pagamento, o runner agora promove `switch_only` quando existir `melhor_cenario_promovivel`.

## Evidência objetiva

### 2026-04-23
- melhor cenário promovível: `Lote 3000 mar. B + Lote 3000 mar. V -> Mercado Pago Cofrinho 120% CDI (Meli+)`;
- gate: `override_promovivel_sem_pagamento`;
- switching executado: `True`.

### 2026-05-04
- `lotes_normalizados_pos_vencimento` passou a registrar explicitamente os dois lotes `3000 mar.`;
- `lotes_monitorados` passou a mostrar `valor_relevante` e `valor_disponivel` corretos após o vencimento.

## Observação metodológica
A V177 altera a trajetória da janela curta porque o switching promovível de 2026-04-23 passa a ser efetivamente executado. Por isso, dias posteriores não devem ser comparados diretamente com a V176 sem considerar essa nova trajetória.

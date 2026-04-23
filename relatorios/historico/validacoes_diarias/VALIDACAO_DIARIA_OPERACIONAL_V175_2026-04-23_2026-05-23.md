# Validação diária operacional V175 (2026-04-23 a 2026-05-23)

## Correções aplicadas

1. **Elegibilidade temporal operacional**
   - `materializar_decisao_local_v1(...)` agora aplica filtro explícito de disponibilidade na data de referência.
   - `carregar_recomputacao_sequencial_central_v1(...)` agora remove candidatos não elegíveis operacionalmente antes da comparação central.
   - `carregar_motor_recomendacao_pagamentos_switching_v1(...)` agora filtra `quadro_fontes` pela disponibilidade operacional na data de referência.

2. **Runner diário de validação**
   - Novo módulo: `nucleo/runner_validacao_diaria_operacional_v175.py`
   - Novo script: `scripts/validar_janela_diaria_operacional_v175.py`
   - Janela validada: `2026-04-23` até `2026-05-23`

## Resultado factual da execução

Resumo do JSON gerado:

- dias no horizonte: **31**
- dias com pagamento: **9**
- dias sem pagamento: **22**
- dias com ações candidatas de switching: **30**
- dias com cenários promovíveis: **0**
- dias com switching executado: **0**
- pagamentos no horizonte: **13**
- pagamentos com switching no fluxo: **0**
- inconsistências temporais no estado: **0**

Famílias de cenários avaliadas:

- `individual_integral_parametrizado`: **145**
- `agrupado_integral_parametrizado`: **56**

## Leitura operacional mínima

- A regressão temporal anterior foi corrigida no nível operacional do dia.
- O runner agora percorre **dia 0, dia +1, dia +2, ...** até o fim da janela.
- O switching é avaliado também em dias sem pagamento.
- Nesta janela e com os limites operacionais do runner V175 (`limite_candidatos_por_data=8`, `cap_fontes_destino=3`), **não surgiu cenário promovível**.

## Artefato principal da validação

- `saidas/validacao_diaria_operacional_v175_2026-04-23_2026-05-23.json`


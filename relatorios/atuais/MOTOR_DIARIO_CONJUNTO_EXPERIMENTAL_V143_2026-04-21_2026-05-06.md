# Motor diário conjunto experimental V143
## Janela auditada
- Início: 2026-04-21
- Fim: 2026-05-06
- Limite de candidatos de switching por data: 24
- Cap de fontes por destino: 5

## Objetivo
Implementar um motor diário conjunto experimental tratando o dia como unidade de decisão e comparando, quando houver pagamento, `pay_only` versus `switch_then_pay`; e, quando não houver pagamento, `no_action` versus `switch_only`, sempre com foco em patrimônio líquido terminal proxy sob continuação neutra até o fim da janela.

## Resumo executivo
- Dias no horizonte: 16
- Dias com pagamento: 3
- Pagamentos no horizonte: 4
- Decisões `pay_only`: 3
- Decisões `switch_then_pay`: 0
- Decisões `no_action`: 13
- Decisões `switch_only`: 0
- Patrimônio líquido terminal proxy final: R$ 29586.91
- Fontes de pagamento escolhidas: {'combinacao_minima_fontes': 4}

## Leitura principal
- Nesta janela, nenhuma decisão diária promoveu `switch_then_pay` ou `switch_only`.
- O motor escolheu `pay_only` nos 3 dias com pagamento e `no_action` nos demais dias.
- Todos os 4 pagamentos foram cobertos por `combinacao_minima_fontes`, sem déficit e sem violação de pagamentos protegidos.
- Após restringir explicitamente os recebidos futuros ao horizonte 2026-04-21 até 2026-05-06, o comparador deixou de gerar switching promovível na janela; isso evita falso ganho terminal induzido por recebidos fora do horizonte.

## Decisões por dia
### 2026-04-29
- Tipo do dia: dia_com_pagamento
- Pacote vencedor: `pay_only`
- Pagamentos: despesa_auto_00069
- Patrimônio terminal proxy estimado do vencedor: R$ 29586.91
- Vetor total estimado do vencedor: (0.0, 0.0, 0.0, 3.48, 181.63, 0.0, 3.78, 4.0)
  - Candidato `pay_only` -> patrimônio R$ 29586.91, vetor (0.0, 0.0, 0.0, 3.48, 181.63, 0.0, 3.78, 4.0)
    - despesa_auto_00069: fonte `combinacao_minima_fontes` (combinacao_minima_controlada), déficit 0.00
### 2026-05-04
- Tipo do dia: dia_com_pagamento
- Pacote vencedor: `pay_only`
- Pagamentos: despesa_auto_00070
- Patrimônio terminal proxy estimado do vencedor: R$ 29590.39
- Vetor total estimado do vencedor: (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0)
  - Candidato `pay_only` -> patrimônio R$ 29590.39, vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0)
    - despesa_auto_00070: fonte `combinacao_minima_fontes` (combinacao_minima_controlada), déficit 0.00
### 2026-05-06
- Tipo do dia: dia_com_pagamento
- Pacote vencedor: `pay_only`
- Pagamentos: despesa_auto_00072, despesa_auto_00071
- Patrimônio terminal proxy estimado do vencedor: R$ 29590.39
- Vetor total estimado do vencedor: (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0)
  - Candidato `pay_only` -> patrimônio R$ 29590.39, vetor (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0)
    - despesa_auto_00072: fonte `combinacao_minima_fontes` (combinacao_minima_controlada), déficit 0.00
    - despesa_auto_00071: fonte `combinacao_minima_fontes` (combinacao_minima_controlada), déficit 0.00

## Métrica central final
- violacoes_protegida: 0.0
- deficit_liquido_total: 0.0
- pagamentos_sem_cobertura_integral: 0.0
- perda_patrimonio_liquido_terminal: 3.48
- destruicao_estrategica_lotes: 181.63
- deterioracao_liquidez_futura: 0.0
- custo_fiscal_imediato: 3.78
- custo_operacional: 4.0

## Limitações desta V143
- A comparação do pacote do dia usa continuação neutra até o fim da janela, sem novo switching proativo depois do dia avaliado.
- Portanto, esta implementação é adequada para auditar precedência diária e promoção local de switching, mas ainda não substitui um resolvedor global exato multi-dia.
- Nesta janela específica, a ausência de `switch_then_pay` não prova que switching seja irrelevante no projeto; mostra apenas que não houve cenário promovível dentro do recorte e do horizonte efetivamente considerados.

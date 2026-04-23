# Auditoria de alinhamento entre contrato vigente e objetivo final — V176

## Conclusão executiva

A baseline V175 corrigiu a elegibilidade temporal operacional, mas ainda não entregava uma trilha diária suficientemente auditável para validar o objetivo final do projeto.

A V176 fecha duas lacunas prioritárias:

1. deixa explícito, em documentação oficial, que a validação diária user-facing deve ser lida contra o objetivo final do projeto;
2. reforma o runner diário para expor, por dia, os componentes reais do pagamento vencedor e o quadro de switching candidato/classificado.

## Divergências que precisavam ficar explícitas no projeto

### 1. Saída resumida demais para pagamentos
- Problema anterior: o runner retornava rótulos como `combinacao_minima_controlada`, sem mostrar a decomposição real por fonte/lote.
- Correção de governança na V176: o runner agora deve expor `componentes_reais_pagamento` e `fontes_candidatas_ordenadas`.

### 2. Saída resumida demais para switching
- Problema anterior: o runner retornava apenas contagens agregadas e o pacote vencedor do dia.
- Correção de governança na V176: o runner agora deve expor `acoes_candidatas`, `cenarios_classificados` e `melhor_cenario_promovivel`.

### 3. Critério de promovibilidade mal refletido no runner V175
- Problema anterior: o runner V175 checava `promovivel`, enquanto o comparador híbrido marca `promovivel_hibrido`.
- Efeito: risco de contar ou selecionar cenários de forma incorreta no runner de validação.
- Correção operacional na V176: seleção e contagem passam a usar `escolher_melhor_cenario_promovivel(...)` e `promovivel_hibrido`.

### 4. Lotes monitorados pouco visíveis
- Problema anterior: lotes críticos, como os 3k de março, não apareciam de forma clara no estado diário do runner.
- Correção operacional na V176: inclusão de `lotes_monitorados` por dia, usando a lista já prevista no config.

## Resultado esperado da V176

A V176 não expande ainda o espaço de busca do switching, mas deixa a trilha diária suficientemente auditável para:
- validar o pagamento vencedor por lote/fonte;
- conferir disponibilidade temporal diária;
- inspecionar os lotes monitorados;
- e ver por que cenários de switching são ou não promovidos.

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
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

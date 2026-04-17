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
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

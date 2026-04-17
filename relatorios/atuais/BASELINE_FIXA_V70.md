# Baseline fixa V70

## Objetivo desta versão

Derivar a V69 de forma cirúrgica para abrir a micro-etapa **F1.6**, materializando `decisao_local_v1` por pagamento sobre a matriz temporal completa (`fonte_elegivel_pagamento` + `saldo_disponivel_geral`), sem alterar o motor financeiro nem integrar a decisão ao fluxo principal.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- refinamento do contrato mínimo da F1 para incluir `decisao_local_v1` como quarta estrutura real observável;
- materialização executável de `decisao_local_v1` por `pagamento_id` e `data_pagamento`;
- inclusão de metadados auditáveis como `criterio_decisao`, `custo_economico_proxy`, `valor_disponivel_escolhido` e `pagamento_totalmente_coberto`;
- atualização do diagnóstico de `decisao_local_v1` para a Etapa 6 da F1.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V70. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento` e `saldo_disponivel_geral` continuam preservadas; a correção desta versão atua apenas na camada F1 de decisão local observável.

## Critério desta baseline

A V70 preserva a baseline funcional da V68 e abre a primeira regra executável de escolha local da F1 ao dizer, para cada pagamento futuro, qual fonte seria escolhida pela regra v1 sobre a matriz temporal completa, ainda sem abrir solver, switching ou decisão econômica real otimizada.

## Atualização V70

- manutenção da V69 como baseline oficial de partida;
- abertura da micro-etapa **F1.6** por materialização de `decisao_local_v1`;
- preservação integral da lógica econômica já implementada;
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

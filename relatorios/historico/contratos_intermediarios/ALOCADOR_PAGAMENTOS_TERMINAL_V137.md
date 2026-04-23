# ALOCADOR PAGAMENTOS TERMINAL V137

## Objetivo

Elevar o `alocador_pagamentos_terminal_v1` de esqueleto funcional mínimo para uma primeira versão realmente utilizável na integração com o motor de pagamentos.

## Escopo implementado

A V137 passa a comparar explicitamente, para cada pagamento:
- saldo disponível;
- lote não aportado já disponível na data;
- lote aportado resgatável na data, com custo fiscal estimado;
- combinação mínima funcional entre fontes;
- cenário com switching elegível já filtrado pelo comparador híbrido, desde que seja fornecido com estado pós-switching.

## Regras novas

1. Lote aportado com carência ativa na data do pagamento deixa de entrar como fonte elegível.
2. O custo fiscal estimado do resgate entra no score da fonte.
3. O cenário com switching só entra quando o plano chega já classificado como `vencedor_terminal` ou `vencedor_hibrido_aceitavel`.
4. Planos não promovíveis pelo comparador híbrido não entram como fonte candidata.
5. O retorno inclui metadados explícitos sobre a comparação com switching.

## Limite assumido nesta etapa

A V137 não substitui ainda a recomputação central nem decide sozinha o melhor plano temporal de switching. Ela prepara o núcleo de pagamento para consumir um cenário com switching já filtrado externamente.

# ALOCADOR PAGAMENTOS TERMINAL V137

- Objetivo: validar a primeira versão funcional do `alocador_pagamentos_terminal_v1` com comparação explícita entre saldo disponível, lote não aportado, lote aportado e cenário com switching elegível filtrado pelo comparador híbrido.

## Resultado sintético

- Melhor sem switching: `combinacao_minima_fontes` (usar_combinacao_minima_fontes)
- Melhor com switching elegível: `cenario_switching_elegivel` (usar_cenario_switching_elegivel)
- Switching bloqueado: `combinacao_minima_fontes` (usar_combinacao_minima_fontes)

## Assertivas

- considera cenário com switching promovível: True
- bloqueia switching não promovível: True

## Observação

- Esta validação é sintética e estrutural; o objetivo aqui é confirmar o contrato funcional do alocador antes da integração plena com o fluxo central de pagamentos.

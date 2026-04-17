# Baseline fixa V61

## Objetivo desta versão

Derivar a V60 de forma cirúrgica para abrir a **Etapa 2 da Frente F1**, materializando a primeira estrutura real de caixa/recebidos auditáveis: `recebido_auditavel`, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- ampliação de `nucleo/caixa_recebidos_auditaveis.py` para materializar `recebido_auditavel` a partir do inventário canônico e dos vínculos históricos de gastos;
- inclusão de `recebidos_auditaveis` em `nucleo/contexto_baseline.py` como camada derivada não invasiva;
- criação do script `scripts/diagnostico/inspecionar_recebidos_auditaveis.py` e do wrapper `scripts/inspecionar_recebidos_auditaveis.py`;
- atualização da documentação vigente para registrar a Etapa 2 da F1.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V61. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.

## Critério desta baseline

A V61 preserva a baseline limpa da V60 e abre somente a primeira estrutura real da F1. O objetivo é criar a base estável para que as próximas etapas possam materializar `fonte_elegivel_pagamento` e, depois, abrir a decisão local v1 entre saldo disponível e resgate.

## Atualização V61

- manutenção da V60 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- materialização executável de `recebido_auditavel`;
- preservação do motor financeiro e do fluxo principal.

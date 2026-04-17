# Baseline fixa V60

## Objetivo desta versão

Derivar a V59 de forma cirúrgica para abrir apenas a **Etapa 1 da Frente F1**, formalizando o contrato mínimo da nova camada de caixa/recebidos auditáveis e tornando essa etapa observável por documentação e script diagnóstico, sem alterar o motor financeiro nem integrar ainda a F1 ao fluxo principal.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/caixa_recebidos_auditaveis.py` com as estruturas canônicas mínimas da F1;
- criação do script `scripts/diagnostico/inspecionar_contrato_f1.py` e do wrapper `scripts/inspecionar_contrato_f1.py`;
- atualização da documentação vigente para registrar a abertura parcial da F1.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V60. A F1, nesta etapa, é apenas contratual/diagnóstica e não altera console principal, planilha operacional, replay ou valuation.

## Critério desta baseline

A V60 preserva a baseline limpa da V59 e abre somente a camada contratual mínima da F1. O objetivo é criar a base estável para que as próximas etapas possam materializar caixa/recebidos auditáveis e, depois, a decisão local v1 entre saldo disponível e resgate.

## Atualização V60

- formalização da V59 como baseline oficial da nova fase de trabalho;
- manutenção do release checker como gate obrigatório;
- abertura parcial da F1 com contrato mínimo observável;
- inclusão de estruturas canônicas para `fonte_elegivel_pagamento`, `recebido_auditavel` e `decisao_local_v1`.

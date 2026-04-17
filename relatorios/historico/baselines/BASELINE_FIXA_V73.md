# Baseline fixa V73

## Objetivo desta versão

Derivar a V72 de forma cirúrgica para abrir a **auditoria comparativa proxy econômico v2 vs v3** sobre a mesma base e os mesmos pagamentos, sem alterar o motor financeiro, sem abrir multifonte e sem integrar novas decisões ao fluxo principal.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- preservação da `decisao_local_v1` com proxy econômico v3 como baseline vigente;
- inclusão de funções reproduzíveis para recalcular a decisão local com proxy v2 e proxy v3 na mesma base;
- inclusão da auditoria comparativa `v2 vs v3` com quadro detalhado de mudanças, deltas sob métricas comuns e artefatos exportáveis;
- inclusão do diagnóstico `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V73. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1` continuam preservados; a correção desta versão atua apenas na camada diagnóstica da F1.

## Critério desta baseline

A V73 preserva a V72 como baseline funcional de decisão local monofonte e adiciona uma auditoria interna para verificar se o proxy v3 gera ganho observável real em relação ao v2 antes de abrir multifonte.

## Atualização V73

- manutenção da V72 como baseline oficial de partida;
- abertura da auditoria comparativa **proxy econômico v2 vs v3**;
- preservação integral da lógica econômica já implementada;
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

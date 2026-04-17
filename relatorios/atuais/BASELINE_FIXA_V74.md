# Baseline fixa V74

## Objetivo desta versão

Derivar a V73 de forma cirúrgica para executar uma **sincronização documental** do repositório, alinhando contrato operacional, backlog, README e relatórios vigentes ao estado real da baseline, sem alterar o motor financeiro, sem abrir multifonte e sem mexer na decisão local congelada.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- sincronização do `README`, do contrato operacional e do backlog com a realidade da V73;
- congelamento explícito do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência;
- atualização dos relatórios vigentes e do índice documental para a nova baseline.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V74. O motor financeiro, a lógica de valuation, o replay histórico e as materializações já abertas de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1` continuam preservados; a correção desta versão atua apenas na identidade da baseline, na documentação vigente e nos nomes de artefatos.

## Critério desta baseline

A V74 não abre nova frente funcional. Ela consolida documentalmente a V73, fecha a inconsistência entre contrato/backlog/README e o estado real do repositório e prepara o próximo envio seletivo de scripts originais restantes apenas quando trouxerem regra de negócio ainda ausente.

## Atualização V74

- manutenção da V73 como baseline funcional de partida;
- sincronização documental do repositório para refletir o estado real da baseline;
- preservação do `proxy econômico v3` congelado como decisão monofonte vigente;
- manutenção do release checker como gate obrigatório;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

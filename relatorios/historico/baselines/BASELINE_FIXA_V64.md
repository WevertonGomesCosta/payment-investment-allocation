# Baseline fixa V64

## Objetivo desta versão

Derivar a V63 de forma cirúrgica para incluir, na seção `Situação atual` do console e da planilha operacional, a situação atual de todos os recebidos auditáveis, incluindo os exauridos, sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- substituição de `dados/cache_bcb.json` pelo arquivo de cache BCB/CDI atualizado enviado pelo usuário;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- regeneração do artefato operacional vigente com a nova série CDI explícita até 2026-04-16;
- atualização da documentação vigente para registrar a atualização do cache BCB/CDI.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V64. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.

## Critério desta baseline

A V64 preserva a baseline funcional da V63 e amplia a seção `Situação atual` do console e da planilha operacional para incluir todos os recebidos auditáveis, inclusive os exauridos, mantendo intactos o motor financeiro e a etapa funcional da F1 já aberta.

## Atualização V64

- manutenção da V63 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- atualização de `dados/cache_bcb.json` com série explícita até 2026-04-16;
- regeneração do `.xlsx` operacional vigente;
- preservação do motor financeiro, da F1 e do fluxo principal.


## Atualização V64

- manutenção da V63 como baseline oficial corrente;
- inclusão da situação atual de todos os recebidos auditáveis no console;
- inclusão da situação atual de todos os recebidos auditáveis na aba `Situação atual` da planilha operacional;
- preservação explícita dos recebidos exauridos nessa leitura atual.

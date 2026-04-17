# Baseline fixa V65

## Objetivo desta versão

Derivar a V64 de forma cirúrgica para reorganizar a seção `Situação atual` do console e da planilha operacional em blocos explícitos de lotes exauridos e lotes ativos, mantendo a leitura dos recebidos auditáveis, inclusive os exauridos, sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- reorganização da seção `Situação atual` do console em blocos de lotes exauridos, lotes ativos e recebidos auditáveis;
- reorganização da aba `Situação atual` da planilha com duas tabelas de lotes exauridos e duas tabelas de lotes ativos;
- atualização da documentação vigente para registrar a nova organização da saída operacional.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V65. A F1, nesta etapa, continua fora do fluxo decisório principal; as estruturas derivadas seguem auditáveis por diagnóstico e a saída atual apenas reorganiza a visualização.

## Critério desta baseline

A V65 preserva a baseline funcional da V64 e reorganiza a seção `Situação atual` do console e da planilha operacional em blocos explícitos de lotes exauridos e lotes ativos, mantendo também a leitura de todos os recebidos auditáveis, inclusive os exauridos, sem alterar o motor financeiro.

## Atualização V65

- manutenção da V64 como baseline oficial de partida;
- manutenção do release checker como gate obrigatório;
- divisão da seção `Situação atual` em lotes exauridos e lotes ativos no console;
- divisão da aba `Situação atual` em duas tabelas de lotes exauridos e duas tabelas de lotes ativos;
- preservação do bloco de recebidos auditáveis, incluindo os exauridos;
- preservação do motor financeiro, do replay e da F1 fora do fluxo decisório.

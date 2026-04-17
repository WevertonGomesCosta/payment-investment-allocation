# Baseline fixa V63

## Objetivo desta versão

Derivar a V62 de forma cirúrgica para atualizar o cache BCB/CDI do repositório com o arquivo enviado pelo usuário, regenerando os artefatos correntes sem alterar o motor financeiro nem a etapa funcional da F1 já aberta.

## Reorganização aplicada

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- substituição de `dados/cache_bcb.json` pelo arquivo de cache BCB/CDI atualizado enviado pelo usuário;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- regeneração do artefato operacional vigente com a nova série CDI explícita até 2026-04-16;
- atualização da documentação vigente para registrar a atualização do cache BCB/CDI.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V63. A F1, nesta etapa, continua fora do fluxo principal do console e da planilha operacional; a nova estrutura é apenas derivada e inspecionável por diagnóstico.

## Critério desta baseline

A V63 preserva a baseline funcional da V62 e aplica apenas a atualização do cache BCB/CDI, reduzindo a dependência de fallback encadeado na situação atual e mantendo intacta a etapa funcional da F1 já aberta.

## Atualização V63

- manutenção da V62 como base oficial da fase F1;
- manutenção do release checker como gate obrigatório;
- atualização de `dados/cache_bcb.json` com série explícita até 2026-04-16;
- regeneração do `.xlsx` operacional vigente;
- preservação do motor financeiro, da F1 e do fluxo principal.

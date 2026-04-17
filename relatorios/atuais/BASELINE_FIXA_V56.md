# Baseline fixa V56

## Objetivo desta versão

Reorganizar arquiteturalmente a V55 sem alterar a lógica financeira validada da baseline.

## Reorganização aplicada

- centralização da montagem da baseline em `nucleo/contexto_baseline.py`;
- centralização da identidade da versão e dos nomes de artefatos em `nucleo/identidade_baseline.py`;
- extração do helper de leitura do config em `nucleo/config_utils.py`;
- modularização do console em:
  - `aplicacao/console/common.py`
  - `aplicacao/console/secoes_execucao.py`
  - `aplicacao/console/secoes_canonicas.py`
  - `aplicacao/console/secoes_financeiras.py`
  - `aplicacao/console/secoes_triagem.py`
- manutenção dos wrappers de compatibilidade antigos;
- remoção de resíduos de versionamento hardcoded e do código morto `_resolver_data_economica_situacao_atual`.

## Garantia de compatibilidade

Os comandos canônicos e os comandos antigos continuam executáveis na V56.

## Critério desta baseline

A V56 reorganiza orquestração, apresentação e governança do repositório, mas preserva a matemática já validada dos lotes, do replay e da planilha operacional.

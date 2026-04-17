# Baseline fixa V58

## Objetivo desta versão

Derivar a V57 de forma cirúrgica para retirar a auditoria comparativa contra app do fluxo executável e tornar auditável o uso de fallback CDI na situação atual, sem alterar o motor financeiro.

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

Os comandos canônicos e os comandos antigos continuam executáveis na V58.

## Critério desta baseline

A V58 reorganiza orquestração, apresentação e governança do repositório, mas preserva a matemática já validada dos lotes, do replay e da planilha operacional.


## Atualização V58

- fallback encadeado do CDI para dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente quando o download do BCB falhar.

- remoção do ramo de auditoria contra app do fluxo executável da baseline;
- remoção do teste de `-1 dia` do fluxo principal;
- rotulagem auditável do fallback CDI na situação atual do console e do `.xlsx`.

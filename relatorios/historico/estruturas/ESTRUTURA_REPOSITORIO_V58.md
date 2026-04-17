# Estrutura oficial do repositório V58

## Orquestração canônica

- `nucleo/contexto_baseline.py` → montagem central da baseline
- `nucleo/identidade_baseline.py` → versão e nomes-base dos artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config

## Console

- `aplicacao/console/principal.py` → orquestrador do console
- `aplicacao/console/common.py` → helpers de formatação
- `aplicacao/console/secoes_*.py` → renderização modular por seção
- `aplicacao/principal.py` → wrapper de compatibilidade

## Scripts

- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/*.py` → wrappers de compatibilidade

## Auditabilidade de fechamento

- `nucleo/rotulagem_fechamento.py` → resumo auditável do fechamento econômico da situação atual

## Dados

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Saídas

- `saidas/operacional/` → artefatos vigentes da baseline atual

## Documentação

- `relatorios/atuais/` → documentos vigentes
- `relatorios/historico/` → trilha preservada por categoria documental


## Atualização V58

- fallback encadeado do CDI para dias úteis consecutivos sem fator novo, repetindo o último fator válido disponível até a data de referência corrente quando o download do BCB falhar.

- remoção do ramo de auditoria contra app do fluxo executável da baseline;
- remoção do teste de `-1 dia` do fluxo principal;
- rotulagem auditável do fallback CDI na situação atual do console e do `.xlsx`.

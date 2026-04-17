# Estrutura oficial do repositório V70

## Orquestração canônica

- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento` e `saldo_disponivel_geral e decisao_local_v1`
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
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `scripts/diagnostico/inspecionar_decisao_local_v1.py`
- `scripts/*.py` → wrappers de compatibilidade

## Camada F1 aberta até aqui

- `nucleo/caixa_recebidos_auditaveis.py` → contrato mínimo da F1 + materialização de `recebido_auditavel`, `fonte_elegivel_pagamento` por pagamento, `saldo_disponivel_geral` e `decisao_local_v1`
- `scripts/diagnostico/inspecionar_contrato_f1.py` → leitura observável do contrato mínimo da F1
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py` → leitura observável da primeira estrutura real da F1
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py` → leitura observável da segunda estrutura real da F1 na Etapa 4
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py` → leitura observável da terceira estrutura real da F1 na Etapa 5
- `scripts/diagnostico/inspecionar_decisao_local_v1.py` → leitura observável da quarta estrutura real da F1 na Etapa 6

## Auditabilidade de fechamento

- `nucleo/rotulagem_fechamento.py` → resumo auditável do fechamento econômico da situação atual
- `scripts/operacional/gerar_planilha_operacional.py` → aba dedicada `Fechamento econômico atual`

## Governança mínima de release

- `scripts/diagnostico/verificar_release_baseline.py` → checagem automática mínima de higiene da baseline

## Dados

- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

## Saídas

- `saidas/operacional/` → artefatos vigentes da baseline atual

## Documentação

- `relatorios/atuais/` → documentos vigentes
- `relatorios/historico/` → trilha preservada por categoria documental

## Atualização V70

- materialização de `decisao_local_v1` por pagamento;
- inclusão de estrutura e diagnóstico para `decisao_local_v1`;
- preservação da base funcional, da planilha operacional e do console principal;
- manutenção da F1 fora do fluxo decisório principal.

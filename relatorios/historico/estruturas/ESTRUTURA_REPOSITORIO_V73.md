# Estrutura oficial do repositório V73

## Núcleo

- `nucleo/contexto_baseline.py` → montagem central da baseline e derivação de `recebidos_auditaveis`, `fontes_elegiveis_pagamento`, `saldo_disponivel_geral` e `decisao_local_v1`;
- `nucleo/identidade_baseline.py` → identidade da baseline e nomes canônicos de artefatos;
- `nucleo/caixa_recebidos_auditaveis.py` → contrato mínimo da F1 + materialização de `recebido_auditavel`, `fonte_elegivel_pagamento`, `saldo_disponivel_geral`, `decisao_local_v1` e auditoria comparativa `proxy v2 vs v3`.

## Aplicação e wrappers

- `aplicacao/console/principal.py`
- `aplicacao/principal.py`
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- wrappers compatíveis em `scripts/*.py`

## Diagnósticos vigentes

- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `scripts/diagnostico/inspecionar_decisao_local_v1.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`

## Atualização V73

- baseline atualizada para **V73**;
- preservação da decisão local com proxy econômico v3 como baseline vigente;
- inclusão da auditoria comparativa `v2 vs v3` como camada diagnóstica reproduzível;
- preservação do motor financeiro, do replay histórico e do fluxo principal.

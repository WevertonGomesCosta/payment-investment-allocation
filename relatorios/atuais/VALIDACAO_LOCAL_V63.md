# Validação local V63

## Escopo validado

- identidade da baseline atualizada para V63;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- atualização do cache BCB/CDI em `dados/cache_bcb.json`;
- script diagnóstico de `fonte_elegivel_pagamento` e wrapper de compatibilidade executáveis.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`
- `python scripts/inspecionar_contrato_f1.py`
- `python scripts/inspecionar_recebidos_auditaveis.py`
- `python scripts/inspecionar_fontes_elegiveis_pagamento.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v63.xlsx`

## Atualização V63

- manutenção da nova fase sobre a baseline V62;
- manutenção da checagem de release como gate obrigatório;
- atualização do cache BCB/CDI com regeneração dos artefatos correntes, sem tocar no motor financeiro nem na etapa funcional da F1.

## Evidências observáveis da V63

- `dados/cache_bcb.json` passa a conter série explícita até `2026-04-16`;
- a situação atual deixa de depender de dois fechamentos em fallback e passa a depender de apenas um fechamento em fallback na data de referência `2026-04-17`;
- o release checker continua aprovando a baseline sem ruído estrutural;
- os comandos canônicos seguem executando sem regressão funcional.

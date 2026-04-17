# Validação local V69

## Escopo validado

- identidade da baseline atualizada para V69;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 5;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada por `pagamento_id` e `data_pagamento`;
- materialização executável de `saldo_disponivel_geral` por pagamento;
- diagnóstico de `saldo_disponivel_geral` atualizado para mostrar origem, status, duplicidade e método de agregação;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
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
- `python scripts/inspecionar_saldo_disponivel_geral.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v69.xlsx`

## Atualização V69

- manutenção da fase atual sobre a baseline V68;
- abertura da Etapa 5 da F1 por materialização de `saldo_disponivel_geral`;
- manutenção da checagem de release como gate obrigatório;
- preservação integral da lógica econômica e da materialização já aberta na F1.

## Evidências observáveis da V69

- o diagnóstico de `saldo_disponivel_geral` passa a exibir `pagamento_id`, `data_pagamento`, origem, status e duplicidade;
- o resumo passa a exibir `pagamentos_com_saldo_disponivel`, `pagamentos_sem_saldo_disponivel` e `origem_saldo`;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

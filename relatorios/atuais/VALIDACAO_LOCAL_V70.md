# Validação local V70

## Escopo validado

- identidade da baseline atualizada para V70;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 6;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada por `pagamento_id` e `data_pagamento`;
- materialização executável de `saldo_disponivel_geral` preservada;
- materialização executável de `decisao_local_v1` por pagamento sobre a matriz temporal completa;
- diagnóstico de `decisao_local_v1` atualizado para mostrar critério, fonte escolhida, cobertura e status da origem;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `python scripts/diagnostico/inspecionar_decisao_local_v1.py`
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
- `python scripts/inspecionar_decisao_local_v1.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v70.xlsx`

## Atualização V70

- manutenção da fase atual sobre a baseline V68;
- abertura da Etapa 6 da F1 por materialização de `saldo_disponivel_geral`;
- manutenção da checagem de release como gate obrigatório;
- preservação integral da lógica econômica e da materialização já aberta na F1.

## Evidências observáveis da V70

- o diagnóstico de `decisao_local_v1` passa a exibir `pagamento_id`, `data_pagamento`, fonte escolhida, critério de decisão e cobertura;
- o resumo passa a exibir `tipo_fonte_escolhida`, `criterio_decisao` e `pagamentos_totalmente_cobertos`;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

# Validação local V68

## Escopo validado

- identidade da baseline atualizada para V68;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e refinado para a Etapa 4;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` refinada por `pagamento_id` e `data_pagamento`;
- diagnóstico de `fonte_elegivel_pagamento` atualizado para mostrar elegibilidade temporal, bloqueios e método de leitura do valor disponível;
- preservação observável do console principal, da planilha operacional e dos wrappers compatíveis.

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

- `saidas/operacional/relatorio_operacional_v68.xlsx`
- `saidas/operacional/auditoria_diaria_lote_6630_64_fev_v68.xlsx`
- `saidas/operacional/auditoria_diaria_lote_6630_64_fev_v68.csv`

## Atualização V68

- manutenção da fase atual sobre a baseline V67;
- abertura da Etapa 4 da F1 por refinamento temporal de `fonte_elegivel_pagamento`;
- manutenção da checagem de release como gate obrigatório;
- preservação integral da lógica econômica e da materialização já aberta na F1.

## Evidências observáveis da V68

- o diagnóstico de `fonte_elegivel_pagamento` passa a exibir `pagamento_id`, `data_pagamento`, elegibilidade temporal e motivo de bloqueio;
- o resumo passa a exibir `total_pagamentos_alvo`, `total_fontes_pagamento` e `pagamentos_com_alguma_fonte_elegivel`;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

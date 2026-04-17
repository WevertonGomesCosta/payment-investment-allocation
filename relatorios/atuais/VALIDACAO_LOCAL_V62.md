# Validação local V62

## Escopo validado

- identidade da baseline atualizada para V62;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` aberta;
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

- `saidas/operacional/relatorio_operacional_v62.xlsx`

## Atualização V62

- manutenção da nova fase sobre a baseline V61 limpa;
- manutenção da checagem de release como gate obrigatório;
- abertura da Etapa 3 da F1 por materialização de `fonte_elegivel_pagamento`, sem tocar no motor financeiro.

## Evidências observáveis da V62

- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py` retorna `status_validacao: OK` e imprime o quadro materializado de fontes elegíveis;
- o release checker continua aprovando a baseline sem ruído estrutural;
- os comandos canônicos seguem executando sem regressão funcional.

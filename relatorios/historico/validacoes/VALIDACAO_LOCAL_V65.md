# Validação local V65

## Escopo validado

- identidade da baseline atualizada para V65;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- reorganização da seção `Situação atual` no console para separar lotes exauridos e lotes ativos;
- reorganização da aba `Situação atual` da planilha com quatro tabelas de lotes;
- recebidos auditáveis preservados na mesma aba/seção.

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

- `saidas/operacional/relatorio_operacional_v65.xlsx`

## Atualização V65

- manutenção da nova fase sobre a baseline V64;
- manutenção da checagem de release como gate obrigatório;
- separação de lotes exauridos e lotes ativos na saída atual do console e da planilha;
- preservação dos recebidos auditáveis e do motor financeiro.

## Evidências observáveis da V65

- o console passa a exibir a seção `Situação atual` com blocos distintos para `lotes exauridos` e `lotes ativos`;
- cada bloco de lotes exibe duas tabelas: identificação/tempo e valores atuais;
- a aba `Situação atual` passa a conter quatro tabelas de lotes, além do bloco de recebidos auditáveis;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

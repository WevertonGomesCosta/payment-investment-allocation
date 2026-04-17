# Validação local V66

## Escopo validado

- identidade da baseline atualizada para V66;
- checagem mínima de release mantida como gate obrigatório;
- contrato mínimo da F1 preservado e validado;
- materialização executável de `recebido_auditavel` preservada;
- materialização executável de `fonte_elegivel_pagamento` preservada;
- remoção da tabela detalhada de recebidos da seção `Situação atual` no console;
- remoção da tabela detalhada de recebidos da aba `Situação atual` da planilha;
- criação da aba `Fechamento econômico atual` na planilha;
- normalização pós-replay de resíduos sub-limiar validada;
- correção observável do `Lote 4124,75 fev.` na situação atual.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python scripts/diagnostico/inspecionar_contrato_f1.py`
- `python scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 4124,75 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 4124,75 fev."`
- `python scripts/verificar_release_baseline.py`
- `python scripts/inspecionar_contrato_f1.py`
- `python scripts/inspecionar_recebidos_auditaveis.py`
- `python scripts/inspecionar_fontes_elegiveis_pagamento.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v66.xlsx`
- `saidas/operacional/auditoria_diaria_lote_4124_75_fev_v66.xlsx`
- `saidas/operacional/auditoria_diaria_lote_4124_75_fev_v66.csv`

## Atualização V66

- manutenção da fase atual sobre a baseline V65;
- manutenção da checagem de release como gate obrigatório;
- remoção da tabela detalhada de recebidos da situação atual;
- separação do fechamento econômico em aba própria da planilha;
- correção do residual sub-limiar do `Lote 4124,75 fev.`.

## Evidências observáveis da V66

- o console deixa de exibir a tabela `situação atual de todos os recebidos (inclui exauridos)`;
- a aba `Situação atual` deixa de conter essa tabela detalhada;
- a planilha passa a conter a aba `Fechamento econômico atual`;
- o `Lote 4124,75 fev.` continua classificado como exaurido, mas deixa de exibir `Bruto`, `Líquido` e `Saldo rem` positivos abaixo do limiar operacional;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

# Validação local V67

## Escopo validado

- identidade da baseline atualizada para V67;
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

## Atualização V67

- manutenção da fase atual sobre a baseline V66;
- substituição dos rótulos operacionais `misto` por `uso_pre_aplicacao_com_aporte_posterior` e `pagamento_e_aplicacao`;
- manutenção da checagem de release como gate obrigatório;
- preservação integral da lógica econômica e da materialização já aberta na F1.

## Evidências observáveis da V67

- os diagnósticos de recebidos passam a exibir `uso_pre_aplicacao_com_aporte_posterior` no lugar de `misto`;
- os resumos passam a exibir `pagamento_e_aplicacao` no lugar de destino `misto`;
- os comandos canônicos seguem executando sem regressão funcional;
- o release checker continua aprovando a baseline em estado limpo final.

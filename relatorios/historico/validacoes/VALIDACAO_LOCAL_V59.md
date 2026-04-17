# Validação local V59

## Escopo validado

- identidade da baseline atualizada para V59;
- remoção do ramo residual `menos_1_dia`;
- consistência do índice documental vigente;
- checagem mínima automática de release;
- wrappers antigos preservados.

## Execução validada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/verificar_release_baseline.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`
- `python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."`
- `python scripts/verificar_release_baseline.py`

## Artefatos gerados

- `saidas/operacional/relatorio_operacional_v59.xlsx`

## Atualização V59

- limpeza de artefatos efêmeros (`__pycache__` e `.pyc`) do pacote final;
- atualização da documentação vigente para a versão atual;
- remoção do código morto residual associado ao fluxo `menos_1_dia`;
- adição de uma checagem mínima automática de release.

## Evidências observáveis da V59

- o índice documental passa a apontar apenas para os arquivos vigentes da baseline atual;
- o ramo `menos_1_dia` deixa de existir no código ativo da baseline;
- a checagem de release falha quando encontra artefatos efêmeros, inconsistência documental ou referências ativas indevidas;
- os comandos canônicos continuam executando na baseline atual.

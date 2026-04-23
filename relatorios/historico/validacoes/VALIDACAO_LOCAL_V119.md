# Validação local V119

## Execuções mínimas

- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado observado

- a integração curta permaneceu executável;
- o switching deixou de ser apenas proxy estrutural;
- o histórico do cenário passou a registrar custo fiscal realizado, valor migrado, carência/liquidez do destino e valor terminal estimado do lote;
- a baseline V119 permaneceu íntegra no release checker.

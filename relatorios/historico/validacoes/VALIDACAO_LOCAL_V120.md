# Validação local V120

## Rotinas executadas

- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado observado

- o planejador temporal passou a ranquear por ganho terminal econômico mínimo real estimado;
- no recorte curto, nenhum switching permaneceu elegível após custo fiscal + reprojeção terminal + penalidade incremental de carência/liquidez;
- o cenário vencedor passou a ser o `baseline_sem_switching`;
- a baseline V120 permaneceu íntegra no release checker.

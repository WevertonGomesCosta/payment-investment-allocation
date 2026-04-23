# Validação local V121

## Rotinas executadas

- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado observado

- o planejador temporal passou a comparar múltiplos destinos elegíveis por lote;
- no recorte curto, foram considerados 12 destinos elegíveis por lote;
- nenhum destino alternativo permaneceu elegível após custo fiscal + reprojeção terminal + penalidade incremental de carência/liquidez;
- o cenário vencedor permaneceu o `baseline_sem_switching`;
- a baseline V121 permaneceu íntegra no release checker.

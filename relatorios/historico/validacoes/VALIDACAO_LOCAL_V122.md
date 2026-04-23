# Validação local V122

## Execuções mínimas realizadas

- `python scripts/diagnostico/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado esperado

- o relatório multihorizonte deve ser gerado em `relatorios/atuais/TESTE_HORIZONTE_LONGO_PLANEJADOR_SWITCHING_TEMPORAL_V122.md`;
- a baseline V122 deve permanecer íntegra no release checker;
- a planilha operacional V122 deve ser gerada normalmente.

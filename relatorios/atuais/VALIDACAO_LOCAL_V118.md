# Validação local V118

## Escopo validado

Validação da primeira integração funcional mínima da camada temporal conjunta.

## Rotinas executadas

- `python scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `python scripts/diagnostico/inspecionar_contrato_v117.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `python scripts/diagnostico/verificar_release_baseline.py`

## Resultado observado

- o recorte curto foi executado no horizonte `2026-04-20` a `2026-05-20`;
- foram avaliados 3 cenários:
  - `baseline_sem_switching`;
  - `switching_temporal_top1`;
  - `switching_temporal_top2`;
- o melhor cenário no vetor lexicográfico auditável foi `switching_temporal_top1`;
- os 15 pagamentos do recorte foram cobertos integralmente nos 3 cenários;
- a V118 passou a gerar vetor central auditável e patrimônio terminal proxy por cenário;
- o release checker permaneceu em `OK` para a baseline V118.

## Conclusão

A V118 deixa de ser apenas uma camada documental e passa a ter integração funcional mínima real, sem ainda substituir a frente central V108 nem abrir solver global completo.

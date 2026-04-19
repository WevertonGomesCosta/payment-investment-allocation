# Validação local V94

## Comandos executados

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/inspecionar_auditoria_runner_futuro_shadow.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`

## Resultado

- baseline V94 compilando e executando;
- auditoria dos casos críticos do runner shadow executando e gerando artefatos;
- release checker aprovado em estado limpo.

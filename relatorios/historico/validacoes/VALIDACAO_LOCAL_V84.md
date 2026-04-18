# Validação local V84

## Bateria executada

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado

- baseline V84 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico da auditoria estrutural executando;
- release checker fechando em `OK` no pacote final limpo.

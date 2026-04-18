# Validação local V87

## Bateria executada

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado

- baseline V87 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico do mapa da execução principal do Script 2 executando;
- release checker fechando em `OK` no pacote final limpo.

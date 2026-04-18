# Validação local V85

## Bateria executada

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado

- baseline V85 compilando e executando;
- relatório operacional vigente gerado;
- diagnóstico da auditoria estrutural executando;
- release checker fechando em `OK` no pacote final limpo.

- wrappers raiz previamente quebrados executando diretamente;
- `python scripts/verificar_release_baseline.py` executando corretamente;
- `python scripts/inspecionar_switching_economico_shadow.py` executando corretamente;
- `python scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` executando corretamente;
- `python scripts/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py` executando corretamente;
- `python scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` executando corretamente.

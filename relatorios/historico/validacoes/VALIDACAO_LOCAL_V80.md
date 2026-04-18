# Validação local V80

## Bateria executada

- `python -m compileall aplicacao nucleo scripts`
- `python scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`
- `python aplicacao/console/principal.py`
- `python scripts/operacional/gerar_planilha_operacional.py`
- `PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py`

## Resultado

- baseline V80 compilando e executando;
- auditoria cirúrgica dos 42 casos reaproveitáveis gerada com sucesso;
- `release checker` aprovado em estado limpo;
- sem alteração do fluxo principal, do motor financeiro e do `proxy v3` congelado.

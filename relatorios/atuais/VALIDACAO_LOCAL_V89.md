# Validação local V89

## Bateria executada

```bash
python -m compileall aplicacao nucleo scripts
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
PYTHONDONTWRITEBYTECODE=1 python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado

- baseline V89 compilando e executando com os dados atualizados;
- relatório operacional vigente gerado;
- diagnóstico do mapa da execução principal do Script 2 executando;
- release checker fechando em `OK` no pacote final limpo.


## Validação adicional da V89

- atualização dos dados canônicos `dados/dados_financeiros.xlsx` e `dados/cache_bcb.json`;
- rerun do benchmark shadow agrupado vs individual com dados atualizados;
- release checker aprovado em estado limpo.

# Validação local V53

## Comandos executados

```bash
python -m compileall aplicacao nucleo scripts
python aplicacao/principal.py
python aplicacao/console/principal.py
python scripts/gerar_planilha_operacional.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/inspecionar_base.py
python scripts/diagnostico/inspecionar_base.py
```

## Resultado

- execução preservada nos caminhos antigos;
- execução preservada nos caminhos novos canônicos;
- planilha operacional gerada em `saidas/operacional/relatorio_operacional_v53.xlsx`;
- auditoria diária gerada em `saidas/operacional/`;
- sem regressão funcional observável na baseline.

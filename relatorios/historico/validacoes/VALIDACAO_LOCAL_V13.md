# Validação local V13

Esta validação foi executada no ambiente disponível antes da entrega da V13.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais observadas

- saída do console com severidade explícita (`OK`, `AVISO`, `ERRO`);
- resumo consolidado das camadas canônicas;
- carregamento correto de config, planilha, carteira, inventário, gastos e calendário/taxas base.

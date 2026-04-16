# Validação local V22

Esta validação foi executada no ambiente disponível antes da entrega da V22.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais observadas

- carregamento do `config_atualizado.json`;
- localização da planilha `dados_financeiros.xlsx`;
- leitura das abas primárias do contrato;
- carregamento do núcleo financeiro mínimo com lotes financeiros, fator líquido e amostra de saque;
- ausência de abertura de solver, replay, switching econômico e relatório financeiro atual.

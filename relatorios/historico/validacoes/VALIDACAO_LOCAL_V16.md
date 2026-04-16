# Validação local V16

Esta validação foi executada no ambiente disponível antes da entrega da V16.

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
- matching canônico reforçado dos produtos aportados;
- resumo shadow mais consolidado no console;
- ausência de erro fatal na baseline.

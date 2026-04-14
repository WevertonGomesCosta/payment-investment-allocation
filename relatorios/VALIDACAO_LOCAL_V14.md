# Validação local V14

Esta validação foi executada no ambiente disponível antes da entrega da V14.

## Escopo da derivação

Centralização de utilitários neutros transversais em módulo próprio, sem abertura de replay do passado, núcleo financeiro, switching ou CDI operacional.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado resumido

- `python aplicacao/principal.py`: retorno 0
- `python scripts/inspecionar_base.py`: retorno 0

## Evidências principais observadas

- baseline carregada corretamente como V14;
- `config_atualizado.json` localizado corretamente;
- `dados_financeiros.xlsx` localizado corretamente;
- carteira canônica, inventário canônico, gastos canônicos e calendário financeiro/taxas base carregados com sucesso;
- console permaneceu organizado e auditável após a refatoração;
- centralização dos utilitários neutros não alterou o comportamento mínimo esperado da baseline.

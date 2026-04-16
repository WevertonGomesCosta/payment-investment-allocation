# Validação local V12

Esta validação foi executada no ambiente disponível antes da entrega da V12.

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
- construção da carteira canônica;
- construção do inventário canônico;
- construção dos gastos canônicos;
- construção da camada neutra de calendário financeiro e taxas/CDI base;
- saída inicial de console organizada por blocos.

## Observação

Dependências não críticas para esta etapa mínima podem continuar ausentes no ambiente,
desde que não impeçam a validação básica da baseline.

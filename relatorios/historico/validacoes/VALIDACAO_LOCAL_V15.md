# Validação local V15

Esta validação foi executada no ambiente disponível antes da entrega da V15.

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
- leitura correta das três abas primárias do contrato;
- manutenção da carteira canônica, inventário canônico, gastos canônicos e calendário/taxas base;
- construção de lotes shadow normalizados;
- derivação de eventos brutos de aporte histórico;
- reconciliação observado vs shadow marcada como equivalente;
- trilha técnica de eventos ordenada de forma determinística;
- saída de console organizada e sem erro fatal.

## Escopo mantido fora desta versão

Continuam fora da V15:
- relatório econômico;
- cálculo líquido/fiscal;
- replay shadow de contas;
- núcleo financeiro;
- switching diagnóstico econômico.

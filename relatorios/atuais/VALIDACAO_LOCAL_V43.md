# Validação local V43

## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

## Resultado da execução local
A baseline executou sem erro com a nova base `dados/dados_financeiros.xlsx`.

Resumo observado no console:
- versão reportada: `V43`
- data de referência: `2026-04-16`
- abas primárias lidas com sucesso: `Carteira`, `Inventário de Lotes`, `Todos os Gastos`
- carteira canônica: `91` produtos
- inventário canônico: `15` lotes
- gastos canônicos: `214` despesas
- triagem preliminar: `70` candidatos
- núcleo financeiro mínimo: `10` lotes financeiros
- planilha operacional gerada: `saidas/relatorio_operacional_v43.xlsx`

## Critérios validados
- adoção da nova planilha canônica em `dados/dados_financeiros.xlsx`;
- limpeza do pacote final, sem logs brutos soltos nem saídas antigas acumuladas;
- manutenção apenas da documentação vigente em `relatorios/atuais/`;
- preservação da trilha histórica em `relatorios/historico/`.

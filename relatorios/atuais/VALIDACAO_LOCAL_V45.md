# Validação local V45

## Procedimentos executados
- `python -m compileall aplicacao nucleo scripts`
- `python aplicacao/principal.py`
- `python scripts/gerar_planilha_operacional.py`

## Resultado da execução local
A baseline executou sem erro após a revisão documental e a atualização da versão para `V45`.

Resumo observado no console:
- versão reportada: `V45`
- data de referência: `2026-04-16`
- abas primárias lidas com sucesso: `Carteira`, `Inventário de Lotes`, `Todos os Gastos`
- carteira canônica: `91` produtos
- inventário canônico: `15` lotes
- gastos canônicos: `214` despesas
- triagem preliminar: `70` candidatos
- núcleo financeiro mínimo: `10` lotes financeiros
- planilha operacional gerada: `saidas/relatorio_operacional_v45.xlsx`

## Critérios validados
- revisão documental sem regressão operacional na baseline;
- separação entre contrato executável vigente e backlog contratual futuro;
- manutenção da hierarquia documental em `relatorios/atuais/` e `relatorios/historico/`;
- geração operacional preservada após a atualização de versão.

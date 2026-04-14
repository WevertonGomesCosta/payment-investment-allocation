# Validação local da V6

Esta validação foi executada localmente antes da entrega da versão V6, em conformidade
com a regra operacional de testar e corrigir o que for possível antes do envio do
repositório.

## Comandos executados

```bash
python aplicacao/principal.py
python scripts/inspecionar_base.py
```

## Resultado observado

- Execução concluída sem erro fatal nos dois comandos.
- `config_atualizado.json` foi localizado corretamente em `dados/`.
- `dados_financeiros.xlsx` foi localizado corretamente em `dados/`.
- As abas primárias `Carteira`, `Inventário de Lotes` e `Todos os Gastos` foram lidas com sucesso.
- As abas auxiliares `Resumo Mensal` e `Todas as Carteiras` foram identificadas e separadas como não operacionais na inspeção atual.
- A saída do console permaneceu organizada em blocos legíveis.

## Achados relevantes desta validação

- O ambiente atual executou a baseline mesmo com `pulp` e `workalendar` ausentes, porque a
  etapa atual não depende deles para a inspeção mínima.
- Não foi identificado bug impeditivo adicional na baseline V6 dentro do escopo desta validação.

## Observação

Esta validação não substitui as próximas auditorias comparativas dos scripts-base nem a
validação funcional das etapas futuras de domínio. Ela apenas confirma a estabilidade
mínima da baseline V6 entregue nesta etapa.

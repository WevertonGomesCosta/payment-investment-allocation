# Baseline fixa V41

## Escopo
A V41 consolida a auditoria da seção **Situação atual — lotes ativos** para eliminar divergência entre console, planilha operacional e cálculo interno.

## Ajustes desta versão
- a tabela de lotes ativos passou a recalcular `Bruto` e `Líquido` explicitamente na `data_referência`, usando `valor_bruto_em_data(...)` e `valor_liquido_em_data(...)`;
- a coluna `Valor original` foi adicionada ao console e à aba `Situação atual`;
- a planilha operacional passou a ser gerada como `relatorio_operacional_v41.xlsx`.

## Regra operacional mantida
A data de referência continua sendo a data atual da execução, com fallback controlado do último fator CDI disponível quando o cache não contiver o próprio dia.

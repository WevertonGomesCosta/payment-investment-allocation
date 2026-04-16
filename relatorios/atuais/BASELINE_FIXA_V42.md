# Baseline fixa V42

## Escopo
A V42 corrige a divergência da seção **Situação atual — lotes ativos** quando o cache CDI já contém o fator do fechamento útil imediatamente anterior à data de referência.

## Ajustes desta versão
- a situação atual passou a usar uma **data econômica efetiva** para exibição dos lotes ativos;
- quando a série CDI já alcança o fechamento útil imediatamente anterior à data de referência, a saída deixa de extrapolar um dia adicional sobre a data corrente;
- quando a série CDI ainda está atrasada em relação a esse fechamento útil, a saída mantém a foto já bridged pelo fallback anterior;
- a regra foi aplicada tanto no console quanto na aba `Situação atual` da planilha operacional.

## Regra operacional desta versão
A data de referência continua sendo a data atual da execução para contexto operacional. A exibição da **Situação atual** usa a última foto econômica coerente com o fechamento útil disponível, evitando acréscimo indevido de um dia adicional de rendimento quando o cache já contém o último fechamento útil.

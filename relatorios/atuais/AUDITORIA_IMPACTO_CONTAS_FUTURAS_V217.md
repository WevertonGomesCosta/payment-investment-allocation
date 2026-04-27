# AUDITORIA DE IMPACTO SOBRE CONTAS FUTURAS — V217

## Status

`V217_AUDITORIA_IMPACTO_CONTAS_FUTURAS_REAIS`

A V216 foi aceita como candidata funcional após auditoria dos CSVs reais: 8 lotes planejados promovidos, 3 pagamentos consumindo lotes planejados, invariante válida nos promovidos, liquidez/carência compatíveis e nenhuma dupla contagem na escolha final.

A V217 abre a próxima etapa controlada: comparar o impacto dos aportes planejados sobre as contas futuras reais antes de qualquer promoção formal de baseline.

## Escopo positivo

- rodar o mesmo recorte real com aportes planejados desabilitados;
- rodar o mesmo recorte real com aportes planejados habilitados;
- comparar pagamento a pagamento;
- medir déficit, cobertura, custo fiscal, perda terminal, penalidade de liquidez e fonte escolhida;
- listar lotes planejados efetivamente promovidos;
- gerar alertas se houver aumento de déficit, uso sem cobertura integral ou invariante inválida em promovidos.

## Escopo negativo

- não promover baseline;
- não alterar lógica econômica da V216;
- não alterar contrato mestre;
- não alterar saída canônica;
- não mexer na estrutura diária congelada.

## Comando

```bash
python scripts/diagnostico/auditar_impacto_contas_futuras_v217.py --real
```

## Saídas esperadas

- `saidas/diagnostico/impacto_contas_futuras_v217_resumo_real.csv`
- `saidas/diagnostico/impacto_contas_futuras_v217_comparativo_pagamentos_real.csv`
- `saidas/diagnostico/impacto_contas_futuras_v217_lotes_planejados_real.csv`
- `saidas/diagnostico/impacto_contas_futuras_v217_alertas_real.csv`

## Critério de avanço

A versão seguinte só deve considerar promoção de baseline se a V217 real não gerar alertas críticos e se o cenário com aportes planejados preservar ou melhorar cobertura das contas futuras.

# Recomputação sequencial central V108

A V108 recalibra a `recomputacao_sequencial_central_v1` da V107 com três mudanças estruturais mínimas na frente central:

1. penalidade explícita de escassez futura para pagamentos `PROTEGIDA`;
2. prioridade intraclasse operacional no mesmo dia;
3. fallback auditável de **sem fonte viável**.

## Objetivo da V108

Reduzir violações de `PROTEGIDA` e tornar a frente central mais fiel à métrica canônica mínima central, sem reabrir o solver global completo e sem voltar a uma lógica de otimização local do bloco crítico.

## Resultado esperado

A V108 deve ser lida como calibração da frente central, com foco em:

- preservar liquidez útil para `PROTEGIDA` futura;
- melhorar a ordenação de pagamentos protegidos no mesmo dia;
- evitar saídas enganosas quando não há mais fonte economicamente viável.

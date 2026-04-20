# Recomputação sequencial central V109

A V109 recalibra a `recomputacao_sequencial_central_v1` da V107 com três mudanças estruturais mínimas na frente central:

- proteção reforçada para `SEMIPROTEGIDA_A_CARTAO` material
- cap na penalidade de escassez futura para `PROTEGIDA`
- distinção auditável entre `sem fonte viável` e `fonte preservada por reserva`

Além disso, a V109 mantém a frente central como eixo principal do projeto.

1. penalidade explícita de escassez futura para pagamentos `PROTEGIDA`;
2. prioridade intraclasse operacional no mesmo dia;
3. fallback auditável de **sem fonte viável**.

## Objetivo da V109

Reduzir violações de `PROTEGIDA` e tornar a frente central mais fiel à métrica canônica mínima central, sem reabrir o solver global completo e sem voltar a uma lógica de otimização local do bloco crítico.

## Resultado esperado

A V109 deve ser lida como calibração da frente central, com foco em:

- preservar liquidez útil para `PROTEGIDA` futura;
- melhorar a ordenação de pagamentos protegidos no mesmo dia;
- evitar saídas enganosas quando não há mais fonte economicamente viável.

# 02_contrato_exaustao_controlada_remanescentes.md — RD-2026-04-28-09A

## Princípio

Remanescentes baixos positivos não devem permanecer indefinidamente fragmentando a carteira se puderem ser usados de forma auditável em uma conta futura, isoladamente ou em combinação com outro lote/fonte.

Essa regra não autoriza ajuste manual. Ela cria um candidato formal de decisão: `combinacao_exaustao_residual`.

## Definição operacional

Um candidato `combinacao_exaustao_residual` consiste em:

1. selecionar um lote com remanescente baixo positivo;
2. usar integralmente o saldo líquido disponível desse lote em um pagamento futuro;
3. complementar o pagamento com outro lote/fonte elegível;
4. zerar o lote residual sem gerar saldo negativo;
5. manter cobertura integral da conta;
6. comparar o resultado contra a alocação baseline.

## Condições de elegibilidade

| Critério | Regra |
|---|---|
| Saldo residual | Deve ser positivo e abaixo do limiar operacional definido no config ou na rodada |
| Consumo real | Deve haver evidência de que o lote é fonte consumida/sugerida, não apenas reserva |
| Cobertura | A conta deve ser integralmente coberta |
| Complemento | O complemento deve vir de lote/fonte elegível |
| Liquidez | Todos os lotes usados devem estar líquidos na data |
| Carência | Nenhuma carência pode ser violada |
| Fiscalidade | IR/IOF devem ser calculados pelo mesmo motor oficial |
| Cronologia | Recebidos futuros só podem ser usados após disponibilidade |
| Saldo final | Nenhum lote pode ficar com saldo negativo |
| Auditabilidade | A saída deve registrar residual usado, complemento e saldo final |

## Função objetivo

A função objetivo principal permanece sendo o patrimônio líquido terminal com penalizações de risco/liquidez já previstas no modelo oficial.

A exaustão residual só pode ser promovida se:

1. melhorar o objetivo terminal; ou
2. empatar economicamente dentro de limiar material; ou
3. piorar de forma materialmente irrelevante e reduzir fragmentação operacional, desde que o contrato permita essa tolerância.

## Critério secundário

Quando houver empate econômico ou diferença materialmente irrelevante, o motor pode preferir a alternativa que:

- reduz fragmentação;
- exaure remanescentes baixos;
- melhora auditabilidade operacional;
- evita micro-saldos persistentes;
- simplifica a recomendação de pagamentos futuros.

## Critérios de rejeição

O candidato deve ser rejeitado se:

- gerar cobertura parcial;
- gerar saldo negativo;
- violar liquidez, carência, fiscalidade ou cronologia;
- usar lote apenas marcado como reserva sem evidência de consumo;
- piorar materialmente o patrimônio terminal;
- comprometer pagamentos futuros;
- mascarar erro de alocação existente.

## Saída auditável obrigatória

Toda promoção ou rejeição deve registrar:

| Campo | Conteúdo |
|---|---|
| Pagamento | Conta/data/valor |
| Lote residual | Identificação do lote com saldo baixo |
| Valor residual usado | Valor líquido usado do lote residual |
| Fonte complementar | Lote/fonte que completa a conta |
| Saldo final residual | Saldo final do lote residual, esperado zero |
| Comparação baseline | Resultado da alocação original |
| Diferença econômica | Ganho/perda terminal estimada |
| Motivo da decisão | Promoção ou rejeição |
| Gates avaliados | Liquidez, carência, fiscalidade, cronologia, cobertura, saldo |

## Escopo desta rodada

Esta rodada aprova o contrato metodológico, mas não altera o motor.

A implementação futura deve reaproveitar a lógica existente de combinação mínima e seleção econômica, evitando caminho paralelo ou regra ad hoc.

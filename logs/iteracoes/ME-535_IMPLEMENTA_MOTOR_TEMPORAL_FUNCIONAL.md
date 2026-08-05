# ME-535 — implementa motor temporal funcional

- Branch: `me535-motor-temporal-funcional`
- Base: `aa501a04ef5e8d76d387c8999f0e5d489a20e62f`
- Natureza: alteração decisória controlada nas Etapas 4–7.

## Implementado

1. enriquecimento econômico e fiscal do `EstadoTemporalInicial`;
2. construção dos cinco pacotes normativos;
3. trajetórias independentes a partir do mesmo estado inicial;
4. pagamentos com alocação monofonte ou multifonte dentro do pacote;
5. switching integral com ticket, carência, liquidez e destino elegível;
6. valoração por patrimônio líquido terminal;
7. seleção determinística por `argmax`;
8. propagação stateful do pacote vencedor;
9. promoção da matriz econômica ao ledger;
10. gate bloqueante de evidência econômica;
11. testes sintéticos e contrato de validação real antes do merge.

## Não alterado

- dados financeiros;
- cache BCB;
- console;
- XLSX;
- `Situação Atual`;
- Etapas 9–11;
- PRs #551 e #552.

## Regra de fechamento

A frente somente pode ser considerada concluída após execução real de `python aplicacao/principal.py` com aprovação das Etapas 5–11 e ausência de divergência material causada pelo núcleo.

# Motor recomendação pagamentos + switching V114

## Papel da V114

A V114 não substitui a baseline principal da frente central (**V108**). Ela adiciona uma camada operacional orientada à pergunta prática do projeto:

> qual lote usar para pagar cada conta e quando vale fazer switching antes do pagamento?

## Estratégias comparadas por conta

Para cada pagamento futuro, o motor compara três famílias:

1. **sem switching**: usar a recomendação central atual sem realocação prévia;
2. **switching simples**: aplicar oportunidade shadow elegível da fonte/lote antes do pagamento;
3. **combinação mínima**: combinar fonte principal e fonte reserva quando isso melhora cobertura.

## Saída operacional principal

A saída central da V114 é um quadro por conta com:

- estratégia recomendada;
- lote recomendado;
- lote reserva;
- necessidade de switching;
- data sugerida;
- origem e destino do switching;
- ganho líquido estimado do switching;
- cobertura esperada;
- motivo da recomendação.

## Governança

- a V108 continua como baseline principal da frente central;
- a V114 é uma camada **operacional/consultiva** sobre a baseline principal;
- o motor não reabre solver global completo.

# Métrica canônica mínima central

Este documento formaliza a métrica mínima que deverá governar a futura `recomputacao_sequencial_central_v1`.

## Finalidade

A métrica canônica mínima central existe para impedir que o projeto volte a ser guiado por ganhos locais isolados — por exemplo, melhora de uma âncora específica — sem conexão explícita com o resultado conjunto do cenário.

## Princípio

A métrica central deve responder à pergunta:

> entre dois cenários auditáveis de pagamentos e uso de lotes, qual preserva melhor o objetivo econômico terminal do projeto, respeitando governança operacional mínima?

## Comparador hierárquico mínimo

Até nova decisão explícita, a comparação entre cenários deve seguir esta ordem de prioridade:

1. **Violações de pagamentos `PROTEGIDA`**
2. **Déficit líquido total dos pagamentos**
3. **Número de pagamentos sem cobertura integral**
4. **Patrimônio líquido terminal proxy do cenário**
5. **Destruição estratégica de lotes relevantes**
6. **Fragmentação residual e deterioração evitável da liquidez futura**

## Forma recomendada de implementação

### Comparador lexicográfico

A forma mínima recomendada é um comparador lexicográfico auditável:

\[
M_{central}(c) =
(
V_p,
D_t,
N_{sem},
-P_{term},
E_{estrat},
F_{liq}
)
\]

Onde:

- \(V_p\) = número ou severidade agregada de violações em pagamentos `PROTEGIDA`
- \(D_t\) = déficit líquido total dos pagamentos
- \(N_{sem}\) = número de pagamentos sem cobertura integral
- \(P_{term}\) = patrimônio líquido terminal proxy do cenário
- \(E_{estrat}\) = penalidade por destruição estratégica de lotes relevantes
- \(F_{liq}\) = penalidade por fragmentação residual e piora desnecessária da liquidez futura

**Menor é melhor**, exceto em \(P_{term}\), que entra com sinal invertido para manter a convenção lexicográfica de minimização.

### Observação

Se, por necessidade prática, a comparação for implementada como score escalar, a hierarquia acima deve continuar preservada por pesos dominantes ou regras equivalentes claramente auditáveis.

## Interpretação operacional mínima

### 1. Pagamentos `PROTEGIDA`
Nenhum cenário que viole pagamentos `PROTEGIDA` pode ser considerado melhor apenas por melhorar a cobertura de uma âncora local ou o excesso local de uma decisão instantânea.

### 2. Déficit líquido total
Entre dois cenários sem violação adicional de `PROTEGIDA`, deve prevalecer o que reduz mais o déficit líquido total dos pagamentos.

### 3. Número de pagamentos sem cobertura integral
Se o déficit total ficar equivalente, deve prevalecer o cenário que deixa menos pagamentos sem cobertura integral.

### 4. Patrimônio líquido terminal proxy
Somente depois da proteção operacional mínima é que o projeto deve privilegiar o cenário de melhor patrimônio terminal proxy.

### 5. Destruição estratégica de lotes
Cenários que consomem precocemente lotes estratégicos devem ser penalizados, principalmente quando isso reduz a capacidade futura de pagamento, aporte ou switching.

### 6. Fragmentação residual
A métrica deve evitar soluções que espalham resgates sem ganho real, aumentam sobras ineficientes ou deterioram a liquidez futura sem justificativa econômica.

## O que esta métrica não é

Esta métrica **não** é:

- score local de um único pagamento;
- score proxy instantâneo da decisão local v1;
- métrica limitada à cobertura de um bloco curto;
- regra automática de promoção de experimentos locais.

## Uso previsto na próxima etapa

A futura `recomputacao_sequencial_central_v1` deve:

- recalcular a melhor fonte a cada pagamento com estado residual atualizado;
- comparar alternativas locais com base nesta métrica central mínima;
- manter rastreabilidade por lote;
- documentar no console e na planilha os componentes relevantes do comparador central.

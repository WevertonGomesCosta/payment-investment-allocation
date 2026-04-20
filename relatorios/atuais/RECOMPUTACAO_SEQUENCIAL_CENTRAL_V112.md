# Recomputação Sequencial Central V112

A V112 implementa a `recomputacao_sequencial_central_v2` como evolução da frente central após a V108.

## Mudanças estruturais

- troca a penalidade agregada de escassez futura por **reserva crítica por fonte**;
- calcula **demanda marginal** para `PROTEGIDA` em janelas de 7/14/21 dias;
- explicita **reserva crítica total**, **orçamento livre** e **referências de dependência** por fonte;
- preserva a hierarquia central do projeto sem reabrir a linha de exceção para cartão material.

## Objetivo

Reduzir sobrepreservação e buscar ganho líquido central sem custo alto em `PROTEGIDA`, mantendo a frente central como eixo principal.

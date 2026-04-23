# Recalibração do planejador temporal de switching — V120

## Objetivo

Substituir o ranqueamento por ganho proxy simples por um ranqueamento por **ganho terminal econômico mínimo real estimado**.

## Componentes incorporados

- custo fiscal estimado do resgate;
- patrimônio terminal reprojetado da origem até o fim do recorte;
- patrimônio terminal reprojetado do destino após reinvestimento líquido;
- penalidade incremental de carência/liquidez baseada na janela adicional de indisponibilidade;
- score final de ranqueamento econômico.

## Resultado no recorte curto

No recorte até 2026-05-20, nenhum candidato de switching permaneceu elegível após a recalibração.

Os principais candidatos ficaram com ganho terminal econômico mínimo estimado negativo, incluindo:
- `Lote 6630,64 fev.`: `-2.59`;
- `Lote 3000 mar. B`: `-9.47`;
- `Lote 3000 mar. V`: `-10.34`;
- `Lote 8500 mar.`: `-84.58`;
- `Lote 5680 abr.`: `-0.70`.

## Interpretação

A V120 evita que o simulador central gaste capacidade com switchings que parecem bons por proxy, mas já chegam economicamente dominados no próprio planejador temporal.

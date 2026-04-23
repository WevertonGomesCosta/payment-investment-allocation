# Expansão multidestino do planejador temporal de switching — V121

## Objetivo

Expandir o `planejador_switching_temporal_v1` para comparar múltiplos destinos elegíveis por lote usando o mesmo `ganho_terminal_economico_minimo_estimado` introduzido na V120.

## Componentes incorporados

- lista de destinos elegíveis construída a partir da triagem do motor;
- comparação por lote contra até 12 destinos elegíveis no recorte curto;
- exclusão de destino idêntico ao produto de origem do lote;
- ranqueamento econômico único para todos os destinos testados;
- identificação explícita do melhor destino por lote.

## Resultado no recorte curto

No recorte até 2026-05-20, nenhum destino alternativo permaneceu elegível após a expansão multidestino.

Os melhores destinos por lote ficaram, ainda assim, economicamente negativos:
- `Lote 6630,64 fev.` → `Tesouro Educa+ 2027`: `-2.07`;
- `Lote 3000 mar. B` → `Tesouro Educa+ 2027`: `-8.90`;
- `Lote 3000 mar. V` → `Tesouro Educa+ 2027`: `-9.78`;
- `Lote 8500 mar.` → `Tesouro Educa+ 2027`: `-82.98`;
- `Lote 5680 abr.` → `Tesouro Educa+ 2032`: `-0.70`.

## Interpretação

A V121 mostra que o problema do recorte não era apenas a escolha do destino padrão `Tesouro Educa+ 2032`. Mesmo comparando múltiplos destinos elegíveis, nenhum deles sobreviveu economicamente no recorte curto quando custo fiscal, carência e patrimônio terminal reprojetado foram considerados.

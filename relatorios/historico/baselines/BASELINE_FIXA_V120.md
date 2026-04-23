# Baseline fixa V120

A V120 é a baseline **temporal mínima recalibrada no planejador de switching**.

## Papel da V120

A V120 preserva:
- o contrato V117 do motor conjunto temporal;
- a frente central V108 como referência contratual;
- a camada operacional V116 como referência local por conta;
- a segunda integração econômica mínima da V119 no simulador.

E acrescenta:
- recalibração do `planejador_switching_temporal_v1`;
- ranqueamento por `ganho_terminal_economico_minimo_estimado`;
- incorporação prévia de custo fiscal, carência incremental e patrimônio terminal reprojetado antes do simulador central.

## Escopo efetivo da V120

A V120 ainda não é solver global completo.
Ela é uma baseline de **triagem temporal economicamente mais coerente**, voltada a evitar envio de switchings estruturalmente ruins ao simulador central.

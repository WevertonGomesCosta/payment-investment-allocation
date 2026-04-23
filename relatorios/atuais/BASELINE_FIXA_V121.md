# Baseline fixa V121

A V121 é a baseline **temporal mínima expandida para múltiplos destinos elegíveis no planejador de switching**.

## Papel da V121

A V121 preserva:
- o contrato V117 do motor conjunto temporal;
- a frente central V108 como referência contratual;
- a camada operacional V116 como referência local por conta;
- a segunda integração econômica mínima da V119 no simulador;
- a recalibração econômica mínima do planejador introduzida na V120.

E acrescenta:
- expansão do `planejador_switching_temporal_v1` para múltiplos destinos elegíveis por lote;
- comparação multidestino com o mesmo `ganho_terminal_economico_minimo_estimado`;
- identificação explícita de quando o destino padrão falha e nenhum destino alternativo sobrevive economicamente.

## Escopo efetivo da V121

A V121 ainda não é solver global completo.
Ela é uma baseline de **triagem temporal multidestino economicamente mais coerente**, voltada a testar se alternativas ao destino padrão melhoram o cenário antes da simulação central.

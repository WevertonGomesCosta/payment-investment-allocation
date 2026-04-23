# Baseline fixa V122

A V122 é a baseline **diagnóstica multihorizonte do planejador temporal de switching**.

## Papel da V122

A V122 preserva:
- a frente central V108;
- a camada temporal V117–V121 já integrada;
- a expansão multidestino do `planejador_switching_temporal_v1`.

E acrescenta:
- um teste explícito de horizonte mais longo no planejador;
- uma comparação entre 30, 60, 90 e 120 dias;
- evidência de quando o custo fiscal inicial deixa de dominar completamente o switching.

## Escopo efetivo da V122

A V122 não altera a lógica econômica do simulador central.
Ela acrescenta instrumentação diagnóstica para decidir se o próximo passo deve continuar no planejador ou migrar candidatos positivos para simulação central controlada.

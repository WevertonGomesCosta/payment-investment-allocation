# Alocador pagamentos terminal — V141

## Escopo da etapa

A V141 implementa a **Fase 1 de absorção dos modelos do Script 1** no `alocador_pagamentos_terminal_v1`, incorporando:
- `score_hibrido_5p_fonte`
- `penalidade_cliff_idade`
- `oportunidade_vpl_marginal`

Essas heurísticas entram como:
- score auxiliar por fonte;
- desempate econômico;
- ordenação interna da combinação mínima.

## Regra de decisão da V141

A decisão principal continua subordinada à métrica terminal do alocador.
Depois disso, a ordenação fina entre candidatos passa a usar a chave:
1. `score_terminal_comparativo`
2. `score_hibrido_5p_fonte`
3. `penalidade_cliff_idade`
4. `oportunidade_vpl_marginal`
5. penalidades estratégicas e de liquidez já existentes

## Efeito esperado

- menor resgate de lote aportado próximo de cliff ruim;
- melhor distinção entre cobertura local e cobertura economicamente correta;
- menor uso cosmético de combinação mínima.

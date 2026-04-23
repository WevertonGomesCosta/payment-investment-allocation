# Auditoria dos casos críticos do runner futuro shadow

## Objetivo

Esta auditoria explica os casos sem cobertura integral do benchmark shadow do runner de simulação futura do Script 2 correto e mantém, ao final, um subbloco específico dos casos multifonte.

## Resultado central

1. O problema dominante do runner shadow é a perda de cobertura integral, não os poucos casos multifonte.
2. A maior parte dos casos críticos ocorre por **ausência total de liquidez no dia**, depois da primeira quebra de cobertura.
3. Os 3 casos multifonte devem ser lidos como subbloco final da auditoria e não como frente principal de absorção.

## Decisão operacional

A baseline V93 mantém o runner futuro apenas como benchmark shadow e prioriza a leitura causal dos casos sem cobertura integral antes de qualquer nova absorção do Script 2 legado.

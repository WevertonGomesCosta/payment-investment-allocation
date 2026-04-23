# Modelos do Script 1

Camada reservada para absorção incremental das heurísticas do Script 1 que ainda são úteis para maximizar patrimônio líquido terminal na alocação de pagamentos.

## Estado atual

A V142 mantém o contrato da V140 e implementa a Fase 1 no alocador:

### Fase 1 — integração imediata ao alocador
- `score_hibrido_5p_fonte`
- `penalidade_cliff_idade`
- `oportunidade_vpl_marginal`

### Fase 2 — abertura controlada de combinação
- `seletor_modo_individual_ou_combinado`
- `triagem_topk_fontes_combinacao`

## Arquivos principais
- `contrato_modelos_script1.py`
- `registro_modelos_script1.py`
- `heuristicas_fase1.py`

## Regra central
Os modelos do Script 1 entram como heurísticas auxiliares do `alocador_pagamentos_terminal_v1` e não como substituição do comparador terminal nem do comparador híbrido de switching.


## Validação ampliada V142

- `relatorios/atuais/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_AMPLIADO_V142.md`

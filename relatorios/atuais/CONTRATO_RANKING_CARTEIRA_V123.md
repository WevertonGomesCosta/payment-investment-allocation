
# Contrato operacional do ranking Carteira-only — V123

## Objetivo
Integrar ao projeto principal o método estabilizado de score/ranking da aba `Carteira`, sem mutar a planilha-fonte e sem reabrir a metodologia congelada.

## Escopo da V123
- entrada oficial: somente a aba `Carteira`;
- fonte contratual: `config/carteira_contract_v123.json`;
- parâmetros fixos: `config/fixed_parameters_ranking_carteira.json`;
- artefatos separados: ranking completo, top 30, destinos de switching e resumo de validação.

## Decisão de integração
O projeto passa a usar o ranking Carteira-only como fonte preferencial de destinos do `planejador_switching_temporal_v1`. A `triagem_motor` permanece como fallback e camada proxy, não como ranking principal de produtos.

## Implementação mínima desta versão
Nesta etapa, o núcleo do cálculo do ranking canônico é lido da própria aba `Carteira` já estabilizada e a penalização adicional de prazo no consolidado é recalculada internamente para produzir `SAOF_Final_Prazo`, `Rank_Consolidado_Prazo_Ativos` e `Delta_Rank`.

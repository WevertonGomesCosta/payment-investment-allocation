# Mapa das heurísticas prioritárias do Script 1 para pagamentos — V140

## Resumo executivo

A absorção do Script 1 deve começar por heurísticas que alteram a **qualidade da escolha da fonte de pagamento**, e não por blocos de treino, exportação ou solver completo.

## Heurísticas prioritárias

| Ordem | Heurística | Status V140 | Papel inicial no alocador |
|---|---|---:|---|
| 1 | `score_hibrido_5p_fonte` | contratada | score auxiliar por fonte |
| 2 | `penalidade_cliff_idade` | contratada | desempate tributário/fiscal |
| 3 | `oportunidade_vpl_marginal` | contratada | reforço terminal marginal |
| 4 | `seletor_modo_individual_ou_combinado` | contratada para fase 2 | decidir quando abrir combinação mínima |
| 5 | `triagem_topk_fontes_combinacao` | contratada para fase 2 | reduzir custo combinatório |

## O que entra primeiro no fluxo

### Bloco A — ranqueamento econômico das fontes
Usa H1 + H2 + H3 para produzir um score econômico auxiliar de cada fonte elegível.

### Bloco B — decisão local entre fontes simples
Usa o score auxiliar para priorizar:
- `saldo_disponivel`
- `lote_nao_aportado`
- `lote_aportado`
- `cenario_switching_elegivel`

### Bloco C — abertura controlada de combinação mínima
Só depois de H1–H3 estarem estáveis.
Usa H4 + H5.

## Sinais de que a integração está correta
- menor uso de `combinacao_minima_fontes` cosmética;
- menor resgate de lote aportado próximo de cliff ruim;
- maior coerência entre escolha local e patrimônio terminal projetado.

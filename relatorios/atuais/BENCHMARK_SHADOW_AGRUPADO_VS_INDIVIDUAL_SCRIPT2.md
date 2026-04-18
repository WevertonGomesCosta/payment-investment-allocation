
# Benchmark shadow do teste agrupado vs individual do Script 2

## Escopo

Este benchmark reproduz, em modo shadow e auditável, a camada de governança do Script 2 legado que comparava execução **agrupada por dia** versus **individual**. Nesta baseline, a absorção ocorre sobre a decisão local vigente com `proxy v3`, sem migrar o runner legado bruto.

## Método aplicado na V88

- modo **individual**: reutiliza `decisao_local_v1` vigente, pagamento a pagamento;
- modo **agrupado**: agrega os pagamentos por data e recalcula a decisão local v1 com as fontes e o saldo disponível agregados por data;
- comparação em métrica comum do próprio `proxy v3`, usando:
  - custo proxy ponderado por valor;
  - excesso líquido total;
  - mudança de lote dominante por data.

## Regras desta etapa

1. O benchmark é **somente diagnóstico**.
2. O resultado **não** substitui o fluxo principal.
3. O benchmark **não** reabre o `proxy v3` automaticamente.
4. A recomendação agrupado vs individual é apenas uma régua de governança inspirada no Script 2 legado.

## Leitura operacional esperada

- Se o modo agrupado reduzir custo proxy e excesso de forma material, ele entra como hipótese de benchmark a ser reavaliada em etapa futura.
- Se o modo individual continuar melhor ou a diferença for inconclusiva, a baseline atual permanece governada pelo modo vigente da V88.

## Decisão da V88

A V88 **abre apenas o benchmark shadow** do teste agrupado vs individual do Script 2, sem absorver funcionalmente a orquestração legada.


## Atualização da V89

Com os arquivos canônicos `dados/dados_financeiros.xlsx` e `dados/cache_bcb.json` atualizados, o benchmark shadow agrupado vs individual foi rerodado e manteve o mesmo veredito operacional: `individual` segue como modo recomendado e permanecem **9 datas com mudança de lote dominante**, o que mantém válida a hipótese de uma auditoria fina apenas dessas datas.

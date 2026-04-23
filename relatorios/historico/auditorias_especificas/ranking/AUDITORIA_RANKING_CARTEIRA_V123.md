
# Auditoria técnica do ranking da Carteira — V123

## Achado principal
O ranqueamento usado pelo `planejador_switching_temporal_v1` não vinha do método Carteira-only estabilizado. Os destinos eram ordenados pela `triagem_motor`, baseada em score proxy contextual, o que permitia superexposição de Tesouro como destino padrão.

## Correção aplicada
- criação do pacote `nucleo/ranking_carteira_estabilizado.py`;
- leitura da aba `Carteira` completa como entrada única do ranking;
- uso do contrato e dos parâmetros fixos externos;
- cálculo interno da penalização adicional de prazo no consolidado;
- adoção do ranking Carteira-only como fonte preferencial de destinos do switching temporal.

## Efeito esperado
Produtos com score final prazo superior ao Tesouro deixam de ser rebaixados por uma triagem proxy transitória antes da avaliação econômica de longo prazo.

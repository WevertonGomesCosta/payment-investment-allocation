# Estrutura do repositório V100

## Camada nova da V100

A V100 introduz uma camada intermediária entre a decisão local e qualquer leitura de plano futuro: a auditoria temporal da `decisao_local_v1`, que reaplica a sequência dos pagamentos sugeridos com depleção cumulativa da mesma fonte ao longo do tempo.

## Papel da V100

A nova camada não substitui o método vigente e não replaneja pagamentos. Seu papel é apenas separar:

- validade local já aprovada;
- coerência sequencial futura;
- primeira quebra por fonte;
- necessidade de reescolha dinâmica após exaustão cumulativa.

## Artefatos novos

- `nucleo/auditoria_temporal_decisao_local.py`;
- `scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py`;
- `scripts/inspecionar_auditoria_temporal_decisao_local.py`;
- nova aba `Auditoria temporal` na planilha operacional V100.

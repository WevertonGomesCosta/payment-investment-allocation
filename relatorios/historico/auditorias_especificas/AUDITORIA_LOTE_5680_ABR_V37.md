# AUDITORIA ESPECÍFICA — LOTE 5680 ABR. — V37

## Cadastro do lote
- lote: `Lote 5680 abr.`
- data de recebimento: `2026-04-06`
- data de aplicação: `2026-04-14`
- valor original: `R$ 5.680,00`
- produto: `CDB Neon Planejado 150% CDI - 60 dias`

## Regra aplicada
Entre `2026-04-06` e `2026-04-14` inclusive, o lote é tratado como **caixa pré-aplicação**:
- disponível para pagamentos;
- sem rendimento;
- sem IR/IOF de investimento;
- sem bloqueio por carência.

## Eventos históricos auditados
| Data | Conta | Fase | Bruto | Líquido | Saldo remanescente |
|---|---|---:|---:|---:|---:|
| 2026-04-08 | Pelada e churrasco | caixa_pre_aplicacao | 70,00 | 70,00 | 5.610,00 |
| 2026-04-10 | Concerto Carro | caixa_pre_aplicacao | 434,75 | 434,75 | 5.175,25 |
| 2026-04-14 | Escola | caixa_pre_aplicacao | 151,71 | 151,71 | 5.023,54 |
| 2026-04-14 | Escola | caixa_pre_aplicacao | 206,80 | 206,80 | 4.816,74 |
| 2026-04-14 | Calça biola | caixa_pre_aplicacao | 45,00 | 45,00 | 4.771,74 |
| 2026-04-14 | Velt | caixa_pre_aplicacao | 18,75 | 18,75 | 4.752,99 |

## Conclusão
O desvio material observado anteriormente não vinha de uma nova falha de rendimento, mas da ausência de modelagem da janela entre recebimento e aplicação.

Com a regra da V37, o lote deixa de gerar resíduos materiais e passa a ter leitura operacional coerente com a base informada pelo usuário.

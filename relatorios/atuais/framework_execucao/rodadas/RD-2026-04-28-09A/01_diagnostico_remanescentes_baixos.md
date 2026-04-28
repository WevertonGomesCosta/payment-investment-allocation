# 01_diagnostico_remanescentes_baixos.md — RD-2026-04-28-09A

## Objetivo
Formalizar o diagnóstico metodológico dos remanescentes baixos identificados na RD-09, separando lote sugerido, lote reserva e oportunidade real de exaustão controlada.

## Evidência de entrada
| Evidência | Arquivo |
|---|---|
| Eventos dos lotes de menor folga | `relatorios\atuais\framework_execucao\rodadas\RD-2026-04-28-09\evidencias\01_eventos_lotes_menor_folga.csv` |
| Alertas dos lotes de menor folga | `relatorios\atuais\framework_execucao\rodadas\RD-2026-04-28-09\evidencias\02_alertas_lotes_menor_folga.csv` |
| Resumo JSON por lote | `relatorios\atuais\framework_execucao\rodadas\RD-2026-04-28-09\evidencias\03_resumo_lotes_menor_folga.json` |

## Remanescentes baixos considerados
| Lote | Eventos totais | Como sugerido | Como reserva | Menor saldo remanescente | Alertas | Interpretação |
|---|---:|---:|---:|---:|---:|---|
| `Lote 3600 mai.` | 10 | 10 | 0 | R$ 18,05 | 9 | Lote efetivamente sugerido e com remanescente baixo; candidato prioritário à exaustão controlada. |
| `Lote 3000 mar. B` | 95 | 4 | 91 | R$ 0,00 | 24 | Maioria das ocorrências é reserva; não interpretar como consumo efetivo sem trilha adicional. |

## Separação conceitual obrigatória
| Categoria | Significado | Pode fundamentar exaustão residual? |
|---|---|---|
| `lote_sugerido` | Fonte principal indicada para pagamento | Sim, se houver saldo baixo real após uso |
| `lote_reserva` | Fonte alternativa ou fallback registrado | Não, salvo se houver evidência de consumo efetivo |
| `lote_efetivamente_consumido` | Fonte cujo saldo foi reduzido na simulação/saída | Sim |
| `remanescente_baixo` | Saldo positivo abaixo de limiar operacional | Sim, como candidato, não como obrigação automática |
| `combinacao_exaustao_residual` | Uso integral do saldo residual + complemento de outra fonte | Sim, se passar nos gates econômicos |

## Diagnóstico
- `Lote 3600 mai.` é o caso mais direto: aparece como lote sugerido e atinge saldo remanescente baixo.
- `Lote 3000 mar. B` exige cautela: aparece muitas vezes como reserva, então a evidência bruta superestima sua participação operacional.
- A exaustão de remanescentes deve ser incorporada como candidato formal do motor, não como ajuste manual de saldo.

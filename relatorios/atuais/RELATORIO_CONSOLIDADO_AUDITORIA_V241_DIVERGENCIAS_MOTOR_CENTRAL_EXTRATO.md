# Relatório consolidado — auditoria V241 de divergências motor/central/extrato

## Objetivo

Consolidar a auditoria V241 registrada em `saidas/diagnostico/`, sintetizando as divergências entre motor de recomendação, simulador central e extrato operacional, sem mover ou remover os CSVs originais.

## Arquivos-fonte preservados

- `saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv`
- `saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv`

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa apenas consolida a auditoria V241 em relatório atual.

## Síntese executiva

| Métrica | Valor | Percentual |
|---|---:|---:|
| `total_pagamentos_auditados` | 149 | 100.0 |
| `linhas_com_origem_mista_detectada` | 148 | 99.33 |
| `divergencia_lote_motor_central` | 33 | 22.15 |
| `divergencia_lote_motor_extrato` | 33 | 22.15 |
| `divergencia_lote_central_extrato` | 0 | 0.0 |
| `divergencia_estrategia_motor_extrato` | 0 | 0.0 |
| `divergencia_cobertura_motor_central` | 0 | 0.0 |
| `divergencia_cobertura_motor_extrato` | 0 | 0.0 |
| `divergencia_cobertura_central_extrato` | 0 | 0.0 |
| `divergencia_saldo_motor_central` | 148 | 99.33 |
| `divergencia_saldo_motor_extrato` | 148 | 99.33 |
| `divergencia_saldo_central_extrato` | 0 | 0.0 |
| `divergencia_switching_motor_extrato` | 0 | 0.0 |

## Principais achados

- Pagamentos auditados: **149**.
- Linhas com origem mista detectada: **148** (99.33%).
- Divergências de lote entre motor e central: **33** (22.15%).
- Divergências de saldo entre motor e central: **148** (99.33%).
- Casos com necessidade de switching no motor: **36** (24.16%).
- Divergências de estratégia motor/extrato: **0**.
- Divergências de cobertura motor/central/extrato: **0**.
- Divergências de switching motor/extrato: **0**.

## Interpretação operacional

A auditoria V241 indica que a camada central e o extrato estão coerentes em lote, saldo, cobertura, estratégia e switching, pois as divergências central/extrato ficaram zeradas nas métricas agregadas. As divergências concentram-se na comparação do motor com a central/extrato, especialmente em saldo e, em menor grau, no lote recomendado.

A presença de origem mista em quase todas as linhas indica que os pagamentos avaliados combinam informações de diferentes camadas operacionais. Por isso, a auditoria V241 deve ser tratada como evidência de calibração entre motor, central e extrato, não como saída operacional final.

## Amostra dos casos com divergência de lote motor-central

| Pagamento | Data | Descrição | Valor | Lote motor | Lote central | Lote extrato | Estratégia motor | Estratégia extrato |
|---|---|---|---:|---|---|---|---|---|
| `despesa_auto_00082` | 2026-06-02 | Cartão NU | 580.0 | Lote 8500 mar. | Lote 3600 mai. | Lote 3600 mai. | switching_simples | switching_simples |
| `despesa_auto_00085` | 2026-06-08 | Claro | 120.0 | Lote 8500 mar. | Lote 3000 mar. V | Lote 3000 mar. V | switching_simples | switching_simples |
| `despesa_auto_00086` | 2026-06-10 | Ginástica Biola | 65.0 | Lote 8500 mar. | saldo_disponivel_geral | saldo_disponivel_geral | switching_simples | switching_simples |
| `despesa_auto_00087` | 2026-06-10 | Pelada | 50.0 | Lote 8500 mar. | saldo_disponivel_geral | saldo_disponivel_geral | switching_simples | switching_simples |
| `despesa_auto_00089` | 2026-06-11 | Cemig | 95.12 | Lote 8500 mar. | Lote 3600 mai. | Lote 3600 mai. | switching_simples | switching_simples |
| `despesa_auto_00090` | 2026-06-12 | Aluguel | 981.95 | Lote 8500 mar. | Lote 1800 jun. | Lote 1800 jun. | switching_simples | switching_simples |
| `despesa_auto_00091` | 2026-06-12 | Escola | 2831.4 | Lote 8500 mar. | Lote 5680 jun. | Lote 5680 jun. | switching_simples | switching_simples |
| `despesa_auto_00092` | 2026-06-15 | Internet | 132.4 | Lote 5680 abr. | Lote 3600 mai. | Lote 3600 mai. | switching_simples | switching_simples |
| `despesa_auto_00094` | 2026-06-19 | Condomínio | 113.31 | Lote 5680 abr. | Lote 3600 mai. | Lote 3600 mai. | switching_simples | switching_simples |
| `despesa_auto_00095` | 2026-07-02 | Cartão NU | 930.0 | Lote 5680 abr. | Lote 8500 mar. | Lote 8500 mar. | switching_simples | switching_simples |
| `despesa_auto_00096` | 2026-07-06 | Cemig SIM | 195.0 | Lote 5680 abr. | Lote 3600 mai. | Lote 3600 mai. | switching_simples | switching_simples |
| `despesa_auto_00097` | 2026-07-06 | Faxina Rosa | 950.0 | Lote 5680 abr. | Lote 1800 jun. | Lote 1800 jun. | switching_simples | switching_simples |

## Decisão documental

Os dois CSVs originais permanecem em `saidas/diagnostico/` como evidência diagnóstica bruta da V241. Este relatório passa a ser a síntese consolidada em `relatorios/atuais/`, mas não autoriza remoção, movimentação ou rebaixamento dos arquivos-fonte nesta etapa.

## Próxima ação operacional

A próxima etapa deve decidir se, após este consolidado, os dois CSVs V241 continuam necessários em `saidas/diagnostico/` ou se podem virar candidatos à remoção controlada futura. Essa decisão exige nova auditoria explícita e commit próprio.

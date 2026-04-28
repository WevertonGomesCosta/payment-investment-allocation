# Auditoria de conteúdo — saídas diagnósticas V241

## Objetivo

Auditar os 2 CSVs diagnósticos V241 em `saidas/diagnostico/`, avaliando se devem permanecer em `saidas/diagnostico/`, ser movidos futuramente para `relatorios/atuais/` como evidência consolidada, ou ser removidos após consolidação. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas auditoria de conteúdo e decisão preliminar.

## Arquivos avaliados

| Arquivo | Existe | Linhas | Tipo | Decisão preliminar |
|---|---|---:|---|---|
| `saidas\diagnostico\divergencias_motor_central_extrato_v241_resumo.csv` | sim | 13 | `RESUMO_DIAGNOSTICO` | `MANTER_EM_SAIDAS_DIAGNOSTICO_POR_ORA` |
| `saidas\diagnostico\divergencias_motor_central_extrato_v241_detalhe.csv` | sim | 149 | `DETALHE_DIAGNOSTICO` | `MANTER_EM_SAIDAS_DIAGNOSTICO_POR_ORA` |

## Interpretação preliminar

Os dois arquivos formam um par diagnóstico: o arquivo `resumo` preserva métricas agregadas e o arquivo `detalhe` preserva a auditoria linha a linha por pagamento. Como ambos se referem à V241 e documentam divergências entre motor, central e extrato, a decisão mais segura nesta etapa é mantê-los em `saidas/diagnostico/` até que exista um relatório consolidado específico sobre a auditoria V241.

## Métricas do arquivo de resumo

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

## Campos booleanos/divergências no arquivo de detalhe

| Campo | Ocorrências | Total | Percentual |
|---|---:|---:|---:|
| `divergencia_lote_motor_central` | 33 | 149 | 22.15 |
| `divergencia_lote_motor_extrato` | 33 | 149 | 22.15 |
| `divergencia_lote_central_extrato` | 0 | 149 | 0.0 |
| `divergencia_estrategia_motor_extrato` | 0 | 149 | 0.0 |
| `divergencia_cobertura_motor_central` | 0 | 149 | 0.0 |
| `divergencia_cobertura_motor_extrato` | 0 | 149 | 0.0 |
| `divergencia_cobertura_central_extrato` | 0 | 149 | 0.0 |
| `divergencia_saldo_motor_central` | 148 | 149 | 99.33 |
| `divergencia_saldo_motor_extrato` | 148 | 149 | 99.33 |
| `divergencia_saldo_central_extrato` | 0 | 149 | 0.0 |
| `divergencia_switching_motor_extrato` | 0 | 149 | 0.0 |
| `origem_mista_detectada` | 148 | 149 | 99.33 |
| `pagamento_totalmente_coberto_central` | 149 | 149 | 100.0 |
| `necessidade_switching_motor` | 36 | 149 | 24.16 |
| `necessita_switching_extrato` | 36 | 149 | 24.16 |

## Decisão desta etapa

Nenhum dos 2 CSVs diagnósticos V241 deve ser removido ou movido nesta etapa. A decisão preliminar é `MANTER_EM_SAIDAS_DIAGNOSTICO_POR_ORA` para ambos. Eles só devem ser movidos para `relatorios/atuais/` ou removidos após criação de um relatório consolidado específico da auditoria V241 e nova decisão explícita.

## Próxima ação operacional

A próxima etapa deve criar um relatório consolidado da auditoria V241 em `relatorios/atuais/`, com base nesses dois CSVs, ainda sem mover ou remover os arquivos originais.

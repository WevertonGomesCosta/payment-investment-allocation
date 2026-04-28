# Índice-mestre — validações históricas consolidadas

## Objetivo

Centralizar a leitura das validações históricas já consolidadas por faixa, preservando rastreabilidade sem depender da consulta cotidiana aos arquivos granulares em `relatorios/historico/validacoes/`.

## Regra de autoridade documental

Este índice tem valor histórico e organizacional. Ele não substitui a documentação normativa vigente em `relatorios/atuais/`, nem altera motor, dados, scripts operacionais ou saídas oficiais.

- Validações inventariadas: 116
- Menor versão detectada: V6
- Maior versão detectada: V140
- Arquivos granulares ainda não removidos nesta etapa.

## Relatórios consolidados por faixa

| Faixa | Relatório consolidado | Arquivos |
|---|---|---:|
| `V001_V030` | `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V001_V030.md` | 24 |
| `V031_V060` | `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V031_V060.md` | 21 |
| `V061_V090` | `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V061_V090.md` | 28 |
| `V091_V120` | `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V091_V120.md` | 24 |
| `V121_V150` | `relatorios/atuais/RELATORIO_CONSOLIDADO_VALIDACOES_HISTORICAS_V121_V150.md` | 19 |

## Síntese por faixa

| Faixa | Leitura consolidada |
|---|---|
| `V001_V030` | Execuções locais iniciais, `aplicacao/principal.py`, inspeções de base, cache CDI/BCB, primeiros contratos e validações iniciais de lotes. |
| `V031_V060` | Compileall, inspeções da base, planilha operacional, valuation, CDI/cache, fallback de dados, organização arquitetural, release checker e Frente F1. |
| `V061_V090` | Frente F1, recebidos auditáveis, fontes elegíveis, saldo disponível, decisão local, proxy v2/v3, legado, shadow e auditoria estrutural. |
| `V091_V120` | Runner shadow, primeira quebra, observabilidade, recomputação sequencial, bloco crítico, motor pagamentos/switching e integração temporal mínima. |
| `V121_V150` | Planejador temporal, ranking Carteira-only, simulação central, multihorizonte, grade diária, comparador híbrido, lotes futuros, alocador terminal e Script 1. |

## Decisão sugerida

Com este índice-mestre e os cinco relatórios por faixa, a pasta granular `relatorios/historico/validacoes/` pode ser candidata à remoção controlada em etapa separada, desde que os relatórios consolidados permaneçam versionados.

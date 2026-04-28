# Relatório de decisão — arquivos REVISAO_MANUAL em relatorios/atuais

## Objetivo

Revisar os arquivos classificados como `REVISAO_MANUAL` na triagem de `relatorios/atuais/`, atribuindo uma decisão preliminar sem remover, mover ou renomear nenhum arquivo nesta etapa.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas documental e decisória.

- Arquivos em `REVISAO_MANUAL`: 17

## Resumo por decisão sugerida

| Decisão sugerida | Arquivos |
|---|---:|
| `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | 6 |
| `MANTER_ATE_REVISAO_MOTOR_DIAS_LOTES` | 2 |
| `MANTER_COMO_DOCUMENTO_VIGENTE` | 4 |
| `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | 5 |

## Decisão arquivo a arquivo

| Arquivo | Versão | Linhas | Decisão sugerida | Justificativa |
|---|---:|---:|---|---|
| `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md` |  | 331 | `MANTER_COMO_DOCUMENTO_VIGENTE` | Documento parece representar estado operacional, especificação, baseline ou orientação vigente. |
| `relatorios/atuais/LEIA-ME_OPERACIONAL.md` |  | 66 | `MANTER_COMO_DOCUMENTO_VIGENTE` | Documento parece representar estado operacional, especificação, baseline ou orientação vigente. |
| `relatorios/atuais/PLANO_LIMPEZA_REPOSITORIO_POS_RD.md` |  | 43 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/STATUS_LOCAL_IGNORADOS_POS_LIMPEZA.txt` |  | 44 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/CORRECAO_CIRURGICA_V200.md` | 200 | 22 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md` | 205 | 73 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/HOTFIX_UTILITARIOS_SERIES_V207.md` | 207 | 47 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/CORRECAO_SALDOS_FUTUROS_LOTES_V208.md` | 208 | 49 | `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA` | Documento parece ser hotfix/correção/plano auxiliar já potencialmente absorvido por relatórios ou estado atual. |
| `relatorios/atuais/INTEGRACAO_FUNCIONAL_APORTES_FUTUROS_V216.md` | 216 | 121 | `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | Documento registra frente técnica recente ainda relevante para interpretar decisões V216–V223. |
| `relatorios/atuais/CORRECAO_CALCULO_DIAS_LOTES_V218.md` | 218 | 92 | `MANTER_ATE_REVISAO_MOTOR_DIAS_LOTES` | Documento deve permanecer enquanto a frente de dias corridos, dias úteis, idade fiscal e rendimento de lotes não for fechada. |
| `relatorios/atuais/CORRECAO_REPRODUTIBILIDADE_DIAS_LOTES_V219.md` | 219 | 59 | `MANTER_ATE_REVISAO_MOTOR_DIAS_LOTES` | Documento deve permanecer enquanto a frente de dias corridos, dias úteis, idade fiscal e rendimento de lotes não for fechada. |
| `relatorios/atuais/GATE_ECONOMICO_APORTES_PLANEJADOS_V220.md` | 220 | 12 | `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | Documento registra frente técnica recente ainda relevante para interpretar decisões V216–V223. |
| `relatorios/atuais/HOTFIX_RESOLVER_CSV_GATE_ECONOMICO_V221.md` | 221 | 31 | `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | Documento registra frente técnica recente ainda relevante para interpretar decisões V216–V223. |
| `relatorios/atuais/HOTFIX_FLUXO_EFETIVO_GATE_ECONOMICO_V222.md` | 222 | 49 | `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | Documento registra frente técnica recente ainda relevante para interpretar decisões V216–V223. |
| `relatorios/atuais/CONSOLIDACAO_NOMINAL_GATE_IMPACTO_V223.md` | 223 | 34 | `MANTER_COMO_SUPORTE_TECNICO_RECENTE` | Documento registra frente técnica recente ainda relevante para interpretar decisões V216–V223. |
| `relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md` | 225 | 43 | `MANTER_COMO_DOCUMENTO_VIGENTE` | Documento parece representar estado operacional, especificação, baseline ou orientação vigente. |
| `relatorios/atuais/PROMOCAO_CONTROLADA_BASELINE_V225.md` | 225 | 84 | `MANTER_COMO_DOCUMENTO_VIGENTE` | Documento parece representar estado operacional, especificação, baseline ou orientação vigente. |

## Próxima decisão operacional

A próxima etapa deve revisar primeiro os arquivos marcados como `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA`, verificando se o conteúdo já está coberto por documentos vigentes, índices de rastreabilidade ou relatórios consolidados. Nenhuma remoção deve ocorrer sem uma auditoria explícita de cobertura documental.

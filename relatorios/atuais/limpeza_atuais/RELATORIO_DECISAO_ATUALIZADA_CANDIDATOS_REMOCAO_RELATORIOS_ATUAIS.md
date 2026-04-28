# Decisão atualizada — candidatos à remoção em relatorios/atuais

## Objetivo

Atualizar a decisão dos 6 arquivos previamente marcados como `CANDIDATO_CONSOLIDACAO_OU_REMOCAO_FUTURA`, incorporando o resultado da auditoria de conteúdo de `HOTFIX_CONSOLE_IMPORTS_V205.md`.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa apenas atualiza a decisão documental.

## Evidência incorporada

A auditoria de conteúdo de `HOTFIX_CONSOLE_IMPORTS_V205.md` comparou o hotfix contra `GOVERNANCA_ESTRUTURAL_V206.md` e `LEIA-ME_OPERACIONAL.md` e concluiu `NAO_REMOVER_AINDA`, pois havia linhas operacionais de prioridade alta sem cobertura suficiente.

## Resumo das decisões atualizadas

| Decisão atualizada | Arquivos |
|---|---:|
| `MANTER_ATE_COBERTURA_SER_REFORCADA` | 3 |
| `MANTER_E_REVISAR_MANUALMENTE` | 3 |

## Decisão arquivo a arquivo

| Arquivo | Cobertura anterior | Decisão anterior | Decisão atualizada | Motivo |
|---|---|---|---|---|
| `relatorios/atuais/PLANO_LIMPEZA_REPOSITORIO_POS_RD.md` | `SEM_COBERTURA_DETECTADA` | `MANTER_E_REVISAR_MANUALMENTE` | `MANTER_E_REVISAR_MANUALMENTE` | Nenhuma cobertura textual/nominal foi detectada; manter e revisar manualmente. |
| `relatorios/atuais/STATUS_LOCAL_IGNORADOS_POS_LIMPEZA.txt` | `SEM_COBERTURA_DETECTADA` | `MANTER_E_REVISAR_MANUALMENTE` | `MANTER_E_REVISAR_MANUALMENTE` | Nenhuma cobertura textual/nominal foi detectada; manter e revisar manualmente. |
| `relatorios/atuais/CORRECAO_CIRURGICA_V200.md` | `COBERTURA_FRACA` | `MANTER_ATE_COBERTURA_SER_REFORCADA` | `MANTER_ATE_COBERTURA_SER_REFORCADA` | A cobertura textual existe, mas ainda é fraca; manter até reforço documental. |
| `relatorios/atuais/HOTFIX_CONSOLE_IMPORTS_V205.md` | `COBERTURA_FORTE` | `CANDIDATO_REMOCAO_CONTROLADA_APOS_REVISAO_HUMANA` | `MANTER_ATE_COBERTURA_SER_REFORCADA` | A auditoria de conteúdo do hotfix V205 concluiu NAO_REMOVER_AINDA, pois há linhas operacionais de prioridade alta sem cobertura suficiente. |
| `relatorios/atuais/HOTFIX_UTILITARIOS_SERIES_V207.md` | `SEM_COBERTURA_DETECTADA` | `MANTER_E_REVISAR_MANUALMENTE` | `MANTER_E_REVISAR_MANUALMENTE` | Nenhuma cobertura textual/nominal foi detectada; manter e revisar manualmente. |
| `relatorios/atuais/CORRECAO_SALDOS_FUTUROS_LOTES_V208.md` | `COBERTURA_FRACA` | `MANTER_ATE_COBERTURA_SER_REFORCADA` | `MANTER_ATE_COBERTURA_SER_REFORCADA` | A cobertura textual existe, mas ainda é fraca; manter até reforço documental. |

## Decisão desta etapa

Nenhum dos 6 arquivos deve ser removido nesta etapa. `HOTFIX_CONSOLE_IMPORTS_V205.md`, antes classificado como candidato à remoção controlada após revisão humana, passa a ficar retido como `MANTER_ATE_COBERTURA_SER_REFORCADA`.

## Próxima ação operacional

A próxima etapa deve decidir se vale a pena reforçar a cobertura documental dos arquivos com `COBERTURA_FRACA` e `SEM_COBERTURA_DETECTADA`, ou simplesmente mantê-los como documentos auxiliares recentes até uma limpeza posterior mais ampla de `relatorios/atuais/`.

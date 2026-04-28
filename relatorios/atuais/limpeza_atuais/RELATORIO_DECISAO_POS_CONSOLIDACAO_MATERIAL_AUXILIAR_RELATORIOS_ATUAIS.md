# Decisão pós-consolidação — material auxiliar de limpeza/auditoria

## Objetivo

Registrar a decisão pós-consolidação dos 27 arquivos classificados como `MATERIAL_CONSOLIDAVEL`, separando evidência já coberta pelo relatório consolidado, evidência auxiliar ainda necessária, evidência sensível/operacional e itens que exigem revisão manual.

## Regra desta etapa

- Arquivos avaliados: 27
- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas decisória e documental.

## Resumo por classe pós-consolidação

| Classe pós-consolidação | Arquivos | Ação |
|---|---:|---|
| `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | 10 | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | 16 | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `EVIDENCIA_SENSIVEL_OPERACIONAL` | 1 | Manter até revisão posterior; contém evidência ligada a saídas/diagnósticos operacionais. |

## Resumo por classe e grupo funcional

| Classe | Grupo funcional | Arquivos |
|---|---|---:|
| `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | `auditoria_historico_saida_propria` | 1 |
| `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | `inventario_estrutura_pastas` | 3 |
| `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | `limpeza_scripts` | 5 |
| `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | `status_local_ignorados` | 1 |
| `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | `auditoria_relatorios_historico` | 12 |
| `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | `inventario_relatorios_historico` | 4 |
| `EVIDENCIA_SENSIVEL_OPERACIONAL` | `auditoria_saidas_diagnostico` | 1 |

## Decisão arquivo a arquivo

| Arquivo | Grupo funcional | Classe pós-consolidação | Ação |
|---|---|---|---|
| `relatorios/atuais/limpeza_estrutura/auditoria_refinada_historico_saida_propria_v203.csv` | `auditoria_historico_saida_propria` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_1.csv` | `inventario_estrutura_pastas` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_2.csv` | `inventario_estrutura_pastas` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_3.csv` | `inventario_estrutura_pastas` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_scripts/auditoria_referencias_candidatos_remocao.csv` | `limpeza_scripts` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_scripts/auditoria_refinada_referencias_candidatos_remocao.csv` | `limpeza_scripts` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_scripts/auditoria_wrappers_temporal_decisao.csv` | `limpeza_scripts` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_scripts/candidatos_remocao_scripts_diagnostico.csv` | `limpeza_scripts` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv` | `limpeza_scripts` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_estrutura/status_local_ignorados_estrutura.txt` | `status_local_ignorados` | `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` | Manter; ainda ajuda a auditar decisões de limpeza, scripts ou estrutura. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_artefatos_soltos.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_especificas_raiz.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_ranking.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_reorganizacao.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_shadow_legacy.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_temporal.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_contratos_intermediarios.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_documentacao_baseline.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_limpeza_repositorio.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_objetivo_final.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_reorganizacao_local_switching.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_validacoes_diarias.csv` | `auditoria_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico.csv` | `inventario_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_baselines.csv` | `inventario_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_estruturas.csv` | `inventario_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_validacoes.csv` | `inventario_relatorios_historico` | `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` | Pode virar candidata à remoção futura, em etapa separada, após conferência final do relatório consolidado. |
| `relatorios/atuais/limpeza_estrutura/auditoria_saidas_diagnostico.csv` | `auditoria_saidas_diagnostico` | `EVIDENCIA_SENSIVEL_OPERACIONAL` | Manter até revisão posterior; contém evidência ligada a saídas/diagnósticos operacionais. |

## Interpretação operacional

Os arquivos classificados como `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` são os únicos que podem ser avaliados como candidatos à remoção futura. Mesmo assim, esta etapa não autoriza remoção; ela apenas cria a lista decisória para eventual etapa posterior com `git rm` explícito e commit próprio.

Os arquivos classificados como `EVIDENCIA_AUXILIAR_AINDA_NECESSARIA` ou `EVIDENCIA_SENSIVEL_OPERACIONAL` devem permanecer no repositório por enquanto.

## Decisão desta etapa

Nenhum dos 27 arquivos será removido nesta etapa. A próxima etapa, se desejada, deve considerar apenas os `EVIDENCIA_JA_COBERTA_PELO_CONSOLIDADO` como candidatos à remoção controlada, mantendo todos os demais.

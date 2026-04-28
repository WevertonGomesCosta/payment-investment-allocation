# Decisão preliminar — MATERIAL_LIMPEZA_AUDITORIA em relatorios/atuais

## Objetivo

Reclassificar os arquivos marcados como `MATERIAL_LIMPEZA_AUDITORIA` na triagem de `relatorios/atuais/`, separando evidência permanente, material consolidável e itens que exigem revisão manual. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas documental e classificatória.

- Arquivos avaliados em `MATERIAL_LIMPEZA_AUDITORIA`: 39

## Resumo por decisão sugerida

| Decisão sugerida | Arquivos |
|---|---:|
| `EVIDENCIA_PERMANENTE_LIMPEZA` | 8 |
| `EVIDENCIA_PERMANENTE_OPERACIONAL` | 4 |
| `MATERIAL_CONSOLIDAVEL` | 27 |

## Interpretação operacional

| Decisão | Interpretação |
|---|---|
| `EVIDENCIA_PERMANENTE_OPERACIONAL` | Auditorias recentes ou documentos operacionais que não devem ser tratados como lixo de limpeza. |
| `EVIDENCIA_PERMANENTE_LIMPEZA` | Resumos e inventários que preservam a trilha da limpeza já executada. |
| `MATERIAL_CONSOLIDAVEL` | CSVs/TXTs auxiliares que podem ser consolidados futuramente antes de qualquer remoção. |
| `REVISAO_MANUAL_MATERIAL_LIMPEZA` | Arquivos que exigem inspeção humana antes de qualquer decisão. |

## Decisão arquivo a arquivo

| Arquivo | Linhas | Decisão sugerida | Próxima ação |
|---|---:|---|---|
| `relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md` | 791 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_estrutura/RESUMO_AUDITORIA_ESTRUTURAL_PASTAS.md` | 45 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_estrutura/RESUMO_INVENTARIO_BASELINES_HISTORICAS.md` | 54 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_estrutura/RESUMO_INVENTARIO_ESTRUTURAS_HISTORICAS.md` | 29 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_estrutura/RESUMO_INVENTARIO_RELATORIOS_HISTORICO.md` | 35 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_estrutura/RESUMO_INVENTARIO_VALIDACOES_HISTORICAS.md` | 23 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_scripts/RESUMO_AUDITORIA_REFINADA_CANDIDATOS_REMOCAO.md` | 22 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/limpeza_scripts/RESUMO_INVENTARIO_SCRIPTS_DIAGNOSTICO.md` | 30 | `EVIDENCIA_PERMANENTE_LIMPEZA` | Manter; documento preserva rastreabilidade da limpeza já executada. |
| `relatorios/atuais/AUDITORIA_CAMADA_SAIDA_CANONICA_V202.md` | 85 | `EVIDENCIA_PERMANENTE_OPERACIONAL` | Manter; documento registra auditoria operacional recente e não deve ser removido como material auxiliar. |
| `relatorios/atuais/AUDITORIA_CONSOLE_DIAGNOSTICO_V216.md` | 73 | `EVIDENCIA_PERMANENTE_OPERACIONAL` | Manter; documento registra auditoria operacional recente e não deve ser removido como material auxiliar. |
| `relatorios/atuais/AUDITORIA_IMPACTO_CONTAS_FUTURAS_V217.md` | 43 | `EVIDENCIA_PERMANENTE_OPERACIONAL` | Manter; documento registra auditoria operacional recente e não deve ser removido como material auxiliar. |
| `relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md` | 55 | `EVIDENCIA_PERMANENTE_OPERACIONAL` | Manter; documento registra auditoria operacional recente e não deve ser removido como material auxiliar. |
| `relatorios/atuais/limpeza_estrutura/auditoria_refinada_historico_saida_propria_v203.csv` | 51 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_artefatos_soltos.csv` | 3 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_especificas_raiz.csv` | 21 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_ranking.csv` | 5 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_reorganizacao.csv` | 5 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_shadow_legacy.csv` | 6 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_auditorias_temporal.csv` | 16 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_contratos_intermediarios.csv` | 22 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_documentacao_baseline.csv` | 7 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_limpeza_repositorio.csv` | 7 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_objetivo_final.csv` | 5 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_reorganizacao_local_switching.csv` | 12 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_relatorios_historico_validacoes_diarias.csv` | 9 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/auditoria_saidas_diagnostico.csv` | 3 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_1.csv` | 12 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_2.csv` | 34 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_pastas_profundidade_3.csv` | 48 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico.csv` | 413 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_baselines.csv` | 115 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_estruturas.csv` | 77 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/inventario_relatorios_historico_validacoes.csv` | 117 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_estrutura/status_local_ignorados_estrutura.txt` | 45 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_scripts/auditoria_referencias_candidatos_remocao.csv` | 34 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_scripts/auditoria_refinada_referencias_candidatos_remocao.csv` | 34 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_scripts/auditoria_wrappers_temporal_decisao.csv` | 8 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_scripts/candidatos_remocao_scripts_diagnostico.csv` | 34 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |
| `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv` | 80 | `MATERIAL_CONSOLIDAVEL` | Consolidar futuramente em índice/relatório único antes de qualquer remoção. |

## Decisão desta etapa

Nenhum arquivo da classe `MATERIAL_LIMPEZA_AUDITORIA` deve ser removido nesta etapa. Os arquivos marcados como `MATERIAL_CONSOLIDAVEL` podem ser avaliados em uma próxima rodada para criação de um relatório consolidado único de evidências auxiliares. Somente depois dessa consolidação deve ser considerada qualquer remoção controlada.

## Próxima ação operacional

A próxima etapa deve focar apenas nos arquivos `MATERIAL_CONSOLIDAVEL`, criando um índice/relatório consolidado dos CSVs e TXTs auxiliares, ainda sem remoção.

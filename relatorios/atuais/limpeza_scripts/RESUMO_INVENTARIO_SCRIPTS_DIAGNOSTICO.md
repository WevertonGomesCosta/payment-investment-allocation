# Inventário preliminar de `scripts/diagnostico/`

## Objetivo

Classificar scripts diagnósticos após a limpeza documental e remoção de `scripts/historico_raiz/`, sem apagar arquivos automaticamente.

## Resumo por categoria

| Categoria | Ação preliminar | Qtde |
|---|---|---:|
| auditoria_recente_motor_central | manter_por_enquanto | 1 |
| diagnostico_historico_antigo | candidato_remocao | 22 |
| diagnostico_historico_intermediario | candidato_remocao | 11 |
| diagnostico_recente_pos_baseline | avaliar | 7 |
| infra_diagnostico | manter_por_enquanto | 3 |
| inspecao_sem_versao_explicita | avaliar | 30 |
| outro | avaliar | 2 |
| release_check | manter | 2 |
| release_check | manter_por_enquanto | 1 |

## Critério de uso

- `manter`: scripts ainda úteis para release/check.
- `manter_por_enquanto`: scripts recentes ou estruturais que exigem revisão antes de remoção.
- `avaliar`: scripts que precisam de inspeção de uso/importação.
- `candidato_remocao`: scripts históricos antigos, provavelmente removíveis após conferência.

## Arquivo detalhado

- `relatorios\atuais\limpeza_scripts\inventario_scripts_diagnostico.csv`

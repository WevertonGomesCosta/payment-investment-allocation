# Auditoria da pasta saidas

## Objetivo

Auditar os arquivos rastreados em `saidas/`, separando preliminarmente saídas oficiais, diagnósticas, históricas, temporárias prováveis e itens que exigem revisão manual. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas inventário e classificação preliminar.

## Estado inicial

- Arquivos rastreados em `saidas/`: 4
- Entradas em `git status --short` antes da geração: 0

## Resumo por subpasta

| Subpasta | Arquivos |
|---|---:|
| `saidas/.gitkeep` | 1 |
| `saidas/diagnostico` | 2 |
| `saidas/operacional` | 1 |

## Resumo por extensão

| Extensão | Arquivos |
|---|---:|
| `.csv` | 2 |
| `.md` | 1 |
| `[sem_ext]` | 1 |

## Resumo por classe preliminar

| Classe | Arquivos | Ação |
|---|---:|---|
| `METADADO_ESTRUTURAL_MANTER` | 2 | Manter; arquivo estrutural da pasta. |
| `SAIDA_DIAGNOSTICO_AUDITAR` | 2 | Auditar; pode ser evidência diagnóstica necessária ou artefato removível após consolidação. |

## Decisão arquivo a arquivo

| Arquivo | Subpasta | Extensão | Tamanho bytes | Classe | Ação |
|---|---|---|---:|---|---|
| `saidas/.gitkeep` | `saidas/.gitkeep` | `[sem_ext]` | 0 | `METADADO_ESTRUTURAL_MANTER` | Manter; arquivo estrutural da pasta. |
| `saidas/operacional/README.md` | `saidas/operacional` | `.md` | 254 | `METADADO_ESTRUTURAL_MANTER` | Manter; arquivo estrutural da pasta. |
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_detalhe.csv` | `saidas/diagnostico` | `.csv` | 40352 | `SAIDA_DIAGNOSTICO_AUDITAR` | Auditar; pode ser evidência diagnóstica necessária ou artefato removível após consolidação. |
| `saidas/diagnostico/divergencias_motor_central_extrato_v241_resumo.csv` | `saidas/diagnostico` | `.csv` | 1092 | `SAIDA_DIAGNOSTICO_AUDITAR` | Auditar; pode ser evidência diagnóstica necessária ou artefato removível após consolidação. |

## Decisão desta etapa

Nenhum arquivo em `saidas/` deve ser removido ou movido com base apenas nesta auditoria. A próxima etapa deve revisar primeiro os itens classificados como `SAIDA_DIAGNOSTICO_AUDITAR`, pois diagnósticos costumam ser os candidatos mais prováveis a consolidação ou limpeza futura.

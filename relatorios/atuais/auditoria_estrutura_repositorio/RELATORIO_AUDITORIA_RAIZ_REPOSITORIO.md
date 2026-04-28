# Auditoria da raiz do repositório

## Objetivo

Auditar os arquivos rastreados diretamente na raiz do repositório, classificando sua função operacional e decidindo preliminarmente se devem permanecer na raiz, ser revisados para movimentação futura ou passar por revisão manual. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas documental e classificatória.

## Estado inicial

- Arquivos rastreados na raiz: 7
- Entradas em `git status --short` antes da geração: 0

## Resumo por classe

| Classe | Arquivos | Ação |
|---|---:|---|
| `MANTER_RAIZ_CONFIG_EXECUCAO` | 1 | Manter na raiz; arquivo esperado para instalação, dependências ou execução. |
| `MANTER_RAIZ_CONFIG_REPOSITORIO` | 3 | Manter na raiz; arquivo padrão de configuração do Git/editor. |
| `MANTER_RAIZ_DOCUMENTO_PADRAO` | 2 | Manter na raiz; arquivo padrão de apresentação/licença do repositório. |
| `REVISAR_AMBIENTE_IDE` | 1 | Revisar; arquivo de IDE pode ser legítimo, mas exige decisão explícita. |

## Decisão arquivo a arquivo

| Arquivo | Extensão | Linhas | Classe | Ação |
|---|---|---:|---|---|
| `requirements.txt` | `.txt` | 8 | `MANTER_RAIZ_CONFIG_EXECUCAO` | Manter na raiz; arquivo esperado para instalação, dependências ou execução. |
| `.editorconfig` | `[sem_ext]` | 12 | `MANTER_RAIZ_CONFIG_REPOSITORIO` | Manter na raiz; arquivo padrão de configuração do Git/editor. |
| `.gitattributes` | `[sem_ext]` | 6 | `MANTER_RAIZ_CONFIG_REPOSITORIO` | Manter na raiz; arquivo padrão de configuração do Git/editor. |
| `.gitignore` | `[sem_ext]` | 93 | `MANTER_RAIZ_CONFIG_REPOSITORIO` | Manter na raiz; arquivo padrão de configuração do Git/editor. |
| `LICENSE` | `[sem_ext]` | 21 | `MANTER_RAIZ_DOCUMENTO_PADRAO` | Manter na raiz; arquivo padrão de apresentação/licença do repositório. |
| `README.md` | `.md` | 178 | `MANTER_RAIZ_DOCUMENTO_PADRAO` | Manter na raiz; arquivo padrão de apresentação/licença do repositório. |
| `payment-investment-allocation.Rproj` | `.rproj` | 13 | `REVISAR_AMBIENTE_IDE` | Revisar; arquivo de IDE pode ser legítimo, mas exige decisão explícita. |

## Decisão desta etapa

Nenhum arquivo da raiz deve ser removido nesta etapa. Arquivos classificados como `MANTER_RAIZ_*` devem permanecer na raiz. Arquivos classificados como `REVISAR_*` ou `REVISAO_MANUAL_RAIZ` devem ser avaliados em etapa posterior, com decisão explícita antes de qualquer movimentação ou remoção.

## Próxima ação operacional

Após versionar esta auditoria, a próxima etapa deve revisar apenas os arquivos da raiz classificados como `REVISAR_POSSIVEL_ARTEFATO_AUXILIAR`, `REVISAR_AMBIENTE_IDE` ou `REVISAO_MANUAL_RAIZ`.

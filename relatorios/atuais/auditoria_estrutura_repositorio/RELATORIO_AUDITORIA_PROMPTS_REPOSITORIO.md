# Auditoria da pasta prompts

## Objetivo

Auditar os arquivos rastreados em `prompts/`, identificando o objetivo de cada arquivo e separando prompts operacionais, prompts de continuidade, templates, legados, possíveis temporários e itens que exigem revisão manual. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas inventário e classificação preliminar.

## Estado inicial

- Arquivos rastreados em `prompts/`: 8
- Entradas em `git status --short` antes da geração: 0

## Resumo por subpasta

| Subpasta | Arquivos |
|---|---:|
| `prompts/abertura_chat` | 1 |
| `prompts/auditoria` | 2 |
| `prompts/claude` | 1 |
| `prompts/codex` | 1 |
| `prompts/continuidade` | 1 |
| `prompts/gemini` | 1 |
| `prompts/simulacao` | 1 |

## Resumo por extensão

| Extensão | Arquivos |
|---|---:|
| `.md` | 8 |

## Resumo por classe preliminar

| Classe | Arquivos | Ação |
|---|---:|---|
| `PROMPT_CONTINUIDADE_MANTER` | 1 | Manter por ora; pode registrar continuidade operacional entre chats. |
| `PROMPT_OPERACIONAL_MANTER` | 1 | Manter por ora; pode orientar execução controlada do projeto. |
| `REVISAO_MANUAL_PROMPTS` | 6 | Revisar manualmente antes de mover ou remover. |

## Decisão arquivo a arquivo

| Arquivo | Subpasta | Extensão | Linhas | Classe | Ação |
|---|---|---|---:|---|---|
| `prompts/continuidade/PROMPT_CONTINUIDADE.md` | `prompts/continuidade` | `.md` | 41 | `PROMPT_CONTINUIDADE_MANTER` | Manter por ora; pode registrar continuidade operacional entre chats. |
| `prompts/abertura_chat/PROMPT_CORE.md` | `prompts/abertura_chat` | `.md` | 49 | `PROMPT_OPERACIONAL_MANTER` | Manter por ora; pode orientar execução controlada do projeto. |
| `prompts/auditoria/PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md` | `prompts/auditoria` | `.md` | 53 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |
| `prompts/auditoria/PROMPT_AUDITORIA_PREVENTIVA.md` | `prompts/auditoria` | `.md` | 55 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |
| `prompts/claude/PROMPT_CLAUDE_VALIDACAO.md` | `prompts/claude` | `.md` | 34 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |
| `prompts/codex/PROMPT_CODEX_IMPLEMENTACAO.md` | `prompts/codex` | `.md` | 43 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |
| `prompts/gemini/PROMPT_GEMINI_ADVERSARIAL.md` | `prompts/gemini` | `.md` | 35 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |
| `prompts/simulacao/PROMPT_SIMULACAO.md` | `prompts/simulacao` | `.md` | 33 | `REVISAO_MANUAL_PROMPTS` | Revisar manualmente antes de mover ou remover. |

## Decisão desta etapa

Nenhum arquivo em `prompts/` deve ser removido ou movido com base apenas nesta auditoria. A próxima etapa deve revisar primeiro os itens classificados como `REVISAO_MANUAL_PROMPTS`, `TEMPLATE_PROMPT_REVISAR`, `PROMPT_LEGADO_REVISAR` ou `POSSIVEL_TEMPORARIO_REVISAR`.

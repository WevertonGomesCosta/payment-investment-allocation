# Decisão — remoção da pasta prompts

## Objetivo

Registrar a decisão explícita de remover a pasta `prompts/` do repositório.

## Contexto

A auditoria inicial de `prompts/` identificou 8 arquivos rastreados:

| Classe preliminar | Arquivos |
|---|---:|
| `PROMPT_CONTINUIDADE_MANTER` | 1 |
| `PROMPT_OPERACIONAL_MANTER` | 1 |
| `REVISAO_MANUAL_PROMPTS` | 6 |

Embora a auditoria preliminar não tenha autorizado remoção automática, a decisão operacional posterior foi remover a pasta inteira.

## Arquivos a remover

- `prompts/abertura_chat/PROMPT_CORE.md`
- `prompts/auditoria/PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md`
- `prompts/auditoria/PROMPT_AUDITORIA_PREVENTIVA.md`
- `prompts/claude/PROMPT_CLAUDE_VALIDACAO.md`
- `prompts/codex/PROMPT_CODEX_IMPLEMENTACAO.md`
- `prompts/continuidade/PROMPT_CONTINUIDADE.md`
- `prompts/gemini/PROMPT_GEMINI_ADVERSARIAL.md`
- `prompts/simulacao/PROMPT_SIMULACAO.md`

## Justificativa

A pasta `prompts/` contém material auxiliar de condução operacional entre chats, validações externas e implementação controlada. Esses arquivos não são parte do motor, dos dados canônicos, da configuração central nem das saídas oficiais.

A decisão é remover a pasta para reduzir superfície documental auxiliar no repositório.

## Regra desta etapa

A remoção deve ser feita de forma controlada:

1. registrar este relatório;
2. remover apenas `prompts/`;
3. conferir `git diff --cached --name-status`;
4. confirmar que os arquivos removidos pertencem somente a `prompts/`;
5. fazer commit próprio;
6. confirmar `git status --short` limpo ao final.

## Decisão final

A pasta `prompts/` fica autorizada para remoção controlada do Git.

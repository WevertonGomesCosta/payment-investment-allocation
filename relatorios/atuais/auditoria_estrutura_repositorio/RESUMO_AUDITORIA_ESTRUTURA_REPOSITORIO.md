# Auditoria estrutural inicial do repositório

## Objetivo

Iniciar uma nova frente de revisão estrutural do repositório inteiro, pasta por pasta, para entender o objetivo de cada diretório e avaliar se seus arquivos devem ser mantidos, movidos, consolidados ou futuramente excluídos. Esta etapa não remove, move ou renomeia arquivos.

## Regra desta etapa

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Esta etapa é apenas inventário e classificação preliminar.

## Estado inicial

- Arquivos rastreados avaliados: 301
- Pastas de primeiro nível: 10
- Entradas em `git status --short` antes da geração: 0

## Resumo por pasta de primeiro nível

| Pasta | Arquivos | Objetivo preliminar | Decisão preliminar |
|---|---:|---|---|
| `[raiz]` | 7 | Arquivos de entrada/controle do projeto na raiz. | `AUDITAR_ARQUIVOS_RAIZ` |
| `aplicacao` | 9 | Camada de aplicação, console, execução e apresentação operacional. | `MANTER_AUDITAR_FUNCAO` |
| `config` | 3 | Configurações centrais do projeto. | `MANTER_AUDITAR_FUNCAO` |
| `dados` | 3 | Dados, planilhas, caches e insumos operacionais. | `MANTER_AUDITAR_FUNCAO` |
| `docs` | 2 | Pasta não classificada automaticamente; exige revisão manual. | `REVISAO_MANUAL_PASTA` |
| `nucleo` | 65 | Núcleo funcional, motores, simuladores e regras econômicas. | `MANTER_AUDITAR_FUNCAO` |
| `prompts` | 8 | Pasta não classificada automaticamente; exige revisão manual. | `REVISAO_MANUAL_PASTA` |
| `relatorios` | 125 | Documentação vigente, consolidada, histórica e de auditoria. | `MANTER_DOCUMENTACAO_AUDITAR_RESIDUOS` |
| `saidas` | 4 | Artefatos gerados, saídas oficiais, diagnósticas ou históricas. | `AUDITAR_ARTEFATOS_GERADOS` |
| `scripts` | 75 | Scripts de execução, diagnóstico, validação, auditoria ou compatibilidade. | `AUDITAR_SCRIPTS_EXECUCAO_DIAGNOSTICO` |

## Resumo por subpasta de segundo nível

| Subpasta | Arquivos |
|---|---:|
| `[raiz]` | 7 |
| `aplicacao` | 2 |
| `aplicacao/console` | 7 |
| `config` | 3 |
| `dados` | 3 |
| `docs/governanca` | 2 |
| `nucleo` | 47 |
| `nucleo/builders` | 3 |
| `nucleo/motor_diario` | 7 |
| `nucleo/pagamentos` | 5 |
| `nucleo/runners` | 3 |
| `prompts/abertura_chat` | 1 |
| `prompts/auditoria` | 2 |
| `prompts/claude` | 1 |
| `prompts/codex` | 1 |
| `prompts/continuidade` | 1 |
| `prompts/gemini` | 1 |
| `prompts/simulacao` | 1 |
| `relatorios` | 2 |
| `relatorios/atuais` | 123 |
| `saidas` | 1 |
| `saidas/diagnostico` | 2 |
| `saidas/operacional` | 1 |
| `scripts` | 6 |
| `scripts/auditoria` | 3 |
| `scripts/diagnostico` | 63 |
| `scripts/operacional` | 3 |

## Resumo por decisão preliminar

| Decisão preliminar | Arquivos |
|---|---:|
| `AUDITAR_ARQUIVOS_RAIZ` | 7 |
| `AUDITAR_ARTEFATOS_GERADOS` | 4 |
| `AUDITAR_SCRIPTS_EXECUCAO_DIAGNOSTICO` | 75 |
| `MANTER_AUDITAR_FUNCAO` | 80 |
| `MANTER_DOCUMENTACAO_AUDITAR_RESIDUOS` | 125 |
| `REVISAO_MANUAL_PASTA` | 10 |

## Resumo por extensão

| Extensão | Arquivos |
|---|---:|
| `.csv` | 26 |
| `.json` | 5 |
| `.md` | 120 |
| `.py` | 139 |
| `.rproj` | 1 |
| `.txt` | 3 |
| `.xlsx` | 1 |
| `[sem_ext]` | 6 |

## Ordem recomendada de revisão pasta por pasta

1. `[raiz]` — arquivos soltos na raiz, porque definem entrada e higiene geral do repositório.
2. `saidas` — maior risco de conter artefatos gerados ou resíduos operacionais.
3. `scripts` — separar execução canônica, diagnóstico, legado e wrappers.
4. `relatorios` — verificar se a limpeza documental encerrada ficou coerente.
5. `dados` — confirmar o que é dado canônico, cache, insumo ou artefato derivado.
6. `config` — manter com cautela; fonte central de regras.
7. `nucleo` — manter; auditar apenas organização funcional.
8. `aplicacao` — manter; auditar console/entrada/saída operacional.
9. `tests` ou `testes` — manter; avaliar cobertura e atualidade.
10. Demais pastas — revisar manualmente.

## Decisão desta etapa

Nenhuma pasta ou arquivo deve ser removido com base apenas neste inventário. A próxima etapa deve começar pela pasta `[raiz]`, listando arquivos soltos e decidindo se cada um deve permanecer na raiz, ser movido para documentação/configuração ou ser auditado para remoção futura.

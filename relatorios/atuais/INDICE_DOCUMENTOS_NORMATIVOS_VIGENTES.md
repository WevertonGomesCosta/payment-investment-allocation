# Índice curto — documentos normativos vigentes

## Objetivo

Registrar os documentos normativos vigentes de maior autoridade em `relatorios/atuais/`, indicando a função principal de cada arquivo e sua hierarquia de leitura.

## Regra deste índice

- Arquivos removidos: 0
- Arquivos movidos: 0
- Arquivos renomeados: 0
- Este índice apenas organiza a leitura dos documentos normativos vigentes.

## Documentos normativos vigentes

| Ordem de leitura | Documento | Autoridade principal | Uso operacional |
|---:|---|---|---|
| 1 | `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md` | Contrato mestre do projeto | Fonte principal para regras operacionais, hierarquia documental, escopo vigente e limites de alteração. |
| 2 | `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md` | Modelo metodológico oficial | Fonte principal para formulação matemática, objetivo econômico, decisão diária, restrições e estrutura do modelo. |
| 3 | `relatorios/atuais/GOVERNANCA_ESTRUTURAL_V206.md` | Governança estrutural vigente | Fonte principal para organização estrutural do repositório, separação entre documentação vigente, histórica e auxiliar. |
| 4 | `relatorios/atuais/GOVERNANCA_FINAL_SCRIPTS_V204.md` | Governança final de scripts | Fonte principal para autoridade operacional dos scripts, bloqueios, camadas canônicas e scripts históricos. |
| 5 | `relatorios/atuais/GOVERNANCA_SCRIPTS_V203.md` | Governança intermediária de scripts | Documento normativo de apoio para entender a transição até a governança final V204. |

## Hierarquia prática

1. Em caso de dúvida sobre o projeto como um todo, consultar primeiro `CONTRATO_OPERACIONAL_PROJETO.md`.
2. Em caso de dúvida metodológica, consultar `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`.
3. Em caso de dúvida sobre estrutura do repositório, consultar `GOVERNANCA_ESTRUTURAL_V206.md`.
4. Em caso de dúvida sobre scripts canônicos, legados ou bloqueados, consultar primeiro `GOVERNANCA_FINAL_SCRIPTS_V204.md`.
5. Usar `GOVERNANCA_SCRIPTS_V203.md` como apoio histórico/normativo para interpretar a transição anterior à V204.

## Decisão

Os 5 documentos listados devem permanecer como documentação normativa vigente. Nenhum deles deve ser removido, rebaixado ou consolidado sem auditoria específica posterior.

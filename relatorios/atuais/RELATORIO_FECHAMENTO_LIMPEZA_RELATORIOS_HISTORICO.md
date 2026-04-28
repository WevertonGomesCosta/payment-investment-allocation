# Relatório de fechamento — limpeza de relatorios/historico

## Estado final

A pasta `relatorios/historico/` foi encerrada como fonte de arquivos granulares rastreados.

Resultado final verificado:

~~~bash
git ls-files relatorios/historico | sort | wc -l
# 0
~~~

## Estratégia aplicada

A limpeza foi conduzida de forma controlada:

1. inventário dos blocos históricos;
2. consolidação em relatórios atuais;
3. criação de índices-mestre para blocos grandes;
4. remoção granular somente após preservação documental;
5. commits separados por etapa.

## Blocos consolidados/removidos

| Bloco histórico | Tratamento |
|---|---|
| `relatorios/historico/baselines/` | Inventário, consolidação por faixas, índice-mestre e remoção controlada |
| `relatorios/historico/estruturas/` | Inventário, consolidação por faixas, índice-mestre e remoção controlada |
| `relatorios/historico/validacoes/` | Inventário, consolidação por faixas, índice-mestre e remoção controlada |
| `relatorios/historico/auditorias_especificas/` | Consolidação por subblocos e remoção controlada |
| Demais blocos pequenos | Auditados e consolidados/removidos conforme risco documental |

## Documentos atuais preservados

A trilha histórica passou a ficar preservada em:

- `relatorios/atuais/INDICE_MESTRE_BASELINES_HISTORICAS.md`
- `relatorios/atuais/INDICE_MESTRE_ESTRUTURAS_HISTORICAS.md`
- `relatorios/atuais/INDICE_MESTRE_VALIDACOES_HISTORICAS.md`
- relatórios consolidados por faixa em `relatorios/atuais/`
- inventários e auditorias auxiliares em `relatorios/atuais/limpeza_estrutura/`
- relatórios consolidados específicos em `relatorios/atuais/`

## Regra de autoridade

Os documentos consolidados têm valor histórico e organizacional. Eles não substituem:

- contrato mestre vigente;
- modelo oficial;
- scripts canônicos;
- dados canônicos;
- saídas operacionais oficiais.

## Decisão final

A pasta `relatorios/historico/` foi esvaziada no Git sem perda da trilha relevante, pois os conteúdos foram previamente inventariados, consolidados e indexados.

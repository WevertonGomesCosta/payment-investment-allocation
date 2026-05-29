# Contratos individuais das etapas

Esta pasta reúne os contratos individuais canônicos das etapas operacionais do projeto `payment-investment-allocation`.

## Função da pasta

Separar contratos individuais de:

- contrato operacional mestre;
- modelo matemático-estatístico-financeiro oficial;
- logs de iteração;
- relatórios históricos;
- adendos;
- planos;
- diagnósticos;
- artefatos de auditoria.

## Hierarquia normativa

Os contratos individuais desta pasta são subordinados a:

1. `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`;
2. `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md`.

Em caso de divergência, prevalecem o contrato mestre e o modelo oficial.

## Contratos individuais vigentes

- `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md`
- `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md`
- `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md`
- `CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md`
- `CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`

## Cadeia funcional consolidada

A cadeia documental vigente das Etapas 1–7 é:

```text
Etapa 1 -> PacoteEntradaResolvida
Etapa 2 -> PacoteValidacaoPreExecucao
Etapa 3 -> PacoteDadosOperacionaisCanonicos / UniversoEconomicoCanonico
Etapa 4 -> EstadoTemporalInicial
Etapa 5 -> ResultadoMotorTemporalConjunto
Etapa 6 -> LedgerTemporalCanonico
Etapa 7 -> ResultadoGatesValidacaoNucleo
```

## Histórico documental consolidado

- Etapas 1–3 preservadas como padrão documental e operacional-explicativo.
- Etapa 4 revisada para refletir `EstadoTemporalInicial` como saída formal.
- Etapa 5 consolidada após fechamento funcional como motor temporal conjunto.
- Etapa 6 criada e fechada como `LedgerTemporalCanonico`.
- Etapa 7 criada, ajustada e funcionalizada como Gates de Validação de Núcleo.

## Fontes históricas preservadas

Os contratos foram derivados ou consolidados a partir de documentos contratuais e logs de iteração já existentes. Esses documentos permanecem no local original como histórico; esta pasta contém os contratos canônicos organizados para consulta normativa individual por etapa.

| Contrato individual | Situação documental |
|---|---|
| `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md` | Preservado como padrão documental. |
| `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md` | Preservado como padrão documental. |
| `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md` | Preservado como padrão documental. |
| `CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md` | Revisado para cadeia atual e fluxograma técnico. |
| `CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md` | Consolidado após fechamento funcional. |
| `CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md` | Ajustado para apontar explicitamente à Etapa 7. |
| `CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md` | Revisado para refletir a implementação funcional mergeada. |

## Regra de escopo

Esta pasta deve conter apenas contratos individuais de etapas.

Não devem ser movidos para esta pasta:

- logs de microetapas;
- relatórios de auditoria;
- relatórios históricos;
- planos preparatórios;
- adendos transversais;
- arquivos diagnósticos;
- saídas observáveis;
- CSVs auxiliares.

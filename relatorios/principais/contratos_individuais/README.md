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

## Fontes históricas preservadas

Os contratos das Etapas 1–4 foram derivados de documentos contratuais já existentes em `logs/iteracoes/`, preservando a lógica, as fronteiras e os fluxogramas já formalizados:

| Contrato individual | Documento-fonte preservado |
|---|---|
| `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md` | `logs/iteracoes/ME-V17-F0-V32A_FORMALIZA_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md` |
| `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md` | `logs/iteracoes/ME-V17-F0-V32B_FORMALIZA_ETAPA2_VALIDACAO_PACOTE_ENTRADA_RESOLVIDA.md` |
| `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md` | `logs/iteracoes/ME-V17-F0-V32C_FORMALIZA_ETAPA3_CANONIZACAO_OPERACIONAL.md` |
| `CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md` | `logs/iteracoes/ME-V17-F0-V4B_ESPECIFICA_CONTRATOS_FLUXOGRAMA_ETAPA4.md` |

Os documentos-fonte permanecem no local original como logs históricos. Esta pasta contém cópias canônicas organizadas para consulta normativa individual por etapa.

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

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
- artefatos de auditoria;
- saídas observáveis.

## Hierarquia normativa

Os contratos individuais desta pasta são subordinados a:

1. `relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md`;
2. `relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md`.

Em caso de divergência, prevalecem o contrato mestre e o modelo oficial.

## Padrão estrutural único

A partir da `MACRO-CONTRATOS-02`, todos os contratos individuais das Etapas 1–8 seguem a mesma estrutura documental de 19 seções:

1. Identificação documental
2. Status normativo
3. Posição na cadeia macro
4. Função da etapa
5. Entrada formal obrigatória e exclusiva
6. Componentes consumíveis da entrada
7. Saída formal obrigatória
8. Componentes mínimos da saída
9. Processo interno da etapa
10. O que a etapa pode fazer
11. O que a etapa não pode fazer
12. Relação com a etapa anterior
13. Relação com a etapa posterior
14. Schema/funções públicas previstas ou implementadas
15. Auditoria esperada
16. Critérios de aceite
17. Fluxograma operacional-explicativo completo
18. Condição de parada
19. Histórico documental / adendos funcionais consolidados

## Contratos individuais vigentes

- `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md`
- `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md`
- `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md`
- `CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md`
- `CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md`
- `CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md`
- `CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md`

## Cadeia funcional consolidada

A cadeia documental vigente das Etapas 1–8 é:

```text
Etapa 1 -> PacoteEntradaResolvida
Etapa 2 -> PacoteValidacaoPreExecucao
Etapa 3 -> PacoteDadosOperacionaisCanonicos / UniversoEconomicoCanonico / PacoteAuditoriaCanonizacaoOperacional
Etapa 4 -> EstadoTemporalInicial
Etapa 5 -> ResultadoMotorTemporalConjunto
Etapa 6 -> LedgerTemporalCanonico
Etapa 7 -> ResultadoGatesValidacaoNucleo
Etapa 8 -> SaidaCanonicaOficial
```

## Padrão dos fluxogramas individuais

Todos os fluxogramas individuais devem ser operacional-explicativos completos. Cada fluxograma deve explicitar:

- entrada formal da etapa;
- módulo ou função central, quando existir ou estiver contratada;
- blocos internos principais;
- artefatos intermediários relevantes;
- auditoria, validação ou fechamento interno;
- saída formal da etapa;
- destino para a etapa seguinte contratual.

Fluxogramas não devem introduzir fonte de estado proibida, rota paralela, fallback legado, console, XLSX, saída canônica ou script diagnóstico fora do escopo formal da etapa.

## Situação documental das etapas

| Contrato individual | Situação documental |
|---|---|
| `CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md` | Padronizado estruturalmente sem alterar a semântica histórica. |
| `CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md` | Padronizado estruturalmente como gate puro de pré-execução. |
| `CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md` | Padronizado estruturalmente como canonização operacional. |
| `CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md` | Padronizado como construção do estado temporal inicial. |
| `CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md` | Padronizado como motor temporal conjunto e resultado fechado. |
| `CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md` | Padronizado como ledger temporal canônico. |
| `CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md` | Padronizado como gates de validação de núcleo. |
| `CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md` | Alinhado à implementação real de `SaidaCanonicaOficial` em `nucleo/saida_canonica_oficial.py`, sem transferir console/XLSX para a Etapa 8. |

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
- CSVs auxiliares;
- arquivos de código;
- dados ou caches operacionais.

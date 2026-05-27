# ME-CONTRATOS-01 — organiza contratos individuais

## Data

2026-05-27

## Tipo

DOCUMENTAL / GOVERNANÇA DOCUMENTAL

## Classe

Organização de contratos individuais sem alteração funcional.

## Branch

`me-contratos-01-organiza-contratos-individuais`

## Baseline de entrada

`main` após merge da PR #402.

Merge commit de entrada:

`0e570bf7c9f38c87c4d2781c04bda1f4b09372c8`

## Objetivo

Separar contratos individuais de etapas em uma pasta canônica própria:

`relatorios/principais/contratos_individuais/`

Essa separação evita misturar contratos individuais com:

- contrato mestre;
- modelo matemático-estatístico-financeiro oficial;
- logs de iteração;
- relatórios históricos;
- adendos;
- planos;
- diagnósticos;
- saídas observáveis.

## Arquivos adicionados

- `relatorios/principais/contratos_individuais/README.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md`
- `relatorios/principais/contratos_individuais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`
- `logs/iteracoes/ME-CONTRATOS-01_ORGANIZA_CONTRATOS_INDIVIDUAIS.md`

## Arquivos removidos

- `relatorios/principais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md`

## Justificativa da remoção

O contrato individual da Etapa 5 estava solto na raiz de `relatorios/principais/`, misturado com contrato mestre, modelo oficial e demais documentos principais.

A remoção evita duplicidade normativa e concentra contratos individuais na pasta canônica recém-criada.

## Decisão sobre logs históricos

Logs de iteração com nomes contendo `CONTRATO`, `V4Z`, `ContextoBaseline`, `ContextoSaidaCanonicaCompat`, `shadow` ou termos semelhantes permanecem preservados em `logs/iteracoes/` como histórico.

Eles não foram movidos para `contratos_individuais/`, pois logs históricos não são contratos individuais canônicos.

## Decisão sobre adendos e relatórios

Adendos, relatórios e planos não foram movidos.

A pasta criada deve conter apenas contratos individuais de etapas.

## Correção conceitual incorporada ao contrato da Etapa 5

O contrato individual da Etapa 5, ao ser movido para a nova pasta, passa a usar a saída canônica:

`ResultadoMotorTemporalConjunto`

Não foi preservado `ResultadoMotorTemporalMinimo` como artefato de saída canônico.

## Confirmações

- Não houve alteração de código funcional.
- Não houve alteração de dados.
- Não houve alteração de motor temporal.
- Não houve alteração de ledger.
- Não houve alteração de console.
- Não houve alteração de XLSX.
- Não houve criação de script diagnóstico.
- Não houve criação de sentinela.
- Não houve criação de V4Z.
- Não houve alteração em `aplicacao/*`.
- Não houve alteração em `nucleo/*`.
- Não houve alteração em `dados/*`.
- Não houve alteração em `saidas/*`.

## Validação esperada

Por ser microetapa documental, validar:

```bash
git diff --name-only origin/main...HEAD
git status --short
```

O diff deve ficar restrito aos documentos listados nesta microetapa.

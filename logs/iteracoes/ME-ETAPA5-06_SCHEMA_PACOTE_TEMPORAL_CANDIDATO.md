# ME-ETAPA5-06 — schema único de PacoteTemporalCandidato

## Data

2026-05-27

## Tipo

FUNCIONAL / ESTRUTURAL DE SCHEMA

## Classe

Criação do schema único de pacote temporal candidato dentro de `ResultadoMotorTemporalConjunto`, sem geração de pacotes candidatos, sem decisão econômica e sem ledger.

## Branch

`me-etapa5-06-schema-pacote-temporal-candidato`

## Baseline de entrada

`main` após merge da PR #409.

Merge commit de entrada:

`bca7c28d9dc67e29788ea012c7eb7afd6bcfc4ee`

## Objetivo

Criar o schema comum de:

`PacoteTemporalCandidato`

como estrutura única dentro de:

`ResultadoMotorTemporalConjunto`

Essa estrutura deve permitir, em microetapas futuras, representar pacotes conjuntos envolvendo pagamento, combinação de fontes e switching integral, sem criar trilhas separadas entre pagamento e switching.

## Arquivos alterados

- `nucleo/motor_temporal_conjunto.py`
- `logs/iteracoes/ME-ETAPA5-06_SCHEMA_PACOTE_TEMPORAL_CANDIDATO.md`

## Estruturas adicionadas

- `FonteCandidataPacoteTemporal`
- `SwitchingCandidatoPacoteTemporal`
- `TransicaoCandidataPacoteTemporal`
- `PacoteTemporalCandidato`
- `SchemaPacoteTemporalCandidato`
- `AuditoriaSchemaPacoteTemporalCandidato`

## Campos adicionados a ResultadoMotorTemporalConjunto

- `schema_pacote_temporal_candidato`
- `pacotes_temporais_candidatos_por_data`
- `auditoria_schema_pacote_temporal_candidato`

## Funções adicionadas

- `montar_schema_pacote_temporal_candidato(...)`
- `inicializar_pacotes_temporais_candidatos_por_data(...)`
- `montar_auditoria_schema_pacote_temporal_candidato(...)`

## Escopo implementado

A microetapa implementa apenas:

- schema único do pacote temporal candidato;
- tipos de pacote previstos;
- status de factibilidade previstos;
- campos proibidos de decisão;
- mapa vazio de pacotes candidatos por data do horizonte;
- auditoria estrutural do schema.

## Escopo explicitamente não implementado

Esta microetapa não implementa:

- geração de pacotes candidatos;
- escolha de pacote vencedor;
- decisão econômica;
- escolha de fonte ótima;
- seleção de lote;
- execução de pagamento;
- promoção de switching;
- execução de switching novo;
- materialização de lote pós-switching;
- ledger oficial;
- saída canônica final;
- console;
- XLSX;
- scripts diagnósticos;
- testes;
- alteração de dados.

## Validação esperada

Validar localmente:

```bash
git diff --name-only origin/main...HEAD
python -m py_compile nucleo/motor_temporal_conjunto.py
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
git status --short
```

Resultado esperado:

- diff restrito a `nucleo/motor_temporal_conjunto.py` e este log;
- `py_compile` sem erro;
- runtime principal sem regressão;
- árvore limpa, salvo eventual atualização esperada de `dados/cache_bcb.json` por BCB online, a ser tratada separadamente.

## Confirmações

- `EstadoTemporalInicial` continua sendo a única entrada da Etapa 5.
- `ResultadoMotorTemporalConjunto` continua sendo a única saída da Etapa 5.
- Não foi criado `ResultadoMotorTemporalMinimo`.
- Não foi criado ledger.
- Não foi criada decisão econômica.
- Não houve alteração de console.
- Não houve alteração de XLSX.
- Não houve alteração de saída canônica.
- Não houve alteração de dados.
- Não houve criação de script diagnóstico.
- Não houve criação de sentinela.
- Não houve criação de V4Z.

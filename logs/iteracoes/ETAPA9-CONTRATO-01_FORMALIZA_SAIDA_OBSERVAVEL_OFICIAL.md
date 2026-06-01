# ETAPA9-CONTRATO-01 — Formaliza Saída Observável Oficial / Renderização / Exportação

## 1. Objetivo

Criar a frente documental da Etapa 9 do projeto `payment-investment-allocation`, formalizando a camada posterior à Etapa 8 responsável por transformar `SaidaCanonicaOficial` em saída observável oficial para console, XLSX e relatório operacional observável.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `8d7b7d67bfcddcccdce7b82eee4a4bfd7b2cb76a`
- Marco incorporado: `FECHAMENTO-CONTRATOS-ETAPAS-1-8-01`
- Branch da frente: `etapa9-contrato-01`

## 3. Diagnóstico mínimo inicial

O baseline remoto de `main` foi identificado como o merge da PR #462:

```text
8d7b7d6 Merge pull request #462 from WevertonGomesCosta/fechamento-contratos-etapas-1-8-01
```

Também foram observados como merges imediatamente anteriores:

```text
4549a09 Merge pull request #461 from WevertonGomesCosta/contrato-etapa7-alinhamento-01
2b5a26b Merge pull request #460 from WevertonGomesCosta/contrato-etapa8-alinhamento-01
57c9177 Merge pull request #459 from WevertonGomesCosta/macro-auditoria-cadeia-01
0706b46 Merge pull request #458 from WevertonGomesCosta/codex/fix-decisao_temporal_inconsistente-bug
```

## 4. Leitura normativa executada

Foram lidos para orientar esta frente:

```text
relatorios/principais/CONTRATO_OPERACIONAL_PROJETO.md
relatorios/principais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA1_ENTRADA_RESOLVIDA.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA2_VALIDACAO_PRE_EXECUCAO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA3_DADOS_OPERACIONAIS_CANONICOS.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA4_ESTADO_TEMPORAL_INICIAL.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA5_MOTOR_TEMPORAL_CONJUNTO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA6_LEDGER_TEMPORAL_CANONICO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md
logs/iteracoes/CONTRATO-ETAPA8-ALINHAMENTO-01_ATUALIZA_CONTRATO_IMPLEMENTACAO_REAL.md
logs/iteracoes/CONTRATO-ETAPA7-ALINHAMENTO-01_ATUALIZA_REFERENCIA_ETAPA8.md
logs/iteracoes/FECHAMENTO-CONTRATOS-ETAPAS-1-8-01_CONGELA_CADEIA_CONTRATUAL.md
```

## 5. Síntese normativa curta

### O que a Etapa 9 pode receber

A Etapa 9 pode receber somente:

```text
SaidaCanonicaOficial
```

Não pode consultar diretamente motor, ledger, gates, estado temporal, dados brutos, planilha, cache, logs, scripts diagnósticos, console ou XLSX anterior como fonte decisória.

### O que a Etapa 9 pode produzir

A Etapa 9 pode produzir:

```text
PacoteSaidaObservavelOficial
```

Esse pacote deve conter blocos para console, blocos para XLSX, resumo operacional observável, últimos pagamentos, próximos pagamentos, fontes, obrigações cobertas e bloqueadas, switchings, saldos, avisos, bloqueios, lacunas de renderização e metadados de origem em `SaidaCanonicaOficial`.

### O que a Etapa 9 está proibida de fazer

A Etapa 9 não pode reotimizar, revalorar, escolher nova fonte, trocar pacote vencedor, alterar obrigação, alterar switching, alterar saldo, corrigir dado financeiro, executar pagamento real, executar switching real ou criar rota paralela fora da cadeia.

### Fronteira entre Etapa 8 e Etapa 9

A Etapa 8 produz `SaidaCanonicaOficial` e não gera console/XLSX oficiais.

A Etapa 9 consome `SaidaCanonicaOficial` e prepara `PacoteSaidaObservavelOficial` para consumo posterior por console, XLSX e visualização/exportação.

### Riscos contratuais a evitar

- Reabrir Etapa 8 para corrigir console/XLSX.
- Usar saída legada como fonte decisória.
- Usar funções legadas como adaptador decisório paralelo.
- Transformar rótulos como `não decidido_etapa5` em correção cosmética sem evidência canônica.
- Consultar diretamente ledger/gates/motor para suprir lacuna de renderização.
- Mascarar lacuna upstream sem registrar bloqueio objetivo.

### Restrições do modelo oficial

O modelo determina que a decisão econômica é diária, conjunta, condicionada ao estado observado, e maximiza patrimônio líquido terminal líquido. Renderização não é nova otimização, reconciliação ou correção decisória. Ranking, switching, liquidez, rendimento, fontes, obrigações e saldos devem chegar à Etapa 9 já materializados pela cadeia Etapas 5–8; a Etapa 9 apenas os apresenta de modo observável.

## 6. Escopo executado

Arquivos criados ou alterados:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA9_SAIDA_OBSERVAVEL_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/ETAPA9-CONTRATO-01_FORMALIZA_SAIDA_OBSERVAVEL_OFICIAL.md
```

## 7. Resumo do contrato da Etapa 9

O contrato criado:

- define `SaidaCanonicaOficial` como entrada obrigatória e exclusiva;
- define `PacoteSaidaObservavelOficial` como saída formal prevista;
- posiciona a Etapa 9 depois da Etapa 8 e antes de exportação física/visualização/paridade;
- autoriza preparação de blocos para console e XLSX;
- proíbe reotimização, revaloração e alteração de decisão;
- proíbe consulta direta a motor, ledger, gates, planilha, logs, scripts diagnósticos, console anterior e XLSX anterior;
- estabelece tratamento explícito para `fonte_a_decidir`, `não decidido_etapa5` e `obrigacao_temporal_futura_sem_decisao_etapa5`;
- exige que lacunas sejam registradas como lacunas formais de renderização ou evidência upstream objetiva;
- prepara a frente funcional `ETAPA9-FUNCIONAL-01`.

## 8. Restrições preservadas

- Não altera `aplicacao/*`.
- Não altera `nucleo/*`.
- Não altera `dados/*`.
- Não altera `saidas/*`.
- Não altera `scripts/diagnostico/*`.
- Não altera contratos individuais das Etapas 1–8.
- Não altera contrato operacional mestre.
- Não altera modelo matemático-estatístico-financeiro oficial.
- Não altera console.
- Não altera XLSX.
- Não implementa `PacoteSaidaObservavelOficial`.
- Não integra runtime.

## 9. Validação esperada

A validação documental esperada é:

```bash
git status --short
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
```

O diff deve ficar restrito a:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA9_SAIDA_OBSERVAVEL_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/ETAPA9-CONTRATO-01_FORMALIZA_SAIDA_OBSERVAVEL_OFICIAL.md
```

## 10. Decisão operacional

```text
APROVAR a frente documental ETAPA9-CONTRATO-01 para PR, desde que a validação do diff confirme escopo restrito aos três documentos esperados.
```

## 11. Próxima frente recomendada

Após validação e merge desta frente:

```text
ETAPA9-FUNCIONAL-01 — Implementa PacoteSaidaObservavelOficial mínimo consumindo exclusivamente SaidaCanonicaOficial, sem alterar console/XLSX ainda.
```

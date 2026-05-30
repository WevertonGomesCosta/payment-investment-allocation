# MICRO-ETAPA8-CONTRATO-01 — Formaliza contrato documental da Etapa 8

## 1. Identificação

- **Microfrente:** MICRO-ETAPA8-CONTRATO-01
- **Tipo:** documental
- **Classe:** formalização de contrato individual de etapa
- **Baseline de entrada:** `6bc6f4d70c7bb53a17579f1c716d9d8ceb4cbd3b`
- **Branch:** `docs/micro-etapa8-contrato-01`
- **Etapa formalizada:** Etapa 8 — Saída Canônica Oficial

## 2. Objetivo

Formalizar documentalmente a Etapa 8 como a primeira camada autorizada a preparar a saída canônica oficial após aprovação dos gates da Etapa 7.

A microfrente define:

- entrada formal da Etapa 8;
- saída formal prevista;
- componentes consumíveis;
- proibições;
- relação com Etapa 7;
- relação com camadas posteriores;
- fluxograma operacional-explicativo;
- condição de parada;
- ausência de alteração funcional.

## 3. Diagnóstico prévio requerido

O diagnóstico requerido pela microfrente é:

```text
branch de base esperada: main
remote esperado: WevertonGomesCosta/payment-investment-allocation
HEAD/main esperado: 6bc6f4d70c7bb53a17579f1c716d9d8ceb4cbd3b
origin/main esperado: 6bc6f4d70c7bb53a17579f1c716d9d8ceb4cbd3b
estado esperado: sem alterações locais não commitadas
```

A execução remota confirmou que `main` está idêntica ao baseline `6bc6f4d70c7bb53a17579f1c716d9d8ceb4cbd3b` antes da abertura da branch documental.

## 4. Arquivos alterados

Somente os arquivos documentais abaixo pertencem ao escopo desta microfrente:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/MICRO-ETAPA8-CONTRATO-01_FORMALIZA_CONTRATO_DOCUMENTAL_ETAPA8.md
```

## 5. Arquivos e áreas não alterados

Esta microfrente não altera:

- `aplicacao/*`;
- `nucleo/*`;
- `dados/*`;
- `saidas/*`;
- `scripts/diagnostico/*`;
- console;
- XLSX;
- saída canônica existente;
- contratos individuais das Etapas 1–7;
- contrato operacional mestre;
- runtime;
- regras econômicas;
- motor temporal;
- ledger;
- gates;
- cache BCB;
- planilhas.

## 6. Decisão contratual registrada

A Etapa 8 passa a ser definida documentalmente como:

```text
ResultadoGatesValidacaoNucleo aprovado + LedgerTemporalCanonico validado
    -> Etapa 8
    -> SaidaCanonicaOficial
```

A progressão só é permitida quando:

```text
ResultadoGatesValidacaoNucleo.pronto_para_etapa8=True
```

Quando `pronto_para_etapa8=False`, a preparação da saída canônica oficial deve ser bloqueada.

## 7. Artefato previsto

O artefato contratual provisório da Etapa 8 é:

```text
SaidaCanonicaOficial
```

Esse artefato é previsto documentalmente. Não há implementação formal nova nesta microfrente.

## 8. Funções pré-existentes do runtime

Funções já existentes, como:

```text
construir_saida_canonica_com_switching_v17_c7(...)
construir_matriz_elegibilidade_fontes_s7b(...)
aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(...)
```

foram classificadas no contrato como funções pré-existentes do runtime/legado operacional. Esta microfrente não as promove automaticamente a implementação formal final da Etapa 8.

## 9. Ausência de alteração funcional

Esta microfrente não implementa:

- `construir_saida_canonica_oficial(...)`;
- novo módulo de saída;
- novo gate;
- novo ledger;
- nova regra econômica;
- nova matriz de elegibilidade;
- geração XLSX;
- alteração em `aplicacao/principal.py`;
- alteração em qualquer arquivo funcional.

## 10. Validações esperadas

Após commit, as validações esperadas são:

```bash
git diff --name-only origin/main...HEAD
```

Deve listar somente:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/MICRO-ETAPA8-CONTRATO-01_FORMALIZA_CONTRATO_DOCUMENTAL_ETAPA8.md
```

```bash
git diff --stat origin/main...HEAD
```

Deve indicar apenas alterações documentais.

```bash
git status --short
```

Deve retornar limpo após commit.

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
```

Deve passar, pois não houve alteração funcional.

```bash
python -B aplicacao/principal.py
```

Deve preservar o comportamento vigente do runtime: quando `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False`, a progressão para saída posterior deve permanecer bloqueada e console/XLSX oficiais não devem ser gerados.

## 11. Critérios de aceite

A PR desta microfrente deve ser aceita somente se:

1. alterar exclusivamente os três arquivos permitidos;
2. criar o contrato individual da Etapa 8 com as 19 seções exigidas;
3. atualizar o README apenas para incluir a Etapa 8 na cadeia documental;
4. registrar este log documental;
5. não alterar código, runtime, dados, saídas ou scripts diagnósticos;
6. não alterar contratos das Etapas 1–7;
7. não alterar o contrato operacional mestre;
8. manter a Etapa 8 como preparação canônica pós-gates, sem console/XLSX como responsabilidade central;
9. exigir `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=True` para progressão.

## 12. Condição de parada

A microfrente deve parar sem merge se a auditoria da PR identificar:

- alteração fora dos três arquivos permitidos;
- alteração funcional;
- alteração em contratos das Etapas 1–7;
- alteração no contrato operacional mestre;
- promoção indevida de função legada a implementação formal final da Etapa 8;
- ambiguidade entre Etapa 8 e camada posterior de console/XLSX;
- necessidade de reabrir decisão econômica, ledger, motor temporal ou gates.

## 13. Próxima microfrente recomendada

Após auditoria, validação local e merge desta PR documental, a próxima microfrente recomendada é:

```text
MICRO-ETAPA8-AUDITORIA-01 — Audita contrato documental da Etapa 8 contra Etapas 1–7 e runtime atual
```

Essa próxima microfrente deve auditar o novo contrato da Etapa 8 contra:

- contratos individuais das Etapas 1–7;
- `aplicacao/principal.py`;
- comportamento pós-PR #437;
- ausência de progressão quando `pronto_para_etapa8=False`;
- fronteira entre Etapa 8 e console/XLSX.

Ela ainda não deve implementar código funcional.

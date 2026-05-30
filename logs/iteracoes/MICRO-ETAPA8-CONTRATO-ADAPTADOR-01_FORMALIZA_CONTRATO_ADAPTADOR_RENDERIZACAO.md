# MICRO-ETAPA8-CONTRATO-ADAPTADOR-01 — Formaliza contrato da camada adaptadora entre SaidaCanonicaOficial e renderização/exportação

## Identificação

- **Microfrente:** MICRO-ETAPA8-CONTRATO-ADAPTADOR-01
- **Tipo:** documental / contrato complementar
- **Baseline de entrada:** `5db3d79477b987277814dbe50eb725969fe4907e`
- **Branch:** `docs/micro-etapa8-contrato-adaptador-01`

## Objetivo

Formalizar a camada adaptadora entre `SaidaCanonicaOficial` e renderização/exportação, sem implementar código.

## Arquivos alterados

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_ADAPTADOR_RENDERIZACAO_EXPORTACAO.md
logs/iteracoes/MICRO-ETAPA8-CONTRATO-ADAPTADOR-01_FORMALIZA_CONTRATO_ADAPTADOR_RENDERIZACAO.md
```

## Decisão registrada

A substituição direta de `saida_canonica` por `SaidaCanonicaOficial` em console/XLSX permanece proibida.

A transição deve ocorrer por adaptador formal:

```text
SaidaCanonicaOficial -> PacoteRenderizacaoSaidaCanonica -> console/XLSX
```

## Restrições preservadas

Esta microfrente não altera:

- runtime;
- console;
- XLSX;
- motor;
- ledger;
- gates;
- dados;
- saídas operacionais;
- lógica econômica.

## Próxima microfrente recomendada

```text
MICRO-ETAPA8-AUDITORIA-ADAPTADOR-01 — Audita contrato do adaptador contra diagnóstico de consumo console/XLSX
```

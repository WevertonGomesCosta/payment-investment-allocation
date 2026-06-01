# CONTRATO-ETAPA7-ALINHAMENTO-01 — Atualiza referência da Etapa 8

## 1. Objetivo

Atualizar a referência documental da Etapa 8 no contrato e no fluxograma da Etapa 7, removendo nomenclatura antiga que ainda indicava `Saída Canônica Validada` e `contrato futuro`.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `2b5a26b`
- Marco anterior: `CONTRATO-ETAPA8-ALINHAMENTO-01`

## 3. Escopo

Arquivos alterados:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA7_GATES_VALIDACAO_NUCLEO.md
logs/iteracoes/CONTRATO-ETAPA7-ALINHAMENTO-01_ATUALIZA_REFERENCIA_ETAPA8.md
```

## 4. Alteração aplicada

Substituída a referência antiga:

```text
Etapa 8 — Saída Canônica Validada
contrato futuro
```

pela referência vigente:

```text
Etapa 8 — Saída Canônica Oficial
nucleo/saida_canonica_oficial.py
construir_saida_canonica_oficial(...)
```

A seção de relação com a etapa posterior também foi ajustada para indicar que a Etapa 8 já possui contrato próprio e implementação formal.

## 5. Restrições preservadas

- Não altera código funcional.
- Não altera `aplicacao/*`.
- Não altera `nucleo/*`.
- Não altera runtime.
- Não altera gates funcionais.
- Não altera Etapa 8.
- Não altera console/XLSX.
- Não abre auditoria da saída observável.

## 6. Decisão

```text
APROVAR alinhamento documental da Etapa 7 à Etapa 8 vigente.
```

## 7. Próxima frente recomendada

Após validação e merge:

```text
FECHAMENTO-CONTRATOS-ETAPAS-1-8-01 — Congela cadeia contratual das Etapas 1–8
```

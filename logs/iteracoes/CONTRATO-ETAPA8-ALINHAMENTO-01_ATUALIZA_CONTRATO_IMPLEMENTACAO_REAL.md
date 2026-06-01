# CONTRATO-ETAPA8-ALINHAMENTO-01 — Atualiza contrato da Etapa 8 para refletir implementação real

## 1. Objetivo

Alinhar o contrato individual da Etapa 8 ao estado funcional real do projeto após a implementação de `SaidaCanonicaOficial` e de `construir_saida_canonica_oficial(...)`.

## 2. Baseline de entrada

- Branch base: `main`
- Baseline: `57c9177`
- Último marco incorporado: `MACRO-AUDITORIA-CADEIA-01`

## 3. Escopo

Arquivos alterados:

```text
relatorios/principais/contratos_individuais/CONTRATO_ETAPA8_SAIDA_CANONICA_OFICIAL.md
relatorios/principais/contratos_individuais/README.md
logs/iteracoes/CONTRATO-ETAPA8-ALINHAMENTO-01_ATUALIZA_CONTRATO_IMPLEMENTACAO_REAL.md
```

## 4. Alterações aplicadas

- O contrato da Etapa 8 deixa de descrever `SaidaCanonicaOficial` como artefato meramente previsto.
- O contrato passa a registrar `nucleo/saida_canonica_oficial.py` como módulo funcional implementado.
- O contrato passa a registrar `construir_saida_canonica_oficial(ledger, gates) -> SaidaCanonicaOficial` como função pública implementada.
- O fluxograma da Etapa 8 passa a mencionar explicitamente o módulo e a função implementada.
- O README dos contratos individuais passa a informar que a Etapa 8 está alinhada à implementação real, sem transferir console/XLSX para a Etapa 8.

## 5. Restrições preservadas

- Não altera código funcional.
- Não altera `aplicacao/*`.
- Não altera `nucleo/*`.
- Não altera dados.
- Não altera saídas.
- Não altera console.
- Não altera XLSX.
- Não recria adaptadores.
- Não recria comparadores.
- Não reabre equivalência observável.
- Não altera contratos das Etapas 1–7.
- Não altera contrato operacional mestre.

## 6. Decisão

```text
APROVAR alinhamento documental da Etapa 8 ao código real já implementado.
```

## 7. Próxima frente recomendada

Após auditoria e merge desta frente:

```text
MACRO-SAIDA-OBSERVAVEL-01 — Audita por que próximos pagamentos aparecem como não decidido_etapa5
```

Essa próxima frente deve identificar se o rótulo vem da saída legada/console ou de lacuna real no motor/ledger, sem criar adaptadores e sem migrar console/XLSX antes de localizar a origem.

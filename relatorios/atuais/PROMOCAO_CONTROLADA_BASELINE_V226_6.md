# PROMOÇÃO CONTROLADA DE BASELINE — V226.6

## Status formal (revisado por divergência de evidência)

```text
PROMOCAO_CONTROLADA_V226_6_EM_ANALISE_DOCUMENTAL
```

Esta microetapa registra revisão documental da V226.6 para manter rastreabilidade honesta entre critérios declarados e artefatos anexados na rodada atual.

## Decisão

A V226.6 permanece candidata da frente, porém a promoção controlada fica **condicionada** por divergência entre o critério específico de switching declarado e o artefato atual anexado.

Esta microetapa de promoção:

- **não altera funcionalidade**;
- **não altera motor econômico**;
- **não altera saída canônica**;
- **não altera planilha operacional**;
- **não altera console**;
- **não altera dados/config/cache/ranking/replay**;
- **não altera contrato mestre nem modelo matemático-estatístico-financeiro**.

## Escopo técnico preservado da frente V226

Permanece preservado como escopo técnico da frente:

1. consistência entre fonte auditável, saldo e cobertura no Extrato Futuro;
2. bloqueio de cobertura operacional quando lote/fonte está indeterminado;
3. limpeza de valores financeiros/temporais operacionais quando não há fonte/lote auditável;
4. coerência entre status/motivo de bloqueio e auditabilidade operacional;
5. separação de switching candidato vs switching materializado nos campos operacionais;
6. tratamento diagnóstico explícito para `fonte_pos_switching_nao_materializada`;
7. proteção contra reintrodução de lote exaurido (`Lote 6630,64 fev.`) no futuro;
8. preservação da estrutura operacional de auditoria no XLSX (37 campos no Extrato Futuro).

## Evidência documental: divergência identificada na rodada atual

```text
ARTEFATO_ATUAL_INTERNET_2026_06_15:
- Status recomendação = sem_saldo_temporal_auditavel
- Estratégia = sem_switching
- Necessita switching = não
- Pacote do dia = pay_only
- Fonte switching = motor_pagamento
- Score switching = 0

CONCLUSAO_DOCUMENTAL_DA_RODADA:
- Critérios fonte–saldo–cobertura continuam preservados.
- Critério específico "Internet 2026-06-15 = fonte_pos_switching_nao_materializada"
  NÃO está comprovado pelo artefato atual anexado.
```

## Escopo negativo obrigatório

Esta microetapa documental V226.6:

- não reabre contrato, modelo, ranking ou gate econômico;
- não modifica o conjunto de dados canônicos;
- não altera regras econômicas da baseline anterior;
- não implica promoção da V226.6 como baseline histórica global substituta da V225;
- não altera funcionalidade;
- não corrige código;
- não substitui decisão técnica por inferência documental.

## Estado de referência após revisão documental

```text
BASELINE_HISTORICA_ANTERIOR: BASELINE_FUNCIONAL_ESTAVEL_V225
V226_6_STATUS_ATUAL: PROMOCAO_CONTROLADA_CONDICIONADA_POR_DIVERGENCIA_DE_EVIDENCIA
```

## Decisão final

```text
PROMOCAO_CONTROLADA_V226_6_BLOQUEADA_POR_DIVERGENCIA_DE_EVIDENCIA
MANTER_V225_COMO_BASELINE_HISTORICA_ANTERIOR
SEM_ALTERACAO_FUNCIONAL_NESTA_MICROETAPA_DE_PROMOCAO
PROXIMA_DECISAO_REQUER_ESCOLHA_EXPLICITA:
A) USAR_ARTEFATO_VALIDADO_ANTERIOR_DA_V226_6_COMO_EVIDENCIA_OFICIAL
B) ABRIR_NOVA_MICROCORRECAO_FUNCIONAL_SE_ARTEFATO_ATUAL_FOR_A_SAIDA_CANONICA_OFICIAL
```

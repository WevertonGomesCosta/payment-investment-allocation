# PROMOÇÃO CONTROLADA DE BASELINE — V226.6

## Status formal

```text
BASELINE_FUNCIONAL_ESTAVEL_V226_6_FRENTE_FONTE_SALDO_COBERTURA_SWITCHING
```

Esta promoção controlada registra a V226.6 como baseline funcional estável **da frente V226** (consistência fonte–saldo–cobertura e rastreabilidade diagnóstica de switching), mantendo a V225 como baseline histórica anterior.

## Decisão

A V226.6 foi tratada como candidata validada para esta frente, com os critérios de aceite já confirmados em validação local do usuário.

Esta microetapa de promoção:

- **não altera funcionalidade**;
- **não altera motor econômico**;
- **não altera saída canônica**;
- **não altera planilha operacional**;
- **não altera console**;
- **não altera dados/config/cache/ranking/replay**;
- **não altera contrato mestre nem modelo matemático-estatístico-financeiro**.

## Escopo aprovado da frente V226

Fica aprovado e promovido como estável nesta frente:

1. consistência entre fonte auditável, saldo e cobertura no Extrato Futuro;
2. bloqueio de cobertura operacional quando lote/fonte está indeterminado;
3. limpeza de valores financeiros/temporais operacionais quando não há fonte/lote auditável;
4. coerência entre status/motivo de bloqueio e auditabilidade operacional;
5. separação de switching candidato vs switching materializado nos campos operacionais;
6. tratamento diagnóstico explícito para `fonte_pos_switching_nao_materializada`;
7. proteção contra reintrodução de lote exaurido (`Lote 6630,64 fev.`) no futuro;
8. preservação da estrutura operacional de auditoria no XLSX (37 campos no Extrato Futuro).

## Critérios de aceite validados (referência de promoção)

```text
1) Internet 2026-06-15: Status recomendação = fonte_pos_switching_nao_materializada
2) Internet 2026-06-15: Motivo bloqueio lote = fonte_pos_switching_nao_materializada
3) Internet 2026-06-15: sem Destino/Data switching candidatos em campos operacionais
4) Internet 2026-06-15: Fonte switching = diagnostico_nao_materializado quando sem materialização
5) Lote sugerido = não determinado: sem valores financeiros/temporais operacionais
6) Lote sugerido = não determinado: sem Cobertura integral = sim e sem Status = ok
7) Lote pós-switching não recebe nome de produto
8) Lote 6630,64 fev. permanece ausente do Extrato Futuro
9) XLSX preservado com 37 campos de auditoria
10) V226.6 alterou apenas nucleo/saida_canonica.py em relação à V226.5
```

## Escopo negativo obrigatório

Esta promoção controlada V226.6:

- não reabre contrato, modelo, ranking ou gate econômico;
- não modifica o conjunto de dados canônicos;
- não altera regras econômicas da baseline anterior;
- não implica promoção da V226.6 como baseline histórica global substituta da V225;
- apenas formaliza a estabilidade da frente V226.

## Estado de referência após promoção controlada

```text
BASELINE_HISTORICA_ANTERIOR: BASELINE_FUNCIONAL_ESTAVEL_V225
BASELINE_ESTAVEL_DA_FRENTE_V226: BASELINE_FUNCIONAL_ESTAVEL_V226_6_FRENTE_FONTE_SALDO_COBERTURA_SWITCHING
```

## Decisão final

```text
PROMOVER_V226_6_COMO_BASELINE_ESTAVEL_DA_FRENTE_V226
MANTER_V225_COMO_BASELINE_HISTORICA_ANTERIOR
SEM_ALTERACAO_FUNCIONAL_NESTA_MICROETAPA_DE_PROMOCAO
```


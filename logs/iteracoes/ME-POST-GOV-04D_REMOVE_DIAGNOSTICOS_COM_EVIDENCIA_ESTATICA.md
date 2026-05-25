# ME-POST-GOV-04D — Remoção física dos diagnósticos com evidência estática registrada

## Objetivo

Remover fisicamente os 11 scripts classificados como `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` após a criação de evidência estática substitutiva na ME-POST-GOV-04C.

A microetapa conclui o saneamento físico do namespace `scripts/diagnostico/`, preservando apenas o gate permanente `auditar_nucleo_vivo_v4z.py` e o índice diagnóstico.

## Baseline de entrada

```text
BASELINE: main
HEAD: 0dcb959952dd8e2cad558d46c5492789c0631f0b
ULTIMO_MERGE: PR #368 — ME-POST-GOV-04C registra evidências estáticas dos diagnósticos
```

## Escopo permitido

```text
scripts/diagnostico/*
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
saidas/*
```

A ME-POST-GOV-04D não altera motor, replay, ledger, ranking, saída canônica, contrato mestre, modelo oficial ou regra econômica.

## Evidência prévia

A evidência estática substitutiva foi registrada em:

```text
logs/iteracoes/ME-POST-GOV-04C_EVIDENCIAS_ESTATICAS_DIAGNOSTICOS.md
```

## Scripts removidos nesta microetapa

| Script | Evidência prévia | Ação ME-POST-GOV-04D |
|---|---|---|
| `scripts/diagnostico/auditar_consistencia_exportacao_auxiliar_u4_vs_u3_v17_f0_u5.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/auditar_governanca_promocao_saida_auxiliar_v17_f0_u6.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/auditar_regras_operacionais_uso_recebidos_v17_f0_t5.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/auditar_separacao_previsao_materializacao_v17_f0_s6.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/consolidar_matriz_correcao_v17_c5.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/consolidar_plano_migracao_v17_b0.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/construir_taxonomia_v17_a2.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/desenhar_pacote_orquestrado_pre_saida_v17_b2.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/explicitar_valores_resgate_multifonte_v17_f0_u2.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/formalizar_criterios_elegibilidade_pagamento_v17_f0_u1.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |
| `scripts/diagnostico/formalizar_ledger_diagnostico_recebidos_v17_f0_t6.py` | `REGISTRADA_ME_POST_GOV_04C` | removido |

## Scripts preservados

O gate permanente foi preservado:

```text
scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

O índice de diagnósticos foi preservado e atualizado:

```text
scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md
```

## Estado esperado do namespace diagnóstico ativo

Após esta microetapa, `scripts/diagnostico/` deve conter apenas:

```text
scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md
scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

## Decisão da microetapa

```text
STATUS: REMOCAO_FINAL_DIAGNOSTICOS_COM_EVIDENCIA_APLICADA
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
PROXIMA_ACAO: VALIDAR_PR_E_EXECUTAR_GATES
```

## Validação esperada

Após checkout da branch ou após merge, rodar:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

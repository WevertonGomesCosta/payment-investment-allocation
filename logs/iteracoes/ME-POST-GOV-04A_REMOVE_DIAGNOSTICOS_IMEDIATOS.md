# ME-POST-GOV-04A — Remoção física dos diagnósticos classificados como REMOVER_IMEDIATAMENTE

## Objetivo

Aplicar fisicamente apenas as decisões `REMOVER_IMEDIATAMENTE` registradas na ME-POST-GOV-03.

A microetapa remove somente os scripts explicitamente classificados nessa categoria e atualiza `scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md` para refletir o estado físico pós-remoção.

## Baseline de entrada

```text
BASELINE: main
HEAD: da306c494bc643e872650235323e076eba116420
ULTIMO_MERGE: PR #365 — ME-POST-GOV-03 classificação decisória dos diagnósticos transitórios
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
relatorios/principais/*
saidas/*
```

A ME-POST-GOV-04A não altera motor, replay, ledger, ranking, saída canônica, contrato mestre, modelo oficial ou regra econômica.

## Scripts removidos

| Script | Decisão ME-POST-GOV-03 | Ação ME-POST-GOV-04A |
|---|---|---|
| `scripts/diagnostico/auditar_comparacao_pacotes_diarios.py` | `REMOVER_IMEDIATAMENTE` | removido |
| `scripts/diagnostico/checagem_pos_conflito_current.py` | `REMOVER_IMEDIATAMENTE` | removido |
| `scripts/diagnostico/diagnosticar_baixa_resolutividade_extrato_futuro.py` | `REMOVER_IMEDIATAMENTE` | removido |
| `scripts/diagnostico/mapear_pontos_reescolha_v16j0.py` | `REMOVER_IMEDIATAMENTE` | removido |

## Scripts preservados

O gate permanente abaixo foi preservado:

```text
scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

Os scripts classificados como `ARQUIVAR_FORA_ROTA_VIVA` e `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` não foram movidos nem removidos nesta microetapa.

## Decisão da microetapa

```text
STATUS: REMOCOES_IMEDIATAS_APLICADAS
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

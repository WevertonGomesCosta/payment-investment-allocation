# ME-POST-GOV-03 — Classificação decisória dos diagnósticos transitórios

## Objetivo

Classificar decisoriamente todos os scripts marcados como `TRANSITORIO_PENDENTE` em `scripts/diagnostico/INDICE_DIAGNOSTICOS_ATIVOS.md` após o merge da PR #364.

A microetapa segue estritamente o GOV-01 e não promove nenhum script novo a gate permanente.

## Baseline de entrada

```text
BASELINE: main
HEAD: bbce9e66dbb73bc07a27fa925cd6984216bc8858
ULTIMO_MERGE: PR #364 — ME-POST-GOV-02 saneamento do namespace diagnóstico
```

## Auditoria de saída antes da abertura

Auditoria local informada pelo usuário:

```text
git checkout main: aprovado
git pull --ff-only: aprovado
git status --short: vazio
git log --oneline -5: HEAD em bbce9e6
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Resultado V4Z reportado:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
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

Esta microetapa não altera motor, replay, ledger, ranking, saída canônica, contrato mestre, modelo oficial ou regra econômica.

## Regra de classificação aplicada

- `MANTER_COMO_GATE_PERMANENTE`: apenas para gate já formalizado, estável e compatível.
- `ARQUIVAR_FORA_ROTA_VIVA`: diagnóstico histórico cuja evidência pode ser preservada fora do namespace ativo.
- `SUBSTITUIR_POR_EVIDENCIA_ESTATICA`: diagnóstico cujo resultado deve sobreviver como log, relatório ou especificação, não como script executável.
- `REMOVER_IMEDIATAMENTE`: script pontual, contextual, obsoleto ou exploratório sem utilidade de preservação.
- `PROMOVER_A_GATE_PERMANENTE`: não aplicado nesta microetapa.

## Decisão consolidada

| Decisão | Quantidade |
|---|---:|
| `MANTER_COMO_GATE_PERMANENTE` | 1 |
| `ARQUIVAR_FORA_ROTA_VIVA` | 26 |
| `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` | 11 |
| `REMOVER_IMEDIATAMENTE` | 4 |
| `PROMOVER_A_GATE_PERMANENTE` | 0 |

## Gate permanente preservado

```text
scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

## Observação importante

Esta microetapa registra a decisão. Ela não remove fisicamente os scripts nem os move para histórico. A aplicação física deve ocorrer em microetapa subsequente, em lotes pequenos e auditáveis, ainda limitada a `scripts/diagnostico/*` e `logs/iteracoes/*`.

## Decisão da microetapa

```text
STATUS: CLASSIFICACAO_DECISORIA_REGISTRADA
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
PROXIMA_ACAO: APLICAR_DECISOES_EM_LOTES_CONTROLADOS
```

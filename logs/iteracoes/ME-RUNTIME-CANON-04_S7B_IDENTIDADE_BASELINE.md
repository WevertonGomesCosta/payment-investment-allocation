# ME-RUNTIME-CANON-04 — S7B usa identidade central da baseline

## Objetivo

Remover o literal local `VERSAO_BASELINE = "V225"` de `nucleo/matriz_elegibilidade_fontes_s7b.py` e usar a identidade central definida em `nucleo.identidade_baseline.VERSAO_BASELINE`.

A microetapa continua a canonização gradual da rota runtime versionada após a ME-RUNTIME-CANON-03, sem alterar regra econômica, motor, replay, ledger, ranking, switching, pagamentos ou saída observável deliberadamente.

## Baseline de entrada

```text
BASELINE: main
HEAD: f9ea34bdec1d3a316f29acc490ac3bb55f2f65d5
ULTIMO_MERGE: PR #373 — ME-RUNTIME-CANON-03 reutiliza saída canônica na S7B
```

## Escopo permitido

```text
nucleo/matriz_elegibilidade_fontes_s7b.py
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/contexto_baseline.py
nucleo/construir_saida_canonica_v17_c7.py
nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
scripts/diagnostico/*
dados/*
saidas/*
```

## Alteração aplicada

Antes:

```python
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7

VERSAO_BASELINE = "V225"
```

Depois:

```python
from nucleo.construir_saida_canonica_v17_c7 import construir_saida_canonica_com_switching_v17_c7
from nucleo.identidade_baseline import VERSAO_BASELINE
```

A chamada fallback da S7B permanece semanticamente equivalente:

```python
saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
```

## Invariantes preservados

```text
ContextoBaseline: preservado
ContextoOperacionalCanonico: não alterado
principal.py: não alterado
S7B recebe saida_canonica_preconstruida: preservado
S7B fallback antigo: preservado
S7C: não alterado
Wrapper construir_saida_canonica_v17_c7.py: não alterado
Ranking: não alterado
Switching: não alterado
Regra econômica: não alterada
```

## Riscos controlados

| Risco | Tratamento |
|---|---|
| Divergência futura entre S7B e identidade oficial da baseline | removida ao centralizar `VERSAO_BASELINE` |
| Alteração observável na rota principal | risco baixo, pois a rota principal passa `saida_canonica_preconstruida` desde a ME-RUNTIME-CANON-03 |
| Quebra do fallback externo da S7B | mitigado porque `VERSAO_BASELINE` mantém o mesmo valor atual via identidade central |

## Decisão

```text
STATUS: S7B_IDENTIDADE_BASELINE_CENTRALIZADA
ALTERA_RUNTIME: sim_controlado
ALTERA_NUCLEO: sim_controlado
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: validar saída observável e depois auditar consumo indireto em saida_canonica.py e saida_observavel.py
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Comparar marcadores observáveis:

```text
relatorio_operacional_v225.xlsx gerado
patrimônio líquido atual = 79892.30
rendimento líquido atual = 952.14
ranking top 1 = Mercado Pago Cofrinho 120% CDI (Meli+)
4 switchings reais preservados
```

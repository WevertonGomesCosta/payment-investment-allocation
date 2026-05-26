# ME-RUNTIME-CANON-03 — S7B recebe saída canônica pré-construída

## Objetivo

Eliminar a dupla construção da saída canônica na rota runtime principal sem alterar a saída observável.

Antes desta microetapa, `aplicacao/principal.py` construía `saida_canonica` e, em seguida, `nucleo/matriz_elegibilidade_fontes_s7b.py` reconstruía internamente a saída ao montar a matriz de elegibilidade.

## Baseline de entrada

```text
BASELINE: main
HEAD: d6de574a00529c2e9288457811b913d3cce9a9a9
ULTIMO_MERGE: PR #372 — ME-RUNTIME-CANON-02 prova de equivalência do ContextoBaseline
```

## Escopo permitido

```text
aplicacao/principal.py
nucleo/matriz_elegibilidade_fontes_s7b.py
logs/iteracoes/*
```

## Escopo proibido

```text
nucleo/contexto_baseline.py
nucleo/construir_saida_canonica_v17_c7.py
nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py
scripts/diagnostico/*
dados/*
saidas/*
```

A ME-RUNTIME-CANON-03 não altera motor, replay, ledger, ranking, contrato mestre, modelo oficial, regra econômica, lógica de switching, lógica de pagamento ou XLSX deliberadamente.

## Alteração aplicada

### 1. `nucleo/matriz_elegibilidade_fontes_s7b.py`

A assinatura de `construir_matriz_elegibilidade_fontes_s7b()` passa a aceitar:

```python
saida_canonica_preconstruida=None
```

A função usa a saída pré-construída quando fornecida:

```python
saida = saida_canonica_preconstruida
if saida is None:
    saida = construir_saida_canonica_com_switching_v17_c7(contexto, versao=VERSAO_BASELINE)
```

A reconstrução interna permanece como fallback de retrocompatibilidade para chamadas externas que ainda não passem `saida_canonica_preconstruida`.

### 2. `aplicacao/principal.py`

A rota principal passa a reutilizar a saída já construída:

```python
matriz = construir_matriz_elegibilidade_fontes_s7b(
    contexto_baseline,
    data_referencia=saida_canonica.data_referencia,
    saida_canonica_preconstruida=saida_canonica,
)
```

## Efeito arquitetural

```text
ANTES: principal.py construia saida_canonica; S7B reconstruia saida_canonica internamente.
DEPOIS: principal.py constrói saida_canonica uma vez; S7B consome essa mesma saída na rota runtime principal.
```

## Invariantes preservados

```text
ContextoBaseline: preservado
ContextoOperacionalCanonico: não alterado
Wrapper construir_saida_canonica_v17_c7.py: não alterado
S7C: não alterado
Ranking: não alterado
Switching: não alterado
Saída canônica: mesma instância já construída antes da S7C
XLSX: esperado sem alteração observável
Console: esperado sem alteração observável
```

## Riscos controlados

| Risco | Tratamento |
|---|---|
| Quebra de chamadas externas da S7B | mitigado por parâmetro opcional com fallback antigo |
| Alteração observável de saída | mitigado porque `principal.py` passa a mesma saída já construída antes |
| Mudança de ordem S7C | não ocorre; S7C continua depois da matriz |
| Remoção de `VERSAO_BASELINE = "V225"` local | não feita nesta microetapa; fica para ME-RUNTIME-CANON-04 |

## Decisão

```text
STATUS: S7B_SAIDA_CANONICA_PRECONSTRUIDA_APLICADA
ALTERA_RUNTIME: sim_controlado
ALTERA_NUCLEO: sim_controlado
ALTERA_APLICACAO: sim_controlado
ALTERA_REGRA_ECONOMICA: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ETAPA_5_LIBERADA: false
PROXIMA_ACAO: validar equivalência observável da saída
```

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

Além dos gates acima, comparar a saída operacional esperada com o baseline imediatamente anterior:

```text
relatorio_operacional_v225.xlsx gerado
patrimônio líquido atual preservado
rendimento líquido atual preservado
ranking top 1 preservado
4 switchings reais preservados
próximos pagamentos sem nova decisão indevida
```

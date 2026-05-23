# ME-V17-F0-V4Z5 — Alinhamento de proveniência do ContextoOperacionalCanonico

```text
MICROETAPA: ME-V17-F0-V4Z5
VERSAO_CANDIDATA: V17-F0-V.4Z5
TIPO: CODIGO / DIAGNOSTICO
BASELINE_DE_ENTRADA: V17-F0-V.4Z4
BASE_MAIN: 79bfb4db4561c08d36b00a65a0f3a9dbac60487d
ALTERA_APLICACAO_PRINCIPAL: false
ALTERA_CONTEXT_BASELINE: false
ALTERA_RUNTIME_PRINCIPAL: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ALTERA_RANKING: false
ALTERA_XLSX: false
ALTERA_DADOS: false
```

## Objetivo

Alinhar a proveniência de entrada e a janela CDI do `ContextoOperacionalCanonico` no modo padrão, sem migrar `aplicacao/principal.py`.

## Escopo permitido

```text
nucleo/leitor_planilha.py
nucleo/contexto_baseline.py
scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py
```

## Validação esperada

```bash
python -m py_compile nucleo/leitor_planilha.py nucleo/contexto_baseline.py scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py
python scripts/diagnostico/auditar_equivalencia_contextos_v4z4.py --sem-arquivos
python -B aplicacao/principal.py
```

A Etapa 5 permanece bloqueada até validação local.

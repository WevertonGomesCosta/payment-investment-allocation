# ME-V17-F0-V4Z1 — Contexto operacional canônico antes da Etapa 5

```text
MICROETAPA: ME-V17-F0-V4Z1
VERSAO_CANDIDATA: V17-F0-V.4Z1
TIPO: CODIGO / DIAGNOSTICO
CLASSE: CONTEXTO_OPERACIONAL_CANONICO_LIMPO
ALTERA_CONTEXTOS_HISTORICOS: false
ALTERA_MOTOR: false
ALTERA_REPLAY: false
ALTERA_LEDGER: false
ALTERA_RANKING: false
ALTERA_SAIDA_XLSX: false
ALTERA_DADOS: false
```

## Objetivo

A V17-F0-V.4Z1 adiciona `ContextoOperacionalCanonico` e `carregar_contexto_operacional_canonico()` sem remover `ContextoBaseline`.

## Contrato

O contexto limpo não deve conter campos `shadow`, `benchmark`, módulos experimentais, sentinelas específicas ou chamadas a loaders versionados.

## Validação

```bash
python -m py_compile nucleo/contexto_baseline.py scripts/diagnostico/auditar_nucleo_vivo_v4z.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

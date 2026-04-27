# HOTFIX V224 — LIMPEZA PRÉ-RELEASE DE ARTEFATOS EFÊMEROS

## Status

`V224_CANDIDATA_DIAGNOSTICA_PRE_BASELINE`

A V224 usa a V223 validada e corrige a falha final de release causada por `__pycache__` e `.pyc` criados durante a execução dos diagnósticos.

## Problema

Após a V223 passar nas auditorias funcionais, o comando:

```bash
python scripts/diagnostico/verificar_release_baseline.py
```

falhou apenas por artefatos efêmeros:

```text
__pycache__
*.pyc
```

## Correção

Foram adicionados:

```bash
python scripts/diagnostico/limpar_artefatos_efemeros.py
python scripts/diagnostico/verificar_release_limpo.py
```

O segundo comando executa a limpeza e depois chama o release checker.

## Escopo negativo

- Não altera a regra econômica.
- Não altera o motor principal.
- Não altera cálculo de dias.
- Não altera idade fiscal.
- Não altera a decisão do gate.

# MICRO-ETAPA8-CORRECAO-01 — Corrige metadado temporal de SaidaCanonicaOficial para timezone-aware UTC

## Identificação

- **Microfrente:** MICRO-ETAPA8-CORRECAO-01
- **Tipo:** correção técnica cirúrgica
- **Baseline de entrada:** `105a30037847c9d4eea21986a7276dd78b85732a`
- **Branch:** `fix/micro-etapa8-correcao-01`

## Objetivo

Corrigir o metadado temporal `gerado_em` em `SaidaCanonicaOficial` para usar datetime UTC timezone-aware.

## Alteração

Em `nucleo/saida_canonica_oficial.py`:

```python
from datetime import date, datetime
```

foi substituído por:

```python
from datetime import date, datetime, timezone
```

E:

```python
datetime.utcnow().isoformat(timespec='seconds') + 'Z'
```

foi substituído por:

```python
datetime.now(timezone.utc).isoformat(timespec='seconds')
```

## Escopo preservado

A microfrente não altera:

- runtime;
- console;
- XLSX;
- motor;
- ledger;
- gates;
- contratos;
- lógica econômica;
- bloqueios da Etapa 8.

## Validação esperada

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

O comportamento esperado permanece: gates bloqueados impedem console/XLSX oficiais.

# Scripts diagnósticos canônicos — V203

Este diretório concentra diagnósticos e wrappers compatíveis com a camada de saída canônica.

## Regra V203

Scripts diagnósticos não têm autoridade operacional. Quando precisam observar pagamentos, switching, extrato ou cobertura, devem ler:

```python
from nucleo.saida_canonica import construir_saida_canonica
```

## Scripts bloqueados

Scripts legados com saída própria foram substituídos por stubs com o marcador:

```text
BLOQUEADO_POR_GOVERNANCA_V203
```

Os originais estão preservados em:

```text
scripts/historico_saida_propria_v203/
```

## Diagnósticos úteis mantidos

- `inspecionar_motor_recomendacao_pagamentos_switching_v1.py`
- `inspecionar_recomputacao_sequencial_central_v1.py`
- `inspecionar_base.py`
- `verificar_release_baseline.py`

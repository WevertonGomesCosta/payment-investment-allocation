# Scripts do repositório

Estrutura canônica da baseline vigente **V203**:

- `scripts/operacional/`: geração operacional oficial;
- `scripts/diagnostico/`: diagnósticos canônicos, wrappers e checagem de release;
- `scripts/auditoria/`: auditorias específicas;
- `scripts/historico_raiz/`: acervo histórico da antiga raiz de `scripts/`;
- `scripts/historico_saida_propria_v203/`: originais preservados dos scripts bloqueados na V203.

## Regra de autoridade operacional

A saída operacional oficial deve depender de:

```python
nucleo.saida_canonica.construir_saida_canonica(...)
```

Scripts legados que geravam console, CSV, Excel, JSON ou Markdown próprios foram bloqueados quando classificados como risco de divergência. Eles permanecem no caminho antigo apenas como stubs com bloqueio de governança.

## Caminhos oficiais

```bash
python scripts/operacional/gerar_planilha_operacional.py
python scripts/diagnostico/verificar_release_baseline.py
```

## Diagnósticos canônicos úteis

```bash
python scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py
python scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py
```

Esses diagnósticos leem `PacoteSaidaCanonica` e não têm autoridade para recalcular saída operacional paralela.


## Governança V204

A V204 aplica limpeza final de governança sem alteração econômica: código morto do console foi removido,
scripts históricos `.py` foram bloqueados, auditorias auxiliares foram separadas de saídas oficiais e
helpers utilitários de baixo risco foram centralizados em `nucleo/utilitarios_neutros.py`.

A camada oficial de saída permanece `nucleo.saida_canonica`.

# ME-V17-F0-V37S — Substitui switching bruto por canônico no ledger

## Escopo
- Promoção interna em `nucleo/ledger_temporal_conjunto.py` para usar `switching_canonico` como fonte primária de mapa/eventos.
- Caminho legado da aba `Switching` preservado como fallback auditável.
- Script de auditoria comparativa legado vs modo interno canônico.

## Implementação
- Funções legadas renomeadas para sufixo `_legado_v37s`.
- Funções canônicas internas adicionadas com schema compatível ao ledger.
- Funções operacionais passam a tentar canônico primeiro e cair para legado quando vazio/indisponível.

## Validação
- Executar:
  - `python -m py_compile nucleo/ledger_temporal_conjunto.py`
  - `python -m py_compile scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py`
  - `python scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py --sem-csv`
  - `python -B aplicacao/principal.py`
  - `git diff --check`
  - `git status --short`

# 04_decisao_rd07.md — RD-2026-04-28-07

## Decisão final
**METADADOS_SITUACAO_ATUAL_CORRIGIDOS_GO_COM_OBSERVACAO**

## Justificativa
1. A causa de mismatch de chaves foi tratada por mapeamento explícito no `principal.py`.
2. A validação estática confirma cobertura dos metadados alvo.
3. A validação dinâmica via `python aplicacao/principal.py` ficou bloqueada no ambiente atual por ausência de `scipy`, antes da seção `SITUAÇÃO ATUAL`.
4. Não há evidência de impacto em motor econômico, pagamentos, switching, função objetivo, dados oficiais, cache BCB/CDI ou `requirements.txt`.

## Observação remanescente
- Reexecutar `python aplicacao/principal.py` em ambiente com `scipy` disponível para confirmar visualmente no console a eliminação dos `None` remanescentes nos cinco campos alvo.

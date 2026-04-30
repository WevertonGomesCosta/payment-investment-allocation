# Fechamento final de inconsistências de legado pré-Codex — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:29:29

## Ações executadas

1. `aplicacao/console/secoes_financeiras.py`: neutralizado como stub legado.
2. `aplicacao/console/secoes_canonicas.py`: neutralizado como stub legado.
3. `AGENTS.md` corrigido para UTF-8 limpo e estado consistente.
4. `scripts/validacao/validar_rota_oficial_v225.py` criado/atualizado.
5. Scripts temporários movidos da raiz: 0.
6. `CODEX_READY_V225.md` e `INVENTARIO_LEGADO_INATIVO_V225.md` regenerados.

## Estado antes

- contexto único: SIM
- saída observável: SIM
- console sem `secoes_financeiras`: SIM
- console sem `secoes_canonicas`: SIM
- estado mínimo: NÃO

## Estado depois

- contexto único: SIM
- saída observável: SIM
- console sem `secoes_financeiras`: SIM
- console sem `secoes_canonicas`: SIM
- stubs legados ativos: SIM
- estado mínimo: SIM

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- pagamentos;
- switching;
- ranking;
- cache;
- `dados/config_atualizado.json`;
- rota principal.

## Validação necessária

```bash
python scripts/validacao/validar_rota_oficial_v225.py
python aplicacao/principal.py
```

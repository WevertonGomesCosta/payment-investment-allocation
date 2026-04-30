# Enxugamento final do repositório pré-Codex — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:43:03

## Ações executadas

1. Helpers locais com nomes parecidos com funções legadas renomeados: 0.
2. Arquivos legados reduzidos a stub removidos: 0.
3. Arquivos/diretórios auxiliares temporários removidos: 4.
4. `AGENTS.md` atualizado para refletir remoção dos legados.
5. `scripts/validacao/validar_rota_oficial_v225.py` atualizado para validar ausência dos legados.
6. `CODEX_READY_V225.md` e `INVENTARIO_LEGADO_INATIVO_V225.md` regenerados.

## Avisos

```text
aplicacao/console/secoes_financeiras.py: já ausente
aplicacao/console/secoes_canonicas.py: já ausente
```

## Estado depois

- contexto único: SIM
- saída observável: SIM
- console sem `secoes_financeiras`: SIM
- console sem `secoes_canonicas`: SIM
- legados removidos: SIM
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

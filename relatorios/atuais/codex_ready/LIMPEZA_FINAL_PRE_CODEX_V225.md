# Limpeza final pré-Codex — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T12:57:42
- Escopo: limpeza estrutural final para facilitar uso pelo Codex

## Ações executadas

1. `AGENTS.md` normalizado em UTF-8 limpo.
2. Criado `scripts/validacao/validar_rota_oficial_v225.py`.
3. `aplicacao/console/secoes_financeiras.py`: mantido: referências operacionais externas encontradas.
4. `aplicacao/console/secoes_canonicas.py`: mantido: referências operacionais externas encontradas.
5. Scripts temporários removidos da raiz: 0.
6. Relatórios Codex-ready regenerados.

## Estado antes

- contexto único: SIM
- saída observável: SIM
- sem uso operacional de `secoes_financeiras.py`: NÃO
- estado mínimo: NÃO

## Estado depois

- contexto único: SIM
- saída observável: SIM
- sem uso operacional de `secoes_financeiras.py`: NÃO
- estado mínimo: NÃO

## Restrições respeitadas

Não houve alteração em:

- cálculo econômico;
- replay;
- regra de pagamentos;
- switching;
- ranking;
- cache;
- `dados/config_atualizado.json`;
- identidade da baseline V225;
- relatórios históricos.

## Validação necessária

```bash
python scripts/validacao/validar_rota_oficial_v225.py
python aplicacao/principal.py
```

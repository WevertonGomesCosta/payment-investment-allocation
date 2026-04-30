# CODEX-ready V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:43:03
- Tipo: enxugamento final do repositório pré-Codex
- Escopo: remoção de stubs legados e arquivos temporários
- Alteração de motor econômico: não
- Alteração de replay: não
- Alteração de pagamentos: não
- Alteração de switching: não
- Alteração de ranking: não
- Alteração de cache: não

## Estado auditado

| Item | Status |
|---|---:|
| `aplicacao/principal.py` existe | SIM |
| `dados/config_atualizado.json` existe | SIM |
| Entrada oficial carrega contexto único | SIM |
| Console e planilha usam dados observáveis centralizados | SIM |
| Console sem dependência operacional de `secoes_financeiras.py` | SIM |
| Console sem dependência operacional de `secoes_canonicas.py` | SIM |
| Arquivos legados de console removidos | SIM |
| Planilha não cria aba `Validacao` | SIM |
| Estado mínimo Codex-ready | SIM |

## Rota oficial

```text
aplicacao/principal.py
├── carregar_contexto_baseline(...) uma única vez
├── construir_saida_canonica(...) uma única vez
├── render_console(contexto_baseline, saida_canonica)
└── gerar_planilha_operacional(contexto=contexto_baseline, saida=saida_canonica)
```

## Comando oficial de validação

```bash
python scripts/validacao/validar_rota_oficial_v225.py
```

## Saída esperada

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

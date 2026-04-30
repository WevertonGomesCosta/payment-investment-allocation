# Inventário de legado inativo — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:29:29
- Escopo: fechamento final de inconsistências de legado pré-Codex

## Legados de console neutralizados

### `aplicacao/console/secoes_financeiras.py`

Status: neutralizado como stub legado

Backup preservado em:

```text
relatorios/atuais/codex_ready/legado_preservado/secoes_financeiras_original_v225.txt
```

### `aplicacao/console/secoes_canonicas.py`

Status: neutralizado como stub legado

Backup preservado em:

```text
relatorios/atuais/codex_ready/legado_preservado/secoes_canonicas_original_v225.txt
```

## Scripts temporários removidos da raiz

```text
nenhum script temporário encontrado na raiz
```

Cópias preservadas em:

```text
relatorios/atuais/codex_ready/scripts_temporarios_removidos/
```

## Regra para Codex

Qualquer alteração que afete dados mostrados simultaneamente no console e na planilha deve seguir esta ordem:

```text
1. alterar ou criar contrato em nucleo/saida_observavel.py
2. renderizar no console sem recalcular
3. renderizar na planilha sem recalcular
4. validar python scripts/validacao/validar_rota_oficial_v225.py
```

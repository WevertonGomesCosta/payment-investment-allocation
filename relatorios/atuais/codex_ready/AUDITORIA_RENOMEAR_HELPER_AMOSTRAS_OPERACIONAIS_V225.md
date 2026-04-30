# Renomeação de helper local de amostras operacionais — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:11:51
- Arquivo alterado: `aplicacao/console/principal.py`

## Problema

O auditor Codex-ready estava classificando falsamente o helper local `_render_secao_amostras_pagamentos` como uso operacional da função legada `render_secao_amostras_pagamentos`, porque o nome novo ainda continha a string da função antiga.

## Correção

O helper local foi renomeado para:

```text
_render_amostras_pagamentos_operacionais
```

A chamada correspondente também foi atualizada.

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- regra de pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline V225;
- `dados/config_atualizado.json`.

## Validação esperada

```bash
python corrigir_classificacao_rota_codex_ready_v225.py
grep -n "Estado mínimo" relatorios/atuais/codex_ready/CODEX_READY_V225.md
python scripts/validacao/validar_rota_oficial_v225.py
python aplicacao/principal.py
```

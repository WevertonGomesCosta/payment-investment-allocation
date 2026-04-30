# Auditoria de funções render_secao_* em secoes_financeiras — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T10:41:57
- Arquivo auditado: `aplicacao/console/secoes_financeiras.py`
- Objetivo: detectar funções próprias/duplicadas que possam recriar divergência entre console e planilha.

## Contrato atual

- `aplicacao/principal.py` usa contexto único: SIM
- console usa `nucleo/saida_observavel.py`: SIM
- planilha usa `construir_blocos_situacao_atual(...)`: SIM
- `nucleo/saida_observavel.py` lido: SIM

## Resumo

- Funções `render_secao_*` encontradas: 12
- CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL: 7
- LEGADO_NAO_OPERACIONAL_APARENTE: 3
- NEUTRALIZADA: 1
- USADA_PELA_ROTA_OFICIAL: 1

## Classificação detalhada

| Função | Linhas | Classe | Refs externas | Ação recomendada |
|---|---:|---|---:|---|
| `render_secao_nucleo` | 6-42 | LEGADO_NAO_OPERACIONAL_APARENTE | 0 | Candidata a remoção futura em lote pequeno, com validação. |
| `render_secao_replay` | 45-110 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_metodo_pagamentos` | 116-148 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_amostras_pagamentos` | 150-167 | USADA_PELA_ROTA_OFICIAL | 2 | Manter; se virar saída comum, migrar contrato para `saida_observavel.py`. |
| `render_secao_auditoria_temporal_pagamentos` | 171-196 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_reescolha_dinamica_pagamentos` | 200-235 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_heuristica_conjunta_parcial` | 239-286 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_situacao_atual` | 288-308 | NEUTRALIZADA | 2 | Manter neutralizada; remover só em microetapa futura segura. |
| `render_secao_planejamento_conjunto_local` | 310-349 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_microplanejamento_conjunto_v2` | 352-393 | CANDIDATA_MIGRACAO_SAIDA_OBSERVAVEL | 0 | Não reativar diretamente; migrar dados para `saida_observavel.py`. |
| `render_secao_recomputacao_sequencial_central_v1` | 396-431 | LEGADO_NAO_OPERACIONAL_APARENTE | 0 | Candidata a remoção futura em lote pequeno, com validação. |
| `render_secao_motor_recomendacao_pagamentos_switching_v1` | 434-484 | LEGADO_NAO_OPERACIONAL_APARENTE | 0 | Candidata a remoção futura em lote pequeno, com validação. |

## Referências externas por função

### `render_secao_nucleo`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_replay`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_metodo_pagamentos`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_amostras_pagamentos`

```text
aplicacao/console/principal.py:20:from aplicacao.console.secoes_financeiras import render_secao_amostras_pagamentos | aplicacao/console/principal.py:182:    render_secao_amostras_pagamentos(
```

### `render_secao_auditoria_temporal_pagamentos`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_reescolha_dinamica_pagamentos`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_heuristica_conjunta_parcial`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_situacao_atual`

```text
aplicacao/console/principal.py:81:def _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None: | aplicacao/console/principal.py:220:    _render_secao_situacao_atual(
```

### `render_secao_planejamento_conjunto_local`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_microplanejamento_conjunto_v2`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_recomputacao_sequencial_central_v1`

```text
nenhuma referência externa operacional encontrada
```

### `render_secao_motor_recomendacao_pagamentos_switching_v1`

```text
nenhuma referência externa operacional encontrada
```

## Decisão desta microetapa

Esta auditoria não removeu funções automaticamente. Remoções devem ocorrer em lote pequeno após revisar itens classificados como `LEGADO_NAO_OPERACIONAL_APARENTE`.

## Validação sugerida

```bash
python -m py_compile aplicacao/console/secoes_financeiras.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py aplicacao/principal.py
python aplicacao/principal.py
```

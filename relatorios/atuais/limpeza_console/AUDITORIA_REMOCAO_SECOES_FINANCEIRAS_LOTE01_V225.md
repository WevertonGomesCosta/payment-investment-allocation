# Auditoria de remoção de funções legadas — secoes_financeiras — lote 01 — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T10:58:35
- Arquivo alterado: `aplicacao/console/secoes_financeiras.py`
- Tipo: remoção controlada de funções legadas não operacionais aparentes

## Funções removidas

- `render_secao_nucleo`
- `render_secao_recomputacao_sequencial_central_v1`
- `render_secao_motor_recomendacao_pagamentos_switching_v1`

## Funções explicitamente preservadas

- `render_secao_amostras_pagamentos`
- `render_secao_situacao_atual`
- `render_secao_replay`
- `render_secao_metodo_pagamentos`
- `render_secao_auditoria_temporal_pagamentos`
- `render_secao_reescolha_dinamica_pagamentos`
- `render_secao_heuristica_conjunta_parcial`
- `render_secao_planejamento_conjunto_local`
- `render_secao_microplanejamento_conjunto_v2`

## Critério de remoção

As três funções removidas foram classificadas na auditoria anterior como `LEGADO_NAO_OPERACIONAL_APARENTE`, sem referências externas operacionais.

Foram preservadas:

- a função usada pela rota oficial: `render_secao_amostras_pagamentos`;
- a função neutralizada: `render_secao_situacao_atual`;
- as funções candidatas à migração futura para `nucleo/saida_observavel.py`.

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline.

## Validação local necessária

```bash
python -m py_compile aplicacao/console/secoes_financeiras.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py aplicacao/principal.py
python aplicacao/principal.py
```

## Status da remoção

- Removidas com sucesso: render_secao_nucleo, render_secao_recomputacao_sequencial_central_v1, render_secao_motor_recomendacao_pagamentos_switching_v1
- Preservadas com sucesso: render_secao_amostras_pagamentos, render_secao_situacao_atual, render_secao_replay, render_secao_metodo_pagamentos, render_secao_auditoria_temporal_pagamentos, render_secao_reescolha_dinamica_pagamentos, render_secao_heuristica_conjunta_parcial, render_secao_planejamento_conjunto_local, render_secao_microplanejamento_conjunto_v2

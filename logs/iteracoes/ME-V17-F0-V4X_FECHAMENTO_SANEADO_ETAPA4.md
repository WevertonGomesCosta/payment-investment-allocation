# ME-V17-F0-V4X — Fechamento saneado da Etapa 4

## Objetivo
Executar validação final da Etapa 4 (V4U/V4V/V4W + cache BCB de 2026-05-22) removendo falsos negativos do auditor V4X e classificando apenas bloqueios funcionais reais.

## Baseline de entrada
- Repositório `WevertonGomesCosta/payment-investment-allocation`.
- Referência: pós PR #352 e commit `57b3e7d` (cache BCB para 2026-05-22).

## Ajustes aplicados no V4X
- Robustez P2: `_auditar_cache_bcb()` agora trata ausência de `dados/cache_bcb.json` sem abortar (retorna status `cache_bcb_ausente`).
- Robustez P2: parse do output do V4W protegido com `try/except`, expondo `v4w_parse_ok` e `v4w_parse_erro` sem interromper V4X.
- Correção do cálculo do Lote 3120 via saída observável consolidada com pacote (campos `Bruto sac.`, `Líq. sac.`, `Líq. atual`), eliminando falso negativo de bruto sacado.
- Substituição de varredura textual por auditoria AST/estrutural para distinguir ocorrência funcional ativa de comentário/string.
- Classificação explícita da falha de `aplicacao/principal.py` por ambiente (`erro_csv_s6_ausente_sem_recomposicao_segura`) sem marcar regressão funcional da V4X.
- Regra da próxima etapa corrigida: Etapa 5 só recomendada quando fechamento saneado estiver ok.

## Evidências coletadas

### V4U / V4V / V4W
- `v4u_validada=true`
- `v4v_validada=true`
- `v4w_validada=true`
- `console_consumindo_pacote=true`
- `xlsx_consumindo_pacote=true`
- `saida_observavel_sem_fallback_silencioso_sem_pacote=true`
- `funcoes_publicas_criticas_exigem_ou_recebem_pacote=true`

### Cache BCB
- `data_referencia=2026-05-22`
- `cache_bcb_registrado=true`
- `cache_bcb_atualizado_para_referencia=true`
- `data_atualizacao_cache=2026-05-22`
- `ultima_data_com_fator_no_cache=2026-05-21`
- `status_obtencao_cdi_bcb=cache_atualizado_sem_fetch`

### Lote 3120 mai (corrigido)
- `lote_3120_mai_presente_ativos=true`
- `lote_3120_mai_presente_exauridos=false`
- `lote_3120_mai_saldo_final=50.52`
- `lote_3120_mai_bruto_sacado=3093.76`
- `lote_3120_mai_liquido_sacado=3088.95`
- `lote_3120_mai_validado=true`

### principal.py (ambiente vs regressão)
- `principal_py_ok=false`
- `principal_py_falha_ambiente=true`
- `principal_py_erro=erro_csv_s6_ausente_sem_recomposicao_segura`
- Classificação: falha ambiental explícita, não regressão funcional intrínseca da V4X.

### Resíduos proibidos funcionais (AST)
- `residuos_proibidos_funcionais_restantes=10`
- Itens funcionais ativos identificados:
  - `_lote_deve_ser_ativo_observavel_por_replay`
  - `_mapa_aplicacao_por_lote`
  - `_mapa_pagamentos_replay_por_chave`
  - `_mapa_produto_por_lote`
  - `_mapa_saldo_final_replay_por_lote`
  - `_mapa_valor_original_por_lote`
  - `getattr.__dict__`
  - `getattr.log_passado`
  - `getattr.replay_passado`
  - `somar_valores_sacados_por_lote`

## Decisão técnica
- Observação: o bloqueio atual é **real** por resíduos funcionais remanescentes detectados por AST, e não apenas falso positivo textual.
- `etapa4_fechamento_saneado_ok=false`
- `etapa5_pode_abrir=false`
- `proxima_etapa_recomendada=V17-F0-V.4X-ajuste`

## Resíduos permitidos remanescentes
Não aplicável nesta execução: os remanescentes detectados são funcionais/ativos no runtime de `nucleo/saida_observavel.py`.

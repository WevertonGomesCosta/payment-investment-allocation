# ME-V17-F0-V4X — Fechamento saneado da Etapa 4

## Objetivo
Executar validação final de fechamento saneado da Etapa 4 (V4U/V4V/V4W + cache BCB 2026-05-22), verificando prontidão técnica para abertura da Etapa 5 sem alteração funcional.

## Baseline de entrada
- Branch atual do repositório `WevertonGomesCosta/payment-investment-allocation`.
- Referência informada: pós merge PR #352 e commit `57b3e7d` (cache BCB 2026-05-22).

## Evidências coletadas

### V4U / V4V / V4W
- `v4u_validada=true`.
- `v4v_validada=true`.
- `v4w_validada=true`.
- `console_consumindo_pacote=true`.
- `xlsx_consumindo_pacote=true`.
- `saida_observavel_sem_fallback_silencioso_sem_pacote=true`.
- `funcoes_publicas_criticas_exigem_ou_recebem_pacote=true`.

### Cache BCB
- `data_referencia=2026-05-22`.
- `cache_bcb_registrado=true`.
- `cache_bcb_atualizado_para_referencia=true`.
- `data_atualizacao_cache=2026-05-22`.
- `ultima_data_com_fator_no_cache=2026-05-21`.
- `status_obtencao_cdi_bcb=cache_atualizado_sem_fetch`.

### Lote 3120 mai
- `lote_3120_mai_presente_ativos=true`.
- `lote_3120_mai_presente_exauridos=false`.
- `lote_3120_mai_saldo_final=50.52`.
- `lote_3120_mai_bruto_sacado=3088.95` (divergente do esperado 3093.76).
- `lote_3120_mai_liquido_sacado=3088.95`.
- `lote_3120_mai_validado=false`.

### Runtime/XLSX operacional
- `principal_py_ok=false` por `RuntimeError: erro_csv_s6_ausente_sem_recomposicao_segura`.
- `saida_operacional_xlsx_gerada=false` neste ambiente.

### Auditoria estática de resíduos proibidos em `nucleo/saida_observavel.py`
- `residuos_proibidos_restantes=15`.
- Resíduos encontrados (nomes proibidos):
  - `somar_valores_sacados_por_lote`
  - `_mapa_aplicacao_por_lote`
  - `_mapa_produto_por_lote`
  - `_mapa_valor_original_por_lote`
  - `_mapa_saldo_final_replay_por_lote`
  - `_mapa_pagamentos_replay_por_chave`
  - `_lote_deve_ser_ativo_observavel_por_replay`
  - `replay_passado`
  - `log_passado`
  - `lotes_apos_replay`
  - `lotes_antes_replay`
  - `lotes_replay`
  - `lotes_originais`
  - `fila = [contexto]`
  - `getattr(obj, "__dict__"`

## Decisão de fechamento saneado da Etapa 4
- `etapa4_funcional=false`.
- `etapa4_saneada=false`.
- `etapa4_fechamento_saneado_ok=false`.
- `etapa5_pode_abrir=false`.

## Autorização técnica para Etapa 5
**Não autorizada nesta execução V4X**, pois existem bloqueios de runtime e resíduos proibidos remanescentes na saída observável.

## Resíduos permitidos remanescentes
Nesta execução, os remanescentes identificados **não foram classificados como apenas históricos/arquivados**; são referências encontradas no arquivo de runtime `nucleo/saida_observavel.py` e bloqueiam o fechamento saneado.

# Auditoria de `_safe_float` — V225

## Identificação

- Data/hora local: 2026-04-30T14:32:49
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código funcional: não

## Objetivo

Auditar a duplicidade entre:

```text
nucleo.aportes_futuros_planejados._safe_float
nucleo.utilitarios_neutros._safe_float
```

sem alterar motor econômico, replay, pagamentos, switching, ranking, cache nem `dados/config_atualizado.json`.

## Resumo

| Métrica | Valor |
|---|---:|
| definições encontradas | 2 |
| assinaturas distintas | 2 |
| hashes AST distintos | 2 |
| chamadas AST encontradas | 135 |
| arquivos com chamadas | 7 |
| casos comportamentais divergentes | 4 |

## Definições

| Arquivo | Linha | Assinatura | Hash AST | Resumo |
|---|---:|---|---|---|
| `nucleo/aportes_futuros_planejados.py` | 20 | `(valor, padrao=...)` | `8204bbd7cf1a35fe` | def _safe_float(valor: Any, padrao: float = 0.0) -> float: if valor is None: return padrao try: if hasattr(valor, "isna") and valor.isna(): return padrao except Exception: pass if isinstance(valor, str): bruto = valor.replace("R$", "").replace(" ", "").stri... |
| `nucleo/utilitarios_neutros.py` | 159 | `(valor, default=...)` | `baa356995668eef4` | def _safe_float(valor: Any, default: float = 0.0) -> float: try: if valor in (None, ''): return float(default) return float(valor) except Exception: return float(default) |

## Comparação comportamental isolada

| Caso | Entrada | Aportes | Utilitários | Iguais |
|---|---|---|---|---:|
| `none` | `None` | `0.0` | `0.0` | SIM |
| `vazio` | `''` | `0.0` | `0.0` | SIM |
| `espaco` | `' '` | `0.0` | `0.0` | SIM |
| `inteiro` | `123` | `123.0` | `123.0` | SIM |
| `float` | `123.45` | `123.45` | `123.45` | SIM |
| `string_float_ponto` | `'123.45'` | `123.45` | `123.45` | SIM |
| `string_decimal_virgula` | `'123,45'` | `123.45` | `0.0` | NAO |
| `string_milhar_br` | `'1.234,56'` | `1234.56` | `0.0` | NAO |
| `string_moeda_br` | `'R$ 1.234,56'` | `1234.56` | `0.0` | NAO |
| `string_moeda_negativa` | `'-R$ 1.234,56'` | `-1234.56` | `0.0` | NAO |
| `string_percentual` | `'12,5%'` | `0.0` | `0.0` | SIM |
| `texto_invalido` | `'abc'` | `0.0` | `0.0` | SIM |
| `nan_float` | `nan` | `nan` | `nan` | SIM |

## Chamadas detectadas

| Arquivo | Linha | Escopo | Conteúdo |
|---|---:|---|---|
| `nucleo/alocador_pagamentos_terminal_v1.py` | 127 | `_valor_pagamento` | return round(_safe_float(pagamento[chave]), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 184 | `_estimar_custo_fiscal_lote` | valor_total = round(_safe_float(bruto.get('valor_liquido_resgatavel') or bruto.get('valor_disponivel') or bruto.get('principal_remanescente')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 185 | `_estimar_custo_fiscal_lote` | principal_total = round(_safe_float(bruto.get('principal_remanescente') or bruto.get('valor_inicial')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 213 | `_impacto_unitario_combo` | valor_disponivel = max(_safe_float(item.get('valor_disponivel')), 0.0) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 215 | `_impacto_unitario_combo` | custo_fiscal = max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 217 | `_impacto_unitario_combo` | liquidez = _safe_float(item.get('penalidade_liquidez_unitaria'), 0.0) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 225 | `_chave_combo_script1` | valor_coberto=min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 226 | `_chave_combo_script1` | valor_deficit=max(valor_pagamento - max(_safe_float(item.get('valor_disponivel')), 0.0), 0.0), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 227 | `_chave_combo_script1` | custo_fiscal_imediato=max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 229 | `_chave_combo_script1` | min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 233 | `_chave_combo_script1` | penalidade_liquidez_futura=max(_safe_float(item.get('penalidade_liquidez_unitaria')), 0.0) * min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 233 | `_chave_combo_script1` | penalidade_liquidez_futura=max(_safe_float(item.get('penalidade_liquidez_unitaria')), 0.0) * min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 234 | `_chave_combo_script1` | penalidade_estrategica_lote=min(valor_pagamento, max(_safe_float(item.get('valor_disponivel')), 0.0)) * _normalizar_proxy_terminal(item.get('proxy_terminal')), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 295 | `alocar_pagamento_terminal_v1` | saldo_disponivel = round(_safe_float(estado.get('saldo_disponivel_geral')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 376 | `alocar_pagamento_terminal_v1` | valor_fonte = round(_safe_float(bruto.get('valor') or bruto.get('valor_disponivel')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 430 | `alocar_pagamento_terminal_v1` | valor_fonte = round(_safe_float(bruto.get('valor_liquido_resgatavel') or bruto.get('principal_remanescente')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 483 | `alocar_pagamento_terminal_v1` | [x for x in candidatos_combo if _safe_float(x.get('valor_disponivel')) > 0.0], |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 495 | `alocar_pagamento_terminal_v1` | valor_disponivel = round(_safe_float(item.get('valor_disponivel')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 500 | `alocar_pagamento_terminal_v1` | custo_fiscal_total_item = max(_safe_float(item.get('custo_fiscal_total_estimado')), 0.0) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 562 | `alocar_pagamento_terminal_v1` | custo_fiscal_switch = round(_safe_float(plano.get('custo_fiscal_switching_total') or plano.get('custo_fiscal_realizado') or plano.get('custo_fiscal_estimado')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 563 | `alocar_pagamento_terminal_v1` | perda_liquidez_switch = round(_safe_float(plano.get('perda_liquidez_switching_total') or plano.get('perda_liquidez_estimada')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 564 | `alocar_pagamento_terminal_v1` | delta_perda_switch = round(_safe_float(plano.get('delta_perda_terminal_vs_baseline') or plano.get('ganho_terminal_economico_minimo_estimado')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 565 | `alocar_pagamento_terminal_v1` | perda_terminal_total = round(_safe_float(subresultado.get('perda_retorno_terminal_estimada')) + delta_perda_switch, 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 566 | `alocar_pagamento_terminal_v1` | penalidade_liquidez_total = round(_safe_float(subresultado.get('penalidade_liquidez_futura')) + perda_liquidez_switch, 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 567 | `alocar_pagamento_terminal_v1` | custo_fiscal_total = round(_safe_float(subresultado.get('custo_fiscal_imediato')) + custo_fiscal_switch, 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 568 | `alocar_pagamento_terminal_v1` | valor_deficit = round(_safe_float(subresultado.get('valor_deficit')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 569 | `alocar_pagamento_terminal_v1` | valor_coberto = round(_safe_float(subresultado.get('valor_coberto')), 2) |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 585 | `alocar_pagamento_terminal_v1` | penalidade_estrategica_lote=round(_safe_float(subresultado.get('penalidade_estrategica_lote')), 2), |
| `nucleo/alocador_pagamentos_terminal_v1.py` | 591 | `alocar_pagamento_terminal_v1` | penalidade_estrategica=round(_safe_float(subresultado.get('penalidade_estrategica_lote')), 2), |
| `nucleo/aportes_futuros_planejados.py` | 55 | `_config_aportes_v216` | "tolerancia_monetaria": round(_safe_float(bruto.get("tolerancia_monetaria", 0.01), 0.01), 2), |
| `nucleo/aportes_futuros_planejados.py` | 71 | `_valor_atual_recebido` | return round(_safe_float(item.get("valor_disponivel", item.get("valor"))), 2) |
| `nucleo/aportes_futuros_planejados.py` | 76 | `_valor_original_recebido` | return round(_safe_float( |
| `nucleo/aportes_futuros_planejados.py` | 80 | `_valor_original_recebido` | or (atual + _safe_float(item.get("valor_pago_com_recebido_v216")) + _safe_float(item.get("valor_aportado_planejado_v216"))) |
| `nucleo/aportes_futuros_planejados.py` | 80 | `_valor_original_recebido` | or (atual + _safe_float(item.get("valor_pago_com_recebido_v216")) + _safe_float(item.get("valor_aportado_planejado_v216"))) |
| `nucleo/aportes_futuros_planejados.py` | 99 | `_demanda_pagamentos_futuros` | return round(sum(_safe_float(p.get("valor")) for p in _pagamentos_futuros_janela(estado, data_atual, dias)), 2) |
| `nucleo/aportes_futuros_planejados.py` | 103 | `_capacidade_caixa_outras_fontes` | saldo = _safe_float(estado.get("saldo_disponivel_geral")) |
| `nucleo/aportes_futuros_planejados.py` | 139 | `_selecionar_produto_destino_v216` | aplicacao_minima = _safe_float(prod.get("aplicacao_minima")) |
| `nucleo/aportes_futuros_planejados.py` | 140 | `_selecionar_produto_destino_v216` | aplicacao_maxima = _safe_float(prod.get("aplicacao_maxima")) |
| `nucleo/aportes_futuros_planejados.py` | 141 | `_selecionar_produto_destino_v216` | liquidez_dias = int(_safe_float(prod.get("liquidez_dias"), 0.0)) |
| `nucleo/aportes_futuros_planejados.py` | 142 | `_selecionar_produto_destino_v216` | carencia_dias = int(_safe_float(prod.get("carencia_dias"), 0.0)) |
| `nucleo/aportes_futuros_planejados.py` | 160 | `_selecionar_produto_destino_v216` | _safe_float(prod.get("score_final")), |
| `nucleo/aportes_futuros_planejados.py` | 161 | `_selecionar_produto_destino_v216` | _safe_float(prod.get("retorno_anual_proxy")), |
| `nucleo/aportes_futuros_planejados.py` | 202 | `_construir_lote_planejado_v216` | liquidez_dias = int(_safe_float(produto.get("liquidez_dias"), 0.0)) |
| `nucleo/aportes_futuros_planejados.py` | 203 | `_construir_lote_planejado_v216` | carencia_dias = int(_safe_float(produto.get("carencia_dias"), 0.0)) |
| `nucleo/aportes_futuros_planejados.py` | 215 | `_construir_lote_planejado_v216` | "retorno_anual_proxy_atual": _safe_float(produto.get("retorno_anual_proxy")), |
| `nucleo/aportes_futuros_planejados.py` | 222 | `_construir_lote_planejado_v216` | "taxa_base_cdi": _safe_float(produto.get("taxa_base_cdi")), |
| `nucleo/aportes_futuros_planejados.py` | 223 | `_construir_lote_planejado_v216` | "taxa_bonus_cdi": _safe_float(produto.get("taxa_bonus_cdi")), |
| `nucleo/aportes_futuros_planejados.py` | 302 | `materializar_aportes_planejados_v216` | valor_pago = round(_safe_float(recebido.get("valor_pago_com_recebido_v216")), 2) |
| `nucleo/aportes_futuros_planejados.py` | 319 | `materializar_aportes_planejados_v216` | retorno = _safe_float((produto or {}).get("retorno_anual_proxy")) |
| `nucleo/aportes_futuros_planejados.py` | 352 | `materializar_aportes_planejados_v216` | "liquidez_dias_destino": int(_safe_float((produto or {}).get("liquidez_dias"))), |
| `nucleo/aportes_futuros_planejados.py` | 353 | `materializar_aportes_planejados_v216` | "carencia_dias_destino": int(_safe_float((produto or {}).get("carencia_dias"))), |
| `nucleo/aportes_futuros_planejados.py` | 376 | `materializar_aportes_planejados_v216` | recebido["valor_aportado_planejado_v216"] = round(_safe_float(recebido.get("valor_aportado_planejado_v216")) + valor_aporte, 2) |
| `nucleo/aportes_futuros_planejados.py` | 396 | `avaliar_gate_economico_aportes_planejados_v220` | tol = max(_safe_float(tolerancia, 0.01), 0.0) |
| `nucleo/aportes_futuros_planejados.py` | 398 | `avaliar_gate_economico_aportes_planejados_v220` | if _safe_float(delta_patrimonio_terminal_proxy) < -tol: |
| `nucleo/aportes_futuros_planejados.py` | 400 | `avaliar_gate_economico_aportes_planejados_v220` | if _safe_float(delta_perda_terminal_total) > tol: |
| `nucleo/aportes_futuros_planejados.py` | 402 | `avaliar_gate_economico_aportes_planejados_v220` | if _safe_float(delta_penalidade_estrategica_total) > tol: |
| `nucleo/aportes_futuros_planejados.py` | 404 | `avaliar_gate_economico_aportes_planejados_v220` | if _safe_float(delta_deficit_total) > tol: |
| `nucleo/aportes_futuros_planejados.py` | 411 | `avaliar_gate_economico_aportes_planejados_v220` | "delta_patrimonio_terminal_proxy": round(_safe_float(delta_patrimonio_terminal_proxy), 2), |
| `nucleo/aportes_futuros_planejados.py` | 412 | `avaliar_gate_economico_aportes_planejados_v220` | "delta_perda_terminal_total": round(_safe_float(delta_perda_terminal_total), 2), |
| `nucleo/aportes_futuros_planejados.py` | 413 | `avaliar_gate_economico_aportes_planejados_v220` | "delta_penalidade_estrategica_total": round(_safe_float(delta_penalidade_estrategica_total), 2), |
| `nucleo/aportes_futuros_planejados.py` | 414 | `avaliar_gate_economico_aportes_planejados_v220` | "delta_deficit_total": round(_safe_float(delta_deficit_total), 2), |
| `nucleo/comparador_hibrido_switching_v1.py` | 29 | `classificar_cenario_diario` | delta_perda = _safe_float(resultado.get('delta_perda_terminal_vs_baseline')) |
| `nucleo/comparador_hibrido_switching_v1.py` | 30 | `classificar_cenario_diario` | delta_patrimonio = _safe_float(resultado.get('delta_patrimonio_proxy_vs_baseline')) |
| `nucleo/comparador_hibrido_switching_v1.py` | 31 | `classificar_cenario_diario` | delta_deficit = _safe_float(resultado.get('delta_deficit_vs_baseline')) |
| `nucleo/comparador_hibrido_switching_v1.py` | 32 | `classificar_cenario_diario` | delta_protegida = _safe_float(resultado.get('delta_violacoes_protegida_vs_baseline')) |
| `nucleo/comparador_hibrido_switching_v1.py` | 85 | `chave_promocao_hibrida` | _safe_float(resultado.get('delta_perda_terminal_vs_baseline')), |
| `nucleo/comparador_hibrido_switching_v1.py` | 86 | `chave_promocao_hibrida` | _safe_float(resultado.get('delta_deficit_vs_baseline')), |
| `nucleo/comparador_hibrido_switching_v1.py` | 87 | `chave_promocao_hibrida` | -_safe_float(resultado.get('delta_patrimonio_proxy_vs_baseline')), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 97 | `_comparar_com_baseline` | 'delta_perda_terminal_vs_baseline': round(_safe_float(metrica.get('perda_patrimonio_liquido_terminal')) - _safe_float(base.get('perda_patrimonio_liquido_terminal')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 97 | `_comparar_com_baseline` | 'delta_perda_terminal_vs_baseline': round(_safe_float(metrica.get('perda_patrimonio_liquido_terminal')) - _safe_float(base.get('perda_patrimonio_liquido_terminal')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 98 | `_comparar_com_baseline` | 'delta_deficit_vs_baseline': round(_safe_float(metrica.get('deficit_liquido_total')) - _safe_float(base.get('deficit_liquido_total')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 98 | `_comparar_com_baseline` | 'delta_deficit_vs_baseline': round(_safe_float(metrica.get('deficit_liquido_total')) - _safe_float(base.get('deficit_liquido_total')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 99 | `_comparar_com_baseline` | 'delta_violacoes_protegida_vs_baseline': round(_safe_float(metrica.get('violacoes_protegida')) - _safe_float(base.get('violacoes_protegida')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 99 | `_comparar_com_baseline` | 'delta_violacoes_protegida_vs_baseline': round(_safe_float(metrica.get('violacoes_protegida')) - _safe_float(base.get('violacoes_protegida')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 100 | `_comparar_com_baseline` | 'delta_patrimonio_proxy_vs_baseline': round(_safe_float(sim.get('patrimonio_liquido_terminal_proxy')) - _safe_float(baseline.get('patrimonio_liquido_terminal_proxy')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 100 | `_comparar_com_baseline` | 'delta_patrimonio_proxy_vs_baseline': round(_safe_float(sim.get('patrimonio_liquido_terminal_proxy')) - _safe_float(baseline.get('patrimonio_liquido_terminal_proxy')), 2), |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 105 | `_ticket_ok` | minimo = _safe_float(acao.get('aplicacao_minima_destino')) |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 106 | `_ticket_ok` | maximo = _safe_float(acao.get('aplicacao_maxima_destino')) |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 128 | `_cap_fontes_por_destino` | grupo = sorted(grupo, key=lambda a: _safe_float(a.get('ganho_terminal_economico_minimo_estimado')), reverse=True) |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | 146 | `_melhores_por_fonte_destino` | score = _safe_float(acao.get('ganho_terminal_economico_minimo_estimado')) |
| ... | ... | ... | mais 55 chamada(s) no CSV |

## Decisão técnica

- Fonte canônica recomendada nesta etapa: `indefinida nesta etapa`
- Risco de consolidação imediata: medio/alto para alteração funcional

Não consolidar automaticamente. As implementações divergem em casos de entrada relevantes, especialmente strings em formato brasileiro/moeda ou entradas inválidas. A próxima etapa deve definir contrato único de conversão numérica antes de migrar chamadas.

## Estratégia recomendada

1. Não substituir `_safe_float` agora se houver divergências comportamentais.
2. Formalizar primeiro o contrato desejado para conversão numérica:
   - `None`;
   - string vazia;
   - moeda brasileira;
   - decimal com vírgula;
   - separador de milhar;
   - porcentagem;
   - valores inválidos;
   - `NaN`.
3. Depois expandir `nucleo.utilitarios_neutros._safe_float` para cobrir o contrato completo.
4. Só então migrar chamadas locais para a fonte única.
5. Validar com:

```bash
python aplicacao/principal.py
```

## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_SAFE_FLOAT_V225.md
relatorios/atuais/codex_ready/auditoria_safe_float_definicoes_v225.csv
relatorios/atuais/codex_ready/auditoria_safe_float_chamadas_v225.csv
relatorios/atuais/codex_ready/auditoria_safe_float_comparacao_v225.csv
```

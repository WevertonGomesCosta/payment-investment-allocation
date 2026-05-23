# V17-F0-V.4Z2 — Auditoria estrutural pré-Etapa 5

- arquivos auditados: `75`
- módulos inventariados: `75`
- funções inventariadas: `839`

## Resumo

```json
{
  "funcoes_com_residuos": 414,
  "modulos_com_residuos": 69,
  "modulos_shadow_ou_experimentais": [
    "nucleo/auditoria_primeira_quebra_runner_futuro_shadow.py",
    "nucleo/auditoria_runner_futuro_shadow.py",
    "nucleo/benchmark_agrupado_individual_shadow.py",
    "nucleo/benchmark_runner_futuro_shadow.py",
    "nucleo/helpers_shadow_compartilhados.py",
    "nucleo/ledger_switching_canonico_shadow_v37q.py",
    "nucleo/pacote_ledger_temporal_switching_shadow_v37q.py",
    "nucleo/resolver_hibrido_5p_shadow.py",
    "nucleo/saida_canonica_ledger_shadow.py",
    "nucleo/saida_canonica_temporal_shadow_v4k.py",
    "nucleo/switching_canonico_ledger_shadow.py",
    "nucleo/switching_economico_shadow.py",
    "nucleo/switching_shadow_reconciliacao.py"
  ],
  "modulos_versionados": [
    "nucleo/alocador_pagamentos_terminal_v1.py",
    "nucleo/avaliador_cenarios_conjuntos_v1.py",
    "nucleo/comparador_hibrido_switching_v1.py",
    "nucleo/construir_saida_canonica_v17_c7.py",
    "nucleo/fluxo_pagamentos_terminal_v138.py",
    "nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py",
    "nucleo/ledger_switching_canonico_shadow_v37q.py",
    "nucleo/ledger_switching_estado_temporal_v17_f0_o2.py",
    "nucleo/ledger_temporal_switching_canonico_v37r.py",
    "nucleo/matriz_elegibilidade_fontes_s7b.py",
    "nucleo/microplanejamento_conjunto_bloco_critico_v2.py",
    "nucleo/motor_recomendacao_pagamentos_switching_v1.py",
    "nucleo/pacote_ledger_temporal_switching_shadow_v37q.py",
    "nucleo/planejador_switching_temporal_v1.py",
    "nucleo/planejamento_conjunto_local_bloco_critico_v1.py",
    "nucleo/ponte_renderizacao_switching_v17_c6.py",
    "nucleo/recomputacao_sequencial_central_v1.py",
    "nucleo/saida_canonica_controlada_v4l.py",
    "nucleo/saida_canonica_switching_v17_c7.py",
    "nucleo/saida_canonica_temporal_shadow_v4k.py",
    "nucleo/simulador_central_eventos_v1.py"
  ],
  "sentinelas_em_modulos": [
    "nucleo/caixa_recebidos_auditaveis.py",
    "nucleo/ledger_temporal_conjunto.py",
    "nucleo/microplanejamento_conjunto_bloco_critico_v2.py",
    "nucleo/pacote_saida_observavel_temporal.py",
    "nucleo/planejamento_conjunto_local_bloco_critico_v1.py",
    "nucleo/saida_canonica.py",
    "nucleo/saida_observavel.py"
  ]
}
```

## Runtime principal

```json
[
  {
    "arquivo": "aplicacao/principal.py",
    "chamadas_projeto_inferidas": [
      "aplicacao.console.principal.render_console",
      "nucleo.construir_saida_canonica_v17_c7.construir_saida_canonica_com_switching_v17_c7",
      "nucleo.contexto_baseline.carregar_contexto_baseline",
      "nucleo.gerar_planilha_operacional.main",
      "nucleo.integracao_matriz_elegibilidade_pagamentos_s7c.aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c",
      "nucleo.matriz_elegibilidade_fontes_s7b.construir_matriz_elegibilidade_fontes_s7b"
    ],
    "classes": [],
    "decisao_preliminar": "auditar_runtime_antes_etapa5",
    "etapa_inferida": "runtime_principal",
    "funcoes_internas": [],
    "funcoes_publicas": [
      "carregar_contexto_e_saida",
      "main"
    ],
    "importado_por": [],
    "imports_projeto": [
      "aplicacao.console.principal",
      "nucleo.construir_saida_canonica_v17_c7",
      "nucleo.contexto_baseline",
      "nucleo.gerar_planilha_operacional",
      "nucleo.identidade_baseline",
      "nucleo.integracao_matriz_elegibilidade_pagamentos_s7c",
      "nucleo.matriz_elegibilidade_fontes_s7b"
    ],
    "justificativa_decisao": "entrypoint principal ainda define a rota executavel",
    "metodos": [],
    "nome_versionado": false,
    "sentinelas": [],
    "tem_entrypoint": true,
    "tem_io": false,
    "termos_residuo": [
      "auditoria",
      "benchmark",
      "shadow"
    ],
    "tipo_modulo": "entrypoint_runtime"
  }
]
```

## Gate pré-Etapa 5

```json
{
  "este_auditor_nao_altera_runtime": true,
  "nao_iniciar_etapa5_se_houver_residuos_na_rota_runtime": true,
  "principal_py_deve_ser_executado_localmente": true
}
```

## Módulos com resíduos

- `aplicacao/principal.py` — decisão: `auditar_runtime_antes_etapa5`; resíduos: `['auditoria', 'benchmark', 'shadow']`
- `aplicacao/console/principal.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'benchmark', 'fallback', 'shadow']`
- `aplicacao/console/secoes_execucao.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback']`
- `nucleo/alocador_pagamentos_terminal_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `[]`
- `nucleo/aportes_futuros_planejados.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/auditoria_primeira_quebra_runner_futuro_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'benchmark', 'shadow']`
- `nucleo/auditoria_runner_futuro_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'benchmark', 'shadow']`
- `nucleo/auditoria_temporal_decisao_local.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/avaliador_cenarios_conjuntos_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `[]`
- `nucleo/benchmark_agrupado_individual_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'benchmark', 'legado', 'shadow']`
- `nucleo/benchmark_runner_futuro_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'benchmark', 'diagnostico', 'shadow']`
- `nucleo/cache_cdi_bcb.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback', 'legado']`
- `nucleo/caixa_recebidos_auditaveis.py` — decisão: `remover_sentinelas_ou_rebaixar_regressao`; resíduos: `['auditoria', 'benchmark', 'diagnostico', 'fallback', 'shadow', '8500']`
- `nucleo/calendario_financeiro.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback']`
- `nucleo/carregador_config.py` — decisão: `manter_ou_validar`; resíduos: `['legado']`
- `nucleo/carteira_canonica.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'benchmark']`
- `nucleo/comparador_hibrido_switching_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `[]`
- `nucleo/construir_saida_canonica_v17_c7.py` — decisão: `canonizar_ou_substituir`; resíduos: `[]`
- `nucleo/contexto_baseline.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'benchmark', 'legado', 'shadow']`
- `nucleo/dados_operacionais_canonicos.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'legacy']`
- `nucleo/entrada_resolvida.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/fiscal_lotes.py` — decisão: `manter_ou_validar`; resíduos: `['fallback']`
- `nucleo/fluxo_pagamentos_terminal_v138.py` — decisão: `arquivar_ou_renomear`; resíduos: `['auditoria', 'benchmark', 'shadow']`
- `nucleo/gerar_planilha_operacional.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'benchmark', 'diagnostico', 'shadow']`
- `nucleo/helpers_shadow_compartilhados.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['benchmark', 'shadow']`
- `nucleo/heuristica_conjunta_parcial_bloco_critico.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/identidade_baseline.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'benchmark', 'diagnostico', 'shadow']`
- `nucleo/integracao_matriz_elegibilidade_pagamentos_s7c.py` — decisão: `canonizar_ou_substituir`; resíduos: `['diagnostico']`
- `nucleo/inventario_lotes_expandido_pos_switching.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/ledger_switching_canonico_shadow_v37q.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/ledger_switching_estado_temporal_v17_f0_o2.py` — decisão: `canonizar_ou_substituir`; resíduos: `[]`
- `nucleo/ledger_temporal_conjunto.py` — decisão: `remover_sentinelas_ou_rebaixar_regressao`; resíduos: `['auditoria', 'diagnostico', 'fallback', 'legado', 'shadow', '8500']`
- `nucleo/ledger_temporal_switching_canonico_v37r.py` — decisão: `arquivar_ou_renomear`; resíduos: `['auditoria', 'fallback', 'legado', 'shadow']`
- `nucleo/leitor_planilha.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback', 'legado']`
- `nucleo/matriz_elegibilidade_fontes_s7b.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', 'diagnostico']`
- `nucleo/matriz_pacotes_diarios.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'shadow']`
- `nucleo/microplanejamento_conjunto_bloco_critico_v2.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', '8500']`
- `nucleo/motor_recomendacao_pagamentos_switching_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', 'diagnostico', 'fallback', 'shadow']`
- `nucleo/nucleo_financeiro_minimo.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback']`
- `nucleo/pacote_auditoria_temporal.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback', 'legado', 'shadow']`
- `nucleo/pacote_estado_temporal.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'shadow']`
- `nucleo/pacote_ledger_temporal.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'legacy', 'legado', 'shadow']`
- `nucleo/pacote_ledger_temporal_operacional.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback', 'legado', 'shadow']`
- `nucleo/pacote_ledger_temporal_switching_shadow_v37q.py` — decisão: `isolar_historico`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/pacote_orquestrado_pre_saida.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'diagnostico']`
- `nucleo/pacote_replay_passado.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'shadow']`
- `nucleo/pacote_saida_observavel_temporal.py` — decisão: `remover_sentinelas_ou_rebaixar_regressao`; resíduos: `['auditoria', 'fallback', 'shadow', '3120', 'Lote 3120 mai']`
- `nucleo/pacotes_temporais_agregados_saida.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/planejador_switching_temporal_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `['benchmark']`
- `nucleo/planejamento_conjunto_local_bloco_critico_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', '8500']`
- `nucleo/ponte_renderizacao_switching_v17_c6.py` — decisão: `arquivar_ou_renomear`; resíduos: `[]`
- `nucleo/ranking_carteira_estabilizado.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/recomputacao_sequencial_central_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', 'diagnostico', 'fallback']`
- `nucleo/reescolha_dinamica_pos_quebra.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/replay_passado_controlado.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria', 'fallback']`
- `nucleo/resolver_hibrido_5p_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'benchmark', 'fallback', 'legado', 'shadow']`
- `nucleo/rotulagem_fechamento.py` — decisão: `manter_ou_validar`; resíduos: `['fallback']`
- `nucleo/saida_canonica.py` — decisão: `remover_sentinelas_ou_rebaixar_regressao`; resíduos: `['auditoria', 'diagnostico', 'fallback', 'shadow', '3120', '6630', '8500']`
- `nucleo/saida_canonica_controlada_v4l.py` — decisão: `arquivar_ou_renomear`; resíduos: `['auditoria', 'shadow']`
- `nucleo/saida_canonica_ledger_shadow.py` — decisão: `isolar_historico`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/saida_canonica_switching_v17_c7.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria']`
- `nucleo/saida_canonica_temporal_shadow_v4k.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/saida_observavel.py` — decisão: `remover_sentinelas_ou_rebaixar_regressao`; resíduos: `['auditoria', 'diagnostico', 'fallback', '6630', '8500']`
- `nucleo/simulador_central_eventos_v1.py` — decisão: `canonizar_ou_substituir`; resíduos: `['auditoria', 'fallback']`
- `nucleo/switching_canonico_ledger_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/switching_economico_shadow.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/switching_shadow_reconciliacao.py` — decisão: `isolar_bloqueante_se_consumido`; resíduos: `['auditoria', 'legado', 'shadow']`
- `nucleo/triagem_motor.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
- `nucleo/validacao_pre_execucao.py` — decisão: `separar_diagnostico_do_contrato`; resíduos: `['auditoria']`
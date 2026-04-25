# MAPA DE SCRIPTS — V201

## 1. Objetivo

Este manifesto classifica os scripts do repositório após a limpeza segura V201. Ele não altera a execução do motor; apenas define autoridade operacional e risco de uso.

## 2. Regra de autoridade

- Scripts em `scripts/operacional/` são o caminho canônico para geração operacional.
- Scripts em `scripts/auditoria/` são o caminho canônico para auditorias formais.
- Scripts em `scripts/diagnostico/` são apoio técnico e diagnóstico sob demanda.
- Scripts em `scripts/historico_raiz/` são acervo histórico sem autoridade operacional.
- Wrappers na raiz de `scripts/` são preservados apenas para compatibilidade.
- Nenhum script histórico deve gravar em `saidas/oficial/`.

## 3. Contagem por status

| Status | Arquivos |
|---|---:|
| auditoria ativa | 1 |
| diagnóstico ativo | 2 |
| diagnóstico sob demanda | 78 |
| histórico sem execução corrente | 64 |
| operacional ativo | 1 |
| wrapper/compatibilidade | 5 |

Total de scripts Python classificados: **151**.

## 4. Duplicações por nome

Foram encontrados **65** nomes repetidos entre caminhos diferentes. Isso é esperado principalmente entre `scripts/diagnostico/` e `scripts/historico_raiz/`, mas deve ser tratado como risco de confusão operacional.

| Nome | Ocorrências |
|---|---:|
| `__init__.py` | 8 |
| `consolidar_grade_diaria_hibrida_v133.py` | 2 |
| `consolidar_grade_diaria_hibrida_v134.py` | 2 |
| `consolidar_grade_diaria_hibrida_v136.py` | 2 |
| `consolidar_grade_diaria_parametrizada_v130.py` | 2 |
| `consolidar_grade_diaria_switching_v126.py` | 2 |
| `consolidar_grade_diaria_switching_v127.py` | 2 |
| `consolidar_grade_diaria_switching_v128.py` | 2 |
| `gerar_auditoria_diaria_lote.py` | 2 |
| `gerar_planilha_operacional.py` | 2 |
| `inspecionar_alocador_pagamentos_terminal_v137.py` | 2 |
| `inspecionar_alocador_pagamentos_terminal_v141.py` | 2 |
| `inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py` | 2 |
| `inspecionar_auditoria_3k_mar_pos_pagamento_v147.py` | 3 |
| `inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py` | 2 |
| `inspecionar_auditoria_estrutural_redundancia.py` | 2 |
| `inspecionar_auditoria_runner_futuro_shadow.py` | 2 |
| `inspecionar_auditoria_temporal_decisao_local.py` | 2 |
| `inspecionar_base.py` | 2 |
| `inspecionar_benchmark_agrupado_individual_shadow.py` | 2 |
| `inspecionar_benchmark_runner_futuro_shadow.py` | 2 |
| `inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` | 2 |
| `inspecionar_chave_tau_v149.py` | 3 |
| `inspecionar_comparador_hibrido_switching_v132.py` | 2 |
| `inspecionar_comparativo_proxy_v2_v3.py` | 2 |
| `inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py` | 2 |
| `inspecionar_consolidacao_helpers_baixo_risco.py` | 2 |
| `inspecionar_contrato_f1.py` | 2 |
| `inspecionar_contrato_v117.py` | 2 |
| `inspecionar_correcao_flattening_v148.py` | 3 |
| `inspecionar_decisao_local_v1.py` | 2 |
| `inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py` | 2 |
| `inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py` | 2 |
| `inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py` | 2 |
| `inspecionar_fontes_elegiveis_pagamento.py` | 2 |
| `inspecionar_grade_diaria_hibrida_v133.py` | 2 |
| `inspecionar_grade_diaria_hibrida_v134.py` | 2 |
| `inspecionar_grade_diaria_hibrida_v136.py` | 2 |
| `inspecionar_grade_diaria_parametrizada_v130.py` | 2 |
| `inspecionar_grade_diaria_switching_v126.py` | 2 |
| `inspecionar_grade_diaria_switching_v127.py` | 2 |
| `inspecionar_heuristica_conjunta_parcial_bloco_critico.py` | 3 |
| `inspecionar_integracao_funcional_minima_v117.py` | 2 |
| `inspecionar_mapa_absorcao_legado.py` | 2 |
| `inspecionar_mapa_execucao_principal_script2.py` | 2 |
| `inspecionar_microplanejamento_conjunto_bloco_critico_v2.py` | 3 |
| `inspecionar_motor_diario_conjunto_experimental_v143.py` | 3 |
| `inspecionar_motor_diario_conjunto_experimental_v144.py` | 3 |
| `inspecionar_motor_diario_pos_vencimento_v146.py` | 3 |
| `inspecionar_motor_recomendacao_pagamentos_switching_v1.py` | 2 |
| `inspecionar_parametros_produtos_switching_v129.py` | 2 |
| `inspecionar_planejador_switching_temporal_horizonte_longo_v122.py` | 2 |
| `inspecionar_planejamento_conjunto_local_bloco_critico_v1.py` | 3 |
| `inspecionar_primeira_quebra_runner_futuro_shadow.py` | 2 |
| `inspecionar_ranking_carteira_estabilizado_v123.py` | 2 |
| `inspecionar_recebidos_auditaveis.py` | 2 |
| `inspecionar_recomputacao_sequencial_central_v1.py` | 2 |
| `inspecionar_reescolha_dinamica_pos_quebra.py` | 2 |
| `inspecionar_resolver_hibrido_5p_shadow.py` | 2 |
| `inspecionar_saldo_disponivel_geral.py` | 2 |
| `inspecionar_simulacao_central_controlada_horizonte_longo_v124.py` | 2 |
| `inspecionar_switching_economico_shadow.py` | 2 |
| `inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` | 2 |
| `run_v150_multi.py` | 3 |
| `verificar_release_baseline.py` | 2 |

## 5. Duplicações exatas de conteúdo

Grupos com conteúdo Python idêntico: **7**. A V201 não remove essas cópias; apenas registra o risco para uma futura limpeza com wrappers.

### Grupo 1
- `scripts/__init__.py`
- `scripts/auditoria/__init__.py`
- `scripts/diagnostico/__init__.py`
- `scripts/operacional/__init__.py`

### Grupo 2
- `scripts/diagnostico/consolidar_grade_diaria_hibrida_v136.py`
- `scripts/historico_raiz/consolidar_grade_diaria_hibrida_v136.py`

### Grupo 3
- `scripts/diagnostico/inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py`
- `scripts/historico_raiz/inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py`

### Grupo 4
- `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v136.py`
- `scripts/historico_raiz/inspecionar_grade_diaria_hibrida_v136.py`

### Grupo 5
- `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py`
- `scripts/historico_raiz/inspecionar_integracao_funcional_minima_v117.py`

### Grupo 6
- `scripts/diagnostico/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`
- `scripts/historico_raiz/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py`

### Grupo 7
- `scripts/diagnostico/temporal_decisao/__init__.py`
- `scripts/diagnostico/temporal_decisao/bloco_critico/__init__.py`
- `scripts/diagnostico/temporal_decisao/motor_diario/__init__.py`
- `scripts/diagnostico/temporal_decisao/valoracao_decisao/__init__.py`

## 6. Classificação completa

| Script | Status | Autoridade | Saídas detectadas | LOC |
|---|---|---|---|---:|
| `scripts/__init__.py` | wrapper/compatibilidade | compatibilidade; encaminhar para caminho canônico | - | 0 |
| `scripts/_compat.py` | wrapper/compatibilidade | compatibilidade; encaminhar para caminho canônico | - | 17 |
| `scripts/auditoria/__init__.py` | histórico sem execução corrente | não canônico | - | 0 |
| `scripts/auditoria/gerar_auditoria_diaria_lote.py` | auditoria ativa | canônico para auditoria formal | console, csv, xlsx | 264 |
| `scripts/diagnostico/__init__.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 0 |
| `scripts/diagnostico/_bootstrap.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 9 |
| `scripts/diagnostico/consolidar_grade_diaria_hibrida_v133.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 163 |
| `scripts/diagnostico/consolidar_grade_diaria_hibrida_v134.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 179 |
| `scripts/diagnostico/consolidar_grade_diaria_hibrida_v136.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 179 |
| `scripts/diagnostico/consolidar_grade_diaria_parametrizada_v130.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 148 |
| `scripts/diagnostico/consolidar_grade_diaria_switching_v126.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 41 |
| `scripts/diagnostico/consolidar_grade_diaria_switching_v127.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 41 |
| `scripts/diagnostico/consolidar_grade_diaria_switching_v128.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 79 |
| `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v137.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 169 |
| `scripts/diagnostico/inspecionar_alocador_pagamentos_terminal_v141.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 136 |
| `scripts/diagnostico/inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 98 |
| `scripts/diagnostico/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 44 |
| `scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 108 |
| `scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 74 |
| `scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 51 |
| `scripts/diagnostico/inspecionar_base.py` | diagnóstico ativo | canônico para diagnóstico/release | - | 15 |
| `scripts/diagnostico/inspecionar_benchmark_agrupado_individual_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 75 |
| `scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 72 |
| `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 88 |
| `scripts/diagnostico/inspecionar_chave_tau_v149.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_comparador_hibrido_switching_v132.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 172 |
| `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 93 |
| `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 94 |
| `scripts/diagnostico/inspecionar_consolidacao_helpers_baixo_risco.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 48 |
| `scripts/diagnostico/inspecionar_contrato_f1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, json | 38 |
| `scripts/diagnostico/inspecionar_contrato_v117.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 32 |
| `scripts/diagnostico/inspecionar_correcao_flattening_v148.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_decisao_local_v1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 50 |
| `scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 91 |
| `scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 167 |
| `scripts/diagnostico/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 102 |
| `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 67 |
| `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v133.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 281 |
| `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v134.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 290 |
| `scripts/diagnostico/inspecionar_grade_diaria_hibrida_v136.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 319 |
| `scripts/diagnostico/inspecionar_grade_diaria_parametrizada_v130.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 279 |
| `scripts/diagnostico/inspecionar_grade_diaria_switching_v126.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 342 |
| `scripts/diagnostico/inspecionar_grade_diaria_switching_v127.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 340 |
| `scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_integracao_funcional_minima_v117.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console | 122 |
| `scripts/diagnostico/inspecionar_mapa_absorcao_legado.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 38 |
| `scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 40 |
| `scripts/diagnostico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_motor_diario_conjunto_experimental_v143.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_motor_diario_conjunto_experimental_v144.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_motor_diario_pos_vencimento_v146.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_motor_recomendacao_pagamentos_switching_v1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 28 |
| `scripts/diagnostico/inspecionar_parametros_produtos_switching_v129.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 337 |
| `scripts/diagnostico/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console | 155 |
| `scripts/diagnostico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 65 |
| `scripts/diagnostico/inspecionar_ranking_carteira_estabilizado_v123.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, csv, json, xlsx | 64 |
| `scripts/diagnostico/inspecionar_recebidos_auditaveis.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 58 |
| `scripts/diagnostico/inspecionar_recomputacao_sequencial_central_v1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 53 |
| `scripts/diagnostico/inspecionar_reescolha_dinamica_pos_quebra.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 52 |
| `scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 85 |
| `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 63 |
| `scripts/diagnostico/inspecionar_simulacao_central_controlada_horizonte_longo_v124.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console | 118 |
| `scripts/diagnostico/inspecionar_switching_economico_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 75 |
| `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console, csv, xlsx | 92 |
| `scripts/diagnostico/inspecionar_validacao_diaria_operacional_v176.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 67 |
| `scripts/diagnostico/inspecionar_validacao_diaria_operacional_v177.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 28 |
| `scripts/diagnostico/run_v150_multi.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 8 |
| `scripts/diagnostico/temporal_decisao/__init__.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 2 |
| `scripts/diagnostico/temporal_decisao/bloco_critico/__init__.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 2 |
| `scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 60 |
| `scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 58 |
| `scripts/diagnostico/temporal_decisao/bloco_critico/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | console | 57 |
| `scripts/diagnostico/temporal_decisao/motor_diario/__init__.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 2 |
| `scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v143.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 27 |
| `scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_conjunto_experimental_v144.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 200 |
| `scripts/diagnostico/temporal_decisao/motor_diario/inspecionar_motor_diario_pos_vencimento_v146.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 230 |
| `scripts/diagnostico/temporal_decisao/motor_diario/run_v150_multi.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 108 |
| `scripts/diagnostico/temporal_decisao/valoracao_decisao/__init__.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | - | 2 |
| `scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 399 |
| `scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_chave_tau_v149.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 301 |
| `scripts/diagnostico/temporal_decisao/valoracao_decisao/inspecionar_correcao_flattening_v148.py` | diagnóstico sob demanda | apoio técnico, sem primazia operacional | arquivo, console, json | 303 |
| `scripts/diagnostico/verificar_release_baseline.py` | diagnóstico ativo | canônico para diagnóstico/release | console | 114 |
| `scripts/gerar_auditoria_diaria_lote.py` | wrapper/compatibilidade | compatibilidade; encaminhar para caminho canônico | - | 12 |
| `scripts/gerar_planilha_operacional.py` | wrapper/compatibilidade | compatibilidade; encaminhar para caminho canônico | - | 12 |
| `scripts/historico_raiz/consolidar_grade_diaria_hibrida_v133.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/consolidar_grade_diaria_hibrida_v134.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/consolidar_grade_diaria_hibrida_v136.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console, json | 179 |
| `scripts/historico_raiz/consolidar_grade_diaria_parametrizada_v130.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/consolidar_grade_diaria_switching_v126.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/consolidar_grade_diaria_switching_v127.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/consolidar_grade_diaria_switching_v128.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v137.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_alocador_pagamentos_terminal_v141.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_ativacao_lotes_nao_aportados_futuros_v136.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console, json | 98 |
| `scripts/historico_raiz/inspecionar_auditoria_3k_mar_pos_pagamento_v147.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_auditoria_cirurgica_bloco_8500_picpay_v131.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_auditoria_estrutural_redundancia.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_auditoria_runner_futuro_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_auditoria_temporal_decisao_local.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 17 |
| `scripts/historico_raiz/inspecionar_base.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 12 |
| `scripts/historico_raiz/inspecionar_benchmark_agrupado_individual_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_benchmark_runner_futuro_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 14 |
| `scripts/historico_raiz/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_chave_tau_v149.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_comparador_hibrido_switching_v132.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_comparativo_proxy_v2_v3.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 13 |
| `scripts/historico_raiz/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_consolidacao_helpers_baixo_risco.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_contrato_f1.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_contrato_v117.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_correcao_flattening_v148.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_decisao_local_v1.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_fontes_elegiveis_pagamento.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_grade_diaria_hibrida_v133.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_grade_diaria_hibrida_v134.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_grade_diaria_hibrida_v136.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console, json | 319 |
| `scripts/historico_raiz/inspecionar_grade_diaria_parametrizada_v130.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_grade_diaria_switching_v126.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_grade_diaria_switching_v127.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_heuristica_conjunta_parcial_bloco_critico.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 17 |
| `scripts/historico_raiz/inspecionar_integracao_funcional_minima_v117.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console | 122 |
| `scripts/historico_raiz/inspecionar_mapa_absorcao_legado.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_mapa_execucao_principal_script2.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_microplanejamento_conjunto_bloco_critico_v2.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_motor_diario_conjunto_experimental_v143.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_motor_diario_conjunto_experimental_v144.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_motor_diario_pos_vencimento_v146.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_motor_recomendacao_pagamentos_switching_v1.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_parametros_produtos_switching_v129.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_planejador_switching_temporal_horizonte_longo_v122.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console | 155 |
| `scripts/historico_raiz/inspecionar_planejamento_conjunto_local_bloco_critico_v1.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 17 |
| `scripts/historico_raiz/inspecionar_primeira_quebra_runner_futuro_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_ranking_carteira_estabilizado_v123.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_recebidos_auditaveis.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_recomputacao_sequencial_central_v1.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 5 |
| `scripts/historico_raiz/inspecionar_reescolha_dinamica_pos_quebra.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 17 |
| `scripts/historico_raiz/inspecionar_resolver_hibrido_5p_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 15 |
| `scripts/historico_raiz/inspecionar_saldo_disponivel_geral.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_simulacao_central_controlada_horizonte_longo_v124.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/inspecionar_switching_economico_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 16 |
| `scripts/historico_raiz/run_v150_multi.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | - | 8 |
| `scripts/historico_raiz/validar_janela_diaria_operacional_v175.py` | histórico sem execução corrente | histórico; não deve escrever em saída oficial | arquivo, console, json | 33 |
| `scripts/operacional/__init__.py` | histórico sem execução corrente | não canônico | - | 0 |
| `scripts/operacional/gerar_planilha_operacional.py` | operacional ativo | canônico para geração operacional | console | 924 |
| `scripts/verificar_release_baseline.py` | wrapper/compatibilidade | compatibilidade; encaminhar para caminho canônico | - | 8 |

## 7. Implicação para a próxima etapa

A próxima etapa deve concentrar a camada observável em uma estrutura única. O manifesto mostra que a divergência mais relevante não é a existência de scripts históricos em si, mas a presença de múltiplos pontos capazes de formatar ou recomputar saídas.

# Auditoria de scripts residuais em `aplicacao/` e `nucleo/` — V225

## Identificação

- Data/hora local: 2026-04-30T13:53:06
- Entrada oficial analisada: `aplicacao/principal.py`
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código: não

## Resumo

| Métrica | Valor |
|---|---:|
| módulos Python auditados | 51 |
| módulos alcançados estaticamente pela rota oficial | 39 |
| módulos não alcançados estaticamente | 12 |
| módulos com risco alto para Codex | 0 |
| módulos com risco médio para Codex | 27 |
| funções duplicadas relevantes | 11 |
| imports internos mapeados | 175 |
| ocorrências de termos auditados | 23 |

## Interpretação

- `alto`: candidato prioritário a correção, neutralização ou remoção antes de novas implementações pelo Codex.
- `medio`: auditar antes de remover; pode ser módulo auxiliar, import dinâmico, CLI local ou frente futura.
- `baixo`: sem indício residual relevante nesta auditoria estática.

Arquivos não alcançados estaticamente pela rota oficial **não devem ser removidos automaticamente**. A checagem é estática e pode não capturar import dinâmico, uso via CLI ou uso futuro planejado.

## Candidatos de risco alto

nenhum item

## Candidatos de risco médio

| Arquivo | Risco | Classificação | Ação recomendada |
|---|---:|---|---|
| `aplicacao/__init__.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `aplicacao/console/__init__.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `aplicacao/console/secoes_execucao.py` | medio | renderizador_fora_do_console_oficial | auditar; migrar dados para saida_observavel ou remover renderizador legado |
| `aplicacao/console/secoes_triagem.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial; renderizador_fora_do_console_oficial | auditar; migrar dados para saida_observavel ou remover renderizador legado |
| `nucleo/__init__.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/alocador_pagamentos_terminal_v1.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/aportes_futuros_planejados.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/auditoria_primeira_quebra_runner_futuro_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/auditoria_runner_futuro_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/auditoria_temporal_decisao_local.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/avaliador_cenarios_conjuntos_v1.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/benchmark_agrupado_individual_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/benchmark_runner_futuro_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/comparador_hibrido_switching_v1.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/fiscal_lotes.py` | medio | nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/gerar_planilha_operacional.py` | medio | cli_standalone_em_aplicacao_ou_nucleo | auditar se deve ir para scripts/ ou ser removido |
| `nucleo/helpers_shadow_compartilhados.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/microplanejamento_conjunto_bloco_critico_v2.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/motor_recomendacao_pagamentos_switching_v1.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/planejador_switching_temporal_v1.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/planejamento_conjunto_local_bloco_critico_v1.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/recomputacao_sequencial_central_v1.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/resolver_hibrido_5p_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/simulador_central_eventos_v1.py` | medio | nome_sugere_residual_ou_historico; nao_alcancado_estaticamente_pela_rota_oficial | auditar manualmente antes de remover; pode ser modulo futuro ou import dinamico |
| `nucleo/switching_economico_shadow.py` | medio | nome_sugere_residual_ou_historico | manter |
| `nucleo/switching_shadow_reconciliacao.py` | medio | nome_sugere_residual_ou_historico | manter |

## Funções duplicadas relevantes

| Função | Risco | Arquivos | Ação recomendada |
|---|---:|---|---|
| `_clonar_lote` | medio | nucleo/benchmark_runner_futuro_shadow.py; nucleo/replay_passado_controlado.py | avaliar se duplicidade e aceitavel |
| `_criterio_desempate` | medio | nucleo/microplanejamento_conjunto_bloco_critico_v2.py; nucleo/planejamento_conjunto_local_bloco_critico_v1.py | avaliar se duplicidade e aceitavel |
| `_fmt_data` | medio | nucleo/rotulagem_fechamento.py; nucleo/saida_canonica.py | avaliar se duplicidade e aceitavel |
| `_ordenar_politicas` | medio | nucleo/microplanejamento_conjunto_bloco_critico_v2.py; nucleo/planejamento_conjunto_local_bloco_critico_v1.py | avaliar se duplicidade e aceitavel |
| `_patrimonio_terminal_proxy` | medio | nucleo/recomputacao_sequencial_central_v1.py; nucleo/simulador_central_eventos_v1.py | avaliar se duplicidade e aceitavel |
| `_projetar_valor_terminal` | medio | nucleo/planejador_switching_temporal_v1.py; nucleo/simulador_central_eventos_v1.py | avaliar se duplicidade e aceitavel |
| `_safe_float` | medio | nucleo/aportes_futuros_planejados.py; nucleo/utilitarios_neutros.py | avaliar se duplicidade e aceitavel |
| `_safe_round` | medio | nucleo/microplanejamento_conjunto_bloco_critico_v2.py; nucleo/planejamento_conjunto_local_bloco_critico_v1.py | avaliar se duplicidade e aceitavel |
| `_slug_fonte` | medio | nucleo/caixa_recebidos_auditaveis.py; nucleo/utilitarios_neutros.py | avaliar se duplicidade e aceitavel |
| `obter_config` | medio | nucleo/carregador_config.py; nucleo/config_utils.py | avaliar se duplicidade e aceitavel |
| `para_dict` | medio | nucleo/alocador_pagamentos_terminal_v1.py; nucleo/caixa_recebidos_auditaveis.py; nucleo/fluxo_pagamentos_terminal_v138.py; nucleo/planejador_switching_temporal_v1.py | avaliar se duplicidade e aceitavel |

## Referências residuais a legados principais

| Termo | Arquivo | Linha | Conteúdo |
|---|---|---:|---|
| `render_secao_` | `aplicacao/console/principal.py` | 19 | from aplicacao.console.secoes_execucao import render_secao_execucao |
| `render_secao_` | `aplicacao/console/principal.py` | 55 | def _render_secao_ranking_oficial(contexto_baseline, saida_canonica=None) -> None: |
| `render_secao_` | `aplicacao/console/principal.py` | 79 | def _render_secao_switchings_oficiais(contexto_baseline, saida_canonica=None) -> None: |
| `render_secao_` | `aplicacao/console/principal.py` | 190 | render_secao_execucao( |
| `render_secao_` | `aplicacao/console/principal.py` | 205 | _render_secao_ranking_oficial(contexto_baseline, saida_canonica) |
| `render_secao_` | `aplicacao/console/principal.py` | 206 | _render_secao_switchings_oficiais(contexto_baseline, saida_canonica) |
| `render_secao_` | `aplicacao/console/secoes_execucao.py` | 6 | def render_secao_execucao(*, versao, pacote_config, pacote_planilha, contexto, severidade_dependencias, auditoria_cache_cdi, data_ultimo_fator_cdi, resumo_por_aba, abas_primarias_reais, abas_auxiliares): |
| `render_secao_` | `aplicacao/console/secoes_triagem.py` | 6 | def render_secao_triagem(*, auditoria_triagem, contexto_triagem, severidade_triagem): |

## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_RESIDUAIS_APLICACAO_NUCLEO_V225.md
relatorios/atuais/codex_ready/auditoria_residuais_modulos_v225.csv
relatorios/atuais/codex_ready/auditoria_residuais_funcoes_duplicadas_v225.csv
relatorios/atuais/codex_ready/auditoria_residuais_imports_v225.csv
relatorios/atuais/codex_ready/auditoria_residuais_buscas_v225.csv
```

## Próxima ação recomendada

1. Revisar primeiro os itens `alto`.
2. Para cada item `medio`, decidir se:
   - deve permanecer como módulo funcional;
   - deve migrar para `scripts/`;
   - deve ser removido;
   - deve ser documentado como módulo futuro.
3. Não remover módulos de `nucleo/` apenas por não aparecerem no grafo estático.
4. Após qualquer remoção, validar:

```bash
python aplicacao/principal.py
python aplicacao/principal.py
```

## Complemento — remocao de secoes_triagem.py

- Data/hora local: 2026-04-30T14:03:38
- Arquivo: `aplicacao/console/secoes_triagem.py`
- Status: `removido`
- Relatorio especifico: `relatorios/atuais/codex_ready/REMOCAO_SECOES_TRIAGEM_PRE_CODEX_V225.md`
- Validacao requerida:
  - `python aplicacao/principal.py`
  - `python aplicacao/principal.py`

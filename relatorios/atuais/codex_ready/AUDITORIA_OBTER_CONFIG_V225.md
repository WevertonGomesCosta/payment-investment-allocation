# Auditoria da duplicidade de `obter_config` — V225

## Identificação

- Data/hora local: 2026-04-30T14:19:50
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código funcional: não

## Objetivo

Auditar a duplicidade entre:

```text
nucleo.carregador_config.obter_config
nucleo.config_utils.obter_config
```

sem alterar motor econômico, replay, pagamentos, switching, ranking, cache nem `dados/config_atualizado.json`.

## Definições encontradas

| Arquivo | Linha | Assinatura | Hash AST | Resumo |
|---|---:|---|---|---|
| `nucleo/carregador_config.py` | 136 | `(config, *caminho, padrao=...)` | `bc4e2b49527c5fda` | def obter_config(config: dict[str, Any], *caminho: str, padrao: Any = None) -> Any: return obter_config_compartilhado(config, *caminho, padrao=padrao) |
| `nucleo/config_utils.py` | 6 | `(config, *caminho, padrao=...)` | `3d8fbb97174b4d28` | def obter_config(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any: atual: Any = config for chave in caminho: if not isinstance(atual, Mapping) or chave not in atual: return padrao atual = atual[chave] return atual |

## Importações e aliases relacionados

| Arquivo | Linha | Tipo | Módulo | Nome | Alias | Origem classificada |
|---|---:|---|---|---|---|---|
| `nucleo/benchmark_agrupado_individual_shadow.py` | 34 | from | `nucleo.config_utils` | `obter_config` | `` | config_utils |
| `nucleo/cache_cdi_bcb.py` | 21 | from | `nucleo.config_utils` | `obter_config` | `_cfg_get` | config_utils |
| `nucleo/calendario_financeiro.py` | 25 | from | `nucleo.config_utils` | `obter_config` | `_cfg_get` | config_utils |
| `nucleo/carregador_config.py` | 17 | from | `nucleo.config_utils` | `obter_config` | `obter_config_compartilhado` | config_utils |
| `nucleo/contexto_baseline.py` | 10 | from | `nucleo.carregador_config` | `PacoteConfig` | `` | indeterminado |
| `nucleo/contexto_baseline.py` | 10 | from | `nucleo.carregador_config` | `carregar_config` | `` | indeterminado |
| `nucleo/contexto_baseline.py` | 32 | from | `nucleo.config_utils` | `obter_config` | `` | config_utils |
| `nucleo/leitor_planilha.py` | 22 | from | `nucleo.config_utils` | `obter_config` | `_cfg_get` | config_utils |
| `nucleo/nucleo_financeiro_minimo.py` | 27 | from | `nucleo.config_utils` | `obter_config` | `_cfg_get` | config_utils |
| `nucleo/resolver_hibrido_5p_shadow.py` | 32 | from | `nucleo.config_utils` | `obter_config` | `` | config_utils |
| `nucleo/switching_economico_shadow.py` | 32 | from | `nucleo.config_utils` | `obter_config` | `` | config_utils |
| `nucleo/triagem_motor.py` | 23 | from | `nucleo.config_utils` | `obter_config` | `` | config_utils |

## Chamadas AST relacionadas

Resumo por origem classificada:

```text
- config_utils: 25
- local_ou_indeterminado: 1
```

| Arquivo | Linha | Escopo | Nome | Origem | Conteúdo |
|---|---:|---|---|---|---|
| `nucleo/benchmark_agrupado_individual_shadow.py` | 328 | `carregar_benchmark_agrupado_individual_shadow` | `obter_config` | config_utils | limiar_rel = float(obter_config(config, 'benchmark_shadow_script2', 'limiar_diferenca_relativa', padrao=0.05) or 0.05) |
| `nucleo/carregador_config.py` | 137 | `obter_config` | `obter_config_compartilhado` | config_utils | return obter_config_compartilhado(config, *caminho, padrao=padrao) |
| `nucleo/carregador_config.py` | 156 | `obter_primeiro_config_disponivel` | `obter_config` | local_ou_indeterminado | valor = obter_config(config, *caminho, padrao=None) |
| `nucleo/contexto_baseline.py` | 77 | `obter_limiar_residuo_resolvido` | `obter_config` | config_utils | auditoria_cfg = obter_config(config, 'auditoria', padrao={}) or {} |
| `nucleo/contexto_baseline.py` | 78 | `obter_limiar_residuo_resolvido` | `obter_config` | config_utils | replay_cfg = obter_config(config, 'replay', padrao={}) or {} |
| `nucleo/resolver_hibrido_5p_shadow.py` | 90 | `_params_hibrido_shadow` | `obter_config` | config_utils | cfg = obter_config(config, 'hibrido_shadow', padrao={}) or {} |
| `nucleo/resolver_hibrido_5p_shadow.py` | 266 | `carregar_resolver_hibrido_5p_shadow` | `obter_config` | config_utils | horizonte_dias = int(obter_config(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180) |
| `nucleo/resolver_hibrido_5p_shadow.py` | 267 | `carregar_resolver_hibrido_5p_shadow` | `obter_config` | config_utils | valor_minimo_resgate_bruto = float(obter_config(config, 'pagamento', 'valor_minimo_resgate_bruto', padrao=0.01) or 0.01) |
| `nucleo/switching_economico_shadow.py` | 204 | `carregar_switching_economico_shadow` | `obter_config` | config_utils | horizonte_dias = int(obter_config(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180) |
| `nucleo/switching_economico_shadow.py` | 205 | `carregar_switching_economico_shadow` | `obter_config` | config_utils | ganho_minimo = float(obter_config(config, 'switching_shadow', 'ganho_minimo_absoluto', padrao=5.0) or 5.0) |
| `nucleo/triagem_motor.py` | 54 | `_proxy_retorno_anual` | `obter_config` | config_utils | horizonte = int(obter_config(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180) |
| `nucleo/triagem_motor.py` | 55 | `_proxy_retorno_anual` | `obter_config` | config_utils | cdi = float(obter_config(config, 'premissas_mercado', 'cdi_anual_modelo', padrao=0.149) or 0.149) |
| `nucleo/triagem_motor.py` | 56 | `_proxy_retorno_anual` | `obter_config` | config_utils | selic = float(obter_config(config, 'premissas_mercado', 'selic_anual_modelo', padrao=cdi) or cdi) |
| `nucleo/triagem_motor.py` | 57 | `_proxy_retorno_anual` | `obter_config` | config_utils | ipca = float(obter_config(config, 'premissas_mercado', 'ipca_anual_modelo', padrao=0.045) or 0.045) |
| `nucleo/triagem_motor.py` | 58 | `_proxy_retorno_anual` | `obter_config` | config_utils | cap_var = float(obter_config(config, 'triagem_motor', 'cap_anual_variavel', padrao=1.0) or 1.0) |
| `nucleo/triagem_motor.py` | 59 | `_proxy_retorno_anual` | `obter_config` | config_utils | cap_mult = float(obter_config(config, 'triagem_motor', 'cap_anual_cdi_multiplicador', padrao=1.5) or 1.5) |
| `nucleo/triagem_motor.py` | 189 | `_construir_contexto_triagem` | `obter_config` | config_utils | 'horizonte_principal_dias': int(obter_config(config, 'simulacao', 'horizonte_alocacao_dias', padrao=180) or 180), |
| `nucleo/triagem_motor.py` | 190 | `_construir_contexto_triagem` | `obter_config` | config_utils | 'horizonte_minimo_dias': int(obter_config(config, 'simulacao', 'horizonte_minimo_dias', padrao=30) or 30), |
| `nucleo/triagem_motor.py` | 240 | `carregar_triagem_motor` | `obter_config` | config_utils | w_ret = float(obter_config(config, 'triagem_motor', 'peso_retorno', padrao=0.35) or 0.35) |
| `nucleo/triagem_motor.py` | 241 | `carregar_triagem_motor` | `obter_config` | config_utils | w_liq = float(obter_config(config, 'triagem_motor', 'peso_liquidez', padrao=0.30) or 0.30) |
| `nucleo/triagem_motor.py` | 242 | `carregar_triagem_motor` | `obter_config` | config_utils | w_via = float(obter_config(config, 'triagem_motor', 'peso_viabilidade', padrao=0.20) or 0.20) |
| `nucleo/triagem_motor.py` | 243 | `carregar_triagem_motor` | `obter_config` | config_utils | w_ris = float(obter_config(config, 'triagem_motor', 'peso_risco', padrao=0.15) or 0.15) |
| `nucleo/triagem_motor.py` | 263 | `carregar_triagem_motor` | `obter_config` | config_utils | top_k_global = int(obter_config(config, 'triagem_motor', 'top_k_global', padrao=48) or 48) |
| `nucleo/triagem_motor.py` | 264 | `carregar_triagem_motor` | `obter_config` | config_utils | top_k_familia = int(obter_config(config, 'triagem_motor', 'top_k_por_familia', padrao=8) or 8) |
| `nucleo/triagem_motor.py` | 265 | `carregar_triagem_motor` | `obter_config` | config_utils | score_minimo = float(obter_config(config, 'triagem_motor', 'score_minimo_selecao', padrao=20.0) or 20.0) |
| `nucleo/triagem_motor.py` | 284 | `carregar_triagem_motor` | `obter_config` | config_utils | 'modo_calibracao': str(obter_config(config, 'triagem_motor', 'modo_calibracao', padrao='conservadora_transitoria') or 'conservadora_transitoria'), |

## Comparação semântica

- Relação inferida: carregador_config.obter_config e um wrapper/reexport que delega para config_utils.obter_config importado como obter_config_compartilhado
- `carregador_config` delega para `config_utils`: SIM
- Fonte canônica recomendada: `nucleo.config_utils.obter_config`

## Estratégia segura de consolidação futura

manter nucleo.config_utils.obter_config como primitiva canonica; em consolidacao futura, manter nucleo.carregador_config.obter_config como reexport temporario para compatibilidade; migrar imports gradualmente para nucleo.config_utils.obter_config

## Decisão recomendada

1. Não remover `nucleo.carregador_config.obter_config` imediatamente se houver chamadas/imports existentes.
2. Tratar `nucleo.config_utils.obter_config` como primitiva canônica se a delegação estiver confirmada.
3. Em microetapa futura, transformar `nucleo.carregador_config.obter_config` em reexport explícito/documentado ou migrar seus imports para `nucleo.config_utils.obter_config`.
4. Validar sempre com:

```bash
python aplicacao/principal.py
```

## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_OBTER_CONFIG_V225.md
relatorios/atuais/codex_ready/auditoria_obter_config_definicoes_v225.csv
relatorios/atuais/codex_ready/auditoria_obter_config_imports_v225.csv
relatorios/atuais/codex_ready/auditoria_obter_config_chamadas_v225.csv
relatorios/atuais/codex_ready/auditoria_obter_config_referencias_textuais_v225.csv
```

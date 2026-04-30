# Auditoria de duplicidades econômicas — V225

## Identificação

- Data/hora local: 2026-04-30T14:36:39
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código funcional: não

## Funções auditadas

```text
_projetar_valor_terminal
_patrimonio_terminal_proxy
```

## Resumo decisório

| Função | Definições | Status semântico | Risco | Fonte única recomendada | Decisão |
|---|---:|---|---:|---|---|
| `_projetar_valor_terminal` | 2 | duplicidade_semantica_distinta_ou_nao_comprovada | alto | não definida | manter separadas nesta etapa; funções têm assinaturas/contextos distintos e podem aplicar convenções econômicas diferentes entre planejamento de switching e simulação central |
| `_patrimonio_terminal_proxy` | 2 | duplicidade_semantica_distinta_ou_nao_comprovada | alto | não definida | manter separadas nesta etapa; funções operam sobre estruturas de entrada diferentes e provavelmente representam proxies distintos de patrimônio terminal |

## Interpretação técnica

### `_projetar_valor_terminal`

A duplicidade deve ser tratada como potencialmente semântica. Uma implementação pertence ao planejamento de switching temporal e outra à simulação central de eventos. Mesmo que as fórmulas pareçam próximas, as assinaturas e convenções de entrada podem refletir contextos diferentes.

Decisão recomendada: **manter separadas nesta etapa**. Abrir consolidação somente se uma microetapa econômica futura definir um contrato único de projeção terminal.

### `_patrimonio_terminal_proxy`

A duplicidade deve ser tratada como semanticamente distinta até prova em contrário. Uma versão trabalha com candidatos ajustados/movimento simulado/mapa de lotes/tabelas fiscais; outra trabalha com estado/métrica/ganho de switching. São estruturas de entrada diferentes e provavelmente proxies em níveis distintos do motor.

Decisão recomendada: **manter separadas nesta etapa**. Não criar fonte única agora.

## Detalhamento por função

### `_projetar_valor_terminal`

| Arquivo | Linha | Assinatura | Hash AST | Chaves `.get()` | Chamadas internas | Resumo |
|---|---:|---|---|---|---|---|
| `nucleo/planejador_switching_temporal_v1.py` | 105 | `(valor_base, retorno_anual_pct, dias)` | `c3d9a1bdfc4829c6` |  | float; int; max; round | def _projetar_valor_terminal(valor_base: float, retorno_anual_pct: float, dias: int) -> float: valor = max(float(valor_base or 0.0), 0.0) retorno = max(float(retorno_anual_pct or 0.0), 0.0) dias = max(int(dias or 0), 0) if valor <= 0.0 or dias <= 0: return round(valor, 2) fator = (1.0 + retorno / 100.0) ** (dias / 3... |
| `nucleo/simulador_central_eventos_v1.py` | 148 | `(valor_base, retorno_anual, dias)` | `36e4ddf4c8f038fe` |  | float; int; max; round | def _projetar_valor_terminal(valor_base: float, retorno_anual: float, dias: int) -> float: valor_base = float(valor_base or 0.0) retorno_anual = max(float(retorno_anual or 0.0), 0.0) dias = max(int(dias or 0), 0) if valor_base <= 0.0 or dias <= 0: return round(valor_base, 2) fator = (1.0 + retorno_anual / 100.0) ** ... |

Chamadas AST detectadas: 4

| Arquivo | Linha | Escopo | Conteúdo |
|---|---:|---|---|
| `nucleo/planejador_switching_temporal_v1.py` | 208 | `planejar_switching_temporal_v1` | patrimonio_terminal_origem = _projetar_valor_terminal(valor_liquido, retorno_anual_origem, dias_restantes) |
| `nucleo/planejador_switching_temporal_v1.py` | 247 | `planejar_switching_temporal_v1` | patrimonio_terminal_destino = _projetar_valor_terminal(valor_migrado, retorno_anual_destino, dias_restantes) |
| `nucleo/planejador_switching_temporal_v1.py` | 358 | `planejar_switching_temporal_v1` | patrimonio_terminal_destino = _projetar_valor_terminal(valor_disponivel, retorno_anual_destino, dias_restantes) |
| `nucleo/simulador_central_eventos_v1.py` | 175 | `_valor_terminal_estimado_lote` | return _projetar_valor_terminal(valor_liquido, retorno, dias) |

### `_patrimonio_terminal_proxy`

| Arquivo | Linha | Assinatura | Hash AST | Chaves `.get()` | Chamadas internas | Resumo |
|---|---:|---|---|---|---|---|
| `nucleo/recomputacao_sequencial_central_v1.py` | 313 | `(candidatos_ajustados, *, candidato_escolhido, movimento_simulado, data_referencia, mapa_lotes, tabela_iof, faixas_ir)` | `8aa1ff9875e53c6f` | consumo_generico_pos; fonte_escolhida_id; lote_id; mapa_lotes_pos; saldo_antes_dinamico; saldo_remanescente_central; tipo_fonte_escolhida; valor_disponivel | add; float; get; max; round; set; str; strip; valor_liquido_hoje | def _patrimonio_terminal_proxy( candidatos_ajustados: list[dict[str, Any]], *, candidato_escolhido: dict[str, Any], movimento_simulado: dict[str, Any], data_referencia: date, mapa_lotes: dict[str, Any], tabela_iof: list[float], faixas_ir: list[dict[str, Any]], ) -> float: total = 0.0 vistos: set[str] = set() lote_si... |
| `nucleo/simulador_central_eventos_v1.py` | 951 | `(estado, metrica, ganho_switching)` | `59dab54edb6e9f1c` | data_evento_corrente; data_fim_recorte; data_referencia; lotes_aportados; perda_patrimonio_liquido_terminal; recebidos_nao_aportados_disponiveis; saldo_disponivel_geral; valor; valor_disponivel | _coerce_date; _valor_terminal_estimado_lote; float; get; round; sum | def _patrimonio_terminal_proxy(estado: dict[str, Any], metrica: dict[str, Any], ganho_switching: float) -> float: saldo = float(estado.get('saldo_disponivel_geral') or 0.0) recebidos = sum(float(x.get('valor_disponivel') or x.get('valor') or 0.0) for x in estado.get('recebidos_nao_aportados_disponiveis', [])) data_f... |

Chamadas AST detectadas: 2

| Arquivo | Linha | Escopo | Conteúdo |
|---|---:|---|---|
| `nucleo/recomputacao_sequencial_central_v1.py` | 400 | `_comparador_central` | patrimonio = _patrimonio_terminal_proxy( |
| `nucleo/simulador_central_eventos_v1.py` | 1056 | `simular_cenario_eventos_v1` | patrimonio_proxy = _patrimonio_terminal_proxy(estado, metrica, ganho_switching_total) |

## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_DUPLICIDADES_ECONOMICAS_V225.md
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_definicoes_v225.csv
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_chamadas_v225.csv
relatorios/atuais/codex_ready/auditoria_duplicidades_economicas_comparacao_v225.csv
```

## Decisão final

As duplicidades econômicas **não devem ser removidas como limpeza técnica**.

Elas devem permanecer separadas até que uma frente econômica futura defina:

1. contrato matemático único de projeção terminal;
2. entradas e saídas canônicas;
3. convenções de retorno, horizonte, impostos, liquidez e switching;
4. testes de equivalência econômica;
5. validação com `python aplicacao/principal.py`.

## Validação operacional recomendada

```bash
python aplicacao/principal.py
```

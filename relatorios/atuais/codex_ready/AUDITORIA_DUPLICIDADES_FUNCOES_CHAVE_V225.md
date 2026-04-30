# Auditoria de duplicidades de funções-chave — V225

## Identificação

- Data/hora local: 2026-04-30T14:14:33
- Diretórios auditados:
  - `aplicacao/`
  - `nucleo/`
- Alteração de código: não

## Funções auditadas

```text
obter_config
_safe_float
_slug_fonte
_projetar_valor_terminal
_patrimonio_terminal_proxy
para_dict
```

## Resumo executivo

| Função | Definições | Chamadas | Equivalência | Risco | Recomendação |
|---|---:|---:|---|---:|---|
| `obter_config` | 2 | 25 | divergentes_ou_unica | alto | prioridade alta: definir uma fonte oficial unica para config; auditar chamadas de nucleo/carregador_config.py e nucleo/config_utils.py antes de remover |
| `_safe_float` | 2 | 135 | divergentes_ou_unica | medio | candidato a consolidacao futura em nucleo/utilitarios_neutros.py; migrar chamadas gradualmente e validar principal |
| `_slug_fonte` | 2 | 4 | identicas_ast | medio | candidato a consolidacao futura em nucleo/utilitarios_neutros.py; migrar chamadas gradualmente e validar principal |
| `_projetar_valor_terminal` | 2 | 4 | divergentes_ou_unica | alto | nao remover agora; duplicidade economica sensivel. auditar formulas, parametros e chamadas antes de consolidar |
| `_patrimonio_terminal_proxy` | 2 | 2 | divergentes_ou_unica | alto | nao remover agora; duplicidade economica sensivel. auditar formulas, parametros e chamadas antes de consolidar |
| `para_dict` | 5 | 6 | divergentes_ou_unica | baixo | provavelmente metodos de classes/dataclasses diferentes; nao consolidar automaticamente |

## Interpretação

- `identicas_ast`: as implementações têm corpo estruturalmente equivalente após normalização AST aproximada.
- `divergentes_ou_unica`: há mais de uma definição, mas os corpos divergem ou a equivalência não foi comprovada.
- `sem_duplicidade`: apenas uma definição foi encontrada.

Risco `alto` não significa remover imediatamente. Neste projeto, funções ligadas a config ou valoração econômica devem ser consolidadas somente com microetapa própria e validação.

## Detalhamento por função

### `obter_config`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/carregador_config.py` | `obter_config` | 136 | `(config, *caminho, padrao=...)` | `bc4e2b49527c5fda` | def obter_config(config: dict[str, Any], *caminho: str, padrao: Any = None) -> Any: return obter_config_compartilhado(config, *caminho, padrao=padrao) |
| `nucleo/config_utils.py` | `obter_config` | 6 | `(config, *caminho, padrao=...)` | `3d8fbb97174b4d28` | def obter_config(config: Mapping[str, Any], *caminho: str, padrao: Any = None) -> Any: atual: Any = config for chave in caminho: if not isinstance(atual, Mapping) or chave not in atual: return padrao atual = atual[cha... |

- chamadas AST detectadas: 25
- referências textuais detectadas: 41

### `_safe_float`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/aportes_futuros_planejados.py` | `_safe_float` | 20 | `(valor, padrao=...)` | `8204bbd7cf1a35fe` | def _safe_float(valor: Any, padrao: float = 0.0) -> float: if valor is None: return padrao try: if hasattr(valor, "isna") and valor.isna(): return padrao except Exception: pass if isinstance(valor, str): bruto = valor... |
| `nucleo/utilitarios_neutros.py` | `_safe_float` | 159 | `(valor, default=...)` | `baa356995668eef4` | def _safe_float(valor: Any, default: float = 0.0) -> float: try: if valor in (None, ''): return float(default) return float(valor) except Exception: return float(default) |

- chamadas AST detectadas: 135
- referências textuais detectadas: 128

### `_slug_fonte`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/caixa_recebidos_auditaveis.py` | `_slug_fonte` | 222 | `(chave)` | `581a3466dd9f0c90` | def _slug_fonte(chave: str) -> str: texto = normalizar_texto(chave).replace(' ', '_') return texto or 'fonte' |
| `nucleo/utilitarios_neutros.py` | `_slug_fonte` | 247 | `(chave)` | `581a3466dd9f0c90` | def _slug_fonte(chave: Any) -> str: texto = normalizar_texto(chave).replace(' ', '_') return texto or 'fonte' |

- chamadas AST detectadas: 4
- referências textuais detectadas: 5

### `_projetar_valor_terminal`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/planejador_switching_temporal_v1.py` | `_projetar_valor_terminal` | 105 | `(valor_base, retorno_anual_pct, dias)` | `c3d9a1bdfc4829c6` | def _projetar_valor_terminal(valor_base: float, retorno_anual_pct: float, dias: int) -> float: valor = max(float(valor_base or 0.0), 0.0) retorno = max(float(retorno_anual_pct or 0.0), 0.0) dias = max(int(dias or 0), ... |
| `nucleo/simulador_central_eventos_v1.py` | `_projetar_valor_terminal` | 148 | `(valor_base, retorno_anual, dias)` | `36e4ddf4c8f038fe` | def _projetar_valor_terminal(valor_base: float, retorno_anual: float, dias: int) -> float: valor_base = float(valor_base or 0.0) retorno_anual = max(float(retorno_anual or 0.0), 0.0) dias = max(int(dias or 0), 0) if v... |

- chamadas AST detectadas: 4
- referências textuais detectadas: 6

### `_patrimonio_terminal_proxy`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/recomputacao_sequencial_central_v1.py` | `_patrimonio_terminal_proxy` | 313 | `(candidatos_ajustados, *, candidato_escolhido, movimento_simulado, data_referencia, mapa_lotes, tabela_iof, faixas_ir)` | `8aa1ff9875e53c6f` | def _patrimonio_terminal_proxy( candidatos_ajustados: list[dict[str, Any]], *, candidato_escolhido: dict[str, Any], movimento_simulado: dict[str, Any], data_referencia: date, mapa_lotes: dict[str, Any], tabela_iof: li... |
| `nucleo/simulador_central_eventos_v1.py` | `_patrimonio_terminal_proxy` | 951 | `(estado, metrica, ganho_switching)` | `59dab54edb6e9f1c` | def _patrimonio_terminal_proxy(estado: dict[str, Any], metrica: dict[str, Any], ganho_switching: float) -> float: saldo = float(estado.get('saldo_disponivel_geral') or 0.0) recebidos = sum(float(x.get('valor_disponive... |

- chamadas AST detectadas: 2
- referências textuais detectadas: 8

### `para_dict`
| Arquivo | Qualname | Linha | Assinatura | Hash AST | Resumo |
|---|---|---:|---|---|---|
| `nucleo/alocador_pagamentos_terminal_v1.py` | `FontePagamentoCandidata.para_dict` | 47 | `(self)` | `4d8ad6a8174690bb` | def para_dict(self) -> dict[str, Any]: return asdict(self) |
| `nucleo/caixa_recebidos_auditaveis.py` | `EstruturaContrato.para_dict` | 30 | `(self)` | `8e364303da039080` | def para_dict(self) -> dict[str, Any]: return { 'nome': self.nome, 'descricao': self.descricao, 'campos': [asdict(campo) for campo in self.campos], } |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | `ResultadoPagamentoRecorteV138.para_dict` | 50 | `(self)` | `4d8ad6a8174690bb` | def para_dict(self) -> dict[str, Any]: return asdict(self) |
| `nucleo/fluxo_pagamentos_terminal_v138.py` | `ResumoFluxoPagamentosRecorteV138.para_dict` | 66 | `(self)` | `4d8ad6a8174690bb` | def para_dict(self) -> dict[str, Any]: return asdict(self) |
| `nucleo/planejador_switching_temporal_v1.py` | `AcaoSwitchingTemporalCandidata.para_dict` | 49 | `(self)` | `4d8ad6a8174690bb` | def para_dict(self) -> dict[str, Any]: return asdict(self) |

- chamadas AST detectadas: 6
- referências textuais detectadas: 11


## Arquivos gerados

```text
relatorios/atuais/codex_ready/AUDITORIA_DUPLICIDADES_FUNCOES_CHAVE_V225.md
relatorios/atuais/codex_ready/auditoria_funcoes_chave_definicoes_v225.csv
relatorios/atuais/codex_ready/auditoria_funcoes_chave_chamadas_v225.csv
relatorios/atuais/codex_ready/auditoria_funcoes_chave_resumo_v225.csv
```

## Próxima decisão recomendada

1. Começar por `obter_config`, porque afeta contrato central de configuração.
2. Depois auditar `_safe_float` e `_slug_fonte`, que são utilitários simples.
3. Deixar `_projetar_valor_terminal` e `_patrimonio_terminal_proxy` para microetapa econômica separada.
4. Não consolidar `para_dict` automaticamente se forem métodos de classes distintas.
5. Após qualquer alteração futura, validar diretamente:

```bash
python aplicacao/principal.py
```

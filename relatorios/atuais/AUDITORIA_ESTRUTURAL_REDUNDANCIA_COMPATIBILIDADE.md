# Auditoria estrutural de redundância e compatibilidade

## Escopo

Auditoria leve e diagnóstica originalmente aberta na V84 e atualizada na V85 focada em três frentes:

1. wrappers de compatibilidade em `scripts/`;
2. helpers duplicados em módulos do núcleo e da apresentação;
3. crescimento da superfície diagnóstica e sua carga de manutenção.

## Achados principais

### 1. Wrappers de compatibilidade

- existem **17 scripts raiz** em `scripts/` além de `__init__.py`;
- existe espelhamento entre scripts raiz e implementações reais em `scripts/diagnostico/`, `scripts/auditoria/` e `scripts/operacional`;
- há **pelo menos 4 wrappers raiz com falha confirmada de execução direta** por ausência de bootstrap de `sys.path`:
  - `scripts/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py`;
  - `scripts/verificar_release_baseline.py`;
- há **1 wrapper raiz com bootstrap inconsistente** e falha confirmada de execução direta:
  - `scripts/inspecionar_switching_economico_shadow.py`.

### 2. Helpers duplicados

Duplicações localizadas confirmadas:

- `_cfg` em `nucleo/resolver_hibrido_5p_shadow.py`, `nucleo/switching_economico_shadow.py` e `nucleo/triagem_motor.py`;
- `_iterar_datas` em `nucleo/resolver_hibrido_5p_shadow.py` e `nucleo/switching_economico_shadow.py`;
- `_simular_lote_ate_data` em `nucleo/resolver_hibrido_5p_shadow.py` e `nucleo/switching_economico_shadow.py`;
- `_normalizar_valores_situacao_atual_exaurida` em `aplicacao/console/principal.py` e `scripts/operacional/gerar_planilha_operacional.py`;
- `obter_config` em `nucleo/carregador_config.py` e `nucleo/config_utils.py`.

Essas duplicações ainda não geram regressão imediata, mas já elevam o risco de divergência futura.

### 3. Superfície diagnóstica

- a baseline mantém **15 diagnósticos canônicos** em `scripts/diagnostico/`;
- quase todos também possuem wrapper espelhado na raiz de `scripts/`;
- a superfície diagnóstica cresce mais rápido que o núcleo funcional, o que justifica classificação futura entre camadas canônica, histórica e experimental.

## Conclusão

A V84 permanece funcional e estável, mas a auditoria confirma a necessidade de uma futura correção arquitetural leve em duas frentes: 

1. correção e padronização dos wrappers raiz;
2. consolidação progressiva de helpers duplicados de baixo risco.

## Próxima etapa recomendada

Abrir uma etapa corretiva leve e isolada para:
- corrigir os wrappers raiz quebrados;
- padronizar o bootstrap dos wrappers;
- só depois decidir se vale consolidar helpers duplicados.


## Desdobramento na V85

A V85 corrigiu os wrappers raiz com bootstrap ausente ou inconsistente identificados nesta auditoria, restaurando a execução direta desses atalhos de compatibilidade. A parte restante desta auditoria continua válida apenas para o mapeamento de helpers duplicados e da superfície diagnóstica.

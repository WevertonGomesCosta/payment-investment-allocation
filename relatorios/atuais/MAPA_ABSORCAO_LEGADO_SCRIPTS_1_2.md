# Mapa de absorção legado — Scripts 1 e 2

## Escopo

Este documento classifica os blocos relevantes de `Script 1.txt` e `Script 2.txt` em quatro grupos:
- **migrar já**;
- **migrar depois**;
- **não migrar**;
- **substituída pela baseline atual**.

A V75 usa este mapa como referência obrigatória antes de qualquer nova migração funcional do legado.

## Script 1 — otimização e validação

### Migrar já
- `resolver_hibrido_5p(...)`
  - motivo: contém regra de decisão econômica ainda ausente na baseline atual, com pesos para IOF, IR, idade, liquidez, cliff e VPL.
  - forma recomendada de absorção: primeiro em modo **benchmark/diagnóstico shadow**, sem acoplamento direto ao fluxo principal.

### Migrar depois
- `carregar_parametros_hibrido_5p(...)`
- `carregar_parametros_hibrido_5p_passado(...)`
- `_escolher_modo_treino_por_objetivo(...)`
- `validacao_walk_forward(...)`
  - motivo: úteis para calibração posterior e comparação robusta, mas ainda não são o gargalo operacional da baseline.

### Não migrar
- `treinar_genetica_profundo(...)`
- `treinar_penalidade_5p(...)`
- `objective_pulp_wrapper_5p(...)`
- `salvar_parametros(...)`
- `carregar_parametros(...)`
- fallback de download via Drive, globais e infraestrutura de treino evolutivo
  - motivo: infraestrutura pesada, acoplada e não prioritária nesta fase.

### Substituída pela baseline atual
- utilidades de exportação e diagnósticos auxiliares que já têm equivalente mais simples e controlado na V74/V75.

## Script 2 — switching e diagnósticos

### Migrar já
- `otimizar_switches_portfolio_guloso(...)`
- `_avaliar_switching_e_diagnosticos(...)`
  - motivo: concentram a regra material de **switching econômico legado**, ainda ausente na baseline atual.
  - forma recomendada de absorção: primeiro em modo **shadow/auditoria**, sem substituir o fluxo principal.

### Migrar depois
- `_gerar_comparativo_validacao_switching(...)`
- `_avaliar_iteracao_switch(...)`
- `_decisoes_switch_marginais(...)`
- `_simular_riqueza_carteira(...)`
- `_switch_lotes_base(...)`
  - motivo: complementam a trilha diagnóstica do switching, mas dependem da camada principal acima.

### Não migrar
- `_exportar_resultados_excel(...)`
- `_montar_df_resumo_exportacao(...)`
- `_imprimir_resumo_consolidado_switches(...)`
- funções de impressão/exportação pesada e acoplamentos operacionais do legado
  - motivo: o repositório atual já possui caminhos próprios e mais controlados de saída.

### Substituída pela baseline atual
- trechos de resumo operacional e exportação já cobertos pela planilha operacional vigente, pela separação de seções do console e pelos diagnósticos canônicos da V74/V75.

## Prioridade imediata pós-V75

1. **Switching econômico legado** do Script 2, em modo shadow/auditoria.
2. **Benchmark do `resolver_hibrido_5p`** do Script 1, em modo diagnóstico comparativo.
3. Só depois avaliar a absorção de diagnósticos complementares e calibração.

## Regras de absorção

- Não migrar os scripts inteiros de forma bruta.
- Não incorporar infraestrutura pesada de treino, rede ou exportação antiga sem necessidade material.
- Toda migração funcional deve passar primeiro por camada shadow/diagnóstica quando a regra ainda estiver ausente.
- A baseline vigente continua com `proxy econômico v3` congelado até nova evidência concreta.

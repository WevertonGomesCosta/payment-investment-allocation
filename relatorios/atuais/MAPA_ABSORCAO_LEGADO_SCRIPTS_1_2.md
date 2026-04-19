# Mapa de absorção legado — Scripts 1 e 2

## Escopo

Este documento classifica os blocos relevantes de `Script 1.txt` e `Script 2.txt` em quatro grupos:
- **migrar já**;
- **migrar depois**;
- **não migrar**;
- **substituída pela baseline atual**.

> Correção de identidade vigente: o arquivo que havia sido tratado anteriormente como “Script 2” corresponde, na verdade, ao **Script 1**. O `Script 2.txt` correto passa a ser o runner legado de **switching + simulação futura + exportação final**.

A V92 usa este mapa como referência obrigatória antes de qualquer nova migração funcional do legado.

## Script 1 — otimização, validação e competição entre estratégias

### Migrar já
- `resolver_hibrido_5p(...)`
  - motivo: contém regra de decisão econômica ainda ausente na baseline atual, com pesos para IOF, IR, idade, liquidez, cliff e VPL.
  - forma recomendada de absorção: primeiro em modo **benchmark/diagnóstico shadow**, sem acoplamento direto ao fluxo principal.
- benchmark shadow do teste **agrupado vs. individual**
  - motivo: faz parte da governança da execução principal do Script 1 e já foi aberto como benchmark shadow, mantendo o modo `individual` como recomendação vigente.

### Migrar depois
- `carregar_parametros_hibrido_5p(...)`
- `carregar_parametros_hibrido_5p_passado(...)`
- `_escolher_modo_treino_por_objetivo(...)`
- `validacao_walk_forward(...)`
- competição final entre estratégias legadas em modo shadow
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
- utilidades de exportação e diagnósticos auxiliares que já têm equivalente mais simples e controlado na baseline vigente.

## Script 2 — runner de switching, simulação futura e exportação final

### Migrar já
- `simular_futuro(...)` como benchmark shadow do runner futuro
- auditoria shadow do processamento por evento futuro
- governança shadow dos modos de execução futura
  - motivo: concentram a orquestração material de switching + pagamentos futuros ainda ausente na baseline atual.
  - forma recomendada de absorção: primeiro em modo **shadow/auditoria**, sem substituir o fluxo principal.

### Migrar depois
- `_alocar_aportes_iniciais(...)`
- `_carregar_snapshot_inicial(...)`
- `_exportar_resultados_excel(...)`
- `_montar_relatorio_final_lotes(...)`
  - motivo: complementam o runner legado correto, mas dependem primeiro do benchmark shadow da execução futura.

### Não migrar
- `executar_runner_principal(...)` bruto como novo orquestrador da baseline
- prints/console legado como interface principal
- acoplamentos globais diretos do runner
  - motivo: a baseline atual já possui orquestração, saída e governança próprias.

### Substituída pela baseline atual
- leitura canônica dos dados
- cache CDI e fallback local
- geração do relatório operacional vigente
- camadas shadow já abertas para benchmarks específicos

## Prioridade imediata pós-V92

1. **Switching econômico legado** do Script 2 continua apenas em shadow — **aberto na V76**.
2. **Benchmark do `resolver_hibrido_5p`** do Script 1 continua diagnóstico comparativo — **aberto na V77/V78**.
3. **Benchmark shadow agrupado vs. individual** pertence ao Script 1 — **aberto na V88/V89**.
4. **Nova prioridade aberta na V92:** benchmark shadow do runner de simulação futura do Script 2 correto.

## Regras de absorção

- Não migrar os scripts inteiros de forma bruta.
- Não incorporar infraestrutura pesada de treino, rede ou exportação antiga sem necessidade material.
- Toda migração funcional deve passar primeiro por camada shadow/diagnóstica quando a regra ainda estiver ausente.
- A baseline vigente continua com `proxy econômico v3` congelado até nova evidência concreta.
- O runner legado correto do Script 2 não deve ser acoplado ao fluxo principal sem passar pelo benchmark shadow da simulação futura.

# Auditoria de duplicidade entre scripts e funções — V225

## Identificação

- Baseline operacional: V225
- Tipo: auditoria estrutural/organizacional
- Escopo: scripts e módulos potencialmente duplicados, fora ou próximos da rota `aplicacao/principal.py`
- Restrições desta microetapa:
  - não remover arquivos;
  - não alterar código;
  - não alterar config;
  - não alterar cálculo;
  - não alterar replay;
  - não alterar pagamentos;
  - não alterar switching;
  - não alterar ranking;
  - não alterar identidade da baseline.

## Objetivo

Auditar se existem scripts ou funções que:

1. não fazem parte da rota operacional chamada por `aplicacao/principal.py`;
2. repetem lógica já absorvida em `nucleo/` ou na saída canônica;
3. são wrappers/versionamentos antigos que podem confundir a execução final;
4. podem se tornar problema se forem usados como fonte operacional paralela.

## Rota operacional atual da V225

A rota principal validada é:

```text
aplicacao/principal.py
├── aplicacao.console.principal.main
└── scripts.operacional.gerar_planilha_operacional.main
```

`aplicacao/principal.py` importa diretamente o console e o gerador base da planilha operacional.

A função `carregar_contexto_baseline(...)` é a fronteira operacional que materializa os objetos centrais usados pelo console e pela planilha, incluindo config, calendário, planilha, carteira canônica, dados operacionais, cache CDI, replay, ranking, fontes elegíveis, recomputação, motor de recomendação e camadas shadow/diagnósticas conforme flags.

## Fontes utilizadas na auditoria

- `aplicacao/principal.py`
- `aplicacao/console/principal.py`
- `scripts/operacional/gerar_planilha_operacional.py`
- `nucleo/contexto_baseline.py`
- `relatorios/atuais/limpeza_scripts/inventario_scripts_diagnostico.csv`
- scripts diagnósticos representativos:
  - `scripts/diagnostico/_governanca_saida.py`
  - `scripts/diagnostico/verificar_release_limpo.py`
  - `scripts/diagnostico/auditar_gate_economico_aportes_v223.py`
  - `scripts/diagnostico/auditar_impacto_contas_futuras_v223.py`
  - `scripts/diagnostico/auditar_calculo_dias_lotes_v218.py`
  - `scripts/diagnostico/auditar_calculo_dias_lotes_v219.py`
- módulos históricos/experimentais representativos:
  - `nucleo/fluxo_pagamentos_terminal_v138.py`
  - `nucleo/fluxo_pagamentos_terminal_recorte_amplo_v142.py`

## Resultado executivo

Não há evidência, nesta auditoria, de que os scripts diagnósticos sejam chamados diretamente por `aplicacao/principal.py`. A maior parte dos scripts em `scripts/diagnostico/` é independente, bloqueada por governança ou funciona como wrapper de compatibilidade/histórico.

Entretanto, há redundâncias importantes que devem ser controladas antes da versão final do projeto:

1. **scripts diagnósticos bloqueados**: muitos arquivos mantêm apenas stubs de bloqueio V203 e podem ser candidatos futuros a remoção física;
2. **wrappers canônicos que delegam para versões antigas**: alguns nomes novos, como V223, delegam para scripts antigos V217/V220, criando inversão semântica;
3. **auditorias V218/V219**: repetem helpers e lógica, com V219 supersedendo V218;
4. **módulos experimentais V138/V142**: mantêm lógica de fluxo, switching e simulação paralela à rota atual, com risco se forem reabsorvidos sem comparação;
5. **helpers repetidos**: `_parse_data`, `_safe_float`, `_salvar_csv`, `_cfg_get`, bootstrap de raiz e formatação de tabela aparecem em vários scripts, principalmente diagnósticos;
6. **console ainda contém preparo local de auditorias residuais**: parte da apresentação já vem da saída canônica, mas há funções locais de console que podem virar redundância futura se começarem a recalcular algo que deveria vir de `nucleo.saida_canonica`.

## Classificação por grupos

### Grupo A — rota principal / manter

| Arquivo | Status | Justificativa |
|---|---|---|
| `aplicacao/principal.py` | manter | entrypoint operacional |
| `aplicacao/console/principal.py` | manter, auditar gradualmente | console oficial; ainda tem funções locais de apresentação/auditoria |
| `scripts/operacional/gerar_planilha_operacional.py` | manter | fonte única da planilha operacional após remoção do wrapper |
| `nucleo/contexto_baseline.py` | manter | fronteira central de materialização da baseline |
| `nucleo/saida_canonica.py` | manter | fonte canônica da camada observável |

### Grupo B — scripts diagnósticos independentes chamados manualmente

Esses scripts não fazem parte da rota de `aplicacao/principal.py`, mas podem ser úteis como diagnósticos manuais:

| Arquivo/grupo | Status recomendado | Observação |
|---|---|---|
| `scripts/diagnostico/verificar_release_limpo.py` | manter | executa limpeza efêmera e delega ao release checker |
| `scripts/diagnostico/verificar_release_baseline.py` | manter | release checker principal |
| `scripts/diagnostico/limpar_artefatos_efemeros.py` | manter | utilitário oficial de limpeza pré-release |
| `scripts/diagnostico/auditoria_final_pre_baseline_v223.py` | manter por enquanto | diagnóstico de promoção/validação final |
| `scripts/diagnostico/auditar_divergencias_motor_central_extrato_v241.py` | manter por enquanto | auditoria recente do motor central versus extrato |

Decisão: não remover esses scripts nesta etapa.

### Grupo C — scripts bloqueados por governança V203

Vários scripts em `scripts/diagnostico/` já foram convertidos em stubs de bloqueio com `bloquear_script_legado(...)`. O módulo `_governanca_saida.py` centraliza essa política e imprime marcador de bloqueio, motivo, alternativa canônica e retorno 2.

Exemplos no inventário:

- `consolidar_grade_diaria_hibrida_v133.py`
- `consolidar_grade_diaria_hibrida_v134.py`
- `consolidar_grade_diaria_hibrida_v136.py`
- `consolidar_grade_diaria_switching_v126.py`
- `consolidar_grade_diaria_switching_v127.py`
- `consolidar_grade_diaria_switching_v128.py`
- `inspecionar_alocador_pagamentos_terminal_v137.py`
- `inspecionar_alocador_pagamentos_terminal_v141.py`
- `inspecionar_comparador_hibrido_switching_v132.py`
- `inspecionar_fluxo_pagamentos_terminal_recorte_curto_v138.py`
- `inspecionar_fluxo_pagamentos_terminal_recorte_amplo_v142.py`
- muitos outros listados no inventário de scripts diagnósticos.

Classificação:

- não são dependências da rota principal;
- não devem ser usados como fonte operacional;
- são candidatos fortes a remoção física futura, desde que a trilha histórica esteja preservada em relatórios e/ou `scripts/historico_saida_propria_v203/`.

Risco se mantidos indefinidamente: ruído estrutural, falsas opções de execução e confusão entre scripts oficiais e scripts bloqueados.

### Grupo D — wrappers/versionamentos que delegam para versões antigas

#### `auditar_gate_economico_aportes_v223.py`

Esse script se declara canônico V223, mas delega para:

```text
scripts.diagnostico.auditar_gate_economico_aportes_v220.main
```

Classificação:

- wrapper de compatibilidade;
- potencialmente confuso, pois o nome V223 chama uma implementação V220;
- não faz parte da rota principal;
- candidato futuro a reestruturação.

Decisão futura recomendada:

- ou transformar V223 em arquivo real com implementação consolidada;
- ou renomear/documentar claramente que V223 é alias de V220;
- ou manter apenas um script canônico e mover versões antigas para histórico.

#### `auditar_impacto_contas_futuras_v223.py`

Esse script se declara canônico V223, mas delega para:

```text
scripts.diagnostico.auditar_impacto_contas_futuras_v217.main
```

Classificação:

- wrapper de compatibilidade;
- potencialmente confuso, pois o nome V223 chama uma implementação V217;
- não faz parte da rota principal;
- candidato futuro a consolidação.

Decisão futura recomendada:

- inverter a dependência: script antigo delega para o canônico novo; ou
- promover uma implementação sem sufixo versionado; ou
- mover versões antigas para histórico.

### Grupo E — auditorias V218/V219 com duplicidade funcional

`auditar_calculo_dias_lotes_v218.py` e `auditar_calculo_dias_lotes_v219.py` compartilham estrutura semelhante:

- `_salvar_csv(...)`
- `_parse_data(...)`
- `_safe_float(...)`
- `_carregar_serie_cdi(...)`
- varredura por padrões de duplicação em código
- leitura de `dados/cache_bcb.json`
- leitura de `dados/dados_financeiros.xlsx`
- geração de CSVs de auditoria.

Diferença principal:

- V218 valida cálculo visual de dias corridos/dias úteis;
- V219 expande para idade fiscal centralizada com `nucleo.fiscal_lotes`.

Classificação:

- V219 supersede V218 para auditoria de idade/dias;
- V218 é candidato a histórico ou bloqueio futuro;
- helpers repetidos devem, se ainda necessários, ir para módulo comum de diagnóstico, não para o núcleo operacional.

Risco se mantidos ativos: duas auditorias parecidas podem gerar divergência de interpretação sobre qual resultado é oficial.

### Grupo F — fluxos experimentais V138/V142 no `nucleo/`

#### `nucleo/fluxo_pagamentos_terminal_v138.py`

Contém fluxo completo de pagamentos em recorte curto, com:

- carregamento próprio de contexto;
- montagem de estado;
- plano de switching promovível;
- simulação de cenários;
- consumo de componentes;
- resultados e resumo próprios.

#### `nucleo/fluxo_pagamentos_terminal_recorte_amplo_v142.py`

Importa helpers da V138, mas também duplica lógica importante:

- `_comparar_com_baseline(...)`
- `_melhor_plano_switching_promovivel_para_estado(...)`
- `_rodar_fluxo(...)`
- estruturas dataclass próprias;
- comparação H1-H3;
- simulação de fluxo completo.

Classificação:

- módulos experimentais/históricos;
- não são chamados pela rota principal atual;
- contêm lógica de simulação e switching que se sobrepõe conceitualmente a módulos centrais mais novos;
- risco alto se forem reabsorvidos sem benchmark contra motor atual.

Decisão recomendada:

- não remover imediatamente;
- classificar como `nucleo/experimental` ou `nucleo/historico` em etapa futura;
- impedir import acidental pela rota principal;
- antes de remover, verificar se algum diagnóstico ainda precisa deles.

### Grupo G — runners e versões paralelas

O inventário mostra versões múltiplas de runners/validações:

- `nucleo/runner_validacao_diaria_operacional_v175.py`
- `nucleo/runner_validacao_diaria_operacional_v176.py`
- `nucleo/runner_validacao_diaria_operacional_v177.py`
- scripts diagnósticos correspondentes `inspecionar_validacao_diaria_operacional_v176.py` e `v177.py`

Classificação:

- versões paralelas/históricas;
- muitas já bloqueadas por governança nos scripts diagnósticos;
- podem permanecer como trilha histórica por enquanto;
- candidatos futuros a arquivo histórico ou remoção após inventário de importações.

Risco: reativação acidental de runner antigo com semântica anterior à saída canônica.

### Grupo H — helpers repetidos em scripts diagnósticos

Padrões encontrados/observados:

| Helper | Onde aparece/risco | Decisão |
|---|---|---|
| `_parse_data` | auditorias V218/V219 e outros diagnósticos | consolidar apenas se diagnósticos permanecerem ativos |
| `_safe_float` | diagnósticos e módulos antigos; existe utilitário neutro em `nucleo.utilitarios_neutros` | preferir utilitário canônico quando código for operacional |
| `_salvar_csv` | diagnósticos | aceitável localmente, mas repetitivo |
| `_cfg_get` | planilha operacional e ex-wrapper; existe `nucleo.config_utils.obter_config` | migrar futuramente se quiser reduzir repetição |
| bootstrap de `sys.path`/RAIZ | múltiplos scripts | usar `scripts/diagnostico/_bootstrap.py` para diagnósticos |
| impressão de tabelas | console e `_governanca_saida` | manter separado por enquanto, pois console é camada oficial e diagnóstico é auxiliar |

Decisão: não consolidar helpers genéricos agora, exceto quando forem usados por código operacional. Em diagnósticos, a repetição é menos crítica do que em `nucleo/` ou `aplicacao/`.

### Grupo I — console com preparo local de auditorias residuais

`aplicacao/console/principal.py` já consome `construir_saida_canonica(...)`, mas ainda possui funções locais para preparar auditorias de resíduos e fechamento:

- `_preparar_auditoria_lotes_residuais(...)`
- `_preparar_auditoria_detalhada_residuos(...)`
- `_preparar_resumo_auditoria_detalhada_residuos(...)`
- `_preparar_auditoria_recebimento_vs_aplicacao(...)`, que retorna lista vazia como compatibilidade temporária.

Classificação:

- não é duplicidade deletável agora;
- é risco moderado de redundância futura se começar a divergir de `nucleo.saida_canonica`;
- deve ser auditado em uma microetapa própria.

Decisão futura recomendada:

- migrar gradualmente qualquer auditoria observável estável para `nucleo.saida_canonica` ou módulo canônico auxiliar;
- manter no console apenas renderização e formatação.

## Matriz de risco

| Item | Risco atual | Risco futuro | Ação recomendada |
|---|---:|---:|---|
| Scripts bloqueados V203 | baixo | médio | remover fisicamente após inventário final |
| Wrappers V223 → V217/V220 | baixo | médio/alto | consolidar nomes canônicos ou mover antigos para histórico |
| V218 vs V219 | baixo | médio | manter V219; mover/bloquear V218 futuramente |
| Fluxos V138/V142 | médio | alto | classificar como experimental/histórico; não importar na rota principal |
| Runners V175/V176/V177 | baixo/médio | médio | auditar importações e manter só versão útil/histórica |
| Helpers repetidos diagnósticos | baixo | baixo/médio | consolidar apenas se diagnósticos permanecerem ativos |
| Funções locais do console | médio | médio/alto | auditar depois; console deve renderizar, não recalcular contrato canônico |
| `_cfg_get` duplicado | baixo | baixo | possível migração futura para `nucleo.config_utils` |

## Decisão desta auditoria

Não remover nada nesta microetapa.

A limpeza deve ser feita em etapas menores, na seguinte ordem recomendada:

1. **Auditar scripts bloqueados V203** e remover fisicamente apenas os stubs que não tenham referência operacional nem uso documental necessário.
2. **Consolidar wrappers V223**: transformar `auditar_gate_economico_aportes_v223.py` e `auditar_impacto_contas_futuras_v223.py` em scripts canônicos reais ou mover V217/V220 para histórico.
3. **Resolver V218/V219**: manter V219 como canônico e classificar V218 como histórico/bloqueado.
4. **Auditar fluxos V138/V142**: decidir se são legado experimental ou se alguma função deve ser absorvida formalmente por módulos atuais.
5. **Auditar console**: separar renderização de cálculo, evitando duplicidade futura com `nucleo.saida_canonica`.
6. **Só depois consolidar helpers genéricos** em módulo comum se ainda houver benefício real.

## Próxima microetapa recomendada

A próxima etapa mais segura é a remoção controlada de scripts bloqueados V203, porque eles já não têm autoridade operacional e aparecem no inventário como candidatos à remoção. Antes da remoção, deve-se buscar referências a cada arquivo e preservar a trilha histórica nos relatórios.

Prompt sugerido:

```text
Use a V225 após a auditoria de duplicidade de scripts e funções e abra uma microetapa apenas para auditar os scripts diagnósticos bloqueados por governança V203. Identifique quais arquivos são apenas stubs com bloquear_script_legado(...), quais possuem conteúdo real, quais têm referência operacional e quais podem ser removidos fisicamente com segurança. Não alterar código funcional, config, cálculo, replay, pagamentos, switching, ranking nem identidade da baseline. Se houver remoção, fazer em lote pequeno e validar python aplicacao/principal.py.
```

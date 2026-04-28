# Inventário de uso real do config — baseline V225

## Identificação

- Baseline operacional validada: V225
- Microetapa: auditoria documental/diagnóstica de configuração
- Arquivo canônico de referência: `dados/config_atualizado.json`
- Entry point preservado: `aplicacao/principal.py`
- Escopo: fluxo chamado por `aplicacao/principal.py`, incluindo console e geração da planilha operacional
- Restrições aplicadas:
  - não alterar motor econômico;
  - não alterar regras de pagamento;
  - não alterar regras de switching;
  - não alterar replay;
  - não remover arquivos da pasta `config/`;
  - não alterar `nucleo/identidade_baseline.py`.

## Fontes inspecionadas

### Entry points

- `aplicacao/principal.py`
- `aplicacao/console/principal.py`
- `scripts/operacional/gerar_planilha_operacional.py`

### Núcleo chamado pelo fluxo principal

- `nucleo/carregador_config.py`
- `nucleo/config_utils.py`
- `nucleo/contexto_baseline.py`
- `nucleo/ambiente.py`
- `nucleo/leitor_planilha.py`
- `nucleo/carteira_canonica.py`
- `nucleo/dados_operacionais_canonicos.py`
- `nucleo/cache_cdi_bcb.py`
- `nucleo/calendario_financeiro.py`
- `nucleo/nucleo_financeiro_minimo.py`
- `nucleo/replay_passado_controlado.py`
- `nucleo/triagem_motor.py`
- `nucleo/ranking_carteira_estabilizado.py`
- `nucleo/saida_canonica.py`

## Resultado executivo

A auditoria confirma que `dados/config_atualizado.json` está sendo carregado como config canônico no fluxo operacional validado. O `aplicacao/principal.py` não acessa configuração diretamente; ele chama `main_console()` e `main_planilha()`. O consumo real do config ocorre principalmente por `carregar_contexto_baseline()`, que injeta `pacote_config.conteudo` nas camadas operacionais.

A pasta `config/` não deve ser removida nesta microetapa. Ela contém contratos e parâmetros específicos do ranking da Carteira, especialmente:

- `config/carteira_contract_v123.json`;
- `config/fixed_parameters_ranking_carteira.json`.

Esses arquivos não substituem `dados/config_atualizado.json`; eles são insumos específicos de `nucleo/ranking_carteira_estabilizado.py`.

## Chaves efetivamente consumidas no fluxo principal

### 1. Carregamento e validação do config

| Chave | Consumidor | Uso observado |
|---|---|---|
| `execucao.timezone` | `nucleo/carregador_config.py`, `nucleo/ambiente.py` | validação obrigatória e resolução de timezone |
| `arquivos.planilha` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py` | validação obrigatória e caminho da planilha local |
| `abas.carteira` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/carteira_canonica.py`, console | nome da aba Carteira |
| `abas.lotes` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/dados_operacionais_canonicos.py`, console | nome da aba Inventário de Lotes |
| `abas.despesas` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/dados_operacionais_canonicos.py`, console | nome da aba Todos os Gastos |
| `colunas.carteira` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/carteira_canonica.py` | aliases e resolução de colunas da Carteira |
| `colunas.lotes` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/dados_operacionais_canonicos.py` | aliases e resolução de colunas do Inventário |
| `colunas.despesas` | `nucleo/carregador_config.py`, `nucleo/leitor_planilha.py`, `nucleo/dados_operacionais_canonicos.py` | aliases e resolução de colunas de Todos os Gastos |

### 2. Ambiente e data de referência

| Chave | Consumidor | Uso observado |
|---|---|---|
| `ambiente.instalar_dependencias_automaticamente` | `nucleo/ambiente.py` | fallback quando o chamador não força `instalar_automaticamente` |
| `execucao.timezone` | `nucleo/ambiente.py` | timezone operacional |
| `execucao.data_referencia_simulacao` | `nucleo/ambiente.py` | permite fixar data de referência; quando nulo, usa data atual no timezone |
| `execucao.convencao_dias_ano.cdi` | `nucleo/cache_cdi_bcb.py`, `nucleo/calendario_financeiro.py` | convenção anual do CDI |

Observação: no fluxo atual de `aplicacao/principal.py`, `carregar_contexto_baseline()` chama `bootstrap_ambiente(..., instalar_automaticamente=False)`, portanto o valor de `ambiente.instalar_dependencias_automaticamente` não controla essa execução específica, embora continue suportado pela função.

### 3. Download da planilha e rede

| Chave | Consumidor | Uso observado |
|---|---|---|
| `urls.planilha_financeira_url` | `nucleo/leitor_planilha.py` | URL direta opcional da planilha |
| `google_drive.sheets_file_id` | `nucleo/leitor_planilha.py` | ID usado para montar URL de exportação quando não há URL direta |
| `urls.google_sheets_export_base` | `nucleo/leitor_planilha.py` | template de exportação da planilha |
| `rede.timeout_download_segundos` | `nucleo/leitor_planilha.py` | timeout do download da planilha |
| `rede.verificar_ssl` | `nucleo/leitor_planilha.py`, `nucleo/cache_cdi_bcb.py` | controle de verificação SSL nas requisições |
| `rede.user_agent_download_planilha` | `nucleo/leitor_planilha.py` | header User-Agent para download da planilha |

### 4. CDI/BCB e cache

| Chave | Consumidor | Uso observado |
|---|---|---|
| `arquivos.cache_bcb` | `nucleo/cache_cdi_bcb.py` | caminho do cache CDI local |
| `urls.bcb_sgs_12_url` | `nucleo/cache_cdi_bcb.py` | template da API SGS 12 do BCB |
| `rede.timeout_bcb_segundos` | `nucleo/cache_cdi_bcb.py` | timeout da chamada BCB |
| `rede.user_agent_bcb` | `nucleo/cache_cdi_bcb.py` | header User-Agent do BCB |
| `rede.accept_bcb` | `nucleo/cache_cdi_bcb.py` | header Accept da chamada BCB |
| `premissas_mercado.cdi_anual_modelo` | `nucleo/calendario_financeiro.py`, `nucleo/triagem_motor.py` | taxa anual de modelo/fallback e proxy de retorno |

Observação: `premissas_mercado.cdi_diario_projecao` é consultado no cache com default interno `0.0`, mas não existe no `config_atualizado.json` atual. Não deve ser criado nesta microetapa; apenas fica registrado como possível chave futura se a política de projeção diária for formalizada.

### 5. Calendário financeiro

| Chave | Consumidor | Uso observado |
|---|---|---|
| `premissas_mercado.cdi_anual_modelo` | `nucleo/calendario_financeiro.py` | taxa CDI anual usada para taxa diária base |
| `execucao.convencao_dias_ano.cdi` | `nucleo/calendario_financeiro.py` | dias úteis/ano para cálculo da taxa diária |
| `calendario.ano_inicio_dias_sem_rendimento` | `nucleo/calendario_financeiro.py` | início da janela de dias sem rendimento bancário |
| `calendario.ano_fim_dias_sem_rendimento` | `nucleo/calendario_financeiro.py` | fim da janela de dias sem rendimento bancário |

### 6. Carteira canônica

| Chave | Consumidor | Uso observado |
|---|---|---|
| `abas.carteira` | `nucleo/carteira_canonica.py` | seleção da aba Carteira |
| `colunas.carteira.*` | `nucleo/carteira_canonica.py` | resolução de colunas estruturais da Carteira |
| `politicas_taxa.limite_percentual_vs_multiplicador` | `nucleo/carteira_canonica.py` | normalização de taxas em formato percentual vs multiplicador |

Subchaves de `colunas.carteira` efetivamente chamadas pela canonização:

- `produto_id`
- `nome`
- `tipo`
- `indexador`
- `taxa_base`
- `taxa_bonus`
- `dias_bonus`
- `prazo_dias`
- `carencia_dias`
- `liquidez_dias`
- `isento_ir`
- `aplicacao_minima`
- `aplicacao_maxima`
- `ativo`
- `fgc`
- `banco_emissor`
- `risco_real`
- `somente_combo`
- `permite_combo`
- `produto_base`
- `produto_bonus`
- `ratio_base`
- `ratio_bonus`
- `max_usos`
- `observacoes`
- `produto_padrao`
- `camada`
- `status_confirmacao`
- `campos_pendentes`
- `score_banco`
- `familia_produto`
- `regime_taxa`
- `regime_liquidez`
- `papel_produto`
- `elegivel_motor`
- `elegivel_aporte_novo`
- `elegivel_switch_in`
- `elegivel_reconciliacao_historica`

### 7. Dados operacionais canônicos

| Chave | Consumidor | Uso observado |
|---|---|---|
| `abas.lotes` | `nucleo/dados_operacionais_canonicos.py` | seleção do Inventário de Lotes |
| `abas.despesas` | `nucleo/dados_operacionais_canonicos.py` | seleção de Todos os Gastos |
| `colunas.lotes.*` | `nucleo/dados_operacionais_canonicos.py` | resolução de colunas do inventário |
| `colunas.despesas.*` | `nucleo/dados_operacionais_canonicos.py` | resolução de colunas de gastos |
| `politicas.tratar_pago_nulo_como_nao` | `nucleo/dados_operacionais_canonicos.py` | interpretação de célula nula no campo Pago |

Subchaves de `colunas.lotes` efetivamente chamadas:

- `lote_id`
- `data_recebimento`
- `data_aplicacao`
- `valor_original`
- `produto_id`
- `status_lote`
- `data_base_fiscal`

Subchaves de `colunas.despesas` efetivamente chamadas:

- `despesa_id`
- `data`
- `descricao`
- `valor`
- `pago`
- `lote_usado_1`
- `lote_usado_2`

### 8. Núcleo financeiro mínimo

| Chave | Consumidor | Uso observado |
|---|---|---|
| `iof.tabela` | `nucleo/nucleo_financeiro_minimo.py` | tabela regressiva de IOF |
| `ir.faixas` | `nucleo/nucleo_financeiro_minimo.py` | faixas regressivas de IR |
| `replay.tolerancia_monetaria` | `nucleo/nucleo_financeiro_minimo.py`, `nucleo/replay_passado_controlado.py` | tolerância de saque/exaustão |
| `replay.valor_minimo_lote_ativo` | `nucleo/nucleo_financeiro_minimo.py`, `nucleo/replay_passado_controlado.py` | limiar mínimo de lote ativo |
| `defaults_lote.taxa_base_cdi` | `nucleo/nucleo_financeiro_minimo.py` | fallback de taxa-base para lote sem produto mapeado |
| `defaults_lote.taxa_bonus_cdi` | `nucleo/nucleo_financeiro_minimo.py` | fallback de taxa-bônus |
| `defaults_lote.dias_bonus` | `nucleo/nucleo_financeiro_minimo.py` | fallback de dias de bônus |

### 9. Replay passado controlado

| Chave | Consumidor | Uso observado |
|---|---|---|
| `replay.tolerancia_monetaria` | `nucleo/replay_passado_controlado.py` | tolerância para coberturas e saques |
| `replay.valor_minimo_lote_ativo` | `nucleo/replay_passado_controlado.py` | corte operacional de saldo ativo |
| `auditoria.limiar_residuo_resolvido` | `nucleo/replay_passado_controlado.py`, `nucleo/contexto_baseline.py`, `nucleo/saida_canonica.py`, console | limiar para normalizar resíduo como resolvido |
| `iof.tabela` | via `construir_tabela_iof()` | cálculo líquido no replay |
| `ir.faixas` | via `construir_faixas_ir()` | cálculo líquido no replay |

### 10. Triagem do motor

| Chave | Consumidor | Uso observado |
|---|---|---|
| `simulacao.horizonte_alocacao_dias` | `nucleo/triagem_motor.py` | horizonte principal da triagem e proxy de retorno |
| `simulacao.horizonte_minimo_dias` | `nucleo/triagem_motor.py` | metadado de contexto da triagem |
| `premissas_mercado.cdi_anual_modelo` | `nucleo/triagem_motor.py` | proxy de retorno CDI |
| `premissas_mercado.selic_anual_modelo` | `nucleo/triagem_motor.py` | proxy de retorno Selic |
| `premissas_mercado.ipca_anual_modelo` | `nucleo/triagem_motor.py` | proxy de retorno IPCA |
| `triagem_motor.cap_anual_variavel` | `nucleo/triagem_motor.py` | teto para retorno proxy variável |
| `triagem_motor.cap_anual_cdi_multiplicador` | `nucleo/triagem_motor.py` | teto de multiplicador CDI |
| `triagem_motor.peso_retorno` | `nucleo/triagem_motor.py` | peso do score de retorno |
| `triagem_motor.peso_liquidez` | `nucleo/triagem_motor.py` | peso do score de liquidez |
| `triagem_motor.peso_viabilidade` | `nucleo/triagem_motor.py` | peso do score de viabilidade |
| `triagem_motor.peso_risco` | `nucleo/triagem_motor.py` | peso do score de risco |
| `triagem_motor.top_k_global` | `nucleo/triagem_motor.py` | corte global de candidatos |
| `triagem_motor.top_k_por_familia` | `nucleo/triagem_motor.py` | corte por família de produto |
| `triagem_motor.score_minimo_selecao` | `nucleo/triagem_motor.py` | score mínimo de seleção |
| `triagem_motor.modo_calibracao` | `nucleo/triagem_motor.py` | rótulo/auditoria do modo de calibragem |

### 11. Ranking oficial da Carteira

O ranking oficial consome arquivos específicos da pasta `config/`, não o bloco global `dados/config_atualizado.json`:

| Arquivo | Consumidor | Uso observado |
|---|---|---|
| `config/carteira_contract_v123.json` | `nucleo/ranking_carteira_estabilizado.py` | contrato de colunas, aba, colunas derivadas e ponte para parâmetros fixos |
| `config/fixed_parameters_ranking_carteira.json` | `nucleo/ranking_carteira_estabilizado.py` | parâmetros fixos do score/ranking da Carteira |

Conclusão: preservar ambos por enquanto. Eles são configs específicos de módulo, não duplicatas diretas do config global.

### 12. Saída canônica, console e planilha operacional

| Componente | Uso real de config |
|---|---|
| `nucleo/saida_canonica.py` | usa `contexto.pacote_config.conteudo` principalmente para obter `auditoria.limiar_residuo_resolvido` via `obter_limiar_residuo_resolvido()` |
| `aplicacao/console/principal.py` | usa `pacote_config.conteudo` para nomes de abas e limiar de resíduos; demais seções consomem objetos já materializados pelo contexto |
| `scripts/operacional/gerar_planilha_operacional.py` | não usa diretamente `saidas.*` do config; usa `nucleo.identidade_baseline` e nomes de abas hardcoded na planilha gerada |

## Chaves presentes no config mas não localizadas como consumo direto no fluxo principal auditado

As chaves abaixo aparecem em `dados/config_atualizado.json`, mas não foram localizadas como consumo direto nos arquivos centrais do fluxo `aplicacao/principal.py` inspecionados nesta microetapa. Isso não implica remoção automática; implica apenas que exigem decisão futura antes de limpeza.

### Candidatas a manter como reserva/futuro ou revisar depois

| Chave/bloco | Classificação diagnóstica | Observação |
|---|---|---|
| `google_drive.fallback_bcb_file_id` | não localizado no fluxo principal | pode pertencer a fallback legado/futuro de Drive |
| `google_drive.fallback_param_5p_file_id` | não localizado no fluxo principal | associado a parâmetros 5p/legado; não remover ainda |
| `arquivos.config_atualizado` | não necessário ao loader atual | o loader já fixa `config_atualizado.json` no código; pode ser documentado ou removido futuramente se redundante |
| `arquivos.parametros_5p` | não localizado no fluxo principal | preservar até concluir auditoria dos módulos 5p/shadow |
| `arquivos.log_decisoes_csv` | não localizado no fluxo principal | possível legado de saída |
| `arquivos.historico_lotes_csv` | não localizado no fluxo principal | possível legado de saída |
| `arquivos.temporario_fallback_bcb` | não localizado no fluxo principal | possível legado de fallback BCB |
| `ambiente.modo` | não consumido no fluxo principal auditado | comportamento atual detecta ambiente por função |
| `ambiente.base_dir_local` | não consumido no fluxo principal auditado | caminho resolvido por raiz do repositório |
| `ambiente.base_dir_colab` | não consumido no fluxo principal auditado | Colab é detectado, mas base_dir_colab não aparece como decisor direto |
| `bootstrap.*` | não consumido após fixação do loader | manter apenas se houver script legado que ainda leia esse bloco |
| `historico_bcb.*` | não consumido no cache atual | a janela é derivada dos dados operacionais e data de referência |
| `politicas_coluna.*` | não consumido no fluxo principal atual | pode ser legado de heurística de escolha de coluna |
| `validacoes.*` | não consumido de forma centralizada | validações atuais estão codificadas localmente nos módulos |
| `semantica_bonus.*` | não consumido como regra executável | documentação semântica, não motor atual |
| `pagamento.*` | não localizado como consumo direto no fluxo principal auditado | regras atuais de recomendação parecem distribuídas em módulos, não por esse bloco global |
| `estrategias.*` | não localizado no fluxo principal auditado | provável legado de estratégia global |
| `defaults.ignorar_lote_invalido` | não localizado no fluxo principal auditado | provável legado |
| `saidas.*` | não consumido pela planilha operacional atual | nomes de abas/arquivo estão hardcoded em `gerar_planilha_operacional.py` e `identidade_baseline.py` |
| `exportacao.*` | não consumido na saída operacional atual | possível contrato futuro de exportação |
| `logging.*` | não consumido no fluxo principal auditado | console usa prints/seções, não logging configurável |
| `treinamento.*` | não consumido no fluxo principal validado | manter se módulos de treino ainda existirem fora do fluxo principal |
| `otimizacao.*` | não consumido no fluxo principal validado | manter até auditoria dos módulos shadow/solver |
| `avaliacao.*` | não consumido no fluxo principal validado | manter até auditoria dos relatórios/treino |
| `relatorio.situacao_atual.modo_data_fiscal_liquido` | não localizado no fluxo principal auditado | candidato a conectar futuramente à saída canônica |
| `triagem_motor.janelas_pagamento_dias` | não localizado na triagem atual | triagem calcula janelas fixas 30/60/90 no código |
| `triagem_motor.considerar_confiabilidade_operacional_no_score` | não localizado na triagem atual | coerente com decisão anterior de não usar confiabilidade no score principal nesta fase |
| `defaults_lote.taxa_base_referencia_futura_default` | não localizado no fluxo principal auditado | possível fallback futuro |

## Parâmetros hardcoded candidatos à migração futura

Esta seção registra candidatos, sem recomendar alteração imediata.

### 1. `nucleo/triagem_motor.py`

Candidatos:

- mapa de risco textual:
  - `muito baixo -> 100`
  - `baixo -> 85`
  - `medio -> 60`
  - `alto -> 30`
  - `muito alto -> 10`
- janelas de despesas futuras fixas:
  - 30 dias;
  - 60 dias;
  - 90 dias;
- regras de score de liquidez por bloqueio:
  - `<= 7`, `<= 30`, `<= 60`, `<= 90`, `> 90`;
- penalizações de liquidez e viabilidade.

Observação: parte disso já tem aproximação no config (`triagem_motor.janelas_pagamento_dias`), mas o código atual ainda usa janelas fixas.

### 2. `nucleo/carteira_canonica.py`

Candidatos:

- derivação de `familia_produto` por texto;
- derivação de `regime_taxa` por texto;
- derivação de `regime_liquidez` por carência/liquidez/prazo;
- derivação de `papel_produto`;
- semântica transitória de campos estruturais ausentes.

Observação: como o próprio módulo declara, esses metadados são ponte transitória até maior estruturação da aba Carteira.

### 3. `nucleo/dados_operacionais_canonicos.py`

Candidatos:

- semântica de `Investimento = '-'` como `nao_aportado_exaurido`;
- semântica de investimento em branco como `nao_aportado_disponivel` ou `recebido_futuro_nao_disponivel`;
- geração de `despesa_auto_00001` quando ID está ausente;
- conjunto de valores aceitos como pago (`ok`, `sim`, `s`, `true`, `1`, `pago`, `yes`, `y`).

Observação: essas regras são centrais e devem ser migradas apenas com contrato explícito, porque afetam replay, pagamentos e situação atual.

### 4. `nucleo/replay_passado_controlado.py`

Candidatos:

- score para resolver alias de lote histórico não aportado;
- materialização de lotes históricos exauridos;
- motivos de inconsistência;
- rótulos de fase operacional do lote;
- regra local de normalização de saldo remanescente no log.

Observação: não alterar sem auditoria econômica e validação contra saídas.

### 5. `nucleo/cache_cdi_bcb.py`

Candidatos:

- interpretação do SGS como taxa diária percentual;
- formato esperado do cache (`mapa`, `registros`, `meta`);
- validação mínima de fator `> 1.0`;
- janela de consulta derivada dos dados em vez de `historico_bcb`.

### 6. `nucleo/calendario_financeiro.py`

Candidatos:

- cálculo próprio da Páscoa/Carnaval;
- fallback segunda–sexta quando `workalendar` não estiver disponível;
- fallback encadeado para último fator CDI explícito.

### 7. `nucleo/saida_canonica.py`

Candidatos:

- nomes de colunas observáveis;
- limites de amostras;
- rótulos de status e filtros de destino de switching;
- regras de seleção de quadros preferenciais;
- rótulos de cobertura integral e necessidade de switching.

### 8. `scripts/operacional/gerar_planilha_operacional.py`

Candidatos:

- nomes das abas geradas:
  - `Extrato Passado`;
  - `Extrato Futuro`;
  - `Switching`;
  - `Carteira`;
  - `Top30`;
  - `Resumo Switching`;
  - `Validacao`;
  - `Situação Atual`;
  - `Saida Canonica`;
- estilos visuais de planilha;
- cabeçalhos de tabelas;
- regra de cópia para `/mnt/data`.

Observação: existe bloco `saidas.*` e `exportacao.*` no config, mas a planilha operacional atual ainda não consome esses blocos.

## Arquivos da pasta `config/` que devem ser preservados nesta etapa

| Arquivo | Status | Justificativa |
|---|---|---|
| `config/carteira_contract_v123.json` | preservar | contrato explícito do ranking da Carteira |
| `config/fixed_parameters_ranking_carteira.json` | preservar | parâmetros fixos do ranking usados por `nucleo/ranking_carteira_estabilizado.py` |

## Arquivos de config legados não encontrados como arquivos reais na raiz/dados

A microetapa anterior removeu a precedência automática dos nomes abaixo no loader. Nesta auditoria, eles permanecem classificados como legados não automáticos:

- `config_atualizado_revisado_v7_populacao_inicial.json`
- `config_atualizado_revisado_v6_avaliacao.json`
- `config_atualizado_revisado_v5_otimizacao_bounds.json`
- `config_atualizado_revisado_v4_otimizacao.json`
- `config_atualizado_revisado_v3_treinamento.json`
- `config_atualizado_revisado_v2.json`

Não houve remoção física nesta etapa.

## Conclusão operacional

1. O config canônico efetivo da baseline V225 é `dados/config_atualizado.json`.
2. O fluxo principal não usa o config diretamente no entrypoint; ele usa objetos do `ContextoBaseline`.
3. Os blocos `abas`, `colunas`, `rede`, `urls`, `google_drive.sheets_file_id`, `execucao`, `premissas_mercado`, `calendario`, `iof`, `ir`, `replay`, `auditoria.limiar_residuo_resolvido`, `defaults_lote` e `triagem_motor` têm consumo real parcial ou direto.
4. Muitos blocos do config global são contratos futuros, documentação operacional ou resíduos de versões anteriores; não devem ser removidos sem uma segunda auditoria por módulo.
5. A pasta `config/` deve ser preservada por enquanto, pois serve ao ranking oficial da Carteira.
6. A próxima limpeza segura deve focar em documentação e inventário, não em remoção.

## Próxima microetapa sugerida

Auditar os parâmetros hardcoded candidatos a migração em apenas um módulo por vez, começando por `scripts/operacional/gerar_planilha_operacional.py`, porque ele afeta somente a camada observável de saída e não altera o motor econômico. O objetivo seria conectar nomes de abas/saídas ao config sem mudar cálculos, replay, pagamentos ou switching.

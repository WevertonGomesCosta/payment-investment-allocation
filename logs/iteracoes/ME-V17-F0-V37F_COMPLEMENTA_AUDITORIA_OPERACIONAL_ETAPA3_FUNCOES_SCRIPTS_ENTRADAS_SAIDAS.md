# ME-V17-F0-V37F — Complementa auditoria operacional da Etapa 3 com funções, scripts, entradas e saídas

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37F
- VERSAO_CANDIDATA: V17-F0-V.3.7F
- TIPO: DOCUMENTAL / AUDITORIA OPERACIONAL / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: COMPLEMENTA_AUDITORIA_OPERACIONAL_ETAPA3_FUNCOES_SCRIPTS_ENTRADAS_SAIDAS
- BASELINE_DE_ENTRADA: V17-F0-V.3.7E
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após:

```text
e041b5b — V17-F0-V.3.7E: audita sequencia etapa1 etapa3 fluxograma canonico
```

A V3.7E é válida como auditoria arquitetural geral, mas foi classificada como insuficiente para o mesmo nível de detalhamento operacional usado nas Etapas 1 e 2.

A presente V3.7F complementa a V3.7E com:

- funções necessárias por camada;
- scripts diagnósticos associados;
- entradas formais;
- saídas formais;
- fluxograma operacional no padrão de Etapa 1 e Etapa 2;
- pendências antes da especificação contratual V3.7G.

---

## 3. Veredito da auditoria complementar

```text
V3.7E_VALIDA_COMO_AUDITORIA_ARQUITETURAL_GERAL=sim
V3.7E_SUFFICIENTE_COMO_AUDITORIA_OPERACIONAL_EQUIVALENTE_ETAPAS_1_2=não
V3.7F_NECESSARIA=sim
V3.7G_CONTRATUAL_DEVE_AGUARDAR_COMPLEMENTO_OPERACIONAL=sim
```

A V3.7F não corrige código. Ela apenas formaliza a auditoria operacional faltante.

---

## 4. Padrão mínimo herdado das Etapas 1 e 2

As Etapas 1 e 2 foram auditadas com os seguintes quesitos:

1. artefato produzido;
2. funções produtoras;
3. funções auditoras;
4. scripts diagnósticos;
5. entradas formais;
6. saídas formais;
7. fronteiras do que a etapa pode fazer;
8. proibições explícitas;
9. evidência ou gate;
10. fluxo de passagem para a etapa seguinte.

A V3.7F aplica esse mesmo padrão à Etapa 3 e às camadas posteriores.

---

## 5. Etapa 1 — Entrada resolvida

### 5.1. Função da etapa

A Etapa 1 resolve a entrada física e estrutural.

Ela produz um artefato único:

```text
PacoteEntradaResolvida
```

### 5.2. Entradas formais

```text
PacoteConfig
ContextoExecucao
PacotePlanilha
PacoteCacheCDIDiario
metadados
```

### 5.3. Funções e estruturas centrais

| Função / estrutura | Arquivo | Papel |
|---|---|---|
| `PacoteEntradaResolvida` | `nucleo/entrada_resolvida.py` | Artefato único da Etapa 1 |
| `MapaAbasResolvidas` | `nucleo/entrada_resolvida.py` | Mapeia blocos canônicos para abas físicas |
| `MapaColunasResolvidas` | `nucleo/entrada_resolvida.py` | Mapeia campos canônicos para colunas físicas |
| `JanelaConsultaCDI` | `nucleo/entrada_resolvida.py` | Janela bruta da série CDI/BCB |
| `montar_pacote_entrada_resolvida(...)` | `nucleo/entrada_resolvida.py` | Monta o pacote sem reler planilha ou alterar motor |
| `auditar_pacote_entrada_resolvida(...)` | `nucleo/entrada_resolvida.py` | Audita estruturalmente o pacote |

### 5.4. Saídas formais

```text
PacoteEntradaResolvida
AuditoriaPacoteEntradaResolvida
```

### 5.5. Scripts diagnósticos relacionados

| Script / log | Papel |
|---|---|
| `scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py` | Audita integração do pacote no `ContextoBaseline` |
| `logs/iteracoes/ME-V17-F0-V33A_ESTRUTURAS_PACOTE_ENTRADA_RESOLVIDA.md` | Formaliza estruturas do pacote |
| `logs/iteracoes/ME-V17-F0-V33G_MONTA_PACOTE_ENTRADA_RESOLVIDA.md` | Registra montagem do pacote |
| `logs/iteracoes/ME-V17-F0-V33H_AUDITA_PACOTE_ENTRADA_RESOLVIDA.md` | Registra auditoria do pacote |
| `logs/iteracoes/ME-V17-F0-V33I_AUDITORIA_FECHAMENTO_ETAPA1_PACOTE_ENTRADA_RESOLVIDA.md` | Fecha a auditoria da Etapa 1 |

### 5.6. Proibições da Etapa 1

A Etapa 1 não pode:

- criar dados operacionais canônicos;
- executar validação pré-execução;
- decidir pagamento;
- decidir switching;
- executar replay;
- gerar ledger;
- montar saída;
- renderizar console ou XLSX.

---

## 6. Etapa 2 — Validação pré-execução

### 6.1. Função da etapa

A Etapa 2 valida os artefatos produzidos pela Etapa 1 e bloqueia avanço quando houver erro estrutural.

Ela produz:

```text
PacoteValidacaoPreExecucao
```

### 6.2. Entradas formais

Entrada operacional promovida:

```text
PacoteEntradaResolvida
```

Entrada legada preservada apenas como referência shadow:

```text
PacoteConfig
ContextoExecucao
PacotePlanilha
```

### 6.3. Funções e estruturas centrais

| Função / estrutura | Arquivo | Papel |
|---|---|---|
| `PacoteValidacaoPreExecucao` | `nucleo/validacao_pre_execucao.py` | Resultado formal do gate |
| `validar_pre_execucao(...)` | `nucleo/validacao_pre_execucao.py` | Gate legado preservado como shadow |
| `validar_pre_execucao_pacote_entrada_resolvida(...)` | `nucleo/validacao_pre_execucao.py` | Gate operacional por pacote resolvido |

### 6.4. Saídas formais

```text
PacoteValidacaoPreExecucao
```

### 6.5. Scripts diagnósticos relacionados

| Script / log | Papel |
|---|---|
| `scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py` | Compara validação legada, reexecutada e por pacote |
| `scripts/diagnostico/auditar_pos_promocao_gate_etapa2_v35c.py` | Audita pós-promoção do gate da Etapa 2 |
| `logs/iteracoes/ME-V17-F0-V34B_VALIDACAO_PARALELA_PACOTE_ENTRADA_RESOLVIDA.md` | Registra validação paralela |
| `logs/iteracoes/ME-V17-F0-V34C_COMPARA_VALIDACAO_LEGADA_VS_PACOTE_ENTRADA_RESOLVIDA.md` | Registra comparação da validação |
| `logs/iteracoes/ME-V17-F0-V35A_FORMALIZA_PROMOCAO_CONTROLADA_GATE_ETAPA2_PACOTE_ENTRADA_RESOLVIDA.md` | Formaliza promoção do gate |
| `logs/iteracoes/ME-V17-F0-V35D_FECHA_ETAPA2_GATE_PACOTE_ENTRADA_RESOLVIDA.md` | Fecha a Etapa 2 |

### 6.6. Proibições da Etapa 2

A Etapa 2 não pode:

- reler planilha;
- baixar planilha;
- abrir workbook;
- reconstruir aliases;
- criar quadros estruturais;
- carregar ou atualizar cache CDI;
- criar carteira canônica;
- criar gastos, salários, switching ou inventário canônicos;
- executar replay;
- gerar ledger;
- montar saída;
- renderizar console ou XLSX.

---

## 7. Etapa 3 — Canonização operacional

### 7.1. Função normativa da etapa

A Etapa 3 deve transformar entrada resolvida e validada em artefatos operacionais canônicos.

Ela deve produzir:

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
```

### 7.2. Entradas normativas desejadas

```text
PacoteEntradaResolvida
PacoteValidacaoPreExecucao aprovado
```

### 7.3. Entradas transitórias ainda observadas no código

```text
PacotePlanilha
config
data_referencia
carteira_canonica
```

Essas entradas transitórias ainda aparecem porque a Etapa 3 nasceu antes da promoção plena do `PacoteEntradaResolvida` como insumo operacional.

### 7.4. Estrutura central existente

| Estrutura | Arquivo | Papel |
|---|---|---|
| `PacoteDadosOperacionaisCanonicos` | `nucleo/dados_operacionais_canonicos.py` | Pacote operacional canônico atual |

Campos principais já presentes:

```text
inventario_canonico
gastos_canonicos
salarios_canonicos
switching_canonico
inventario_lotes_expandido
lotes_pos_switching_normalizados
auditoria_inventario
auditoria_gastos
auditoria_salarios
auditoria_switching
auditoria_inventario_expandido
```

### 7.5. Funções centrais existentes

| Função | Arquivo | Entrada atual | Saída atual |
|---|---|---|---|
| `carregar_inventario_canonico(...)` | `nucleo/dados_operacionais_canonicos.py` | `PacotePlanilha`, config, data, carteira | inventário canônico base + auditoria |
| `carregar_gastos_canonicos(...)` | `nucleo/dados_operacionais_canonicos.py` | `PacotePlanilha`, config, data | gastos canônicos + auditoria |
| `carregar_salarios_canonicos(...)` | `nucleo/dados_operacionais_canonicos.py` | `PacotePlanilha`, config, data | salários canônicos + auditoria |
| `carregar_switching_canonico(...)` | `nucleo/dados_operacionais_canonicos.py` | `PacotePlanilha`, config, data | switching canônico + auditoria |
| `normalizar_lotes_pos_switching_para_schema_inventario(...)` | `nucleo/inventario_lotes_expandido_pos_switching.py` | switching canônico, config, data, carteira | lotes POS normalizados |
| `construir_inventario_lotes_expandido(...)` | `nucleo/inventario_lotes_expandido_pos_switching.py` | inventário base + lotes POS | inventário operacional expandido |
| `carregar_dados_operacionais_canonicos(...)` | `nucleo/dados_operacionais_canonicos.py` | planilha, config, data, carteira | `PacoteDadosOperacionaisCanonicos` |

### 7.6. Saídas formais atuais

```text
PacoteDadosOperacionaisCanonicos
inventario_canonico
gastos_canonicos
salarios_canonicos
switching_canonico
inventario_lotes_expandido
lotes_pos_switching_normalizados
auditorias canônicas
```

### 7.7. Saídas formais ainda pendentes

```text
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional
contrato explícito de origens migradas
contrato explícito de POS canônicos
contrato explícito de inventário base vs inventário completo
```

### 7.8. Proibições da Etapa 3

A Etapa 3 não pode:

- executar pagamentos futuros;
- decidir switching futuro;
- executar replay passado;
- gerar ledger temporal completo;
- corrigir consumo histórico;
- montar saída canônica;
- renderizar console ou XLSX.

### 7.9. Achado crítico da auditoria

O `ContextoBaseline` ainda executa parte da Etapa 3 antes de montar formalmente o `PacoteEntradaResolvida` como artefato operacional.

Fluxo real observado:

```text
carregar_planilha(...)
validar_pre_execucao(...) [legado shadow]
carregar_carteira_canonica(...)
carregar_dados_operacionais_canonicos(...)
carregar_cache_cdi_diario(...)
montar_pacote_entrada_resolvida(...)
auditar_pacote_entrada_resolvida(...)
validar_pre_execucao_pacote_entrada_resolvida(...)
```

Classificação:

```text
inversão transitória de orquestração
```

Essa inversão não invalida o estado atual, mas deve ser tratada na rota de migração futura. O contrato mínimo da V3.7G deve registrar que a Etapa 3 normativa deve consumir `PacoteEntradaResolvida` já validado, e não depender primariamente de `PacotePlanilha` e config soltos.

---

## 8. Replay passado

### 8.1. Função normativa

O replay passado deve consumir artefatos canônicos e fatos históricos para reconstruir consumo, saques, exaustões, saldos e eventos observados.

### 8.2. Entradas atuais observadas

```text
PacoteDadosOperacionaisCanonicos
nucleo_financeiro
calendario_financeiro
config
data_referencia
serie_cdi
```

### 8.3. Funções atuais

| Função | Arquivo | Papel |
|---|---|---|
| `carregar_replay_passado_controlado(...)` | `nucleo/replay_passado_controlado.py` | Carrega replay passado controlado |

### 8.4. Saídas esperadas

```text
PacoteReplayPassado
eventos_passados
saques_por_lote
lotes_exauridos_por_saque
saldos_pos_replay
auditorias_de_replay
```

### 8.5. Proibições

Replay não deve:

- resolver planilha;
- criar artefatos canônicos da Etapa 3;
- decidir switching futuro;
- renderizar saída;
- corrigir logs ou contratos.

---

## 9. Ledger temporal

### 9.1. Função normativa

O ledger temporal deve consolidar eventos por data, saldos, vencimentos, pagamentos futuros e estado temporal auditável.

### 9.2. Entradas atuais observadas

```text
quadro_futuro
mapa_central
contexto
```

### 9.3. Funções atuais relevantes

| Função | Arquivo | Papel |
|---|---|---|
| `construir_ledger_temporal_conjunto(...)` | `nucleo/ledger_temporal_conjunto.py` | Constrói ledger temporal conjunto |

### 9.4. Saídas esperadas

```text
PacoteLedgerTemporal
estado_temporal_por_data
eventos_temporais
saldos_por_lote
vencimentos
pagamentos_futuros
alertas_temporais
```

### 9.5. Achado crítico

A V3.7B já identificou que `construir_saida_canonica(...)` ainda chama o ledger. Esse é um acoplamento a migrar.

Regra futura:

```text
Saída canônica deve receber ledger pronto, não disparar ledger.
```

---

## 10. Saída canônica

### 10.1. Função normativa

A saída canônica deve consumir artefatos já produzidos e montar o `PacoteSaidaCanonica`.

### 10.2. Entradas esperadas

```text
PacoteDadosOperacionaisCanonicos
PacoteReplayPassado
PacoteLedgerTemporal
auditorias canônicas
contexto de execução
```

### 10.3. Funções atuais relevantes

| Função | Arquivo | Papel |
|---|---|---|
| `construir_saida_canonica(...)` | `nucleo/saida_canonica.py` | Monta pacote de saída |
| `_aplicar_consumo_pagamentos_passados_lotes_pos_switching(...)` | `nucleo/saida_canonica.py` | Contenção temporal ainda indevidamente na saída |
| `_neutralizar_origens_migradas_situacao(...)` | `nucleo/saida_canonica.py` | Contenção observável/canônica transitória |
| `_pos_canonico_ativo(...)` | `nucleo/saida_canonica.py` | Detecção de POS canônico ativo |

### 10.4. Saída formal

```text
PacoteSaidaCanonica
```

### 10.5. Proibições futuras

A saída canônica não deve:

- criar estado patrimonial novo;
- neutralizar origem migrada por regra própria;
- aplicar consumo passado;
- disparar ledger;
- decidir POS canônico;
- corrigir inconsistência temporal ou canônica.

---

## 11. Saída observável, console e XLSX

### 11.1. Função normativa

A saída observável deve formatar e apresentar os artefatos já produzidos.

### 11.2. Entradas esperadas

```text
PacoteSaidaCanonica
ContextoBaseline
```

### 11.3. Funções atuais relevantes

| Função | Arquivo | Papel |
|---|---|---|
| `construir_linhas_lotes_id_curta(...)` | `nucleo/saida_observavel.py` | Monta tabela curta de identificação |
| `construir_linhas_lotes_valores_curta(...)` | `nucleo/saida_observavel.py` | Monta tabela curta de valores |
| `construir_resumo_patrimonio_total_lotes(...)` | `nucleo/saida_observavel.py` | Monta resumo patrimonial observável |
| `aplicacao/principal.py` | aplicação | Orquestra execução e impressão final |

### 11.4. Saídas

```text
console operacional
relatorio_operacional_v225.xlsx
```

### 11.5. Proibições

Saída observável, console e XLSX não devem:

- alterar regra econômica;
- criar ou remover lote canônico;
- alterar replay;
- alterar ledger;
- alterar motor;
- alterar dados.

---

## 12. Fluxograma operacional com funções, entradas e saídas

```text
[Configuração e ambiente]
  Funções:
    carregar_config(...)
    bootstrap_ambiente(...)
    construir_calendario_financeiro(...)
  Entradas:
    config local
    raiz_repositorio
    data_referencia
  Saídas:
    PacoteConfig
    ContextoExecucao
    calendario_financeiro
        |
        v
[Etapa 1 — Entrada resolvida]
  Funções:
    carregar_planilha(...)
    carregar_cache_cdi_diario(...)
    montar_pacote_entrada_resolvida(...)
    auditar_pacote_entrada_resolvida(...)
  Entradas:
    PacoteConfig
    ContextoExecucao
    PacotePlanilha
    PacoteCacheCDIDiario
  Saídas:
    PacoteEntradaResolvida
    AuditoriaPacoteEntradaResolvida
        |
        v
[Etapa 2 — Validação pré-execução]
  Funções:
    validar_pre_execucao_pacote_entrada_resolvida(...)
    validar_pre_execucao(...) [shadow legado]
  Entradas:
    PacoteEntradaResolvida
  Saídas:
    PacoteValidacaoPreExecucao
        |
        v
[Etapa 3 — Canonização operacional]
  Funções atuais:
    carregar_carteira_canonica(...)
    carregar_inventario_canonico(...)
    carregar_gastos_canonicos(...)
    carregar_salarios_canonicos(...)
    carregar_switching_canonico(...)
    normalizar_lotes_pos_switching_para_schema_inventario(...)
    construir_inventario_lotes_expandido(...)
    carregar_dados_operacionais_canonicos(...)
  Entradas normativas:
    PacoteEntradaResolvida validado
    PacoteValidacaoPreExecucao aprovado
  Entradas transitórias atuais:
    PacotePlanilha
    config
    data_referencia
    carteira_canonica
  Saídas:
    PacoteDadosOperacionaisCanonicos
    UniversoEconomicoCanonico [pendente de contrato explícito]
    auditorias_canonicas
        |
        v
[Replay passado]
  Funções atuais:
    carregar_replay_passado_controlado(...)
  Entradas:
    PacoteDadosOperacionaisCanonicos
    nucleo_financeiro
    calendario_financeiro
    config
    data_referencia
    serie_cdi
  Saídas esperadas:
    PacoteReplayPassado
    eventos_passados
    saques_por_lote
    saldos_pos_replay
        |
        v
[Ledger temporal]
  Funções atuais:
    construir_ledger_temporal_conjunto(...)
  Entradas atuais:
    quadro_futuro
    mapa_central
    contexto
  Saídas esperadas:
    PacoteLedgerTemporal
    estado_temporal_por_data
    eventos_temporais
    saldos_por_lote
        |
        v
[Saída canônica]
  Funções atuais:
    construir_saida_canonica(...)
  Entradas esperadas:
    PacoteDadosOperacionaisCanonicos
    PacoteReplayPassado
    PacoteLedgerTemporal
    auditorias
  Saídas:
    PacoteSaidaCanonica
        |
        v
[Saída observável / console / XLSX]
  Funções:
    construir_linhas_lotes_id_curta(...)
    construir_linhas_lotes_valores_curta(...)
    construir_resumo_patrimonio_total_lotes(...)
    aplicacao/principal.py
  Entradas:
    PacoteSaidaCanonica
    ContextoBaseline
  Saídas:
    console operacional
    relatorio_operacional_v225.xlsx
```

---

## 13. Critérios de validação antes da V3.7G

A V3.7G contratual só deve avançar se aceitar estes critérios como base:

1. Etapa 1 é produtora de `PacoteEntradaResolvida`.
2. Etapa 2 é gate por `PacoteValidacaoPreExecucao`.
3. Etapa 3 deve consumir entrada validada, mesmo que o código ainda tenha transição via `PacotePlanilha`.
4. `PacoteDadosOperacionaisCanonicos` é o artefato atual da Etapa 3.
5. `UniversoEconomicoCanonico` ainda precisa de contrato explícito.
6. Replay e ledger devem ganhar pacotes explícitos antes de migração de código.
7. `saida_canonica.py` ainda contém responsabilidades transitórias que não devem ser expandidas.
8. `saida_observavel.py` pode conter filtros de apresentação, mas não regra econômica.

---

## 14. Decisão de rota após V3.7F

A V3.7F conclui que a próxima microetapa deve ser:

```text
V17-F0-V.3.7G — Especifica contratos mínimos entre Etapa 3, replay, ledger e saída canônica
```

Tipo:

```text
DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
```

A V3.7G deve especificar contratos mínimos para:

- `PacoteDadosOperacionaisCanonicos`;
- `UniversoEconomicoCanonico`;
- `PacoteReplayPassado`;
- `PacoteLedgerTemporal`;
- `PacoteSaidaCanonica`;
- fronteira entre saída canônica e saída observável.

---

## 15. Conclusão

A V3.7F complementa a V3.7E e fecha a lacuna operacional da auditoria.

A Etapa 3 já possui artefato operacional parcial e funções produtoras reais, mas ainda não está normativamente contratada para consumir apenas `PacoteEntradaResolvida` validado.

A próxima ação correta é especificar contratos mínimos, sem código, na V3.7G.

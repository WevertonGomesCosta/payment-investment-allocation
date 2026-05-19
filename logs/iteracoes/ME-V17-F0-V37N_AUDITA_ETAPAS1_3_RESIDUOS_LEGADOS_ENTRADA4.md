# ME-V17-F0-V37N — Audita Etapas 1–3, resíduos legados e coerência para entrada da Etapa 4

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37N
- VERSAO_CANDIDATA: V17-F0-V.3.7N
- TIPO: DOCUMENTAL / AUDITORIA ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_ETAPAS1_3_RESIDUOS_LEGADOS_ENTRADA4
- BASELINE_DE_ENTRADA: 4798b3d — Atualiza cache BCB
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Auditar o estado consolidado das Etapas 1, 2 e 3 após a aprovação da V3.7M.1 e atualização do cache BCB, verificando:

1. se a Etapa 1 ainda possui resíduo legado;
2. se esse resíduo é consumido por alguma etapa posterior à Etapa 3;
3. se o fluxo Etapa 1 → Etapa 2 → Etapa 3 permanece funcional;
4. se a saída da Etapa 3 está coerente para alimentar a Etapa 4;
5. quais bloqueios arquiteturais ainda permanecem antes de promover contratos mais puros.

---

## 3. Estado remoto auditado

Baseline consolidada:

```text
4798b3d — Atualiza cache BCB
```

O `main` remoto estava idêntico a essa baseline no início desta auditoria.

---

## 4. Auditoria da Etapa 1 — Entrada resolvida

### 4.1. Artefato principal

A Etapa 1 possui o artefato formal:

```text
PacoteEntradaResolvida
```

com componentes:

```text
pacote_config
contexto_execucao
pacote_planilha
mapa_abas_resolvidas
mapa_colunas_resolvidas
quadros_brutos
quadros_estruturais_resolvidos
janela_consulta_cdi
pacote_cache_cdi
auditorias de entrada, resolução e cache
```

### 4.2. Resíduos legados detectados na Etapa 1

A Etapa 1 ainda preserva resíduos de transição:

```text
pacote_planilha
quadros_brutos
fallback para quadros_canonicos quando quadros_estruturais_resolvidos não existe
```

Esses itens são resíduos porque mantêm objetos e nomes oriundos da arquitetura anterior de leitura/planilha dentro do artefato formal novo.

### 4.3. Classificação do resíduo da Etapa 1

```text
RESIDUO_LEGADO_ETAPA1=sim
TIPO=estrutural/transicional
BLOQUEIA_FUNCIONALIDADE_ATUAL=nao
BLOQUEIA_PROMOCAO_ARQUITETURAL_PLENA=sim
```

O resíduo é aceitável no estado atual porque a Etapa 1 está funcionando como envelope formal, mas ainda não substituiu plenamente os produtores físicos legados.

---

## 5. Auditoria da Etapa 2 — Validação pré-execução

A Etapa 2 já possui gate por `PacoteEntradaResolvida`:

```text
validar_pre_execucao_pacote_entrada_resolvida(...)
```

A função declara explicitamente que:

```text
não baixa planilha
não abre workbook
não resolve aliases
não reconstrói mapas
não carrega cache BCB
não cria dados operacionais canônicos
não executa motor
não gera saída
```

A validação usa o pacote da Etapa 1, confere mapas, quadros estruturais, janela CDI, cache CDI e auditorias de entrada.

### 5.1. Status da Etapa 2

```text
ETAPA2_GATE_PACOTE_ENTRADA_RESOLVIDA=funcional
ETAPA2_CRIA_DADOS_CANONICOS=nao
ETAPA2_EXECUTA_MOTOR=nao
ETAPA2_GERA_SAIDA=nao
```

---

## 6. Auditoria da Etapa 3 — Canonização operacional

A Etapa 3 ainda recebe:

```text
pacote_planilha
config
data_referencia
carteira_canonica opcional
```

por meio de:

```text
carregar_dados_operacionais_canonicos(...)
```

Ela produz:

```text
PacoteDadosOperacionaisCanonicos
```

com:

```text
inventario_canonico
gastos_canonicos
salarios_canonicos
switching_canonico
inventario_lotes_expandido
lotes_pos_switching_normalizados
auditorias correspondentes
```

### 6.1. POS switching

A Etapa 3 já normaliza lotes POS switching e integra o inventário operacional expandido:

```text
normalizar_lotes_pos_switching_para_schema_inventario(...)
construir_inventario_lotes_expandido(...)
```

### 6.2. Auditoria de risco de dupla contagem

A auditoria da Etapa 3 registra explicitamente:

```text
qtd_lotes_destino_switching_integrados
qtd_lotes_inventario_canonico_operacional
qtd_lotes_origem_switching_distintos
qtd_lotes_origem_switching_encontrados_no_inventario
qtd_lotes_origem_switching_potencialmente_ativos
risco_dupla_contagem_origem_switching
neutralizacao_temporal_origem_switching=nao_realizada_nesta_microetapa
```

Esse ponto confirma que a Etapa 3 já produz o inventário operacional expandido, mas ainda reconhece que neutralizações temporais finais pertencem ao replay/ledger.

### 6.3. Status da Etapa 3

```text
ETAPA3_FUNCIONAL=sim
ETAPA3_PRODUZ_PACOTE_DADOS_OPERACIONAIS_CANONICOS=sim
ETAPA3_POS_SWITCHING_INTEGRADO=sim
ETAPA3_TOTALMENTE_DESACOPLADA_DO_PACOTE_PLANILHA=nao
```

---

## 7. Fluxo real do ContextoBaseline

O fluxo atual ainda possui inversão transitória:

```text
carregar_planilha
validar_pre_execucao legado shadow
carregar_carteira_canonica
carregar_dados_operacionais_canonicos
materializar_recebidos_auditaveis
carregar_cache_cdi_diario
montar_pacote_entrada_resolvida
auditar_pacote_entrada_resolvida
validar_pre_execucao_pacote_entrada_resolvida
```

Ou seja, `dados_operacionais` ainda é carregado antes do `PacoteEntradaResolvida` ser montado e validado formalmente.

### 7.1. Classificação

```text
INVERSAO_TRANSITORIA_CONTEXTO_BASELINE=sim
BLOQUEIA_EXECUCAO_ATUAL=nao
BLOQUEIA_ARQUITETURA_FINAL_ETAPA1_ETAPA3=sim
```

A arquitetura final ainda deve fazer a Etapa 3 consumir formalmente o `PacoteEntradaResolvida` validado pela Etapa 2.

---

## 8. Consumo de resíduos da Etapa 1 após a Etapa 3

### 8.1. Consumo direto detectado no ledger

O ledger temporal ainda consome resíduos de planilha bruta:

```text
contexto.pacote_planilha.quadros_brutos['Switching']
```

em funções como:

```text
_mapa_switchings_aba_operacional(...)
_eventos_switching_aba_operacional(...)
```

Também existe fallback para:

```text
pd.read_excel(..., sheet_name='Switching')
```

quando o quadro bruto não está disponível.

### 8.2. Interpretação

```text
RESIDUO_ETAPA1_CONSUMIDO_APOS_ETAPA3=sim
CONSUMIDOR_PRINCIPAL=ledger_temporal_conjunto
CAMADA=posterior_a_Etapa3
RISCO=medio
```

Esse é o resíduo mais importante ainda vivo: o ledger posterior à Etapa 3 ainda depende de planilha bruta/aba Switching em vez de consumir exclusivamente `switching_canonico`, `inventario_canonico`, `inventario_lotes_expandido` ou `PacoteLedgerTemporal`.

### 8.3. Consumo indireto na saída

A saída canônica ainda chama diretamente:

```text
construir_ledger_temporal_conjunto(...)
```

Logo, a saída herda indiretamente esse resíduo do ledger. A V3.7M conectou o `PacoteLedgerTemporal` apenas como shadow opcional, sem remover a ponte legada.

---

## 9. Funcionalidade consolidada até agora

As evidências runtime recentes aprovadas sustentam que o fluxo atual está funcional:

### 9.1. Ledger shadow equivalente

A V3.7L.2 registrou:

```text
validacao_ok=True
qtd_eventos_legado=158
qtd_eventos_shadow=158
qtd_fifo_legado=2844
qtd_fifo_shadow=2844
equivalente_eventos=True
equivalente_fifo=True
equivalente_pagamento_ids=True
equivalente_status=True
equivalente_motivo=True
equivalente_saldos=True
```

### 9.2. Saída canônica com ledger shadow opcional

A V3.7M.1 registrou, com shadow ligado:

```text
ligado_extrato_passado_identico=True
ligado_extrato_futuro_identico=True
ligado_lotes_ativos_identico=True
ligado_lotes_exauridos_identico=True
ligado_recebidos_atuais_identico=True
ligado_fechamento_atual_identico=True
ligado_resumo_recebidos_identico=True
ligado_auditoria_sem_bloco_shadow_identica=True
ligado_bloco_shadow_presente=True
ligado_bloco_shadow_validacao_ok=True
ligado_bloco_shadow_equivalente_eventos=True
ligado_bloco_shadow_equivalente_fifo=True
ligado_qtd_eventos_temporais_shadow=158
ligado_qtd_fifo_candidatos_shadow=2844
```

### 9.3. Status funcional

```text
FLUXO_ATUAL_FUNCIONAL=sim
SAIDA_OBSERVAVEL_ESTAVEL=sim
PACOTE_LEDGER_TEMPORAL_SHADOW_VALIDADO=sim
CONEXAO_SHADOW_SAIDA_CANONICA_VALIDADA=sim
```

---

## 10. Coerência da saída da Etapa 3 para entrada da Etapa 4

### 10.1. Coerência operacional

A Etapa 3 produz insumos suficientes para a Etapa 4 atual:

```text
inventario_canonico operacional
inventario_lotes_expandido
lotes_pos_switching_normalizados
gastos_canonicos
salarios_canonicos
switching_canonico
auditorias estruturais
```

Esses artefatos são coerentes para alimentar replay, fontes elegíveis, saldo disponível, decisão local e ledger.

### 10.2. Coerência arquitetural incompleta

Apesar da coerência operacional, a fronteira Etapa 3 → Etapa 4 ainda não está pura, porque a Etapa 4/ledger ainda consulta:

```text
contexto.pacote_planilha.quadros_brutos['Switching']
```

em vez de consumir apenas os artefatos canônicos da Etapa 3.

### 10.3. Veredito

```text
SAIDA_ETAPA3_COERENTE_PARA_ENTRADA_ETAPA4=sim_operacionalmente
SAIDA_ETAPA3_ARQUITETURALMENTE_SUFFICIENTE_PARA_ETAPA4_PURA=nao_ainda
```

---

## 11. Riscos e bloqueios atuais

### 11.1. Resíduo crítico

```text
ledger_temporal_conjunto ainda lê aba Switching bruta
```

Esse resíduo deve ser removido somente após o `PacoteLedgerTemporal` se tornar a ponte oficial entre ledger e saída.

### 11.2. Inversão ContextoBaseline

```text
carregar_dados_operacionais_canonicos ainda roda antes da validação formal do PacoteEntradaResolvida
```

Isso deve ser corrigido em uma frente futura de reorganização do fluxo Etapa 1 → Etapa 2 → Etapa 3.

### 11.3. Bug opcional no benchmark agrupado/individual

A execução anterior identificou que `carregar_benchmark_agrupado_individual_shadow(...)` é chamado em `contexto_baseline.py` sem o argumento `saldo_disponivel_geral`, gerando:

```text
TypeError: missing 1 required positional argument: 'config'
```

Os scripts diagnósticos recentes contornam esse problema com:

```text
incluir_benchmark_agrupado_individual_shadow=False
```

O `aplicacao/principal.py` também desativa esse benchmark no carregamento principal, portanto o console/planilha principal não está bloqueado por esse bug.

### 11.4. Classificação do bug

```text
BUG_CONTEXTO_BASELINE_BENCHMARK_AGRUPADO=sim
AFETA_FLUXO_PRINCIPAL_ATUAL=nao
AFETA_CONTEXTOS_DIAGNOSTICOS_COM_DEFAULTS=sim
RECOMENDA_MICROCORRECAO_FUTURA=sim
```

---

## 12. Decisão da auditoria

```text
ETAPA1_FUNCIONAL=sim
ETAPA1_COM_RESIDUO_LEGADO=sim
RESIDUO_ETAPA1_CONSUMIDO_APOS_ETAPA3=sim
ETAPA2_FUNCIONAL=sim
ETAPA3_FUNCIONAL=sim
ETAPA3_COERENTE_PARA_ETAPA4_ATUAL=sim
ETAPA3_SUFICIENTE_PARA_ETAPA4_ARQUITETURALMENTE_PURA=nao
SAIDA_CANONICA_ESTAVEL_APOS_V37M=sim
MICROCORRECAO_IMEDIATA_OBRIGATORIA=nao
MIGRACAO_ARQUITETURAL_FUTURA_NECESSARIA=sim
```

---

## 13. Próximas microetapas recomendadas

### 13.1. Próxima microetapa mais segura

```text
V17-F0-V.3.7O — Especifica substituição do consumo bruto de Switching no ledger por switching_canonico
```

Tipo:

```text
DOCUMENTAL / CONTRATO DE MIGRAÇÃO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Definir como _mapa_switchings_aba_operacional(...) e _eventos_switching_aba_operacional(...) devem deixar de ler contexto.pacote_planilha.quadros_brutos['Switching'] e passar a consumir contexto.dados_operacionais.switching_canonico, preservando equivalência runtime.
```

### 13.2. Alternativa executável posterior

```text
V17-F0-V.3.7P — Implementa adaptador switching_canonico_para_ledger_shadow
```

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Criar uma ponte shadow entre switching_canonico da Etapa 3 e os mapas/eventos esperados pelo ledger legado, comparando saída com o caminho atual baseado na aba Switching bruta.
```

### 13.3. Microcorreção opcional separada

```text
V17-F0-V.3.7O-b — Corrige assinatura do benchmark agrupado/individual no ContextoBaseline
```

Tipo:

```text
EXECUTÁVEL / MICROCORREÇÃO DE ORQUESTRAÇÃO / SEM ALTERAÇÃO DE SAÍDA
```

Objetivo:

```text
Corrigir a chamada de carregar_benchmark_agrupado_individual_shadow(...) adicionando saldo_disponivel_geral na posição correta, sem alterar Etapas 1–3 nem saída.
```

---

## 14. Conclusão

O conjunto Etapa 1 → Etapa 2 → Etapa 3 está funcional e coerente para alimentar a Etapa 4 atual.

Entretanto, a arquitetura ainda não está pura: há resíduo legado da Etapa 1 preservado no contexto e consumido diretamente pelo ledger posterior à Etapa 3, sobretudo pela leitura da aba bruta `Switching`.

A próxima frente tecnicamente correta não é alterar a saída canônica, mas preparar a migração controlada do ledger para consumir `switching_canonico` da Etapa 3 em modo shadow, mantendo equivalência com o caminho legado antes de qualquer promoção.

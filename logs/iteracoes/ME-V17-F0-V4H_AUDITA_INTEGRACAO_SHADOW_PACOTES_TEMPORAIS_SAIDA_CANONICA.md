# ME-V17-F0-V4H — Audita integração shadow dos pacotes temporais com a saída canônica

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4H
- VERSAO_CANDIDATA: V17-F0-V.4H
- TIPO: DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_INTEGRACAO_SHADOW_PACOTES_TEMPORAIS_SAIDA_CANONICA
- BASELINE_DE_ENTRADA: V17-F0-V.4G.1
- BASELINE_COMMIT_ENTRADA: 2e6edf79e89bbc29688bfcd644a986838a36002a
- ALTERA_CODIGO: não
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Mapear exatamente quais partes da saída canônica ainda chamam ou reconstroem replay, ledger, estado temporal e auditorias, preparando a conexão shadow dos pacotes temporais sem alteração observável.

A V4H não implementa integração. Ela define a fronteira de risco e a ordem segura para as próximas microetapas.

---

## 3. Condição de entrada

A V4G.1 validou o `PacoteAuditoriaTemporal` shadow com:

```text
validacao_v4g_ok=True
auditoria_replay_presente=True
auditoria_ledger_presente=True
auditoria_estado_temporal_presente=True
auditoria_fontes_elegiveis_ok=True
auditoria_switching_temporal_ok=True
auditoria_invariantes_ok=True
validacao_temporal_global_ok=True
saida_canonica_identica_dupla_execucao=True
```

A V4G.1 também registrou resíduos ainda existentes:

```text
usa_retorno_ledger_dict_legado=True
saida_chama_ledger_diretamente=sim_fluxo_atual_ainda_transitorio
campos_vazios_auditados=[
  "estado_temporal_por_data",
  "vencimentos_processados",
  "fontes_elegiveis_por_data",
  "vencimentos_por_data",
  "migracoes_por_data"
]
```

---

## 4. Arquivos inspecionados

Foram inspecionados, sem alteração:

```text
nucleo/saida_canonica.py
logs/iteracoes/ME-V17-F0-V4G1_REGISTRA_EQUIVALENCIA_RUNTIME_PACOTE_AUDITORIA_TEMPORAL_SHADOW.md
```

---

## 5. Diagnóstico geral

A saída canônica ainda exerce três papéis misturados:

```text
1. Consumidora de resultados temporais.
2. Orquestradora parcial da Etapa 4.
3. Renderizadora/camada observável oficial.
```

A arquitetura alvo da Etapa 4 exige que a saída canônica deixe, gradualmente, de orquestrar replay/ledger/estado e passe a consumir pacotes temporais validados.

Veredito geral:

```text
SAIDA_CANONICA_CONSOME_ETAPA4=sim
SAIDA_CANONICA_AINDA_ORQUESTRA_ETAPA4=sim
PACOTES_TEMPORAIS_SHADOW_EXISTEM=sim
PACOTES_TEMPORAIS_AINDA_NAO_INTEGRADOS_A_SAIDA=sim
INTEGRACAO_DIRETA_AGORA=nao_recomendada
```

---

## 6. Ponto 1 — Extrato passado

### 6.1. Estado atual

A função:

```text
_construir_extrato_passado(contexto)
```

lê diretamente:

```text
contexto.replay_passado.log_passado
```

Depois agrega por `Despesa ID`, normaliza saldos remanescentes por limiar e ainda inclui pagamentos passados POS ausentes por meio de função auxiliar.

### 6.2. Pacote temporal correspondente

O pacote shadow correspondente já existe:

```text
PacoteReplayPassado.log_movimentos_passados
PacoteReplayPassado.estado_lotes_passado
PacoteReplayPassado.auditoria_replay
```

### 6.3. Lacuna de integração

A saída ainda consome o replay legado diretamente, não o `PacoteReplayPassado` contratual.

Classificação:

```text
FRONTEIRA_EXTRATO_PASSADO_ADERENCIA=parcial
SAIDA_RECONSTRUI_EXTRATO_PASSADO_A_PARTIR_DO_REPLAY_LEGADO=sim
SUBSTITUICAO_SEGURA=possivel_em_modo_shadow
```

### 6.4. Integração recomendada futura

Criar comparação shadow:

```text
extrato_passado_atual
vs
extrato_passado_derivado_de_PacoteReplayPassado
```

Critério de aprovação futura:

```text
extrato_passado_identico=True
qtd_extrato_passado_identica=True
sem_alteracao_console=True
sem_alteracao_xlsx=True
```

---

## 7. Ponto 2 — Extrato futuro

### 7.1. Estado atual

A função:

```text
_construir_extrato_futuro(contexto)
```

faz internamente:

```text
quadro = _quadro_futuro_preferencial(contexto)
mapa_fontes_elegiveis_auditaveis = _mapa_fontes_elegiveis_auditaveis_por_pagamento(contexto)
mapa_central = _mapa_pagamentos_central(contexto)
ledger_result = construir_ledger_temporal_conjunto(quadro, mapa_central, contexto)
eventos_ledger = ledger_result['eventos']
fifo_candidatos_avaliados = ledger_result['fifo_candidatos_avaliados']
```

Depois interpreta evento por evento para montar linhas observáveis do extrato futuro.

### 7.2. Pacote temporal correspondente

O pacote shadow correspondente já existe:

```text
PacoteLedgerTemporalOperacional.eventos_temporais
PacoteLedgerTemporalOperacional.fifo_candidatos_avaliados
PacoteLedgerTemporalOperacional.fontes_elegiveis_por_pagamento
PacoteAuditoriaTemporal.auditoria_ledger
PacoteAuditoriaTemporal.auditoria_fontes_elegiveis
```

### 7.3. Lacuna de integração

A saída ainda chama o ledger diretamente e usa o retorno dict legado como fonte real.

Classificação:

```text
FRONTEIRA_EXTRATO_FUTURO_ADERENCIA=baixa_media
SAIDA_CHAMA_LEDGER_DIRETAMENTE=sim
SAIDA_USA_RETORNO_DICT_LEDGER=sim
PACOTE_LEDGER_OPERACIONAL_AINDA_NAO_CONSUMIDO=sim
```

### 7.4. Integração recomendada futura

Criar rota shadow:

```text
construir_extrato_futuro_atual(contexto)
vs
construir_extrato_futuro_shadow(pacote_ledger_temporal_operacional, pacote_auditoria_temporal)
```

Critério de aprovação futura:

```text
extrato_futuro_identico=True
qtd_eventos_ledger_identica=True
fifo_identico=True
auditoria_saida_identica_ou_acrescida_apenas_bloco_shadow=True
```

---

## 8. Ponto 3 — Situação atual / lotes ativos e exauridos

### 8.1. Estado atual

A função:

```text
_construir_lotes_situacao(contexto, destinos_pos_switching_passivos)
```

usa diretamente:

```text
contexto.replay_passado.lotes_apos_replay
contexto.cache_cdi.serie_cdi
contexto.tabela_iof
contexto.faixas_ir
ledger_result.destinos_pos_switching_materializados_passivos
```

Ela recalcula saldos brutos/líquidos por lote, normaliza exauridos e injeta destinos pós-switching passivos quando necessário.

Depois a saída ainda executa:

```text
_aplicar_consumo_pagamentos_passados_lotes_pos_switching(...)
_construir_origens_migradas_por_switching_auditoria(...)
_neutralizar_origens_migradas_situacao(...)
```

### 8.2. Pacote temporal correspondente

Os pacotes shadow correspondentes são:

```text
PacoteEstadoTemporal.estado_lotes_por_data
PacoteEstadoTemporal.estado_lotes_final
PacoteEstadoTemporal.saldos_por_lote
PacoteEstadoTemporal.migracoes_por_data
PacoteAuditoriaTemporal.auditoria_estado_temporal
PacoteAuditoriaTemporal.auditoria_residuos_legados
```

### 8.3. Lacuna de integração

A situação atual ainda é calculada dentro da saída canônica, não consumida como estado temporal pronto.

Classificação:

```text
FRONTEIRA_SITUACAO_ATUAL_ADERENCIA=baixa
SAIDA_RECALCULA_SALDOS_ATUAIS=sim
SAIDA_NEUTRALIZA_ORIGENS_MIGRADAS=sim
PACOTE_ESTADO_TEMPORAL_AINDA_NAO_CONSUMIDO=sim
```

### 8.4. Integração recomendada futura

Criar shadow comparativo:

```text
lotes_ativos_atual/lotes_exauridos_atual
vs
lotes_ativos_shadow/lotes_exauridos_shadow_derivados_de_PacoteEstadoTemporal
```

Critério de aprovação futura:

```text
lotes_ativos_identico=True
lotes_exauridos_identico=True
resumos_patrimoniais_identicos=True
neutralizacao_origens_migradas_preservada=True
```

---

## 9. Ponto 4 — Auditoria da saída

### 9.1. Estado atual

A função:

```text
construir_saida_canonica(contexto)
```

monta um dicionário `auditoria` com:

```text
contagens da própria saída
fifo_candidatos_avaliados
qtd_eventos_ledger
múltiplas chaves do ledger_result
listas diagnósticas do ledger_result
origens migradas por switching
reconciliações patrimoniais
invariantes do extrato futuro
sombra de divergências contra o ledger
```

### 9.2. Pacote temporal correspondente

O pacote shadow correspondente já existe:

```text
PacoteAuditoriaTemporal
```

### 9.3. Lacuna de integração

A saída ainda centraliza parte da auditoria temporal junto com auditoria observável.

Classificação:

```text
FRONTEIRA_AUDITORIA_TEMPORAL_ADERENCIA=baixa_media
AUDITORIA_TEMPORAL_DISTRIBUIDA_NA_SAIDA=sim
PACOTE_AUDITORIA_TEMPORAL_AINDA_NAO_CONSUMIDO=sim
```

### 9.4. Integração recomendada futura

Criar bloco shadow opcional:

```text
audit_temporal_shadow={...}
```

sem alterar as chaves atuais da auditoria da saída.

Critério de aprovação futura:

```text
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
saida_observavel_identica=True
```

---

## 10. Ponto 5 — Construção principal da saída

### 10.1. Estado atual

`construir_saida_canonica(contexto)` ainda executa, no mesmo fluxo:

```text
_construir_extrato_passado(contexto)
_construir_extrato_futuro(contexto)
_construir_switchings(contexto)
_construir_ranking_amostra(contexto)
_quadro_futuro_preferencial(contexto)
_mapa_pagamentos_central(contexto)
construir_ledger_temporal_conjunto(...)
_construir_lotes_situacao(...)
_aplicar_consumo_pagamentos_passados_lotes_pos_switching(...)
_construir_origens_migradas_por_switching_auditoria(...)
_neutralizar_origens_migradas_situacao(...)
_construir_recebidos_atuais(contexto)
_linhas_fechamento_atual(contexto)
_linhas_resumo_recebidos(contexto)
```

### 10.2. Diagnóstico

A saída canônica ainda é o maior ponto de orquestração pós-Etapa 3.

Classificação:

```text
SAIDA_COMO_ORQUESTRADORA_TEMPORAL=sim
RISCO_DE_MIGRACAO_DIRETA=alto
RECOMENDACAO=integracao_shadow_gradual
```

---

## 11. Matriz de aderência aos pacotes temporais

| Bloco da saída | Fonte atual | Pacote shadow correspondente | Aderência | Próxima ação segura |
|---|---|---|---|---|
| Extrato passado | `contexto.replay_passado.log_passado` | `PacoteReplayPassado` | parcial | comparar shadow sem trocar fonte |
| Extrato futuro | chamada direta ao ledger | `PacoteLedgerTemporalOperacional` | baixa/média | criar rota shadow para extrato futuro |
| Situação atual | replay + cache + ledger_result + filtros da saída | `PacoteEstadoTemporal` | baixa | comparar lotes ativos/exauridos shadow |
| Auditoria temporal | dict da saída + ledger_result + globais internos | `PacoteAuditoriaTemporal` | baixa/média | anexar bloco shadow opcional |
| Console/XLSX | consome `PacoteSaidaCanonica` | sem mudança imediata | n/d | manter intocado |

---

## 12. Ordem segura de integração após V4H

### 12.1. V4I — Cria construtor shadow de pacotes temporais agregados para saída

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Criar um adaptador único que, dado o contexto, constrói PacoteReplayPassado, PacoteLedgerTemporalOperacional, PacoteEstadoTemporal e PacoteAuditoriaTemporal de forma coordenada, sem alterar a saída.
```

Motivo:

```text
Evitar que cada futura comparação da saída reimplemente manualmente a cadeia V4D→V4G.
```

---

### 12.2. V4J — Audita saída canônica contra pacotes temporais agregados em modo shadow

Tipo:

```text
EXECUTÁVEL / DIAGNÓSTICO / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Comparar extrato passado, extrato futuro, lotes ativos, lotes exauridos, resumos patrimoniais e auditoria atual contra os pacotes temporais agregados.
```

Critérios:

```text
extrato_passado_identico=True
extrato_futuro_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
resumo_patrimonial_identico=True
saida_canonica_identica=True
```

---

### 12.3. V4K — Acrescenta bloco shadow temporal à auditoria da saída

Tipo:

```text
EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Adicionar bloco opcional de auditoria temporal shadow ao `PacoteSaidaCanonica.auditoria`, preservando integralmente as saídas observáveis.
```

Critério:

```text
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
console_xlsx_identicos=True
```

---

### 12.4. V4L — Promove consumo shadow validado do extrato passado

Tipo:

```text
EXECUTÁVEL / PROMOÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Fazer o extrato passado consumir `PacoteReplayPassado` validado em vez de `contexto.replay_passado.log_passado` diretamente.
```

---

### 12.5. V4M — Promove consumo shadow validado do extrato futuro

Tipo:

```text
EXECUTÁVEL / PROMOÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Fazer o extrato futuro consumir `PacoteLedgerTemporalOperacional` validado em vez de chamar diretamente o ledger.
```

---

### 12.6. V4N — Promove consumo shadow validado da situação atual

Tipo:

```text
EXECUTÁVEL / PROMOÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Fazer a situação atual consumir `PacoteEstadoTemporal` validado em vez de recalcular saldos/lotes diretamente dentro da saída.
```

---

## 13. Decisão sobre implementação imediata

A V4H não recomenda substituir nenhuma fonte imediatamente.

Decisão:

```text
SUBSTITUIR_EXTRATO_PASSADO_AGORA=nao
SUBSTITUIR_EXTRATO_FUTURO_AGORA=nao
SUBSTITUIR_SITUACAO_ATUAL_AGORA=nao
ADICIONAR_BLOCO_AUDITORIA_TEMPORAL_AGORA=nao
CRIAR_ADAPTADOR_AGREGADO_TEMPORAL_PRIMEIRO=sim
```

---

## 14. Decisão final

```text
V4H_STATUS=AUDITORIA_INTEGRACAO_SHADOW_CONCLUIDA
SAIDA_CANONICA_AINDA_CHAMA_LEDGER_DIRETAMENTE=sim
SAIDA_CANONICA_AINDA_CONSOME_REPLAY_LEGADO_DIRETAMENTE=sim
SAIDA_CANONICA_AINDA_RECONSTRUI_ESTADO_TEMPORAL=sim
PACOTES_TEMPORAIS_SHADOW_PRONTOS_PARA_AGREGADOR=sim
INTEGRACAO_DIRETA_BLOQUEADA_ATE_COMPARACAO_SHADOW=sim
PROXIMA_MICROETAPA=V17-F0-V.4I
```

---

## 15. Conclusão

A V4H conclui que os pacotes temporais shadow estão prontos para serem agregados e comparados contra a saída, mas ainda não devem substituir diretamente nenhuma fonte operacional.

A próxima etapa segura é criar um adaptador agregado temporal shadow que construa os quatro pacotes temporais de forma coordenada, preservando a saída atual e preparando diagnósticos de equivalência por bloco.

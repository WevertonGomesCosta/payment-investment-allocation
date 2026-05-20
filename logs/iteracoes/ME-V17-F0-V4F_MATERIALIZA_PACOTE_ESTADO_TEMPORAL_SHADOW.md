# ME-V17-F0-V4F — Materializa PacoteEstadoTemporal shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4F
- VERSAO_CANDIDATA: V17-F0-V.4F
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: MATERIALIZA_PACOTE_ESTADO_TEMPORAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4E.1
- BASELINE_COMMIT_ENTRADA: 19dd2cdf519b39adafd522c48e88b66511c08abd
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Materializar `PacoteEstadoTemporal` em modo shadow, consolidando o estado pós-replay e os eventos/saldos/fontes do ledger operacional shadow, sem alterar replay efetivo, ledger efetivo, saída canônica ou saída observável.

---

## 3. Condição de entrada

A V4E.1 validou o `PacoteLedgerTemporalOperacional` shadow com:

```text
validacao_v4e_ok=True
eventos_operacional_mesma_qtd_legado=True
fifo_operacional_identico_shadow=True
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
saida_canonica_identica_dupla_execucao=True
```

A V4E manteve como campos vazios auditados:

```text
estado_temporal_por_data
vencimentos_processados
fontes_elegiveis_por_data
```

A V4F inicia a materialização explícita do estado temporal, usando os pacotes V4D e V4E como fontes shadow.

---

## 4. Arquivos criados

```text
nucleo/pacote_estado_temporal.py
scripts/diagnostico/auditar_pacote_estado_temporal_v4f.py
logs/iteracoes/ME-V17-F0-V4F_MATERIALIZA_PACOTE_ESTADO_TEMPORAL_SHADOW.md
```

---

## 5. Implementação

### 5.1. Novo módulo

Foi criado:

```text
nucleo/pacote_estado_temporal.py
```

com:

```text
PacoteEstadoTemporal
construir_pacote_estado_temporal_shadow(...)
```

O adaptador consome:

```text
PacoteReplayPassado shadow
PacoteLedgerTemporalOperacional shadow
contexto opcional
```

Não executa replay, não executa ledger, não altera estado efetivo e não altera saída.

---

### 5.2. Campos materializados

O pacote materializa:

```text
estado_lotes_por_data
estado_lotes_final
saldos_por_lote
saldos_disponiveis_por_data
fontes_disponiveis_por_data
vencimentos_por_data
migracoes_por_data
auditoria_estado_temporal
validacao_estado_temporal
metadados_origem
```

### 5.3. Fontes usadas

O estado temporal shadow usa:

```text
pacote_replay_passado.estado_lotes_passado
pacote_ledger_operacional.saldos_por_lote
pacote_ledger_operacional.saldos_disponiveis_por_data
pacote_ledger_operacional.fontes_elegiveis_por_pagamento
pacote_ledger_operacional.eventos_temporais
pacote_ledger_operacional.vencimentos_processados
```

---

## 6. Campos ainda esperados como possivelmente vazios

A V4F pode manter como vazios auditados:

```text
vencimentos_por_data
migracoes_por_data
```

A ausência de vencimentos ou migrações materializáveis não deve ser tratada como erro bloqueante nesta microetapa, desde que o estado e os saldos sejam materializados e a saída permaneça idêntica.

---

## 7. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_pacote_estado_temporal_v4f.py
```

O script constrói em sequência:

```text
PacoteReplayPassado shadow
retorno legado do ledger
PacoteLedgerTemporal shadow
PacoteLedgerTemporalOperacional shadow
PacoteEstadoTemporal shadow
```

Depois valida a saída canônica por dupla execução.

Métricas esperadas:

```text
estado_lotes_por_data_total>0
estado_lotes_final_total>0
saldos_por_lote_total>0
fontes_disponiveis_por_data_total>0
usa_pacote_replay_passado_shadow=True
usa_pacote_ledger_temporal_operacional_shadow=True
nao_altera_replay_efetivo=True
nao_altera_ledger_efetivo=True
nao_altera_saida_canonica=True
saida_canonica_identica_dupla_execucao=True
validacao_v4f_ok=True
```

---

## 8. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/pacote_estado_temporal.py
python -m py_compile scripts/diagnostico/auditar_pacote_estado_temporal_v4f.py
python scripts/diagnostico/auditar_pacote_estado_temporal_v4f.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 9. Critérios de aprovação

A V4F só deve ser considerada aprovada se:

```text
validacao_v4f_ok=True
estado_lotes_por_data_total>0
estado_lotes_final_total>0
saldos_por_lote_total>0
fontes_disponiveis_por_data_total>0
saida_canonica_identica_dupla_execucao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 10. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4F.1 — Registra equivalência runtime do PacoteEstadoTemporal shadow
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 11. Próxima microetapa após V4F.1

A próxima etapa arquitetural esperada é:

```text
V17-F0-V.4G — Especifica e materializa PacoteAuditoriaTemporal shadow
```

Tipo sugerido:

```text
DOCUMENTAL + EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Centralizar auditorias de replay, ledger, estado, fontes, switching, invariantes e resíduos legados em um pacote temporal único.
```

---

## 12. Conclusão

A V4F materializa o primeiro `PacoteEstadoTemporal` explícito da Etapa 4. O pacote é shadow e não substitui a execução atual. Ele prepara a futura conexão da saída canônica aos pacotes temporais validados.

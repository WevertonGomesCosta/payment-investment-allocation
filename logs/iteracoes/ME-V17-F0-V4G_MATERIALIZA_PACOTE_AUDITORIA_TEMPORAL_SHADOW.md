# ME-V17-F0-V4G — Especifica e materializa PacoteAuditoriaTemporal shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4G
- VERSAO_CANDIDATA: V17-F0-V.4G
- TIPO: DOCUMENTAL + EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: MATERIALIZA_PACOTE_AUDITORIA_TEMPORAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4F.1 + dados financeiros atualizados
- BASELINE_COMMIT_ENTRADA: 15d483d4cafcd6024e3831acd035991fb6fb7d89
- ALTERA_CODIGO: sim
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

Centralizar auditorias de replay, ledger, estado, fontes, switching, invariantes e resíduos legados em um pacote temporal único, preservando integralmente a execução atual.

---

## 3. Condição de entrada

A V4F.1 validou o `PacoteEstadoTemporal` shadow com:

```text
validacao_v4f_ok=True
estado_lotes_por_data_total=27
estado_lotes_final_total=21
saldos_por_lote_total=9
fontes_disponiveis_por_data_total=112
saida_canonica_identica_dupla_execucao=True
```

Depois, os dados financeiros foram atualizados em commit separado:

```text
15d483d — Atualiza dados financeiros
```

Esse commit alterou apenas:

```text
dados/dados_financeiros.xlsx
```

---

## 4. Arquivos criados

```text
nucleo/pacote_auditoria_temporal.py
scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py
logs/iteracoes/ME-V17-F0-V4G_MATERIALIZA_PACOTE_AUDITORIA_TEMPORAL_SHADOW.md
```

---

## 5. Implementação

### 5.1. Novo módulo

Foi criado:

```text
nucleo/pacote_auditoria_temporal.py
```

com:

```text
PacoteAuditoriaTemporal
construir_pacote_auditoria_temporal_shadow(...)
```

O pacote consome:

```text
PacoteReplayPassado shadow
PacoteLedgerTemporalOperacional shadow
PacoteEstadoTemporal shadow
contexto opcional
```

Não executa replay, não executa ledger, não reprocessa estado e não altera saída.

---

### 5.2. Auditorias centralizadas

O pacote materializa:

```text
auditoria_replay
auditoria_ledger
auditoria_estado_temporal
auditoria_fontes_elegiveis
auditoria_switching_temporal
auditoria_invariantes
auditoria_residuos_legados
validacao_temporal_global
metadados_origem
```

### 5.3. Invariantes auditados

A V4G audita, em modo shadow:

```text
validacao_replay_ok
validacao_ledger_ok
validacao_estado_ok
estado_lotes_por_data_materializado
estado_lotes_final_materializado
switching_canonico_usado_como_fonte_primaria
fallback_switching_bruto_nao_usado_como_fonte_primaria
saida_canonica_nao_recalculada_pelo_pacote_temporal
```

### 5.4. Resíduos legados centralizados

A V4G registra:

```text
usa_contexto_amplo
usa_pacote_planilha
usa_quadros_brutos
usa_planilha_bruta_como_fonte_primaria
usa_planilha_bruta_apenas_fallback
usa_retorno_ledger_dict_legado
saida_chama_ledger_diretamente
campos_vazios_auditados
```

A presença de `saida_chama_ledger_diretamente=sim_fluxo_atual_ainda_transitorio` é esperada nesta fase e deve ser tratada apenas em etapa posterior de conexão da saída aos pacotes temporais.

---

## 6. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py
```

O script constrói em sequência:

```text
PacoteReplayPassado shadow
retorno legado do ledger
PacoteLedgerTemporal shadow
PacoteLedgerTemporalOperacional shadow
PacoteEstadoTemporal shadow
PacoteAuditoriaTemporal shadow
```

Depois valida a saída canônica por dupla execução.

Métricas esperadas:

```text
auditoria_replay_presente=True
auditoria_ledger_presente=True
auditoria_estado_temporal_presente=True
auditoria_fontes_elegiveis_ok=True
auditoria_switching_temporal_ok=True
auditoria_invariantes_ok=True
auditoria_residuos_legados_presente=True
validacao_temporal_global_ok=True
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
estado_lotes_por_data_materializado=True
estado_lotes_final_materializado=True
saida_canonica_identica_dupla_execucao=True
validacao_v4g_ok=True
```

---

## 7. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/pacote_auditoria_temporal.py
python -m py_compile scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py
python scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 8. Critérios de aprovação

A V4G só deve ser considerada aprovada se:

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
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 9. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4G.1 — Registra equivalência runtime do PacoteAuditoriaTemporal shadow
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 10. Próxima microetapa após V4G.1

A próxima etapa arquitetural esperada é:

```text
V17-F0-V.4H — Audita integração shadow dos pacotes temporais com a saída canônica
```

Tipo sugerido:

```text
DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Mapear exatamente quais partes da saída canônica ainda chamam ou reconstroem replay, ledger, estado e auditorias, preparando a conexão shadow dos pacotes temporais sem alteração observável.
```

---

## 11. Conclusão

A V4G materializa o pacote agregador de auditorias temporais da Etapa 4. O pacote é shadow e não substitui nenhuma execução efetiva. Ele consolida auditorias antes dispersas e prepara a futura conexão da saída canônica aos pacotes temporais validados.

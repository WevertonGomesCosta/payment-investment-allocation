# ME-V17-F0-V4E — Normaliza PacoteLedgerTemporalOperacional shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4E
- VERSAO_CANDIDATA: V17-F0-V.4E
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: NORMALIZA_PACOTE_LEDGER_TEMPORAL_OPERACIONAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4D.1 + cache BCB atualizado
- BASELINE_COMMIT_ENTRADA: a7ff78e067037d8d3a84bf31240cda1f4617b55b
- ALTERA_CODIGO: sim
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Normalizar `PacoteLedgerTemporal` para um contrato operacional shadow da Etapa 4, corrigindo metadados pós-V3.7S, adicionando aliases e explicitando campos ausentes como vazios auditados, sem alterar o ledger efetivo nem a saída canônica.

---

## 3. Condição de entrada

A V4D.1 validou o `PacoteReplayPassado` shadow.

O cache BCB foi atualizado em commit separado:

```text
a7ff78e — Atualiza cache BCB
```

Alteração do cache:

```text
inclui fator de 2026-05-19
data_atualizacao=2026-05-20
meta.data_final=2026-05-20
```

---

## 4. Arquivos criados

```text
nucleo/pacote_ledger_temporal_operacional.py
scripts/diagnostico/auditar_pacote_ledger_temporal_operacional_v4e.py
logs/iteracoes/ME-V17-F0-V4E_NORMALIZA_PACOTE_LEDGER_TEMPORAL_OPERACIONAL_SHADOW.md
```

---

## 5. Implementação

### 5.1. Novo módulo

Foi criado:

```text
nucleo/pacote_ledger_temporal_operacional.py
```

com:

```text
PacoteLedgerTemporalOperacional
construir_pacote_ledger_temporal_operacional_shadow(...)
```

O adaptador recebe:

```text
retorno_legado
pacote_shadow V3.7K
contexto opcional
```

e constrói um pacote operacional shadow sem executar decisão econômica nova.

### 5.2. Normalizações adicionadas

O pacote operacional shadow adiciona:

```text
modo_execucao
fontes_elegiveis_por_pagamento
metadados pós-V3.7S
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_switching_auditavel=True
usa_planilha_bruta_como_fonte_primaria=False
usa_planilha_bruta_apenas_fallback=True
usa_switching_canonico_como_fonte_primaria=True
```

### 5.3. Campos ainda vazios auditados

Campos ainda não materializados integralmente são mantidos como vazios auditados:

```text
estado_temporal_por_data
vencimentos_processados
fontes_elegiveis_por_data
```

Esses campos pertencem às próximas etapas da Etapa 4, especialmente materialização do estado temporal.

---

## 6. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_pacote_ledger_temporal_operacional_v4e.py
```

O script compara:

```text
retorno legado do ledger
PacoteLedgerTemporal shadow V3.7K
PacoteLedgerTemporalOperacional shadow V4E
saída canônica em dupla execução
```

Métricas esperadas:

```text
eventos_operacional_mesma_qtd_legado=True
fifo_operacional_identico_shadow=True
pagamentos_futuros_processados_total>0
fontes_elegiveis_por_pagamento_total>0
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_switching_auditavel=True
usa_planilha_bruta_como_fonte_primaria=False
usa_planilha_bruta_apenas_fallback=True
usa_switching_canonico_como_fonte_primaria=True
nao_altera_ledger_efetivo=True
nao_altera_saida_canonica=True
saida_canonica_identica_dupla_execucao=True
validacao_v4e_ok=True
```

---

## 7. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/pacote_ledger_temporal_operacional.py
python -m py_compile scripts/diagnostico/auditar_pacote_ledger_temporal_operacional_v4e.py
python scripts/diagnostico/auditar_pacote_ledger_temporal_operacional_v4e.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 8. Critérios de aprovação

A V4E só deve ser considerada aprovada se:

```text
validacao_v4e_ok=True
eventos_operacional_mesma_qtd_legado=True
fifo_operacional_identico_shadow=True
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
saida_canonica_identica_dupla_execucao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 9. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4E.1 — Registra equivalência runtime do PacoteLedgerTemporalOperacional shadow
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 10. Próxima microetapa após V4E.1

A próxima etapa arquitetural esperada é:

```text
V17-F0-V.4F — Materializa PacoteEstadoTemporal shadow
```

Tipo sugerido:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Consolidar estado pós-replay e eventos do ledger em PacoteEstadoTemporal explícito.
```

---

## 11. Conclusão

A V4E cria um pacote operacional shadow para o ledger temporal, sem substituir a execução atual. Ela corrige a semântica dos metadados após a V3.7S e prepara a materialização futura do estado temporal.

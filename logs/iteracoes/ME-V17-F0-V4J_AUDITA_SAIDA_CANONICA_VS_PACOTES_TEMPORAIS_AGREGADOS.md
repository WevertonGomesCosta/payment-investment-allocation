# ME-V17-F0-V4J — Audita saída canônica contra pacotes temporais agregados em modo shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4J
- VERSAO_CANDIDATA: V17-F0-V.4J
- TIPO: EXECUTÁVEL / DIAGNÓSTICO / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: AUDITA_SAIDA_CANONICA_VS_PACOTES_TEMPORAIS_AGREGADOS_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4I.1
- BASELINE_COMMIT_ENTRADA: 9256083022d1d0c218867c46d9dea64a5c990311
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

Comparar a saída canônica atual contra os pacotes temporais agregados em modo shadow, incluindo:

```text
extrato_passado
extrato_futuro
lotes_ativos
lotes_exauridos
resumos patrimoniais / fechamento atual
auditoria atual
```

A V4J não integra os pacotes temporais à saída e não promove nenhuma fonte operacional. Ela apenas mede aderência e classifica lacunas.

---

## 3. Condição de entrada

A V4I.1 validou o agregador shadow com:

```text
validacao_v4i_ok=True
pacote_replay_passado_presente=True
pacote_ledger_temporal_operacional_presente=True
pacote_estado_temporal_presente=True
pacote_auditoria_temporal_presente=True
eventos_ledger_qtd_equivalente=True
fifo_ledger_qtd_equivalente=True
saida_canonica_identica_dupla_execucao=True
```

Resíduos transitórios ainda esperados:

```text
usa_retorno_ledger_dict_legado=True
saida_chama_ledger_diretamente_fluxo_atual=sim_fluxo_atual_ainda_transitorio
```

---

## 4. Arquivos criados

```text
scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py
logs/iteracoes/ME-V17-F0-V4J_AUDITA_SAIDA_CANONICA_VS_PACOTES_TEMPORAIS_AGREGADOS.md
```

---

## 5. Natureza do diagnóstico

A V4J é uma auditoria de aderência e não um gate de identidade total.

Motivo:

```text
A saída canônica ainda não consome os pacotes temporais como fonte operacional.
Logo, diferenças entre blocos da saída e pacotes temporais podem indicar lacunas de integração shadow, não necessariamente regressão.
```

A validação deve aprovar quando:

```text
saida_canonica_identica_dupla_execucao=True
validacao_agregador_ok=True
erros_bloqueantes_agregador_total=0
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
divergencias_classificadas=True
```

---

## 6. Blocos comparados

### 6.1. Extrato passado

Compara:

```text
PacoteSaidaCanonica.extrato_passado
vs
PacoteReplayPassado.log_movimentos_passados
```

Métricas:

```text
qtd_saida
qtd_pacote
qtd_identica
chaves_intersecao
chaves_apenas_saida
chaves_apenas_pacote
status
```

---

### 6.2. Extrato futuro

Compara:

```text
PacoteSaidaCanonica.extrato_futuro
vs
PacoteLedgerTemporalOperacional.eventos_temporais
vs
PacoteLedgerTemporalOperacional.pagamentos_futuros_processados
```

Métricas:

```text
qtd_saida
qtd_eventos_pacote
qtd_pagamentos_pacote
qtd_identica_eventos
qtd_identica_pagamentos
chaves_intersecao_pagamentos
chaves_apenas_saida
chaves_apenas_pacote
status
```

---

### 6.3. Lotes ativos e exauridos

Compara:

```text
PacoteSaidaCanonica.lotes_ativos + lotes_exauridos
vs
PacoteEstadoTemporal.estado_lotes_final
```

Métricas:

```text
qtd_lotes_ativos_saida
qtd_lotes_exauridos_saida
qtd_lotes_saida_total
qtd_estado_lotes_final
qtd_saldos_por_lote_pacote
lotes_intersecao
lotes_apenas_saida
lotes_apenas_estado
status
```

---

### 6.4. Resumo patrimonial

Compara presença de métricas em:

```text
PacoteSaidaCanonica.fechamento_atual
vs
PacoteEstadoTemporal.estado_lotes_final
```

Nesta microetapa, a comparação é parcial porque o pacote de estado temporal ainda não substitui a lógica patrimonial observável.

---

### 6.5. Auditoria

Compara:

```text
PacoteSaidaCanonica.auditoria
vs
PacoteAuditoriaTemporal
```

Classifica presença, validação temporal global e resíduos.

---

## 7. Classificação de divergências

O script classifica cada bloco como:

```text
identico
shadow_gap
parcial_comparavel
nao_comparavel
```

Interpretação:

| Status | Significado |
|---|---|
| `identico` | bloco já coincide em quantidade/chaves principais |
| `shadow_gap` | há diferença esperada porque a saída ainda não consome o pacote |
| `parcial_comparavel` | há dados suficientes para comparação parcial, mas não para identidade |
| `nao_comparavel` | pacote ou bloco ainda não permite comparação útil |

`shadow_gap` não é erro bloqueante na V4J.

---

## 8. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py
```

O script executa:

```text
1. carregar_contexto_baseline(...)
2. construir_saida_canonica(contexto)
3. construir_pacotes_temporais_agregados_saida_shadow(contexto)
4. construir_saida_canonica(contexto) novamente
5. comparar blocos
6. classificar divergências
```

---

## 9. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py
python scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 10. Critérios de aprovação

A V4J é aprovada se:

```text
validacao_v4j_ok=True
saida_canonica_identica_dupla_execucao=True
validacao_agregador_ok=True
erros_bloqueantes_agregador_total=0
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
divergencias_classificadas=True
```

Não é obrigatório que todos os blocos sejam idênticos nesta etapa.

---

## 11. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4J.1 — Registra diagnóstico runtime da saída canônica contra pacotes temporais agregados
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 12. Próxima microetapa após V4J.1

A depender do diagnóstico runtime, a próxima etapa deve ser uma destas:

```text
V17-F0-V.4K — Acrescenta bloco shadow temporal à auditoria da saída
```

ou, se a V4J mostrar lacuna relevante antes disso:

```text
V17-F0-V.4K0 — Corrige/normaliza comparação shadow da saída antes de integração
```

---

## 13. Conclusão

A V4J cria a primeira auditoria executável comparando a saída canônica atual contra os pacotes temporais agregados da Etapa 4. A microetapa preserva a saída efetiva e mede, de forma explícita, quais blocos já estão aderentes e quais ainda exigem integração shadow gradual.

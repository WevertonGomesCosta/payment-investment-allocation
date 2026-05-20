# ME-V17-F0-V4I — Cria construtor shadow de pacotes temporais agregados para saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4I
- VERSAO_CANDIDATA: V17-F0-V.4I
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: CRIA_CONSTRUTOR_SHADOW_PACOTES_TEMPORAIS_AGREGADOS_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4H
- BASELINE_COMMIT_ENTRADA: 4bfaa82c9385e307685f556ac5f7892085b2c391
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

Criar um adaptador único que, dado o contexto, constrói de forma coordenada:

```text
PacoteReplayPassado
PacoteLedgerTemporalOperacional
PacoteEstadoTemporal
PacoteAuditoriaTemporal
```

sem alterar a saída canônica nem substituir qualquer fluxo efetivo.

---

## 3. Condição de entrada

A V4H concluiu que:

```text
PACOTES_TEMPORAIS_SHADOW_PRONTOS_PARA_AGREGADOR=sim
INTEGRACAO_DIRETA_BLOQUEADA_ATE_COMPARACAO_SHADOW=sim
CRIAR_ADAPTADOR_AGREGADO_TEMPORAL_PRIMEIRO=sim
```

A saída canônica ainda chama o ledger diretamente e ainda consome replay legado diretamente. A V4I não corrige isso; ela cria a infraestrutura shadow coordenada para permitir comparações futuras.

---

## 4. Arquivos criados

```text
nucleo/pacotes_temporais_agregados_saida.py
scripts/diagnostico/auditar_pacotes_temporais_agregados_saida_v4i.py
logs/iteracoes/ME-V17-F0-V4I_CRIA_CONSTRUTOR_SHADOW_PACOTES_TEMPORAIS_AGREGADOS_SAIDA.md
```

---

## 5. Implementação

### 5.1. Novo módulo

Foi criado:

```text
nucleo/pacotes_temporais_agregados_saida.py
```

com:

```text
PacotesTemporaisAgregadosSaida
construir_pacotes_temporais_agregados_saida_shadow(...)
```

### 5.2. Ordem coordenada de construção

O agregador executa a cadeia shadow:

```text
1. PacoteReplayPassado
2. retorno legado do ledger usado apenas como origem shadow
3. PacoteLedgerTemporal shadow V3.7K
4. PacoteLedgerTemporalOperacional
5. PacoteEstadoTemporal
6. PacoteAuditoriaTemporal
7. PacotesTemporaisAgregadosSaida
```

### 5.3. Garantias do adaptador

O agregador declara explicitamente:

```text
nao_altera_contexto=True
nao_altera_replay_efetivo=True
nao_altera_ledger_efetivo=True
nao_altera_estado_temporal_efetivo=True
nao_altera_saida_canonica=True
```

---

## 6. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_pacotes_temporais_agregados_saida_v4i.py
```

O script valida:

```text
presença dos quatro pacotes temporais
validações individuais dos pacotes
equivalência de quantidade de eventos do ledger
equivalência de quantidade de FIFO
materialização do estado temporal
switching_canonico como fonte primária
planilha bruta não usada como fonte primária
saída canônica idêntica em dupla execução
```

Métricas esperadas:

```text
validacao_v4i_ok=True
pacote_replay_passado_presente=True
pacote_ledger_temporal_operacional_presente=True
pacote_estado_temporal_presente=True
pacote_auditoria_temporal_presente=True
validacao_replay_ok=True
validacao_ledger_ok=True
validacao_estado_ok=True
validacao_auditoria_temporal_ok=True
validacao_agregador_ok=True
eventos_ledger_qtd_equivalente=True
fifo_ledger_qtd_equivalente=True
saida_canonica_identica_dupla_execucao=True
```

---

## 7. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/pacotes_temporais_agregados_saida.py
python -m py_compile scripts/diagnostico/auditar_pacotes_temporais_agregados_saida_v4i.py
python scripts/diagnostico/auditar_pacotes_temporais_agregados_saida_v4i.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 8. Critérios de aprovação

A V4I só deve ser considerada aprovada se:

```text
validacao_v4i_ok=True
eventos_ledger_qtd_equivalente=True
fifo_ledger_qtd_equivalente=True
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
saida_canonica_identica_dupla_execucao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 9. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4I.1 — Registra equivalência runtime dos pacotes temporais agregados para saída
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 10. Próxima microetapa após V4I.1

A próxima etapa arquitetural esperada é:

```text
V17-F0-V.4J — Audita saída canônica contra pacotes temporais agregados em modo shadow
```

Tipo sugerido:

```text
EXECUTÁVEL / DIAGNÓSTICO / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Comparar extrato passado, extrato futuro, lotes ativos, lotes exauridos, resumos patrimoniais e auditoria atual contra os pacotes temporais agregados.
```

---

## 11. Conclusão

A V4I cria o ponto único de construção dos pacotes temporais shadow para a saída canônica. A microetapa não integra nem promove consumo desses pacotes pela saída; ela apenas evita duplicação da cadeia V4D→V4G nas próximas auditorias.

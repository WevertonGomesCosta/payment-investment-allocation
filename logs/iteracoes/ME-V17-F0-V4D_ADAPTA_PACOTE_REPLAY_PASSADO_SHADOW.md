# ME-V17-F0-V4D — Adapta PacoteReplayPassado mínimo em modo shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4D
- VERSAO_CANDIDATA: V17-F0-V.4D
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: ADAPTA_PACOTE_REPLAY_PASSADO_MINIMO_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4C
- BASELINE_COMMIT_ENTRADA: 93293c86b3376390467a74c7c46d35f24dffc7ab
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER: não
- ALTERA_ESTADO_TEMPORAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Criar um adaptador shadow de `PacoteReplayPassado` mínimo a partir do `PacoteReplayPassadoControlado` atual, com aliases contratuais, metadados e validação, sem alterar o replay efetivo nem a saída.

---

## 3. Arquivos criados

```text
nucleo/pacote_replay_passado.py
scripts/diagnostico/auditar_pacote_replay_passado_v4d.py
logs/iteracoes/ME-V17-F0-V4D_ADAPTA_PACOTE_REPLAY_PASSADO_SHADOW.md
```

---

## 4. Implementação

### 4.1. Novo módulo

Foi criado:

```text
nucleo/pacote_replay_passado.py
```

com:

```text
PacoteReplayPassado
construir_pacote_replay_passado_shadow(...)
```

O adaptador não executa replay, não altera lotes, não altera contexto e não altera saída canônica.

### 4.2. Aliases contratuais

O adaptador mapeia o replay atual para o contrato V4B:

| Origem atual | Campo contratual V4D |
|---|---|
| `lotes_apos_replay` | `lotes_apos_replay` |
| `log_passado` | `log_movimentos_passados` |
| `estado_lotes_passado` | `estado_lotes_passado` |
| `auditoria` | `auditoria_replay` |
| `validacao` | `validacao_replay` |

Também adiciona:

```text
versao
modo_execucao
data_referencia
audit_trilha_pagamentos_passados
metadados_origem
```

---

## 5. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_pacote_replay_passado_v4d.py
```

O script compara:

```text
replay_passado original
PacoteReplayPassado shadow
saída canônica em dupla execução
```

Métricas esperadas:

```text
lotes_apos_replay_identicos=True
log_movimentos_passados_identico=True
estado_lotes_passado_identico=True
auditoria_replay_presente=True
validacao_replay_presente=True
metadados_origem_presente=True
nao_altera_replay_efetivo=True
nao_altera_saida_canonica=True
saida_canonica_identica_dupla_execucao=True
validacao_v4d_ok=True
```

---

## 6. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile nucleo/pacote_replay_passado.py
python -m py_compile scripts/diagnostico/auditar_pacote_replay_passado_v4d.py
python scripts/diagnostico/auditar_pacote_replay_passado_v4d.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 7. Critérios de aprovação

A V4D só deve ser considerada aprovada se:

```text
validacao_v4d_ok=True
lotes_apos_replay_identicos=True
log_movimentos_passados_identico=True
estado_lotes_passado_identico=True
saida_canonica_identica_dupla_execucao=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 8. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4D.1 — Registra equivalência runtime do PacoteReplayPassado shadow
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 9. Próxima microetapa após V4D.1

A próxima etapa arquitetural esperada permanece:

```text
V17-F0-V.4E — Normaliza PacoteLedgerTemporalOperacional shadow
```

Objetivo:

```text
Normalizar PacoteLedgerTemporal para contrato operacional shadow, corrigindo metadados pós-V3.7S, adicionando aliases e explicitando campos ausentes como vazios auditados.
```

---

## 10. Conclusão

A V4D cria a primeira adaptação executável da Etapa 4 após os contratos V4B e a aderência V4C. O replay efetivo permanece intocado; o novo pacote apenas fornece uma camada shadow contratual para validação e etapas futuras.

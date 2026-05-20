# ME-V17-F0-V4D.1 — Registra equivalência runtime do PacoteReplayPassado shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4D.1
- VERSAO_CANDIDATA: V17-F0-V.4D.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_PACOTE_REPLAY_PASSADO_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4D
- BASELINE_COMMIT_ENTRADA: b45cf8bb65faa6d9d031e7aa09f6c92229a43e66
- ALTERA_CODIGO: não
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

Registrar a evidência runtime local de que o `PacoteReplayPassado` shadow criado na V4D é equivalente ao `PacoteReplayPassadoControlado` atual e não altera a saída canônica.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile nucleo/pacote_replay_passado.py
python -m py_compile scripts/diagnostico/auditar_pacote_replay_passado_v4d.py
python scripts/diagnostico/auditar_pacote_replay_passado_v4d.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4D

```text
=== AUDITORIA PACOTE REPLAY PASSADO SHADOW V4D ===
adaptador: pacote_replay_passado_shadow
versao: V17-F0-V.4D-shadow
modo_execucao: shadow
data_referencia_presente: True
qtd_lotes_origem: 18
qtd_lotes_pacote: 18
lotes_apos_replay_identicos: True
log_passado_qtd_origem: 110
log_movimentos_passados_qtd_pacote: 110
log_movimentos_passados_identico: True
estado_lotes_passado_qtd_origem: 18
estado_lotes_passado_qtd_pacote: 18
estado_lotes_passado_identico: True
auditoria_replay_presente: True
validacao_replay_presente: True
metadados_origem_presente: True
auditoria_base_preservada: True
validacao_base_preservada: True
audit_trilha_pagamentos_passados_total: 110
nao_altera_replay_efetivo: True
nao_altera_saida_canonica: True
saida_canonica_identica_dupla_execucao: True
validacao_ok: True
validacao_v4d_ok: True
```

---

## 5. Evidência runtime — aplicação principal

`python -B aplicacao/principal.py` executou sem erro localmente e gerou a saída operacional oficial:

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

Resumo relevante observado:

```text
- data de referência: 2026-05-20
- dados financeiros: download
- status obtenção planilha: ok
- dados CDI/BCB: cache_local
- status obtenção CDI/BCB: cache_atualizado_sem_fetch
- cache atualizado para referência: sim
- última data com fator no cache: 2026-05-19
- caminho do cache: dados/cache_bcb.json
```

A execução atualizou `dados/cache_bcb.json`, alteração esperada e externa ao escopo da V4D. O cache deve ser commitado separadamente após o registro desta microetapa.

---

## 6. Auditoria dos critérios de aceite

```text
py_compile_pacote_replay_passado=True
py_compile_auditoria_v4d=True
validacao_v4d_ok=True
lotes_apos_replay_identicos=True
log_movimentos_passados_identico=True
estado_lotes_passado_identico=True
auditoria_replay_presente=True
validacao_replay_presente=True
metadados_origem_presente=True
nao_altera_replay_efetivo=True
nao_altera_saida_canonica=True
saida_canonica_identica_dupla_execucao=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
```

---

## 7. Estado Git local após validação

O estado local informado após `git diff --check` e `git status -sb` foi:

```text
## main...origin/main
 M dados/cache_bcb.json
```

Interpretação:

```text
ALTERACAO_PENDENTE_POS_V4D=dados/cache_bcb.json
ALTERACAO_ESPERADA=sim
BLOQUEIA_V4D=nao
COMMIT_SEPARADO_RECOMENDADO=sim
```

---

## 8. Decisão

```text
V4D_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
PACOTE_REPLAY_PASSADO_SHADOW_VALIDADO=sim
REPLAY_EFETIVO_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OPERACIONAL_GERADA=sim
CACHE_BCB_ATUALIZADO_FORA_DO_ESCOPO=sim
```

---

## 9. Próxima ação imediata

Commitar separadamente a atualização esperada do cache BCB:

```text
dados/cache_bcb.json
```

Mensagem sugerida:

```text
Atualiza cache BCB
```

---

## 10. Próxima microetapa arquitetural

Após o commit separado do cache, seguir para:

```text
V17-F0-V.4E — Normaliza PacoteLedgerTemporalOperacional shadow
```

Tipo sugerido:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Normalizar PacoteLedgerTemporal para contrato operacional shadow, corrigindo metadados pós-V3.7S, adicionando aliases e explicitando campos ausentes como vazios auditados.
```

---

## 11. Conclusão

A V4D está aprovada por evidência runtime. O `PacoteReplayPassado` shadow preserva os objetos do replay controlado, adiciona aliases contratuais e metadados, e não altera a saída canônica.

A única alteração local pendente após validação é `dados/cache_bcb.json`, esperada pela execução do pipeline em 2026-05-20 e a ser commitada separadamente.

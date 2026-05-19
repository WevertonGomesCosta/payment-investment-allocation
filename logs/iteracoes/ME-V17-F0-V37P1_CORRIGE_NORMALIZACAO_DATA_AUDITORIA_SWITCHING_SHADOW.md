# ME-V17-F0-V37P.1 — Corrige normalização de data na auditoria switching shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37P.1
- VERSAO_CANDIDATA: V17-F0-V.3.7P.1
- TIPO: MICROCORREÇÃO DIAGNÓSTICA / SEM ALTERAÇÃO OPERACIONAL
- CLASSE: CORRIGE_NORMALIZACAO_DATA_AUDITORIA_SWITCHING_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7P
- ALTERA_SCRIPT_DIAGNOSTICO: sim
- ALTERA_ADAPTADOR: não
- ALTERA_LEDGER_OPERACIONAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Evidência runtime recebida

O usuário executou:

```bash
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py --sem-csv
```

A auditoria retornou:

```text
comparacao_mapa_legado_vs_canonico: False
comparacao_eventos_legado_vs_canonico: True
sem_alteracao_observavel: True
```

A única divergência reportada no mapa foi de forma de data:

```text
legado: 2026-05-05T00:00:00
shadow: 2026-05-05
```

para os lotes:

```text
Lote 3000 mar. B
Lote 3000 mar. V
Lote 8500 mar.
```

---

## 3. Diagnóstico

A divergência não indicava diferença econômica, diferença de lote, diferença de destino, diferença de valor ou diferença de evento.

Ela ocorria porque o script diagnóstico normalizava objetos com `isoformat()` antes de reduzir `pd.Timestamp` para data civil.

Assim, o caminho legado produzia:

```text
YYYY-MM-DDT00:00:00
```

e o caminho shadow produzia:

```text
YYYY-MM-DD
```

---

## 4. Correção aplicada

Arquivo alterado:

```text
scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py
```

Correção:

```text
_norm_data(...) agora tenta primeiro pd.to_datetime(...).date().isoformat()
```

antes de cair em `isoformat()` genérico.

---

## 5. Escopo preservado

Não foram alterados:

```text
nucleo/switching_canonico_ledger_shadow.py
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
nucleo/saida_canonica_ledger_shadow.py
aplicacao/principal.py
aplicacao/console/principal.py
nucleo/gerar_planilha_operacional.py
dados/cache_bcb.json
```

---

## 6. Decisão

```text
DIVERGENCIA_RUNTIME_ORIGINAL=normalizacao_de_data_no_script_diagnostico
DIVERGENCIA_ECONOMICA=nao
DIVERGENCIA_DE_EVENTOS=nao
DIVERGENCIA_DE_LOTES=nao
DIVERGENCIA_DE_VALORES=nao
MICROCORRECAO_APLICADA=sim
VALIDACAO_RUNTIME_POS_CORRECAO=pendente_de_execucao_local
```

---

## 7. Próxima ação

Executar novamente:

```bash
git pull origin main
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py --sem-csv
```

Se a execução retornar todos os critérios verdadeiros, registrar a aprovação runtime da equivalência.

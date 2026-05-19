# ME-V17-F0-V37L.1 — Corrige bloqueio de contexto no diagnóstico PacoteLedgerTemporal shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37L.1
- VERSAO_CANDIDATA: V17-F0-V.3.7L.1
- TIPO: EXECUTÁVEL / MICROCORREÇÃO / SEM ALTERAÇÃO DE SAÍDA
- CLASSE: CORRIGE_BLOQUEIO_CONTEXTO_DIAGNOSTICO_LEDGER_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7L
- ALTERA_CODIGO: sim
- ALTERA_SCRIPT_DIAGNOSTICO: sim
- ALTERA_CONTEXTO_BASELINE: não
- ALTERA_LEDGER_LEGADO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A execução local do usuário confirmou que o script diagnóstico passou a existir após sincronização do repositório, mas falhou durante a construção do contexto:

```text
TypeError: carregar_benchmark_agrupado_individual_shadow() missing 1 required positional argument: 'config'
```

A falha ocorreu antes de:

```text
construir_ledger_temporal_conjunto(...)
construir_pacote_ledger_temporal_shadow(...)
comparar equivalência runtime
```

Portanto, a equivalência runtime continuava pendente.

---

## 3. Diagnóstico causal

A falha não pertence ao `PacoteLedgerTemporal`.

A causa foi uma dependência desnecessária no diagnóstico:

```text
carregar_contexto_baseline(...)
```

estava sendo chamado com todos os componentes padrão, incluindo:

```text
incluir_benchmark_agrupado_individual_shadow=True
```

Esse benchmark não é necessário para auditar equivalência entre ledger legado e pacote shadow.

---

## 4. Correção aplicada

Arquivo alterado:

```text
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

Alteração aplicada:

```python
contexto = carregar_contexto_baseline(
    raiz_repositorio=args.raiz,
    instalar_automaticamente=False,
    incluir_benchmark_agrupado_individual_shadow=False,
)
```

---

## 5. Escopo preservado

Não foi alterado:

```text
nucleo/contexto_baseline.py
nucleo/ledger_temporal_conjunto.py
nucleo/pacote_ledger_temporal.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
nucleo/replay_passado_controlado.py
nucleo/dados_operacionais_canonicos.py
aplicacao/principal.py
aplicacao/console/principal.py
dados/
cache/
saidas/
```

---

## 6. Justificativa da microcorreção

A correção é deliberadamente restrita porque:

- o benchmark agrupado/individual não é insumo da auditoria do ledger shadow;
- corrigir `contexto_baseline.py` abriria escopo central de orquestração;
- a finalidade imediata é permitir execução do diagnóstico V3.7K;
- nenhuma decisão econômica ou saída deve mudar nesta etapa.

---

## 7. Comando de validação pós-correção

O usuário deve sincronizar o repositório e executar:

```bash
git pull origin main
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py --sem-csv
```

Opcionalmente, para gerar CSVs diagnósticos:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

---

## 8. Critérios para considerar a auditoria runtime aprovada

A execução deve retornar código `0` e produzir:

```text
validacao_ok: True
equivalente_eventos: True
equivalente_fifo: True
equivalente_pagamento_ids: True
equivalente_status: True
equivalente_motivo: True
equivalente_saldos: True
```

Se ocorrer nova falha anterior ao ledger, registrar a nova causa sem promover o pacote.

---

## 9. Decisão

```text
PACOTE_LEDGER_TEMPORAL_PROMOVIDO=nao
SAIDA_CANONICA_ALTERADA=nao
EQUIVALENCIA_RUNTIME_COMPROVADA=pendente_de_nova_execucao_local
```

---

## 10. Próxima ação

Executar novamente o script após `git pull origin main`.

Se a execução completar, registrar o resultado como:

```text
V17-F0-V.3.7L.2 — Registra resultado runtime da auditoria PacoteLedgerTemporal shadow
```

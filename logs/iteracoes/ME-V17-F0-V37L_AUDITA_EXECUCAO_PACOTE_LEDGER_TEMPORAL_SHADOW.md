# ME-V17-F0-V37L — Audita execução do PacoteLedgerTemporal shadow e equivalência contra ledger legado

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37L
- VERSAO_CANDIDATA: V17-F0-V.3.7L
- TIPO: EXECUTÁVEL / DIAGNÓSTICO / SEM ALTERAÇÃO DE SAÍDA
- CLASSE: AUDITA_EXECUCAO_PACOTE_LEDGER_TEMPORAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7K
- ALTERA_CODIGO: não
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

A microetapa foi aberta após:

```text
d994246 — V17-F0-V.3.7K: registra pacote ledger temporal shadow
```

A V3.7K adicionou:

```text
nucleo/pacote_ledger_temporal.py
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
logs/iteracoes/ME-V17-F0-V37K_IMPLEMENTA_PACOTE_LEDGER_TEMPORAL_SHADOW.md
```

A V3.7K não alterou `saida_canonica.py`, `saida_observavel.py`, `ledger_temporal_conjunto.py`, replay, Etapa 3, motor, console, XLSX, dados ou cache.

---

## 3. Objetivo da V3.7L

Executar ou preparar a execução auditável de:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

para verificar equivalência entre:

```text
retorno_legado = construir_ledger_temporal_conjunto(...)
pacote_shadow = construir_pacote_ledger_temporal_shadow(...)
```

---

## 4. Resultado da auditoria de execução neste ambiente

```text
EXECUCAO_REAL_DO_SCRIPT_NESTE_AMBIENTE=nao
MOTIVO=conector_github_disponivel_nao_executa_scripts_e_nao_ha_workflow_CI_associado_ao_commit
EQUIVALENCIA_RUNTIME_COMPROVADA=nao
FALSO_VERDE_EVITADO=sim
PROMOCAO_PARA_SAIDA_CANONICA=proibida
```

A ferramenta disponível nesta sessão permite inspecionar e alterar arquivos no GitHub, mas não executa scripts Python no repositório remoto.

Também foi verificado que não há workflow run do GitHub Actions associado ao commit da V3.7K.

Logo, a equivalência runtime não deve ser declarada como aprovada nesta microetapa.

---

## 5. Auditoria estática realizada

### 5.1. Script diagnóstico existente

Arquivo auditado:

```text
scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

O script existe e contém o fluxo esperado:

```text
carregar_contexto_baseline(...)
_quadro_futuro_preferencial(contexto)
_mapa_pagamentos_central(contexto)
construir_ledger_temporal_conjunto(...)
construir_pacote_ledger_temporal_shadow(..., retorno_legado=retorno_legado)
comparar eventos, FIFO, pagamento_id, status, motivo e saldos
emitir resumo
opcionalmente gravar CSVs em saidas/diagnostico/
```

### 5.2. Compatibilidade de assinatura

Foi verificado que a função real:

```text
carregar_contexto_baseline(...)
```

aceita os argumentos usados pelo script:

```text
raiz_repositorio=args.raiz
instalar_automaticamente=False
```

Portanto, não foi identificado bloqueio estático nessa chamada.

### 5.3. Garantia de não alteração de saída

O script diagnóstico não importa nem chama:

```text
construir_saida_canonica(...)
```

O script também não altera:

```text
nucleo/saida_canonica.py
nucleo/saida_observavel.py
aplicacao/principal.py
aplicacao/console/principal.py
```

A gravação opcional de CSVs é restrita a:

```text
saidas/diagnostico/
```

---

## 6. Comando de execução local obrigatório

A equivalência runtime deve ser verificada localmente com:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py --sem-csv
```

ou, para gerar evidências CSV:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

---

## 7. Métricas esperadas no console

O console deve emitir bloco iniciado por:

```text
=== AUDITORIA PACOTE LEDGER TEMPORAL SHADOW V3.7K ===
```

Métricas esperadas:

```text
validacao_ok
qtd_eventos_legado
qtd_eventos_shadow
qtd_fifo_legado
qtd_fifo_shadow
equivalente_eventos
equivalente_fifo
equivalente_pagamento_ids
equivalente_status
equivalente_motivo
equivalente_saldos
usa_contexto_amplo
usa_planilha_bruta
usa_switching_shadow
usa_pos_injetado
```

---

## 8. Critérios para aprovar equivalência runtime

A equivalência só poderá ser considerada aprovada se o script retornar código `0` e as métricas abaixo forem verdadeiras:

```text
validacao_ok=True
equivalente_eventos=True
equivalente_fifo=True
equivalente_pagamento_ids=True
equivalente_status=True
equivalente_motivo=True
equivalente_saldos=True
```

Se qualquer uma dessas métricas for falsa, o pacote shadow deve permanecer apenas como artefato diagnóstico.

---

## 9. Interpretação dos marcadores transitórios

As métricas abaixo podem continuar verdadeiras na V3.7L:

```text
usa_contexto_amplo=True
usa_planilha_bruta=True
usa_switching_shadow=True
usa_pos_injetado=True
```

Isso não reprova o shadow nesta fase.

Essas métricas apenas registram a realidade transitória do ledger legado que está sendo embrulhado.

---

## 10. Decisão sobre conexão à saída canônica

```text
CONECTAR_PACOTE_LEDGER_TEMPORAL_A_SAIDA_CANONICA=nao
MOTIVO=equivalencia_runtime_ainda_nao_executada_nem_comprovada
```

A saída canônica deve continuar intacta até que exista evidência runtime real.

---

## 11. Status da V3.7L

```text
V37L_STATUS=BLOQUEADA_POR_AUSENCIA_DE_EXECUCAO_RUNTIME_NO_AMBIENTE_DISPONIVEL
VALIDACAO_ESTATICA=aprovada
VALIDACAO_RUNTIME=pendente
PROMOCAO_SHADOW=proibida
```

---

## 12. Próxima microetapa recomendada

A próxima ação deve ser uma das duas alternativas:

### Alternativa A — execução local pelo usuário

Executar:

```bash
python scripts/diagnostico/auditar_pacote_ledger_temporal_shadow_v37k.py
```

Depois registrar o resultado como:

```text
V17-F0-V.3.7L.1 — Registra resultado runtime da auditoria PacoteLedgerTemporal shadow
```

### Alternativa B — preparar CI explícito

Criar workflow ou runner diagnóstico dedicado para executar o script no GitHub Actions.

Essa alternativa deve ser tratada como nova microetapa, pois altera infraestrutura de execução.

---

## 13. Conclusão

A V3.7L não declara equivalência runtime.

Ela evita falso verde, confirma que o script diagnóstico está estruturalmente preparado e bloqueia qualquer conexão do `PacoteLedgerTemporal` à saída canônica até que a execução real seja realizada em ambiente com acesso ao repositório, dados e dependências.

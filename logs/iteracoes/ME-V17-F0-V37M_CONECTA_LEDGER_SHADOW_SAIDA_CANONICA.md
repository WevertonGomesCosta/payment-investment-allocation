# ME-V17-F0-V37M — Conecta PacoteLedgerTemporal à saída canônica em modo shadow opcional sem alterar saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37M
- VERSAO_CANDIDATA: V17-F0-V.3.7M
- TIPO: EXECUTÁVEL / SHADOW OPCIONAL / SEM ALTERAÇÃO OBSERVÁVEL DE SAÍDA
- CLASSE: CONECTA_LEDGER_SHADOW_SAIDA_CANONICA
- BASELINE_DE_ENTRADA: V17-F0-V.3.7L.2
- ALTERA_CODIGO: sim
- ALTERA_SAIDA_CANONICA_OPERACIONAL: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_LEDGER_LEGADO: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A V3.7L.2 registrou equivalência runtime aprovada entre:

```text
construir_ledger_temporal_conjunto(...)
construir_pacote_ledger_temporal_shadow(...)
```

com:

```text
validacao_ok=True
qtd_eventos_legado=158
qtd_eventos_shadow=158
qtd_fifo_legado=2844
qtd_fifo_shadow=2844
equivalente_eventos=True
equivalente_fifo=True
equivalente_pagamento_ids=True
equivalente_status=True
equivalente_motivo=True
equivalente_saldos=True
```

---

## 3. Objetivo da V3.7M

Conectar `PacoteLedgerTemporal` à saída canônica em modo shadow opcional, sem substituir a fonte operacional efetiva da saída.

A saída operacional continua sendo produzida por:

```text
nucleo.saida_canonica.construir_saida_canonica(...)
```

---

## 4. Estratégia implementada

A conexão foi feita em um módulo wrapper dedicado, não por alteração direta do núcleo grande da saída canônica.

Arquivo criado:

```text
nucleo/saida_canonica_ledger_shadow.py
```

Função criada:

```text
construir_saida_canonica_com_ledger_shadow_opcional(...)
```

Comportamento:

- com `ativar_ledger_shadow=False`, retorna a saída canônica operacional atual;
- com `ativar_ledger_shadow=True`, preserva todas as tabelas observáveis da saída operacional;
- acrescenta apenas `auditoria['ledger_shadow_v37m']`;
- não torna `PacoteLedgerTemporal` entrada obrigatória;
- não remove a ponte legada;
- não altera `nucleo/saida_canonica.py`.

---

## 5. Arquivos criados

```text
nucleo/saida_canonica_ledger_shadow.py
scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py
logs/iteracoes/ME-V17-F0-V37M_CONECTA_LEDGER_SHADOW_SAIDA_CANONICA.md
```

---

## 6. Arquivos preservados

Não foram alterados:

```text
nucleo/saida_canonica.py
nucleo/saida_observavel.py
nucleo/ledger_temporal_conjunto.py
nucleo/pacote_ledger_temporal.py
nucleo/replay_passado_controlado.py
nucleo/dados_operacionais_canonicos.py
nucleo/contexto_baseline.py
aplicacao/principal.py
aplicacao/console/principal.py
dados/
cache/
saidas/
```

---

## 7. Bloco de auditoria shadow

Quando ativado, o wrapper acrescenta:

```text
auditoria['ledger_shadow_v37m']
```

Campos principais:

```text
modo_shadow
origem
pacote_ledger_temporal_classe
pacote_ledger_temporal_entrada_obrigatoria_saida
saida_operacional_preservada
ponte_legada_removida
fonte_operacional_saida
validacao_ok
qtd_eventos_temporais_shadow
qtd_fifo_candidatos_shadow
qtd_eventos_ledger_auditoria_saida
qtd_fifo_auditoria_saida
equivalente_qtd_eventos_saida_vs_shadow
equivalente_qtd_fifo_saida_vs_shadow
usa_contexto_amplo
usa_planilha_bruta
usa_switching_shadow
usa_pos_injetado
erros_bloqueantes
avisos
```

---

## 8. Script diagnóstico

Arquivo criado:

```text
scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py
```

O script compara:

```text
saida_base = construir_saida_canonica(contexto)
saida_shadow_desligado = construir_saida_canonica_com_ledger_shadow_opcional(..., ativar_ledger_shadow=False)
saida_shadow_ligado = construir_saida_canonica_com_ledger_shadow_opcional(..., ativar_ledger_shadow=True)
```

Critérios do script:

- saída com shadow desligado deve ser idêntica à saída base;
- saída com shadow ligado deve preservar todos os campos observáveis;
- auditoria sem o bloco `ledger_shadow_v37m` deve ser idêntica;
- bloco `ledger_shadow_v37m` deve existir;
- bloco shadow deve ter validação ok;
- contagens de eventos e FIFO devem ser equivalentes.

---

## 9. Comando de validação local

Após sincronizar o repositório:

```bash
git pull origin main
python scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py --sem-csv
```

Para gerar CSV diagnóstico:

```bash
python scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py
```

---

## 10. Critério obrigatório de aprovação runtime

A V3.7M só deve ser considerada aprovada runtime se o script retornar código `0` e confirmar:

```text
desligado_extrato_passado_identico=True
desligado_extrato_futuro_identico=True
desligado_lotes_ativos_identico=True
desligado_lotes_exauridos_identico=True
ligado_extrato_passado_identico=True
ligado_extrato_futuro_identico=True
ligado_lotes_ativos_identico=True
ligado_lotes_exauridos_identico=True
ligado_fechamento_atual_identico=True
ligado_resumo_recebidos_identico=True
ligado_auditoria_sem_bloco_shadow_identica=True
ligado_bloco_shadow_presente=True
ligado_bloco_shadow_validacao_ok=True
ligado_bloco_shadow_equivalente_eventos=True
ligado_bloco_shadow_equivalente_fifo=True
```

---

## 11. Decisão de promoção

```text
PACOTE_LEDGER_TEMPORAL_CONECTADO_A_SAIDA=sim_em_wrapper_shadow_opcional
PACOTE_LEDGER_TEMPORAL_ENTRADA_OBRIGATORIA_DA_SAIDA=nao
SAIDA_CANONICA_OPERACIONAL_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
PONTE_LEGADA_REMOVIDA=nao
EQUIVALENCIA_OBSERVAVEL_RUNTIME=pendente_de_execucao_local
```

---

## 12. Próxima ação

Executar o script diagnóstico localmente e registrar o resultado como:

```text
V17-F0-V.3.7M.1 — Registra resultado runtime da saída canônica com ledger shadow opcional
```

Se houver divergência em qualquer campo observável, não promover e registrar a causa antes de qualquer nova alteração.

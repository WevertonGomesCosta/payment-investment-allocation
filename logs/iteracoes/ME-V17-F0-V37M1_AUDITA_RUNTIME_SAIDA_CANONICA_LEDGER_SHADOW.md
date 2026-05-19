# ME-V17-F0-V37M.1 — Audita runtime da saída canônica com ledger shadow opcional

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37M.1
- VERSAO_CANDIDATA: V17-F0-V.3.7M.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_RUNTIME_SAIDA_CANONICA_LEDGER_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7M
- ALTERA_CODIGO: não
- ALTERA_SCRIPT_DIAGNOSTICO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_LEDGER_LEGADO: não
- ALTERA_PACOTE_LEDGER_TEMPORAL: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A V3.7M adicionou a conexão opcional shadow da saída canônica por meio de arquivos novos:

```text
nucleo/saida_canonica_ledger_shadow.py
scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py
logs/iteracoes/ME-V17-F0-V37M_CONECTA_LEDGER_SHADOW_SAIDA_CANONICA.md
```

A comparação entre V3.7L.2 e `main` mostrou apenas esses três arquivos adicionados no escopo da V3.7M.

---

## 3. Comando executado localmente

O usuário executou:

```bash
git pull origin main
git log --oneline -5
git status -sb
python scripts/diagnostico/auditar_saida_canonica_com_ledger_shadow_v37m.py --sem-csv
```

O `git log` local registrou:

```text
8006ac4 (HEAD -> main, origin/main, origin/HEAD) V17-F0-V.3.7M: registra conexao shadow saida canonica
9add61b V17-F0-V.3.7M: adiciona auditoria saida ledger shadow
2afb65d V17-F0-V.3.7M: adiciona saida canonica ledger shadow opcional
e0a2073 V17-F0-V.3.7L.2: registra runtime ledger shadow
ce1dee6 V17-F0-V.3.7L.1: registra correcao bloqueio contexto
```

O `git status -sb` local registrou apenas alteração esperada em cache:

```text
## main...origin/main
 M dados/cache_bcb.json
```

Essa alteração de cache BCB não pertence à V3.7M.1 e deve ser tratada em commit separado.

---

## 4. Saída runtime registrada

```text
=== AUDITORIA SAIDA CANONICA COM LEDGER SHADOW V3.7M ===
desligado_versao_identico: True
desligado_data_referencia_identico: True
desligado_extrato_passado_identico: True
desligado_extrato_passado_qtd_base: 110
desligado_extrato_passado_qtd_shadow: 110
desligado_extrato_futuro_identico: True
desligado_extrato_futuro_qtd_base: 158
desligado_extrato_futuro_qtd_shadow: 158
desligado_switchings_identico: True
desligado_switchings_qtd_base: 0
desligado_switchings_qtd_shadow: 0
desligado_ranking_amostra_identico: True
desligado_ranking_amostra_qtd_base: 10
desligado_ranking_amostra_qtd_shadow: 10
desligado_lotes_ativos_identico: True
desligado_lotes_ativos_qtd_base: 7
desligado_lotes_ativos_qtd_shadow: 7
desligado_lotes_exauridos_identico: True
desligado_lotes_exauridos_qtd_base: 11
desligado_lotes_exauridos_qtd_shadow: 11
desligado_recebidos_atuais_identico: True
desligado_recebidos_atuais_qtd_base: 18
desligado_recebidos_atuais_qtd_shadow: 18
desligado_fechamento_atual_identico: True
desligado_fechamento_atual_qtd_base: 7
desligado_fechamento_atual_qtd_shadow: 7
desligado_resumo_recebidos_identico: True
desligado_resumo_recebidos_qtd_base: 7
desligado_resumo_recebidos_qtd_shadow: 7
desligado_auditoria_sem_bloco_shadow_identica: True
desligado_bloco_shadow_presente: False
desligado_bloco_shadow_validacao_ok: False
desligado_bloco_shadow_equivalente_eventos: False
desligado_bloco_shadow_equivalente_fifo: False
desligado_qtd_eventos_temporais_shadow: None
desligado_qtd_fifo_candidatos_shadow: None
desligado_usa_contexto_amplo: None
desligado_usa_planilha_bruta: None
desligado_usa_switching_shadow: None
desligado_usa_pos_injetado: None
ligado_versao_identico: True
ligado_data_referencia_identico: True
ligado_extrato_passado_identico: True
ligado_extrato_passado_qtd_base: 110
ligado_extrato_passado_qtd_shadow: 110
ligado_extrato_futuro_identico: True
ligado_extrato_futuro_qtd_base: 158
ligado_extrato_futuro_qtd_shadow: 158
ligado_switchings_identico: True
ligado_switchings_qtd_base: 0
ligado_switchings_qtd_shadow: 0
ligado_ranking_amostra_identico: True
ligado_ranking_amostra_qtd_base: 10
ligado_ranking_amostra_qtd_shadow: 10
ligado_lotes_ativos_identico: True
ligado_lotes_ativos_qtd_base: 7
ligado_lotes_ativos_qtd_shadow: 7
ligado_lotes_exauridos_identico: True
ligado_lotes_exauridos_qtd_base: 11
ligado_lotes_exauridos_qtd_shadow: 11
ligado_recebidos_atuais_identico: True
ligado_recebidos_atuais_qtd_base: 18
ligado_recebidos_atuais_qtd_shadow: 18
ligado_fechamento_atual_identico: True
ligado_fechamento_atual_qtd_base: 7
ligado_fechamento_atual_qtd_shadow: 7
ligado_resumo_recebidos_identico: True
ligado_resumo_recebidos_qtd_base: 7
ligado_resumo_recebidos_qtd_shadow: 7
ligado_auditoria_sem_bloco_shadow_identica: True
ligado_bloco_shadow_presente: True
ligado_bloco_shadow_validacao_ok: True
ligado_bloco_shadow_equivalente_eventos: True
ligado_bloco_shadow_equivalente_fifo: True
ligado_qtd_eventos_temporais_shadow: 158
ligado_qtd_fifo_candidatos_shadow: 2844
ligado_usa_contexto_amplo: True
ligado_usa_planilha_bruta: True
ligado_usa_switching_shadow: True
ligado_usa_pos_injetado: True
```

---

## 5. Auditoria dos critérios obrigatórios

### 5.1. Modo shadow desligado

Com `ativar_ledger_shadow=False`, a saída permanece idêntica à saída canônica base.

Critérios observáveis aprovados:

```text
desligado_extrato_passado_identico=True
desligado_extrato_futuro_identico=True
desligado_lotes_ativos_identico=True
desligado_lotes_exauridos_identico=True
desligado_fechamento_atual_identico=True
desligado_resumo_recebidos_identico=True
desligado_auditoria_sem_bloco_shadow_identica=True
```

Ausência esperada de bloco shadow:

```text
desligado_bloco_shadow_presente=False
```

---

### 5.2. Modo shadow ligado

Com `ativar_ledger_shadow=True`, a saída observável permanece idêntica e a auditoria recebe apenas o bloco shadow.

Critérios observáveis aprovados:

```text
ligado_extrato_passado_identico=True
ligado_extrato_futuro_identico=True
ligado_lotes_ativos_identico=True
ligado_lotes_exauridos_identico=True
ligado_fechamento_atual_identico=True
ligado_resumo_recebidos_identico=True
ligado_auditoria_sem_bloco_shadow_identica=True
```

Bloco shadow aprovado:

```text
ligado_bloco_shadow_presente=True
ligado_bloco_shadow_validacao_ok=True
ligado_bloco_shadow_equivalente_eventos=True
ligado_bloco_shadow_equivalente_fifo=True
ligado_qtd_eventos_temporais_shadow=158
ligado_qtd_fifo_candidatos_shadow=2844
```

---

## 6. Interpretação dos marcadores transitórios

Os marcadores abaixo permaneceram verdadeiros:

```text
ligado_usa_contexto_amplo=True
ligado_usa_planilha_bruta=True
ligado_usa_switching_shadow=True
ligado_usa_pos_injetado=True
```

Isso não reprova a V3.7M.1.

Esses marcadores apenas confirmam que o pacote shadow ainda embrulha o ledger legado e suas dependências transitórias. A microetapa valida a conexão shadow opcional sem alteração observável de saída, não a purificação arquitetural do ledger.

---

## 7. Decisão

```text
V37M_STATUS=APROVADA
MICROCORRECAO_NECESSARIA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
AUDITORIA_ACRESCIDA_APENAS_COM_BLOCO_SHADOW=sim
PACOTE_LEDGER_TEMPORAL_CONECTADO_COMO_SHADOW_OPCIONAL=sim
PACOTE_LEDGER_TEMPORAL_PROMOVIDO_COMO_ENTRADA_OBRIGATORIA=nao
PONTE_LEGADA_REMOVIDA=nao
```

A V3.7M está aprovada para o escopo definido.

---

## 8. Escopo que permanece proibido

Ainda permanece proibido:

- remover a chamada direta atual de `construir_ledger_temporal_conjunto(...)` na saída canônica;
- tornar `PacoteLedgerTemporal` entrada obrigatória da saída canônica;
- remover contenções POS;
- alterar replay;
- alterar Etapa 3;
- alterar motor econômico;
- alterar console;
- alterar XLSX;
- alterar dados/cache dentro desta microetapa.

---

## 9. Sobre o cache BCB atualizado

A alteração local em:

```text
dados/cache_bcb.json
```

foi reconhecida como alteração esperada, mas não faz parte da V3.7M.1.

Ela deve ser commitada separadamente após o usuário sincronizar este registro de auditoria, com escopo próprio de atualização de cache BCB.

---

## 10. Próxima ação recomendada

Depois de sincronizar o registro V3.7M.1, registrar o cache BCB atualizado em commit separado:

```bash
git pull origin main
git status -sb
git add dados/cache_bcb.json
git commit -m "Atualiza cache BCB"
git push origin main
```

Antes do commit, recomenda-se verificar se somente o cache está modificado:

```bash
git diff --stat
git diff -- dados/cache_bcb.json
```

---

## 11. Conclusão

A V3.7M está aprovada. A conexão do `PacoteLedgerTemporal` à saída canônica em modo shadow opcional preservou integralmente a saída observável e acrescentou apenas o bloco de auditoria shadow quando ativado.

Não há microcorreção necessária para a V3.7M.

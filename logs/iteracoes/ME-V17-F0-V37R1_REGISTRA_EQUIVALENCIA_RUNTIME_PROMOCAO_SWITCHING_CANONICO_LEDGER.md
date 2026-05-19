# ME-V17-F0-V37R.1 — Registra equivalência runtime da promoção controlada switching_canonico no ledger

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37R.1
- VERSAO_CANDIDATA: V17-F0-V.3.7R.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_PROMOCAO_SWITCHING_CANONICO_LEDGER
- BASELINE_DE_ENTRADA: V17-F0-V.3.7R
- BASELINE_COMMIT_ENTRADA: c47b651ade5b75cd37e50ffff21f85a021cf13f7
- ALTERA_CODIGO: não
- ALTERA_LEDGER_LEGADO_DIRETAMENTE: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_REPLAY: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Registrar a evidência runtime local de que a promoção controlada de `switching_canonico` como fonte primária do ledger preserva integralmente o retorno do ledger, o extrato futuro, a saída canônica e a saída observável.

Esta microetapa não altera código nem promove edição direta de `nucleo/ledger_temporal_conjunto.py`.

---

## 3. Comando executado localmente

O usuário executou:

```bash
git pull origin main
python scripts/diagnostico/auditar_ledger_switching_canonico_primario_v37r.py --sem-csv
```

O `git pull` sincronizou:

```text
1d1f04a..c47b651  main -> origin/main
```

---

## 4. Saída runtime registrada

```text
=== AUDITORIA LEDGER SWITCHING CANONICO PRIMARIO V3.7R ===
fonte_primaria_switching_ledger: switching_canonico
fallback_legado_disponivel_apenas_para_auditoria: True
promocao_controlada_v37r: True
edita_ledger_legado_diretamente: False
preserva_schema_operacional_legado: True
eventos_legado_qtd: 158
eventos_canonico_qtd: 158
fifo_legado_qtd: 2844
fifo_canonico_qtd: 2844
eventos_ledger_identicos: True
fifo_identico: True
retorno_ledger_identico: True
pagamentos_futuros_processados_identicos: True
saldos_por_lote_identicos: True
saida_versao_identico: True
saida_data_referencia_identico: True
saida_extrato_passado_identico: True
saida_extrato_futuro_identico: True
saida_switchings_identico: True
saida_ranking_amostra_identico: True
saida_lotes_ativos_identico: True
saida_lotes_exauridos_identico: True
saida_recebidos_atuais_identico: True
saida_fechamento_atual_identico: True
saida_resumo_recebidos_identico: True
saida_auditoria_identico: True
saida_canonica_identica: True
extrato_futuro_identico: True
sem_alteracao_observavel: True
```

---

## 5. Auditoria dos critérios mínimos

### 5.1. Fonte primária e fallback

```text
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_disponivel_apenas_para_auditoria=True
promocao_controlada_v37r=True
edita_ledger_legado_diretamente=False
preserva_schema_operacional_legado=True
```

Veredito:

```text
PROMOCAO_CONTROLADA_VALIDADA=sim
```

---

### 5.2. Ledger temporal

```text
eventos_legado_qtd=158
eventos_canonico_qtd=158
fifo_legado_qtd=2844
fifo_canonico_qtd=2844
eventos_ledger_identicos=True
fifo_identico=True
retorno_ledger_identico=True
pagamentos_futuros_processados_identicos=True
saldos_por_lote_identicos=True
```

Veredito:

```text
LEDGER_TEMPORAL_IDENTICO=sim
```

---

### 5.3. Saída canônica e extrato futuro

```text
saida_versao_identico=True
saida_data_referencia_identico=True
saida_extrato_passado_identico=True
saida_extrato_futuro_identico=True
saida_switchings_identico=True
saida_ranking_amostra_identico=True
saida_lotes_ativos_identico=True
saida_lotes_exauridos_identico=True
saida_recebidos_atuais_identico=True
saida_fechamento_atual_identico=True
saida_resumo_recebidos_identico=True
saida_auditoria_identico=True
saida_canonica_identica=True
extrato_futuro_identico=True
sem_alteracao_observavel=True
```

Veredito:

```text
SAIDA_CANONICA_IDENTICA=sim
EXTRATO_FUTURO_IDENTICO=sim
SAIDA_OBSERVAVEL_IDENTICA=sim
```

---

## 6. Decisão

```text
V37R_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
SWITCHING_CANONICO_PROMOVIDO_COMO_FONTE_PRIMARIA_CONTROLADA=sim
FALLBACK_LEGADO_DISPONIVEL_APENAS_PARA_AUDITORIA=sim
LEDGER_LEGADO_EDITADO_DIRETAMENTE=nao
EVENTOS_LEDGER_IDENTICOS=sim
FIFO_IDENTICO=sim
RETORNO_LEDGER_IDENTICO=sim
EXTRATO_FUTURO_IDENTICO=sim
SAIDA_CANONICA_IDENTICA=sim
SAIDA_OBSERVAVEL_IDENTICA=sim
```

---

## 7. Interpretação

A execução comprova que `switching_canonico` da Etapa 3 pode substituir o caminho bruto da aba `Switching` como fonte primária controlada do ledger sem alterar o resultado operacional.

A V3.7R ainda não altera diretamente `nucleo/ledger_temporal_conjunto.py`. A promoção foi validada em construtor controlado e reversível, preservando o schema operacional downstream.

---

## 8. Próxima microetapa recomendada

```text
V17-F0-V.3.7S — Substitui internamente o consumo bruto de Switching no ledger por switching_canonico com fallback auditável
```

Tipo sugerido:

```text
EXECUTÁVEL / SUBSTITUIÇÃO INTERNA CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo sugerido:

```text
Alterar minimamente nucleo/ledger_temporal_conjunto.py para usar switching_canonico como fonte primária real nas funções internas de mapa/eventos de switching, mantendo o caminho legado somente como fallback auditável, e provar identidade de eventos, FIFO, retorno do ledger, extrato futuro, saída canônica e saída observável.
```

Escopo sugerido:

```text
nucleo/ledger_temporal_conjunto.py
scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py
logs/iteracoes/ME-V17-F0-V37S_SUBSTITUI_SWITCHING_BRUTO_LEDGER_POR_CANONICO.md
```

Critérios mínimos:

```text
fonte_primaria_interna_switching_ledger=switching_canonico
fallback_legado_switching_auditavel=True
eventos_ledger_identicos=True
fifo_identico=True
retorno_ledger_identico=True
extrato_futuro_identico=True
saida_canonica_identica=True
sem_alteracao_observavel=True
```

---

## 9. Condição de parada para V3.7S

A V3.7S deve parar sem promoção se ocorrer divergência em qualquer um dos seguintes blocos:

```text
eventos_temporais
fifo_candidatos_avaliados
retorno_ledger
pagamentos_futuros_processados
saldos_por_lote
extrato_futuro
saida_canonica
saida_observavel
```

---

## 10. Conclusão

A V3.7R está aprovada com equivalência runtime.

O projeto já possui evidência de que `switching_canonico` pode funcionar como fonte primária controlada do ledger preservando integralmente a saída. A próxima etapa segura é substituir internamente o consumo bruto de `Switching` no ledger por `switching_canonico`, mantendo fallback legado auditável.

# ME-V17-F0-V37Q.1 — Registra equivalência runtime do ledger com switching_canonico shadow opcional

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37Q.1
- VERSAO_CANDIDATA: V17-F0-V.3.7Q.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_LEDGER_SWITCHING_CANONICO_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7Q
- BASELINE_COMMIT_ENTRADA: 1d1f04ae1e255b063f1c0c5acfb59ca064c64e0d
- ALTERA_CODIGO: não
- ALTERA_LEDGER_OPERACIONAL: não
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

Registrar a evidência runtime local de que o ledger com `switching_canonico` conectado em modo shadow opcional preserva integralmente o comportamento observável do fluxo atual.

A microetapa não promove `switching_canonico` como fonte operacional do ledger.

---

## 3. Comando executado localmente

O usuário executou:

```bash
git pull origin main
python scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py --sem-csv
```

O `git pull` sincronizou:

```text
4a5cae3..1d1f04a  main -> origin/main
```

---

## 4. Saída runtime registrada

```text
=== AUDITORIA LEDGER COM SWITCHING CANONICO SHADOW V3.7Q ===
pacote_desligado_eventos_qtd: 158
pacote_ligado_eventos_qtd: 158
pacote_desligado_fifo_qtd: 2844
pacote_ligado_fifo_qtd: 2844
eventos_temporais_identicos: True
fifo_identico: True
pagamentos_futuros_processados_identicos: True
saldos_por_lote_identicos: True
auditoria_sem_bloco_switching_identica: True
bloco_switching_shadow_presente: True
bloco_switching_shadow_validacao_ok: True
comparacao_mapa_legado_vs_canonico: True
comparacao_eventos_legado_vs_canonico: True
ledger_operacional_preservado: True
ledger_operacional_ainda_usa_caminho_legado: True
promove_switching_canonico_para_ledger: False
saida_canonica_preservada: True
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
sem_alteracao_observavel: True
```

---

## 5. Auditoria dos critérios mínimos

### 5.1. Ledger temporal

```text
eventos_temporais_identicos=True
fifo_identico=True
pagamentos_futuros_processados_identicos=True
saldos_por_lote_identicos=True
```

Veredito:

```text
LEDGER_TEMPORAL_PRESERVADO=sim
```

---

### 5.2. Auditoria shadow de switching

```text
auditoria_sem_bloco_switching_identica=True
bloco_switching_shadow_presente=True
bloco_switching_shadow_validacao_ok=True
comparacao_mapa_legado_vs_canonico=True
comparacao_eventos_legado_vs_canonico=True
```

Veredito:

```text
SWITCHING_CANONICO_SHADOW_EQUIVALENTE=sim
```

---

### 5.3. Preservação operacional

```text
ledger_operacional_preservado=True
ledger_operacional_ainda_usa_caminho_legado=True
promove_switching_canonico_para_ledger=False
```

Veredito:

```text
PROMOCAO_OPERACIONAL_NAO_REALIZADA=sim
```

---

### 5.4. Saída canônica e saída observável

```text
saida_canonica_preservada=True
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
sem_alteracao_observavel=True
```

Veredito:

```text
SAIDA_CANONICA_PRESERVADA=sim
SAIDA_OBSERVAVEL_PRESERVADA=sim
```

---

## 6. Decisão

```text
V37Q_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
LEDGER_COM_SWITCHING_CANONICO_SHADOW_VALIDADO=sim
EVENTOS_LEDGER_IDENTICOS=sim
FIFO_IDENTICO=sim
SALDOS_POR_LOTE_IDENTICOS=sim
SAIDA_CANONICA_IDENTICA=sim
SAIDA_OBSERVAVEL_IDENTICA=sim
LEDGER_OPERACIONAL_AINDA_USA_CAMINHO_LEGADO=sim
PROMOVE_SWITCHING_CANONICO_PARA_LEDGER=nao
```

---

## 7. Interpretação

A V3.7Q comprova que o `switching_canonico` da Etapa 3 já pode ser conectado ao envelope shadow do ledger sem alterar eventos temporais, FIFO, saldos, saída canônica ou saída observável.

A execução também confirma que o caminho operacional ainda é o legado. Portanto, a microetapa é uma integração shadow validada, não uma promoção.

---

## 8. Próxima microetapa recomendada

```text
V17-F0-V.3.7R — Promove switching_canonico como fonte primária shadow-controlada do ledger
```

Tipo sugerido:

```text
EXECUTÁVEL / PROMOÇÃO CONTROLADA / COM FALLBACK LEGADO AUDITÁVEL / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo sugerido:

```text
Alterar o ledger para obter mapa e eventos de switching a partir de switching_canonico como fonte primária, mantendo o caminho legado apenas como fallback/auditoria comparativa, e provar que eventos, FIFO, extrato futuro e saída canônica permanecem idênticos.
```

Critérios mínimos sugeridos:

```text
fonte_primaria_switching_ledger=switching_canonico
fallback_legado_disponivel_apenas_para_auditoria=True
eventos_ledger_identicos=True
fifo_identico=True
extrato_futuro_identico=True
saida_canonica_identica=True
sem_alteracao_observavel=True
```

---

## 9. Condição de parada para V3.7R

A promoção futura deve parar sem commit operacional se ocorrer qualquer divergência em:

```text
eventos_temporais
fifo_candidatos_avaliados
pagamentos_futuros_processados
saldos_por_lote
extrato_futuro
saida_canonica
saida_observavel
```

---

## 10. Conclusão

A V3.7Q está aprovada com equivalência runtime.

O projeto já possui evidência de que `switching_canonico` pode ser conectado ao ledger em modo shadow opcional preservando integralmente o fluxo observável. A próxima etapa segura é uma promoção controlada para fonte primária, mantendo o caminho legado como fallback/auditoria e exigindo prova de identidade da saída.

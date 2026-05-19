# ME-V17-F0-V37Q — Conecta switching_canonico ao ledger em modo shadow opcional

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37Q
- VERSAO_CANDIDATA: V17-F0-V.3.7Q
- TIPO: EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: CONECTA_SWITCHING_CANONICO_LEDGER_SHADOW_OPCIONAL
- BASELINE_DE_ENTRADA: V17-F0-V.3.7P.2
- BASELINE_COMMIT_ENTRADA: b3242401799e1e6c4c08ab80713c6cee0c34c5d3
- ALTERA_CODIGO: sim
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

Conectar o adaptador `switching_canonico_para_ledger_shadow` ao fluxo de construção do ledger em modo shadow opcional, preservando o caminho legado como fonte operacional efetiva.

A V3.7Q não promove `switching_canonico` como fonte operacional do ledger.

---

## 3. Condição de entrada

A V3.7P.2 aprovou a equivalência runtime entre:

```text
_mapa_switchings_aba_operacional(contexto)
vs
switching_canonico_para_mapa_ledger_shadow(contexto)
```

E entre:

```text
_eventos_switching_aba_operacional(contexto)
vs
switching_canonico_para_eventos_ledger_shadow(contexto)
```

com:

```text
comparacao_mapa_legado_vs_canonico=True
comparacao_eventos_legado_vs_canonico=True
sem_alteracao_observavel=True
```

---

## 4. Arquivos criados

```text
nucleo/ledger_switching_canonico_shadow_v37q.py
nucleo/pacote_ledger_temporal_switching_shadow_v37q.py
scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py
logs/iteracoes/ME-V17-F0-V37Q_CONECTA_SWITCHING_CANONICO_LEDGER_SHADOW_OPCIONAL.md
```

---

## 5. Arquivos deliberadamente não alterados

```text
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
nucleo/saida_canonica_ledger_shadow.py
aplicacao/principal.py
aplicacao/console/principal.py
nucleo/gerar_planilha_operacional.py
dados/cache_bcb.json
```

---

## 6. Componente 1 — auditoria switching canônico no ledger shadow

Arquivo:

```text
nucleo/ledger_switching_canonico_shadow_v37q.py
```

Função principal:

```text
auditar_switching_canonico_ledger_shadow_v37q(contexto)
```

Bloco de auditoria:

```text
switching_canonico_ledger_shadow_v37q
```

Responsabilidade:

```text
comparar estruturas legadas de switching do ledger
vs
estruturas canônicas derivadas de contexto.dados_operacionais.switching_canonico
```

A função não altera eventos do ledger, FIFO, replay ou saída.

---

## 7. Componente 2 — conexão opcional ao PacoteLedgerTemporal

Arquivo:

```text
nucleo/pacote_ledger_temporal_switching_shadow_v37q.py
```

Função principal:

```text
construir_pacote_ledger_temporal_com_switching_canonico_shadow_v37q(...)
```

Parâmetro de ativação:

```text
ativar_switching_canonico_shadow: bool = False
```

Comportamento:

- com `ativar_switching_canonico_shadow=False`, retorna o pacote shadow padrão sem bloco V3.7Q;
- com `ativar_switching_canonico_shadow=True`, retorna o mesmo pacote, com os mesmos eventos e FIFO, acrescido apenas do bloco de auditoria `switching_canonico_ledger_shadow_v37q`.

---

## 8. Garantias da integração

Mesmo com o shadow ligado:

```text
eventos_temporais vêm do retorno legado
fifo_candidatos_avaliados vêm do retorno legado
pagamentos_futuros_processados vêm do retorno legado
saldos_por_lote vêm do retorno legado
ledger operacional continua usando o caminho legado
switching_canonico não é promovido para fonte operacional
```

---

## 9. Script diagnóstico

Arquivo:

```text
scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py
```

Comando recomendado:

```bash
python scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py --sem-csv
```

Com CSV:

```bash
python scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py
```

CSV esperado:

```text
saidas/diagnostico/auditoria_ledger_com_switching_canonico_shadow_v37q_resumo.csv
```

---

## 10. Critérios avaliados pelo diagnóstico

O script deve retornar código zero somente se todos os critérios forem verdadeiros:

```text
eventos_temporais_identicos=True
fifo_identico=True
pagamentos_futuros_processados_identicos=True
saldos_por_lote_identicos=True
auditoria_sem_bloco_switching_identica=True
bloco_switching_shadow_presente=True
bloco_switching_shadow_validacao_ok=True
comparacao_mapa_legado_vs_canonico=True
comparacao_eventos_legado_vs_canonico=True
ledger_operacional_preservado=True
ledger_operacional_ainda_usa_caminho_legado=True
promove_switching_canonico_para_ledger=False
saida_canonica_identica=True
sem_alteracao_observavel=True
```

---

## 11. Condição de parada

A V3.7Q não deve ser promovida se qualquer um dos seguintes itens falhar:

```text
eventos_temporais_identicos=False
fifo_identico=False
extrato futuro ou saída canônica divergente
bloco shadow ausente
bloco shadow com validacao_ok=False
comparacao_mapa_legado_vs_canonico=False
comparacao_eventos_legado_vs_canonico=False
ledger_operacional_ainda_usa_caminho_legado=False
promove_switching_canonico_para_ledger=True
```

Qualquer correção deve ocorrer em microetapa própria, sem alterar o ledger operacional.

---

## 12. Decisão

```text
SWITCHING_CANONICO_CONECTADO_AO_PACOTE_LEDGER_SHADOW=sim
LEDGER_OPERACIONAL_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
PROMOCAO_SWITCHING_CANONICO_PARA_LEDGER=nao
VALIDACAO_RUNTIME=pendente_de_execucao_local
```

---

## 13. Próxima ação

Executar localmente:

```bash
git pull origin main
python scripts/diagnostico/auditar_ledger_com_switching_canonico_shadow_v37q.py --sem-csv
```

Se passar, registrar:

```text
V17-F0-V.3.7Q.1 — Registra equivalência runtime do ledger com switching_canonico shadow opcional
```

---

## 14. Conclusão

A V3.7Q conecta `switching_canonico` ao envelope shadow do ledger, mas preserva integralmente o caminho legado como fonte operacional.

Essa microetapa fecha a transição entre a equivalência isolada da V3.7P e a futura promoção controlada do ledger para consumir `switching_canonico` como fonte primária.

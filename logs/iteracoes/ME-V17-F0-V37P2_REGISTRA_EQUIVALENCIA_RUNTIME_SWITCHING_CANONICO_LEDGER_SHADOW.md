# ME-V17-F0-V37P.2 — Registra equivalência runtime switching_canonico vs Switching bruto no ledger shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37P.2
- VERSAO_CANDIDATA: V17-F0-V.3.7P.2
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_SWITCHING_CANONICO_LEDGER_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7P.1
- BASELINE_COMMIT_ENTRADA: 4a5cae3bd12f3c1905e1850e4542083fbf6807ac
- ALTERA_CODIGO: não
- ALTERA_ADAPTADOR: não
- ALTERA_SCRIPT_DIAGNOSTICO: não
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

Registrar a evidência runtime local de que o adaptador `switching_canonico_para_ledger_shadow` reproduz, em modo shadow, o caminho legado do ledger baseado na aba bruta `Switching`.

A microetapa não promove o adaptador como fonte operacional do ledger.

---

## 3. Comando executado localmente

O usuário executou:

```bash
git pull origin main
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py --sem-csv
```

O `git pull` sincronizou a microcorreção V3.7P.1:

```text
145dac8..4a5cae3  main -> origin/main
```

---

## 4. Saída runtime registrada

```text
=== AUDITORIA SWITCHING CANONICO LEDGER SHADOW V3.7P ===
adaptador: switching_canonico_ledger_shadow
origem: switching_canonico_etapa3
switching_canonico_presente: True
switching_canonico_linhas: 4
qtd_mapa_switchings: 3
qtd_eventos_switching: 4
nao_le_pacote_planilha: True
nao_le_quadros_brutos: True
nao_reabre_excel: True
nao_altera_ledger_operacional: True
nao_altera_saida_canonica: True
qtd_mapa_legado: 3
qtd_mapa_shadow: 3
lotes_origem_apenas_legado: []
lotes_origem_apenas_shadow: []
divergencias_mapa: []
mapa_qtd_identica: True
mapa_lotes_origem_identicos: True
mapa_campos_criticos_identicos: True
qtd_eventos_legado: 4
qtd_eventos_shadow: 4
eventos_apenas_legado: []
eventos_apenas_shadow: []
divergencias_eventos: []
eventos_qtd_identica: True
eventos_chaves_equivalentes: True
eventos_campos_criticos_identicos: True
comparacao_mapa_legado_vs_canonico: True
comparacao_eventos_legado_vs_canonico: True
sem_alteracao_observavel: True
```

---

## 5. Auditoria dos critérios obrigatórios

### 5.1. Garantias de isolamento

```text
nao_le_pacote_planilha=True
nao_le_quadros_brutos=True
nao_reabre_excel=True
nao_altera_ledger_operacional=True
nao_altera_saida_canonica=True
sem_alteracao_observavel=True
```

Veredito:

```text
ISOLAMENTO_SHADOW_APROVADO=sim
```

---

### 5.2. Equivalência do mapa de switching

```text
qtd_mapa_legado=3
qtd_mapa_shadow=3
lotes_origem_apenas_legado=[]
lotes_origem_apenas_shadow=[]
divergencias_mapa=[]
mapa_qtd_identica=True
mapa_lotes_origem_identicos=True
mapa_campos_criticos_identicos=True
comparacao_mapa_legado_vs_canonico=True
```

Veredito:

```text
MAPA_SWITCHING_CANONICO_EQUIVALENTE_AO_LEGADO=sim
```

---

### 5.3. Equivalência dos eventos de switching

```text
qtd_eventos_legado=4
qtd_eventos_shadow=4
eventos_apenas_legado=[]
eventos_apenas_shadow=[]
divergencias_eventos=[]
eventos_qtd_identica=True
eventos_chaves_equivalentes=True
eventos_campos_criticos_identicos=True
comparacao_eventos_legado_vs_canonico=True
```

Veredito:

```text
EVENTOS_SWITCHING_CANONICO_EQUIVALENTES_AO_LEGADO=sim
```

---

## 6. Interpretação

A execução comprova que o adaptador canônico baseado em:

```text
contexto.dados_operacionais.switching_canonico
```

reproduz as estruturas que o ledger legado extrai da aba bruta `Switching`, sem acessar `pacote_planilha`, sem acessar `quadros_brutos`, sem reabrir Excel e sem alterar a saída observável.

---

## 7. Decisão

```text
V37P_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
ADAPTADOR_SWITCHING_CANONICO_LEDGER_SHADOW_APROVADO=sim
MAPA_LEGADO_VS_CANONICO_EQUIVALENTE=sim
EVENTOS_LEGADO_VS_CANONICO_EQUIVALENTES=sim
LEDGER_OPERACIONAL_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
PROMOCAO_PARA_LEDGER_OPERACIONAL=nao
```

---

## 8. O que ainda não foi promovido

Apesar da equivalência runtime, o ledger efetivo ainda não consome o adaptador canônico.

Ainda permanece verdadeiro:

```text
ledger_operacional_usa_caminho_legado_switching_bruto=sim
switching_canonico_conectado_ao_ledger_efetivo=nao
```

A promoção deve ocorrer em microetapa posterior, controlada e com modo shadow ligado ao ledger.

---

## 9. Próxima microetapa recomendada

```text
V17-F0-V.3.7Q — Conecta switching_canonico ao ledger em modo shadow opcional
```

Tipo:

```text
EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Conectar o adaptador switching_canonico_para_ledger_shadow ao fluxo de construção do ledger em modo shadow opcional, preservando o caminho legado como fonte operacional efetiva.
```

Critérios mínimos:

```text
eventos ledger idênticos
fifo idêntico
extrato futuro idêntico
saída canônica idêntica
auditoria acrescida apenas com bloco shadow
ledger operacional ainda usando caminho legado
```

---

## 10. Conclusão

A V3.7P está aprovada com equivalência runtime.

O projeto já possui prova local de que `switching_canonico` da Etapa 3 pode reproduzir o consumo legado da aba bruta `Switching` no nível de mapa e eventos esperados pelo ledger.

A próxima etapa segura é conectar essa equivalência ao ledger em modo shadow opcional, ainda sem promoção operacional.

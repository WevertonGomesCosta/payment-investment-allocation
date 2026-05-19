# ME-V17-F0-V37P — Implementa adaptador switching_canonico_para_ledger_shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37P
- VERSAO_CANDIDATA: V17-F0-V.3.7P
- TIPO: EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: IMPLEMENTA_ADAPTADOR_SWITCHING_CANONICO_LEDGER_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.3.7O
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

Implementar adaptador shadow para comparar o caminho legado do ledger baseado na aba bruta `Switching` com o caminho canônico baseado em:

```text
contexto.dados_operacionais.switching_canonico
```

A V3.7P não promove o caminho canônico como fonte operacional do ledger.

---

## 3. Arquivos alterados

```text
nucleo/switching_canonico_ledger_shadow.py
scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py
logs/iteracoes/ME-V17-F0-V37P_IMPLEMENTA_ADAPTADOR_SWITCHING_CANONICO_LEDGER_SHADOW.md
```

---

## 4. Arquivos deliberadamente não alterados

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

## 5. Adaptador criado

Arquivo:

```text
nucleo/switching_canonico_ledger_shadow.py
```

Funções principais:

```text
switching_canonico_para_mapa_ledger_shadow(contexto)
switching_canonico_para_eventos_ledger_shadow(contexto)
auditar_adaptador_switching_canonico_ledger_shadow(contexto)
```

Garantias declaradas pelo adaptador:

```text
nao_le_pacote_planilha=True
nao_le_quadros_brutos=True
nao_reabre_excel=True
nao_altera_ledger_operacional=True
nao_altera_saida_canonica=True
```

---

## 6. Fonte consumida pelo adaptador

O adaptador consome somente:

```text
contexto.dados_operacionais.switching_canonico
```

Ele não consome:

```text
contexto.pacote_planilha.quadros_brutos
pd.read_excel(...)
```

---

## 7. Estruturas shadow produzidas

### 7.1. Mapa por lote de origem

Estrutura compatível com o uso legado de:

```text
_mapa_switchings_aba_operacional(contexto)
```

Campos shadow:

```text
lote_origem
data_switching
produto_destino
valor_liquido_origem
status_switching
origem_mapa_migracao
lote_pos_switching
switching_id_canonico
ordem_planilha_switching
```

### 7.2. Eventos POS switching

Estrutura compatível com o uso legado de:

```text
_eventos_switching_aba_operacional(contexto)
```

Campos shadow:

```text
evento_switching_id
evento_switching_id_legado_compat
switching_id_canonico
lote_origem
data_switching
produto_destino
valor_liquido_origem
lote_pos_switching
status_materializacao_passiva
origem_mapa_migracao
ordem_planilha_switching
```

---

## 8. Script diagnóstico criado

Arquivo:

```text
scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py
```

Comando recomendado:

```bash
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py --sem-csv
```

Com CSVs:

```bash
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py
```

Saídas CSV esperadas quando `--sem-csv` não for usado:

```text
saidas/diagnostico/auditoria_switching_canonico_ledger_shadow_v37p_resumo.csv
saidas/diagnostico/auditoria_switching_canonico_ledger_shadow_v37p_divergencias_mapa.csv
saidas/diagnostico/auditoria_switching_canonico_ledger_shadow_v37p_divergencias_eventos.csv
```

---

## 9. Comparações executadas pelo diagnóstico

O script compara:

```text
_mapa_switchings_aba_operacional(contexto)
vs
switching_canonico_para_mapa_ledger_shadow(contexto)
```

E também:

```text
_eventos_switching_aba_operacional(contexto)
vs
switching_canonico_para_eventos_ledger_shadow(contexto)
```

Critérios principais:

```text
mapa_qtd_identica
mapa_lotes_origem_identicos
mapa_campos_criticos_identicos
eventos_qtd_identica
eventos_chaves_equivalentes
eventos_campos_criticos_identicos
```

Critérios finais compostos:

```text
comparacao_mapa_legado_vs_canonico
comparacao_eventos_legado_vs_canonico
```

---

## 10. Critério de aprovação runtime

A execução local deve retornar código zero somente se todos os critérios abaixo forem verdadeiros:

```text
nao_le_pacote_planilha=True
nao_le_quadros_brutos=True
nao_reabre_excel=True
nao_altera_ledger_operacional=True
nao_altera_saida_canonica=True
comparacao_mapa_legado_vs_canonico=True
comparacao_eventos_legado_vs_canonico=True
sem_alteracao_observavel=True
```

---

## 11. Condição de parada

Se qualquer divergência aparecer, a V3.7P não deve ser promovida.

Casos que bloqueiam promoção:

```text
mapa_qtd_identica=False
mapa_lotes_origem_identicos=False
mapa_campos_criticos_identicos=False
eventos_qtd_identica=False
eventos_chaves_equivalentes=False
eventos_campos_criticos_identicos=False
```

A correção, se necessária, deve ocorrer em microetapa própria, sem alterar ledger efetivo.

---

## 12. Limitações conhecidas

A V3.7P ainda importa funções privadas do ledger legado no script diagnóstico:

```text
_mapa_switchings_aba_operacional
_eventos_switching_aba_operacional
```

Isso é aceitável nesta microetapa porque o objetivo é comparar contra o caminho legado. O adaptador canônico propriamente dito não depende dessas funções.

---

## 13. Decisão

```text
ADAPTADOR_SWITCHING_CANONICO_LEDGER_SHADOW_IMPLEMENTADO=sim
LEDGER_OPERACIONAL_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
CONSOLE_XLSX_ALTERADOS=nao
DADOS_CACHE_ALTERADOS=nao
PROMOCAO_PARA_LEDGER=nao
VALIDACAO_RUNTIME=pendente_de_execucao_local
```

---

## 14. Próxima ação

Executar localmente:

```bash
git pull origin main
python scripts/diagnostico/auditar_switching_canonico_ledger_shadow_v37p.py --sem-csv
```

Se todos os critérios forem verdadeiros, registrar:

```text
V17-F0-V.3.7P.1 — Registra equivalência runtime switching_canonico vs Switching bruto no ledger shadow
```

Se houver divergência, abrir microcorreção específica do adaptador, sem tocar no ledger operacional.

---

## 15. Conclusão

A V3.7P implementa o primeiro passo executável para remover o consumo bruto de `Switching` pelo ledger, mas mantém a mudança isolada em modo shadow.

A promoção para o ledger operacional só poderá ocorrer após equivalência runtime comprovada.

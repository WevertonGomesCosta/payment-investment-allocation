# ME-V17-F0-V4K0 — Normaliza comparação shadow de lotes/estado temporal contra base observável da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4K0
- VERSAO_CANDIDATA: V17-F0-V.4K0
- TIPO: EXECUTÁVEL / DIAGNÓSTICO-CORREÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
- CLASSE: NORMALIZA_COMPARACAO_LOTES_ESTADO_TEMPORAL_BASE_OBSERVAVEL_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4J.1
- BASELINE_COMMIT_ENTRADA: 3b95a6ea47f4e18aa247b684fc47f1aea69583e8
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Investigar os três lotes presentes apenas no `PacoteEstadoTemporal`, identificar se são origens migradas, destinos sintéticos, resíduos de estado ou duplicidades transitórias, e normalizar a comparação shadow para a mesma base observável da saída antes de anexar bloco temporal à auditoria.

---

## 3. Condição de entrada

A V4J.1 aprovou o diagnóstico runtime da saída contra os pacotes temporais agregados, mas encontrou uma lacuna concentrada em lotes:

```text
lotes_ativos_qtd_saida=5
lotes_exauridos_qtd_saida=13
lotes_saida_total=18
estado_lotes_final_qtd_pacote=21
lotes_intersecao=18
lotes_apenas_saida=0
lotes_apenas_estado=3
lotes_status=shadow_gap
```

A V4J.1 decidiu:

```text
SEGUIR_PARA_V4K_DIRETO=nao
SEGUIR_PARA_V4K0=sim
```

---

## 4. Arquivos criados

```text
scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py
logs/iteracoes/ME-V17-F0-V4K0_NORMALIZA_COMPARACAO_LOTES_ESTADO_TEMPORAL_OBSERVAVEL.md
```

---

## 5. Natureza da microetapa

A V4K0 não remove registros do `PacoteEstadoTemporal` e não altera a saída canônica.

Ela apenas cria uma normalização de comparação:

```text
estado_lotes_final_original
vs
estado_lotes_final_normalizado_para_base_observavel_da_saida
```

Interpretação operacional:

```text
PacoteEstadoTemporal pode preservar registros temporais adicionais.
A saída observável usa uma base filtrada/neutralizada.
A comparação com a saída deve usar a mesma base observável da saída.
```

---

## 6. Script diagnóstico

Foi criado:

```text
scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py
```

O script executa:

```text
1. carregar_contexto_baseline(...)
2. construir_saida_canonica(contexto)
3. construir_pacotes_temporais_agregados_saida_shadow(contexto)
4. construir_saida_canonica(contexto) novamente
5. identificar lotes da saída observável
6. identificar lotes do estado temporal final
7. listar lotes_apenas_estado
8. classificar motivo dos lotes extras
9. normalizar estado para a base observável da saída
10. validar comparação normalizada
```

---

## 7. Classificação dos lotes extras

Cada lote presente apenas no estado temporal é classificado com:

```text
lote_id
motivo
classe_normalizacao
observavel_na_saida
origem_estado_final
status_final
migrado
lote_pos_switching
qtd_registros_historico_estado
origens_historico
status_historico
```

Classes esperadas:

```text
excluir_da_base_observavel_shadow
revisar_manual
```

A V4K0 aprova apenas se todos os lotes extras forem classificados e excluíveis da base observável shadow.

---

## 8. Métricas esperadas

```text
lotes_apenas_estado_identificados=True
motivo_lotes_apenas_estado_classificado=True
lotes_apenas_estado_excluiveis_base_observavel=True
comparacao_lotes_normalizada=True
lotes_apenas_saida_qtd=0
saida_canonica_identica_dupla_execucao=True
sem_alteracao_observavel=True
validacao_v4k0_ok=True
```

---

## 9. Validações obrigatórias locais

Executar localmente:

```bash
python -m py_compile scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py
python scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 10. Critérios de aprovação

A V4K0 só deve ser considerada aprovada se:

```text
validacao_v4k0_ok=True
lotes_apenas_estado_identificados=True
motivo_lotes_apenas_estado_classificado=True
comparacao_lotes_normalizada=True
saida_canonica_identica_dupla_execucao=True
sem_alteracao_observavel=True
python -B aplicacao/principal.py executa sem erro localmente
```

---

## 11. Decisão esperada após validação

Se a validação local passar, registrar:

```text
V17-F0-V.4K0.1 — Registra normalização runtime de lotes/estado temporal contra base observável da saída
```

Tipo:

```text
DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
```

---

## 12. Próxima microetapa após V4K0.1

Se a V4K0 passar, a próxima etapa volta a ser:

```text
V17-F0-V.4K — Acrescenta bloco shadow temporal à auditoria da saída
```

Tipo sugerido:

```text
EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Adicionar bloco opcional de auditoria temporal shadow ao PacoteSaidaCanonica.auditoria, preservando integralmente as saídas observáveis.
```

---

## 13. Conclusão

A V4K0 cria a camada necessária para que a comparação entre `PacoteEstadoTemporal` e situação observável da saída seja feita na mesma base. Isso evita anexar um bloco temporal à auditoria da saída enquanto ainda há divergência estrutural não classificada em lotes.

# ME-V17-F0-V4K0.1 — Registra normalização runtime de lotes/estado temporal contra base observável da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4K0.1
- VERSAO_CANDIDATA: V17-F0-V.4K0.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_NORMALIZACAO_RUNTIME_LOTES_ESTADO_TEMPORAL_BASE_OBSERVAVEL_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4K0
- BASELINE_COMMIT_ENTRADA: 59ede0783d6c6ec1f7a35c1e529a9116ef151977
- ALTERA_CODIGO: não
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

Registrar a evidência runtime local de que a V4K0 normalizou a comparação shadow de lotes/estado temporal contra a base observável da saída, preservando a saída canônica e classificando os lotes extras do `PacoteEstadoTemporal`.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py
python scripts/diagnostico/auditar_normalizacao_lotes_estado_temporal_v4k0.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4K0

```text
=== AUDITORIA NORMALIZACAO LOTES ESTADO TEMPORAL SHADOW V4K0 ===
adaptador: normalizacao_lotes_estado_temporal_v4k0
versao_agregador: V17-F0-V.4I-shadow
data_referencia_presente: True
validacao_agregador_ok: True
erros_bloqueantes_agregador_total: 0
saida_canonica_identica_dupla_execucao: True
lotes_saida_total: 18
lotes_ativos_qtd_saida: 5
lotes_exauridos_qtd_saida: 13
estado_lotes_final_qtd_original: 21
estado_lotes_final_qtd_normalizado: 18
lotes_apenas_estado_qtd: 3
lotes_apenas_estado: ["Lote 3120 mai + Lote 3000 mai Neon", "Lote 5680 abr. + Lote 3120 mai", "Lote 5680 abr. + Lote 3400 mai."]
lotes_apenas_saida_qtd: 0
lotes_apenas_saida: []
lotes_apenas_estado_identificados: True
motivo_lotes_apenas_estado_classificado: True
lotes_apenas_estado_excluiveis_base_observavel: True
comparacao_lotes_normalizada: True
lotes_normalizados_intersecao: 18
lotes_normalizados_apenas_estado: []
lotes_normalizados_apenas_saida: []
fonte_primaria_switching_ledger: switching_canonico
usa_planilha_bruta_como_fonte_primaria: False
usa_retorno_ledger_dict_legado: True
saida_chama_ledger_diretamente_fluxo_atual: sim_fluxo_atual_ainda_transitorio
sem_alteracao_observavel: True
validacao_v4k0_ok: True
```

---

## 5. Lotes extras identificados e classificados

Os três lotes presentes apenas no `PacoteEstadoTemporal` foram:

```text
Lote 3120 mai + Lote 3000 mai Neon
Lote 5680 abr. + Lote 3120 mai
Lote 5680 abr. + Lote 3400 mai.
```

Classificação comum:

```text
motivo=saldo_temporal_ledger_sem_lote_observavel_saida
classe_normalizacao=excluir_da_base_observavel_shadow
observavel_na_saida=False
origem_estado_final=pacote_ledger_temporal_operacional.saldos_por_lote
status_final=ok
migrado=False
qtd_registros_historico_estado=1
```

Interpretação:

```text
LOTES_EXTRAS_SAO_SALDOS_TEMPORAIS_DO_LEDGER=sim
LOTES_EXTRAS_NAO_SAO_OBSERVAVEIS_NA_SAIDA=sim
LOTES_EXTRAS_DEVEM_SER_EXCLUIDOS_DA_BASE_OBSERVAVEL_SHADOW=sim
```

---

## 6. Comparação normalizada

Antes da normalização:

```text
lotes_saida_total=18
estado_lotes_final_qtd_original=21
lotes_apenas_estado_qtd=3
```

Depois da normalização para a base observável da saída:

```text
estado_lotes_final_qtd_normalizado=18
lotes_normalizados_intersecao=18
lotes_normalizados_apenas_estado=[]
lotes_normalizados_apenas_saida=[]
comparacao_lotes_normalizada=True
```

---

## 7. Evidência runtime — aplicação principal

`python -B aplicacao/principal.py` executou sem erro localmente e gerou:

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

Resumo operacional observado:

```text
- versão: V225
- data de referência: 2026-05-20
- dados financeiros: download
- status obtenção planilha: ok
- dados CDI/BCB: cache_local
- status obtenção CDI/BCB: cache_atualizado_sem_fetch
- última data com fator no cache: 2026-05-19
- switchings promovidos/executados: 4
- total de lotes sintéticos pós-switching: 4
- total de aportes futuros: 18
```

---

## 8. Auditoria dos critérios de aceite

```text
py_compile_auditoria_v4k0=True
validacao_v4k0_ok=True
lotes_apenas_estado_identificados=True
motivo_lotes_apenas_estado_classificado=True
lotes_apenas_estado_excluiveis_base_observavel=True
comparacao_lotes_normalizada=True
lotes_apenas_saida_qtd=0
saida_canonica_identica_dupla_execucao=True
sem_alteracao_observavel=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
git_diff_check_ok=True
worktree_limpa=True
```

---

## 9. Estado Git local após validação

O estado local informado após validação foi:

```text
## main...origin/main
```

Interpretação:

```text
ALTERACOES_PENDENTES=nao
DADOS_FINANCEIROS_PENDENTES=nao
CACHE_BCB_PENDENTE=nao
VALIDACAO_LOCAL_COMPLETA=sim
```

---

## 10. Decisão

```text
V4K0_STATUS=APROVADA_COM_NORMALIZACAO_RUNTIME
COMPARACAO_LOTES_NORMALIZADA=sim
LOTES_APENAS_ESTADO_CLASSIFICADOS=sim
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
WORKTREE_LIMPA=sim
```

---

## 11. Próxima microetapa arquitetural

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

Critérios mínimos esperados:

```text
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
extrato_passado_identico=True
extrato_futuro_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
fechamento_atual_identico=True
console_xlsx_identicos=True
sem_alteracao_observavel=True
```

---

## 12. Conclusão

A V4K0 está aprovada por evidência runtime. A divergência de lotes detectada na V4J foi normalizada como diferença entre estado temporal amplo e base observável da saída. A rota segura volta para a V4K, agora com a comparação de lotes normalizada.

# ME-V17-F0-V4K.1 — Registra equivalência runtime do bloco temporal shadow na auditoria da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4K.1
- VERSAO_CANDIDATA: V17-F0-V.4K.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_BLOCO_TEMPORAL_SHADOW_AUDITORIA_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4K
- BASELINE_COMMIT_ENTRADA: f30d41a9354cbe24f89f191b4394c32bfd5e437c
- ALTERA_CODIGO: não
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA_EFETIVA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Registrar a evidência runtime local de que a V4K acrescentou o bloco temporal shadow à auditoria da saída por rota opcional, preservando integralmente os blocos observáveis e o caminho principal da aplicação.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile nucleo/saida_canonica_temporal_shadow_v4k.py
python -m py_compile scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py
python scripts/diagnostico/auditar_saida_temporal_shadow_v4k.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4K

```text
=== AUDITORIA SAIDA CANONICA TEMPORAL SHADOW V4K ===
adaptador: saida_canonica_temporal_shadow_v4k
bloco_temporal_shadow_presente: True
auditoria_existente_preservada: True
auditoria_acrescida_apenas_bloco_temporal_shadow: True
extrato_passado_identico: True
extrato_futuro_identico: True
switchings_identico: True
ranking_amostra_identico: True
lotes_ativos_identico: True
lotes_exauridos_identico: True
recebidos_atuais_identico: True
fechamento_atual_identico: True
resumo_recebidos_identico: True
versao_identica: True
data_referencia_identica: True
bloco_temporal_ok: True
bloco_validacao_agregador_ok: True
bloco_erros_bloqueantes_total: 0
bloco_extrato_passado_identico: True
bloco_extrato_futuro_identico: True
bloco_lotes_normalizados_identicos: True
bloco_fonte_primaria_switching_ledger: switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria: False
sem_alteracao_observavel: True
validacao_v4k_ok: True
```

---

## 5. Evidência runtime — aplicação principal

`python -B aplicacao/principal.py` executou sem erro localmente e gerou:

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

Resumo operacional observado:

```text
versao: V225
data_referencia: 2026-05-20
dados_financeiros: download
status_obtencao_planilha: ok
dados_CDI_BCB: cache_local
status_obtencao_CDI_BCB: cache_atualizado_sem_fetch
cache_atualizado_para_referencia: sim
ultima_data_com_fator_no_cache: 2026-05-19
switchings_promovidos_executados: 4
total_lotes_sinteticos_pos_switching: 4
total_aportes_futuros: 18
relatorio_operacional: saidas/oficial/relatorio_operacional_v225.xlsx
```

---

## 6. Auditoria dos critérios de aceite

```text
py_compile_modulo_temporal_shadow=True
py_compile_auditoria_v4k=True
validacao_v4k_ok=True
bloco_temporal_shadow_presente=True
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
extrato_passado_identico=True
extrato_futuro_identico=True
switchings_identico=True
ranking_amostra_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
recebidos_atuais_identico=True
fechamento_atual_identico=True
resumo_recebidos_identico=True
versao_identica=True
data_referencia_identica=True
bloco_temporal_ok=True
bloco_validacao_agregador_ok=True
bloco_erros_bloqueantes_total=0
bloco_extrato_passado_identico=True
bloco_extrato_futuro_identico=True
bloco_lotes_normalizados_identicos=True
bloco_fonte_primaria_switching_ledger=switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria=False
sem_alteracao_observavel=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
git_diff_check_ok=True
worktree_limpa=True
```

---

## 7. Estado Git local após validação

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

## 8. Decisão

```text
V4K_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
BLOCO_TEMPORAL_SHADOW_PRESENTE=sim
AUDITORIA_EXISTENTE_PRESERVADA=sim
AUDITORIA_ACRESCIDA_APENAS_BLOCO_TEMPORAL_SHADOW=sim
SAIDA_CANONICA_EFETIVA_ALTERADA=nao
SAIDA_OBSERVAVEL_ALTERADA=nao
WORKTREE_LIMPA=sim
```

---

## 9. Próxima microetapa arquitetural

```text
V17-F0-V.4L — Promove bloco temporal shadow para caminho opcional controlado da saída canônica
```

Tipo sugerido:

```text
EXECUTÁVEL / INTEGRAÇÃO CONTROLADA / SEM ALTERAÇÃO OBSERVÁVEL POR PADRÃO
```

Objetivo:

```text
Expor o bloco temporal shadow por um caminho opcional controlado da saída canônica, mantendo o comportamento padrão da saída inalterado e permitindo ativação explícita por diagnóstico/flag/parâmetro.
```

Critérios mínimos esperados:

```text
saida_padrao_identica=True
saida_com_shadow_temporal_tem_bloco=True
auditoria_existente_preservada=True
auditoria_acrescida_apenas_bloco_temporal_shadow=True
extrato_passado_identico=True
extrato_futuro_identico=True
lotes_ativos_identico=True
lotes_exauridos_identico=True
fechamento_atual_identico=True
console_xlsx_identicos=True
sem_alteracao_observavel_padrao=True
```

---

## 10. Conclusão

A V4K está aprovada por evidência runtime. O bloco `temporal_shadow_v4k` foi integrado em rota opcional, a auditoria existente foi preservada, e todos os blocos observáveis permaneceram idênticos. A próxima etapa segura é a V4L, promovendo esse bloco para caminho opcional controlado da saída canônica sem alterar o comportamento padrão.

# ME-V17-F0-V4L.1 — Registra equivalência runtime do caminho controlado temporal shadow da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4L.1
- VERSAO_CANDIDATA: V17-F0-V.4L.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_CAMINHO_CONTROLADO_TEMPORAL_SHADOW_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4L
- BASELINE_COMMIT_ENTRADA: 30fd303d6a4bbe5fe7ab650cf7935bec097a9bce
- ALTERA_CODIGO: não
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA_PADRAO: não
- ALTERA_SAIDA_OBSERVAVEL_PADRAO: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Registrar a evidência runtime local de que a V4L promoveu o bloco temporal shadow para caminho opcional controlado da saída canônica, mantendo a saída padrão idêntica e preservando todos os blocos observáveis.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile nucleo/saida_canonica_controlada_v4l.py
python -m py_compile scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py
python scripts/diagnostico/auditar_saida_controlada_temporal_shadow_v4l.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4L

```text
=== AUDITORIA SAIDA CANONICA CONTROLADA TEMPORAL SHADOW V4L ===
adaptador: saida_canonica_controlada_v4l
saida_padrao_identica: True
saida_com_shadow_temporal_tem_bloco: True
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
sem_alteracao_observavel_padrao: True
validacao_v4l_ok: True
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
py_compile_saida_controlada_v4l=True
py_compile_auditoria_v4l=True
validacao_v4l_ok=True
saida_padrao_identica=True
saida_com_shadow_temporal_tem_bloco=True
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
sem_alteracao_observavel_padrao=True
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
V4L_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
CAMINHO_CONTROLADO_TEMPORAL_SHADOW_VALIDADO=sim
SAIDA_PADRAO_IDENTICA=sim
SAIDA_COM_SHADOW_TEMPORAL_TEM_BLOCO=sim
AUDITORIA_EXISTENTE_PRESERVADA=sim
AUDITORIA_ACRESCIDA_APENAS_BLOCO_TEMPORAL_SHADOW=sim
SAIDA_CANONICA_PADRAO_ALTERADA=nao
SAIDA_OBSERVAVEL_PADRAO_ALTERADA=nao
WORKTREE_LIMPA=sim
```

---

## 9. Próxima microetapa arquitetural

```text
V17-F0-V.4M — Audita elegibilidade para promoção do caminho controlado no construtor oficial da saída
```

Tipo sugerido:

```text
DOCUMENTAL / DIAGNÓSTICO ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Decidir se a assinatura oficial de construir_saida_canonica pode receber parâmetro opcional incluir_temporal_shadow=False sem risco de regressão, ou se a rota controlada deve permanecer externa por mais uma rodada.
```

---

## 10. Conclusão

A V4L está aprovada por evidência runtime. O caminho controlado permite ativar explicitamente o bloco temporal shadow sem alterar o comportamento padrão da saída canônica e sem alterar console, XLSX, dados ou cache.

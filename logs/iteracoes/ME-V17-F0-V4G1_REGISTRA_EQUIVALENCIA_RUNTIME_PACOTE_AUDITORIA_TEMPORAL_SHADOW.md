# ME-V17-F0-V4G.1 — Registra equivalência runtime do PacoteAuditoriaTemporal shadow

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4G.1
- VERSAO_CANDIDATA: V17-F0-V.4G.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_PACOTE_AUDITORIA_TEMPORAL_SHADOW
- BASELINE_DE_ENTRADA: V17-F0-V.4G
- BASELINE_COMMIT_ENTRADA: 54991b7f5a6b7cd0c807ca9864d12bfd7b0348c7
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

Registrar a evidência runtime local de que o `PacoteAuditoriaTemporal` shadow criado na V4G centraliza auditorias temporais de replay, ledger, estado, fontes, switching, invariantes e resíduos legados sem alterar replay efetivo, ledger efetivo, estado temporal efetivo ou saída canônica.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile nucleo/pacote_auditoria_temporal.py
python -m py_compile scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py
python scripts/diagnostico/auditar_pacote_auditoria_temporal_v4g.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4G

```text
=== AUDITORIA PACOTE AUDITORIA TEMPORAL SHADOW V4G ===
adaptador: pacote_auditoria_temporal_shadow
versao: V17-F0-V.4G-shadow
modo_execucao: shadow
data_referencia_presente: True
auditoria_replay_presente: True
auditoria_ledger_presente: True
auditoria_estado_temporal_presente: True
auditoria_fontes_elegiveis_ok: True
auditoria_switching_temporal_ok: True
auditoria_invariantes_ok: True
auditoria_residuos_legados_presente: True
validacao_temporal_global_ok: True
erros_bloqueantes_total: 0
avisos_total: 3
fonte_primaria_switching_ledger: switching_canonico
fallback_legado_switching_auditavel: True
usa_planilha_bruta_como_fonte_primaria: False
qtd_fontes_elegiveis_por_pagamento: 2808
qtd_fontes_disponiveis_por_data: 112
qtd_fifo_candidatos_avaliados: 2808
estado_lotes_por_data_materializado: True
estado_lotes_final_materializado: True
usa_retorno_ledger_dict_legado: True
saida_chama_ledger_diretamente: sim_fluxo_atual_ainda_transitorio
campos_vazios_auditados: ["estado_temporal_por_data", "vencimentos_processados", "fontes_elegiveis_por_data", "vencimentos_por_data", "migracoes_por_data"]
nao_altera_replay_efetivo: True
nao_altera_ledger_efetivo: True
nao_altera_estado_temporal_efetivo: True
nao_altera_saida_canonica: True
saida_canonica_identica_dupla_execucao: True
validacao_v4g_ok: True
```

---

## 5. Evidência runtime — aplicação principal

`python -B aplicacao/principal.py` executou sem erro localmente e gerou:

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

Resumo operacional relevante observado:

```text
- versão: V225
- data de referência: 2026-05-20
- dados financeiros: download
- status obtenção planilha: ok
- dados CDI/BCB: cache_local
- status obtenção CDI/BCB: cache_atualizado_sem_fetch
- cache atualizado para referência: sim
- última data com fator no cache: 2026-05-19
- switchings promovidos/executados: 4
- total de lotes sintéticos pós-switching: 4
- total de aportes futuros: 18
- saída operacional gerada em: saidas/oficial/relatorio_operacional_v225.xlsx
```

---

## 6. Auditoria dos critérios de aceite

```text
py_compile_pacote_auditoria_temporal=True
py_compile_auditoria_v4g=True
validacao_v4g_ok=True
auditoria_replay_presente=True
auditoria_ledger_presente=True
auditoria_estado_temporal_presente=True
auditoria_fontes_elegiveis_ok=True
auditoria_switching_temporal_ok=True
auditoria_invariantes_ok=True
auditoria_residuos_legados_presente=True
validacao_temporal_global_ok=True
erros_bloqueantes_total=0
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
estado_lotes_por_data_materializado=True
estado_lotes_final_materializado=True
saida_canonica_identica_dupla_execucao=True
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

## 8. Resíduos ainda auditados

A V4G centraliza os seguintes resíduos ainda existentes:

```text
usa_retorno_ledger_dict_legado=True
saida_chama_ledger_diretamente=sim_fluxo_atual_ainda_transitorio
campos_vazios_auditados=["estado_temporal_por_data", "vencimentos_processados", "fontes_elegiveis_por_data", "vencimentos_por_data", "migracoes_por_data"]
```

Esses resíduos não bloqueiam a V4G. Eles devem orientar a próxima fase de integração shadow dos pacotes temporais com a saída canônica.

---

## 9. Decisão

```text
V4G_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
PACOTE_AUDITORIA_TEMPORAL_SHADOW_VALIDADO=sim
REPLAY_EFETIVO_ALTERADO=nao
LEDGER_EFETIVO_ALTERADO=nao
ESTADO_TEMPORAL_EFETIVO_ALTERADO=nao
SAIDA_CANONICA_ALTERADA=nao
SAIDA_OPERACIONAL_GERADA=sim
WORKTREE_LIMPA=sim
```

---

## 10. Próxima microetapa arquitetural

```text
V17-F0-V.4H — Audita integração shadow dos pacotes temporais com a saída canônica
```

Tipo sugerido:

```text
DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Mapear exatamente quais partes da saída canônica ainda chamam ou reconstroem replay, ledger, estado e auditorias, preparando a conexão shadow dos pacotes temporais sem alteração observável.
```

---

## 11. Conclusão

A V4G está aprovada por evidência runtime. O `PacoteAuditoriaTemporal` shadow centraliza auditorias antes dispersas, confirma `switching_canonico` como fonte primária do ledger, preserva saída canônica e registra explicitamente os resíduos que devem ser tratados na integração futura com a saída.

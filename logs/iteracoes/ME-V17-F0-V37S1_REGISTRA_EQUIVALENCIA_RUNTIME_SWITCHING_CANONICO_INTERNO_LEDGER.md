# ME-V17-F0-V37S.1 — Registra equivalência runtime da substituição interna Switching bruto → switching_canonico no ledger

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37S.1
- VERSAO_CANDIDATA: V17-F0-V.3.7S.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_SWITCHING_CANONICO_INTERNO_LEDGER
- BASELINE_DE_ENTRADA: V17-F0-V.3.7S
- BASELINE_COMMIT_ENTRADA: baa43e9f44e95bbf51e66d3e1831627563660e9c
- PR_ASSOCIADO: #341
- ALTERA_CODIGO: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Registrar a evidência runtime local de que a V3.7S substituiu internamente o consumo bruto da aba `Switching` no ledger por `switching_canonico` como fonte primária, mantendo fallback legado auditável e preservando a saída observável.

---

## 3. Estado Git após merge

Após merge do PR #341, o estado local informado foi:

```text
## main...origin/main
```

Últimos commits informados:

```text
baa43e9 Merge pull request #341 from WevertonGomesCosta/codex/replace-raw-switching-with-canonical-in-ledger
1c44839 V17-F0-V.3.7S: substitui switching bruto por canonico no ledger
9ea362b V17-F0-V.3.7R.1: registra equivalencia runtime promocao switching canonico ledger
c47b651 V17-F0-V.3.7R: registra promocao controlada switching canonico ledger
d53fc74 V17-F0-V.3.7R: adiciona auditoria ledger switching canonico primario
```

---

## 4. Comandos executados localmente

```bash
git fetch origin pull/341/head:pr-341-v37s
git switch pr-341-v37s
python -m py_compile nucleo/ledger_temporal_conjunto.py
python -m py_compile scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py
python scripts/diagnostico/auditar_ledger_switching_canonico_interno_v37s.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
git switch main
git pull origin main
gh pr merge 341 --merge
git pull origin main
git status -sb
git log --oneline --decorate -5
```

---

## 5. Evidência runtime — diagnóstico V3.7S

A execução local retornou:

```text
=== AUDITORIA LEDGER SWITCHING CANONICO INTERNO V3.7S ===
fonte_primaria_interna_switching_ledger: switching_canonico
fallback_legado_switching_auditavel: True
mapa_canonico_total: 3
eventos_switching_canonico_total: 4
eventos_ledger_identicos: True
fifo_identico: True
retorno_ledger_identico: True
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
extrato_futuro_identico: True
saida_canonica_identica: True
sem_alteracao_observavel: True
```

---

## 6. Evidência runtime — aplicação principal

A execução local de:

```bash
python -B aplicacao/principal.py
```

foi concluída sem erro e gerou:

```text
Saída operacional gerada em: C:\Users\Weverton\OneDrive\GitHub\payment-investment-allocation\saidas\oficial\relatorio_operacional_v225.xlsx
```

Resumo relevante observado:

```text
- dados financeiros: download
- status obtenção planilha: ok
- dados CDI/BCB: cache_local
- status obtenção CDI/BCB: cache_atualizado_sem_fetch
- switchings promovidos/executados: 4
- total de lotes sintéticos pós-switching: 4
- data de referência: 2026-05-19
- último fator explícito CDI: 2026-05-18
```

---

## 7. Auditoria dos critérios da V3.7S

```text
fonte_primaria_interna_switching_ledger=switching_canonico
fallback_legado_switching_auditavel=True
mapa_canonico_total=3
eventos_switching_canonico_total=4
eventos_ledger_identicos=True
fifo_identico=True
retorno_ledger_identico=True
extrato_futuro_identico=True
saida_canonica_identica=True
sem_alteracao_observavel=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
git_diff_check_ok=True
worktree_limpa_pos_merge=True
```

---

## 8. Decisão

```text
V37S_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
SWITCHING_CANONICO_FONTE_PRIMARIA_INTERNA_LEDGER=sim
FALLBACK_LEGADO_SWITCHING_AUDITAVEL=sim
EVENTOS_LEDGER_IDENTICOS=sim
FIFO_IDENTICO=sim
RETORNO_LEDGER_IDENTICO=sim
EXTRATO_FUTURO_IDENTICO=sim
SAIDA_CANONICA_IDENTICA=sim
SAIDA_OBSERVAVEL_IDENTICA=sim
PR_341_MERGEADO=sim
```

---

## 9. Interpretação

A V3.7S encerra a principal dependência bruta remanescente entre Etapa 1 e ledger: o consumo interno primário da aba `Switching` foi substituído por `switching_canonico` da Etapa 3.

O caminho legado permanece disponível como fallback auditável, mas não é mais a fonte primária quando o switching canônico está presente.

---

## 10. Próxima microetapa recomendada

```text
V17-F0-V.3.7T — Audita fechamento da fronteira Etapa 3 → ledger após substituição interna do Switching
```

Tipo sugerido:

```text
DOCUMENTAL / DIAGNÓSTICO ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo sugerido:

```text
Verificar se ainda há consumo primário de resíduos da Etapa 1 após a Etapa 3, especialmente em replay, ledger, PacoteLedgerTemporal, saída canônica e saída observável, e decidir se a frente V3.7 pode ser encerrada antes da abertura da V4A.
```

---

## 11. Conclusão

A V3.7S está aprovada com equivalência runtime e merge realizada no `main`.

A próxima etapa segura não é abrir V4 diretamente, mas auditar formalmente o fechamento da fronteira Etapa 3 → ledger para confirmar que o principal consumo bruto remanescente foi eliminado e que eventuais resíduos restantes são apenas fallback/auditoria ou pertencem à próxima etapa arquitetural.

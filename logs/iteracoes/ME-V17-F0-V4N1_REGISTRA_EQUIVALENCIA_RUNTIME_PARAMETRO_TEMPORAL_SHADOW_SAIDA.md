# ME-V17-F0-V4N.1 — Registra equivalência runtime do parâmetro temporal shadow no construtor oficial da saída

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4N.1
- VERSAO_CANDIDATA: V17-F0-V.4N.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_EQUIVALENCIA_RUNTIME_PARAMETRO_TEMPORAL_SHADOW_CONSTRUTOR_OFICIAL_SAIDA
- BASELINE_DE_ENTRADA: V17-F0-V.4N + cache BCB atualizado
- BASELINE_COMMIT_ENTRADA: b49b0bb2ac62a10679043fb2cd675a8c88ba8381
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

Registrar a evidência runtime local de que a V4N promoveu `incluir_temporal_shadow=False` para a assinatura oficial de `construir_saida_canonica(...)`, preservando comportamento padrão e permitindo ativação explícita do bloco temporal shadow.

---

## 3. Comandos executados localmente

```bash
gh pr merge 342 --merge
git pull origin main
python -m py_compile nucleo/saida_canonica.py
python -m py_compile scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py
python scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
git add dados/cache_bcb.json
git commit -m "Atualiza cache BCB"
git push origin main
```

---

## 4. Evidência de merge e baseline

O PR 342 foi mergeado e o `main` local foi atualizado:

```text
0be3eb0..0e5dfa0  main -> origin/main
3 files changed, 200 insertions(+), 2 deletions(-)
create mode 100644 logs/iteracoes/ME-V17-F0-V4N_PROMOVE_PARAMETRO_TEMPORAL_SHADOW_CONSTRUTOR_OFICIAL_SAIDA.md
create mode 100644 scripts/diagnostico/auditar_saida_canonica_parametro_temporal_shadow_v4n.py
```

Depois da validação, o cache BCB atualizado foi commitado separadamente:

```text
b49b0bb — Atualiza cache BCB
```

---

## 5. Evidência runtime — diagnóstico V4N

```text
=== AUDITORIA PARAMETRO TEMPORAL SHADOW V4N ===
adaptador: saida_canonica::construir_saida_canonica
saida_padrao_identica: True
saida_parametro_false_identica: True
saida_parametro_true_tem_bloco: True
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
bloco_temporal_ok: True
bloco_validacao_agregador_ok: True
bloco_erros_bloqueantes_total: 0
bloco_fonte_primaria_switching_ledger: switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria: False
sem_alteracao_observavel_padrao: True
validacao_v4n_ok: True
```

---

## 6. Evidência runtime — aplicação principal

`python -B aplicacao/principal.py` executou sem erro localmente e gerou:

```text
saidas/oficial/relatorio_operacional_v225.xlsx
```

Resumo operacional observado:

```text
versao: V225
data_referencia: 2026-05-21
dados_financeiros: download
status_obtencao_planilha: ok
dados_CDI_BCB: cache_local
status_obtencao_CDI_BCB: cache_atualizado_sem_fetch
cache_atualizado_para_referencia: sim
ultima_data_com_fator_no_cache: 2026-05-20
fonte_da_serie: cache_local
status_do_fetch: cache_atualizado_sem_fetch
```

---

## 7. Auditoria dos critérios de aceite

```text
py_compile_saida_canonica=True
py_compile_auditoria_v4n=True
validacao_v4n_ok=True
saida_padrao_identica=True
saida_parametro_false_identica=True
saida_parametro_true_tem_bloco=True
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
bloco_temporal_ok=True
bloco_validacao_agregador_ok=True
bloco_erros_bloqueantes_total=0
bloco_fonte_primaria_switching_ledger=switching_canonico
bloco_usa_planilha_bruta_como_fonte_primaria=False
sem_alteracao_observavel_padrao=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
git_diff_check_ok=True
cache_bcb_atualizado_e_commitado=True
```

---

## 8. Bug operacional observado — Lote 3120 mai

A validação da aplicação principal confirmou que o bug do lote permanece visível na saída:

```text
2026-05-20 | Cartão Azul | 2913.53 | Lote 3120 mai | Saldo Antes -105.93
2026-05-20 | Condomínio  | 19.02   | Lote 3120 mai | Saldo Antes -3019.46
```

Na situação atual:

```text
Lote 3120 mai | exaurido_por_saque
Orig. 3122.53 | Bruto sac. 3093.76 | Líq. sac. 3088.95 | Bruto atual 0.00 | Líq. atual 0.00 | Patr. líq. 3088.95 | Rend. líq. -33.58
```

Interpretação:

```text
BUG_LOTE_3120_MAI_CONFIRMADO=sim
CORRIGIR_NA_V4N=nao
ABRIR_DIAGNOSTICO_ESPECIFICO_NA_V4O=sim
```

---

## 9. Decisão

```text
V4N_STATUS=APROVADA_COM_EQUIVALENCIA_RUNTIME
PARAMETRO_OFICIAL_TEMPORAL_SHADOW_VALIDADO=sim
SAIDA_CANONICA_PADRAO_ALTERADA=nao
SAIDA_OBSERVAVEL_PADRAO_ALTERADA=nao
CACHE_BCB_ATUALIZADO_SEPARADAMENTE=sim
BUG_LOTE_3120_MAI_PERSISTE=sim
```

---

## 10. Próxima microetapa arquitetural

```text
V17-F0-V.4O — Diagnostica saldo, exaustão e rendimento do Lote 3120 mai na Etapa 4
```

Tipo sugerido:

```text
EXECUTÁVEL / DIAGNÓSTICO TEMPORAL / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Rastrear o Lote 3120 mai no inventário canônico, replay passado, ledger, PacoteEstadoTemporal, extrato passado e situação atual para identificar por que ele ficou com saldo negativo, exaurido e rendimento líquido negativo.
```

Critérios centrais:

```text
origem_do_saldo_negativo_identificada=True
origem_da_exaustao_incorreta_identificada=True
origem_do_rendimento_negativo_identificada=True
pagamentos_que_consumiram_lote_listados=True
saldo_modelo_vs_saldo_app_comparado=True
sem_alteracao_observavel=True
```

---

## 11. Conclusão

A V4N está aprovada por validação runtime pós-merge. O parâmetro `incluir_temporal_shadow=False` foi promovido ao construtor oficial da saída sem alterar o comportamento padrão. O cache BCB foi atualizado e commitado separadamente. A próxima etapa deve ser a V4O para diagnosticar o bug do `Lote 3120 mai` antes de qualquer fechamento da Etapa 4.

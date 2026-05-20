# ME-V17-F0-V4J.1 — Registra diagnóstico runtime da saída canônica contra pacotes temporais agregados

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4J.1
- VERSAO_CANDIDATA: V17-F0-V.4J.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REGISTRA_DIAGNOSTICO_RUNTIME_SAIDA_CANONICA_VS_PACOTES_TEMPORAIS_AGREGADOS
- BASELINE_DE_ENTRADA: V17-F0-V.4J
- BASELINE_COMMIT_ENTRADA: b285df36d74dbccac8e1d7b1f1ea9baa9db6b596
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

Registrar a evidência runtime local de que a V4J auditou a saída canônica contra os pacotes temporais agregados em modo shadow, preservando a saída efetiva e classificando divergências entre blocos.

---

## 3. Comandos executados localmente

```bash
git pull origin main
python -m py_compile scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py
python scripts/diagnostico/auditar_saida_canonica_vs_pacotes_temporais_v4j.py --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

---

## 4. Evidência runtime — diagnóstico V4J

```text
=== AUDITORIA SAIDA CANONICA VS PACOTES TEMPORAIS AGREGADOS SHADOW V4J ===
adaptador: saida_canonica_vs_pacotes_temporais_agregados_shadow
versao_agregador: V17-F0-V.4I-shadow
data_referencia_presente: True
saida_canonica_identica_dupla_execucao: True
validacao_agregador_ok: True
erros_bloqueantes_agregador_total: 0
extrato_passado_qtd_saida: 114
extrato_passado_qtd_pacote: 114
extrato_passado_qtd_identica: True
extrato_passado_status: identico
extrato_futuro_qtd_saida: 156
extrato_futuro_qtd_eventos_pacote: 156
extrato_futuro_qtd_pagamentos_pacote: 156
extrato_futuro_qtd_identica_eventos: True
extrato_futuro_status: identico
lotes_ativos_qtd_saida: 5
lotes_exauridos_qtd_saida: 13
lotes_saida_total: 18
estado_lotes_final_qtd_pacote: 21
lotes_status: shadow_gap
resumo_patrimonial_status: parcial_comparavel
auditoria_status: parcial_comparavel
fonte_primaria_switching_ledger: switching_canonico
usa_planilha_bruta_como_fonte_primaria: False
usa_retorno_ledger_dict_legado: True
saida_chama_ledger_diretamente_fluxo_atual: sim_fluxo_atual_ainda_transitorio
blocos_identicos: 2
blocos_com_shadow_gap: 1
blocos_parcialmente_comparaveis: 2
blocos_nao_comparaveis: 0
divergencias_classificadas: True
validacao_v4j_ok: True
```

---

## 5. Comparação por bloco

### 5.1. Extrato passado

```text
qtd_saida=114
qtd_pacote=114
qtd_identica=True
chaves_intersecao=114
chaves_apenas_saida=0
chaves_apenas_pacote=0
status=identico
```

Interpretação:

```text
EXTRATO_PASSADO_ADERENTE_AO_PACOTE_REPLAY=sim
```

---

### 5.2. Extrato futuro

```text
qtd_saida=156
qtd_eventos_pacote=156
qtd_pagamentos_pacote=156
qtd_identica_eventos=True
qtd_identica_pagamentos=True
chaves_intersecao_pagamentos=156
chaves_apenas_saida=0
chaves_apenas_pacote=0
status=identico
```

Interpretação:

```text
EXTRATO_FUTURO_ADERENTE_AO_PACOTE_LEDGER_OPERACIONAL=sim
```

---

### 5.3. Lotes ativos e exauridos

```text
lotes_ativos_qtd_saida=5
lotes_exauridos_qtd_saida=13
lotes_saida_total=18
estado_lotes_final_qtd_pacote=21
lotes_intersecao=18
lotes_apenas_saida=0
lotes_apenas_estado=3
status=shadow_gap
```

Interpretação:

```text
LOTES_SAIDA_CONTIDOS_NO_ESTADO_TEMPORAL=sim
ESTADO_TEMPORAL_TEM_3_LOTES_EXTRAS=sim
LACUNA=normalizar_estado_temporal_para_base_observavel_da_saida
```

Essa lacuna não é regressão da V4J. Ela indica que o `PacoteEstadoTemporal` ainda preserva três lotes que a saída observável já filtra/neutraliza na situação atual.

---

### 5.4. Resumo patrimonial

```text
qtd_metricas_saida=7
qtd_estado_lotes_final=21
status=parcial_comparavel
tem_valor_original_total=False
tem_patrimonio_liquido_atual=False
tem_rendimento_liquido_atual=False
```

Interpretação:

```text
RESUMO_PATRIMONIAL_AINDA_NAO_DERIVAVEL_DIRETAMENTE_DO_PACOTE_ESTADO_TEMPORAL=sim
```

A comparação é parcial porque o `PacoteEstadoTemporal` ainda não expõe, como contrato próprio, os mesmos campos observáveis usados pelo fechamento patrimonial da saída.

---

### 5.5. Auditoria

```text
auditoria_saida_presente=True
auditoria_temporal_presente=True
validacao_temporal_global_ok=True
qtd_chaves_auditoria_saida=462
saida_chama_ledger_diretamente=sim_fluxo_atual_ainda_transitorio
usa_retorno_ledger_dict_legado=True
status=parcial_comparavel
```

Interpretação:

```text
AUDITORIA_TEMPORAL_SHADOW_VALIDADA=sim
AUDITORIA_DA_SAIDA_AINDA_NAO_CONSOME_BLOCO_TEMPORAL_SHADOW=sim
```

---

## 6. Evidência runtime — aplicação principal

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

## 7. Auditoria dos critérios de aceite

```text
py_compile_auditoria_v4j=True
validacao_v4j_ok=True
saida_canonica_identica_dupla_execucao=True
validacao_agregador_ok=True
erros_bloqueantes_agregador_total=0
fonte_primaria_switching_ledger=switching_canonico
usa_planilha_bruta_como_fonte_primaria=False
divergencias_classificadas=True
principal_py_executou_sem_erro=True
relatorio_operacional_v225_gerado=True
git_diff_check_ok=True
worktree_limpa=True
```

---

## 8. Estado Git local após validação

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

## 9. Decisão sobre próxima etapa

A V4J passou, mas o diagnóstico indica uma lacuna relevante antes de integrar bloco shadow temporal à auditoria da saída:

```text
lotes_status=shadow_gap
estado_lotes_final_qtd_pacote=21
lotes_saida_total=18
lotes_apenas_estado=3
```

Decisão:

```text
SEGUIR_PARA_V4K_DIRETO=nao
SEGUIR_PARA_V4K0=sim
```

---

## 10. Próxima microetapa recomendada

```text
V17-F0-V.4K0 — Normaliza comparação shadow de lotes/estado temporal contra base observável da saída
```

Tipo sugerido:

```text
EXECUTÁVEL / DIAGNÓSTICO-CORREÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Investigar os três lotes presentes apenas no PacoteEstadoTemporal, identificar se são origens migradas, destinos sintéticos, resíduos de estado ou duplicidades transitórias, e normalizar a comparação shadow para a mesma base observável da saída antes de anexar bloco temporal à auditoria.
```

Critérios esperados:

```text
lotes_apenas_estado_identificados=True
motivo_lotes_apenas_estado_classificado=True
comparacao_lotes_normalizada=True
saida_canonica_identica_dupla_execucao=True
sem_alteracao_observavel=True
```

---

## 11. Conclusão

A V4J está aprovada por diagnóstico runtime. Extrato passado e extrato futuro já coincidem com os pacotes temporais agregados em quantidade e chaves principais. A lacuna remanescente está concentrada na comparação entre lotes da saída e `PacoteEstadoTemporal`, com três lotes presentes apenas no estado temporal.

Portanto, antes da V4K, a rota segura é abrir a V4K0 para normalizar a comparação shadow de lotes/estado temporal contra a base observável da saída.

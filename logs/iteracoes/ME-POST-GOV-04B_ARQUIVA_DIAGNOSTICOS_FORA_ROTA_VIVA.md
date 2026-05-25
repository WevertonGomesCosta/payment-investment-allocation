# ME-POST-GOV-04B — Arquivamento fora da rota viva dos diagnósticos transitórios

## Objetivo

Aplicar fisicamente as decisões `ARQUIVAR_FORA_ROTA_VIVA` registradas na ME-POST-GOV-03.

A decisão operacional desta microetapa foi remover os scripts do namespace ativo `scripts/diagnostico/`, preservando sua rastreabilidade pelo histórico Git. Essa escolha evita criar uma segunda rota executável de diagnósticos históricos e mantém o namespace ativo limitado ao gate permanente e aos scripts ainda pendentes de substituição por evidência estática.

## Baseline de entrada

```text
BASELINE: main
HEAD: 137b5725dfe6d02796a63645fca526820865f01a
ULTIMO_MERGE: PR #366 — ME-POST-GOV-04A remove diagnósticos imediatos
```

## Escopo permitido

```text
scripts/diagnostico/*
logs/iteracoes/*
```

## Escopo proibido

```text
aplicacao/*
nucleo/*
dados/*
relatorios/principais/*
saidas/*
```

A ME-POST-GOV-04B não altera motor, replay, ledger, ranking, saída canônica, contrato mestre, modelo oficial ou regra econômica.

## Auditoria de entrada enviada pelo usuário

```text
git fetch origin: aprovado
git checkout me-post-gov-04b-arquiva-fora-rota-viva: aprovado
git status --short: vazio
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py: aprovado
python -B aplicacao/principal.py: aprovado
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos: aprovado
```

Resultado V4Z reportado:

```text
entrada_limpa_etapa5_ok=True
contexto_operacional_canonico_limpo=True
io_incompativel=[]
sentinelas_no_nucleo={}
```

## Scripts removidos nesta microetapa

Foram removidos fisicamente 26 scripts classificados como `ARQUIVAR_FORA_ROTA_VIVA`:

```text
scripts/diagnostico/auditar_aba_tabela_operacional_pagamentos_v17_f0_s7i.py
scripts/diagnostico/auditar_amostras_salario_sem_recebido_e_sem_aporte_v17_f0_s4.py
scripts/diagnostico/auditar_classes_divergencias_valores_v17_c10.py
scripts/diagnostico/auditar_competicao_recebidos_49_aprovados_v17_f0_t4.py
scripts/diagnostico/auditar_divergencias_salarios_recebidos_v17_f0_s1.py
scripts/diagnostico/auditar_duplicidades_code_nucleo_v17_e1_b.py
scripts/diagnostico/auditar_lacuna_integracao_temporal_v17_f0_s2.py
scripts/diagnostico/auditar_precedencia_intradiaria_recebidos_v17_f0_t7.py
scripts/diagnostico/auditar_recomendacoes_pagamento_v17_f0_u0.py
scripts/diagnostico/auditar_reconciliacao_temporal_v17_f0_s0.py
scripts/diagnostico/auditar_saida_canonica_v17_a4.py
scripts/diagnostico/auditar_saldos_saida_auxiliar_v17_f0_u7pre.py
scripts/diagnostico/auditar_semantica_dados_v17_a3.py
scripts/diagnostico/auditar_tabela_operacional_pagamentos_v17_f0_s7h.py
scripts/diagnostico/auditar_transicao_temporal_switching_v17_d0.py
scripts/diagnostico/auditar_uso_operacional_tabela_pagamentos_v17_f0_s7j.py
scripts/diagnostico/classificar_bloqueios_v17_a0_2.py
scripts/diagnostico/classificar_divergencias_pacote_saida_v17_c4.py
scripts/diagnostico/classificar_pagamentos_sem_lote_v17_f0_t0.py
scripts/diagnostico/exportar_saida_operacional_auxiliar_pagamentos_v17_f0_u4.py
scripts/diagnostico/integrar_saida_operacional_pagamentos_multifonte_v17_f0_u3.py
scripts/diagnostico/investigar_fontes_temporais_sem_lote_v17_f0_t1.py
scripts/diagnostico/reconciliar_recebidos_concorrencia_sem_lote_v17_f0_t2.py
scripts/diagnostico/testar_alocacao_conjunta_recebidos_sem_lote_v17_f0_t3.py
scripts/diagnostico/validar_canonizacao_v17_a1.py
scripts/diagnostico/validar_invariantes_extrato_futuro.py
```

## Scripts não alterados nesta microetapa

O gate permanente foi preservado:

```text
scripts/diagnostico/auditar_nucleo_vivo_v4z.py
```

Os 11 scripts classificados como `SUBSTITUIR_POR_EVIDENCIA_ESTATICA` não foram removidos nem alterados nesta microetapa.

## Decisão da microetapa

```text
STATUS: ARQUIVAMENTO_FORA_ROTA_VIVA_APLICADO
ALTERA_RUNTIME: false
ALTERA_NUCLEO: false
ALTERA_APLICACAO: false
ALTERA_REGRA_ECONOMICA: false
PROXIMA_ACAO: VALIDAR_PR_E_EXECUTAR_GATES
```

## Validação esperada

Após checkout da branch ou após merge, rodar:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos
```

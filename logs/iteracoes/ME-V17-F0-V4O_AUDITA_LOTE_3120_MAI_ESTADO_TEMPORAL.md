# ME-V17-F0-V4O — Audita Lote 3120 mai na Etapa 4

## Identificacao

- MICROETAPA: ME-V17-F0-V4O
- VERSAO_CANDIDATA: V17-F0-V.4O
- TIPO: EXECUTAVEL / DIAGNOSTICO TEMPORAL / SEM ALTERACAO OBSERVAVEL
- BASELINE_DE_ENTRADA: V17-F0-V.4N.1
- BASELINE_COMMIT_ENTRADA: e7171005af6475b9491dae51a5b8bb5a3fc54b84
- ALTERA_CODIGO: sim
- ALTERA_REPLAY_EFETIVO: nao
- ALTERA_LEDGER_EFETIVO: nao
- ALTERA_ESTADO_TEMPORAL_EFETIVO: nao
- ALTERA_SAIDA_CANONICA_PADRAO: nao
- ALTERA_SAIDA_OBSERVAVEL_PADRAO: nao
- ALTERA_CONSOLE: nao
- ALTERA_XLSX: nao
- ALTERA_DADOS: nao
- ALTERA_CACHE: nao

## Objetivo

Rastrear o Lote 3120 mai no inventario canonico, replay passado, ledger, PacoteEstadoTemporal, extrato passado e situacao atual, identificando a camada onde aparecem saldo negativo, classificacao como exaurido e rendimento liquido negativo.

## Arquivos criados

```text
scripts/diagnostico/auditar_lote_3120_mai_estado_temporal_v4o.py
logs/iteracoes/ME-V17-F0-V4O_AUDITA_LOTE_3120_MAI_ESTADO_TEMPORAL.md
```

## Escopo do diagnostico

O script rastreia o lote nas seguintes origens:

```text
saida_extrato_passado
saida_extrato_futuro
saida_lotes_ativos
saida_lotes_exauridos
replay_log_movimentos_passados
replay_estado_lotes_passado
replay_audit_trilha_pagamentos_passados
ledger_eventos_temporais
ledger_fifo_candidatos_avaliados
ledger_saldos_por_lote
ledger_fontes_elegiveis_por_pagamento
estado_lotes_por_data
estado_lotes_final
estado_saldos_por_lote
estado_fontes_disponiveis_por_data
dados_operacionais_inventario_canonico
dados_operacionais_inventario_lotes_expandido
dados_operacionais_lotes_canonicos
dados_operacionais_recebidos_canonicos
```

## Criterios de aprovacao diagnostica

A V4O deve ser considerada aprovada apenas se o diagnostico retornar:

```text
origem_do_saldo_negativo_identificada=True
origem_da_exaustao_incorreta_identificada=True
origem_do_rendimento_negativo_identificada=True
pagamentos_que_consumiram_lote_listados=True
saldo_modelo_vs_saldo_app_comparado=True
sem_alteracao_observavel=True
validacao_v4o_ok=True
```

## Comandos de validacao local

```bash
python -m py_compile scripts/diagnostico/auditar_lote_3120_mai_estado_temporal_v4o.py
python scripts/diagnostico/auditar_lote_3120_mai_estado_temporal_v4o.py --saldo-app 50 --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

## Proxima decisao

Se a validacao local passar, registrar:

```text
V17-F0-V.4O.1 — Registra diagnostico runtime do Lote 3120 mai na Etapa 4
```

Depois disso, definir a microcorrecao V4P somente com base na causa identificada pela V4O.

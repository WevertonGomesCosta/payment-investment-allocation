# ME-V17-F0-V4O.1 — Registra diagnóstico runtime refinado do Lote 3120 mai

## Identificação

- MICROETAPA: ME-V17-F0-V4O.1
- VERSAO_CANDIDATA: V17-F0-V.4O.1
- TIPO: DIAGNÓSTICO / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- BASELINE_DE_ENTRADA: V17-F0-V.4O.0a
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

## Evidência runtime

Comandos executados localmente:

```bash
git pull origin main
python -m py_compile scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py
python scripts/diagnostico/auditar_lote_3120_mai_replay_vs_saida_v4o0a.py --saldo-app 50 --sem-csv
python -B aplicacao/principal.py
git diff --check
git status -sb
```

Resultado central do diagnóstico:

```text
replay_saldo_final_lote_3120_identificado: True
replay_saldo_final_lote_3120: 50.52
saida_extrato_passado_saldo_negativo_identificado: True
saida_classifica_exaurido: True
saida_zerada: True
bruto_atual_saida: 0.0
liquido_atual_saida: 0.0
patrimonio_liquido_saida: 3088.95
rendimento_liquido_saida: -33.58
rendimento_negativo_saida_identificado: True
saldo_modelo_replay_vs_saldo_app_comparado: True
diferenca_saldo_app_menos_replay: -0.52
diferenca_replay_menos_saida_liquido_atual: 50.52
divergencia_replay_vs_saida_identificada: True
causa_classificada: True
causa_provavel: saida_observavel_classifica_como_exaurido_e_zera_lote_com_replay_saldo_positivo
sem_alteracao_observavel: True
validacao_v4o0a_ok: True
```

## Interpretação causal

O replay passado mantém sobra positiva do Lote 3120 mai:

```text
Saldo Remanescente final no replay: 50.52
```

A saída observável, entretanto, classifica o mesmo lote como exaurido, zera `Bruto atual` e `Líq. atual`, e apresenta rendimento líquido negativo:

```text
Status: exaurido_por_saque_pos_switching
Bruto atual: 0.0
Líq. atual: 0.0
Rend. líq.: -33.58
```

A causa provável registrada é:

```text
saida_observavel_classifica_como_exaurido_e_zera_lote_com_replay_saldo_positivo
```

## Validação operacional complementar

`python -B aplicacao/principal.py` executou sem erro e a saída ainda mostra o bug no console, confirmando que a V4O.0a foi apenas diagnóstica.

O `git diff --check` não apontou problemas e o `git status -sb` terminou limpo:

```text
## main...origin/main
```

## Decisão

```text
V4O_STATUS=APROVADA_COM_DIAGNOSTICO_REFINADO
V4O1_STATUS=REGISTRADA
BUG_LOTE_3120_CAUSA_CLASSIFICADA=sim
CORRIGIR_NA_SAIDA_OBSERVAVEL_COM_BASE_NO_REPLAY=sim
```

## Próxima microetapa

```text
V17-F0-V.4P — Corrige causa identificada do saldo/exaustão/rendimento do Lote 3120 mai
```

Tipo sugerido:

```text
EXECUTÁVEL / MICROCORREÇÃO CAUSAL / COM ALTERAÇÃO OBSERVÁVEL CONTROLADA
```

Objetivo sugerido:

```text
Ajustar a classificação observável de lotes exauridos/ativos para que lote com saldo remanescente positivo no replay não seja tratado como exaurido e zerado na situação atual.
```

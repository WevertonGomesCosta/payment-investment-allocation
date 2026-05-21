# ME-V17-F0-V4P.1 — Registra correção runtime do Lote 3120 mai

## Identificação

- MICROETAPA: ME-V17-F0-V4P.1
- VERSAO_CANDIDATA: V17-F0-V.4P.1
- TIPO: DOCUMENTAL / REGISTRO DE EVIDÊNCIA RUNTIME / SEM ALTERAÇÃO DE CÓDIGO
- BASELINE_DE_ENTRADA: V17-F0-V.4P.0a + V17-F0-V.4P.0b
- PR ASSOCIADO: #343
- MERGE COMMIT: 0d2dc32453a070c2cde542f649d1d1c3b8936a96
- ALTERA_CODIGO: não
- ALTERA_REPLAY_EFETIVO: não
- ALTERA_LEDGER_EFETIVO: não
- ALTERA_ESTADO_TEMPORAL_EFETIVO: não
- ALTERA_SAIDA_CANONICA_ESTRUTURAL: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

## Objetivo

Registrar formalmente que o bug do `Lote 3120 mai` foi corrigido em duas camadas observáveis:

1. Situação Atual — o lote deixa de ser exibido como exaurido quando o replay mantém saldo final positivo.
2. Pagamentos — Amostras Operacionais — os pagamentos realizados passam a exibir valores auditáveis do replay, eliminando `Saldo Antes` negativo e preservando o saldo remanescente final correto.

## Correção efetivamente consolidada

### V4P.0a

A V4P.0a restringiu a reclassificação observável por saldo final real do replay.

A regra anterior testada localmente, baseada no último saldo positivo intermediário, foi rejeitada porque reativava indevidamente lotes já exauridos. A regra consolidada passou a usar o saldo final real do replay, preservando zeros, e bloqueou reclassificação de lotes migrados por switching.

Evidência runtime pós-merge:

```text
lote_3120_corrigido=True
lote_3120_replay_saldo_final_preservado=True
lote_3120_liquido_atual_corrigido=True
lote_3120_rendimento_liquido_nao_negativo_por_zeragem_incorreta=True
qtd_lotes_reclassificados_por_saldo_replay=1
lotes_reclassificados_por_saldo_replay=['Lote 3120 mai']
nenhum_lote_migrado_reclassificado=True
lotes_migrados_reclassificados=[]
nenhum_lote_em_ativos_e_exauridos=True
lotes_em_ativos_e_exauridos=[]
validacao_v4p0a_ok=True
```

### V4P.0b

A V4P.0b corrigiu a amostra observável de pagamentos realizados. A seção de pagamentos passou a preferir os valores auditáveis do replay passado quando há correspondência por data, descrição, lote e valor líquido.

Evidência runtime pós-merge:

```text
lote_3120_situacao_atual_corrigida=True
lote_3120_pagamentos_realizados_corrigidos=True
nenhum_saldo_antes_negativo_para_lote_3120=True
saldo_remanescente_final_pagamentos_lote_3120=50.52
saldo_final_replay_lote_3120=50.52
pagamentos_realizados_console_consistente_com_replay=True
sem_regressao_lotes_ativos_exauridos=True
validacao_v4p0b_ok=True
```

Linhas auditadas na amostra operacional:

```text
2026-05-20 | Cartão Azul | Lote 3120 mai | Saldo Antes 2987.71 | Rem. 69.57
2026-05-20 | Condomínio  | Lote 3120 mai | Saldo Antes 69.57   | Rem. 50.52
2026-05-15 | Internet    | Lote 3120 mai | Saldo Antes 3114.52 | Rem. 2981.97
```

## Estado observável final do lote

Na Situação Atual, o `Lote 3120 mai` passa a ser exibido como ativo:

```text
Lote 3120 mai | ativo
Bruto atual: 50.52
Líq. atual: 50.52
Patr. líq.: 3139.47
Rend. líq.: 16.94
```

O lote não aparece simultaneamente em ativos e exauridos.

## Validações executadas em main pós-merge

Comandos executados localmente após `git pull origin main`:

```bash
python -m py_compile nucleo/saida_observavel.py
python -m py_compile aplicacao/console/principal.py
python -m py_compile scripts/diagnostico/auditar_correcao_lote_3120_mai_v4p0a.py
python -m py_compile scripts/diagnostico/auditar_pagamentos_realizados_lote_3120_v4p0b.py

python scripts/diagnostico/auditar_correcao_lote_3120_mai_v4p0a.py --sem-csv
python scripts/diagnostico/auditar_pagamentos_realizados_lote_3120_v4p0b.py --sem-csv
python -B aplicacao/principal.py

git diff --check
git status -sb
```

Resultado operacional:

```text
principal.py executou sem erro
saída operacional gerada em saidas/oficial/relatorio_operacional_v225.xlsx
git diff --check sem erro
git status -sb limpo em main
```

## Decisão

```text
V4P_STATUS=APROVADA
V4P0A_STATUS=APROVADA
V4P0B_STATUS=APROVADA
V4P1_STATUS=REGISTRADA
BUG_LOTE_3120_SITUACAO_ATUAL_CORRIGIDO=sim
BUG_LOTE_3120_AMOSTRA_PAGAMENTOS_CORRIGIDO=sim
REGRESSAO_OBSERVAVEL_DETECTADA=nao
```

## Observação arquitetural

A correção consolidada permanece na camada observável. Ela não altera replay, ledger, regras econômicas, dados financeiros, cache BCB ou estrutura canônica dos pacotes temporais.

## Próxima microetapa recomendada

```text
V17-F0-V.4Q — Audita fechamento funcional da Etapa 4 após correção do Lote 3120 mai
```

Tipo sugerido:

```text
EXECUTÁVEL / DIAGNÓSTICO FINAL / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo sugerido:

```text
Validar replay, ledger, PacoteEstadoTemporal, PacoteAuditoriaTemporal, saída canônica, saída observável, console e XLSX depois da correção V4P.
```

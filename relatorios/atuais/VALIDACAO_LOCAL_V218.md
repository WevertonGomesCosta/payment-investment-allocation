# VALIDAÇÃO LOCAL — V218

## Comandos executados

```bash
python scripts/diagnostico/auditar_calculo_dias_lotes_v218.py
python scripts/diagnostico/verificar_release_baseline.py
```

## Resultado do diagnóstico V218

```text
CSV: saidas/diagnostico/auditoria_calculo_dias_lotes_v218_real.csv
CSV: saidas/diagnostico/auditoria_lote_5680_abr_v218_real.csv
CSV: saidas/diagnostico/auditoria_calculo_dias_duplicacoes_v218.csv
=== AUDITORIA CALCULO DIAS LOTES V218 ===
versao: V218
data_referencia: 2026-04-27
lotes_auditados: 16
lote_5680_abr_linhas: 1
lote_5680_abr_dias_corridos_v218: 13
lote_5680_abr_dias_uteis_v218: 8
lote_5680_abr_dias_recebimento_ate_aplicacao: 8
lote_5680_abr_data_referencia_usada: 2026-04-27
duplicacoes_criticas: 0
status: calculo_dias_canonico_v218_validado
```

## Resultado do release checker

```text
OK - release baseline validado para V218
```

## Lote auditado: Lote 5680 abr.

| Campo | Valor |
|---|---:|
| Recebimento | 2026-04-06 |
| Aplicação | 2026-04-14 |
| Data de referência usada | 2026-04-27 |
| Dias corridos V218 | 13 |
| Dias úteis V218 | 8 |
| Dias recebimento → aplicação | 8 |
| Correção aplicada | sim |

## Interpretação

O valor antigo de 8 dias corridos correspondia ao intervalo entre recebimento e aplicação. A V218 corrige a idade do investimento para usar a data de aplicação como origem e a data atual/de referência como destino.

## Auditoria de duplicação

A auditoria encontrou `duplicacoes_criticas: 0` para saídas/auditorias de identificação temporal. Permanecem usos não críticos/documentados de `data_base_fiscal` em rotinas fiscais ou econômicas internas, onde a semântica não é a mesma de exibição de `Dias corridos`/`Dias úteis`.

## Higiene de pacote

- `__pycache__`: ausente após limpeza final.
- `.pyc`: ausente após limpeza final.
- Release checker: aprovado para V218.

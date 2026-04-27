# CORREÇÃO DO CÁLCULO DE DIAS CORRIDOS E DIAS ÚTEIS — V218

## Status

`V218_CALCULO_DIAS_LOTES_CANONICO`

A V218 usa a V217 apenas como candidata diagnóstica e não promove baseline.

## Problema corrigido

A auditoria do lote `Lote 5680 abr.` mostrou que a tabela de lotes ativos podia usar uma referência temporal incorreta para a idade do investimento. O caso observado era:

```text
Recebimento: 2026-04-06
Aplicação:  2026-04-14
Dias corridos exibidos: 8
Dias úteis exibidos:    0
```

Esse resultado indicava uso indevido de intervalo relacionado ao recebimento/aplicação ou ao último uso, em vez da data atual/de referência da execução.

## Regra V218

Para identificação temporal de lote:

```text
dias_corridos = data_referencia_usada - data_aplicacao
dias_uteis    = dias de rendimento entre D+1 da aplicação e a data_referencia_usada
```

Critério de referência:

- lote ativo: usar `contexto.execucao.data_referencia`;
- lote exaurido: usar `Último uso`, quando existir, preservando leitura histórica;
- nunca usar `data_recebimento` para idade do investimento;
- nunca usar `data_base_fiscal` como fonte de exibição de idade do lote.

## Implementação

Funções centralizadas adicionadas em `nucleo/calendario_financeiro.py`:

- `contar_dias_corridos_lote(...)`
- `contar_dias_uteis_lote(...)`
- `calcular_dias_lote(...)`

Módulos ajustados para consumir a regra canônica:

- `nucleo/saida_canonica.py`
- `nucleo/replay_passado_controlado.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`

## Auditoria de duplicação

A V218 remove a função local `_contar_dias_uteis_economicos_lote(...)` do script de auditoria diária e passa a usar `calcular_dias_lote(...)`.
Cálculos fiscais internos de IOF/IR em `nucleo_financeiro_minimo.py` permanecem separados porque medem idade fiscal/rendimento, não idade exibida do investimento.

## Diagnóstico

Executar:

```bash
python scripts/diagnostico/auditar_calculo_dias_lotes_v218.py
```

Arquivos gerados:

- `saidas/diagnostico/auditoria_calculo_dias_lotes_v218_real.csv`
- `saidas/diagnostico/auditoria_lote_5680_abr_v218_real.csv`
- `saidas/diagnostico/auditoria_calculo_dias_duplicacoes_v218.csv`


## Resultado observado na validação local

Para `Lote 5680 abr.`:

```text
data_referencia: 2026-04-27
dias_corridos_v218: 13
dias_uteis_v218: 8
dias_recebimento_ate_aplicacao: 8
```

Assim, o valor 8 foi preservado apenas como diagnóstico do intervalo `Recebimento → Aplicação`, mas deixou de ser usado como idade do investimento ativo.

## Decisão

```text
V218_APROVADA_COMO_CORRECAO_FUNCIONAL_CANDIDATA
NAO_PROMOVER_BASELINE_AINDA
```

A próxima etapa deve voltar ao gate econômico dos aportes planejados, agora usando os dias corrigidos.

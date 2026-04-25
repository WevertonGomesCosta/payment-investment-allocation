# HOTFIX_UTILITARIOS_SERIES_V207

## Status

APLICADO COMO HOTFIX ESTRUTURAL SOBRE A V206.

## Erro corrigido

A execução de `python aplicacao/principal.py` falhava em `nucleo/auditoria_temporal_decisao_local.py` ao chamar `_rotulo_fonte(item)` com `item` vindo de `DataFrame.iterrows()`. Nesse caso, `item` é um `pandas.Series`.

A versão V206 de `_rotulo_fonte` usava a expressão `(candidato or {})`, válida para `dict`, mas inválida para `pandas.Series`, gerando:

```text
ValueError: The truth value of a Series is ambiguous.
```

## Correção aplicada

Em `nucleo/utilitarios_neutros.py`, os helpers semânticos centralizados passaram a usar acesso neutro por campo, compatível com:

- `dict`;
- `pandas.Series`;
- objetos com método `.get(...)`;
- objetos com atributo correspondente.

Foram adicionados helpers internos de baixo risco:

- `_valor_ausente(...)`;
- `_valor_campo(...)`;
- `_primeiro_campo_texto(...)`.

Foram ajustados:

- `_rotulo_fonte(...)`;
- `_fonte_id(...)`;
- `_split_fontes_compostas(...)`.

## Escopo preservado

Não houve alteração de regra econômica, motor de pagamentos, switching, contrato mestre, modelo matemático-estatístico-financeiro ou regra de recebidos/aportes futuros.

## Validação mínima

- chamada direta de `_rotulo_fonte(pd.Series(...))`: OK;
- chamada direta de `_fonte_id(pd.Series(...))`: OK;
- `python aplicacao/principal.py`: OK;
- release checker: OK para V207.

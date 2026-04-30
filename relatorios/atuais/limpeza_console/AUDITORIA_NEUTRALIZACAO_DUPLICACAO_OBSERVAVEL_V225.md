# Auditoria de neutralização de duplicação observável — V225

## Identificação

- Baseline: V225
- Data/hora local da auditoria: 2026-04-30T09:20:29
- Escopo:
  - `aplicacao/console/secoes_financeiras.py`
  - `aplicacao/console/secoes_canonicas.py`
  - `nucleo/saida_observavel.py`

## Decisão aplicada

A função antiga abaixo foi neutralizada:

```text
aplicacao/console/secoes_financeiras.py::render_secao_situacao_atual
```

A fonte única autorizada para os dados observáveis da Situação Atual passa a ser:

```text
nucleo/saida_observavel.py
```

Renderizadores autorizados:

```text
aplicacao/console/principal.py
nucleo/gerar_planilha_operacional.py
```

## Classificação de aplicacao/console/secoes_canonicas.py

```text
RISCO: há referência externa potencialmente operacional a secoes_canonicas/render_secao_canonicas.
```

## Referências encontradas — render_secao_canonicas

```text
aplicacao/console/secoes_canonicas.py:6:def render_secao_canonicas(*, carteira_canonica, dados_operacionais, switching_shadow, severidade_carteira, severidade_inventario, severidade_gastos, severidade_lotes_shadow, severidade_eventos_shadow, severidade_triagem, severidade_nucleo, resumo_inventario, resumo_gastos, validacao_carteira, validacao_inventario, validacao_gastos, resumo_lotes_shadow, auditoria_eventos_shadow, reconciliacao_shadow, auditoria_triagem, auditoria_nucleo):
```

## Referências encontradas — secoes_canonicas

```text
relatorios/atuais/INVENTARIO_RASTREADO_POS_LIMPEZA.md:8:aplicacao/console/secoes_canonicas.py
relatorios/atuais/RELATORIO_CONSOLIDADO_BASELINES_HISTORICAS_V031_V060.md:583:  - `aplicacao/console/secoes_canonicas.py`
Binary file relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv matches
```

## Referências encontradas — render_secao_situacao_atual

```text
aplicacao/console/principal.py:81:def _render_secao_situacao_atual(contexto_baseline, saida_canonica, resumo_fechamento, resumo_recebidos) -> None:
aplicacao/console/principal.py:222:    _render_secao_situacao_atual(
aplicacao/console/secoes_financeiras.py:288:def render_secao_situacao_atual(*args, **kwargs):
aplicacao/console/secoes_financeiras.py:305:        "render_secao_situacao_atual em aplicacao.console.secoes_financeiras "
```

## Referências encontradas — saida_observavel

```text
aplicacao/console/principal.py:25:from nucleo.saida_observavel import (
aplicacao/console/secoes_financeiras.py:294:        nucleo/saida_observavel.py
aplicacao/console/secoes_financeiras.py:306:        "foi neutralizada. Use nucleo.saida_observavel.py como fonte Ãºnica "
nucleo/gerar_planilha_operacional.py:24:from nucleo.saida_observavel import construir_blocos_situacao_atual
```

## Restrições respeitadas

Não houve alteração em:

- motor econômico;
- replay;
- pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline.

A alteração ficou restrita à neutralização de uma função legada de apresentação e ao registro documental da auditoria.

## Validação esperada

```bash
python -m py_compile aplicacao/console/secoes_financeiras.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
python aplicacao/principal.py
```

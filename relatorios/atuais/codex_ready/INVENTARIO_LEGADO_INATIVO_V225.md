# Inventário de legado inativo — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T13:16:25
- Escopo: classificação final da rota oficial Codex-ready

## `aplicacao/console/secoes_financeiras.py`

- Sem uso operacional na rota oficial: SIM
- Neutralizado como legado: NÃO

Referências na rota oficial:

```text
nenhuma referência encontrada
```

Referências fora de relatórios, incluindo documentação/scripts auxiliares:

```text
AGENTS.md:81:- `aplicacao/console/secoes_financeiras.py`;
Binary file relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv matches
aplicacao/console/secoes_financeiras.py:108:def render_secao_amostras_pagamentos(*, pagamentos_realizados=None, pagamentos_proximos=None):
aplicacao/console/secoes_financeiras.py:260:        "render_secao_situacao_atual em aplicacao.console.secoes_financeiras "
```

## `aplicacao/console/secoes_canonicas.py`

- Neutralizado como legado: NÃO

Referências na rota oficial:

```text
nenhuma referência encontrada
```

Referências fora de relatórios, incluindo documentação/scripts auxiliares:

```text
AGENTS.md:82:- `aplicacao/console/secoes_canonicas.py`.
Binary file relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv matches
aplicacao/console/secoes_canonicas.py:6:def render_secao_canonicas(*, carteira_canonica, dados_operacionais, switching_shadow, severidade_carteira, severidade_inventario, severidade_gastos, severidade_lotes_shadow, severidade_eventos_shadow, severidade_triagem, severidade_nucleo, resumo_inventario, resumo_gastos, validacao_carteira, validacao_inventario, validacao_gastos, resumo_lotes_shadow, auditoria_eventos_shadow, reconciliacao_shadow, auditoria_triagem, auditoria_nucleo):
```

## Regra para Codex

Qualquer alteração que afete dados mostrados simultaneamente no console e na planilha deve seguir esta ordem:

```text
1. alterar ou criar contrato em nucleo/saida_observavel.py
2. renderizar no console sem recalcular
3. renderizar na planilha sem recalcular
4. validar python scripts/validacao/validar_rota_oficial_v225.py
```

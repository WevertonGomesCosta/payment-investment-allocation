# Inventário de legado inativo — V225

## Identificação

- Baseline: V225
- Data/hora local: 2026-04-30T12:44:20
- Escopo: inventário documental para preparação Codex-ready
- Remoção de arquivos nesta etapa: nenhuma

## Legado preservado

### `aplicacao/console/secoes_financeiras.py`

Status: preservado.

Situação atual:

- `render_secao_situacao_atual` está neutralizada: SIM
- console oficial não importa mais `secoes_financeiras.py`: SIM

Decisão:

- não remover ainda;
- não reativar funções antigas diretamente;
- se algum bloco precisar voltar ao console/planilha, migrar primeiro a fonte para `nucleo/saida_observavel.py`.

Referências operacionais encontradas para `secoes_financeiras` fora de relatórios:

```text
AGENTS.md:51:- console sem dependÃªncia operacional de `secoes_financeiras.py`: SIM
AGENTS.md:108:- `aplicacao/console/secoes_financeiras.py`;
aplicacao/console/secoes_financeiras.py:260:        "render_secao_situacao_atual em aplicacao.console.secoes_financeiras "
Binary file relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv matches
```

### `aplicacao/console/secoes_canonicas.py`

Status: legado não operacional aparente, preservado para auditoria futura.

Decisão:

- não remover nesta etapa;
- não reativar sem auditoria;
- caso alguma saída ali seja necessária, migrar primeiro para `nucleo/saida_observavel.py` ou `nucleo/saida_canonica.py`, conforme o caso.

Referências operacionais encontradas para `secoes_canonicas` fora de relatórios:

```text
AGENTS.md:109:- `aplicacao/console/secoes_canonicas.py`.
Binary file relatorios/atuais/auditoria_estrutura_repositorio/inventario_estrutura_repositorio_por_arquivo.csv matches
```

Referências operacionais encontradas para `render_secao_canonicas` fora de relatórios:

```text
aplicacao/console/secoes_canonicas.py:6:def render_secao_canonicas(*, carteira_canonica, dados_operacionais, switching_shadow, severidade_carteira, severidade_inventario, severidade_gastos, severidade_lotes_shadow, severidade_eventos_shadow, severidade_triagem, severidade_nucleo, resumo_inventario, resumo_gastos, validacao_carteira, validacao_inventario, validacao_gastos, resumo_lotes_shadow, auditoria_eventos_shadow, reconciliacao_shadow, auditoria_triagem, auditoria_nucleo):
```

## Fonte observável ativa

`nucleo/saida_observavel.py` está ativo e é usado por console e planilha.

Referências operacionais encontradas para `saida_observavel` fora de relatórios:

```text
AGENTS.md:23:python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
AGENTS.md:61:`nucleo/saida_observavel.py` Ã© a fonte Ãºnica para dados observÃ¡veis compartilhados entre console e planilha.
AGENTS.md:76:AlteraÃ§Ãµes em dados observÃ¡veis compartilhados devem ser feitas primeiro em `nucleo/saida_observavel.py`.
AGENTS.md:104:NÃ£o reativar diretamente arquivos ou funÃ§Ãµes legadas de apresentaÃ§Ã£o. Se uma informaÃ§Ã£o antiga precisar voltar ao console ou Ã  planilha, migrar primeiro o contrato de dados para `nucleo/saida_observavel.py`.
AGENTS.md:140:python -m py_compile aplicacao/principal.py aplicacao/console/principal.py nucleo/saida_observavel.py nucleo/gerar_planilha_operacional.py
aplicacao/console/principal.py:24:from nucleo.saida_observavel import (
aplicacao/console/secoes_financeiras.py:249:        nucleo/saida_observavel.py
aplicacao/console/secoes_financeiras.py:261:        "foi neutralizada. Use nucleo.saida_observavel.py como fonte Ãºnica "
nucleo/gerar_planilha_operacional.py:24:from nucleo.saida_observavel import construir_blocos_situacao_atual
```

## Riscos conhecidos

1. Reativar funções antigas de `secoes_financeiras.py` pode recriar divergência console × planilha.
2. Reativar `secoes_canonicas.py` pode recriar saídas paralelas fora do contrato atual.
3. Criar novos cálculos de apresentação diretamente em `aplicacao/console/principal.py` ou `nucleo/gerar_planilha_operacional.py` pode violar a fonte única `saida_observavel.py`.
4. Executar rotas alternativas que carreguem contexto separadamente pode recriar divergência por download/cache/contexto.

## Regra para Codex

Qualquer alteração que afete dados mostrados simultaneamente no console e na planilha deve seguir esta ordem:

```text
1. alterar ou criar contrato em nucleo/saida_observavel.py
2. renderizar no console sem recalcular
3. renderizar na planilha sem recalcular
4. validar python aplicacao/principal.py
```

## Arquivos que não foram removidos nesta etapa

- `aplicacao/console/secoes_financeiras.py`
- `aplicacao/console/secoes_canonicas.py`

## Próxima limpeza possível

Somente após validação da etapa Codex-ready:

1. auditar se `secoes_financeiras.py` ainda possui referência operacional;
2. remover funções legadas restantes em lote pequeno;
3. auditar `secoes_canonicas.py`;
4. mover legado não operacional para histórico ou remover com validação.

# 01_diagnostico_metadados_none.md — RD-2026-04-28-07

## Objetivo
Corrigir o mismatch entre rótulos humanos de `fechamento_atual` e chaves técnicas esperadas na seção `SITUAÇÃO ATUAL` do console.

## Evidências usadas
- `evidencias/busca_metadados_none.txt`
- `evidencias/busca_variaveis_metadados.txt`

## Diagnóstico
1. `render_secao_situacao_atual` lê chaves técnicas (`data_referencia`, `status_fechamento`, etc.).
2. `principal.py` montava `resumo_fechamento_situacao_atual` diretamente por `Métrica -> Valor`.
3. `saida_canonica.fechamento_atual` fornece rótulos humanos (`Data de referência`, `Status do fechamento econômico`, etc.).
4. Resultado: `get('data_referencia')` e correlatas retornavam `None` quando só os rótulos humanos estavam presentes.

## Microcorreção aplicada
- Arquivo alterado: `aplicacao/console/principal.py`.
- Implementado mapeamento explícito:
  - `Data de referência -> data_referencia`
  - `Status do fechamento econômico -> status_fechamento`
  - `Fonte do fechamento -> fonte_fechamento`
  - `Fechamentos com fallback CDI -> qtd_fechamentos_fallback_cdi`
  - `Último fator explícito CDI -> data_ultimo_fator_explicito_cdi`
  - `Data confirmada da série -> data_fechamento_confirmado`
- Incluída também `Leitura auditável -> observacao` para preservar a exibição textual quando disponível.

## Escopo preservado
Sem alteração em motor econômico, pagamentos, switching, função objetivo, dados oficiais, cache BCB/CDI, saída canônica e `requirements.txt`.

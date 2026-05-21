# ME-V17-F0-V4Q — Auditoria de fechamento funcional da Etapa 4

## Objetivo
Executar auditoria final pós V4P.0a/V4P.0b/V4P.1 validando replay, ledger, pacotes temporais, saída canônica, saída observável, console e XLSX sem alterar comportamento observável.

## Artefatos
- `scripts/diagnostico/auditar_fechamento_funcional_etapa4_v4q.py`

## Ajustes aplicados nesta revisão
- Remoção de hardcode de `nenhum_lote_migrado_reclassificado` e `rendimento_liquido_atual_nao_inflado_por_reclassificacao`.
- Cálculo de lotes migrados reclassificados com base em reclassificados por saldo replay e marca de migração por switching em `Status ciclo/Status`.
- Validação de `rendimento_liquido_atual_nao_inflado_por_reclassificacao` derivada dos critérios decisórios combinados.
- Ajuste de `xlsx_operacional_gerado` para evidenciar por stdout (`Saída operacional gerada em:`) ou por existência de `saidas/oficial/relatorio_operacional_v225.xlsx`.
- Inclusão explícita da chave `bloco_temporal_shadow_presente`.
- Ampliação de `validacao_v4q_ok` com os critérios decisórios solicitados.

## Nota sobre execução no ambiente Codex
- A tentativa de execução neste ambiente **pode** falhar em `aplicacao/principal.py` caso o insumo S6 não esteja disponível (`erro_csv_s6_ausente_sem_recomposicao_segura`).
- Essa condição é registrada apenas como contexto de ambiente de execução.
- **A conclusão final da microetapa V4Q fica condicionada à validação local** com os comandos oficiais.

## Validação local esperada
- `python -m py_compile scripts/diagnostico/auditar_fechamento_funcional_etapa4_v4q.py`
- `python scripts/diagnostico/auditar_fechamento_funcional_etapa4_v4q.py --sem-csv`
- `python -B aplicacao/principal.py`
- `git diff --check`
- `git status -sb`

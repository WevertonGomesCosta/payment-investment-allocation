# ME-PRE-ETAPA5-05_REFORMA_ETAPA4_ESTADO_TEMPORAL

## Objetivo
Implementar a reforma estrutural da Etapa 4 com EstadoTemporalInicial formal, cadeia canônica operacional e remoção de ContextoBaseline da rota viva.

## Baseline
- Branch local inicial: `work`.
- `origin` indisponível no ambiente, sem possibilidade de criar branch remota aqui.

## Arquivos alterados
- `nucleo/contexto_operacional_canonico.py` (novo ponto de entrada canônico Etapas 1-4).
- `nucleo/estado_temporal_inicial.py` (novo artefato formal da Etapa 4).
- `aplicacao/principal.py` (rota viva migrada para cadeia canônica + EstadoTemporalInicial).
- `aplicacao/console/principal.py` (sem import de ContextoBaseline).
- `nucleo/gerar_planilha_operacional.py` (sem import de ContextoBaseline).
- `nucleo/saida_canonica.py` (sem import de ContextoBaseline).
- `nucleo/contexto_baseline.py` removido fisicamente.

## Aderência contratual
- Etapa 4 agora produz `EstadoTemporalInicial` explicitamente.
- `pagamentos_temporais` é construído de `gastos_canonicos` (Etapa 3), incluindo contas futuras.
- `obrigacao_temporal=True` para todas as contas canônicas.
- Auditoria estrutural via `auditar_estado_temporal_inicial`.

## Migração rota viva
- `aplicacao/principal.py` usa `carregar_contexto_operacional_canonico` + `construir_estado_temporal_inicial`.
- Console/XLSX/saída canônica não importam `ContextoBaseline`.

## Etapa 5
- Não implementada nesta microetapa.

## Validações no Codex
- `python -m py_compile ...` ✅
- `python - <<'PY' ... EstadoTemporalInicial ...` ✅
- `python -B aplicacao/principal.py` ❌ erro de código legado em `nucleo/saida_canonica.py` (`_PRE_INVARIANTE_EXTRATO_FUTURO` não definido)
- `python scripts/diagnostico/auditar_nucleo_vivo_v4z.py --sem-arquivos` ❌ script ainda apontando para `nucleo/contexto_baseline.py`

## Riscos remanescentes
- Script de gate V4Z precisa ser atualizado para novo arquivo canônico.
- `nucleo/saida_canonica.py` possui erro em runtime não relacionado diretamente à nova camada temporal, mas bloqueia execução principal.

## Próxima etapa recomendada
- Corrigir `nucleo/saida_canonica.py` (`_PRE_INVARIANTE_EXTRATO_FUTURO`).
- Atualizar `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` para `nucleo/contexto_operacional_canonico.py`.
- Reexecutar validações de ponta a ponta.

## Atualização microetapa (desbloqueio runtime operacional)
- Escopo desta frente: corrigir apenas o bloqueio real de runtime em `python -B aplicacao/principal.py`.
- Correção aplicada: inicialização defensiva de variáveis de módulo em `nucleo/saida_canonica.py`:
  - `_PRE_INVARIANTE_EXTRATO_FUTURO = {}`
  - `_SOMBRA_DIVERGENCIAS_LEDGER = {}`
- Não houve alteração de regra econômica, Etapa 5, dados, ou recriação de `ContextoBaseline`.
- `scripts/diagnostico/auditar_nucleo_vivo_v4z.py` explicitamente **não** tratado como gate desta PR.

## Atualização microetapa (P1 fontes_temporais)
- Corrigida disponibilidade de `fontes_temporais` com lógica conservadora: `disponivel` -> `elegivel_na_data_pagamento` -> `elegivel_temporalmente` -> `False`.
- Corrigido `valor_estimado` em `fontes_temporais` com ordem: `valor_liquido_disponivel` -> `valor_bruto_disponivel` -> `valor_liquido` -> `valor` -> `0.0`, com conversão segura para `float`.
- Auditoria do `EstadoTemporalInicial` ampliada com: `qtd_fontes_temporais`, `qtd_fontes_disponiveis`, `qtd_fontes_indisponiveis`, `qtd_fontes_valor_positivo`.

## Atualização microetapa (regressão observável próximos pagamentos)
- Corrigida regressão em que console mostrava "sem linhas para exibir" em próximos pagamentos mesmo com obrigações futuras no `EstadoTemporalInicial`.
- `nucleo/saida_observavel.py` agora usa fallback observável por `estado_temporal_inicial.pagamentos_temporais` quando `saida_canonica.pagamentos_proximos_console(...)` vier vazio.
- Fallback renderiza apenas obrigações temporais futuras, ordenadas por data, com neutralidade econômica:
  - lote/fonte: `fonte_a_decidir` / `não decidido_etapa5`;
  - status: `obrigacao_temporal_futura_sem_decisao_etapa5`.
- Etapa 5 não foi implementada; não houve decisão de fonte/pacote/switching.

## Atualização microetapa (switching materializado aplicado na Etapa 4)
- `EstadoTemporalInicial` passou a aplicar eventos de `switching_canonico` no `inventario_temporal`.
- Cada evento de switching agora entra em `switching_temporal_realizado` com status temporal (`materializado`/`declarado`) e valor líquido migrado.
- Para switchings materializados:
  - lote origem passa para `migrado_por_switching`/`exaurido_por_switching` e deixa de ser ativo comum;
  - lote destino é criado/consolidado com `origem_canonica=switching_canonico`, `sintetico_pos_switching=True`, `origem_switching`, produto e valor migrado.
- Auditoria temporal ampliada com resumo de switchings (qtd e valor líquido migrado total) e bloqueios para ausência de origem/destino.
- Renderização da seção de lotes ativos passou a filtrar lotes migrados com base no `EstadoTemporalInicial`.
- Resumo patrimonial observável passou a usar eventos materializados de `EstadoTemporalInicial` como fallback quando métricas de origens migradas vierem zeradas da saída canônica.

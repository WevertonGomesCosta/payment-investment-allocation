# ME-V17-F0-V4S1 — Registro de execução dos comandos informativos (V4S)

## Contexto
Execução dos comandos solicitados para verificação informativa da microetapa V4S.

Data (UTC): 2026-05-21

## Comandos executados e resultados

### 1) `python -m py_compile scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py`
- Exit code: **1**
- Resultado:
  - `[Errno 2] No such file or directory: 'scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py'`
- Causa provável:
  - O arquivo alvo ainda não existe neste caminho no estado atual do repositório.

### 2) `python scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py --sem-csv`
- Exit code: **2**
- Resultado:
  - `python: can't open file '/workspace/payment-investment-allocation/scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py': [Errno 2] No such file or directory`
- Causa provável:
  - Mesma causa do comando 1: script inexistente no caminho informado.

### 3) `python -B aplicacao/principal.py`
- Exit code: **1**
- Resultado:
  - Exceção em runtime: `RuntimeError: erro_csv_s6_ausente_sem_recomposicao_segura`
  - Origem observada no traceback: `nucleo/matriz_elegibilidade_fontes_s7b.py` durante `_carregar_s6_df()`.
- Causa provável:
  - Ausência do CSV/insumo S6 esperado pelo fluxo operacional principal.

### 4) `git diff --check`
- Exit code: **0**
- Resultado:
  - Sem apontamentos de whitespace/error check no diff atual.

### 5) `git status -sb`
- Exit code: **0**
- Resultado:
  - Branch atual: `work`

## Observações de governança
- As falhas acima foram tratadas como **informativas** e **não bloqueantes**, conforme diretriz da microetapa.
- Este registro não abre Etapa 5 e não usa validações como condição de parada.

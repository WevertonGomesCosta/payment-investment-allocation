# ME-V17-F0-V4S — Auditoria estática de resíduos funcionais pós-Etapa 4

## Objetivo
Completar a microetapa V17-F0-V.4S com inventário estático (AST) de resíduos funcionais e duplicidades pós-Etapa 4, sem abrir Etapa 5 e sem alterações funcionais.

## Resposta ao comentário do Codex (precedência de categorias V4)
Correção aplicada: a classificação técnica dos diagnósticos V4 agora prioriza categorias específicas antes da categoria genérica `auditoria`.

Ordem implementada:
1. `normalizacao`
2. `equivalencia_runtime`
3. `runtime`
4. `correcao`
5. `fechamento`
6. `pacote`
7. `shadow`
8. `auditoria`
9. `outros`

Com isso, `auditoria` passa a ser fallback técnico, removendo o viés anterior.

## Principais achados
- Foram classificadas funções em `nucleo/saida_observavel.py` com acesso a contexto/replay.
- Foram classificadas funções com varredura genérica (`__dict__`, `iterrows`/`itertuples`/`to_dict`).
- Foram identificadas funções com correção/reconstrução observável baseada em replay.
- Foram identificadas duplicidades potenciais nas famílias:
  - valor original,
  - produto/carteira,
  - aplicação/base fiscal,
  - saldo/sacado/remanescente.
- Foram classificados diagnósticos V4 com classificação técnica e operacional.
- Foram classificados caminhos shadow por arquivo e por mapeamento explícito de trilhas críticas temporais.

## Classificação técnica e operacional dos diagnósticos V4
### Técnica
- `normalizacao`
- `equivalencia_runtime`
- `runtime`
- `correcao`
- `fechamento`
- `pacote`
- `shadow`
- `auditoria`
- `outros`

### Operacional
- `ativo_regressao`
- `historico_preservar`
- `candidato_arquivo_historico_futuro`
- `candidato_remocao_futura`

## Classificação operacional dos resíduos funcionais
Classes emitidas:
- `remover_agora`
- `manter_ate_etapa5`
- `migrar_para_contrato_futuro`
- `preservar_como_auditoria_historica`
- `manter_controlado`
- `investigar_antes_de_remover`

Cobertura mínima garantida:
- consulta contexto/replay em `saida_observavel`;
- varredura genérica via `__dict__`;
- iteração genérica em DataFrames;
- correção/reconstrução com replay;
- caminhos shadow;
- diagnósticos V4.

## Expansão de caminhos shadow (explícita)
Além do filtro por nome de arquivo, foi adicionado mapeamento explícito para:
- PacoteReplayPassado shadow
- PacoteLedgerTemporalOperacional shadow
- PacoteEstadoTemporal shadow
- PacoteAuditoriaTemporal shadow
- pacotes_temporais_agregados_saida
- bloco temporal shadow na auditoria da saída
- parâmetro incluir_temporal_shadow

## Critérios informativos emitidos pelo script
- `execucao_v4s_concluida=True`
- `inventario_residuos_emitido=True`
- `residuos_funcionais_identificados=<bool>`
- `duplicidades_potenciais_identificadas=<bool>`
- `saida_observavel_replay_classificado=<bool>`
- `funcoes_com_varredura_generica_classificadas=<bool>`
- `diagnosticos_v4_classificados=<bool>`
- `caminhos_shadow_classificados=<bool>`
- `nenhuma_remocao_automatica=True`
- `plano_limpeza_codigo_definido=<bool>`
- `residuos_bloqueantes_etapa5=<bool>`
- `recomendacao_abrir_etapa5=<bool>`
- `diagnostico_v4s_ok=True`

## Plano de limpeza funcional (informativo, por prioridade)
1. **Prioridade alta (investigar)**: varreduras genéricas em DataFrame e `__dict__` (risco de acoplamento oculto).
2. **Prioridade média (migrar contrato)**: reconstrução observável baseada em replay para contratos explícitos.
3. **Prioridade média (controlado)**: caminhos shadow temporais com rastreabilidade de uso.
4. **Prioridade baixa (histórico)**: diagnósticos V4 candidatos a histórico/arquivo futuro.

Nenhuma remoção automática foi realizada nesta microetapa.

## Recomendação informativa sobre Etapa 5
- `residuos_bloqueantes_etapa5=False` (do ponto de vista desta auditoria estática).
- `recomendacao_abrir_etapa5=False` (recomendação conservadora: avançar apenas após microetapa de limpeza controlada).

## Execução dos comandos informativos (não bloqueantes)
### 1) `python -m py_compile scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py`
- Exit code: **0**
- Resultado: compilação OK.

### 2) `python scripts/diagnostico/auditar_residuos_funcionais_pos_etapa4_v4s.py --sem-csv`
- Exit code: **0**
- Resultado: inventário emitido em `chave=valor` com critérios e contagens solicitadas.

### 3) `python -B aplicacao/principal.py`
- Exit code: **1**
- Resultado: `RuntimeError: erro_csv_s6_ausente_sem_recomposicao_segura`.
- Causa provável: ausência de insumo CSV S6 no ambiente.
- Tratamento: falha informativa e não bloqueante para V4S.

### 4) `git diff --check`
- Exit code: **0**
- Resultado: sem apontamentos.

### 5) `git status -sb`
- Exit code: **0**
- Resultado: branch `work`.

## Governança
- Não houve alteração de código funcional.
- Não houve abertura da Etapa 5.
- Não houve remoção automática de resíduos.
- Falhas informativas não foram usadas como condição de parada.

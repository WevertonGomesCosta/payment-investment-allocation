# V17-F0-V.4W — Remove resíduos legados da saída observável

- objetivo: limpar resíduos legados de reconstrução por contexto/replay em `nucleo/saida_observavel.py` após migração V4V.
- baseline V4V: `validacao_v4u_ok=true`, `validacao_v4v_ok=true`, consumo de pacote ativo e `origem_lotes_ativos_exauridos="snapshot_observavel_consolidado"`.
- arquivos alterados: `nucleo/pacote_saida_observavel_temporal.py`, `nucleo/saida_observavel.py`, `scripts/diagnostico/auditar_limpeza_saida_observavel_residuos_v4w.py`.
- helpers removidos: `somar_valores_sacados_por_lote`, `_lote_deve_ser_ativo_observavel_por_replay`.
- acessos diretos replay/contexto removidos da saída observável; não há `replay_passado`/`log_passado`/listas de lotes replay no arquivo.
- varreduras genéricas removidas: sem `fila=[contexto]`, sem inspeção `__dict__`, sem varreduras genéricas DataFrame para reconstrução observável.
- pacote enriquecido: `valores_sacados_por_lote` agora contém `bruto_sacado`, `liquido_sacado`, `imposto_sacado`, `valor_sacado_total`, `qtd_movimentos`.
- evidências V4U/V4V preservadas por execução dos auditores existentes.
- evidência Lote 3120 mai: bruto sacado 3093.76, líquido sacado 3088.95, saldo final 50.52, presente em ativos e ausente em exauridos.
- etapa 5 permanece fechada (`etapa5_pode_abrir_agora=false`).
- próxima microetapa recomendada: `V17-F0-V.4X`.

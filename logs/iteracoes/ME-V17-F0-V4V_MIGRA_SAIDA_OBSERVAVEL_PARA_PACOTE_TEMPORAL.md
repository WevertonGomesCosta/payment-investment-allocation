# V17-F0-V.4V — Migra saida_observavel para consumir PacoteSaidaObservavelTemporal

- objetivo: migrar `nucleo/saida_observavel.py` para consumir `PacoteSaidaObservavelTemporal` com fallback legado preservado.
- baseline V4U: `validacao_v4u_ok=true`, lote 3120 mai ativo com saldo final 50.52 e etapa 5 fechada.
- arquivos alterados: `nucleo/saida_observavel.py`, `aplicacao/console/principal.py`, `scripts/diagnostico/auditar_migracao_saida_observavel_pacote_temporal_v4v.py`.
- funções adaptadas: mapas de saldo/pagamentos/produto/valor original/aplicação + linhas consolidadas e amostras operacionais aceitando `pacote_saida_observavel_temporal` opcional.
- acessos agora preferenciais via pacote: `saldos_finais_replay_por_lote`, `pagamentos_replay_por_chave`, `aplicacoes_por_lote`, `produtos_por_lote`, `valores_originais_por_lote`, `valores_sacados_por_lote`.
- helpers legados preservados: cálculo legado por contexto/replay segue disponível quando pacote não é fornecido.
- evidências de equivalência: auditor V4V compara caminho legado vs caminho com pacote para realizados, próximos, lotes ativos e exauridos.
- evidências lote 3120 mai: presente em ativos, ausente em exauridos, saldo final 50.52.
- decisão: etapa 5 permanece fechada (`etapa5_pode_abrir_agora=false`).
- próxima microetapa: `V17-F0-V.4W`.

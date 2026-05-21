# ME-V17-F0-V4U — Cria PacoteSaidaObservavelTemporal

- Correção de base do PR aplicada para manter escopo apenas V4U.
- `nucleo/pacote_saida_observavel_temporal.py` continua **sem importar** `nucleo/saida_observavel.py`.
- Auditor V4U usa `nucleo.saida_observavel` apenas para montar snapshots consolidados de equivalência diagnóstica.
- Origem aplicada no pacote: `origem_lotes_ativos_exauridos=snapshot_observavel_consolidado` quando snapshots são fornecidos.
- Lote 3120 mai validado como ativo e ausente em exauridos no snapshot consolidado.
- Etapa 5 permanece fechada (`etapa5_pode_abrir_agora=False`).
- Próxima microetapa permanece V17-F0-V.4V.

- Nota curta: comentário Codex P1 endereçado; pacote agora lê campos reais do replay (incluindo Conta e Valor Conta), chave de pagamentos inclui ordem_original para evitar sobrescrita de eventos repetidos e valores_sacados_por_lote não depende apenas de "Valor"; Etapa 5 permanece fechada; V4V segue como próxima microetapa.

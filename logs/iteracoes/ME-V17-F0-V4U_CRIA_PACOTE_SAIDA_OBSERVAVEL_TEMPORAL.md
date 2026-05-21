# ME-V17-F0-V4U — Cria PacoteSaidaObservavelTemporal

- Objetivo: criar contrato substitutivo preparatório para remover, em V4V/V4W, a dependência direta de `saida_observavel` sobre contexto/replay.
- Baseline pós-V4T: interface Etapa 4→5 validada e Etapa 5 permanece fechada por resíduo arquitetural conhecido.
- Motivo arquitetural: isolar mapas substitutivos em pacote explícito sem alterar saída observável nesta microetapa.
- Escopo: `nucleo/pacote_saida_observavel_temporal.py`, diagnóstico V4U e este log.
- Arquivos alterados: os 3 acima; sem mudanças em `aplicacao/`, `dados/`, XLSX, runtime econômico e motores.
- Contrato criado: `PacoteSaidaObservavelTemporal` (`VERSAO_PACOTE_SAIDA_OBSERVAVEL_TEMPORAL=V17-F0-V.4U`).
- Mapas substitutivos: saldos finais replay por lote, pagamentos replay por chave textual estável, aplicações/produtos/valores por lote, valores sacados por lote.
- Evidências Lote 3120 mai: presente em ativos snapshot, ausente em exauridos snapshot, saldo final alvo ~50.52.
- Ausência de alteração observável: pacote usa `saida` somente como snapshot observável, sem recalcular/reclassificar lotes/extrato.
- Decisão: `etapa5_pode_abrir_agora=False` mantida.
- Próxima microetapa: V17-F0-V.4V.
- Comandos executados: py_compile (pacote e auditor), auditor V4U, auditor V4T, `python -B aplicacao/principal.py`, `git diff --check`, `git status -sb`.

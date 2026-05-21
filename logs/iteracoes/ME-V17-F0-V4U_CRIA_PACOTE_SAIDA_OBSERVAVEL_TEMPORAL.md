# ME-V17-F0-V4U — Cria PacoteSaidaObservavelTemporal

- Correção de base do PR aplicada para manter escopo apenas V4U.
- `nucleo/pacote_saida_observavel_temporal.py` continua **sem importar** `nucleo/saida_observavel.py`.
- Auditor V4U usa `nucleo.saida_observavel` apenas para montar snapshots consolidados de equivalência diagnóstica.
- Origem aplicada no pacote: `origem_lotes_ativos_exauridos=snapshot_observavel_consolidado` quando snapshots são fornecidos.
- Lote 3120 mai validado como ativo e ausente em exauridos no snapshot consolidado.
- Etapa 5 permanece fechada (`etapa5_pode_abrir_agora=False`).
- Próxima microetapa permanece V17-F0-V.4V.

- Nota curta: comentário Codex P1 endereçado; pacote agora lê campos reais do replay (incluindo Conta e Valor Conta), chave de pagamentos inclui ordem_original para evitar sobrescrita de eventos repetidos e valores_sacados_por_lote não depende apenas de "Valor"; Etapa 5 permanece fechada; V4V segue como próxima microetapa.

- Nota curta: comentário Codex P1 sobre campos dos snapshots consolidados foi endereçado; `Aplic.` e `Orig.` agora são reconhecidos; `valores_originais_por_lote` não recua para saldo atual quando `Orig.` está disponível; Etapa 5 permanece fechada; V4V continua como próxima microetapa.
## Nota de correção — comentário Codex P1 sobre valor sacado por lote

O comentário Codex P1 sobre `valores_sacados_por_lote` foi endereçado.

A V4U passa a tratar `Valor Conta` como identificador do valor total da despesa para chave de pagamento, mas não como valor sacado por lote.

Para `valores_sacados_por_lote`, o pacote passa a usar preferencialmente:

- `Líquido`;
- `Liquido`;
- `Valor Líquido`;
- `Valor Liquido`;
- `Valor`.

Essa distinção evita superestimação em pagamentos multifonte, nos quais `Valor Conta` pode se repetir em múltiplos movimentos enquanto o valor líquido representa o consumo efetivo de cada lote.

A Etapa 5 permanece fechada. A próxima microetapa segue sendo V17-F0-V.4V.

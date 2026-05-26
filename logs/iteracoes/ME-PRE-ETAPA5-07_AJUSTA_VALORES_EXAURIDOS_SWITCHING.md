# ME-PRE-ETAPA5-07 — Ajusta valores de lotes exauridos por switching e rótulo patrimonial pós-switching

- Ajustada a composição econômica observável de lotes origem encerrados por switching em `construir_linhas_lotes_valores_encerrados_por_switching`.
- A linha de cada lote migrado agora considera, de forma agregada por lote:
  - pagamentos históricos (bruto/líquido) no extrato passado;
  - valores históricos já auditados em `origens_migradas_por_switching`;
  - valores migrados nos eventos de switching materializados (`saida.switchings`).
- Mantido `Bruto atual = 0.00` e `Líq. atual = 0.00` para origens encerradas.
- `Patr. líq.` passa a refletir `Líq. sac.` total observável do lote migrado e `Rend. líq.` passa a refletir `Patr. líq. - Orig.`.
- Decisão sobre rótulo patrimonial: adotada **Alternativa A** (ajuste de rótulo), renomeando para
  `Valor original destinos pós-switching ativos/sintéticos atuais`, pois o cálculo atual reflete apenas destinos atualmente ativos/sintéticos.
- Não houve alteração de regra econômica, motor temporal, ledger ou dados.

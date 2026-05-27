# ME-PRE-ETAPA5-08 — organiza tabela patrimonial observável

- Reorganizada a saída de `construir_resumo_patrimonio_total_lotes` em dois blocos explícitos de apresentação:
  1) `Patrimônio econômico principal`;
  2) `Reconciliação patrimonial / auditoria`.
- Não houve alteração de cálculo econômico: apenas ordenação/rotulagem na apresentação.
- Métricas de reconciliação e de switching foram mantidas para rastreabilidade auditável, mas separadas do bloco principal.
- Escopo intencionalmente restrito a `nucleo/saida_observavel.py` e este registro da microetapa.

# 01_evidencia_detalhada_n4_n6_n7_n8.md — RD-2026-04-28-06B

## Objetivo
Fechar as restrições N4/N6/N7/N8 da RD-2026-04-28-06-LCI com base no pacote complementar de evidências locais já gerado para a RD-06B.

## Evidências utilizadas (pacote local já disponível)
- `evidencias/00_estado_local_ambiente.txt`
- `evidencias/01_inventario_planilha_operacional.txt`
- `evidencias/02_N4_pagamentos_fontes_lotes_planilha.txt`
- `evidencias/03_N6_combinacao_cobertura_parcial_planilha.txt`
- `evidencias/04_N7_recebidos_futuros_datas_planilha.txt`
- `evidencias/05_N8_ordem_intradiaria_pacotes_planilha.txt`
- `evidencias/07_N4_pagamentos_fontes_lotes_console.txt`
- `evidencias/08_N6_combinacao_cobertura_parcial_console.txt`
- `evidencias/09_N7_recebidos_futuros_datas_console.txt`
- `evidencias/10_N8_ordem_intradiaria_pacotes_console.txt`
- `evidencias/11_lote_6630_e_metadados_none_console.txt`
- `evidencias/13_N8_decisoes_diarias_runner_v177_15d.json`
- `evidencias/13_N8_ordem_intradiaria_runner_v177_15d.csv`
- `evidencias/14_N8_resumo_ordem_intradiaria_runner_v177_15d.json`

## Consolidação por controle
### N4 — PASS
- Extratos passado/futuro e console trazem rastreabilidade de pagamento com conta/despesa/lote e valores (saldo antes, bruto, imposto, líquido, saldo remanescente).

### N6 — PASS_COM_OBSERVACAO
- Linhas verificadas no Extrato Futuro com `Cobertura integral = sim`.
- Não houve evidência de pagamento parcial indevido na amostra.
- Observação: sem decomposição formal completa de combinação mínima em todas as linhas.

### N7 — PASS
- Recebidos/lotes futuros usados em datas compatíveis na amostra observada.
- Sem inconsistência temporal observada na janela analisada.

### N8 — PASS_AMOSTRAL_COM_OBSERVACAO
- Janela amostral de 15 dias: **2026-04-29 a 2026-05-13**.
- Trilha diária com campos de pacote vencedor, pagamentos, switching, gates e eventos temporais.
- Distribuição observada: `pay_only=7`, `no_action=6`, `switch_only=2`.
- Gates observados: `selecao_pacote=14`, `override_promovivel_sem_pagamento=1`.
- Inconsistências intradiárias observadas: `0`.
- Observação obrigatória: não houve `switch_then_pay` na janela.

## Observações transversais
- Metadados `None` em `SITUAÇÃO ATUAL` permanecem como achado observacional separado.
- Não há evidência nesta rodada de falha econômica do motor.

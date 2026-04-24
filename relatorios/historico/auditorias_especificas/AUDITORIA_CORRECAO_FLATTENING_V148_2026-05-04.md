# Auditoria experimental da correção de flattening em 2026-05-04

Baseline: V147
Versão experimental: V148

## Resumo
- Lotes normalizados no dia: Lote 3000 mar. V=R$ 3.104,32, Lote 3000 mar. B=R$ 2.571,24
- Patrimônio terminal proxy do pacote base (`pay_only`): **R$ 25.456,76**
- Patrimônio terminal proxy do pacote `switch_then_pay` 3k-only: **R$ 25.476,11**
- Delta de patrimônio terminal proxy: **R$ 19,35**
- `switch_then_pay` 3k-only vence o base: **False**
- Fontes do switching: Lote 3000 mar. V, Lote 3000 mar. B
- Destinos do switching: prod::mercado pago cofrinho 120% cdi meli+, prod::mercado pago cofrinho 120% cdi meli+

## Melhor cenário 3k-only sem gate
{
  "rotulo": "Lote 3000 mar. V + Lote 3000 mar. B -> Mercado Pago Cofrinho 120% CDI (Meli+)",
  "fontes": [
    "Lote 3000 mar. V",
    "Lote 3000 mar. B"
  ],
  "destinos": [
    "prod::mercado pago cofrinho 120% cdi meli+",
    "prod::mercado pago cofrinho 120% cdi meli+"
  ],
  "patrimonio_liquido_terminal_proxy": 25573.89,
  "ganho_terminal_vs_baseline": 0.0
}

## Lotes de switching no estado pós-dia
[
  {
    "id": "Lote 3000 mar. B_ap_2026-05-04",
    "investimento": "Mercado Pago Cofrinho 120% CDI (Meli+)",
    "valor_liquido_resgatavel": 2571.24,
    "valor_terminal_estimado": 2580.01,
    "valor_liquido_base_terminal_estimado": 2571.24,
    "data_final_valor_terminal_estimado": "2026-05-12",
    "origem_tipo_evento": "aporte_nao_aportado"
  },
  {
    "id": "Lote 3000 mar. V_ap_2026-05-04",
    "investimento": "Mercado Pago Cofrinho 120% CDI (Meli+)",
    "valor_liquido_resgatavel": 3104.32,
    "valor_terminal_estimado": 3114.9,
    "valor_liquido_base_terminal_estimado": 3104.32,
    "data_final_valor_terminal_estimado": "2026-05-12",
    "origem_tipo_evento": "aporte_nao_aportado"
  }
]

## Comparação vetorial
{
  "violacoes_protegida": 0.0,
  "deficit_liquido_total": 0.0,
  "pagamentos_sem_cobertura_integral": 0.0,
  "perda_patrimonio_liquido_terminal": 0.0,
  "destruicao_estrategica_lotes": 0.0,
  "deterioracao_liquidez_futura": 0.0,
  "custo_fiscal_imediato": 0.0,
  "custo_operacional": 2.0
}
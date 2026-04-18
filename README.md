# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V80

A V80 preserva integralmente a base funcional da V79 e abre uma **auditoria cirúrgica apenas dos 42 casos reaproveitáveis** identificados na auditoria residual entre o `proxy econômico v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o motor financeiro e sem reabrir a decisão local congelada.

## Gate obrigatório antes de cada entrega

```bash
python scripts/diagnostico/verificar_release_baseline.py
```

## Comandos canônicos

```bash
python aplicacao/console/principal.py
python scripts/operacional/gerar_planilha_operacional.py
python scripts/auditoria/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/diagnostico/inspecionar_base.py
python scripts/diagnostico/verificar_release_baseline.py
python scripts/diagnostico/inspecionar_contrato_f1.py
python scripts/diagnostico/inspecionar_recebidos_auditaveis.py
python scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py
python scripts/diagnostico/inspecionar_saldo_disponivel_geral.py
python scripts/diagnostico/inspecionar_decisao_local_v1.py
python scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py
python scripts/diagnostico/inspecionar_mapa_absorcao_legado.py
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py
python scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py
```

## Documentação vigente

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V80.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V80.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V80.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`
- `relatorios/atuais/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`

## Resumo operacional da V80

- `proxy econômico v3` permanece congelado como decisão monofonte vigente;
- `multifonte v1` continua fora do fluxo principal e condicionada à evidência;
- `switching_economico_shadow` e `resolver_hibrido_5p_shadow` continuam camadas diagnósticas;
- a V80 aprofunda apenas os 42 casos reaproveitáveis, sem alterar o comportamento executável do projeto.

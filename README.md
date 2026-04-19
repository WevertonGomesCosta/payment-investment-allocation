# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V101

A V101 preserva a baseline funcional imediatamente anterior e adiciona uma camada de reescolha dinâmica pós-quebra sobre a auditoria temporal da decisão local v1: mantém a saída operacional do console e da planilha e passa a recomputar a fonte dos pagamentos futuros que deixam de ser coerentes sequencialmente, sem reabrir o solver global.

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
python scripts/diagnostico/inspecionar_mapa_execucao_principal_script2.py
python scripts/diagnostico/inspecionar_switching_economico_shadow.py
python scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py
python scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_divergencias_residuais_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py
python scripts/diagnostico/inspecionar_auditoria_estrutural_redundancia.py
python scripts/diagnostico/inspecionar_benchmark_runner_futuro_shadow.py
python scripts/diagnostico/inspecionar_auditoria_runner_futuro_shadow.py
```

## Documentação vigente

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V101.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V101.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V101.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`
- `relatorios/atuais/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md`
- `relatorios/atuais/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`
- `relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`
- `relatorios/atuais/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md`

## Resumo operacional da V101

- a V101 mantém a auditoria da primeira quebra de cobertura do runner shadow em 2026-05-20;
- a V101 preserva o console e o extrato futuro da planilha como camada de auditabilidade local já aprovada;
- a V101 preserva a auditoria temporal da decisão local v1 com depleção cumulativa dos lotes sugeridos;
- a V101 adiciona uma camada de reescolha dinâmica pós-quebra para recomputar a fonte dos pagamentos futuros que deixam de ser coerentes sequencialmente;
- a V101 adiciona colunas dinâmicas ao extrato futuro da planilha, uma nova aba de reescolha dinâmica e uma nova seção dedicada no console principal.

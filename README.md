# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V96

A V96 preserva integralmente a baseline funcional imediatamente anterior e mantém a auditoria da primeira quebra de cobertura do runner shadow em 2026-05-20. O ajuste desta derivação é cirúrgico: adiciona ao console o lote sugerido para os próximos pagamentos, a auditoria do método governante de escolha e a justificativa operacional do porquê o proxy econômico v3 continua governando a decisão local.

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
- `relatorios/atuais/BASELINE_FIXA_V96.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V96.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V96.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`
- `relatorios/atuais/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md`
- `relatorios/atuais/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`
- `relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`
- `relatorios/atuais/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md`

## Resumo operacional da V96

- o runner principal legado do Script 2 foi classificado em mapa de absorção e não entra funcionalmente na baseline atual;
- `proxy econômico v3` permanece congelado como decisão monofonte vigente;
- `multifonte v1` continua fora do fluxo principal e condicionada à evidência;
- `switching_economico_shadow` e `resolver_hibrido_5p_shadow` continuam camadas diagnósticas;
- a V96 mantém a auditoria da primeira quebra de cobertura do runner shadow em 2026-05-20;
- a V96 adiciona ao console o lote sugerido para os próximos pagamentos e uma leitura auditável da escolha;
- a V96 imprime os modelos, parâmetros centrais e a justificativa operacional do método governante atual;
- o runner shadow cobre 15/152 pagamentos integralmente, usa multifonte em 3 casos e altera o lote principal em 150 pagamentos;
- por isso, a recomendação do benchmark permanece **vigente**, e o runner legado correto continua apenas diagnóstico.


- Diagnóstico adicional vigente: `scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py` (primeira quebra de cobertura do runner futuro shadow).

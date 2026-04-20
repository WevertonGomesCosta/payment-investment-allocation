# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V104

A V104 preserva a cadeia auditável da baseline anterior e adiciona uma camada de **planejamento conjunto local do bloco crítico** entre 20/04/2026 e 20/05/2026. Essa camada continua sem solver global, compara poucas políticas candidatas de consumo e preservação de lotes e seleciona a melhor segundo a cobertura do **Cartão Azul de 20/05**, a cobertura do bloco e o déficit total.

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
python scripts/diagnostico/inspecionar_auditoria_temporal_decisao_local.py
python scripts/diagnostico/inspecionar_reescolha_dinamica_pos_quebra.py
python scripts/diagnostico/inspecionar_heuristica_conjunta_parcial_bloco_critico.py
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
python scripts/diagnostico/inspecionar_primeira_quebra_runner_futuro_shadow.py
```

## Documentação vigente

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V104.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V104.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V104.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`
- `relatorios/atuais/MAPA_ABSORCAO_EXECUCAO_PRINCIPAL_SCRIPT_2.md`
- `relatorios/atuais/BENCHMARK_SHADOW_AGRUPADO_VS_INDIVIDUAL_SCRIPT1.md`
- `relatorios/atuais/BENCHMARK_SHADOW_RUNNER_SIMULACAO_FUTURA_SCRIPT2.md`
- `relatorios/atuais/AUDITORIA_RESIDUAL_DIVERGENCIAS_PROXY_V3_VS_HIBRIDO.md`
- `relatorios/atuais/AUDITORIA_CIRURGICA_42_CASOS_REAPROVEITAVEIS.md`
- `relatorios/atuais/AUDITORIA_FINA_TRANSICAO_DOMINANTE_3000B_8500MAR.md`
- `relatorios/atuais/AUDITORIA_ESTRUTURAL_REDUNDANCIA_COMPATIBILIDADE.md`
- `relatorios/atuais/CONSOLIDACAO_HELPERS_DUPLICADOS_BAIXO_RISCO.md`
- `relatorios/atuais/AUDITORIA_CASOS_CRITICOS_RUNNER_FUTURO_SHADOW.md`
- `relatorios/atuais/AUDITORIA_PRIMEIRA_QUEBRA_RUNNER_FUTURO_SHADOW.md`

## Resumo operacional da V104

- a V104 mantém a saída operacional do console e da planilha já auditadas;
- adiciona o `planejamento_conjunto_local_bloco_critico_v1` com comparação de políticas candidatas;
- preserva a auditoria temporal da decisão local e a reescolha dinâmica pós-quebra;
- adiciona uma heurística conjunta parcial restrita ao bloco crítico 20/04/2026–20/05/2026;
- introduz planejamento de reservas estratégicas por fonte para reduzir consumo precoce;
- registra trocas preventivas de lote antes da quebra e compara a primeira sem cobertura com as camadas anteriores.

# Estrutura do repositório V78

## Núcleo da baseline

- `nucleo/contexto_baseline.py` — montagem central da baseline
- `nucleo/identidade_baseline.py` — identidade da V78 e nomes-base de artefatos
- `nucleo/caixa_recebidos_auditaveis.py` — estruturas materializadas da F1
- `nucleo/replay_passado_controlado.py` — replay mínimo observável do passado
- `nucleo/nucleo_financeiro_minimo.py` — camada financeira preservada
- `nucleo/switching_shadow_reconciliacao.py` — camada shadow reconciliatória de switching
- `nucleo/switching_economico_shadow.py` — camada shadow de switching econômico legado

## Aplicação

- `aplicacao/console/principal.py` — caminho canônico do console
- `aplicacao/principal.py` — wrapper de compatibilidade

## Scripts

### Operacionais
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`

### Diagnósticos
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `scripts/diagnostico/inspecionar_decisao_local_v1.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`
- `scripts/diagnostico/inspecionar_mapa_absorcao_legado.py`
- `scripts/diagnostico/inspecionar_switching_economico_shadow.py`

### Wrappers antigos preservados
- `scripts/*.py`

## Documentação vigente

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V78.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V78.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V78.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`


## Inclusão estrutural adicional da V78

- `nucleo/resolver_hibrido_5p_shadow.py`
- `scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py`
- `scripts/inspecionar_resolver_hibrido_5p_shadow.py`


## Inclusão estrutural adicional da V78

- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
- `scripts/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`

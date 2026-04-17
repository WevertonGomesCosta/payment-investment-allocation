# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V73

A V73 preserva a base funcional da V72 e abre a auditoria comparativa **proxy econômico v2 vs v3** sobre a mesma base e os mesmos pagamentos, sem alterar o motor financeiro nem integrar novas decisões ao fluxo principal.

## Estrutura canônica da V73

### Orquestração da baseline
- `nucleo/contexto_baseline.py` → montagem central da baseline
- `nucleo/identidade_baseline.py` → versão e nomes-base de artefatos
- `nucleo/config_utils.py` → leitura compartilhada do config

### Execução principal
- `aplicacao/console/principal.py` → caminho canônico do console
- `aplicacao/principal.py` → wrapper de compatibilidade

### Scripts auxiliares
- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/auditoria/gerar_auditoria_diaria_lote.py`
- `scripts/diagnostico/inspecionar_base.py`
- `scripts/diagnostico/verificar_release_baseline.py`
- `scripts/diagnostico/inspecionar_contrato_f1.py`
- `scripts/diagnostico/inspecionar_recebidos_auditaveis.py`
- `scripts/diagnostico/inspecionar_fontes_elegiveis_pagamento.py`
- `scripts/diagnostico/inspecionar_saldo_disponivel_geral.py`
- `scripts/diagnostico/inspecionar_decisao_local_v1.py`
- `scripts/diagnostico/inspecionar_comparativo_proxy_v2_v3.py`
- `scripts/*.py` → wrappers de compatibilidade

### Camada F1 aberta até aqui
- `nucleo/caixa_recebidos_auditaveis.py`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`

### Dados canônicos
- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

### Saídas
- `saidas/operacional/` → artefatos vigentes da baseline atual

### Documentação vigente
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V73.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V73.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V73.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`

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
```

## Comandos antigos preservados

```bash
python aplicacao/principal.py
python scripts/gerar_planilha_operacional.py
python scripts/gerar_auditoria_diaria_lote.py --lote "Lote 6630,64 fev."
python scripts/inspecionar_base.py
python scripts/verificar_release_baseline.py
python scripts/inspecionar_contrato_f1.py
python scripts/inspecionar_recebidos_auditaveis.py
python scripts/inspecionar_fontes_elegiveis_pagamento.py
python scripts/inspecionar_saldo_disponivel_geral.py
python scripts/inspecionar_decisao_local_v1.py
```

## Atualização V73

- V70 consolidada como baseline oficial de partida;
- checagem de release mantida como gate obrigatório;
- abertura da micro-etapa **F1.7** com `decisao_local_v1` e proxy econômico v3 por pagamento sobre a matriz temporal completa;
- inclusão de diagnóstico e metadados auditáveis para fonte escolhida, lote escolhido, cobertura, critério de decisão e score do proxy econômico v3;
- preservação integral da lógica econômica já implementada.


## Atualização V73

- baseline atualizada para **V73**;
- abertura da auditoria comparativa **proxy econômico v2 vs v3** sobre a mesma base e os mesmos pagamentos;
- inclusão de diagnóstico e artefatos exportáveis para comparar mudança de lote, critério e delta de custo proxy antes de abrir multifonte.

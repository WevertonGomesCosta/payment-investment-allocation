# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V63

A V63 preserva a base funcional da V62 e atualiza `dados/cache_bcb.json` com a série BCB/CDI enviada pelo usuário, estendendo a série explícita até 2026-04-16, regenerando o artefato operacional vigente e mantendo intactos o motor financeiro e a etapa funcional da F1 já aberta.

## Estrutura canônica da V63

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
- `relatorios/atuais/BASELINE_FIXA_V63.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V63.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V63.md`
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
```

## Atualização V63

- V61 consolidada como baseline oficial da fase F1;
- checagem de release mantida como gate obrigatório;
- materialização executável de `fonte_elegivel_pagamento`;
- nenhuma alteração do motor financeiro ou do fluxo principal nesta etapa.

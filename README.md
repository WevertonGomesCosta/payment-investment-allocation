# payment-investment-allocation

Repositório controlado para a unificação incremental de pagamentos, recebidos, investimentos e decisões futuras de switching.

## Estado atual do repositório

**Versão atual da baseline:** V78

A V78 preserva integralmente a base funcional da V77 e abre o **benchmark shadow do `resolver_hibrido_5p` legado**, sem alterar o motor financeiro, sem reabrir o `proxy econômico v3` congelado e sem acoplar o benchmark ao fluxo principal.

## Estrutura canônica da V78

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
- `scripts/diagnostico/inspecionar_mapa_absorcao_legado.py`
- `scripts/diagnostico/inspecionar_switching_economico_shadow.py`
- `scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py`
- `scripts/*.py` → wrappers de compatibilidade

### Camada F1 aberta até aqui
- `nucleo/caixa_recebidos_auditaveis.py`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`

### Mapeamento legado vigente
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`

### Shadow do switching econômico legado
- `nucleo/switching_economico_shadow.py`
- `nucleo/resolver_hibrido_5p_shadow.py`

### Dados canônicos
- `dados/config_atualizado.json`
- `dados/dados_financeiros.xlsx`
- `dados/cache_bcb.json`

### Saídas
- `saidas/operacional/` → artefatos vigentes da baseline atual

### Documentação vigente
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/BASELINE_FIXA_V78.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V78.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V78.md`
- `relatorios/atuais/F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `relatorios/atuais/MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`

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
- `scripts/diagnostico/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
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
python scripts/inspecionar_comparativo_proxy_v2_v3.py
python scripts/inspecionar_mapa_absorcao_legado.py
python scripts/inspecionar_switching_economico_shadow.py
python scripts/inspecionar_resolver_hibrido_5p_shadow.py
- `scripts/inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`
```

## Atualização V78

- baseline atualizada para **V77** sem alteração funcional do motor;
- abertura da absorção inicial do **switching econômico legado em modo shadow**;
- criação de uma camada diagnóstica que compara `manter` vs `switch agora e carregar até o horizonte`;
- criação do diagnóstico `inspecionar_switching_economico_shadow.py`;
- preservação do `proxy econômico v3` congelado como decisão monofonte vigente;
- manutenção de `multifonte v1` como frente futura condicionada à evidência;
- preservação do `release checker` como gate obrigatório antes das próximas entregas.


## Atualização V78

- baseline atualizada para **V78** sem alteração funcional do motor;
- abertura do benchmark shadow do **`resolver_hibrido_5p`** legado;
- criação de uma camada diagnóstica multifonte local por pagamento, isolada do fluxo principal;
- criação do diagnóstico `inspecionar_resolver_hibrido_5p_shadow.py`;
- preservação do `proxy econômico v3` congelado como decisão monofonte vigente;
- manutenção de `multifonte v1` como frente futura condicionada à evidência.


## Atualização V78

- baseline atualizada para **V78** sem alteração do fluxo principal;
- abertura da auditoria comparativa entre a decisão local vigente (**proxy v3**) e o benchmark shadow do **`resolver_hibrido_5p`**;
- criação do diagnóstico `inspecionar_comparativo_proxy_v3_vs_hibrido_shadow.py`;
- manutenção do `proxy econômico v3` como decisão vigente e do benchmark híbrido como camada apenas diagnóstica.

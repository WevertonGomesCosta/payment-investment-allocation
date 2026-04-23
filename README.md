# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, recebidos, aportes e switching** com base única, `config` central e rastreabilidade por lote.

**Baseline entregue do repositório:** V116  
**Baseline central/contratual da frente principal:** V108

A V116 preserva a reorganização estrutural da V115 e acrescenta uma **recalibração cirúrgica do comparador local** do `motor_recomendacao_pagamentos_switching_v1`, com consumo residual temporal por lote e fallback automático para `sem_switching`.

## Objetivo final do projeto

Construir um **motor conjunto, auditável e economicamente coerente** para:

- pagamentos;
- recebidos;
- aportes;
- futuras decisões de switching.

A decisão final deve buscar **maximizar o patrimônio líquido terminal**, respeitando:

- cobertura dos pagamentos;
- liquidez e carência;
- tributação;
- precedência intradiária parametrizada;
- preservação de pagamentos protegidos;
- auditabilidade completa por lote/fonte.

O projeto **não** tem como objetivo final otimizar isoladamente um único pagamento ou uma janela local sem reconexão com o cenário conjunto.

## O que a V116 faz

- recentra a documentação ativa no objetivo final conjunto;
- move documentação histórica redundante para `relatorios/historico/`;
- remove saídas operacionais antigas e não referenciadas;
- reduz redundância de bootstrap nos diagnósticos via helper compartilhado;
- preserva compatibilidade dos wrappers raiz em `scripts/`.

## Camadas vigentes

### Frente central
- `caixa_recebidos_auditaveis`
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v1`

### Camada operacional por conta
- `motor_recomendacao_pagamentos_switching_v1`

### Trilha experimental local
- `heuristica_conjunta_parcial_bloco_critico`
- `planejamento_conjunto_local_bloco_critico_v1`
- `microplanejamento_conjunto_bloco_critico_v2`

## Documentos ativos

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `relatorios/atuais/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md`
- `relatorios/atuais/BASELINE_FIXA_V116.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V116.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V116.md`
- `relatorios/atuais/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`
- `relatorios/atuais/REORGANIZACAO_REPOSITORIO_V115.md`
- `relatorios/INDICE_RELATORIOS.md`

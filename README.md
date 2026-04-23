# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, recebidos, aportes e switching** com base única, `config` central e rastreabilidade por lote.

**Baseline entregue do repositório:** V117  
**Baseline central/contratual da frente principal:** V108

A V117 preserva a V116 como baseline operacional anterior e acrescenta uma **camada documental/técnica mínima** para o futuro motor conjunto temporal, com contrato formal e esqueletos executáveis de planejamento temporal, alocação terminal, simulação de eventos e avaliação conjunta.

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

## O que a V117 faz

- formaliza o `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`;
- cria os esqueletos executáveis mínimos de:
  - `planejador_switching_temporal_v1`;
  - `alocador_pagamentos_terminal_v1`;
  - `simulador_central_eventos_v1`;
  - `avaliador_cenarios_conjuntos_v1`;
- preserva a baseline central V108 e a camada operacional anterior V116 sem reabrir a lógica econômica vigente.

## Camadas vigentes

### Frente central
- `caixa_recebidos_auditaveis`
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v1`

### Camada documental/técnica mínima V117
- `planejador_switching_temporal_v1`
- `alocador_pagamentos_terminal_v1`
- `simulador_central_eventos_v1`
- `avaliador_cenarios_conjuntos_v1`

### Camada operacional por conta
- `motor_recomendacao_pagamentos_switching_v1`

### Trilha experimental local
- `heuristica_conjunta_parcial_bloco_critico`
- `planejamento_conjunto_local_bloco_critico_v1`
- `microplanejamento_conjunto_bloco_critico_v2`

## Documentos ativos

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `relatorios/atuais/MOTOR_RECOMENDACAO_PAGAMENTOS_SWITCHING_V114.md`
- `relatorios/atuais/BASELINE_FIXA_V117.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V117.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V117.md`
- `relatorios/atuais/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`
- `relatorios/INDICE_RELATORIOS.md`

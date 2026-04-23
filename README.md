# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, recebidos, aportes e switching** com base única, `config` central e rastreabilidade por lote.

**Baseline entregue do repositório:** V118  
**Baseline central/contratual da frente principal:** V108

A V118 preserva a V117 como contrato do motor conjunto temporal e acrescenta a **primeira integração funcional mínima** entre planejamento temporal de switching, alocação terminal de pagamentos, simulação curta de eventos e avaliação conjunta de cenários.

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

## O que a V118 faz

- preserva o `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md` como referência do desenho da nova camada central;
- integra minimamente:
  - `planejador_switching_temporal_v1`;
  - `alocador_pagamentos_terminal_v1`;
  - `simulador_central_eventos_v1`;
  - `avaliador_cenarios_conjuntos_v1`;
- executa um recorte curto real de datas críticas com vetor terminal auditável;
- mantém a baseline central V108 e a camada operacional V116 sem reabrir a lógica econômica principal.

## Camadas vigentes

### Frente central
- `caixa_recebidos_auditaveis`
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v1`

### Camada temporal mínima integrada
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
- `relatorios/atuais/BASELINE_FIXA_V118.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V118.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V118.md`
- `relatorios/atuais/INTEGRACAO_FUNCIONAL_MINIMA_V117_RECORTE_CURTO.md`
- `relatorios/atuais/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md`
- `relatorios/INDICE_RELATORIOS.md`

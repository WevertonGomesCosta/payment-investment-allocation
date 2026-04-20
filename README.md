# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, aportes e switching** com base única, config central e rastreabilidade por lote.

**Versão atual do repositório:** V113

**Baseline principal da frente central:** V108

**Camada experimental nova:** `alocacao_intradiaria_pacote_v1`

A V108 recalibra a primeira camada da frente central, **`recomputacao_sequencial_central_v1`**, adicionando:

- penalidade explícita de escassez futura para pagamentos `PROTEGIDA`;
- prioridade intraclasse no mesmo dia;
- fallback auditável de **sem fonte viável**.

## O que a V108 faz

- recalcula a melhor fonte a cada pagamento futuro com **saldos residuais atualizados**;
- compara alternativas pela **métrica canônica mínima central**;
- introduz proteção mínima de curto prazo para `PROTEGIDA` futura;
- mantém rastreabilidade por lote e por fonte;
- preserva V103–V105 como **trilha experimental local**;
- não abre solver global completo.

## Frente central vs trilha experimental

### Frente central
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v1`

### Trilha experimental local
- `heuristica_conjunta_parcial_bloco_critico`
- `planejamento_conjunto_local_bloco_critico_v1`
- `microplanejamento_conjunto_bloco_critico_v2`

## Documentos ativos

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `relatorios/atuais/BASELINE_FIXA_V108.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V108.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V108.md`

## Resumo operacional da V108

A V108 mantém a frente central como eixo principal e recalibra a `recomputacao_sequencial_central_v1` para reduzir violações de `PROTEGIDA` sem voltar a otimizar apenas o bloco crítico local.


## O que a V113 acrescenta

A V113 adiciona uma camada experimental de **alocação conjunta intradiária por data**, mantendo a V108 como baseline principal da frente central.

Essa camada compara poucas políticas candidatas para cada data e escolhe a melhor por comparador lexicográfico diário, reduzindo artefatos de ordem entre pagamentos da mesma data.

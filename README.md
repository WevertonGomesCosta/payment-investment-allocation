# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, aportes e switching** com base única, config central e rastreabilidade por lote.

**Versão atual da baseline:** V108

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


## V114 — motor operacional por conta

A V114 adiciona uma camada operacional de recomendação por conta, comparando pagar sem switching, com switching simples e com combinação mínima. A baseline principal da frente central permanece a V108.

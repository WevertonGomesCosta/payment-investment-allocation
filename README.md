# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, aportes e switching** com base única, config central e rastreabilidade por lote.

**Versão atual da baseline:** V107

A V107 implementa a primeira camada da frente central após o saneamento contratual da V106: a **`recomputacao_sequencial_central_v1`**.

## O que a V107 faz

- recalcula a melhor fonte a cada pagamento futuro com **saldos residuais atualizados**;
- compara alternativas pela **métrica canônica mínima central**;
- mantém rastreabilidade por lote e por fonte;
- preserva as camadas V103–V105 como **trilha experimental local**;
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
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V107.md`
- `relatorios/atuais/BASELINE_FIXA_V107.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V107.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V107.md`

## Resumo operacional da V107

A V107 recoloca o projeto na frente central: em vez de otimizar âncoras locais isoladas, passa a comparar candidatos por uma régua mínima conjunta com foco em pagamentos `PROTEGIDA`, déficit total, cobertura integral e patrimônio terminal proxy.

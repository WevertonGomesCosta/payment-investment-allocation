# payment-investment-allocation

Repositório de unificação incremental do motor de **pagamentos, aportes e switching** com base única, config central e rastreabilidade por lote.

**Versão atual da baseline:** V112

A V112 implementa a **`recomputacao_sequencial_central_v2`**, preservando a governança central da V108 e refinando a reserva futura de `PROTEGIDA` com foco em **reserva crítica por fonte**.

## O que a V112 faz

- recalcula a melhor fonte a cada pagamento futuro com **saldos residuais atualizados**;
- compara alternativas pela **métrica canônica mínima central**;
- usa **reserva crítica por fonte** para `PROTEGIDA`;
- calcula demanda marginal por janelas de **7/14/21 dias**;
- expõe orçamento explícito de reserva por lote/fonte;
- mantém rastreabilidade por lote, fonte e motivo;
- preserva V103–V105 como **trilha experimental local**;
- não abre solver global completo.

## Frente central vs trilha experimental

### Frente central
- `decisao_local_v1`
- `auditoria_temporal_decisao_local`
- `reescolha_dinamica_pos_quebra`
- `recomputacao_sequencial_central_v2`

### Trilha experimental local
- `heuristica_conjunta_parcial_bloco_critico`
- `planejamento_conjunto_local_bloco_critico_v1`
- `microplanejamento_conjunto_bloco_critico_v2`

## Documentos ativos

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/METRICA_CANONICA_MINIMA_CENTRAL.md`
- `relatorios/atuais/SANEAMENTO_CONTRATUAL_V106.md`
- `relatorios/atuais/RECOMPUTACAO_SEQUENCIAL_CENTRAL_V112.md`
- `relatorios/atuais/BASELINE_FIXA_V112.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V112.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V112.md`

## Resumo operacional da V112

A V112 mantém a frente central como eixo principal e substitui a proteção futura agregada da V108 por uma **reserva crítica por fonte**, com demanda marginal por janelas curtas e auditabilidade explícita do orçamento de reserva por lote.

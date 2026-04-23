# payment-investment-allocation

**Baseline atual:** V181  
**Contrato mestre vigente:** V181

A V181 mantém a V179 como baseline metodológica oficial do modelo e amplia o contrato mestre para um formato completo, atual e historicamente contextualizado, adequado para servir de referência em conversas futuras e como base final do projeto.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V181 consolida
- mantém a V179 como modelo matemático estatístico-financeiro oficial do projeto;
- amplia o contrato operacional mestre para um formato completo, atual e historicamente contextualizado;
- mantém os suplementos de validação diária e pós-vencimento/gate como camadas complementares vigentes;
- rebaixa explicitamente V117/V108 a contexto histórico e não normativo principal;
- preserva a trilha de validação diária, o congelamento estrutural local e a linha histórica das baselines centrais no próprio corpo do contrato mestre.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`
- `relatorios/atuais/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`
- `relatorios/atuais/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`
- `relatorios/atuais/AUDITORIA_REEXECUCAO_CACHE_DADOS_V178.md`
- `relatorios/atuais/VALIDACAO_DIARIA_OPERACIONAL_V178_2026-04-23_2026-05-23.md`

## Próxima frente após a V181
Derivar a especificação operacional completa de `resolver_dia(t, E_t)` diretamente a partir do contrato mestre V181 e do modelo oficial V179.

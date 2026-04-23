# payment-investment-allocation

**Baseline atual:** V179  
**Contrato mestre vigente:** V179

A V179 formaliza o modelo matemático estatístico-financeiro oficial do projeto e estabelece o contrato operacional mestre vigente, reorganizando a governança do repositório em torno do objetivo final e rebaixando V117/V108 a contexto histórico.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V179 consolida
- consolida o contrato operacional mestre do projeto;
- formaliza o modelo matemático estatístico-financeiro oficial da V179;
- mantém os suplementos de validação diária e pós-vencimento/gate como camadas complementares vigentes;
- rebaixa explicitamente V117/V108 a contexto histórico e não normativo principal;
- preserva a trilha de validação diária e o congelamento estrutural local já conquistados nas versões anteriores.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`
- `relatorios/atuais/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`
- `relatorios/atuais/CONTRATO_SUPLEMENTAR_POS_VENCIMENTO_GATE_V177.md`
- `relatorios/atuais/AUDITORIA_REEXECUCAO_CACHE_DADOS_V178.md`
- `relatorios/atuais/VALIDACAO_DIARIA_OPERACIONAL_V178_2026-04-23_2026-05-23.md`

## Próxima frente após a V179
Derivar a especificação operacional completa de `resolver_dia(t, E_t)` diretamente a partir do contrato mestre e do modelo oficial.

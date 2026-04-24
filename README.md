# payment-investment-allocation

**Pacote operacional atual:** V188  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V188 fecha a limpeza residual da árvore do repositório. Ela **não altera** o núcleo econômico, o contrato mestre, o modelo oficial nem a estrutura diária por pacotes já congelados.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V188 consolida
- fecha a limpeza residual dos artefatos soltos da raiz do repositório;
- remove auditorias antigas da raiz de `relatorios/`, rebaixando-as para histórico;
- preserva `relatorios/atuais/` apenas com documentos canônicos ativos;
- mantém `scripts/diagnostico/` como caminho canônico do tooling e deixa a raiz de `scripts/` apenas com compatibilidade intencional;
- preserva histórico e rastreabilidade sem competir com os caminhos ativos;
- remove resíduos efêmeros (`__pycache__`, `.pyc`) do pacote final.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

## Próxima frente após a V188
Abrir a especificação operacional de `resolver_dia(t, E_t)` sobre uma árvore já limpa e sem ruído residual de navegação.

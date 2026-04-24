# payment-investment-allocation

**Pacote operacional atual:** V189  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V189 consolida a especificação oficial da camada observável do projeto. Ela **não altera** o núcleo econômico, o contrato mestre, o modelo oficial nem a estrutura diária por pacotes já congelados.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V189 consolida
- mantém a árvore documental limpa da V188;
- adiciona `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md` como referência canônica da camada observável;
- fecha o contrato de saída para console, markdown, json e `.xlsx`;
- fixa a presença do ranking relevante da carteira e dos switchings candidatos/classificados na saída oficial;
- prepara a baseline para derivar `resolver_dia(t, E_t)` sem retrabalho de interface.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md`

## Próxima frente após a V189
Derivar a especificação operacional de `resolver_dia(t, E_t)` sobre uma baseline já limpa e com a camada observável oficialmente fechada.

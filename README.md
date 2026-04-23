# payment-investment-allocation

**Pacote operacional atual:** V184  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V184 é uma limpeza residual fina da camada documental e de navegação do repositório. Ela **não altera** o núcleo econômico, o contrato mestre, o modelo oficial nem a estrutura diária por pacotes já congelados.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V184 consolida
- limpa `relatorios/atuais/`, mantendo apenas os documentos canônicos vigentes;
- rebaixa fisicamente documentos históricos para `relatorios/historico/`;
- preserva a trilha histórica sem deixá-la competir com o caminho ativo;
- corrige a navegação documental em `README`, `LEIA-ME_OPERACIONAL` e `INDICE_RELATORIOS`.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

## Próxima frente após a V184
Derivar a especificação operacional completa de `resolver_dia(t, E_t)` diretamente a partir do contrato mestre V183 e do modelo oficial V182.

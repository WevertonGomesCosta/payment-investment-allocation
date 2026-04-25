# payment-investment-allocation

**Pacote operacional atual:** V201  
**Base funcional fixa de origem:** V200  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V201 aplica uma limpeza residual segura do repositório. Ela **não altera** o motor principal, o contrato mestre, o modelo matemático-estatístico-financeiro nem a lógica econômica validada na V200.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V201 consolida
- rebaixa documentos versionados antigos da raiz para histórico;
- rebaixa relatórios e artefatos antigos de `saidas/oficial/` para `saidas/historico/`;
- mantém `relatorio_operacional_v200.xlsx` como saída operacional oficial ativa;
- cria `relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md`;
- cria `relatorios/atuais/MAPA_SCRIPTS_V201.md`;
- preserva integralmente os módulos funcionais do motor e altera apenas a identidade operacional para V201.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md`
- `relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md`
- `relatorios/atuais/MAPA_SCRIPTS_V201.md`

## Próxima frente após a V201
Derivar a camada única de saída canônica para que console, `.xlsx`, JSON/CSV e markdown dependam da mesma estrutura materializada, sem recálculos paralelos em renderizadores.

## Frente metodológica ainda preservada
Os aportes/recebidos futuros ainda não aportados em carteira permanecem como problema metodológico futuro. Essa frente deve ser aberta depois da unificação da camada de saídas.

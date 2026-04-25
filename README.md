# payment-investment-allocation

**Pacote operacional atual:** V202  
**Base funcional fixa de origem:** V200  
**Baseline contratual vigente:** V183  
**Modelo metodológico vinculante vigente:** V182

A V202 deriva da V201 e cria a camada única de saída canônica para console e planilha operacional. Ela **não altera** o motor principal, o contrato mestre, o modelo matemático-estatístico-financeiro nem a lógica econômica validada.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V202 consolida
- cria `nucleo/saida_canonica.py`;
- faz console e planilha operacional consumirem a mesma estrutura materializada;
- gera `relatorio_operacional_v202.xlsx`;
- cria a aba `Saida Canonica` com auditoria mínima da camada observável;
- mantém aportes/recebidos futuros como frente metodológica posterior.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `relatorios/atuais/BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `relatorios/atuais/ESPECIFICACAO_SAIDA_OFICIAL.md`
- `relatorios/atuais/AUDITORIA_LIMPEZA_RESIDUAL_V201.md`
- `relatorios/atuais/MAPA_SCRIPTS_V201.md`
- `relatorios/atuais/AUDITORIA_CAMADA_SAIDA_CANONICA_V202.md`

## Próxima frente após a V202
Auditar scripts legados que ainda produzem console/arquivos próprios e classificá-los como wrappers, diagnósticos históricos ou candidatos a migração para `nucleo.saida_canonica`.

## Frente metodológica ainda preservada
Os aportes/recebidos futuros ainda não aportados em carteira permanecem como problema metodológico futuro. Essa frente deve ser aberta depois da unificação da camada de saídas.

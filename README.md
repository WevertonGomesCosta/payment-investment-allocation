# payment-investment-allocation

**Baseline atual:** V139  
**Baseline central/contratual da frente principal:** V108

A V139 é uma etapa de **reorganização estrutural de baixo risco** derivada da V138. Ela não altera a lógica econômica central do projeto; limpa a superfície documental, reorganiza a trilha de saídas e prepara a base para absorver os modelos do Script 1 na camada de pagamentos.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V139 faz
- limpa `relatorios/atuais` e move material superado para `relatorios/historico`;
- cria uma trilha de saídas em `saidas/oficial`, `saidas/diagnostico` e `saidas/historico`;
- preserva `saidas/operacional` apenas como camada de compatibilidade temporária;
- cria a reserva estrutural `nucleo/pagamentos/modelos_script1/` para a próxima frente.

## Documentos operacionais vigentes
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`
- `relatorios/atuais/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md`
- `relatorios/atuais/CONTRATO_ABSORCAO_MODELOS_SCRIPT1_PAGAMENTOS_V140.md`

## Próxima etapa após a V139
Absorver os modelos do Script 1 na camada de pagamentos e, só depois disso, ampliar o bloco real de pagamentos além do recorte curto da V138.

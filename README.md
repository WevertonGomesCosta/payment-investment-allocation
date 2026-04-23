# payment-investment-allocation

**Baseline atual:** V179  
**Baseline central/contratual da frente principal:** V108

A V176 preserva o congelamento estrutural local do switching consolidado até a V174, mantém a correção temporal operacional da V175 e reorganiza a validação diária para ficar alinhada ao objetivo final do projeto.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V176 faz
- mantém a V174 como marco de congelamento estrutural da frente local de switching no simulador central;
- mantém a V175 como correção da elegibilidade temporal operacional;
- registra, em documentação oficial, guardrails de não regressão para validação diária orientada ao objetivo final;
- reforma o runner diário para expor, por dia:
  - componentes reais do pagamento vencedor;
  - quadro de fontes candidatas do pagamento;
  - ações candidatas de switching;
  - cenários classificados;
  - melhor cenário promovível;
  - lotes monitorados no estado diário.

## Documentos operacionais prioritários
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`
- `relatorios/atuais/CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`
- `relatorios/atuais/AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md`
- `relatorios/atuais/VALIDACAO_DIARIA_OPERACIONAL_V176_2026-04-23_2026-05-23.md`

## Próxima frente após a V176
Usar a trilha diária reformada para validar manualmente pagamentos e switchings por lote/fonte antes de expandir o espaço de busca de switching.

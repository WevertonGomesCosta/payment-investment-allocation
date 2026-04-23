# payment-investment-allocation

**Baseline atual:** V141  
**Baseline central/contratual da frente principal:** V108

A V141 mantém a reorganização da V139/V140 e implementa a **Fase 1 de absorção dos modelos do Script 1** no `alocador_pagamentos_terminal_v1`, sem reabrir a auditoria ampla de switching.

## Objetivo final do projeto
Construir um motor conjunto, auditável e economicamente coerente para:
- pagamentos;
- recebidos;
- aportes;
- switching.

A decisão final deve maximizar o **patrimônio líquido terminal**, respeitando cobertura, liquidez, carência, tributação, precedência intradiária parametrizada e auditabilidade por lote/fonte.

## O que a V141 faz
- mantém a reorganização documental e de saídas da V139;
- mantém o contrato de absorção dos modelos do Script 1 formalizado na V140;
- incorpora H1–H3 ao `alocador_pagamentos_terminal_v1` como score auxiliar e desempate econômico por fonte;
- prepara a próxima expansão do fluxo real de pagamentos já com a Fase 1 ativa.

## Documentos operacionais vigentes
Consulte primeiro:
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/ALOCADOR_PAGAMENTOS_TERMINAL_V141.md`
- `relatorios/atuais/FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md`
- `relatorios/atuais/CONTRATO_ABSORCAO_MODELOS_SCRIPT1_PAGAMENTOS_V140.md`

## Próxima etapa após a V141
Expandir a integração do `alocador_pagamentos_terminal_v1` para um recorte real maior, já com H1–H3 ativos, antes de abrir a fase 2 das combinações do Script 1.

## O que a V142 adiciona
- auditoria do repositório baseada na V141;
- recorte real maior de pagamentos com comparação entre fluxo com H1–H3 ativas e fluxo neutralizado;
- medição do efeito de H1–H3 sobre escolhas entre lote aportado, lote não aportado, combinação mínima e cenário com switching elegível sob foco em patrimônio líquido terminal proxy.

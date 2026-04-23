# Reescrita do contrato mestre — V180

## Objetivo

A V180 reescreve `CONTRATO_OPERACIONAL_PROJETO.md` como contrato mestre vigente do projeto, alinhado explicitamente ao modelo oficial V179 e às regras consolidadas no chat de revisão contratual.

## Mudanças centrais

1. A V179 passa a ser a baseline documental e metodológica vigente do projeto.
2. O contrato operacional deixa de tomar V108/V117 como base normativa principal.
3. O modelo oficial V179 passa a ser anexo metodológico normativo do contrato mestre.
4. O contrato passa a explicitar como regras vigentes:
   - decisão diária por pacotes;
   - pagamento obrigatório e integral na data da planilha;
   - filtragem prévia por disponibilidade, liquidez, resgate e carência;
   - pós-vencimento como fonte disponível do dia;
   - switching apenas nas formas individual, agrupado combinatório e integral;
   - regra global do dia para residual na fase de pagamento;
   - cronologia intradiária por pacote;
   - convenções de governança documental.
5. V117 e V108 permanecem preservados apenas como contexto histórico/documental intermediário.

## Arquivos ajustados

- `relatorios/atuais/CONTRATO_OPERACIONAL_PROJETO.md`
- `relatorios/atuais/LEIA-ME_OPERACIONAL.md`
- `relatorios/INDICE_RELATORIOS.md`
- `README.md`

## Efeito esperado

A V180 elimina a ambiguidade entre contrato histórico, contrato intermediário e contrato vigente, preparando o repositório para derivar `resolver_dia(t, E_t)` diretamente da V179.

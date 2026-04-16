# BASELINE FIXA V38

## Escopo desta derivação

Esta derivação consolida a formalização documental da regra geral introduzida na V37 para lotes com `Data Recebimento` e `Data Aplicação` distintas.

## Texto canônico oficial da regra

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.

## Uso documental

Este texto deve ser tratado como a formulação oficial curta da baseline para:

- relatórios de auditoria;
- README operacional;
- documentação de regras ativas do replay histórico;
- futuras referências sobre disponibilidade temporal de lotes.

## Observação operacional

A regra acima não é específica do `Lote 5680 abr.`. Ela passa a valer como convenção geral do projeto para qualquer lote em que o recebimento anteceda a aplicação.

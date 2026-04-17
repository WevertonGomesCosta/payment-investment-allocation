# Baseline fixa V52

A V52 explicita no núcleo financeiro a convenção operacional adotada para rendimento de lotes:

- **dia 0** = data de aplicação, sem rendimento do lote;
- **dia 1 em diante** = o lote já pode render, conforme a série CDI disponível e as regras do produto.

A alteração foi incorporada de forma contextual ao lote, evitando que o dia da aplicação seja marcado ou tratado como dia econômico de rendimento.


## Ajuste V52

A geração da auditoria diária do lote passou a alinhar `Dia rendimento`, `Dias úteis` e `Dias úteis efetivos` à mesma convenção econômica da série CDI.


## Ajuste V52

- reorganização da saída do console: núcleo financeiro e replay controlado divididos em seções de resumo/valuation e amostras; observações da carteira canônica movidas para seção própria.


## Ajuste V52

A seção `Situação atual — lotes ativos` foi dividida em duas tabelas: uma para identificação/tempo e outra para valores atuais.

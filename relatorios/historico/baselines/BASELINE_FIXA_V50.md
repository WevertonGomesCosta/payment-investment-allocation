# Baseline fixa V50

A V50 explicita no núcleo financeiro a convenção operacional adotada para rendimento de lotes:

- **dia 0** = data de aplicação, sem rendimento do lote;
- **dia 1 em diante** = o lote já pode render, conforme a série CDI disponível e as regras do produto.

A alteração foi incorporada de forma contextual ao lote, evitando que o dia da aplicação seja marcado ou tratado como dia econômico de rendimento.


## Ajuste V50

A geração da auditoria diária do lote passou a alinhar `Dia rendimento`, `Dias úteis` e `Dias úteis efetivos` à mesma convenção econômica da série CDI.

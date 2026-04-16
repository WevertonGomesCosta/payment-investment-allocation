# BASELINE FIXA V40

## Escopo desta derivação

Esta derivação consolida uma limpeza adicional da saída operacional do script, reorganiza a apresentação do console, aplica o filtro de materialidade diretamente na tabela de inconsistências do replay e gera a planilha operacional com as abas `Extrato passado`, `Extrato futuro`, `Melhores produtos` e `Situação atual`.

## Ajustes operacionais consolidados

- remoção, da saída principal do console, das auditorias já encerradas de:
  - lotes vs. app;
  - recebimento vs. aplicação;
  - lotes residuais;
- reordenação do `RESUMO ESTRUTURAL DAS ABAS PRIMÁRIAS` para logo após a leitura das abas;
- separação dos `Top produtos selecionados` em seção própria no console;
- filtro da tabela de inconsistências do replay para exibir apenas itens **materiais acima do limiar operacional**;
- inclusão da tabela final de lotes ativos com recebimento, aplicação, produto, dias, bruto, líquido e saldo remanescente;
- geração da planilha operacional `.xlsx` em `saidas/relatorio_operacional_v40.xlsx`.

## Regra operacional consolidada

A tabela de inconsistências do replay controlado deve refletir apenas inconsistências materiais acima do limiar operacional vigente. Itens residuais abaixo ou iguais ao limiar continuam registrados internamente para auditoria, mas não devem poluir a saída principal do console nem acionar alerta operacional de inconsistência material.

## Regra canônica mantida da baseline

> Quando um lote possuir `Data Recebimento` e `Data Aplicação` distintas, o valor deve ser tratado como **caixa pré-aplicação** no intervalo entre essas datas. Nessa janela, o lote já pode ser usado para pagamentos, mas ainda **não rende**, **não sofre tributação de investimento** e **não obedece à carência do produto**. O regime financeiro do investimento só passa a valer a partir da efetiva `Data Aplicação`.

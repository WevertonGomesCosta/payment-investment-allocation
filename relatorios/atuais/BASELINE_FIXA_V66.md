# Baseline fixa V66

## Objetivo desta versão

Derivar a V65 de forma cirúrgica para ajustar apenas a camada de exibição e a normalização operacional de resíduos sub-limiar na situação atual, removendo a tabela detalhada de recebidos do console e da planilha operacional, separando o fechamento econômico em aba própria do `.xlsx` e corrigindo o caso do `Lote 4124,75 fev.` que aparecia exaurido com saldo remanescente positivo abaixo do limiar.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- remoção da tabela `situação atual de todos os recebidos (inclui exauridos)` do console e da aba `Situação atual`;
- criação da aba separada `Fechamento econômico atual` no `.xlsx`;
- normalização pós-replay de lotes com saldo bruto residual menor ou igual ao limiar operacional, zerando `saldo_bruto` e `principal_remanescente` e marcando o lote como esgotado;
- ajuste do script de auditoria diária para gerar nomes de arquivo coerentes com o lote informado.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V66. O motor financeiro, a lógica de valuation e a etapa funcional já aberta da F1 continuam preservados; a correção desta versão atua apenas na normalização operacional final de resíduos sub-limiar e na camada de exibição dos artefatos.

## Critério desta baseline

A V66 preserva a baseline funcional da V65 e corrige a inconsistência operacional na situação atual em que um lote já tratado como exaurido pelo limiar ainda aparecia com `Saldo rem` positivo. Ao mesmo tempo, simplifica a leitura dos artefatos correntes removendo a tabela detalhada de recebidos da seção/aba atual e isolando o fechamento econômico da situação atual em aba própria.

## Atualização V66

- manutenção da V65 como baseline oficial de partida;
- manutenção do release checker como gate obrigatório;
- remoção da tabela detalhada de recebidos do console e da planilha;
- criação da aba `Fechamento econômico atual`;
- correção do estado final do `Lote 4124,75 fev.` via normalização pós-replay de resíduos sub-limiar;
- preservação do motor financeiro, do replay histórico e da F1 fora do fluxo decisório principal.

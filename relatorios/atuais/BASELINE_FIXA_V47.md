# BASELINE FIXA V47

## Objetivo da derivação
Atualizar a baseline V46 com o novo arquivo `dados/cache_bcb.json` enviado pelo usuário e revalidar a situação atual dos lotes com a série CDI mais recente disponível no repositório.

## Mudança principal
- substituição de `dados/cache_bcb.json` pela nova versão com atualização em `2026-04-16` e fator diário disponível até `2026-04-15`;
- manutenção da regra de data de referência corrente com fallback controlado do último fator CDI disponível;
- regeneração da planilha operacional em `saidas/relatorio_operacional_v47.xlsx`.

## Leitura operacional
Com o novo cache, a foto econômica da situação atual passa a considerar mais um dia útil de rendimento para os lotes em aberto quando comparada ao cache anterior, o que afeta principalmente os lotes ainda ativos de fevereiro, março e abril.

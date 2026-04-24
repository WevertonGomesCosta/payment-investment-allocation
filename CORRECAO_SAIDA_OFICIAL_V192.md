# Correção operacional da saída oficial — V192

## Escopo
Correção apenas da camada observável, mantendo intactos contrato mestre, modelo oficial, núcleo econômico e estrutura diária por pacotes.

## Ajustes aplicados
- atualização do versionamento operacional para V192;
- correção da classificação de lotes na situação atual do console e do `.xlsx`:
  - lotes futuros não entram mais em `lotes exauridos` nem em `lotes ativos`;
  - lotes com `saldo_bruto`, `saldo_liquido` ou `saldo_rem` dentro do limiar são tratados como exauridos/resolvidos;
- redução de poluição nas tabelas da situação atual do console com limite de linhas exibidas;
- reescrita do bloco `SWITCHINGS CANDIDATOS / CLASSIFICADOS` do console para usar a priorização oficial do ranking vigente, independente de datas de pagamento;
- renomeação do relatório oficial para `relatorio_operacional_v192.xlsx`;
- simplificação da aba `Switching` do `.xlsx` para refletir primeiro os destinos priorizados pelo ranking oficial;
- remoção da aba legada `Melhores produtos` do relatório final.

## Validação local
- `compileall` passou;
- execução curta do console avançou até a situação atual sem novo traceback;
- o console passou a exibir:
  - destinos priorizados do ranking vigente no bloco de switching;
  - lotes futuros fora das tabelas de situação atual;
  - lote residual de baixo valor fora da lista de ativos quando dentro do limiar;
- o relatório `saidas/oficial/relatorio_operacional_v192.xlsx` foi gerado com abas:
  - `Extrato Passado`
  - `Extrato Futuro`
  - `Switching`
  - `Situação Atual`
  - `Carteira`
  - `Ranking_Completo`
  - `Top30`
  - `Destinos_Switch`
  - `Resumo`
  - `Validacao`

# Baseline fixa V43

## Escopo
A V43 consolida uma limpeza ampliada do repositório e adota a nova planilha `dados/dados_financeiros.xlsx` como base canônica atual da baseline.

## Ajustes desta versão
- atualização do arquivo canônico de dados para a nova base enviada pelo usuário;
- remoção de resíduos de versões anteriores na raiz do repositório;
- manutenção apenas da documentação vigente em `relatorios/atuais/`;
- movimentação das antigas baselines e validações correntes para `relatorios/historico/`;
- limpeza do diretório `saidas/`, preservando apenas o artefato operacional atual quando gerado localmente;
- atualização da versão exibida pela baseline para `V43`.

## Regra operacional desta versão
A baseline atual deve ser lida como um pacote limpo e controlado: dados canônicos atualizados em `dados/`, documentação vigente em `relatorios/atuais/`, histórico preservado em `relatorios/historico/` e ausência de artefatos efêmeros ou resíduos de versões anteriores fora dessas trilhas.

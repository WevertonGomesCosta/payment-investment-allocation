# Estrutura do repositório V99

## Camada nova da V99

A V99 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.

## Papel da V99

A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.


## Ajuste fino da V99

A V99 mantém a estrutura da V97, mas simplifica a leitura da amostra curta de pagamentos futuros para privilegiar apenas os campos úteis à validação humana imediata: lote sugerido, score proxy, status local e leitura técnica temporal.


## Ajuste estrutural da V99

A V99 mantém a estrutura da V98, mas passa a projetar no extrato futuro da planilha a mesma camada de auditabilidade financeira já exibida no console, sem abrir solver ou replanejamento temporal.

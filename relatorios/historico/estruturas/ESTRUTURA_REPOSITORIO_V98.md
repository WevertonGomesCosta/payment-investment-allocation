# Estrutura do repositório V98

## Camada nova da V98

A V98 adiciona uma camada leve de observabilidade ao console principal, usando o histórico do `replay_passado` para exibir uma amostra dos pagamentos já realizados e a agenda de `gastos_canonicos` para exibir os próximos pagamentos.

## Papel da V98

A baseline melhora a auditabilidade operacional dos pagamentos futuros sem abrir nenhuma nova frente metodológica e sem alterar o fluxo principal da baseline.


## Ajuste fino da V98

A V98 mantém a estrutura da V97, mas simplifica a leitura da amostra curta de pagamentos futuros para privilegiar apenas os campos úteis à validação humana imediata: lote sugerido, score proxy, status local e leitura técnica temporal.

# Baseline fixa V118

A V118 é a baseline **funcional mínima** da nova camada temporal do projeto.

## Papel da V118

- preservar a baseline central V108 como referência contratual;
- preservar a V116 como baseline operacional anterior por conta;
- manter o contrato V117 do motor conjunto temporal;
- implementar a **primeira integração funcional mínima** entre:
  - `planejador_switching_temporal_v1`;
  - `alocador_pagamentos_terminal_v1`;
  - `simulador_central_eventos_v1`;
  - `avaliador_cenarios_conjuntos_v1`.

## Estado congelado nesta entrega

- **baseline do repositório entregue:** V118
- **baseline central/contratual principal:** V108
- **baseline operacional anterior por conta:** V116
- **camada central temporal mínima integrada:** V118

## Escopo efetivo da V118

A V118 já executa um recorte curto real de datas críticas, com:

- geração de ações temporais candidatas de switching em data autônoma;
- comparação de fontes de pagamento por perda terminal proxy;
- combinação mínima funcional entre fontes;
- simulação sequencial curta com consumo residual de recursos;
- vetor central auditável por cenário.

A V118 ainda **não** é solver global completo e **não** substitui a frente central V108.

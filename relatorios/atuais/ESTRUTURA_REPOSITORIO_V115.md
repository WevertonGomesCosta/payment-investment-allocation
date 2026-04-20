# Estrutura repositório V115

Principais ajustes:

- `scripts/diagnostico/_bootstrap.py`
- `relatorios/atuais/REORGANIZACAO_REPOSITORIO_V115.md`
- `relatorios/atuais/BASELINE_FIXA_V115.md`
- `relatorios/atuais/VALIDACAO_LOCAL_V115.md`
- `relatorios/atuais/ESTRUTURA_REPOSITORIO_V115.md`

Movimentos estruturais:

- documentos antigos de baseline/validação/estrutura saíram de `relatorios/atuais/` e foram consolidados em `relatorios/historico/`;
- `saidas/operacional/` foi reduzida à saída vigente da baseline;
- diagnósticos foram padronizados com bootstrap compartilhado.

Preservado propositalmente:

- `nucleo/motor_recomendacao_pagamentos_switching_v1.py` como camada operacional por conta;
- wrappers raiz em `scripts/` como compatibilidade;
- documentação V108 da frente central como referência principal do motor conjunto.

# Recomputação sequencial central V107

A V107 implementa a `recomputacao_sequencial_central_v1` como primeira camada executável da frente central após o saneamento contratual da V106.

## Escopo

- recalcular a fonte a cada pagamento futuro;
- usar saldos residuais atualizados;
- comparar alternativas pela métrica canônica mínima central;
- manter rastreabilidade por lote e por fonte;
- não abrir solver global completo.

## Comparador mínimo

A ordem de prioridade aplicada continua sendo:

1. violações de pagamentos `PROTEGIDA`;
2. déficit líquido total;
3. pagamentos sem cobertura integral;
4. patrimônio terminal proxy do cenário;
5. destruição estratégica de lotes;
6. fragmentação residual e piora evitável de liquidez futura.

## Papel da V107

A V107 não resolve o problema conjunto final, mas recoloca a evolução do projeto na frente central, deixando V103–V105 explicitamente como trilha experimental local.

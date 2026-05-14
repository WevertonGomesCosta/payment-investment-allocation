# ME-V17-F0-Q3 — Validação XLSX pós-Q.2

## Identificação

- MICROETAPA: ME-V17-F0-Q3
- TIPO: DOCUMENTAL / DIAGNÓSTICO
- CLASSE: VALIDAÇÃO DE SAÍDA OPERACIONAL XLSX
- BASELINE DE ENTRADA: V225 com Q.2 aplicada
- COMMIT DE REFERÊNCIA DA Q.2: `e03e99b` — `V17-F0-Q.2: inclui passados pos no extrato passado`
- ARQUIVO VALIDADO: `saidas/oficial/relatorio_operacional_v225.xlsx`
- ABA VALIDADA: `Extrato Passado`

## Objetivo

Validar se a planilha operacional final gerada após a Q.2 passou a exibir, na aba `Extrato Passado`, os dois pagamentos passados com lotes pós-switching que motivaram a correção:

1. `2026-05-13 | Aluguel | 192.89 | Lote 190 mai`
2. `2026-05-13 | Pelada | 24.00 | Lote 3120 mai`

## Resultado da validação

A validação estrutural do XLSX localizou corretamente o arquivo `saidas/oficial/relatorio_operacional_v225.xlsx` e a aba `Extrato Passado`.

As abas detectadas foram:

- `Extrato Passado`
- `Extrato Futuro`
- `Switching`
- `Carteira`
- `Situação Atual`
- `Saida Canonica`
- `Auditoria Fontes`

O cabeçalho exportado da aba `Extrato Passado` foi:

```text
Data, Conta, Despesa ID, Lote, Saldo Antes, Bruto, Imposto, Líquido, Saldo Remanescente
```

As duas linhas-alvo foram encontradas:

```text
2026-05-13 | Aluguel | despesa_auto_00107 | Lote 190 mai |  | 192.89 | 0 | 192.89 |
2026-05-13 | Pelada  | despesa_auto_00111 | Lote 3120 mai |  | 24    | 0 | 24    |
```

## Ressalva de schema

A validação literal do script inicial exigia a coluna `Lotes usados`, mas essa coluna não é exportada na aba `Extrato Passado` do XLSX. A informação equivalente está presente na coluna `Lote`.

Esta diferença não bloqueia o objetivo da Q.3, pois os dois pagamentos foram localizados no XLSX com data, conta, identificador de despesa, valor líquido e lote correspondente.

## Veredito

Q.3 aprovada com ressalva.

O `relatorio_operacional_v225.xlsx` exibe:

- `Aluguel | 192.89 | Lote 190 mai` na aba `Extrato Passado`;
- `Pelada | 24.00 | Lote 3120 mai` na aba `Extrato Passado`.

## Restrições preservadas

- Não alterar motor.
- Não alterar ledger.
- Não alterar regra econômica.
- Não alterar schema nesta microetapa.
- Não alterar planilha de entrada.
- Não alterar cache.
- Não reabrir a lógica da Q.2.

## Encaminhamento

A Q.3 fica encerrada como validação documental/estrutural aprovada com ressalva.

A ausência da coluna `Lotes usados` no XLSX deve ser tratada, se necessário, em microetapa futura específica de schema/exportação, sem misturar com baixa POS, ledger ou motor econômico.

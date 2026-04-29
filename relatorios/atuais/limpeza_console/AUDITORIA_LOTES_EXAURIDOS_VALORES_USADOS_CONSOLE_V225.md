# Auditoria da tabela de lotes exauridos com valores usados — V225

## Identificação

- Baseline: V225
- Escopo: seção `SITUAÇÃO ATUAL` do console
- Arquivo alterado: `aplicacao/console/principal.py`

## Problema

A tabela de valores dos lotes exauridos apresentava `Bruto` e `Líquido` como valores atuais do lote. Como lotes exauridos têm saldo atual zerado, a tabela mostrava `0.00`, embora o usuário precise ver o valor bruto e líquido efetivamente usado pelo lote.

## Correção aplicada

Foi adicionada uma camada observável no console que monta `lotes_exauridos_valores` a partir de `replay_passado.log_passado`.

Para cada lote exaurido:

```text
Bruto = soma de Bruto no log_passado para o lote
Líquido = soma de Liquido no log_passado para o lote
Saldo rem = 0.00
```

A identificação e o tempo dos lotes exauridos permanecem consumindo `saida_canonica.lotes_exauridos`.

## Restrições respeitadas

Não houve alteração em:

- replay;
- cálculo econômico;
- pagamentos;
- switching;
- ranking;
- planilha operacional;
- cache;
- identidade da baseline.

A alteração ficou restrita à tabela exibida no console.

## Validação local necessária

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

- execução sem erro;
- saída em `saidas/oficial/relatorio_operacional_v225.xlsx`;
- tabela `lotes exauridos > valores atuais` exibindo Bruto/Líquido usados por lote, e não saldo atual zerado;
- sem alteração econômica observável fora da camada de console.

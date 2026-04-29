# Auditoria da correção da fórmula de rendimento total — V225

## Identificação

- Baseline: V225
- Escopo: seção final `RENDIMENTO TOTAL DOS LOTES` no console
- Arquivo alterado: `aplicacao/console/principal.py`
- Resultado: fórmula corrigida no resumo exibido no console

## Problema identificado

A versão anterior calculava o rendimento total como:

```text
(bruto já resgatado + bruto atual remanescente) - valor original total
(líquido já resgatado + líquido atual remanescente) - valor original total
```

Essa fórmula não representava a leitura operacional desejada pelo usuário para o retorno total já obtido nos lotes.

## Correção aplicada

A fórmula foi corrigida para:

```text
rendimento bruto total obtido = valor original total - bruto já resgatado + bruto atual remanescente
rendimento líquido total obtido = valor original total - líquido já resgatado + líquido atual remanescente
```

## Restrições respeitadas

Não houve alteração em:

- cálculo econômico dos motores;
- replay;
- pagamentos;
- switching;
- ranking;
- planilha operacional;
- cache;
- identidade da baseline.

A alteração ficou restrita ao cálculo resumido exibido no console.

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
- seção `RENDIMENTO TOTAL DOS LOTES` exibida;
- rendimento bruto calculado como `valor original total - bruto já resgatado + bruto atual remanescente`;
- rendimento líquido calculado como `valor original total - líquido já resgatado + líquido atual remanescente`;
- sem alteração econômica observável fora dessa exibição de console.

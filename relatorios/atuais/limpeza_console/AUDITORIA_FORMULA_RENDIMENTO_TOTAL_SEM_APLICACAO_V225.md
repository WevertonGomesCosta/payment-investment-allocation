# Auditoria da fórmula de rendimento total com exclusão de lotes sem aplicação — V225

## Identificação

- Baseline: V225
- Escopo: seção `RENDIMENTO TOTAL DOS LOTES` no console
- Arquivo alterado: `aplicacao/console/principal.py`

## Ajuste solicitado

O usuário esclareceu que lotes exauridos sem aplicação não devem compor a base de capital aplicado, pois esses valores não foram efetivamente investidos.

## Fórmula aplicada

Foi criada a métrica intermediária:

```text
valor original aplicado ajustado = valor original total - valor original exaurido sem aplicação
```

A fórmula de rendimento passa a ser:

```text
rendimento bruto total obtido = valor original aplicado ajustado - bruto já resgatado - bruto atual remanescente
rendimento líquido total obtido = valor original aplicado ajustado - líquido já resgatado - líquido atual remanescente
```

Equivalente à forma expandida:

```text
rendimento bruto total obtido = valor original total - valor original exaurido sem aplicação - bruto já resgatado - bruto atual remanescente
rendimento líquido total obtido = valor original total - valor original exaurido sem aplicação - líquido já resgatado - líquido atual remanescente
```

## Identificação dos lotes sem aplicação

Na saída canônica, a identificação foi feita pelos lotes exauridos cujo campo `Produto` indica ausência de aplicação:

```text
-
sem aplicação
sem aplicacao
não aplicado
nao aplicado
```

## Novas linhas no console

A seção passou a exibir:

```text
lotes exauridos sem aplicação
valor original exaurido sem aplicação
valor original aplicado ajustado
```

## Restrições respeitadas

Não houve alteração em:

- replay;
- pagamentos;
- switching;
- ranking;
- planilha operacional;
- cache;
- identidade da baseline.

A alteração ficou restrita ao resumo exibido no console.

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
- seção `RENDIMENTO TOTAL DOS LOTES` exibindo as novas linhas;
- fórmula auditável com exclusão dos lotes exauridos sem aplicação;
- sem alteração econômica observável fora da exibição do console.

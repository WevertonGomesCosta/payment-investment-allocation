# Auditoria da reorganização de patrimônio dos lotes — V225

## Identificação

- Baseline: V225
- Escopo: console e aba `Situação Atual` da planilha operacional
- Arquivos alterados:
  - `aplicacao/console/principal.py`
  - `nucleo/gerar_planilha_operacional.py`

## Alterações no console

### Lotes exauridos

A tabela de valores dos lotes exauridos foi renomeada para refletir valores usados no replay:

```text
Bruto Sacado
Líquido Sacado
Patrimônio líquido
Rendimento líquido
```

A coluna `Saldo rem` deixou de ser exibida nessa tabela.

### Lotes ativos

A tabela de valores dos lotes ativos foi renomeada para refletir saldos atuais:

```text
Bruto Atual
Líquido Atual
Patrimônio líquido atual
Rendimento líquido atual
```

A coluna `Saldo rem` deixou de ser exibida nessa tabela.

### Patrimônio total dos lotes

A seção final foi renomeada de `RENDIMENTO TOTAL DOS LOTES` para:

```text
PATRIMÔNIO TOTAL DOS LOTES
```

As métricas exibidas passaram a ser:

```text
Valor original total
Valor original exaurido sem aplicação
Valor original aplicado ajustado
Valor total bruto sacado
Valor total líquido sacado
Valor bruto atual
Valor líquido atual
Patrimônio líquido atual
Rendimento líquido atual
```

## Alterações na planilha operacional

Na aba `Situação Atual`, as seções foram reorganizadas para:

1. `Lotes exauridos — identificação e tempo`
2. `Lotes exauridos — valores sacados e patrimônio`
3. `Lotes ativos — identificação e tempo`
4. `Lotes ativos — valores atuais e patrimônio`
5. `Patrimônio total dos lotes`
6. `Recebidos auditáveis`
7. `Fechamento econômico`
8. `Resumo de recebidos`

A seção `Patrimônio total dos lotes` foi posicionada antes de `Recebidos auditáveis`, conforme solicitado.

## Aba removida

A aba `Validacao` deixou de ser criada na planilha operacional.

## Fórmulas adotadas

Para lotes exauridos:

```text
Patrimônio líquido = Líquido Sacado
Rendimento líquido = Patrimônio líquido - Valor original
```

Para lotes ativos:

```text
Patrimônio líquido atual = Líquido Sacado + Líquido Atual
Rendimento líquido atual = Patrimônio líquido atual - Valor original
```

Para o resumo total:

```text
Patrimônio líquido atual = Valor total líquido sacado + Valor líquido atual
Rendimento líquido atual = Patrimônio líquido atual - Valor original aplicado ajustado
```

## Restrições respeitadas

Não houve alteração em:

- replay;
- cálculo econômico dos motores;
- pagamentos;
- switching;
- ranking;
- cache;
- identidade da baseline.

As mudanças foram restritas à camada observável do console e da planilha operacional.

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
- console com `PATRIMÔNIO TOTAL DOS LOTES`;
- aba `Situação Atual` com as novas colunas e resumo antes de `Recebidos auditáveis`;
- ausência da aba `Validacao`;
- sem alteração econômica observável fora da camada de apresentação.

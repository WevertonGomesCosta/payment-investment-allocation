# BASELINE FIXA V36

## Escopo desta derivação

A V36 parte da V35 e aplica apenas correções cirúrgicas necessárias para:

1. aceitar a nova base `dados/dados_financeiros.xlsx` enviada pelo usuário;
2. robustecer a leitura de datas vazias/`NaT` no inventário de lotes;
3. corrigir a indexação regressiva do IOF para resgates curtos;
4. reauditar o `Lote 10342 fev.` com a nova planilha e comparar os eventos críticos contra os comprovantes do app.

## Alterações implementadas

### 1. Leitura robusta de datas vazias
Arquivo: `nucleo/utilitarios_neutros.py`

- `para_data(...)` agora testa `pd.isna(valor)` antes de tratar o valor como `date`/`datetime`.
- Isso evita que `pandas.NaT` seja propagado como data válida e quebre a classificação dos lotes futuros da nova planilha.

### 2. Correção da indexação da tabela regressiva do IOF
Arquivo: `nucleo/nucleo_financeiro_minimo.py`

- a função `_taxa_iof(dias, ...)` passou a usar `dias - 1` como índice efetivo da tabela;
- isso alinha a leitura com a convenção econômica da tabela regressiva brasileira, em que o primeiro dia usa a primeira linha (96%), o sétimo dia usa a sétima linha (76%) etc.;
- o mapeamento anterior subestimava o IOF em resgates curtos.

## Resultado principal da reauditoria

### Lote 10342 fev.

Com a nova planilha e a correção do IOF:

- o agrupamento de `12/02/2026` passou a bater no líquido do app e ficou com diferença de apenas `R$ 0,02` no bruto e no imposto total;
- o evento de `13/03/2026` passou a ficar com diferença de `R$ 0,01` no líquido, `R$ 0,02` no bruto e `R$ 0,01` no imposto;
- o lote saiu da classe de resíduo material e passou a ficar operacionalmente dentro do limiar centesimal.

### Situação residual dos lotes auditados

- `Lote 10342 fev.`: resolvido por arredondamento/limiar;
- `Lote 4000 fev.`: dentro do limiar operacional;
- `Lote 4124,75 fev.`: micro-saldo `R$ 0,12`, resolvido por limiar.

## Restrições mantidas

Nada foi aberto além do escopo autorizado. Permanecem fechados:

- solver;
- switching econômico;
- score econômico final;
- relatório financeiro atual;
- engine completa.

# Auditoria da reorganização do console operacional — V225

## Identificação

- Baseline: V225
- Escopo: console operacional e política de cache CDI/BCB
- Arquivos alterados:
  - `aplicacao/console/secoes_execucao.py`
  - `aplicacao/console/principal.py`
  - `nucleo/cache_cdi_bcb.py`
- Resultado: console mais enxuto e informação final de rendimento total dos lotes

## Restrições respeitadas

Não houve alteração intencional em:

- cálculo econômico dos motores;
- replay;
- pagamentos;
- switching;
- ranking;
- estrutura da planilha operacional;
- identidade da baseline.

## Alterações no console

### Execução / ambiente

Removido do console:

```text
colab
```

A seção `AMBIENTE` foi renomeada para `EXECUÇÃO` e mantém apenas informações operacionais relevantes:

```text
timezone
data de referência
warnings de rede configurados
```

### Cache CDI / BCB

Removido do console:

```text
dias de rendimento no mês até a data de referência
```

Adicionados campos de auditoria do cache:

```text
cache atualizado para referência
data de atualização do cache
```

### Ranking

Na amostra de ranking, foi removida a coluna:

```text
Status
```

Colunas mantidas:

```text
Rank
Produto
Score
Proxy terminal
Liquidez
Carência
Ticket mín.
```

### Switching

Na amostra de switching, foram removidas as colunas:

```text
Ganho estimado
Status
```

Colunas mantidas:

```text
Data
Lote origem
Produto origem
Destino
```

### Rendimento total dos lotes

Foi criada a seção final:

```text
RENDIMENTO TOTAL DOS LOTES
```

Ela considera lotes ativos e exauridos da saída canônica e soma:

- valor original total;
- bruto já resgatado;
- líquido já resgatado;
- bruto atual remanescente;
- líquido atual remanescente;
- rendimento bruto total obtido;
- rendimento líquido total obtido.

A intenção é dar uma visão direta do retorno total já obtido, incluindo lotes exauridos.

## Política de planilha

A planilha já seguia a ordem correta no módulo `nucleo/leitor_planilha.py`:

1. tenta baixar a planilha para `dados/dados_financeiros.xlsx`;
2. valida minimamente o arquivo baixado via `pd.ExcelFile`;
3. substitui o arquivo local apenas se o download for válido;
4. depois carrega a planilha local.

Portanto, não foi necessária alteração nessa frente.

## Política de cache BCB

O módulo `nucleo/cache_cdi_bcb.py` foi ajustado para não consultar o BCB quando o cache local já estiver marcado como atualizado para a data de referência.

Nova regra:

- se `cache_bcb.json` tiver `data_atualizacao >= data_referencia` e série válida, usar `cache_local` e marcar `fetch_status = cache_atualizado_sem_fetch`;
- caso contrário, tentar buscar BCB online;
- ao salvar novo cache, registrar `data_atualizacao` como a própria data de referência.

## Validação local necessária

Executar:

```bash
cd ~/OneDrive/GitHub/payment-investment-allocation
git pull
python aplicacao/principal.py
```

Critérios esperados:

1. execução sem erro;
2. saída em `saidas/oficial/relatorio_operacional_v225.xlsx`;
3. console mais enxuto;
4. ausência de `colab`;
5. ausência de `dias de rendimento no mês até a data de referência`;
6. amostra de ranking sem `Status`;
7. amostra de switching sem `Ganho estimado` e `Status`;
8. seção final `RENDIMENTO TOTAL DOS LOTES` exibida;
9. sem alteração econômica observável.

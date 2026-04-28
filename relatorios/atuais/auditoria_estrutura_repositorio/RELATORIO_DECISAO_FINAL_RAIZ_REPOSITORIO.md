# Decisão final — raiz do repositório

## Objetivo

Registrar a decisão final sobre os arquivos rastreados diretamente na raiz do repositório após auditoria estrutural.

## Resultado da auditoria

A auditoria da raiz avaliou 7 arquivos rastreados diretamente na raiz.

| Classe | Arquivos | Decisão |
|---|---:|---|
| `MANTER_RAIZ_CONFIG_EXECUCAO` | 1 | manter |
| `MANTER_RAIZ_CONFIG_REPOSITORIO` | 3 | manter |
| `MANTER_RAIZ_DOCUMENTO_PADRAO` | 2 | manter |
| `REVISAR_AMBIENTE_IDE` | 1 | manter após decisão explícita |

## Decisão sobre arquivo de IDE

O arquivo abaixo foi revisado explicitamente:

- `payment-investment-allocation.Rproj`

Decisão final:

~~~text
MANTER_RASTREADO_NA_RAIZ
~~~

Justificativa: o arquivo `.Rproj` representa o ambiente de projeto usado operacionalmente e deve permanecer disponível na raiz para facilitar abertura, execução e continuidade local do repositório.

## Decisão final da raiz

Todos os 7 arquivos rastreados diretamente na raiz devem permanecer na raiz.

Nenhum arquivo da raiz deve ser removido, movido ou ignorado nesta etapa.

# Contrato futuro de mapeamento chave/cabeçalho — aba `Situação Atual` — V225

## Identificação

- Baseline operacional: V225
- Tipo: contrato futuro documental
- Classe: camada observável / planilha operacional
- Escopo: aba `Situação Atual` da planilha operacional
- Arquivo relacionado: `scripts/operacional/gerar_planilha_operacional.py`
- Origem canônica relacionada: `nucleo/saida_canonica.py`

## Restrições desta microetapa

Esta microetapa é exclusivamente documental.

Não alterar:

- código;
- `dados/config_atualizado.json`;
- cálculo;
- replay;
- pagamentos;
- switching;
- ranking;
- identidade da baseline;
- nomes atuais das abas;
- cabeçalhos atuais da planilha;
- estrutura atual do arquivo XLSX.

## Objetivo

Definir uma estrutura segura para parametrização futura da aba `Situação Atual`, separando explicitamente:

- `chave`: identificador interno usado para extrair dados dos dicionários da saída canônica;
- `cabecalho`: rótulo exibido na planilha operacional;
- `titulo`: título visual da seção dentro da aba.

A separação é necessária porque, no estado atual, os mesmos textos usados como cabeçalhos visuais também são usados como chaves em `_rows(...)`. Se apenas o cabeçalho for alterado no config, a planilha pode passar a gerar colunas vazias.

## Princípio do contrato

Toda coluna configurável da aba `Situação Atual` deve ser representada por objeto com pelo menos dois campos:

```json
{
  "chave": "Saldo rem",
  "cabecalho": "Saldo rem"
}
```

Regra:

- `chave` nunca deve ser alterada sem mudança correspondente na saída canônica;
- `cabecalho` pode ser alterado para melhorar apresentação;
- a extração dos dados deve usar `chave`;
- a escrita da linha de cabeçalho na planilha deve usar `cabecalho`.

## Estrutura futura recomendada no config

A estrutura futura recomendada para `dados/config_atualizado.json` é:

```json
{
  "saidas": {
    "planilha_operacional": {
      "situacao_atual": {
        "secoes": {
          "lotes_exauridos": {
            "titulo": "Lotes exauridos",
            "origem": "saida.lotes_exauridos",
            "colunas": [
              {"chave": "Lote", "cabecalho": "Lote"},
              {"chave": "Recebimento", "cabecalho": "Recebimento"},
              {"chave": "Aplicação", "cabecalho": "Aplicação"},
              {"chave": "Último uso", "cabecalho": "Último uso"},
              {"chave": "Produto", "cabecalho": "Produto"},
              {"chave": "Dias corridos", "cabecalho": "Dias corridos"},
              {"chave": "Dias úteis", "cabecalho": "Dias úteis"},
              {"chave": "Valor original", "cabecalho": "Valor original"},
              {"chave": "Bruto", "cabecalho": "Bruto"},
              {"chave": "Líquido", "cabecalho": "Líquido"},
              {"chave": "Saldo rem", "cabecalho": "Saldo rem"}
            ]
          },
          "lotes_ativos": {
            "titulo": "Lotes ativos",
            "origem": "saida.lotes_ativos",
            "colunas": [
              {"chave": "Lote", "cabecalho": "Lote"},
              {"chave": "Recebimento", "cabecalho": "Recebimento"},
              {"chave": "Aplicação", "cabecalho": "Aplicação"},
              {"chave": "Produto", "cabecalho": "Produto"},
              {"chave": "Dias corridos", "cabecalho": "Dias corridos"},
              {"chave": "Dias úteis", "cabecalho": "Dias úteis"},
              {"chave": "Valor original", "cabecalho": "Valor original"},
              {"chave": "Bruto", "cabecalho": "Bruto"},
              {"chave": "Líquido", "cabecalho": "Líquido"},
              {"chave": "Saldo rem", "cabecalho": "Saldo rem"}
            ]
          },
          "recebidos_atuais": {
            "titulo": "Recebidos auditáveis",
            "origem": "saida.recebidos_atuais",
            "colunas": [
              {"chave": "Recebido", "cabecalho": "Recebido"},
              {"chave": "Lote origem", "cabecalho": "Lote origem"},
              {"chave": "Recebimento", "cabecalho": "Recebimento"},
              {"chave": "Aplicação", "cabecalho": "Aplicação"},
              {"chave": "Valor bruto", "cabecalho": "Valor bruto"},
              {"chave": "Valor líquido", "cabecalho": "Valor líquido"},
              {"chave": "Status", "cabecalho": "Status"},
              {"chave": "Destino", "cabecalho": "Destino"},
              {"chave": "Pagamentos vinculados", "cabecalho": "Pagamentos vinculados"},
              {"chave": "Valor vinculado", "cabecalho": "Valor vinculado"},
              {"chave": "Residual aplicação", "cabecalho": "Residual aplicação"},
              {"chave": "Disponível ref", "cabecalho": "Disponível ref"},
              {"chave": "Observação", "cabecalho": "Observação"}
            ]
          },
          "fechamento_atual": {
            "titulo": "Fechamento econômico",
            "origem": "saida.fechamento_atual",
            "colunas": [
              {"chave": "Métrica", "cabecalho": "Métrica"},
              {"chave": "Valor", "cabecalho": "Valor"}
            ]
          },
          "resumo_recebidos": {
            "titulo": "Resumo de recebidos",
            "origem": "saida.resumo_recebidos",
            "colunas": [
              {"chave": "Métrica", "cabecalho": "Métrica"},
              {"chave": "Valor", "cabecalho": "Valor"}
            ]
          }
        },
        "ordem_secoes": [
          "lotes_exauridos",
          "lotes_ativos",
          "recebidos_atuais",
          "fechamento_atual",
          "resumo_recebidos"
        ]
      }
    }
  }
}
```

## Contrato por seção

### 1. `lotes_exauridos`

Origem:

```text
saida.lotes_exauridos
```

Título atual:

```text
Lotes exauridos
```

Colunas atuais:

| Chave interna | Cabeçalho exibido | Regra futura |
|---|---|---|
| `Lote` | `Lote` | chave estável |
| `Recebimento` | `Recebimento` | chave estável |
| `Aplicação` | `Aplicação` | chave estável |
| `Último uso` | `Último uso` | formalizar antes de renomear |
| `Produto` | `Produto` | chave estável |
| `Dias corridos` | `Dias corridos` | chave estável |
| `Dias úteis` | `Dias úteis` | chave estável |
| `Valor original` | `Valor original` | chave estável |
| `Bruto` | `Bruto` | chave estável |
| `Líquido` | `Líquido` | chave estável |
| `Saldo rem` | `Saldo rem` | formalizar antes de renomear |

### 2. `lotes_ativos`

Origem:

```text
saida.lotes_ativos
```

Título atual:

```text
Lotes ativos
```

Colunas atuais:

| Chave interna | Cabeçalho exibido | Regra futura |
|---|---|---|
| `Lote` | `Lote` | chave estável |
| `Recebimento` | `Recebimento` | chave estável |
| `Aplicação` | `Aplicação` | chave estável |
| `Produto` | `Produto` | chave estável |
| `Dias corridos` | `Dias corridos` | chave estável |
| `Dias úteis` | `Dias úteis` | chave estável |
| `Valor original` | `Valor original` | chave estável |
| `Bruto` | `Bruto` | chave estável |
| `Líquido` | `Líquido` | chave estável |
| `Saldo rem` | `Saldo rem` | formalizar antes de renomear |

### 3. `recebidos_atuais`

Origem:

```text
saida.recebidos_atuais
```

Título atual:

```text
Recebidos auditáveis
```

Colunas atuais:

| Chave interna | Cabeçalho exibido | Regra futura |
|---|---|---|
| `Recebido` | `Recebido` | chave estável |
| `Lote origem` | `Lote origem` | chave estável |
| `Recebimento` | `Recebimento` | chave estável |
| `Aplicação` | `Aplicação` | chave estável |
| `Valor bruto` | `Valor bruto` | chave estável |
| `Valor líquido` | `Valor líquido` | chave estável |
| `Status` | `Status` | chave estável |
| `Destino` | `Destino` | chave estável |
| `Pagamentos vinculados` | `Pagamentos vinculados` | chave estável |
| `Valor vinculado` | `Valor vinculado` | chave estável |
| `Residual aplicação` | `Residual aplicação` | formalizar antes de renomear |
| `Disponível ref` | `Disponível ref` | formalizar antes de renomear |
| `Observação` | `Observação` | formalizar antes de renomear |

### 4. `fechamento_atual`

Origem:

```text
saida.fechamento_atual
```

Título atual:

```text
Fechamento econômico
```

Colunas atuais:

| Chave interna | Cabeçalho exibido | Regra futura |
|---|---|---|
| `Métrica` | `Métrica` | chave genérica estável |
| `Valor` | `Valor` | chave genérica estável |

### 5. `resumo_recebidos`

Origem:

```text
saida.resumo_recebidos
```

Título atual:

```text
Resumo de recebidos
```

Colunas atuais:

| Chave interna | Cabeçalho exibido | Regra futura |
|---|---|---|
| `Métrica` | `Métrica` | chave genérica estável |
| `Valor` | `Valor` | chave genérica estável |

## Validação recomendada para etapa futura

Antes de ativar esse contrato no código, a etapa futura deve validar:

1. todas as seções existem em `ordem_secoes`;
2. cada seção contém `titulo`, `origem` e `colunas`;
3. cada item de `colunas` contém `chave` e `cabecalho` não vazios;
4. nenhuma `chave` configurada está ausente nos dicionários reais da saída canônica, exceto quando a seção estiver vazia;
5. `cabecalho` pode divergir de `chave`, mas `chave` deve permanecer compatível com `PacoteSaidaCanonica`;
6. se o bloco futuro estiver ausente ou inválido, usar fallback local idêntico ao estado atual.

## Helper futuro recomendado

A implementação futura deve evitar reutilizar `_rows(itens, headers)` diretamente para a aba `Situação Atual`, porque esse helper assume que os cabeçalhos são também chaves internas.

Recomenda-se criar helper específico:

```python
def _rows_mapeadas(itens, colunas):
    return [[item.get(coluna["chave"]) for coluna in colunas] for item in itens]


def _headers_mapeados(colunas):
    return [coluna["cabecalho"] for coluna in colunas]
```

Assim, a extração usa `chave` e a exibição usa `cabecalho`.

## Fallback obrigatório

A implementação futura deve manter fallback local idêntico ao estado atual para todas as seções. Isso preserva compatibilidade quando:

- o bloco `saidas.planilha_operacional.situacao_atual` não existir;
- alguma seção estiver incompleta;
- alguma coluna estiver malformada;
- o config ainda estiver sendo migrado.

## O que não deve ser parametrizado nessa frente

Mesmo em etapa futura, esta frente não deve parametrizar:

- cores;
- fontes;
- bordas;
- formatos monetários;
- formatos de data;
- largura automática de colunas;
- espaçamento `r + 3`;
- regras de cálculo de lotes;
- regras de classificação de lotes ativos/exauridos;
- regras de construção de recebidos auditáveis;
- regras de fechamento econômico.

Esses itens devem permanecer locais ou em módulos próprios, não no contrato de cabeçalhos da planilha.

## Decisão da microetapa

A microetapa apenas documenta o contrato futuro. Nenhuma parametrização foi aplicada.

Decisão: a aba `Situação Atual` só deve ser parametrizada se for usado um contrato com pares `chave`/`cabecalho`. Parametrização por lista simples de cabeçalhos não é segura para essa aba.

## Próxima microetapa sugerida

Se for necessário avançar, a próxima microetapa deve ser apenas uma implementação mínima do helper futuro, ainda com fallback idêntico e sem modificar o config. Depois disso, em uma etapa separada, o bloco `saidas.planilha_operacional.situacao_atual` poderia ser adicionado ao config com valores iguais aos atuais.

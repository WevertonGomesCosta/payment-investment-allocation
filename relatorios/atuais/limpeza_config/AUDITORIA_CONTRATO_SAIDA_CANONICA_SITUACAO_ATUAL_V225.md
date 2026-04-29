# Auditoria do contrato da saída canônica — Situação Atual — V225

## Identificação

- Baseline operacional: V225
- Tipo: auditoria documental/diagnóstica
- Escopo: `nucleo/saida_canonica.py`
- Objetos auditados:
  - `lotes_exauridos`
  - `lotes_ativos`
  - `recebidos_atuais`
  - `fechamento_atual`
  - `resumo_recebidos`
- Restrições:
  - não alterar código;
  - não alterar `dados/config_atualizado.json`;
  - não alterar cálculo;
  - não alterar replay;
  - não alterar pagamentos;
  - não alterar switching;
  - não alterar ranking;
  - não alterar identidade da baseline.

## Objetivo

Classificar as chaves dos objetos da saída canônica usados pela aba `Situação Atual` da planilha operacional em três grupos:

1. contrato interno estável;
2. rótulo de apresentação;
3. item que deveria ser formalizado antes de qualquer parametrização adicional da planilha.

## Contexto técnico

O módulo `nucleo/saida_canonica.py` define a dataclass `PacoteSaidaCanonica`, que centraliza a camada observável oficial do projeto. O próprio cabeçalho do módulo declara que console, planilha e futuras saídas JSON/CSV/Markdown devem consumir esse pacote em vez de recalcular saldos, resgates, switchings ou amostras em paralelo.

Entre os campos oficiais da dataclass estão:

```text
lotes_ativos
lotes_exauridos
recebidos_atuais
fechamento_atual
resumo_recebidos
```

Esses campos são listas de dicionários (`list[dict[str, Any]]`) e, portanto, as chaves textuais usadas nesses dicionários funcionam como contrato prático entre a saída canônica, o console e a planilha operacional.

## Diagnóstico geral

A auditoria confirma que, para a aba `Situação Atual`, as chaves como `Lote`, `Recebimento`, `Aplicação`, `Bruto`, `Líquido`, `Saldo rem`, `Métrica` e `Valor` não são apenas rótulos visuais. Elas também são usadas como chaves de extração no gerador da planilha operacional.

Portanto, qualquer parametrização futura dos cabeçalhos da aba `Situação Atual` deve separar explicitamente:

```json
{
  "chave": "Saldo rem",
  "cabecalho": "Saldo rem"
}
```

Não é seguro permitir que o usuário altere apenas o texto do cabeçalho se esse mesmo texto continuar sendo usado como chave interna para extrair dados.

## Objeto 1 — `lotes_exauridos`

### Chaves observadas

```text
Lote
Recebimento
Aplicação
Último uso
Produto
Dias corridos
Dias úteis
Valor original
Bruto
Líquido
Saldo rem
```

### Origem funcional

Objeto construído a partir dos lotes após replay, com cálculo de idade, datas, valores brutos/líquidos e saldo remanescente na data de referência. A função de situação de lotes diferencia lotes ativos e exauridos, usa a data de referência, calendário financeiro, série CDI, tabela IOF, faixas de IR e limiar de resíduo resolvido.

### Classificação

| Chave | Classificação | Decisão |
|---|---|---|
| `Lote` | contrato interno estável | manter como chave canônica |
| `Recebimento` | contrato interno estável | manter como chave canônica |
| `Aplicação` | contrato interno estável | manter como chave canônica |
| `Último uso` | contrato interno específico de exauridos | formalizar antes de parametrizar |
| `Produto` | contrato interno estável | manter como chave canônica |
| `Dias corridos` | contrato interno estável | manter como chave canônica |
| `Dias úteis` | contrato interno estável | manter como chave canônica |
| `Valor original` | contrato interno estável | manter como chave canônica |
| `Bruto` | contrato interno estável | manter como chave canônica |
| `Líquido` | contrato interno estável | manter como chave canônica |
| `Saldo rem` | contrato interno estável, mas nome abreviado | formalizar antes de parametrizar |

### Observação

`Último uso` só aparece em `lotes_exauridos`, não em `lotes_ativos`. Isso deve ser tratado como diferença estrutural intencional, não como inconsistência.

## Objeto 2 — `lotes_ativos`

### Chaves observadas

```text
Lote
Recebimento
Aplicação
Produto
Dias corridos
Dias úteis
Valor original
Bruto
Líquido
Saldo rem
```

### Origem funcional

Objeto construído a partir dos lotes após replay ainda considerados ativos na data de referência. Usa o mesmo domínio de cálculo de `lotes_exauridos`, mas sem a chave `Último uso`.

### Classificação

| Chave | Classificação | Decisão |
|---|---|---|
| `Lote` | contrato interno estável | manter como chave canônica |
| `Recebimento` | contrato interno estável | manter como chave canônica |
| `Aplicação` | contrato interno estável | manter como chave canônica |
| `Produto` | contrato interno estável | manter como chave canônica |
| `Dias corridos` | contrato interno estável | manter como chave canônica |
| `Dias úteis` | contrato interno estável | manter como chave canônica |
| `Valor original` | contrato interno estável | manter como chave canônica |
| `Bruto` | contrato interno estável | manter como chave canônica |
| `Líquido` | contrato interno estável | manter como chave canônica |
| `Saldo rem` | contrato interno estável, mas nome abreviado | formalizar antes de parametrizar |

### Observação

O bloco é estruturalmente semelhante a `lotes_exauridos`, mas não deve receber automaticamente `Último uso`, pois isso mudaria a estrutura observável já validada.

## Objeto 3 — `recebidos_atuais`

### Chaves observadas

```text
Recebido
Lote origem
Recebimento
Aplicação
Valor bruto
Valor líquido
Status
Destino
Pagamentos vinculados
Valor vinculado
Residual aplicação
Disponível ref
Observação
```

### Origem funcional

Objeto associado à materialização/auditoria dos recebidos atuais e disponibilidade operacional na data de referência. É o bloco mais sensível da aba `Situação Atual`, porque conecta recebidos, lote de origem, status, destino, pagamentos vinculados e valores residuais de aplicação.

### Classificação

| Chave | Classificação | Decisão |
|---|---|---|
| `Recebido` | contrato interno estável | manter como chave canônica |
| `Lote origem` | contrato interno estável | manter como chave canônica |
| `Recebimento` | contrato interno estável | manter como chave canônica |
| `Aplicação` | contrato interno estável | manter como chave canônica |
| `Valor bruto` | contrato interno estável | manter como chave canônica |
| `Valor líquido` | contrato interno estável | manter como chave canônica |
| `Status` | contrato interno estável | manter como chave canônica |
| `Destino` | contrato interno estável | manter como chave canônica |
| `Pagamentos vinculados` | contrato interno estável | manter como chave canônica |
| `Valor vinculado` | contrato interno estável | manter como chave canônica |
| `Residual aplicação` | contrato interno sensível | formalizar antes de parametrizar |
| `Disponível ref` | contrato interno sensível e abreviado | formalizar antes de parametrizar |
| `Observação` | contrato interno/apresentação | manter, mas formalizar antes de renomear |

### Observação

`Disponível ref` é uma abreviação de apresentação, mas também funciona como chave interna. Se houver parametrização futura, a chave interna deve continuar sendo `Disponível ref` ou ser migrada de forma explícita para uma chave técnica, por exemplo `disponivel_referencia`, com rótulo exibido separado.

## Objeto 4 — `fechamento_atual`

### Chaves observadas

```text
Métrica
Valor
```

### Origem funcional

Objeto associado ao resumo de fechamento da situação atual, com pares métrica/valor. A origem passa por `resumir_fechamento_situacao_atual`, que concentra a rotulagem do fechamento econômico.

### Classificação

| Chave | Classificação | Decisão |
|---|---|---|
| `Métrica` | contrato interno genérico | manter local |
| `Valor` | contrato interno genérico | manter local |

### Observação

Por serem pares genéricos e estáveis, não há ganho relevante em parametrizar esses cabeçalhos neste momento.

## Objeto 5 — `resumo_recebidos`

### Chaves observadas

```text
Métrica
Valor
```

### Origem funcional

Objeto de resumo agregado dos recebidos auditáveis, também representado como pares métrica/valor.

### Classificação

| Chave | Classificação | Decisão |
|---|---|---|
| `Métrica` | contrato interno genérico | manter local |
| `Valor` | contrato interno genérico | manter local |

### Observação

Compartilha a mesma estrutura de `fechamento_atual`. Parametrizar esses rótulos teria baixo retorno operacional.

## Chaves que devem ser tratadas como contrato interno estável

As seguintes chaves devem ser consideradas contrato interno da saída canônica enquanto a planilha operacional usar `_rows(...)` com listas de strings:

```text
Lote
Recebimento
Aplicação
Produto
Dias corridos
Dias úteis
Valor original
Bruto
Líquido
Saldo rem
Recebido
Lote origem
Valor bruto
Valor líquido
Status
Destino
Pagamentos vinculados
Valor vinculado
Métrica
Valor
```

## Chaves que são simultaneamente contrato e apresentação

Essas chaves têm maior risco em eventual parametrização porque são rótulos humanos, mas também funcionam como identificadores de extração:

```text
Último uso
Saldo rem
Residual aplicação
Disponível ref
Observação
```

Elas devem ser formalizadas antes de qualquer renomeação.

## Chaves que deveriam ser formalizadas antes de parametrização adicional

Recomenda-se formalizar explicitamente, em contrato de saída canônica, pelo menos:

```text
Último uso
Saldo rem
Residual aplicação
Disponível ref
Observação
```

Motivo: são abreviações ou rótulos de apresentação com significado operacional. A existência delas como chave interna pode dificultar renomeação segura no config.

## Recomendação de arquitetura futura

Antes de parametrizar cabeçalhos da aba `Situação Atual`, criar um contrato explícito de mapeamento entre chave interna e rótulo exibido:

```json
{
  "saidas": {
    "planilha_operacional": {
      "situacao_atual": {
        "lotes_exauridos": {
          "titulo": "Lotes exauridos",
          "colunas": [
            {"chave": "Lote", "cabecalho": "Lote"},
            {"chave": "Recebimento", "cabecalho": "Recebimento"},
            {"chave": "Saldo rem", "cabecalho": "Saldo rem"}
          ]
        }
      }
    }
  }
}
```

Essa abordagem preserva a extração por chave interna e permite trocar apenas o rótulo visível da planilha.

## Decisão da microetapa

Não parametrizar a aba `Situação Atual` ainda.

A parametrização só deve avançar após uma das duas alternativas:

1. formalizar contrato de saída canônica com chaves técnicas estáveis e rótulos separados; ou
2. criar um helper local na planilha operacional que aceite pares `chave`/`cabecalho`, mantendo os nomes atuais como default.

## Conclusão

A aba `Situação Atual` deve permanecer local nesta fase. Os objetos `lotes_exauridos`, `lotes_ativos`, `recebidos_atuais`, `fechamento_atual` e `resumo_recebidos` já funcionam como contrato interno da saída canônica, mas esse contrato ainda é implícito, baseado em chaves textuais humanas.

A próxima etapa segura é documentar esse contrato de chaves da saída canônica em um bloco específico no próprio relatório ou, se houver necessidade operacional, criar um contrato explícito futuro com pares `chave`/`cabecalho`. Nenhum código deve ser alterado antes dessa separação.

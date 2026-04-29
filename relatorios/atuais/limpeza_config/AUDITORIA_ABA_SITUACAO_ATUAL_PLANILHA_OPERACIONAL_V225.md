# Auditoria da aba `Situação Atual` — planilha operacional — V225

## Identificação

- Baseline operacional: V225
- Escopo: `scripts/operacional/gerar_planilha_operacional.py`
- Função auditada: `_adicionar_situacao_atual(wb, saida)`
- Tipo: auditoria documental/diagnóstica
- Classe: camada observável de saída XLSX
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

Classificar os elementos hardcoded da aba `Situação Atual` em três grupos:

1. títulos de seções;
2. cabeçalhos exibidos;
3. nomes internos usados em `_rows(...)` para extrair dados da saída canônica.

A finalidade é decidir se vale parametrizar essa aba agora ou se ela deve permanecer local por estar acoplada à saída canônica.

## Estrutura atual da aba

A função `_adicionar_situacao_atual(wb, saida)` cria a aba:

```text
Situação Atual
```

Em seguida, monta cinco blocos/seções sequenciais:

1. `Lotes exauridos`
2. `Lotes ativos`
3. `Recebidos auditáveis`
4. `Fechamento econômico`
5. `Resumo de recebidos`

Cada bloco chama `_apply_table_style(...)` com `title=...` e com uma lista de cabeçalhos. A mesma lista de cabeçalhos é usada em `_rows(...)` como lista de chaves para extrair valores dos objetos presentes em `saida`.

## Classificação por seção

### 1. `Lotes exauridos`

Título da seção:

```text
Lotes exauridos
```

Cabeçalhos exibidos:

```text
Lote, Recebimento, Aplicação, Último uso, Produto, Dias corridos, Dias úteis, Valor original, Bruto, Líquido, Saldo rem
```

Chaves internas usadas em `_rows(...)`:

```text
Lote, Recebimento, Aplicação, Último uso, Produto, Dias corridos, Dias úteis, Valor original, Bruto, Líquido, Saldo rem
```

Objeto de origem:

```text
saida.lotes_exauridos
```

Classificação:

- título: candidato futuro a config;
- cabeçalhos exibidos: candidato futuro a config;
- chaves internas: manter local por enquanto.

Observação: a lista de cabeçalhos exibidos é idêntica à lista de chaves internas. Parametrizar sem separar essas duas camadas pode quebrar a extração se o usuário renomear cabeçalhos no config.

### 2. `Lotes ativos`

Título da seção:

```text
Lotes ativos
```

Cabeçalhos exibidos:

```text
Lote, Recebimento, Aplicação, Produto, Dias corridos, Dias úteis, Valor original, Bruto, Líquido, Saldo rem
```

Chaves internas usadas em `_rows(...)`:

```text
Lote, Recebimento, Aplicação, Produto, Dias corridos, Dias úteis, Valor original, Bruto, Líquido, Saldo rem
```

Objeto de origem:

```text
saida.lotes_ativos
```

Classificação:

- título: candidato futuro a config;
- cabeçalhos exibidos: candidato futuro a config;
- chaves internas: manter local por enquanto.

Observação: o bloco é semelhante ao de lotes exauridos, mas não inclui `Último uso`. Isso deve ser preservado como contrato de apresentação específico.

### 3. `Recebidos auditáveis`

Título da seção:

```text
Recebidos auditáveis
```

Cabeçalhos exibidos:

```text
Recebido, Lote origem, Recebimento, Aplicação, Valor bruto, Valor líquido, Status, Destino, Pagamentos vinculados, Valor vinculado, Residual aplicação, Disponível ref, Observação
```

Chaves internas usadas em `_rows(...)`:

```text
Recebido, Lote origem, Recebimento, Aplicação, Valor bruto, Valor líquido, Status, Destino, Pagamentos vinculados, Valor vinculado, Residual aplicação, Disponível ref, Observação
```

Objeto de origem:

```text
saida.recebidos_atuais
```

Classificação:

- título: candidato futuro a config;
- cabeçalhos exibidos: candidato futuro a config;
- chaves internas: manter local por enquanto.

Observação: esse bloco contém chaves semanticamente ligadas à auditoria de recebidos e à disponibilidade de aplicação. É mais sensível do que os blocos de lotes, porque qualquer renomeação pode ocultar informações importantes se usada também como chave interna.

### 4. `Fechamento econômico`

Título da seção:

```text
Fechamento econômico
```

Cabeçalhos exibidos:

```text
Métrica, Valor
```

Chaves internas usadas em `_rows(...)`:

```text
Métrica, Valor
```

Objeto de origem:

```text
saida.fechamento_atual
```

Classificação:

- título: candidato futuro a config;
- cabeçalhos exibidos: baixa prioridade para config;
- chaves internas: manter local.

Observação: como `Métrica` e `Valor` são pares genéricos, parametrizar esse bloco teria pouco ganho prático.

### 5. `Resumo de recebidos`

Título da seção:

```text
Resumo de recebidos
```

Cabeçalhos exibidos:

```text
Métrica, Valor
```

Chaves internas usadas em `_rows(...)`:

```text
Métrica, Valor
```

Objeto de origem:

```text
saida.resumo_recebidos
```

Classificação:

- título: candidato futuro a config;
- cabeçalhos exibidos: baixa prioridade para config;
- chaves internas: manter local.

Observação: compartilha a mesma estrutura genérica de `Fechamento econômico`.

## Diagnóstico técnico

A aba `Situação Atual` está mais acoplada à saída canônica do que as três abas principais já parametrizadas (`Extrato Passado`, `Extrato Futuro`, `Switching`).

Motivo: nas três abas principais, a parametrização de cabeçalhos foi segura porque os valores adicionados ao config são idênticos aos valores usados como chaves de extração. Para a aba `Situação Atual`, o mesmo padrão funcionaria apenas enquanto os nomes configurados fossem idênticos. Qualquer alteração posterior no config quebraria ou esvaziaria colunas, porque `_rows(...)` usa os cabeçalhos como chaves internas.

Portanto, parametrizar essa aba corretamente exigiria uma camada explícita com dois campos separados:

```json
{
  "titulo": "Lotes exauridos",
  "colunas": [
    {"chave": "Lote", "cabecalho": "Lote"},
    {"chave": "Recebimento", "cabecalho": "Recebimento"}
  ]
}
```

Essa mudança seria estruturalmente maior do que a parametrização anterior e exigiria alteração do helper `_rows(...)` ou criação de um helper específico para pares `chave`/`cabecalho`.

## Decisão recomendada

Não parametrizar a aba `Situação Atual` agora.

Motivos:

1. a aba está fortemente acoplada aos objetos de `saida`;
2. os cabeçalhos também funcionam como chaves internas de extração;
3. parametrizar apenas os textos visíveis sem separar chaves internas e rótulos exibidos criaria risco de planilha com colunas vazias;
4. parametrizar corretamente exigiria uma mudança estrutural maior do que o escopo atual de limpeza observável;
5. os títulos de seção são estáveis e de baixa pressão operacional.

## Classificação final

| Grupo | Classificação | Decisão |
|---|---|---|
| Nome da aba `Situação Atual` | contrato observável | já parametrizado via wrapper/config |
| Títulos das seções | apresentação observável | candidato futuro, baixa prioridade |
| Cabeçalhos exibidos de lotes | apresentação + chave interna | manter local por enquanto |
| Cabeçalhos exibidos de recebidos | apresentação + chave interna sensível | manter local por enquanto |
| `Métrica` / `Valor` | genérico | manter local |
| Chaves internas usadas em `_rows(...)` | contrato com saída canônica | manter local até haver contrato formal da saída canônica |
| Espaçamento `r + 3` | layout local | manter local |
| Estilo aplicado via `_apply_table_style` | apresentação de baixo nível | manter local |

## Próxima microetapa recomendada

Antes de parametrizar a aba `Situação Atual`, auditar a origem desses objetos na saída canônica:

- `saida.lotes_exauridos`
- `saida.lotes_ativos`
- `saida.recebidos_atuais`
- `saida.fechamento_atual`
- `saida.resumo_recebidos`

Objetivo: verificar se existe ou se deve existir um contrato formal de chaves da saída canônica. Só depois disso faria sentido criar uma configuração com pares `chave`/`cabecalho` para a aba `Situação Atual`.

## Conclusão

A aba `Situação Atual` deve permanecer local nesta fase. A única parte já adequadamente parametrizada é o nome da aba. Títulos e cabeçalhos podem ser parametrizados no futuro, mas apenas com separação explícita entre chave interna e rótulo exibido.

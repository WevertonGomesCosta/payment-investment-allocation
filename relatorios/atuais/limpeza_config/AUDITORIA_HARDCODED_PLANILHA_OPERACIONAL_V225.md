# Auditoria de hardcoded observável — planilha operacional — V225

## Identificação

- Baseline operacional: V225
- Escopo: `scripts/operacional/gerar_planilha_operacional.py`
- Tipo: auditoria documental/diagnóstica
- Classe: camada observável de saída XLSX
- Restrições:
  - não alterar cálculo;
  - não alterar replay;
  - não alterar pagamentos;
  - não alterar switching;
  - não alterar ranking;
  - não alterar identidade da baseline;
  - não alterar `dados/config_atualizado.json` nesta microetapa.

## Objetivo

Classificar parâmetros hardcoded restantes na camada observável da planilha operacional, especialmente:

- nomes de abas;
- cabeçalhos;
- nomes internos de colunas usados para extrair dados da saída canônica;
- estilos visuais;
- formatos numéricos;
- limites/layouts locais de exibição.

A auditoria não promove nenhuma mudança funcional. O objetivo é separar o que deve permanecer local por ser detalhe de apresentação daquilo que pode virar contrato explícito em `dados/config_atualizado.json` em etapa futura.

## Arquivos inspecionados

- `scripts/operacional/gerar_planilha_operacional.py`
- `scripts/operacional/gerar_planilha_operacional_configurada.py`
- `dados/config_atualizado.json` como referência de contrato já centralizado

## Resumo executivo

A planilha operacional já possui um wrapper configurável para nomes de arquivo e nomes de abas. Mesmo assim, o gerador base ainda contém hardcoded de apresentação. Isso é esperado porque o gerador base constrói a estrutura XLSX e o wrapper apenas renomeia/copía a saída conforme o config.

A auditoria recomenda **não migrar tudo para config**. Parte dos hardcodeds deve permanecer local porque representa apresentação de baixo nível do Excel, acoplada ao `openpyxl` e à estrutura da saída canônica. Migrar esses detalhes agora aumentaria complexidade sem ganho operacional.

A próxima parametrização segura deve focar apenas em contratos de alto nível da camada observável: cabeçalhos de abas principais e, eventualmente, listas de colunas por aba. Estilos, formatos e largura automática devem permanecer locais por enquanto.

## Inventário classificado

### 1. Caminhos e nomes de arquivo

| Item | Local | Classificação | Decisão |
|---|---|---|---|
| `SAIDA_INTERNA = caminho_saida_operacional(RAIZ, nome_relatorio_operacional())` | gerador base | hardcoded operacional derivado da identidade | manter local |
| `SAIDA_EXTERNA = caminho_artifact(nome_relatorio_operacional())` | gerador base | hardcoded operacional derivado da identidade | manter local |
| `arquivo` em `saidas.planilha_operacional` | wrapper configurável | já parametrizado | manter no config |

Justificativa: o wrapper já resolve o nome final do arquivo com `saidas.planilha_operacional.arquivo`; o gerador base pode continuar produzindo a saída padrão intermediária.

### 2. Nomes de abas

| Item | Local | Classificação | Decisão |
|---|---|---|---|
| `Extrato Passado` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Extrato Futuro` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Switching` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Carteira` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Top30` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Resumo Switching` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Validacao` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Situação Atual` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |
| `Saida Canonica` | gerador base e wrapper | contrato observável | já parametrizado no config via wrapper |

Decisão: não há necessidade de alterar o gerador base agora. O wrapper já fornece camada de configuração sem reabrir a lógica de geração.

Risco se migrar diretamente no gerador base: alterar a criação inicial das abas pode introduzir divergência com o wrapper e com validações esperadas por nomes atuais.

### 3. Cabeçalhos das abas principais

#### 3.1 `Extrato Passado`

Cabeçalhos atuais:

```text
Data, Conta, Despesa ID, Lote, Saldo Antes, Bruto, Imposto, Líquido, Saldo Remanescente
```

Classificação:

- contrato observável de tabela;
- candidato futuro a `saidas.planilha_operacional.cabecalhos.extrato_passado`;
- não migrar nesta etapa.

#### 3.2 `Extrato Futuro`

Cabeçalhos atuais:

```text
Data, Conta, Despesa ID, Valor, Lote sugerido, Saldo Antes, Bruto, Imposto, Líquido, Saldo Remanescente, Cobertura integral, Estratégia, Lote reserva, Necessita switching
```

Classificação:

- contrato observável de tabela;
- candidato futuro a `saidas.planilha_operacional.cabecalhos.extrato_futuro`;
- não migrar nesta etapa.

#### 3.3 `Switching`

Cabeçalhos atuais:

```text
Data sugerida, Lote origem, Produto origem, Produto destino switching, Ganho estimado, Valor líquido origem, Status
```

Classificação:

- contrato observável de tabela;
- candidato futuro a `saidas.planilha_operacional.cabecalhos.switching`;
- não migrar nesta etapa.

### 4. Cabeçalhos e colunas do ranking na planilha

O gerador usa dois níveis de nomes:

1. nomes internos esperados no `DataFrame` de ranking, como:
   - `rank_destino`
   - `nome`
   - `score_final`
   - `proxy_terminal_destino`
   - `retorno_anual_proxy`
   - `liquidez_dias`
   - `carencia_dias`
   - `aplicacao_minima`
   - `aplicacao_maxima`
   - `tipo_produto`
   - `somente_combo`
   - `Status_Confirmação`
   - `Campos_Pendentes`

2. cabeçalhos exibidos na planilha, como:
   - `Rank`
   - `Produto`
   - `Score Final`
   - `Proxy Terminal`
   - `Retorno Proxy aa`
   - `Liquidez Dias`
   - `Carência Dias`
   - `Aplicação Mínima`
   - `Aplicação Máxima`
   - `Tipo Produto`
   - `Somente Combo`
   - `Status Confirmação`
   - `Campos Pendentes`

Classificação:

| Tipo | Decisão |
|---|---|
| nomes internos do `DataFrame` | manter local por enquanto, pois fazem parte do contrato entre ranking e saída canônica |
| cabeçalhos exibidos | candidatos futuros a config |

Recomendação: se houver migração futura, separar claramente:

```json
"colunas_internas": [...]
"cabecalhos_exibidos": [...]
```

sem misturar nomes internos com nomes de exibição.

### 5. Seções da aba `Situação Atual`

Títulos/seções atuais:

- `Lotes exauridos`
- `Lotes ativos`
- `Recebidos auditáveis`
- `Fechamento econômico`
- `Resumo de recebidos`

Cabeçalhos principais incluem:

- `Lote`
- `Recebimento`
- `Aplicação`
- `Último uso`
- `Produto`
- `Dias corridos`
- `Dias úteis`
- `Valor original`
- `Bruto`
- `Líquido`
- `Saldo rem`
- `Recebido`
- `Lote origem`
- `Valor bruto`
- `Valor líquido`
- `Status`
- `Destino`
- `Pagamentos vinculados`
- `Valor vinculado`
- `Residual aplicação`
- `Disponível ref`
- `Observação`
- `Métrica`
- `Valor`

Classificação:

- títulos de seção: candidatos futuros a config, mas baixa prioridade;
- cabeçalhos exibidos: candidatos futuros a config;
- nomes usados em `_rows(...)`: manter sincronizados com a saída canônica; migrar somente se a saída canônica também expuser um contrato estável.

Decisão: manter local por enquanto.

### 6. Estilos visuais

Itens hardcoded:

- `showGridLines = False`
- cor do cabeçalho: `D9EAF7`
- cor do título: `EDF4FA`
- cor da fonte: `1F1F1F`
- borda: `D9E1F2`
- negrito no cabeçalho;
- tamanho 12 nos títulos;
- alinhamento horizontal/vertical;
- wrap text nos cabeçalhos;
- auto filter;
- freeze panes;
- largura mínima/máxima de coluna: `10` e `38`.

Classificação: apresentação local de baixo nível.

Decisão: manter hardcoded por enquanto.

Justificativa: esses valores são detalhes de renderização do Excel, não contrato econômico nem analítico. Parametrizar agora aumentaria a superfície do config sem necessidade operacional.

### 7. Formatos numéricos

Itens hardcoded:

- formato monetário: `R$ #,##0.00;[Red](R$ #,##0.00);-`
- formato inteiro: `0`
- formato de data: `dd/mm/yyyy`
- detecção de data por presença de `Data` no cabeçalho.

Classificação: apresentação local com impacto visual.

Decisão: manter local por enquanto.

Candidato futuro: apenas se houver demanda por internacionalização, moeda alternativa ou mudança global de formato.

### 8. Grupos de colunas monetárias e inteiras

`currency_cols` inclui:

```text
Valor, Saldo Antes, Bruto, Imposto, Líquido, Saldo Remanescente, Ganho estimado, Valor líquido origem, Score, Proxy terminal, Ticket mín., Valor original, Saldo rem, Valor bruto, Valor líquido, Valor vinculado, Residual aplicação
```

`int_cols` inclui:

```text
Dias corridos, Dias úteis, Rank, Liquidez, Carência, Pagamentos vinculados
```

Classificação:

- candidatos moderados a config se houver evolução de layout;
- manter local por enquanto.

Justificativa: dependem dos cabeçalhos exibidos. Migrar antes dos cabeçalhos geraria duplicidade e risco de inconsistência.

### 9. Limites de exibição

Não foram encontrados limites explícitos de número de linhas por aba dentro do gerador da planilha operacional. A planilha recebe os quadros completos vindos da saída canônica ou do ranking.

Limites observáveis existentes:

- largura mínima/máxima de colunas: `10` e `38`;
- espaçamento entre blocos da aba `Situação Atual`: `r + 3`;
- freeze panes ativado em algumas abas.

Classificação: layout local.

Decisão: manter local.

### 10. Cópia externa para `/mnt/data`

O gerador tenta salvar uma cópia externa se o caminho existir:

```text
SAIDA_EXTERNA
```

Classificação: compatibilidade com ambiente de artefatos.

Decisão: manter local.

Justificativa: é uma adaptação operacional ao ambiente de execução e não deve entrar no config financeiro.

## Candidatos futuros a `dados/config_atualizado.json`

Se houver uma próxima etapa de parametrização observável, recomenda-se adicionar apenas contratos de alto nível:

```json
{
  "saidas": {
    "planilha_operacional": {
      "arquivo": "relatorio_operacional_{versao_slug}.xlsx",
      "abas": {
        "extrato_passado": "Extrato Passado",
        "extrato_futuro": "Extrato Futuro",
        "switching": "Switching",
        "carteira": "Carteira",
        "top30": "Top30",
        "resumo_switching": "Resumo Switching",
        "validacao": "Validacao",
        "situacao_atual": "Situação Atual",
        "saida_canonica": "Saida Canonica"
      },
      "cabecalhos": {
        "extrato_passado": [
          "Data", "Conta", "Despesa ID", "Lote", "Saldo Antes", "Bruto", "Imposto", "Líquido", "Saldo Remanescente"
        ],
        "extrato_futuro": [
          "Data", "Conta", "Despesa ID", "Valor", "Lote sugerido", "Saldo Antes", "Bruto", "Imposto", "Líquido", "Saldo Remanescente", "Cobertura integral", "Estratégia", "Lote reserva", "Necessita switching"
        ],
        "switching": [
          "Data sugerida", "Lote origem", "Produto origem", "Produto destino switching", "Ganho estimado", "Valor líquido origem", "Status"
        ]
      }
    }
  }
}
```

Não se recomenda migrar agora:

- cores;
- fontes;
- bordas;
- alinhamentos;
- largura de colunas;
- formatos monetários;
- espaçamentos locais;
- nomes internos de colunas enquanto não houver contrato estável da saída canônica.

## Decisão da microetapa

A microetapa é apenas diagnóstica. Nenhum código foi alterado.

Classificação final:

| Grupo | Decisão |
|---|---|
| nomes de abas | já parametrizados via wrapper/config |
| arquivo de saída | já parametrizado via wrapper/config |
| cabeçalhos das abas principais | candidato futuro a config |
| cabeçalhos da aba Situação Atual | candidato futuro, baixa prioridade |
| nomes internos de colunas | manter local até contrato estável da saída canônica |
| estilos visuais | manter hardcoded |
| formatos numéricos | manter hardcoded |
| largura/auto filter/freeze panes | manter hardcoded |
| cópia para artefato externo | manter local |

## Próxima microetapa recomendada

A próxima etapa segura é adicionar ao `dados/config_atualizado.json` apenas os cabeçalhos das três abas principais (`Extrato Passado`, `Extrato Futuro`, `Switching`) com valores idênticos aos atuais, e adaptar o gerador para usá-los com fallback local. Não incluir estilos, formatos ou colunas internas ainda.

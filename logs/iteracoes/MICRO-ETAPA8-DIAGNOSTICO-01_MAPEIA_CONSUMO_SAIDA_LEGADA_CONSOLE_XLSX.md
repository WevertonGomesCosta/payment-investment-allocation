# MICRO-ETAPA8-DIAGNOSTICO-01 — Mapeia consumo atual de saída legada por console/XLSX contra SaidaCanonicaOficial

## Identificação

- **Microfrente:** MICRO-ETAPA8-DIAGNOSTICO-01
- **Tipo:** documental / diagnóstico
- **Baseline de entrada:** `ca1dff07c8c2d5929da2bf24998764ceb04b0de4`
- **Branch:** `docs/micro-etapa8-diagnostico-01`
- **Escopo:** mapear consumo atual da saída legada por console/XLSX contra `SaidaCanonicaOficial`

## Objetivo

Diagnosticar se `SaidaCanonicaOficial` já pode substituir diretamente a saída legada consumida por console e XLSX, ou se é necessária camada adaptadora/intermediária.

Esta microfrente não altera runtime, console, XLSX, motor, ledger, gates ou saídas.

## Arquivos inspecionados

```text
aplicacao/principal.py
aplicacao/console/principal.py
nucleo/gerar_planilha_operacional.py
nucleo/saida_canonica_oficial.py
```

## Resultado sintético

```text
STATUS: DIAGNOSTICO_CONCLUIDO_COM_SUBSTITUICAO_DIRETA_NAO_RECOMENDADA
```

A substituição direta de `saida_canonica` legada por `SaidaCanonicaOficial` em console/XLSX ainda não é recomendada.

A `SaidaCanonicaOficial` já existe como artefato formal pós-gates, mas sua estrutura é de snapshot canônico de ledger/gates. Console e XLSX ainda dependem de campos, métodos e convenções específicas da saída legada operacional.

## Fluxo atual em `aplicacao/principal.py`

O runtime executa:

```text
Etapas 1–7
bloqueio por pronto_para_etapa8=False
construir_saida_canonica_oficial(...)
construir_saida_canonica_com_switching_v17_c7(...)
construir_matriz_elegibilidade_fontes_s7b(...)
aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(...)
render_console(...)
gerar_planilha_operacional(...)
```

Logo, `SaidaCanonicaOficial` já é construída internamente após gates aprovados, mas console/XLSX ainda consomem `saida_canonica` legada.

## Consumidores atuais da saída legada — console

`aplicacao/console/principal.py` consome `saida_canonica` em múltiplas seções:

| Consumidor | Dependências observadas |
|---|---|
| `_render_amostras_pagamentos_operacionais(...)` | `construir_amostras_pagamentos_operacionais(saida_canonica, ...)` |
| `_render_secao_ranking_oficial(...)` | `saida_canonica.versao`, `saida_canonica.ranking_amostra` |
| `_render_secao_switchings_oficiais(...)` | `construir_switchings_observaveis(...)`, `saida_canonica.lotes_sinteticos_pos_switching_console(...)`, `saida_canonica.recebidos_atuais`, `saida_canonica.recebidos_futuros_console(...)` |
| `_render_situacao_atual_operacional(...)` | lotes consolidados, blocos de situação atual, patrimônio total, recebidos |
| `render_console(...)` | `saida_canonica.fechamento_atual`, `saida_canonica.resumo_recebidos`, `extrato_passado`, métodos auxiliares e pacote observável temporal |

## Consumidores atuais da saída legada — XLSX

`nucleo/gerar_planilha_operacional.py` consome `saida` legada para:

| Aba / função | Dependências observadas |
|---|---|
| `Extrato Passado` | `saida.extrato_passado` |
| `Extrato Futuro` | `saida.extrato_futuro` |
| `Switching` | `construir_switchings_observaveis(contexto, saida, ...)` |
| `Situação Atual` | `construir_blocos_situacao_atual(contexto, saida, ...)` |
| `Saida Canonica` | `saida.auditoria`, `saida.switchings` |
| `Auditoria Fontes` | `pacote_saida.extrato_futuro` |
| `Auditoria FIFO` | `pacote_saida.extrato_futuro`, `pacote_saida.auditoria['fifo_candidatos_avaliados']` |
| Abas diagnósticas opcionais | métodos `lotes_sinteticos_pos_switching_console(...)` e `estado_pos_switching_lotes_console(...)` |

Além disso, a geração XLSX ainda integra CSVs diagnósticos históricos em abas como `Pagamentos Operacionais`, `Fontes Pagamento`, `Multifonte Resgates` e `Pendencias Pagamentos`.

## Componentes disponíveis em `SaidaCanonicaOficial`

`SaidaCanonicaOficial` contém:

```text
ok
preparada
status
data_referencia
origem_formal
ledger_origem
gates_origem
resumo
eventos
obrigacoes_cobertas
obrigacoes_bloqueadas
fontes_utilizadas
fontes_reservadas
switchings_escolhidos
saldos_referenciais_por_data
bloqueios_ledger
avisos_ledger
bloqueios_gates
avisos_gates
evidencias_gates
bloqueios_preparacao
metadados
```

Esses componentes são adequados como base canônica pós-gates, mas não expõem diretamente os campos legados exigidos por console/XLSX.

## Lacunas para substituição direta

| Requisito legado | Existe diretamente em `SaidaCanonicaOficial`? | Diagnóstico |
|---|---:|---|
| `extrato_passado` | Não | Exige adaptador a partir de eventos/obrigações/fontes ou manutenção temporária da saída legada. |
| `extrato_futuro` | Não | Exige schema de apresentação derivado do ledger. |
| `fechamento_atual` | Não | Exige bloco de resumo canônico próprio. |
| `resumo_recebidos` | Não | Exige decisão se recebidos entram no artefato formal ou em camada posterior. |
| `ranking_amostra` | Não | Está fora do snapshot de ledger/gates; requer mapeamento de origem formal. |
| `switchings` | Parcial | Há `switchings_escolhidos`, mas com schema de ledger, não schema observável legado. |
| `auditoria` | Parcial | Há bloqueios/evidências/metadados, mas não no formato esperado pela aba `Saida Canonica`. |
| métodos console pós-switching | Não | Exige adaptador ou reimplementação posterior. |

## Decisão diagnóstica

A substituição direta de `saida_canonica` por `SaidaCanonicaOficial` em `render_console(...)` ou `gerar_planilha_operacional(...)` causaria quebra de contrato de consumo, porque as camadas observáveis esperam atributos e métodos não presentes no artefato formal da Etapa 8.

A próxima microfrente funcional não deve trocar o argumento `saida_canonica` por `saida_canonica_oficial` diretamente.

## Caminho técnico recomendado

Criar uma camada adaptadora explícita, em microfrente futura, que converta `SaidaCanonicaOficial` para um pacote observável compatível com consumo posterior.

Nome sugerido:

```text
PacoteRenderizacaoSaidaCanonica
```

Função sugerida:

```python
construir_pacote_renderizacao_saida_canonica(
    saida_oficial: SaidaCanonicaOficial,
) -> PacoteRenderizacaoSaidaCanonica
```

Essa camada deve ser posterior à Etapa 8 e anterior a console/XLSX, sem reotimizar e sem revalorar.

## Restrições para a próxima etapa

A próxima etapa não deve:

- substituir console/XLSX diretamente;
- alterar motor temporal;
- alterar ledger;
- alterar gates;
- consultar dados brutos;
- reconstruir saída legada a partir de contexto operacional;
- criar nova decisão econômica;
- alterar switchings, saldos ou obrigações.

## Conclusão

`SaidaCanonicaOficial` está consolidada como artefato formal pós-gates, mas console/XLSX ainda dependem da saída legada operacional.

A transição correta é por adaptador/ponte de renderização, não por substituição direta.

## Próxima microfrente recomendada

```text
MICRO-ETAPA8-CONTRATO-ADAPTADOR-01 — Formaliza contrato da camada adaptadora entre SaidaCanonicaOficial e renderização/exportação
```

Escopo recomendado:

- criar contrato documental curto para o adaptador;
- definir entrada: `SaidaCanonicaOficial`;
- definir saída prevista: `PacoteRenderizacaoSaidaCanonica`;
- mapear campos mínimos para console/XLSX;
- proibir reotimização, revaloração e consulta a dados brutos;
- não implementar código ainda.

# MICRO-ETAPA8-FUNCIONAL-02 — Integra SaidaCanonicaOficial ao runtime sem substituir console/XLSX

## 1. Identificação

- **Microfrente:** MICRO-ETAPA8-FUNCIONAL-02
- **Tipo:** funcional controlada
- **Classe:** integração mínima runtime pós-gates
- **Baseline de entrada:** `69b01eb82aa31e9a83bbae675688d974bd8772d6`
- **Branch:** `feat/micro-etapa8-funcional-02`
- **PRs prévias incorporadas:**
  - PR #439 — contrato documental da Etapa 8
  - PR #440 — auditoria documental da Etapa 8
  - PR #441 — artefato formal mínimo da Etapa 8
  - PR #442 — auditoria do módulo formal da Etapa 8

## 2. Objetivo

Integrar `SaidaCanonicaOficial` ao runtime de forma mínima, interna e auditável, sem substituir console/XLSX e sem alterar a lógica econômica existente.

A integração deve ocorrer somente depois da aprovação dos gates da Etapa 7.

## 3. Escopo alterado

Arquivos alterados nesta microfrente:

```text
aplicacao/principal.py
logs/iteracoes/MICRO-ETAPA8-FUNCIONAL-02_INTEGRA_SAIDA_CANONICA_OFICIAL_RUNTIME.md
```

## 4. Alterações implementadas

Em `aplicacao/principal.py`, foi adicionada a importação:

```python
from nucleo.saida_canonica_oficial import construir_saida_canonica_oficial
```

A função `carregar_contexto_e_saida()` passou a:

1. executar Etapas 1–7 como antes;
2. bloquear imediatamente quando `resultado_gates_validacao_nucleo.pronto_para_etapa8=False`;
3. retornar `saida_canonica_oficial=None` quando os gates bloqueiam;
4. chamar `construir_saida_canonica_oficial(...)` somente após gates aprovados;
5. preservar a construção legada de `saida_canonica` para console/XLSX;
6. retornar também o artefato formal `saida_canonica_oficial` para auditoria interna.

## 5. Bloqueio preservado

O bloco de bloqueio permanece anterior a qualquer preparação de saída posterior:

```python
if not resultado_gates_validacao_nucleo.pronto_para_etapa8:
    return (..., None, None)
```

Logo, quando `pronto_para_etapa8=False`:

- `construir_saida_canonica_oficial(...)` não é chamada;
- funções legadas de saída não são chamadas;
- console não é renderizado;
- XLSX não é gerado.

## 6. Console/XLSX preservados

Esta microfrente não substitui:

```python
render_console(...)
gerar_planilha_operacional(...)
```

Também não altera:

```python
construir_saida_canonica_com_switching_v17_c7(...)
construir_matriz_elegibilidade_fontes_s7b(...)
aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(...)
```

Essas funções permanecem como fluxo legado operacional para console/XLSX, a ser tratado em microfrente posterior.

## 7. Ausência de nova saída observável

A microfrente não cria:

- novo arquivo de saída;
- novo XLSX;
- novo console;
- nova pasta em `saidas/*`;
- novo script diagnóstico;
- nova regra econômica.

`SaidaCanonicaOficial` fica apenas como artefato interno/auditável retornado pela função `carregar_contexto_e_saida()`.

## 8. Ausência de alteração econômica

Esta microfrente não altera:

- motor temporal;
- ledger;
- gates;
- ranking;
- score;
- seleção de fonte;
- seleção de pacote;
- switching;
- saldo;
- obrigação coberta ou bloqueada.

## 9. Contrato de retorno atualizado

A função `carregar_contexto_e_saida()` passa a retornar sete itens:

```text
contexto_operacional_canonico
estado_temporal_inicial
resultado_motor_temporal_conjunto
ledger_temporal_canonico
resultado_gates_validacao_nucleo
saida_canonica
saida_canonica_oficial
```

`main()` desempacota o novo item e o preserva como variável interna não renderizada.

## 10. Validações esperadas

```bash
git diff --name-only origin/main...HEAD
```

Deve listar somente:

```text
aplicacao/principal.py
logs/iteracoes/MICRO-ETAPA8-FUNCIONAL-02_INTEGRA_SAIDA_CANONICA_OFICIAL_RUNTIME.md
```

```bash
git diff --stat origin/main...HEAD
```

Deve indicar alteração mínima em `aplicacao/principal.py` e criação deste log.

```bash
git status --short
```

Deve estar limpo após commit.

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
```

Deve passar.

```bash
python -B aplicacao/principal.py
```

No estado atual dos gates, deve preservar a mensagem:

```text
Execução bloqueada pelos gates de validação de núcleo: ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False. Console e XLSX oficiais não foram gerados.
```

## 11. Critérios de aceite

A PR deve ser aceita somente se:

1. alterar apenas `aplicacao/principal.py` e este log;
2. importar `construir_saida_canonica_oficial(...)`;
3. chamar `construir_saida_canonica_oficial(...)` somente após gates aprovados;
4. preservar bloqueio quando `pronto_para_etapa8=False`;
5. não substituir console/XLSX;
6. não alterar funções legadas de saída;
7. não gerar nova saída observável;
8. não alterar motor, ledger ou gates;
9. não alterar contratos;
10. preservar `saida_canonica_oficial` como artefato interno/auditável.

## 12. Próxima microfrente recomendada

Após aprovação e merge desta PR, recomenda-se:

```text
MICRO-ETAPA8-AUDITORIA-03 — Audita integração runtime da SaidaCanonicaOficial
```

Escopo recomendado:

- auditar `aplicacao/principal.py` contra contrato e módulo formal da Etapa 8;
- confirmar que a chamada à Etapa 8 só ocorre após gates aprovados;
- confirmar que, com `pronto_para_etapa8=False`, nenhuma saída posterior é preparada;
- confirmar que console/XLSX continuam no fluxo legado e não foram substituídos;
- decidir próxima microfrente: expor artefato formal para auditoria observável ou corrigir P3 de timezone.

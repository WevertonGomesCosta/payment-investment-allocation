# MACRO-ETAPA8-SAIDA-04 — Corrige P3 do adaptador e prepara integração interna pós-SaidaCanonicaOficial sem console/XLSX

## 1. Identificação

- **Macrofrente:** MACRO-ETAPA8-SAIDA-04
- **Tipo:** funcional controlada
- **Baseline de entrada:** `b13dfe1d5598de50d2f948d9001f332d1f408328`
- **Branch:** `feat/macro-etapa8-saida-04`

## 2. Objetivo

Corrigir a ressalva P3 registrada na auditoria do adaptador e integrar o `PacoteRenderizacaoSaidaCanonica` apenas como artefato interno em memória, após `SaidaCanonicaOficial`, sem alterar console/XLSX e sem gerar saída observável.

## 3. Arquivos alterados

```text
nucleo/adaptador_renderizacao_saida_canonica.py
aplicacao/principal.py
logs/iteracoes/MACRO-ETAPA8-SAIDA-04_CORRIGE_P3_E_INTEGRA_PACOTE_RENDERIZAVEL_INTERNO.md
```

## 4. Correção P3

Em `nucleo/adaptador_renderizacao_saida_canonica.py`, foi removida a variável local acentuada e desnecessária em `_auditoria`.

Antes:

```python
_linha('origem_formal', saída_origem := saida.origem_formal)
_ = saída_origem
```

Depois:

```python
_linha('origem_formal', saida.origem_formal)
```

## 5. Integração interna

Em `aplicacao/principal.py`, foi adicionada a importação:

```python
from nucleo.adaptador_renderizacao_saida_canonica import construir_pacote_renderizacao_saida_canonica
```

Após `saida_canonica_oficial`, o runtime passa a construir internamente:

```python
pacote_renderizacao_saida_canonica = construir_pacote_renderizacao_saida_canonica(saida_canonica_oficial)
```

## 6. Bloqueio preservado

Quando `ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False`, o retorno ocorre antes de:

- `construir_saida_canonica_oficial(...)`;
- `construir_pacote_renderizacao_saida_canonica(...)`;
- funções legadas de saída;
- console;
- XLSX.

O retorno bloqueado passa a incluir `None` também para `pacote_renderizacao_saida_canonica`.

## 7. Console/XLSX preservados

A macrofrente não altera:

```python
render_console(...)
gerar_planilha_operacional(...)
```

Console e XLSX continuam consumindo `saida_canonica` legada, exatamente como antes.

## 8. Contrato de retorno atualizado

`carregar_contexto_e_saida()` passa a retornar oito itens:

```text
contexto_operacional_canonico
estado_temporal_inicial
resultado_motor_temporal_conjunto
ledger_temporal_canonico
resultado_gates_validacao_nucleo
saida_canonica
saida_canonica_oficial
pacote_renderizacao_saida_canonica
```

`main()` desempacota o novo item e o preserva como artefato interno não renderizado.

## 9. Restrições preservadas

Esta macrofrente não altera:

- console;
- XLSX;
- geração de planilha;
- motor temporal;
- ledger;
- gates;
- contratos;
- dados;
- saídas operacionais;
- ranking;
- score;
- regras econômicas.

Também não executa:

- reotimização;
- revaloração;
- nova escolha de fonte;
- alteração de obrigação;
- alteração de switching;
- alteração de saldo;
- geração de saída nova.

## 10. Validação esperada

```bash
git diff --name-only origin/main...HEAD
git diff --stat origin/main...HEAD
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

O runtime deve preservar a mensagem atual de bloqueio quando `pronto_para_etapa8=False`.

## 11. Próxima frente recomendada

```text
MACRO-ETAPA8-SAIDA-05 — Audita integração interna do pacote renderizável
```

Escopo recomendado:

- auditar `aplicacao/principal.py`;
- confirmar construção do pacote renderizável somente após `SaidaCanonicaOficial`;
- confirmar bloqueio quando `pronto_para_etapa8=False`;
- confirmar que console/XLSX seguem inalterados;
- decidir próxima macrofrente de equivalência observável.

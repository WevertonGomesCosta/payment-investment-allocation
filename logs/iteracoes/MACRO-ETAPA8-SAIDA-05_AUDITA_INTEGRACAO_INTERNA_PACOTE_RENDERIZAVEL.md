# MACRO-ETAPA8-SAIDA-05 — Audita integração interna do pacote renderizável

## 1. Identificação

- **Macrofrente:** MACRO-ETAPA8-SAIDA-05
- **Tipo:** documental / auditoria de integração interna
- **Baseline de entrada:** `004e019528ba1c187220314f726cdf944c70d6f7`
- **Branch:** `docs/macro-etapa8-saida-05`
- **PR auditada:** PR #453 — MACRO-ETAPA8-SAIDA-04

## 2. Objetivo

Auditar se a integração interna do `PacoteRenderizacaoSaidaCanonica` preserva o contrato macro pós-gates, sem integrar console/XLSX e sem gerar nova saída observável.

## 3. Resultado

```text
STATUS: APROVAR COM RESSALVA P3 DE API TRANSITORIA
```

## 4. Escopo da PR #453

A PR #453 alterou:

```text
aplicacao/principal.py
nucleo/adaptador_renderizacao_saida_canonica.py
logs/iteracoes/MACRO-ETAPA8-SAIDA-04_CORRIGE_P3_E_INTEGRA_PACOTE_RENDERIZAVEL_INTERNO.md
```

## 5. Correção P3 validada

A variável local acentuada e desnecessária em `_auditoria` foi removida.

O adaptador passou a usar diretamente:

```python
_linha('origem_formal', saida.origem_formal)
```

**Resultado:** aprovado.

## 6. Ordem de execução em `aplicacao/principal.py`

A execução preserva a ordem:

```text
Etapas 1–7
bloqueio por pronto_para_etapa8=False
SaidaCanonicaOficial
PacoteRenderizacaoSaidaCanonica
saida_canonica legada para console/XLSX
```

A chamada ao pacote renderizável ocorre somente após:

```python
saida_canonica_oficial = construir_saida_canonica_oficial(...)
```

E é feita por:

```python
pacote_renderizacao_saida_canonica = construir_pacote_renderizacao_saida_canonica(saida_canonica_oficial)
```

**Resultado:** aprovado.

## 7. Bloqueio preservado

Quando `resultado_gates_validacao_nucleo.pronto_para_etapa8=False`, o retorno ocorre antes de qualquer construção posterior:

```text
saida_canonica=None
saida_canonica_oficial=None
pacote_renderizacao_saida_canonica=None
```

Logo, com gates bloqueados, não são chamados:

- `construir_saida_canonica_oficial(...)`;
- `construir_pacote_renderizacao_saida_canonica(...)`;
- funções legadas de saída;
- console;
- XLSX.

**Resultado:** aprovado.

## 8. Console/XLSX preservados

`render_console(...)` permanece recebendo:

```python
render_console(contexto_operacional_canonico, saida_canonica, estado_temporal_inicial=estado_temporal_inicial)
```

`gerar_planilha_operacional(...)` permanece recebendo:

```python
gerar_planilha_operacional(
    contexto=contexto_operacional_canonico,
    saida=saida_canonica,
)
```

Portanto, console e XLSX não passaram a consumir `PacoteRenderizacaoSaidaCanonica`.

**Resultado:** aprovado.

## 9. Ausência de nova saída observável

O pacote renderizável é preservado apenas em memória e descartado em `main()` por:

```python
_ = pacote_renderizacao_saida_canonica
```

Não há geração de novo arquivo, console, XLSX ou saída operacional.

**Resultado:** aprovado.

## 10. Ausência de alteração econômica

A PR #453 não altera:

- motor temporal;
- ledger;
- gates;
- ranking;
- score;
- regras econômicas;
- switchings;
- saldos;
- obrigações;
- dados;
- saídas operacionais.

**Resultado:** aprovado.

## 11. Ressalva P3 — API transitória

`carregar_contexto_e_saida()` passou a retornar oito itens.

Essa alteração é coerente com a integração interna, mas ainda é uma API transitória. Antes de estabilizar o runtime público ou migrar consumidores externos, deve-se auditar chamadas diretas a `carregar_contexto_e_saida()`.

**Classificação:** P3 não bloqueante.

## 12. Validação local informada

A validação local da PR #453 confirmou:

```bash
python -m py_compile aplicacao/principal.py aplicacao/console/*.py nucleo/*.py
python -B aplicacao/principal.py
```

O runtime preservou a mensagem:

```text
Execução bloqueada pelos gates de validação de núcleo: ResultadoGatesValidacaoNucleo.pronto_para_etapa8=False. Console e XLSX oficiais não foram gerados.
```

## 13. Conclusão

A integração interna do `PacoteRenderizacaoSaidaCanonica` está aprovada.

A camada pós-gates agora existe internamente na sequência:

```text
SaidaCanonicaOficial -> PacoteRenderizacaoSaidaCanonica
```

Console e XLSX permanecem legados até uma frente específica de migração/equivalência observável.

## 14. Próxima frente recomendada

```text
MACRO-ETAPA8-SAIDA-06 — Define plano de equivalência observável entre saída legada e pacote renderizável
```

Escopo recomendado:

- mapear campos ainda indisponíveis;
- definir critérios de equivalência para console e XLSX;
- não migrar consumidores ainda;
- não gerar saída nova;
- preparar plano para comparação lado a lado.

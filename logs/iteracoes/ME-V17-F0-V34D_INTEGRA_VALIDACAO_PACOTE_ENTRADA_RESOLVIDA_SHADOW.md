# ME-V17-F0-V34D — Integra validação por PacoteEntradaResolvida ao ContextoBaseline em modo shadow

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4D
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / INTEGRAÇÃO SHADOW
- CLASSE: INTEGRA_VALIDACAO_PACOTE_ENTRADA_RESOLVIDA_CONTEXT0_BASELINE_SHADOW
- ALTERA CÓDIGO: SIM
- ALTERA `nucleo/contexto_baseline.py`: SIM
- ALTERA `nucleo/validacao_pre_execucao.py`: NÃO
- ALTERA `nucleo/entrada_resolvida.py`: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA MOTOR: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO

---

## 2. Objetivo

Integrar a validação por `PacoteEntradaResolvida` ao `ContextoBaseline` em modo shadow, preservando `validacao_pre_execucao` legada como atributo operacional.

---

## 3. Contexto

A V17-F0-V.3.4B criou a função paralela:

```python
validar_pre_execucao_pacote_entrada_resolvida(...)
```

A V17-F0-V.3.4C criou script diagnóstico comparando:

- `ctx.validacao_pre_execucao`;
- `validar_pre_execucao(...)` reexecutada;
- `validar_pre_execucao_pacote_entrada_resolvida(...)`.

A validação local confirmou que a comparação foi funcionalmente aprovada e que a validação por pacote não substituiu a validação legada.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/contexto_baseline.py`;
- `logs/iteracoes/ME-V17-F0-V34D_INTEGRA_VALIDACAO_PACOTE_ENTRADA_RESOLVIDA_SHADOW.md`.

---

## 5. Conteúdo implementado

### 5.1. Import da função paralela

`nucleo/contexto_baseline.py` passou a importar:

```python
validar_pre_execucao_pacote_entrada_resolvida
```

junto de:

```python
PacoteValidacaoPreExecucao
validar_pre_execucao
```

### 5.2. Novo atributo shadow no ContextoBaseline

Foi adicionado ao dataclass `ContextoBaseline`:

```python
validacao_pre_execucao_pacote_entrada_resolvida_shadow: PacoteValidacaoPreExecucao
```

### 5.3. Execução da validação shadow

Após montar e auditar o `pacote_entrada_resolvida_shadow`, o contexto passa a calcular:

```python
validacao_pre_execucao_pacote_entrada_resolvida_shadow = validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida_shadow,
)
```

O resultado é anexado ao contexto, mas não substitui:

```python
validacao_pre_execucao
```

### 5.4. Retorno do contexto

O `return ContextoBaseline(...)` passou a incluir:

```python
validacao_pre_execucao_pacote_entrada_resolvida_shadow=validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/validacao_pre_execucao.py`;
- altera `nucleo/entrada_resolvida.py`;
- altera `nucleo/leitor_planilha.py`;
- altera `nucleo/cache_cdi_bcb.py`;
- altera `nucleo/dados_operacionais_canonicos.py`;
- altera `nucleo/carteira_canonica.py`;
- altera `nucleo/inventario_lotes_expandido_pos_switching.py`;
- altera `nucleo/nucleo_financeiro_minimo.py`;
- altera `nucleo/saida_canonica.py`;
- altera `nucleo/saida_observavel.py`;
- altera `aplicacao/principal.py`;
- altera contrato mestre;
- altera modelo matemático;
- altera Etapa 3;
- altera motor;
- altera ledger;
- altera console;
- altera XLSX;
- altera saída oficial;
- altera dados;
- altera cache.

---

## 7. Semântica operacional preservada

A validação operacional usada pelo pipeline continua sendo:

```python
ctx.validacao_pre_execucao
```

A nova validação fica disponível apenas como:

```python
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

Portanto, a V3.4D ainda não promove a validação por pacote como gate operacional.

---

## 8. Validação local necessária

Executar:

```bash
python -m compileall nucleo
```

Executar teste local confirmando:

- `ctx.validacao_pre_execucao` existe e está `ok=True`;
- `ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow` existe e está `ok=True`;
- ambos são `PacoteValidacaoPreExecucao`;
- os dois objetos são distintos;
- `validacao_pre_execucao` não foi substituída;
- Etapa 3, motor, saída, console e XLSX não foram alterados.

---

## 9. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa recomendada é:

```text
V17-F0-V.3.4E — Criar auditoria comparativa do ContextoBaseline com validação shadow da Etapa 2
```

Essa etapa deve criar script diagnóstico novo em `scripts/diagnostico/`, sem alterar pipeline principal, para comparar o atributo legado `validacao_pre_execucao` com `validacao_pre_execucao_pacote_entrada_resolvida_shadow`.
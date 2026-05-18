# ME-V17-F0-V34F — Fecha integração shadow da Etapa 2 e planeja promoção controlada do gate por PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4F
- TIPO: DOCUMENTAL / FECHAMENTO / PLANEJAMENTO CONTROLADO
- CLASSE: FECHA_INTEGRACAO_SHADOW_ETAPA2_PLANEJA_PROMOCAO_GATE_PACOTE_ENTRADA_RESOLVIDA
- ALTERA CÓDIGO: NÃO
- ALTERA PIPELINE PRINCIPAL: NÃO
- ALTERA CONTEXTO BASELINE: NÃO
- ALTERA VALIDAÇÃO PRÉ-EXECUÇÃO: NÃO
- ALTERA ENTRADA RESOLVIDA: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA MOTOR: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO
- PROMOVE GATE POR PACOTEENTRADARESOLVIDA: NÃO

---

## 2. Objetivo

Consolidar a série V17-F0-V.3.4A–V17-F0-V.3.4E, registrando que a Etapa 2 já possui validação por `PacoteEntradaResolvida` em modo shadow, sem ainda promover essa validação como gate operacional.

Esta microetapa também planeja a promoção controlada futura do gate por `PacoteEntradaResolvida`, mantendo a validação legada como referência operacional até que a promoção seja explicitamente implementada e auditada.

---

## 3. Série consolidada

### 3.1. V17-F0-V.3.4A

A V3.4A planejou a adaptação da Etapa 2 para consumir `PacoteEntradaResolvida`.

Decisão registrada:

- a Etapa 2 deve continuar sendo gate puro;
- a Etapa 2 deve validar artefatos já resolvidos pela Etapa 1;
- a Etapa 2 não deve reler planilha, reconstruir aliases, criar dados canônicos, executar motor ou gerar saída.

### 3.2. V17-F0-V.3.4B

A V3.4B adicionou, em modo paralelo, a função:

```python
validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
) -> PacoteValidacaoPreExecucao
```

A função legada foi preservada:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

### 3.3. V17-F0-V.3.4C

A V3.4C criou diagnóstico comparativo entre:

- `ctx.validacao_pre_execucao`;
- `validar_pre_execucao(...)` reexecutada;
- `validar_pre_execucao_pacote_entrada_resolvida(...)`.

A auditoria confirmou que a validação por pacote era coerente com a validação legada e não substituía o gate operacional.

### 3.4. V17-F0-V.3.4D

A V3.4D integrou ao `ContextoBaseline`, em modo shadow:

```python
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

A validação operacional permaneceu:

```python
ctx.validacao_pre_execucao
```

### 3.5. V17-F0-V.3.4E

A V3.4E criou auditoria comparativa do `ContextoBaseline` com validação shadow da Etapa 2.

A auditoria confirmou:

- validação legada presente;
- validação shadow presente;
- ambas `ok=True`;
- objetos distintos;
- validação shadow sem erros bloqueantes;
- flags shadow coerentes;
- `PacoteEntradaResolvida` shadow presente;
- auditoria do pacote shadow aprovada.

---

## 4. Estado resultante da Etapa 2

Após a série V3.4A–V3.4E, a Etapa 2 possui duas leituras coexistentes:

### 4.1. Gate operacional vigente

```python
ctx.validacao_pre_execucao
```

Continua sendo o gate operacional consumido pelo pipeline atual.

### 4.2. Gate shadow por PacoteEntradaResolvida

```python
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

Está anexado ao `ContextoBaseline`, validado, auditável e ainda não operacional.

---

## 5. Evidências consolidadas

A validação local da V3.4E retornou:

```text
AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO_V34E_OK
```

A auditoria confirmou:

```text
ok=True
erros=[]
avisos=[]
validacao_legada_ok=True
validacao_shadow_ok=True
validacao_shadow_qtd_erros=0
objetos_distintos=True
pacote_shadow_presente=True
auditoria_pacote_shadow_ok=True
```

Também confirmou flags normativas da validação shadow:

```text
modo_paralelo=True
nao_substitui_validacao_legada=True
nao_reconstroi_aliases=True
nao_cria_dados_canonicos=True
nao_altera_motor=True
nao_altera_saida=True
tipo=gate_puro_pre_execucao_pacote_entrada_resolvida
```

---

## 6. Aviso CDI observado

A validação shadow pode registrar o aviso:

```text
Última data da série CDI é anterior à data de referência.
```

Esse aviso foi tratado como esperado e não reprova a integração shadow, pois a Etapa 2 deve registrar a condição sem atualizar cache, calcular rendimento, alterar motor ou modificar saída.

---

## 7. Decisão de fechamento

A integração shadow da Etapa 2 por `PacoteEntradaResolvida` está considerada fechada e validada para fins diagnósticos.

A validação por pacote ainda não deve ser tratada como gate operacional.

O pipeline deve continuar usando:

```python
ctx.validacao_pre_execucao
```

até que uma microetapa futura promova explicitamente o gate por pacote.

---

## 8. Arquitetura-alvo para promoção futura

A promoção futura deve fazer o `ContextoBaseline` usar `PacoteEntradaResolvida` como fonte da validação pré-execução principal.

Arquitetura-alvo futura:

```text
Etapa 1
  -> PacoteEntradaResolvida

Etapa 2
  -> validar_pre_execucao_pacote_entrada_resolvida(PacoteEntradaResolvida)
  -> PacoteValidacaoPreExecucao operacional

Etapa 3
  -> consome PacoteEntradaResolvida validado
  -> produz PacoteDadosOperacionaisCanonicos
```

A promoção deve ocorrer sem misturar Etapa 3, motor, saída, console ou XLSX.

---

## 9. Plano de promoção controlada

A promoção futura deve ser dividida em microetapas.

### 9.1. Microetapa documental de promoção

Formalizar a decisão de trocar o gate operacional da Etapa 2 para a validação por `PacoteEntradaResolvida`.

Essa decisão deve registrar:

- função atual do gate legado;
- função atual do gate shadow;
- evidências da série V3.4A–V3.4E;
- arquivos que poderão ser alterados;
- arquivos que devem permanecer preservados;
- critérios de auditoria pós-promoção.

### 9.2. Microetapa de implementação da promoção

Alterar apenas `nucleo/contexto_baseline.py` para que:

- `validacao_pre_execucao` passe a ser produzido por `validar_pre_execucao_pacote_entrada_resolvida(...)`;
- a validação legada seja preservada temporariamente como atributo shadow, se necessário;
- `PacoteEntradaResolvida` continue anexado ao contexto;
- Etapa 3, motor, saída, console e XLSX permaneçam inalterados.

### 9.3. Microetapa de auditoria pós-promoção

Criar ou atualizar diagnóstico para confirmar:

- o gate operacional passou a ser por `PacoteEntradaResolvida`;
- a validação legada ainda é reexecutável ou auditável;
- os erros e avisos permanecem coerentes;
- não houve alteração em dados operacionais canônicos;
- não houve alteração em motor, saída, console ou XLSX.

---

## 10. Limites preservados nesta microetapa

Esta microetapa não:

- altera `nucleo/contexto_baseline.py`;
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
- altera cache;
- promove a validação shadow como gate operacional.

---

## 11. Próxima microetapa recomendada

A próxima microetapa recomendada é:

```text
V17-F0-V.3.5A — Formaliza promoção controlada do gate da Etapa 2 por PacoteEntradaResolvida
```

Natureza recomendada:

```text
DOCUMENTAL / ARQUITETURAL / DECISÃO DE PROMOÇÃO CONTROLADA
```

Objetivo recomendado:

```text
Formalizar a troca futura do gate operacional da Etapa 2 para `validar_pre_execucao_pacote_entrada_resolvida(...)`, ainda sem implementar a troca no código.
```

---

## 12. Resultado da microetapa

A V17-F0-V.3.4F fecha a frente de integração shadow da Etapa 2.

A Etapa 2 está pronta para uma futura promoção controlada do gate por `PacoteEntradaResolvida`, mas essa promoção ainda não foi executada.
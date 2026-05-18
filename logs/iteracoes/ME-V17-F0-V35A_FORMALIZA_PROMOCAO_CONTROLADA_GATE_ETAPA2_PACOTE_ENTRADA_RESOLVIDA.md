# ME-V17-F0-V35A — Formaliza promoção controlada do gate da Etapa 2 por PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.5A
- TIPO: DOCUMENTAL / ARQUITETURAL / DECISÃO DE PROMOÇÃO CONTROLADA
- CLASSE: FORMALIZA_PROMOCAO_CONTROLADA_GATE_ETAPA2_PACOTE_ENTRADA_RESOLVIDA
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

Formalizar a decisão arquitetural de promover futuramente o gate operacional da Etapa 2 para a validação por `PacoteEntradaResolvida`, ainda sem executar a troca no código.

A promoção futura deverá substituir o uso operacional de:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

por:

```python
validar_pre_execucao_pacote_entrada_resolvida(pacote_entrada_resolvida)
```

como fonte principal de `ctx.validacao_pre_execucao`.

---

## 3. Estado de entrada

A série V17-F0-V.3.4A–V17-F0-V.3.4F deixou a Etapa 2 no seguinte estado:

```text
ctx.validacao_pre_execucao
  -> gate operacional vigente
  -> produzido pela função legada validar_pre_execucao(...)

ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow
  -> gate shadow validado
  -> produzido por validar_pre_execucao_pacote_entrada_resolvida(...)
```

A V17-F0-V.3.4F consolidou que a validação por `PacoteEntradaResolvida` está anexada ao `ContextoBaseline` em modo shadow, aprovada e auditável, mas ainda não operacional.

---

## 4. Evidências consolidadas da série V3.4A–V3.4F

A frente V3.4 demonstrou que:

- a Etapa 2 pode validar `PacoteEntradaResolvida` sem reconstruir aliases;
- a validação por pacote retorna `PacoteValidacaoPreExecucao`;
- a validação por pacote preserva `ok=True`;
- a validação por pacote não contém erros bloqueantes;
- a validação por pacote pode registrar aviso esperado de defasagem CDI;
- a validação legada permanece disponível;
- a validação shadow está anexada ao `ContextoBaseline`;
- a validação shadow é objeto distinto da validação legada;
- `PacoteEntradaResolvida` shadow está presente;
- a auditoria do pacote shadow está aprovada;
- Etapa 3, motor, saída, console e XLSX permaneceram inalterados.

---

## 5. Decisão arquitetural formalizada

A promoção controlada futura do gate da Etapa 2 está autorizada conceitualmente.

A arquitetura-alvo passa a ser:

```text
Etapa 1
  -> monta PacoteEntradaResolvida

Etapa 2
  -> valida PacoteEntradaResolvida
  -> produz PacoteValidacaoPreExecucao operacional

Etapa 3
  -> consome PacoteEntradaResolvida validado
  -> produz PacoteDadosOperacionaisCanonicos
```

O gate operacional da Etapa 2 deverá ser derivado diretamente de `PacoteEntradaResolvida`, e não mais de pacotes soltos `PacoteConfig`, `ContextoExecucao` e `PacotePlanilha`.

---

## 6. O que a promoção futura deverá fazer

A implementação futura da promoção deverá alterar apenas `nucleo/contexto_baseline.py` para que:

1. `PacoteEntradaResolvida` continue sendo montado antes da validação operacional da Etapa 2 por pacote;
2. `validacao_pre_execucao` passe a ser produzido por:

```python
validar_pre_execucao_pacote_entrada_resolvida(pacote_entrada_resolvida_shadow)
```

ou por artefato equivalente caso o nome shadow seja ajustado na mesma microetapa;

3. a validação legada seja preservada temporariamente como atributo de auditoria, por exemplo:

```python
validacao_pre_execucao_legada_shadow
```

4. a validação por pacote mantenha os marcadores:

```text
modo_paralelo=True
nao_reconstroi_aliases=True
nao_cria_dados_canonicos=True
nao_altera_motor=True
nao_altera_saida=True
```

5. a Etapa 3 continue recebendo os mesmos artefatos operacionais que já recebe enquanto sua adaptação própria não for implementada;
6. motor, saída, console e XLSX permaneçam inalterados.

---

## 7. O que a promoção futura não deverá fazer

A promoção futura não deverá:

- alterar `nucleo/validacao_pre_execucao.py`;
- alterar `nucleo/entrada_resolvida.py`;
- alterar `nucleo/leitor_planilha.py`;
- alterar `nucleo/cache_cdi_bcb.py`;
- alterar `nucleo/dados_operacionais_canonicos.py`;
- alterar `nucleo/carteira_canonica.py`;
- alterar `nucleo/inventario_lotes_expandido_pos_switching.py`;
- alterar `nucleo/nucleo_financeiro_minimo.py`;
- alterar `nucleo/saida_canonica.py`;
- alterar `nucleo/saida_observavel.py`;
- alterar `aplicacao/principal.py`;
- alterar contrato mestre;
- alterar modelo matemático;
- alterar Etapa 3;
- alterar motor;
- alterar ledger;
- alterar console;
- alterar XLSX;
- alterar saída oficial;
- alterar dados;
- alterar cache;
- reler planilha;
- reconstruir aliases;
- criar dados canônicos;
- calcular rendimento;
- executar replay;
- decidir pagamentos;
- decidir switching.

---

## 8. Tratamento do aviso CDI

A validação por `PacoteEntradaResolvida` pode continuar registrando o aviso:

```text
Última data da série CDI é anterior à data de referência.
```

Esse aviso deve permanecer diagnóstico na Etapa 2. Ele não deve induzir atualização de cache, cálculo de rendimento ou mudança de motor durante a promoção do gate.

---

## 9. Critério de equivalência operacional esperado

A promoção futura deverá preservar, na prática, a equivalência operacional entre:

```python
ctx.validacao_pre_execucao.ok
```

e o resultado já observado em:

```python
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow.ok
```

Antes da promoção, o estado validado era:

```text
validacao_legada_ok=True
validacao_shadow_ok=True
validacao_shadow_qtd_erros=0
objetos_distintos=True
```

Após a promoção, o estado esperado será:

```text
ctx.validacao_pre_execucao
  -> produzido por validar_pre_execucao_pacote_entrada_resolvida(...)
  -> ok=True
  -> erros_bloqueantes=[]

ctx.validacao_pre_execucao_legada_shadow
  -> produzido por validar_pre_execucao(...)
  -> ok=True
  -> erros_bloqueantes=[]
```

---

## 10. Sequência futura recomendada

### 10.1. V17-F0-V.3.5B

```text
Promove gate da Etapa 2 por PacoteEntradaResolvida no ContextoBaseline
```

Natureza recomendada:

```text
IMPLEMENTAÇÃO CONTROLADA / CONTEXTO BASELINE
```

Escopo recomendado:

- alterar apenas `nucleo/contexto_baseline.py`;
- fazer `ctx.validacao_pre_execucao` ser produzido pela validação por pacote;
- preservar validação legada como shadow/auditoria;
- manter `PacoteEntradaResolvida` anexado ao contexto;
- não alterar Etapa 3, motor, saída, console ou XLSX.

### 10.2. V17-F0-V.3.5C

```text
Audita pós-promoção do gate da Etapa 2 por PacoteEntradaResolvida
```

Natureza recomendada:

```text
DIAGNÓSTICO / AUDITORIA COMPARATIVA
```

Escopo recomendado:

- criar script diagnóstico em `scripts/diagnostico/`;
- confirmar que `ctx.validacao_pre_execucao` agora vem da validação por pacote;
- confirmar que a validação legada permanece auditável;
- confirmar que não houve alteração de Etapa 3, motor, saída, console ou XLSX.

### 10.3. V17-F0-V.3.5D

```text
Fecha promoção controlada do gate da Etapa 2
```

Natureza recomendada:

```text
DOCUMENTAL / FECHAMENTO
```

Objetivo recomendado:

- consolidar V3.5A–V3.5C;
- registrar o novo estado operacional da Etapa 2;
- preparar a próxima frente de adaptação controlada da Etapa 3 para consumir `PacoteEntradaResolvida` validado.

---

## 11. Resultado desta microetapa

A V17-F0-V.3.5A formaliza a decisão de promoção futura do gate da Etapa 2 por `PacoteEntradaResolvida`.

Nenhuma promoção operacional foi executada nesta microetapa.

O próximo passo é implementar a promoção controlada em microetapa própria.
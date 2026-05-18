# ME-V17-F0-V33J — Integra PacoteEntradaResolvida ao contexto baseline em modo shadow

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3J
- TIPO: IMPLEMENTAÇÃO ESTRUTURAL / INTEGRAÇÃO SHADOW
- CLASSE: INTEGRA_PACOTE_ENTRADA_RESOLVIDA_CONTEXT0_BASELINE_SHADOW
- ALTERA LEITURA DA PLANILHA: NÃO
- ALTERA CACHE CDI/BCB OPERACIONAL: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO

---

## 2. Objetivo

Integrar a montagem e a auditoria do `PacoteEntradaResolvida` ao `ContextoBaseline` em modo shadow, sem substituir ainda os atributos consumidos pelo pipeline atual.

---

## 3. Diagnóstico inicial

A série V3.3A–V3.3H criou, montou e auditou o `PacoteEntradaResolvida` como artefato estrutural da Etapa 1.

A V3.3I registrou a auditoria de fechamento da série e indicou como próxima microetapa a integração shadow ao contexto baseline.

Antes desta microetapa, o pacote podia ser montado de forma isolada, mas ainda não era anexado ao contexto baseline retornado por `carregar_contexto_baseline(...)`.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/contexto_baseline.py`;
- `logs/iteracoes/ME-V17-F0-V33J_INTEGRA_PACOTE_ENTRADA_RESOLVIDA_SHADOW.md`.

---

## 5. Conteúdo implementado

### 5.1. Imports estruturais

`nucleo/contexto_baseline.py` passa a importar:

```python
from nucleo.entrada_resolvida import (
    AuditoriaPacoteEntradaResolvida,
    PacoteEntradaResolvida,
    auditar_pacote_entrada_resolvida,
    montar_pacote_entrada_resolvida,
)
```

### 5.2. Novos campos shadow em ContextoBaseline

Foram adicionados ao dataclass `ContextoBaseline`:

```python
pacote_entrada_resolvida_shadow: PacoteEntradaResolvida
auditoria_pacote_entrada_resolvida_shadow: AuditoriaPacoteEntradaResolvida
```

### 5.3. Montagem shadow no contexto baseline

Após a leitura da planilha, validação pré-execução, canonização operacional e carregamento do cache CDI atual, o contexto baseline passa a montar:

```python
pacote_entrada_resolvida_shadow = montar_pacote_entrada_resolvida(...)
```

com metadados explícitos:

```python
modo_shadow_contexto_baseline=True
substitui_atributos_legados=False
substitui_validacao_pre_execucao=False
substitui_dados_operacionais_canonicos=False
substitui_cache_cdi_operacional=False
```

### 5.4. Auditoria shadow

O pacote montado é auditado por:

```python
auditoria_pacote_entrada_resolvida_shadow = auditar_pacote_entrada_resolvida(
    pacote_entrada_resolvida_shadow,
    exigir_cache_cdi=True,
)
```

A auditoria é anexada ao contexto, mas ainda não bloqueia o pipeline.

---

## 6. Limites preservados

Esta microetapa não:

- substitui `pacote_config`;
- substitui `execucao`;
- substitui `pacote_planilha`;
- substitui `validacao_pre_execucao`;
- substitui `dados_operacionais`;
- substitui `cache_cdi`;
- altera `nucleo/leitor_planilha.py`;
- altera `nucleo/cache_cdi_bcb.py`;
- altera `nucleo/entrada_resolvida.py`;
- altera `nucleo/validacao_pre_execucao.py`;
- altera `nucleo/dados_operacionais_canonicos.py`;
- altera `nucleo/carteira_canonica.py`;
- altera `nucleo/inventario_lotes_expandido_pos_switching.py`;
- altera `nucleo/nucleo_financeiro_minimo.py`;
- altera `nucleo/saida_canonica.py`;
- altera `nucleo/saida_observavel.py`;
- altera `aplicacao/principal.py`;
- altera contrato mestre;
- altera modelo matemático;
- altera motor;
- altera ledger;
- altera console;
- altera XLSX;
- altera saída oficial;
- calcula rendimento;
- executa replay de forma diferente;
- cria `PacoteValidacaoPreExecucao`;
- cria `PacoteDadosOperacionaisCanonicos`.

---

## 7. Observação sobre JanelaConsultaCDI

`carregar_planilha(...)` passa a receber `data_referencia=contexto_execucao.data_referencia` na chamada do contexto baseline, apenas para preencher `JanelaConsultaCDI` no pacote de planilha.

Isso não altera a leitura da planilha nem substitui a forma operacional de carregar o cache CDI.

---

## 8. Resultado esperado

O `ContextoBaseline` passa a expor, em modo shadow:

- `pacote_entrada_resolvida_shadow`;
- `auditoria_pacote_entrada_resolvida_shadow`.

O pipeline atual continua consumindo os atributos legados já existentes.

---

## 9. Validação necessária local

Executar validação local com:

- `python -m compileall nucleo`;
- import de `carregar_contexto_baseline`;
- carregamento do contexto com shadows pesados desativados quando apropriado;
- confirmação de existência de `pacote_entrada_resolvida_shadow`;
- confirmação de existência de `auditoria_pacote_entrada_resolvida_shadow`;
- confirmação de `auditoria_pacote_entrada_resolvida_shadow.ok is True`;
- confirmação de que os atributos legados continuam presentes;
- verificação de escopo restrita a `nucleo/contexto_baseline.py` e este log.

---

## 10. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa deve ser uma auditoria comparativa do contexto baseline antes e depois da integração shadow, confirmando que a inclusão do pacote não alterou os atributos operacionais existentes nem a saída principal.

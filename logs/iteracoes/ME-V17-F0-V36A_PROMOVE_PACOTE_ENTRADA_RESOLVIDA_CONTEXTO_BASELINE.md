# ME-V17-F0-V36A — Promove PacoteEntradaResolvida como artefato operacional do ContextoBaseline

## 1. Identificação

- MICROETAPA: V17-F0-V.3.6A
- TIPO: IMPLEMENTAÇÃO CONTROLADA / CONTEXTO BASELINE / PREPARAÇÃO DA ETAPA 3
- CLASSE: PROMOVE_PACOTE_ENTRADA_RESOLVIDA_COMO_ARTEFATO_OPERACIONAL
- ALTERA CÓDIGO: SIM
- ALTERA CONTEXTO BASELINE: SIM
- ALTERA ETAPA 1: NÃO
- ALTERA ETAPA 2: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA MOTOR: NÃO
- ALTERA REPLAY: NÃO
- ALTERA LEDGER: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO

---

## 2. Objetivo

Promover o `PacoteEntradaResolvida` já existente no `ContextoBaseline` de atributo com semântica principal de `shadow` para artefato operacional oficial do contexto.

A microetapa expõe:

```python
ctx.pacote_entrada_resolvida
ctx.auditoria_pacote_entrada_resolvida
```

preservando, temporariamente, os aliases compatíveis:

```python
ctx.pacote_entrada_resolvida_shadow
ctx.auditoria_pacote_entrada_resolvida_shadow
```

A Etapa 3 ainda não foi adaptada nesta microetapa.

---

## 3. Justificativa arquitetural

A V17-F0-V.3.5D fechou a Etapa 2 como gate operacional por `PacoteEntradaResolvida`, mas registrou que a Etapa 3 não deve consumir diretamente um atributo com semântica final de `shadow`.

Antes de planejar a adaptação da Etapa 3, o `ContextoBaseline` precisa expor explicitamente o pacote resolvido como artefato operacional oficial.

Esta microetapa é uma ponte controlada entre o fechamento da Etapa 2 e a futura preparação da Etapa 3.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `nucleo/contexto_baseline.py`
- `logs/iteracoes/ME-V17-F0-V36A_PROMOVE_PACOTE_ENTRADA_RESOLVIDA_CONTEXTO_BASELINE.md`

---

## 5. Alteração implementada

No dataclass `ContextoBaseline`, foram adicionados os atributos operacionais:

```python
pacote_entrada_resolvida: PacoteEntradaResolvida
auditoria_pacote_entrada_resolvida: AuditoriaPacoteEntradaResolvida
```

Os atributos transitórios foram preservados:

```python
pacote_entrada_resolvida_shadow: PacoteEntradaResolvida
auditoria_pacote_entrada_resolvida_shadow: AuditoriaPacoteEntradaResolvida
```

Na função `carregar_contexto_baseline(...)`, a montagem passou a usar o nome operacional:

```python
pacote_entrada_resolvida = montar_pacote_entrada_resolvida(...)
```

Em seguida, o alias transitório foi preservado por identidade de objeto:

```python
pacote_entrada_resolvida_shadow = pacote_entrada_resolvida
```

A auditoria também foi promovida por nome operacional, preservando alias por identidade:

```python
auditoria_pacote_entrada_resolvida = auditar_pacote_entrada_resolvida(...)
auditoria_pacote_entrada_resolvida_shadow = auditoria_pacote_entrada_resolvida
```

A validação pré-execução passou a consumir o nome operacional:

```python
validacao_pre_execucao = validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida,
)
```

---

## 6. Metadados do pacote

Os metadados do pacote foram ajustados para registrar a promoção operacional no `ContextoBaseline`:

```text
modo_shadow_contexto_baseline=False
artefato_operacional_contexto_baseline=True
alias_shadow_preservado_temporariamente=True
substitui_atributos_legados=False
substitui_validacao_pre_execucao=True
validacao_legada_preservada_shadow=True
substitui_dados_operacionais_canonicos=False
substitui_cache_cdi_operacional=False
```

Esses metadados preservam a regra de que esta microetapa não substitui dados operacionais canônicos, cache CDI operacional, Etapa 3, motor ou saída.

---

## 7. Invariantes esperados

Após esta microetapa, devem ser verdadeiros:

```python
hasattr(ctx, "pacote_entrada_resolvida") is True
hasattr(ctx, "pacote_entrada_resolvida_shadow") is True
ctx.pacote_entrada_resolvida is ctx.pacote_entrada_resolvida_shadow

hasattr(ctx, "auditoria_pacote_entrada_resolvida") is True
hasattr(ctx, "auditoria_pacote_entrada_resolvida_shadow") is True
ctx.auditoria_pacote_entrada_resolvida is ctx.auditoria_pacote_entrada_resolvida_shadow

ctx.validacao_pre_execucao.ok is True
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow is ctx.validacao_pre_execucao
ctx.validacao_pre_execucao_legada_shadow is not ctx.validacao_pre_execucao
```

---

## 8. Limites preservados

Esta microetapa não altera:

- `nucleo/dados_operacionais_canonicos.py`;
- `nucleo/validacao_pre_execucao.py`;
- `nucleo/entrada_resolvida.py`;
- `nucleo/leitor_planilha.py`;
- `nucleo/cache_cdi_bcb.py`;
- `nucleo/carteira_canonica.py`;
- `nucleo/inventario_lotes_expandido_pos_switching.py`;
- scripts de motor;
- replay passado;
- switching econômico;
- ledger;
- saída canônica;
- console;
- XLSX;
- dados;
- cache.

---

## 9. Validação local recomendada

Executar:

```bash
python -m compileall nucleo scripts/diagnostico
```

E validar, em diagnóstico próprio posterior, que os atributos operacionais e os aliases shadow apontam para os mesmos objetos.

---

## 10. Próxima microetapa recomendada

A próxima microetapa recomendada é:

```text
V17-F0-V.3.6B — Audita PacoteEntradaResolvida operacional no ContextoBaseline
```

Natureza recomendada:

```text
DIAGNÓSTICO / AUDITORIA PÓS-PROMOÇÃO
```

Objetivo:

```text
Confirmar por script diagnóstico que ctx.pacote_entrada_resolvida existe, que ctx.pacote_entrada_resolvida_shadow é alias do mesmo objeto, que a auditoria operacional existe, que o gate da Etapa 2 permanece aprovado e que a Etapa 3 continua inalterada.
```

---

## 11. Decisão de fechamento da V3.6A

A V17-F0-V.3.6A não reabre Etapa 1 nem Etapa 2.

Ela apenas promove no `ContextoBaseline` o artefato já existente `PacoteEntradaResolvida` como atributo operacional oficial, preservando alias shadow temporário para compatibilidade.

A Etapa 3 permanece não adaptada nesta microetapa.

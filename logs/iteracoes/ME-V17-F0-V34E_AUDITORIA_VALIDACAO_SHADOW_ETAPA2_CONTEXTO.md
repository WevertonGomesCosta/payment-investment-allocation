# ME-V17-F0-V34E — Auditoria comparativa da validação shadow da Etapa 2 no ContextoBaseline

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4E
- TIPO: DIAGNÓSTICO / AUDITORIA COMPARATIVA
- CLASSE: AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO_BASELINE
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

---

## 2. Objetivo

Criar script diagnóstico novo para comparar, dentro do `ContextoBaseline`, a validação operacional legada:

```python
ctx.validacao_pre_execucao
```

com a validação shadow da Etapa 2 por `PacoteEntradaResolvida`:

```python
ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

A auditoria deve confirmar que a validação shadow está anexada ao contexto, aprovada e distinta da validação operacional legada.

---

## 3. Contexto

A V17-F0-V.3.4D integrou ao `ContextoBaseline`, em modo shadow:

```python
validacao_pre_execucao_pacote_entrada_resolvida_shadow
```

A validação local da V3.4D confirmou:

```text
VALIDACAO_SHADOW_PACOTE_ENTRADA_RESOLVIDA_CONTEXTO_BASELINE_OK
```

A V3.4E cria uma auditoria executável para tornar essa comparação reproduzível.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `scripts/diagnostico/auditar_validacao_shadow_etapa2_contexto_v34e.py`;
- `logs/iteracoes/ME-V17-F0-V34E_AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO.md`.

---

## 5. Conteúdo implementado

Foi criado o script:

```text
scripts/diagnostico/auditar_validacao_shadow_etapa2_contexto_v34e.py
```

O script:

1. carrega `ContextoBaseline` com shadows pesados desativados;
2. lê `ctx.validacao_pre_execucao`;
3. lê `ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow`;
4. confirma que ambos são `PacoteValidacaoPreExecucao`;
5. confirma que ambos estão `ok=True`;
6. confirma que os objetos são distintos;
7. confirma que o shadow não contém erros bloqueantes;
8. confirma flags de modo paralelo, não substituição da legada, não reconstrução de aliases, não criação de dados canônicos, não alteração de motor e não alteração de saída;
9. confirma presença de `pacote_entrada_resolvida_shadow` e auditoria shadow aprovada.

---

## 6. Avisos previstos

A auditoria aceita como avisos esperados:

```text
Última data da série CDI é anterior à data de referência.
Série CDI começa após data_inicial_consulta da JanelaConsultaCDI.
```

Esses avisos não reprovam a auditoria quando não há erro bloqueante.

---

## 7. Resultado esperado

O script deve emitir:

```text
AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO_V34E_OK
```

quando a validação legada e a validação shadow estiverem aprovadas e preservadas como objetos distintos.

---

## 8. Limites preservados

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
- altera cache.

---

## 9. Validação local necessária

Executar:

```bash
python -m compileall nucleo scripts/diagnostico
python -B scripts/diagnostico/auditar_validacao_shadow_etapa2_contexto_v34e.py
```

Verificar que o diff da microetapa contém apenas:

- `scripts/diagnostico/auditar_validacao_shadow_etapa2_contexto_v34e.py`;
- `logs/iteracoes/ME-V17-F0-V34E_AUDITORIA_VALIDACAO_SHADOW_ETAPA2_CONTEXTO.md`.

---

## 10. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa recomendada é:

```text
V17-F0-V.3.4F — Fechar integração shadow da Etapa 2 e planejar promoção controlada do gate por PacoteEntradaResolvida
```

Essa etapa deve ser documental e só deve consolidar a série V3.4A–V3.4E, sem promover ainda a validação shadow como gate operacional.
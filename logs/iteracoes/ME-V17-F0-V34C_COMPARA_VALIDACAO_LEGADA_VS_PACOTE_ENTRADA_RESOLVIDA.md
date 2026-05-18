# ME-V17-F0-V34C — Compara validação legada vs validação por PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4C
- TIPO: DIAGNÓSTICO / AUDITORIA COMPARATIVA
- CLASSE: COMPARA_VALIDACAO_LEGADA_VS_PACOTE_ENTRADA_RESOLVIDA
- ALTERA PIPELINE PRINCIPAL: NÃO
- ALTERA CONTEXTO BASELINE: NÃO
- ALTERA ENTRADA RESOLVIDA: NÃO
- ALTERA VALIDAÇÃO PRÉ-EXECUÇÃO: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA MOTOR: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO
- ALTERA CACHE: NÃO

---

## 2. Objetivo

Criar um script diagnóstico para comparar a validação pré-execução legada com a validação paralela por `PacoteEntradaResolvida`, sem alterar o pipeline principal.

---

## 3. Contexto

A V17-F0-V.3.4B adicionou, em modo paralelo, a função:

```python
validar_pre_execucao_pacote_entrada_resolvida(...)
```

A função legada permaneceu preservada:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

A V3.4C cria uma auditoria executável para comparar essas duas validações antes de qualquer integração shadow ao `ContextoBaseline`.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py`;
- `logs/iteracoes/ME-V17-F0-V34C_COMPARA_VALIDACAO_LEGADA_VS_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 5. Conteúdo implementado

O script:

```text
scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py
```

executa:

1. carregamento do `ContextoBaseline` com shadows pesados desativados;
2. leitura de `ctx.validacao_pre_execucao`;
3. reexecução da validação legada com `validar_pre_execucao(...)`;
4. execução da validação por `PacoteEntradaResolvida` com `validar_pre_execucao_pacote_entrada_resolvida(...)`;
5. comparação de status, erros, avisos e evidências;
6. verificação de que a validação por pacote não substituiu `ctx.validacao_pre_execucao`;
7. verificação de flags de modo paralelo, não reconstrução de aliases, não criação de dados canônicos e não alteração de motor/saída.

---

## 6. Resultado esperado

O script deve emitir:

```text
COMPARACAO_VALIDACAO_PRE_EXECUCAO_V34C_OK
```

quando:

- a validação legada do contexto está aprovada;
- a validação legada reexecutada está aprovada;
- a validação por pacote está aprovada;
- não há erros bloqueantes;
- as flags de modo paralelo estão corretas;
- `ctx.validacao_pre_execucao` não foi substituída pela validação por pacote.

---

## 7. Avisos previstos

A validação por pacote pode registrar avisos operacionais esperados, especialmente:

```text
Última data da série CDI é anterior à data de referência.
```

Esse aviso não reprova a auditoria comparativa se não vier acompanhado de erro bloqueante.

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
python -B scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py
```

Verificar que o diff da microetapa contém apenas:

- `scripts/diagnostico/comparar_validacao_pre_execucao_v34c.py`;
- `logs/iteracoes/ME-V17-F0-V34C_COMPARA_VALIDACAO_LEGADA_VS_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 10. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa recomendada é:

```text
V17-F0-V.3.4D — Integrar validação por PacoteEntradaResolvida ao ContextoBaseline em modo shadow
```

Essa etapa deverá anexar a validação nova ao contexto como atributo shadow, preservando `validacao_pre_execucao` legada como atributo operacional.
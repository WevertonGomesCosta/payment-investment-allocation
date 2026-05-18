# ME-V17-F0-V35C — Audita pós-promoção do gate da Etapa 2 por PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.5C
- TIPO: DIAGNÓSTICO / AUDITORIA PÓS-PROMOÇÃO
- CLASSE: AUDITA_POS_PROMOCAO_GATE_ETAPA2_PACOTE_ENTRADA_RESOLVIDA
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

Criar auditoria diagnóstica pós-promoção para confirmar que o gate operacional da Etapa 2 passou a ser produzido por `PacoteEntradaResolvida` e que a validação legada foi preservada apenas como referência auditável.

---

## 3. Arquivos alterados

Alterados nesta microetapa:

- `scripts/diagnostico/auditar_pos_promocao_gate_etapa2_v35c.py`;
- `logs/iteracoes/ME-V17-F0-V35C_AUDITA_POS_PROMOCAO_GATE_ETAPA2_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 4. Conteúdo implementado

O script diagnóstico verifica:

- `ctx.validacao_pre_execucao` como gate operacional;
- tipo do gate operacional;
- `ok=True` no gate operacional;
- ausência de erros bloqueantes no gate operacional;
- `gate.evidencias["tipo"] == "gate_puro_pre_execucao_pacote_entrada_resolvida"`;
- preservação de `ctx.validacao_pre_execucao_legada_shadow`;
- `ctx.validacao_pre_execucao_legada_shadow.evidencias["tipo"] == "gate_puro_pre_execucao"`;
- `ctx.validacao_pre_execucao_pacote_entrada_resolvida_shadow is ctx.validacao_pre_execucao`;
- presença de `PacoteEntradaResolvida`;
- auditoria do pacote aprovada;
- metadados de promoção restrita à Etapa 2;
- presença dos dados operacionais canônicos já existentes.

---

## 5. Resultado esperado

O script deve emitir:

```text
AUDITORIA_POS_PROMOCAO_GATE_ETAPA2_V35C_OK
```

quando a promoção estiver operacionalmente coerente.

---

## 6. Limites preservados

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
- altera saída canônica;
- altera console;
- altera XLSX;
- altera saída oficial;
- altera dados;
- altera cache.

---

## 7. Validação local necessária

Executar:

```bash
python -m compileall nucleo scripts/diagnostico
python -B scripts/diagnostico/auditar_pos_promocao_gate_etapa2_v35c.py
```

Verificar que o diff da microetapa contém apenas:

- `scripts/diagnostico/auditar_pos_promocao_gate_etapa2_v35c.py`;
- `logs/iteracoes/ME-V17-F0-V35C_AUDITA_POS_PROMOCAO_GATE_ETAPA2_PACOTE_ENTRADA_RESOLVIDA.md`.

---

## 8. Próxima microetapa recomendada

Após validação local aprovada, a próxima microetapa recomendada é:

```text
V17-F0-V.3.5D — Fecha Etapa 2 como gate por PacoteEntradaResolvida
```

Natureza recomendada:

```text
DOCUMENTAL / FECHAMENTO DA ETAPA 2
```

Objetivo:

```text
Consolidar a Etapa 2 como gate operacional por PacoteEntradaResolvida e registrar que a próxima frente deve ser a preparação da Etapa 3 em novo chat.
```
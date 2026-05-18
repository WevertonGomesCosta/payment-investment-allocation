# ME-V17-F0-V33K — Auditoria comparativa do contexto baseline após integração shadow

## 1. Identificação

- MICROETAPA: V17-F0-V.3.3K
- TIPO: DIAGNÓSTICO / AUDITORIA COMPARATIVA
- CLASSE: AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW
- ALTERA CONTEXTO BASELINE: NÃO
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

Criar uma auditoria comparativa executável para verificar se a integração shadow do `PacoteEntradaResolvida` ao `ContextoBaseline` não alterou os atributos operacionais existentes nem o comportamento principal do pipeline.

---

## 3. Diagnóstico inicial

A V17-F0-V.3.3J integrou ao `ContextoBaseline`, em modo shadow:

- `pacote_entrada_resolvida_shadow`;
- `auditoria_pacote_entrada_resolvida_shadow`.

A V3.3J preservou os atributos legados, mas ainda era necessário criar uma auditoria comparativa executável para confirmar que:

- os atributos operacionais continuam presentes;
- o pacote shadow usa as mesmas referências dos objetos legados;
- o cache operacional permanece carregado pela lógica legada;
- os shadows pesados ficam desativados durante a auditoria;
- a auditoria shadow do pacote está aprovada.

---

## 4. Arquivos alterados

Alterados nesta microetapa:

- `scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py`;
- `logs/iteracoes/ME-V17-F0-V33K_AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW.md`.

---

## 5. Conteúdo implementado

### 5.1. Script diagnóstico novo

Foi criado:

```text
scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py
```

O script carrega o contexto baseline com shadows pesados desativados e executa uma auditoria comparativa do estado resultante.

### 5.2. Atributos legados auditados

O script verifica a presença dos atributos operacionais obrigatórios:

- `pacote_config`;
- `execucao`;
- `calendario_financeiro`;
- `pacote_planilha`;
- `validacao_pre_execucao`;
- `carteira_canonica`;
- `dados_operacionais`;
- `recebidos_auditaveis`;
- `fontes_elegiveis_pagamento`;
- `saldo_disponivel_geral`;
- `decisao_local_v1`;
- `cache_cdi`;
- `ranking_carteira`;
- `nucleo_financeiro`;
- `tabela_iof`;
- `faixas_ir`.

### 5.3. Atributos shadow auditados

O script verifica:

- `pacote_entrada_resolvida_shadow`;
- `auditoria_pacote_entrada_resolvida_shadow`.

Também confirma que:

- `pacote_config` é a mesma referência dentro do shadow;
- `execucao` é a mesma referência dentro do shadow;
- `pacote_planilha` é a mesma referência dentro do shadow;
- `cache_cdi` é a mesma referência dentro do shadow.

### 5.4. Metadados shadow auditados

O script confirma as flags:

```text
modo_shadow_contexto_baseline=True
substitui_atributos_legados=False
substitui_validacao_pre_execucao=False
substitui_dados_operacionais_canonicos=False
substitui_cache_cdi_operacional=False
altera_leitura_planilha=False
altera_cache_cdi=False
altera_validacao_pre_execucao=False
altera_dados_operacionais_canonicos=False
altera_motor=False
altera_saida=False
```

### 5.5. Cache operacional

A auditoria verifica que o cache CDI operacional permanece com:

```text
origem_janela_consulta=dados_operacionais_legado
janela_consulta_cdi_informada=False
```

Essa verificação confirma que a `JanelaConsultaCDI` do pacote shadow não substituiu a lógica operacional de cache.

### 5.6. Shapes operacionais

O script registra evidências de shape para:

- `carteira_canonica`;
- `dados_operacionais.inventario_canonico`;
- `dados_operacionais.gastos_canonicos`;
- `dados_operacionais.salarios_canonicos`;
- `dados_operacionais.switching_canonico`.

---

## 6. Limites preservados

Esta microetapa não:

- altera `nucleo/contexto_baseline.py`;
- altera `nucleo/entrada_resolvida.py`;
- altera `nucleo/leitor_planilha.py`;
- altera `nucleo/cache_cdi_bcb.py`;
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

## 7. Saída esperada do script

O script deve emitir:

```text
AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW_V33K_OK
```

quando a integração shadow estiver preservando os atributos operacionais e o cache operacional legado.

---

## 8. Validação necessária local

Executar:

```bash
python -m compileall nucleo scripts/diagnostico
python -B scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py
```

Também verificar que o diff da microetapa contém apenas:

- `scripts/diagnostico/auditar_contexto_baseline_shadow_v33k.py`;
- `logs/iteracoes/ME-V17-F0-V33K_AUDITORIA_COMPARATIVA_CONTEXTO_BASELINE_SHADOW.md`.

---

## 9. Próxima microetapa recomendada

Após validação local aprovada da V3.3K, a próxima microetapa deve ser definida com base no resultado da auditoria comparativa.

Se a auditoria confirmar preservação total dos atributos operacionais, a próxima frente recomendada será planejar a integração controlada da Etapa 2 para consumir `PacoteEntradaResolvida`, ainda sem alterar Etapa 3, motor ou saída.

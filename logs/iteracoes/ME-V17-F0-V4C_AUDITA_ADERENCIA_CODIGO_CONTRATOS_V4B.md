# ME-V17-F0-V4C — Audita aderência do código atual aos contratos V4B

## 1. Identificação

- MICROETAPA: ME-V17-F0-V4C
- VERSAO_CANDIDATA: V17-F0-V.4C
- TIPO: DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_ADERENCIA_CODIGO_ATUAL_CONTRATOS_V4B
- BASELINE_DE_ENTRADA: V17-F0-V.4B
- BASELINE_COMMIT_ENTRADA: 4c361dcc9b9191b70de764247c0cef89d6157562
- ALTERA_CODIGO: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_ESTADO_TEMPORAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Auditar a aderência do código atual aos contratos mínimos especificados na V4B, mapeando campo a campo:

```text
quais campos já existem
quais são derivados
quais estão implícitos
quais são calculados pela saída canônica
quais ainda faltam
```

Esta microetapa é exclusivamente documental e diagnóstica.

---

## 3. Arquivos inspecionados

Foram inspecionados, sem alteração:

```text
logs/iteracoes/ME-V17-F0-V4B_ESPECIFICA_CONTRATOS_FLUXOGRAMA_ETAPA4.md
nucleo/replay_passado_controlado.py
nucleo/ledger_temporal_conjunto.py
nucleo/pacote_ledger_temporal.py
nucleo/saida_canonica.py
```

---

## 4. Critérios de classificação

Cada campo dos contratos V4B foi classificado como:

| Classe | Significado |
|---|---|
| EXISTE | campo já existe em artefato formal ou estrutura retornada |
| EXISTE_COM_NOME_DIFERENTE | existe, mas com nome/schema diferente do contrato V4B |
| DERIVADO | pode ser derivado de campos atuais sem nova regra econômica |
| IMPLICITO | existe como estado interno, mas não é retornado formalmente |
| CALCULADO_NA_SAIDA | é produzido ou ajustado em `saida_canonica.py` |
| SHADOW_VAZIO | campo existe no pacote shadow, mas é preenchido vazio |
| AUSENTE | não existe ou não é recuperável de forma contratual atual |

---

## 5. Aderência — PacoteReplayPassado

### 5.1. Artefato atual

O artefato atual é:

```text
PacoteReplayPassadoControlado
```

Campos atuais:

```text
lotes_apos_replay
log_passado
estado_lotes_passado
auditoria
validacao
```

### 5.2. Matriz de aderência

| Campo V4B | Estado atual | Origem atual | Observação |
|---|---|---|---|
| versao | AUSENTE | n/d | não há versão no dataclass atual |
| modo_execucao | AUSENTE | n/d | modo controlado aparece no nome, não em campo |
| data_referencia | IMPLICITO | argumento `data_referencia` | usado na função, mas não armazenado no pacote |
| lotes_apos_replay | EXISTE | `PacoteReplayPassadoControlado.lotes_apos_replay` | aderente |
| log_movimentos_passados | EXISTE_COM_NOME_DIFERENTE | `log_passado` | precisa renomear/alias contratual |
| estado_lotes_passado | EXISTE | `estado_lotes_passado` | aderente, mas schema parcial |
| audit_trilha_pagamentos_passados | DERIVADO | `log_passado` + `auditoria` | não há campo próprio |
| auditoria_replay | EXISTE_COM_NOME_DIFERENTE | `auditoria` | precisa alias/nome contratual |
| validacao_replay | EXISTE_COM_NOME_DIFERENTE | `validacao` | precisa alias/nome contratual |
| metadados_origem | AUSENTE | n/d | não há metadados formais |

### 5.3. Aderência dos campos de `log_movimentos_passados`

| Campo V4B | Estado atual | Campo atual aproximado |
|---|---|---|
| movimento_id | EXISTE_COM_NOME_DIFERENTE | `Sequencia Saque` |
| despesa_id | EXISTE_COM_NOME_DIFERENTE | `Despesa ID` |
| data_movimento | EXISTE_COM_NOME_DIFERENTE | `Data` |
| descricao_pagamento | EXISTE_COM_NOME_DIFERENTE | `Conta` |
| lote_id | EXISTE_COM_NOME_DIFERENTE | `Lote` |
| fonte_pagamento | DERIVADO | `Lote`, `Fase Operacional Lote`, `Situacao Investimento Lote` |
| valor_pagamento | EXISTE_COM_NOME_DIFERENTE | `Valor Conta` |
| valor_bruto_sacado | EXISTE_COM_NOME_DIFERENTE | `Bruto` |
| imposto | EXISTE_COM_NOME_DIFERENTE | `Imposto` |
| valor_liquido_sacado | EXISTE_COM_NOME_DIFERENTE | `Liquido` |
| saldo_antes | EXISTE_COM_NOME_DIFERENTE | `Saldo Antes` |
| saldo_depois | EXISTE_COM_NOME_DIFERENTE | `Saldo Remanescente` |
| status_cobertura | DERIVADO | auditoria de cobertura agregada |
| motivo_inconsistencia | DERIVADO | lista `inconsistencias` em auditoria |

### 5.4. Aderência dos campos de `estado_lotes_passado`

| Campo V4B | Estado atual | Campo atual aproximado |
|---|---|---|
| lote_id | EXISTE_COM_NOME_DIFERENTE | `Lote ID` |
| data_recebimento | EXISTE_COM_NOME_DIFERENTE | `Data Recebimento` |
| data_aplicacao | EXISTE_COM_NOME_DIFERENTE | `Data Aplicação` |
| data_base_fiscal | EXISTE_COM_NOME_DIFERENTE | `Data Base Fiscal` |
| valor_inicial | EXISTE_COM_NOME_DIFERENTE | `Valor Inicial` |
| saldo_bruto_pos_replay | EXISTE_COM_NOME_DIFERENTE | `Saldo Após Replay` |
| saldo_liquido_pos_replay | DERIVADO | calculável com Lote + regras fiscais |
| principal_remanescente | EXISTE_COM_NOME_DIFERENTE | `Principal Remanescente` |
| fator_acumulado | EXISTE_COM_NOME_DIFERENTE | `Fator Acumulado` |
| esgotado_no_replay | EXISTE_COM_NOME_DIFERENTE | `Esgotado no Replay` |
| vezes_usado_no_replay | EXISTE_COM_NOME_DIFERENTE | `Vezes Usado no Replay` |
| total_bruto_sacado | EXISTE_COM_NOME_DIFERENTE | `Total Bruto Sacado` |
| total_imposto_pago | EXISTE_COM_NOME_DIFERENTE | `Total Imposto Pago` |
| total_liquido_sacado | EXISTE_COM_NOME_DIFERENTE | `Total Líquido Sacado` |
| investimento | EXISTE_COM_NOME_DIFERENTE | `Investimento` |
| situacao_investimento | EXISTE_COM_NOME_DIFERENTE | `Situacao Investimento` |
| carencia_ate | AUSENTE | n/d |
| regra_iof | EXISTE_COM_NOME_DIFERENTE | `Regra IOF` |

### 5.5. Veredito do PacoteReplayPassado

```text
PACOTE_REPLAY_PASSADO_ADERENCIA=parcial_alta
PACOTE_REPLAY_PASSADO_TEM_ARTEFATO_FORMAL=sim
PACOTE_REPLAY_PASSADO_PRECISA_ADAPTADOR_MINIMO=sim
```

O replay é o contrato mais próximo do alvo, mas ainda precisa de `versao`, `modo_execucao`, `data_referencia`, `metadados_origem`, aliases contratuais e campos explícitos para saldo líquido e carência.

---

## 6. Aderência — PacoteLedgerTemporalOperacional

### 6.1. Artefatos atuais

Artefatos atuais relacionados:

```text
construir_ledger_temporal_conjunto(...)
PacoteLedgerTemporal
construir_pacote_ledger_temporal_shadow(...)
```

O ledger efetivo ainda retorna um `dict`. O `PacoteLedgerTemporal` existe, mas ainda em modo shadow.

### 6.2. Matriz de aderência do pacote

| Campo V4B | Estado atual | Origem atual | Observação |
|---|---|---|---|
| versao | EXISTE | `PacoteLedgerTemporal.versao` | ainda versão shadow |
| modo_execucao | EXISTE_COM_NOME_DIFERENTE | `modo_shadow` | precisa generalizar para operacional/shadow |
| data_referencia | EXISTE | `data_referencia` | inferido do contexto |
| eventos_temporais | EXISTE | `eventos_temporais` | vem de `retorno['eventos']` |
| estado_temporal_por_data | SHADOW_VAZIO | lista vazia | ainda não materializado |
| saldos_por_lote | DERIVADO | extraído de eventos | não é estado completo |
| saldos_disponiveis_por_data | SHADOW_VAZIO | lista vazia | não materializado |
| vencimentos_processados | SHADOW_VAZIO | lista vazia | não materializado |
| pagamentos_futuros_processados | DERIVADO | extraído de eventos | existe, mas incompleto |
| fontes_elegiveis_por_pagamento | AUSENTE | n/d | contrato V4B ainda não existe |
| fontes_elegiveis_por_data | SHADOW_VAZIO | lista vazia | não materializado |
| fifo_candidatos_avaliados | EXISTE | `fifo_candidatos_avaliados` | aderente |
| alertas_temporais | DERIVADO | chaves com alerta/bloqueio no retorno | parcial |
| auditoria_ledger_temporal | EXISTE | `auditoria_ledger_temporal` | precisa atualizar semântica após V3.7S |
| validacao_ledger_temporal | EXISTE | `validacao_ledger_temporal` | aderente parcial |
| metadados_origem | EXISTE | `metadados_origem` | ainda shadow/legado |

### 6.3. Aderência dos eventos temporais

O ledger atual já produz eventos com campos importantes, entre eles:

```text
pagamento_id
data
conta
pacote_do_dia
necessita_switching
lote_fonte_origem
lote_sugerido_operacional
switching_candidato
switching_promovido
switching_materializado
evento_switching_id
data_switching_operacional
destino_switching_operacional
lote_pos_switching_materializado
saldo_antes
bruto
imposto
liquido
consumo
saldo_depois
cobertura_integral
status
motivo_bloqueio
fonte_candidata_id
tipo_fonte_candidata
origem_fonte_candidata
fontes_usadas
valor_pago_por_fonte
saldo_antes_por_fonte
consumo_por_fonte
saldo_depois_por_fonte
```

Mapeamento contra V4B:

| Campo V4B | Estado atual | Campo atual aproximado |
|---|---|---|
| evento_id | AUSENTE/PARCIAL | existe `evento_switching_id` apenas para switching |
| data_evento | EXISTE_COM_NOME_DIFERENTE | `data` |
| tipo_evento | DERIVADO | pagamento/switching inferível |
| subtipo_evento | DERIVADO | `pacote_do_dia`, switching flags |
| lote_id | EXISTE_COM_NOME_DIFERENTE | `lote_fonte_origem` / `lote_sugerido_operacional` |
| lote_origem | EXISTE_COM_NOME_DIFERENTE | `lote_fonte_origem` |
| lote_destino | EXISTE_COM_NOME_DIFERENTE | `lote_pos_switching_materializado` |
| pagamento_id | EXISTE | `pagamento_id` |
| valor_evento | DERIVADO | `consumo` / `liquido` |
| valor_bruto | EXISTE_COM_NOME_DIFERENTE | `bruto` |
| valor_liquido | EXISTE_COM_NOME_DIFERENTE | `liquido` |
| imposto | EXISTE | `imposto` |
| saldo_antes | EXISTE | `saldo_antes` |
| saldo_depois | EXISTE | `saldo_depois` |
| status_evento | EXISTE_COM_NOME_DIFERENTE | `status` |
| motivo_bloqueio | EXISTE | `motivo_bloqueio` |
| fonte_temporal | DERIVADO | origem/fonte candidata |
| origem_dado | DERIVADO | metadados ainda dispersos |

### 6.4. Aderência dos pagamentos futuros processados

| Campo V4B | Estado atual | Origem atual |
|---|---|---|
| pagamento_id | EXISTE | evento / derivado no pacote shadow |
| data_pagamento | EXISTE_COM_NOME_DIFERENTE | `data` / `Data` |
| descricao_pagamento | EXISTE_COM_NOME_DIFERENTE | `conta` |
| valor_pagamento | EXISTE/PARCIAL | `fifo_valor_pagamento` ou evento |
| status_pagamento_temporal | EXISTE_COM_NOME_DIFERENTE | `status` |
| cobertura_integral | EXISTE | `cobertura_integral` |
| lote_sugerido_operacional | EXISTE | `lote_sugerido_operacional` |
| lote_reserva | AUSENTE/PARCIAL | pode existir em estruturas anteriores, não no evento final padrão |
| necessita_switching | EXISTE | `necessita_switching` |
| switching_antes_pagamento | DERIVADO | `pacote_do_dia` / flags do quadro |
| switching_depois_pagamento | DERIVADO | `pacote_do_dia` / flags do quadro |
| motivo_bloqueio | EXISTE | `motivo_bloqueio` |
| pacote_dia | EXISTE_COM_NOME_DIFERENTE | `pacote_do_dia` |

### 6.5. Aderência das fontes elegíveis

| Campo V4B | Estado atual | Origem atual |
|---|---|---|
| pagamento_id | EXISTE/PARCIAL | FIFO e eventos |
| data_pagamento | EXISTE/PARCIAL | FIFO/eventos |
| fonte_candidata_id | EXISTE | evento final |
| tipo_fonte_candidata | EXISTE | evento final |
| origem_fonte_candidata | EXISTE | evento final |
| saldo_liquido_disponivel | EXISTE | evento final e FIFO |
| saldo_bruto_disponivel | AUSENTE/PARCIAL | não padronizado |
| carencia_ok | DERIVADO | FIFO interno |
| vencimento_ok | DERIVADO | estado temporal interno |
| migracao_ok | DERIVADO | bloqueios por migração |
| motivo_descarte_fonte | EXISTE | evento final |
| status_fonte | DERIVADO | `status`, `elegivel_temporalmente` |

### 6.6. Veredito do PacoteLedgerTemporalOperacional

```text
PACOTE_LEDGER_TEMPORAL_OPERACIONAL_ADERENCIA=parcial_media
PACOTE_LEDGER_TEMPORAL_SHADOW_EXISTE=sim
RETORNO_LEDGER_DICT_AINDA_E_FONTE_REAL=sim
CAMPOS_CRITICOS_PRESENTES=eventos_temporais,fifo,pagamentos_derivados,saldos_derivados
CAMPOS_CRITICOS_AUSENTES=estado_temporal_por_data,saldos_disponiveis_por_data,vencimentos_processados,fontes_elegiveis_por_pagamento
```

O pacote shadow é a base correta, mas precisa ser normalizado para operacional, com campos hoje vazios ou derivados de eventos.

---

## 7. Aderência — PacoteEstadoTemporal

### 7.1. Artefato atual

Não existe `PacoteEstadoTemporal` formal.

O estado temporal está distribuído em:

```text
replay_passado.lotes_apos_replay
replay_passado.estado_lotes_passado
estado_lotes interno do ledger
saldos_por_lote derivados pelo PacoteLedgerTemporal shadow
ajustes e filtros na saída canônica
```

### 7.2. Matriz de aderência

| Campo V4B | Estado atual | Origem atual |
|---|---|---|
| versao | AUSENTE | n/d |
| data_referencia | IMPLICITO | contexto/execução |
| estado_lotes_por_data | IMPLICITO | estado interno do ledger |
| estado_lotes_final | DERIVADO | replay + ledger + saída |
| saldos_por_lote | DERIVADO | PacoteLedgerTemporal shadow |
| saldos_disponiveis_por_data | SHADOW_VAZIO/AUSENTE | pacote shadow vazio |
| fontes_disponiveis_por_data | AUSENTE | n/d |
| vencimentos_por_data | AUSENTE/IMPLICITO | regras internas |
| migracoes_por_data | DERIVADO | switching canônico + ledger |
| auditoria_estado_temporal | AUSENTE | n/d |
| validacao_estado_temporal | AUSENTE | n/d |

### 7.3. Veredito do PacoteEstadoTemporal

```text
PACOTE_ESTADO_TEMPORAL_ADERENCIA=baixa
PACOTE_ESTADO_TEMPORAL_EXISTE=nao
ESTADO_TEMPORAL_IMPLÍCITO_EXISTE=sim
MATERIALIZAR_ESTADO_TEMPORAL_SHADOW=necessario
```

Este é o principal contrato ainda ausente da Etapa 4.

---

## 8. Aderência — PacoteAuditoriaTemporal

### 8.1. Artefato atual

Não existe `PacoteAuditoriaTemporal` formal.

Auditorias estão distribuídas em:

```text
PacoteReplayPassadoControlado.auditoria
PacoteLedgerTemporal.auditoria_ledger_temporal
PacoteLedgerTemporal.validacao_ledger_temporal
saida.auditoria
logs documentais
scripts diagnósticos
```

### 8.2. Matriz de aderência

| Campo V4B | Estado atual | Origem atual |
|---|---|---|
| versao | AUSENTE | n/d |
| data_referencia | IMPLICITO | contexto/saída/pacotes |
| auditoria_replay | EXISTE_COM_NOME_DIFERENTE | `replay_passado.auditoria` |
| auditoria_ledger | EXISTE_COM_NOME_DIFERENTE | `auditoria_ledger_temporal` |
| auditoria_estado_temporal | AUSENTE | n/d |
| auditoria_fontes_elegiveis | DERIVADO | FIFO/eventos/saída |
| auditoria_switching_temporal | DERIVADO/PARCIAL | ledger + switching shadow |
| auditoria_invariantes | DERIVADO/PARCIAL | diagnósticos em ledger/saída |
| auditoria_residuos_legados | DERIVADO/PARCIAL | logs e flags shadow |
| validacao_temporal_global | AUSENTE | n/d |

### 8.3. Aderência dos invariantes mínimos

| Invariante V4B | Estado atual |
|---|---|
| saldo_lote_nao_negativo | IMPLICITO/PARCIAL |
| pagamento_futuro_nao_usa_lote_exaurido | PARCIAL, com filtros em ledger/saída |
| origem_migrada_nao_permanece_disponivel | PARCIAL, tratado por V3.6F/V3.7D e ledger |
| switching_canonico_usado_como_fonte_primaria | EXISTE após V3.7S |
| fallback_switching_bruto_nao_usado_quando_canonico_presente | EXISTE funcionalmente, mas auditoria ainda não centralizada |
| saida_canonica_nao_recalcula_saldo_temporal | NAO_ADERENTE; saída ainda interpreta e filtra |
| patrimonio_temporal_reconciliavel | PARCIAL, calculado na saída |

### 8.4. Veredito do PacoteAuditoriaTemporal

```text
PACOTE_AUDITORIA_TEMPORAL_ADERENCIA=baixa_media
PACOTE_AUDITORIA_TEMPORAL_EXISTE=nao
AUDITORIAS_DISTRIBUIDAS_EXISTEM=sim
CENTRALIZACAO_AUDITORIA_TEMPORAL=necessaria
```

---

## 9. Aderência — fronteira Etapa 4 → saída canônica

### 9.1. Estado atual

A saída canônica ainda:

```text
consome replay_passado.log_passado
inclui ajustes de POS ausentes no extrato passado
escolhe quadro_futuro
monta mapa_central
chama construir_ledger_temporal_conjunto(...)
interpreta eventos do ledger
filtra lotes exauridos/migrados
monta extrato futuro
monta auditorias e resumos patrimoniais
```

### 9.2. Matriz de aderência

| Regra V4B | Estado atual | Decisão |
|---|---|---|
| saída consome PacoteReplayPassado | PARCIAL | consome `replay_passado.log_passado`, não pacote contratual |
| saída consome PacoteLedgerTemporalOperacional | NAO_ADERENTE | ainda chama ledger diretamente |
| saída consome PacoteEstadoTemporal | NAO_ADERENTE | pacote não existe |
| saída consome PacoteAuditoriaTemporal | NAO_ADERENTE | pacote não existe |
| saída não chama ledger diretamente | NAO_ADERENTE | ainda chama `construir_ledger_temporal_conjunto(...)` |
| saída não reconstrói estado temporal | PARCIAL/NAO_ADERENTE | ainda filtra/interpreta lotes e saldos |

### 9.3. Veredito da fronteira com saída

```text
FRONTEIRA_ETAPA4_SAIDA_ADERENCIA=baixa_media
SAIDA_CANONICA_AINDA_ORQUESTRA_ETAPA4=sim
MIGRACAO_DEVE_SER_SHADOW_E_GRADUAL=sim
```

---

## 10. Resumo por contrato

| Contrato V4B | Aderência atual | Principal lacuna |
|---|---|---|
| PacoteReplayPassado | parcial alta | aliases contratuais, metadados, data/versão/modo |
| PacoteLedgerTemporalOperacional | parcial média | ainda shadow; campos vazios; retorno dict legado |
| PacoteEstadoTemporal | baixa | pacote não existe; estado está implícito/distribuído |
| PacoteAuditoriaTemporal | baixa/média | auditorias distribuídas; sem validação temporal global |
| Fronteira Etapa 4 → saída | baixa/média | saída chama ledger diretamente e reconstrói parte da Etapa 4 |

---

## 11. Prioridade técnica derivada da V4C

A ordem originalmente sugerida na V4B deve ser ajustada para reduzir risco:

### 11.1. Primeiro: PacoteReplayPassado mínimo

Motivo:

```text
já existe PacoteReplayPassadoControlado
aderência é parcial alta
adaptação é de baixo risco
melhora entrada do estado temporal
```

### 11.2. Segundo: PacoteLedgerTemporalOperacional shadow

Motivo:

```text
já existe PacoteLedgerTemporal shadow
precisa corrigir metadados e preencher/explicitar campos derivados
prepara remoção do retorno dict legado
```

### 11.3. Terceiro: PacoteEstadoTemporal shadow

Motivo:

```text
é o principal contrato ausente
precisa consolidar replay + ledger
não deve ser feito antes de estabilizar replay e ledger como pacotes
```

### 11.4. Quarto: PacoteAuditoriaTemporal

Motivo:

```text
é agregador de auditorias já existentes
fica mais simples depois de Replay, Ledger e Estado estarem materializados
```

### 11.5. Quinto: saída canônica em modo shadow

Motivo:

```text
saída só deve ser conectada aos pacotes temporais quando eles existirem e forem equivalentes
```

---

## 12. Próximas microetapas recomendadas

### V4D — Adapta PacoteReplayPassado mínimo em modo shadow

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Criar um adaptador PacoteReplayPassado mínimo a partir do PacoteReplayPassadoControlado atual, com aliases contratuais, metadados e validação, sem alterar o replay efetivo nem a saída.
```

Escopo provável:

```text
nucleo/pacote_replay_passado.py
scripts/diagnostico/auditar_pacote_replay_passado_v4d.py
logs/iteracoes/ME-V17-F0-V4D_ADAPTA_PACOTE_REPLAY_PASSADO_SHADOW.md
```

---

### V4E — Normaliza PacoteLedgerTemporalOperacional shadow

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Normalizar PacoteLedgerTemporal para contrato operacional shadow, corrigindo metadados pós-V3.7S, adicionando aliases e explicitando campos ausentes como vazios auditados.
```

---

### V4F — Materializa PacoteEstadoTemporal shadow

Tipo:

```text
EXECUTÁVEL / ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Consolidar estado pós-replay e eventos do ledger em PacoteEstadoTemporal explícito.
```

---

### V4G — Especifica/implementa PacoteAuditoriaTemporal shadow

Tipo:

```text
DOCUMENTAL + ADAPTADOR SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Centralizar auditorias de replay, ledger, estado, fontes, switching, invariantes e resíduos legados.
```

---

### V4H — Conecta saída canônica aos pacotes temporais em modo shadow

Tipo:

```text
EXECUTÁVEL / INTEGRAÇÃO SHADOW / SEM ALTERAÇÃO OBSERVÁVEL
```

Objetivo:

```text
Comparar caminho atual da saída com caminho baseado em pacotes temporais validados.
```

---

## 13. Decisão final

```text
V4C_STATUS=AUDITORIA_ADERENCIA_CONCLUIDA
PACOTE_REPLAY_PASSADO_ADERENCIA=parcial_alta
PACOTE_LEDGER_TEMPORAL_OPERACIONAL_ADERENCIA=parcial_media
PACOTE_ESTADO_TEMPORAL_ADERENCIA=baixa
PACOTE_AUDITORIA_TEMPORAL_ADERENCIA=baixa_media
FRONTEIRA_ETAPA4_SAIDA_ADERENCIA=baixa_media
IMPLEMENTACAO_EXECUTAVEL=nao
PROXIMA_MICROETAPA=V17-F0-V.4D
```

---

## 14. Conclusão

A V4C confirma que a Etapa 4 já possui bases funcionais suficientes, mas a aderência aos contratos V4B ainda é parcial.

O caminho mais seguro não é começar pelo ledger nem pela saída, mas pelo replay, porque `PacoteReplayPassadoControlado` já existe e pode ser adaptado para o contrato mínimo com baixo risco e sem alterar o replay efetivo.

A próxima etapa recomendada é criar um `PacoteReplayPassado` mínimo em modo shadow, preservando integralmente a saída atual.

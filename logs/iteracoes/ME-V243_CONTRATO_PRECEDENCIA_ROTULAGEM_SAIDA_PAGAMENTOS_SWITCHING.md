# ME-V243 — Contrato diagnóstico de precedência e rotulagem da saída pagamentos + switching

```text
STATUS_DO_REGISTRO: DOCUMENTAL_DIAGNOSTICO_CONTROLADO
MICROETAPA: ME-V243
VERSAO_CANDIDATA: V243
BASELINE_DE_ENTRADA: V242
TIPO: DOCUMENTAL / DIAGNOSTICO
CLASSE: FORMALIZA_CONTRATO_PRECEDENCIA_SAIDA_SEM_ALTERAR_CODIGO
```

---

## 1. Estado herdado da V242

```text
BASELINE_DE_ENTRADA: V242
VERSAO_CANDIDATA: V243
V242: INTERPRETACAO_DIAGNOSTICA_DOS_RESULTADOS_V241
PROXIMA_FRENTE_CONTROLADA_RECOMENDADA_V242: FORMALIZACAO_DE_CONTRATO_DE_PRECEDENCIA
FONTE_DE_VERDADE_OPERACIONAL: NAO_CONSOLIDADA
PRECEDENCIA_OPERACIONAL_DEFINITIVA: NAO_DEFINIDA
DIVERGENCIA_CORRIGIDA: NAO
REGRA_ECONOMICA_ALTERADA: NAO
ME_V244: NAO_INICIADA
```

A ME-V243 cria apenas um contrato diagnóstico/propositivo para orientar a próxima frente controlada.

Este documento não altera código, não altera saída canônica, não altera motores, não altera recomputação central, não altera simulador central, não altera planilha operacional, não altera dados, não altera cache e não corrige divergências.

---

## 2. Síntese dos achados V241/V242

Resultados quantitativos consolidados da V241 e interpretados na V242:

```text
total_pagamentos_auditados: 149
origem_mista_detectada: 148 / 149 = 99.33%
divergencia_lote_motor_central: 33 / 149 = 22.15%
divergencia_lote_motor_extrato: 33 / 149 = 22.15%
divergencia_lote_central_extrato: 0 / 149 = 0.0%
divergencia_estrategia_motor_extrato: 0 / 149 = 0.0%
divergencia_saldo_motor_central: 148 / 149 = 99.33%
divergencia_saldo_motor_extrato: 148 / 149 = 99.33%
divergencia_saldo_central_extrato: 0 / 149 = 0.0%
divergencia_switching_motor_extrato: 0 / 149 = 0.0%
```

Diagnóstico consolidado:

```text
O extrato_futuro está alinhado à recomputação central para lote, saldo e cobertura, mas preserva estratégia e switching do motor. O problema central é a composição híbrida não rotulada entre campos centrais e campos do motor, não uma falha simples de transmissão central para extrato.
```

Consequência operacional:

```text
A saída atual pode ser tecnicamente coerente com as camadas internas, mas insuficientemente rotulada para o uso operacional. O usuário pode interpretar campos de origens diferentes como uma decisão única e homogênea.
```

---

## 3. Mapa dos campos atuais do extrato_futuro

Campos atuais observados no extrato futuro:

```text
Data
Conta
Despesa ID
Valor
Lote sugerido
Saldo Antes
Bruto
Imposto
Líquido
Saldo Remanescente
Cobertura integral
Estratégia
Lote reserva
Necessita switching
```

Classificação diagnóstica geral:

```text
CAMPOS_DE_IDENTIFICACAO:
- Data
- Conta
- Despesa ID
- Valor

CAMPOS_FINANCEIROS_CENTRAIS:
- Lote sugerido
- Saldo Antes
- Bruto
- Imposto
- Líquido
- Saldo Remanescente
- Cobertura integral

CAMPOS_DO_MOTOR_DE_RECOMENDACAO:
- Estratégia
- Lote reserva
- Necessita switching

CAMPOS_HIBRIDOS_OU_AMBIGUOS:
- Lote sugerido, quando lido em conjunto com Estratégia
- Saldo Remanescente, quando lido como se fosse saldo residual temporal do motor
- Cobertura integral, quando lida como se fosse cobertura recomendada pelo motor
- Necessita switching, quando lida em conjunto com lote/saldo central sem rotulagem de origem
```

---

## 4. Origem diagnóstica de cada campo atual

```text
Campo atual: Data
Origem diagnóstica: identificação comum
Camada principal: comum entre motor, recomputação central e extrato
Risco de ambiguidade: baixo
Rotulagem futura recomendada: Data pagamento
```

```text
Campo atual: Conta
Origem diagnóstica: identificação comum
Camada principal: comum entre motor, recomputação central e extrato
Risco de ambiguidade: baixo
Rotulagem futura recomendada: Conta / descrição pagamento
```

```text
Campo atual: Despesa ID
Origem diagnóstica: identificação comum
Camada principal: comum entre motor, recomputação central e extrato
Risco de ambiguidade: baixo
Rotulagem futura recomendada: Pagamento ID
```

```text
Campo atual: Valor
Origem diagnóstica: identificação comum
Camada principal: comum entre motor, recomputação central e extrato
Risco de ambiguidade: baixo
Rotulagem futura recomendada: Valor pagamento
```

```text
Campo atual: Lote sugerido
Origem diagnóstica: recomputação central quando mapa_central está disponível
Camada principal: central
Risco de ambiguidade: alto
Motivo: em 33/149 pagamentos diverge do lote_recomendado do motor, mas coincide com lote_final_central e extrato
Rotulagem futura recomendada: Lote central exibido
Campo complementar recomendado: Lote recomendado motor
```

```text
Campo atual: Saldo Antes
Origem diagnóstica: recomputação central
Camada principal: central
Risco de ambiguidade: moderado
Rotulagem futura recomendada: Saldo antes central
```

```text
Campo atual: Bruto
Origem diagnóstica: recomputação central
Camada principal: central
Risco de ambiguidade: moderado
Rotulagem futura recomendada: Bruto central
```

```text
Campo atual: Imposto
Origem diagnóstica: recomputação central
Camada principal: central
Risco de ambiguidade: moderado
Rotulagem futura recomendada: Imposto central
```

```text
Campo atual: Líquido
Origem diagnóstica: recomputação central
Camada principal: central
Risco de ambiguidade: moderado/alto
Motivo: pode ser confundido com cobertura_esperada do motor
Rotulagem futura recomendada: Líquido central
Campo complementar recomendado: Cobertura esperada motor
```

```text
Campo atual: Saldo Remanescente
Origem diagnóstica: recomputação central
Camada principal: central
Risco de ambiguidade: muito alto
Motivo: diverge do saldo_residual_temporal_pos_recomendacao do motor em 148/149 pagamentos
Rotulagem futura recomendada: Saldo remanescente central
Campo complementar recomendado: Saldo residual temporal motor
```

```text
Campo atual: Cobertura integral
Origem diagnóstica: derivada da camada central/extrato
Camada principal: central/exibida
Risco de ambiguidade: alto
Motivo: pode ser confundida com cobertura_integral_recomendada do motor
Rotulagem futura recomendada: Cobertura integral central/exibida
Campo complementar recomendado: Cobertura integral recomendada motor
```

```text
Campo atual: Estratégia
Origem diagnóstica: motor de recomendação pagamentos + switching
Camada principal: motor
Risco de ambiguidade: alto quando combinada com lote/saldo central
Rotulagem futura recomendada: Estratégia recomendada motor
```

```text
Campo atual: Lote reserva
Origem diagnóstica: motor de recomendação pagamentos + switching
Camada principal: motor
Risco de ambiguidade: moderado
Rotulagem futura recomendada: Lote reserva motor
```

```text
Campo atual: Necessita switching
Origem diagnóstica: motor de recomendação pagamentos + switching / indicador exibido alinhado ao motor
Camada principal: motor
Risco de ambiguidade: moderado
Rotulagem futura recomendada: Necessita switching segundo motor
```

---

## 5. Proposta de rotulagem futura

### 5.1 Campos centrais

Campos centrais devem explicitar que representam a recomputação central ou o valor exibido derivado dela:

```text
Lote sugerido -> Lote central exibido
Saldo Antes -> Saldo antes central
Bruto -> Bruto central
Imposto -> Imposto central
Líquido -> Líquido central
Saldo Remanescente -> Saldo remanescente central
Cobertura integral -> Cobertura integral central/exibida
```

Finalidade:

```text
Evitar que campos financeiros centrais sejam interpretados como resultado direto do motor de recomendação pagamentos + switching.
```

### 5.2 Campos do motor

Campos do motor devem explicitar que representam recomendação, estratégia ou sinalização do motor:

```text
Estratégia -> Estratégia recomendada motor
Lote reserva -> Lote reserva motor
Necessita switching -> Necessita switching segundo motor
```

Campos complementares recomendados para uma implementação futura:

```text
Lote recomendado motor
Cobertura esperada motor
Cobertura integral recomendada motor
Saldo residual temporal motor
Ganho líquido estimado switching motor
Data sugerida switching motor
Produto destino switching motor
Motivo recomendação motor
Fallback automático motor
```

Finalidade:

```text
Permitir auditoria operacional explícita entre o que o motor recomenda e o que a recomputação central exibe como lote/valor financeiro.
```

### 5.3 Campos exibidos

Campos exibidos devem manter rastreabilidade de origem:

```text
origem_lote_exibido: central | motor | fallback | indefinida
origem_saldo_exibido: central | motor | fallback | indefinida
origem_cobertura_exibida: central | motor | derivada | indefinida
origem_estrategia_exibida: motor | central | fallback | indefinida
```

Finalidade:

```text
Tornar explícito se a linha do extrato futuro representa a visão central, a visão do motor ou uma composição controlada.
```

---

## 6. Regras diagnósticas/propositivas para evitar ambiguidade

### Regra diagnóstica 1 — Não exibir campo híbrido sem origem

```text
Todo campo do extrato_futuro que possa vir de mais de uma camada deve possuir origem explícita ou rotulagem que indique sua camada principal.
```

### Regra diagnóstica 2 — Separar campos centrais de campos do motor

```text
Campos financeiros centrais não devem ser apresentados como se fossem recomendação do motor. Campos do motor não devem ser apresentados como se fossem decisão financeira central.
```

### Regra diagnóstica 3 — Não corrigir divergência por substituição silenciosa

```text
Quando lote_recomendado_motor divergir de lote_central_exibido, a futura saída não deve simplesmente substituir um pelo outro sem contrato auditado. A divergência deve ser exibida, rotulada ou resolvida por regra aprovada em microetapa própria.
```

### Regra diagnóstica 4 — Rotular saldos com semânticas distintas

```text
Saldo remanescente central e saldo residual temporal motor devem ser tratados como medidas distintas. A divergência de 148/149 pagamentos indica que não devem ser colapsados em uma única coluna sem definição semântica explícita.
```

### Regra diagnóstica 5 — Preservar switching como sinal do motor até decisão posterior

```text
Como divergencia_switching_motor_extrato foi 0/149, a indicação de switching pode permanecer associada ao motor em etapa futura, mas deve ser rotulada como campo do motor quando exibida ao lado de lote/saldo central.
```

### Regra diagnóstica 6 — Antes de ajustar saída, definir contrato mínimo auditável

```text
Qualquer ajuste técnico futuro em saida_canonica.py deve partir de contrato aprovado que determine:
- quais campos centrais continuam no extrato;
- quais campos do motor serão adicionados ou renomeados;
- quais campos de origem serão incluídos;
- como divergências entre motor e central serão exibidas.
```

---

## 7. Proposta de contrato mínimo para futura saída

Este contrato é diagnóstico/propositivo, não definitivo.

```text
BLOCO_IDENTIFICACAO:
- Data pagamento
- Conta / descrição pagamento
- Pagamento ID
- Valor pagamento
```

```text
BLOCO_VISAO_CENTRAL:
- Lote central exibido
- Saldo antes central
- Bruto central
- Imposto central
- Líquido central
- Saldo remanescente central
- Cobertura integral central/exibida
```

```text
BLOCO_VISAO_MOTOR:
- Estratégia recomendada motor
- Lote recomendado motor
- Lote reserva motor
- Necessita switching segundo motor
- Cobertura esperada motor
- Cobertura integral recomendada motor
- Saldo residual temporal motor
```

```text
BLOCO_AUDITORIA_ORIGEM:
- origem_lote_exibido
- origem_saldo_exibido
- origem_cobertura_exibida
- origem_estrategia_exibida
- divergencia_lote_motor_central
- divergencia_saldo_motor_central
- divergencia_cobertura_motor_central
```

Interpretação:

```text
A futura saída deve permitir que o usuário diferencie claramente a visão central, a visão do motor e as divergências entre ambas. A ME-V243 não decide qual visão deve vencer; apenas propõe que ambas sejam rotuladas até decisão posterior.
```

---

## 8. Ambiguidades que devem ser resolvidas antes de ajuste técnico

```text
AMBIGUIDADE_01:
O campo atual 'Lote sugerido' representa lote central exibido quando mapa_central existe, mas pode ser lido como recomendação do motor.
RISCO: ALTO
RESOLUCAO_PROPOSTA: renomear/rotular como Lote central exibido e adicionar Lote recomendado motor.
```

```text
AMBIGUIDADE_02:
O campo atual 'Saldo Remanescente' representa saldo central, mas diverge do saldo residual temporal do motor em 148/149 pagamentos.
RISCO: MUITO_ALTO
RESOLUCAO_PROPOSTA: renomear/rotular como Saldo remanescente central e adicionar Saldo residual temporal motor.
```

```text
AMBIGUIDADE_03:
O campo atual 'Estratégia' vem do motor, mas aparece ao lado de lote/saldo central.
RISCO: ALTO
RESOLUCAO_PROPOSTA: renomear/rotular como Estratégia recomendada motor.
```

```text
AMBIGUIDADE_04:
O campo atual 'Cobertura integral' é exibido de forma alinhada ao central/extrato, mas pode ser confundido com cobertura recomendada pelo motor.
RISCO: ALTO
RESOLUCAO_PROPOSTA: rotular como Cobertura integral central/exibida e adicionar Cobertura integral recomendada motor quando necessário.
```

```text
AMBIGUIDADE_05:
A saída não possui colunas de origem explícita.
RISCO: ALTO
RESOLUCAO_PROPOSTA: adicionar campos origem_* em microetapa técnica futura, após aprovação.
```

---

## 9. Preparação objetiva da ME-V244

```text
PROXIMA_MICROETAPA_RECOMENDADA: ME-V244
NOME_RECOMENDADO: Ajuste técnico controlado da saída canônica para rotulagem de origem pagamentos + switching
TIPO_RECOMENDADO: CORRECAO_CIRURGICA / IMPLEMENTACAO_CONTROLADA
CLASSE_RECOMENDADA: AJUSTA_ROTULAGEM_SAIDA_SEM_ALTERAR_REGRA_ECONOMICA
STATUS: RECOMENDACAO_APENAS
IMPLEMENTACAO_INICIADA: NAO
```

Objetivo recomendado para a ME-V244:

```text
Implementar, em microetapa própria e após auditoria preventiva, ajuste cirúrgico na camada de saída para explicitar a origem dos campos do extrato_futuro, separando campos centrais e campos do motor de recomendação pagamentos + switching, sem alterar regra econômica, sem alterar motor, sem alterar recomputação central e sem corrigir divergências por substituição silenciosa.
```

Escopo técnico recomendado para avaliação preventiva da ME-V244:

```text
- avaliar alteração controlada em nucleo/saida_canonica.py;
- avaliar impacto em scripts/operacional/gerar_planilha_operacional.py apenas se necessário para exibir colunas novas/renomeadas;
- preservar motor_recomendacao_pagamentos_switching_v1.py;
- preservar recomputacao_sequencial_central_v1.py;
- preservar simulador_central_eventos_v1.py;
- não alterar regra econômica;
- não alterar dados;
- gerar evidência comparativa antes/depois apenas das colunas de saída;
- manter FONTE_DE_VERDADE_OPERACIONAL = NAO_CONSOLIDADA até decisão posterior.
```

A ME-V244 não é iniciada por este documento.

---

## 10. Registros explícitos obrigatórios

```text
FONTE_DE_VERDADE_OPERACIONAL = NAO_CONSOLIDADA
PRECEDENCIA_OPERACIONAL_DEFINITIVA = NAO_DEFINIDA
DIVERGENCIA_CORRIGIDA = NAO
REGRA_ECONOMICA_ALTERADA = NAO
SAIDA_CANONICA_AJUSTADA = NAO
CONTRATO_DE_CAMPOS_EM_CODIGO_AJUSTADO = NAO
```

---

## 11. Registros de não alteração e não execução

```text
CONTRATO_MESTRE: NAO_ALTERADO
MMEF_OFICIAL: NAO_ALTERADO
CODIGO: NAO_ALTERADO
SAIDA_CANONICA: NAO_ALTERADA
MOTORES: NAO_ALTERADOS
RECOMPUTACAO_CENTRAL: NAO_ALTERADA
SIMULADOR_CENTRAL: NAO_ALTERADO
PLANILHA_OPERACIONAL: NAO_ALTERADA
DADOS: NAO_ALTERADOS
CACHE: NAO_ALTERADO
RELATORIOS_EXISTENTES: NAO_ALTERADOS
RELEASE_CHECKER_EXECUTADO: NAO
SCRIPTS_EXECUTADOS: NAO
CODEX_ACIONADO: NAO
V184_USADA_COMO_VERSAO_OFICIAL: NAO
ME_V244_INICIADA: NAO
```

---

## 12. Estado final da ME-V243

```text
CONTRATO_DIAGNOSTICO_PROPOSITIVO: CRIADO
MAPA_CAMPOS_EXTRATO_FUTURO: FORMALIZADO
ORIGEM_DIAGNOSTICA_DOS_CAMPOS: FORMALIZADA
ROTULAGEM_FUTURA_RECOMENDADA: FORMALIZADA
AMBIGUIDADES_PRE_AJUSTE_TECNICO: IDENTIFICADAS
PROXIMA_MICROETAPA_RECOMENDADA: ME-V244
VERSAO_CANDIDATA_ATUAL: V243
PROMOCAO_V243: NAO_REALIZADA
AUDITORIA_POS_IMPLEMENTACAO_DA_ME_V243: PENDENTE
```

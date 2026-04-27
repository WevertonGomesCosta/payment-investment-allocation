# ME-V239 — Auditoria comparativa do contrato de saída pagamentos + switching

```text
STATUS_DO_REGISTRO: AUDITORIA_DIAGNOSTICA_CONTROLADA_READ_ONLY
MICROETAPA: ME-V239
VERSAO_CANDIDATA: V239
BASELINE_DE_ENTRADA: V238
TIPO: DIAGNOSTICO / AUDITORIA
CLASSE_SEMANTICA_MMEF: AUDITA_CONTRATO_SAIDA_PAGAMENTOS_SWITCHING_SEM_ALTERAR_REGRA
```

---

## 1. Estado pós-V238

```text
ESTADO_POS_V238: CARREGADO
V238: AUDITORIA_DIAGNOSTICA_DA_INTEGRACAO_PAGAMENTOS_SWITCHING
INTEGRACAO_PAGAMENTOS_SWITCHING: EXISTE_PARCIALMENTE
PRONTA_PARA_PROMOCAO_DIRETA: NAO
FONTE_VERDADE_OPERACIONAL: NAO_CONSOLIDADA
PRINCIPAL_LACUNA_V238: contrato de precedencia/fonte de verdade entre motor, recomputacao central e saida canonica
ME_V239: AUDITORIA_COMPARATIVA_DO_CONTRATO_DE_SAIDA_PAGAMENTOS_SWITCHING
```

A ME-V239 foi executada em modo read-only.

Nenhum arquivo existente foi alterado.

Nenhum script foi executado.

Nenhuma simulação econômica foi executada.

Nenhuma implementação técnica foi iniciada.

---

## 2. Arquivos inspecionados em modo read-only

Foram inspecionados, sem edição, os seguintes arquivos e documentos:

```text
nucleo/motor_recomendacao_pagamentos_switching_v1.py
nucleo/saida_canonica.py
nucleo/contexto_baseline.py
nucleo/recomputacao_sequencial_central_v1.py
nucleo/simulador_central_eventos_v1.py
nucleo/alocador_pagamentos_terminal_v1.py
scripts/operacional/gerar_planilha_operacional.py
relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md
relatorios/atuais/GATE_ECONOMICO_APORTES_PLANEJADOS_V220.md
logs/iteracoes/ME-V238_AUDITORIA_INTEGRACAO_PAGAMENTOS_SWITCHING.md
```

Observação:

```text
A leitura de nucleo/recomputacao_sequencial_central_v1.py foi necessária para mapear o contrato de campos centrais consumidos por saida_canonica.py. A operação foi exclusivamente read-only e não executou script.
```

---

## 3. Linha de produção da saída operacional

A linha de produção observada é:

```text
carregar_contexto_baseline
  -> recomputacao_sequencial_central_v1
  -> motor_recomendacao_pagamentos_switching_v1
  -> construir_saida_canonica
  -> extrato_futuro
  -> gerar_planilha_operacional
```

Ponto crítico:

```text
saida_canonica.py usa o quadro preferencial do motor quando existe, mas, ao construir o resumo financeiro de cada pagamento futuro, usa primeiro mapa_central quando disponível.
```

Consequência:

```text
O extrato futuro pode combinar campos de origem distinta na mesma linha operacional.
```

---

## 4. Contrato do quadro_recomendacoes do motor

Arquivo de origem:

```text
nucleo/motor_recomendacao_pagamentos_switching_v1.py
```

Pacote principal:

```text
PacoteMotorRecomendacaoPagamentosSwitchingV1
  - quadro_recomendacoes
  - auditoria
```

Campos do `quadro_recomendacoes` relevantes para saída operacional:

```text
pagamento_id
data_pagamento
descricao_pagamento
valor_pagamento
classe_pagamento_operacional
subclasse_pagamento_operacional
estrategia_recomendada
lote_recomendado
lote_reserva
necessidade_switching
data_sugerida_switching
lote_origem_switching
produto_destino_switching
ganho_liquido_estimado_switching
cobertura_esperada
cobertura_integral_recomendada
lote_central_referencia
lote_reserva_referencia
score_central_referencia
tipo_fonte_recomendada
fonte_reserva_id
materialidade_minima_switching
valor_residual_temporal_lote
fracao_residual_temporal_lote
consumo_residual_temporal_estimado
saldo_residual_temporal_pos_recomendacao
fallback_automatico_sem_switching
motivo_fallback_automatico
motivo_recomendacao
```

Estratégias possíveis:

```text
sem_switching
switching_simples
combinacao_minima
```

Interpretação:

```text
O quadro_recomendacoes é a fonte mais direta para decisão operacional por pagamento, pois contém estrategia_recomendada, lote_recomendado, necessidade_switching, cobertura_esperada e campos de saldo residual temporal.
```

---

## 5. Contrato da recomputação sequencial central

Arquivo de origem:

```text
nucleo/recomputacao_sequencial_central_v1.py
```

Pacote principal:

```text
PacoteRecomputacaoSequencialCentralV1
  - quadro_recomputacao_sequencial_central
  - auditoria
```

Campos centrais relevantes para saída operacional:

```text
pagamento_id
data_pagamento
descricao_pagamento
valor_pagamento
classe_pagamento_operacional
subclasse_pagamento_operacional
lote_sugerido_original
lote_final_central
fonte_final_id
tipo_fonte_final
mudou_vs_decisao_local
criterio_central
status_central
score_proxy_central
saldo_antes_central
bruto_central
imposto_central
liquido_central
saldo_remanescente_central
pagamento_totalmente_coberto_central
observacao_central
```

Interpretação:

```text
A recomputação central é a fonte mais direta para valores financeiros exibidos no extrato futuro quando mapa_central está disponível, especialmente Saldo Antes, Bruto, Imposto, Líquido, Saldo Remanescente e Lote sugerido.
```

---

## 6. Contrato do extrato_futuro da saída canônica

Arquivo de origem:

```text
nucleo/saida_canonica.py
```

Campos observados em cada linha do `extrato_futuro`:

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

A planilha operacional consome esses mesmos campos para a aba `Extrato Futuro`:

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

---

## 7. Mapeamento comparativo de origem dos campos

```text
Campo extrato_futuro: Data
Origem observada: quadro preferencial, geralmente motor quando existente
Campo motor: data_pagamento
Campo central: data_pagamento
Origem: comum/compatível
Risco: baixo
```

```text
Campo extrato_futuro: Conta
Origem observada: quadro preferencial, geralmente motor quando existente
Campo motor: descricao_pagamento
Campo central: descricao_pagamento
Origem: comum/compatível
Risco: baixo
```

```text
Campo extrato_futuro: Despesa ID
Origem observada: quadro preferencial, geralmente motor quando existente
Campo motor: pagamento_id
Campo central: pagamento_id
Origem: comum/compatível
Risco: baixo
```

```text
Campo extrato_futuro: Valor
Origem observada: quadro preferencial, geralmente motor quando existente
Campo motor: valor_pagamento
Campo central: valor_pagamento
Origem: comum/compatível
Risco: baixo
```

```text
Campo extrato_futuro: Lote sugerido
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro; mapa_resumos depois; decisao_row como fallback
Campo motor: lote_recomendado
Campo central: lote_final_central ou lote_sugerido_original
Origem: central quando disponível
Risco: alto
```

```text
Campo extrato_futuro: Saldo Antes
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro
Campo motor: não é o campo financeiro final primário; possui cobertura_esperada e saldo residual temporal
Campo central: saldo_antes_central
Origem: central quando disponível
Risco: moderado
```

```text
Campo extrato_futuro: Bruto
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro
Campo central: bruto_central
Origem: central quando disponível
Risco: moderado
```

```text
Campo extrato_futuro: Imposto
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro
Campo central: imposto_central
Origem: central quando disponível
Risco: moderado
```

```text
Campo extrato_futuro: Líquido
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro
Campo motor: cobertura_esperada
Campo central: liquido_central
Origem: central quando disponível
Risco: alto se comparado à cobertura_esperada do motor sem explicitar diferença
```

```text
Campo extrato_futuro: Saldo Remanescente
Origem observada: _resumo_futuro
Precedência atual: mapa_central primeiro
Campo motor: saldo_residual_temporal_pos_recomendacao
Campo central: saldo_remanescente_central
Origem: central quando disponível
Risco: alto se o usuário interpretar como saldo do lote recomendado pelo motor
```

```text
Campo extrato_futuro: Cobertura integral
Origem observada: calculado na saída a partir de Líquido exibido versus Valor
Campo motor: cobertura_integral_recomendada
Campo central: pagamento_totalmente_coberto_central
Origem: derivada do líquido exibido, que tende a ser central
Risco: alto se divergir de cobertura_integral_recomendada
```

```text
Campo extrato_futuro: Estratégia
Origem observada: quadro preferencial
Campo motor: estrategia_recomendada
Campo central: não há estratégia equivalente direta
Origem: motor quando motor existe
Risco: alto por coexistir com Lote sugerido central
```

```text
Campo extrato_futuro: Lote reserva
Origem observada: quadro preferencial
Campo motor: lote_reserva
Campo central: não há campo equivalente direto
Origem: motor quando motor existe
Risco: médio
```

```text
Campo extrato_futuro: Necessita switching
Origem observada: bool(row.get('necessita_switching')) ou estrategia_recomendada == 'switching_simples'
Campo motor existente: necessidade_switching
Campo esperado pela saída: necessita_switching
Origem: parcialmente derivada de estratégia; há divergência nominal entre necessidade_switching e necessita_switching
Risco: alto para casos em que a estratégia não capture toda a semântica de necessidade de switching
```

---

## 8. Campos com origem exclusivamente ou predominantemente no motor

```text
- Estratégia
- Lote reserva
- Necessita switching, indiretamente por estrategia_recomendada == switching_simples
- Motivo da recomendação, embora não exposto atualmente no extrato futuro
- Ganho líquido estimado de switching, embora não exposto atualmente no extrato futuro
- Data sugerida de switching, embora não exposta atualmente no extrato futuro
- Produto destino switching, embora não exposto atualmente no extrato futuro
- Saldo residual temporal do lote, embora não exposto atualmente no extrato futuro
- Fallback automático sem switching, embora não exposto atualmente no extrato futuro
```

Diagnóstico:

```text
A saída operacional exibe apenas parte do contrato do motor. Campos que explicariam a recomendação de switching não aparecem no extrato futuro principal.
```

---

## 9. Campos com origem exclusivamente ou predominantemente central

```text
- Lote sugerido quando mapa_central existe
- Saldo Antes
- Bruto
- Imposto
- Líquido
- Saldo Remanescente
- Cobertura integral, por ser derivada do líquido exibido
```

Diagnóstico:

```text
Os campos financeiros centrais dominam a exibição operacional quando há mapa_central, mesmo que a linha venha do quadro preferencial do motor.
```

---

## 10. Campos com origem mista ou ambígua

```text
Campo: Lote sugerido
Origem mista: motor em mapa_resumos/fallback, central quando mapa_central existe
Risco: alto
```

```text
Campo: Cobertura integral
Origem mista: motor possui cobertura_integral_recomendada, central possui pagamento_totalmente_coberto_central, saída calcula a partir do líquido exibido
Risco: alto
```

```text
Campo: Saldo Remanescente
Origem mista: motor possui saldo_residual_temporal_pos_recomendacao, central possui saldo_remanescente_central
Risco: alto
```

```text
Campo: Necessita switching
Origem mista/ambígua: motor possui necessidade_switching, saída procura necessita_switching e usa fallback por estratégia
Risco: alto
```

```text
Campo: Estratégia + Lote sugerido
Origem cruzada: estratégia do motor combinada com lote sugerido possivelmente central
Risco: muito alto
```

---

## 11. Divergências potenciais identificadas

### 11.1 Divergência de lote sugerido

```text
POTENCIAL_DIVERGENCIA:
lote_recomendado do motor pode divergir de lote_final_central usado em Lote sugerido.
```

```text
RISCO:
Usuário pode seguir um lote sugerido central enquanto a estratégia exibida descreve recomendação do motor.
```

```text
PRIORIDADE: MUITO_ALTA
```

### 11.2 Divergência de cobertura

```text
POTENCIAL_DIVERGENCIA:
cobertura_esperada/cobertura_integral_recomendada do motor pode divergir de liquido_central/pagamento_totalmente_coberto_central.
```

```text
RISCO:
Extrato pode indicar cobertura integral com base no central, enquanto estratégia do motor sugere outra cobertura esperada.
```

```text
PRIORIDADE: ALTA
```

### 11.3 Divergência de saldo remanescente

```text
POTENCIAL_DIVERGENCIA:
saldo_residual_temporal_pos_recomendacao do motor pode divergir de saldo_remanescente_central.
```

```text
RISCO:
Saldo remanescente exibido pode não representar o saldo temporal do lote recomendado pelo motor.
```

```text
PRIORIDADE: ALTA
```

### 11.4 Divergência nominal de necessidade de switching

```text
POTENCIAL_DIVERGENCIA:
Motor produz necessidade_switching; saída consulta necessita_switching e usa estratégia == switching_simples como fallback.
```

```text
RISCO:
A flag pode funcionar apenas por estratégia, mas não por contrato nominal de campo. Isso fragiliza manutenção e auditoria.
```

```text
PRIORIDADE: ALTA
```

### 11.5 Campos explicativos ausentes no extrato futuro

```text
POTENCIAL_DIVERGENCIA:
Ganho estimado de switching, data sugerida, destino de switching, motivo de recomendação e fallback automático não aparecem no extrato futuro principal.
```

```text
RISCO:
O usuário recebe a decisão sem justificativa suficiente para validar operacionalmente o switching.
```

```text
PRIORIDADE: MEDIA_ALTA
```

---

## 12. Fonte de verdade operacional atual

```text
FONTE_DE_VERDADE_OPERACIONAL_ATUAL: NAO_CONSOLIDADA
```

Diagnóstico:

```text
O contrato atual não define explicitamente se a fonte de verdade operacional do extrato futuro deve ser:
1. recomputação central;
2. motor de recomendação pagamentos + switching;
3. saída canônica como composição híbrida;
4. central para valores financeiros e motor para estratégia, desde que isso seja explicitamente rotulado.
```

Estado recomendado:

```text
Antes de qualquer ajuste em saida_canonica.py, o projeto deve medir empiricamente as divergências entre motor, central e extrato futuro em uma auditoria executável controlada.
```

---

## 13. Classificação consolidada dos achados

```text
ACHADO_01_LOTE_SUGERIDO_COM_ORIGEM_CENTRAL:
RISCO: ALTO
PRIORIDADE: MUITO_ALTA
ACAO_RECOMENDADA: medir divergência entre lote_recomendado e lote_final_central

ACHADO_02_ESTRATEGIA_DO_MOTOR_COM_FINANCEIRO_CENTRAL:
RISCO: ALTO
PRIORIDADE: MUITO_ALTA
ACAO_RECOMENDADA: auditar linhas em que estrategia_recomendada não corresponde ao lote exibido

ACHADO_03_FLAG_NECESSITA_SWITCHING_COM_NOME_DIVERGENTE:
RISCO: ALTO
PRIORIDADE: ALTA
ACAO_RECOMENDADA: quantificar impacto do mismatch necessidade_switching versus necessita_switching

ACHADO_04_COBERTURA_INTEGRAL_DERIVADA_DO_LIQUIDO_CENTRAL:
RISCO: ALTO
PRIORIDADE: ALTA
ACAO_RECOMENDADA: comparar cobertura_integral_recomendada versus cobertura integral exibida

ACHADO_05_SALDO_REMANESCENTE_COM_ORIGEM_CENTRAL:
RISCO: ALTO
PRIORIDADE: ALTA
ACAO_RECOMENDADA: comparar saldo_residual_temporal_pos_recomendacao versus saldo_remanescente_central

ACHADO_06_CAMPOS_EXPLICATIVOS_DE_SWITCHING_AUSENTES:
RISCO: MODERADO
PRIORIDADE: MEDIA_ALTA
ACAO_RECOMENDADA: avaliar se extrato futuro deve expor ganho, destino, data sugerida e motivo
```

---

## 14. Decisão sobre próxima frente

A ME-V239 avaliou três possibilidades:

```text
OPCAO_A: auditoria executável controlada
STATUS: RECOMENDADA
JUSTIFICATIVA: mede divergências reais antes de alterar saída ou contrato

OPCAO_B: ajuste direto de saída
STATUS: NAO_RECOMENDADA_AGORA
JUSTIFICATIVA: risco de trocar fonte de verdade sem medir impacto

OPCAO_C: formalização abstrata de contrato de precedência
STATUS: UTIL, MAS PREMATURA COMO PROXIMA ACAO ISOLADA
JUSTIFICATIVA: deve ser orientada por evidência empírica das divergências reais
```

Decisão diagnóstica:

```text
PROXIMA_FRENTE_DEVE_SER: AUDITORIA_EXECUTAVEL_CONTROLADA
MOTIVO: quantificar divergências campo a campo antes de qualquer alteração em saida_canonica.py, motor ou contrato de precedência.
```

---

## 15. Recomendação única de próxima microetapa

```text
PROXIMA_MICROETAPA_RECOMENDADA: ME-V240
NOME_RECOMENDADO: Auditoria executável das divergências motor versus central versus extrato futuro
TIPO_RECOMENDADO: DIAGNOSTICO / AUDITORIA
CLASSE_RECOMENDADA: AUDITA_DIVERGENCIAS_SAIDA_PAGAMENTOS_SWITCHING_SEM_ALTERAR_REGRA
STATUS: RECOMENDACAO_APENAS
IMPLEMENTACAO_INICIADA: NAO
```

Objetivo recomendado para a ME-V240:

```text
Criar e executar uma auditoria diagnóstica controlada que compare, pagamento a pagamento, os campos do quadro_recomendacoes do motor, do quadro_recomputacao_sequencial_central e do extrato_futuro da saída canônica, quantificando divergências de lote sugerido, estratégia, cobertura, saldo remanescente e necessidade de switching, sem alterar motor, sem alterar saída canônica, sem alterar dados financeiros e sem promover mudança econômica.
```

Escopo recomendado inicial:

```text
- criar script diagnóstico específico de auditoria comparativa;
- executar apenas esse script diagnóstico aprovado;
- gerar CSV/MD diagnóstico em saidas/diagnostico ou relatorios/diagnostico, conforme padrão do projeto;
- comparar lote_recomendado versus lote_final_central versus Lote sugerido do extrato futuro;
- comparar cobertura_integral_recomendada versus pagamento_totalmente_coberto_central versus Cobertura integral exibida;
- comparar saldo_residual_temporal_pos_recomendacao versus saldo_remanescente_central versus Saldo Remanescente exibido;
- comparar necessidade_switching versus Necessita switching exibido;
- não alterar motor;
- não alterar saida_canonica;
- não alterar planilha operacional;
- não alterar dados;
- não acionar Codex antes da auditoria preventiva.
```

A ME-V240 não é iniciada por este documento.

---

## 16. Registros de não execução e não alteração

```text
CONTRATO_MESTRE: NAO_ALTERADO
MMEF_OFICIAL: NAO_ALTERADO
FRAMEWORK: NAO_ALTERADO
CHECKLIST_V234: NAO_ALTERADO
TEMPLATE_ITERACAO: NAO_ALTERADO
PROMPTS: NAO_ALTERADOS
REGISTROS_ANTERIORES_V226_V238: NAO_ALTERADOS
README: NAO_ALTERADO
INDICE_RELATORIOS: NAO_ALTERADO
RELATORIOS_ATUAIS: NAO_ALTERADOS
RELATORIOS_HISTORICOS: NAO_ALTERADOS
RELEASE_CHECKER: NAO_ALTERADO
RELEASE_CHECKER_EXECUTADO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUTADO: NAO
SCRIPT_DIAGNOSTICO_EXECUTADO: NAO
SCRIPT_OPERACIONAL_EXECUTADO: NAO
SCRIPT_NOVO_CRIADO: NAO
FUNCAO_NOVA_CRIADA: NAO
SCRIPTS: NAO_ALTERADOS
CODIGO_ECONOMICO: NAO_ALTERADO
MOTOR_DE_PAGAMENTOS: NAO_ALTERADO
MOTOR_DE_SWITCHING: NAO_ALTERADO
SIMULADOR_CENTRAL: NAO_ALTERADO
SAIDA_CANONICA: NAO_ALTERADA
PLANILHA_OPERACIONAL: NAO_ALTERADA
DADOS_FINANCEIROS: NAO_ALTERADOS
CACHE_BCB_CDI: NAO_ALTERADO
SAIDAS_OFICIAIS: NAO_ALTERADAS
PLANILHAS_DE_DADOS: NAO_ALTERADAS
ARQUIVOS_DE_RESULTADO: NAO_ALTERADOS
SIMULACAO_ECONOMICA_EXECUTADA: NAO
CODEX: NAO_ACIONADO
V184: NAO_USADA_COMO_VERSAO_OFICIAL
IMPLEMENTACAO_TECNICA_INICIADA: NAO
CORRECAO_TECNICA_EXECUTADA: NAO
REFATORACAO_EXECUTADA: NAO
```

---

## 17. Estado final da ME-V239

```text
AUDITORIA_CONTRATO_SAIDA_PAGAMENTOS_SWITCHING: CONCLUIDA
FONTE_DE_VERDADE_OPERACIONAL_ATUAL: NAO_CONSOLIDADA
CAMPOS_COM_ORIGEM_MISTA: IDENTIFICADOS
DIVERGENCIAS_POTENCIAIS: IDENTIFICADAS_SEM_EXECUCAO
PROXIMA_FRENTE_RECOMENDADA: AUDITORIA_EXECUTAVEL_CONTROLADA
PROXIMA_MICROETAPA_RECOMENDADA: ME-V240
VERSAO_CANDIDATA_ATUAL: V239
PROMOCAO_V239: NAO_REALIZADA
AUDITORIA_POS_IMPLEMENTACAO_DA_ME_V239: PENDENTE
```

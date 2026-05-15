# ME-V17-F0-T8 — Contrato intradiário de recebidos

## Identificação

- MICROETAPA: V17-F0-T.8
- TIPO: DOCUMENTAL / CONTRATO INTRADIÁRIO LOCAL
- BASELINE_DE_ENTRADA: 8d0a48e
- T7_CONGELADA: sim
- T6_CONGELADA: sim
- T5_CONGELADA: sim
- T4_CONGELADA: sim
- T3_CONGELADA: sim
- T2_CONGELADA: sim
- T1_CONGELADA: sim
- T0_CONGELADA: sim
- S7_CONGELADA: sim
- Q_REABERTA: não

## Objetivo

Formalizar, em caráter documental e local à frente T, a regra de precedência intradiária para recebidos futuros usados em diagnósticos de cobertura.

Esta microetapa não altera motor econômico, recomendador, XLSX oficial, fonte oficial dos pagamentos, status operacional, dados, cache, contrato mestre ou modelo oficial.

## Escopo

Arquivo versionável desta microetapa:

- logs/iteracoes/ME-V17-F0-T8_CONTRATO_INTRADIARIO_RECEBIDOS.md

Nenhum script deve ser criado nesta microetapa.

Nenhum artefato em `saidas/`, `dados/`, cache ou XLSX oficial deve ser versionado.

## Base empírica

A T.7 auditou os consumos de recebidos na mesma data do pagamento, com os seguintes resultados:

- qtd_pagamentos_same_day_t7: 5
- qtd_componentes_same_day_t7: 5
- valor_consumo_same_day_t7: 7229.18
- qtd_pagamentos_same_day_fonte_oficial_lote_t7: 2
- qtd_pagamentos_same_day_bloqueio_intradiario_t7: 3
- qtd_pagamentos_same_day_bloqueio_competitivo_t7: 0
- qtd_pagamentos_same_day_candidato_diagnostico_t7: 0
- qtd_pagamentos_same_day_classe_desconhecida_t7: 0
- qtd_inconsistencia_taxonomica_t7: 0
- qtd_pode_promover_recebido_pos_t7_sim: 0
- qtd_pode_converter_recebido_t5_sim_em_same_day_t7: 0
- status_geral_t7: auditoria_precedencia_intradiaria_recebidos_gerada

## Contrato intradiário local

### RIT-1 — Materialização temporal explícita

Um recebido só pode ser considerado fonte disponível para pagamento se estiver materializado antes do evento de pagamento.

Quando recebido e pagamento possuem a mesma data civil, a data isolada não é suficiente para provar disponibilidade operacional.

### RIT-2 — Bloqueio conservador de recebidos same-day

Na ausência de informação intradiária explícita, todo pagamento que dependa de recebido na mesma data deve permanecer bloqueado para promoção operacional.

Esse bloqueio não impede uso diagnóstico, mas impede transformar o recebido em fonte oficial.

### RIT-3 — Fonte oficial por lote prevalece

Se um pagamento já possui fonte oficial definida por lote, qualquer consumo de recebido same-day observado em ledger diagnóstico é apenas contrafactual.

Nesses casos, a fonte oficial por lote deve ser preservada.

### RIT-4 — Same-day não pode criar candidato automático

Um pagamento que dependa de recebido na mesma data não pode ser promovido automaticamente à classe de candidato operacional.

Para promoção futura, será necessário um contrato intradiário executável, com ordem de eventos ou timestamps auditáveis.

### RIT-5 — Separação entre diagnóstico e decisão operacional

A existência de saldo diagnóstico por recebidos não altera:

- lote recomendado;
- fonte principal;
- fonte reserva;
- status operacional;
- ação recomendada;
- XLSX oficial;
- recomendador;
- motor econômico.

### RIT-6 — Condição mínima para promoção futura

Antes de qualquer promoção futura de recebidos como fonte oficial, devem existir, no mínimo:

1. ledger oficial de recebidos;
2. regra explícita de precedência intradiária;
3. ordem auditável entre recebimento e pagamento;
4. preservação da prioridade das fontes oficiais já aprovadas;
5. reconciliação concorrente com todos os pagamentos do dia;
6. bloqueio automático quando a disponibilidade intradiária não for demonstrável.

## Classificação normativa dos 5 casos same-day

Com base na T.7:

- 2 pagamentos permanecem com fonte oficial por lote.
- 3 pagamentos permanecem bloqueados por dependência intradiária.
- 0 pagamentos podem ser promovidos para uso oficial de recebidos.
- 0 pagamentos same-day são candidatos diagnósticos livres.
- 0 inconsistências taxonômicas foram observadas.

## Decisão documental

- T8_CONTRATO_INTRADIARIO_RECEBIDOS_FORMALIZADO: sim
- RECEBIDO_SAME_DAY_PROMOVIDO_A_FONTE_OFICIAL: não
- FONTE_OFICIAL_LOTE_PRESERVADA: sim
- PAGAMENTOS_SAME_DAY_SEM_REGRA_INTRADIARIA_BLOQUEADOS: sim
- ALTERA_MOTOR: não
- ALTERA_RECOMENDADOR: não
- ALTERA_XLSX_OFICIAL: não
- ALTERA_DADOS_CACHE: não
- ALTERA_CONTRATO_MESTRE: não
- ALTERA_MODELO_OFICIAL: não
- Q_REABERTA: não
- S7_REABERTA: não
- T0_REABERTA: não
- T1_REABERTA: não
- T2_REABERTA: não
- T3_REABERTA: não
- T4_REABERTA: não
- T5_REABERTA: não
- T6_REABERTA: não
- T7_REABERTA: não
- PROXIMA_ETAPA_LIBERADA: T9_MAPEAR_IMPACTO_DO_CONTRATO_INTRADIARIO_NOS_94_CANDIDATOS_DIAGNOSTICOS_SEM_ALTERAR_RECOMENDADOR

## Limite explícito

A T.8 não implementa regra intradiária executável. Ela apenas formaliza o contrato local que deverá orientar etapas futuras.

Qualquer uso operacional de recebidos como fonte oficial continua bloqueado até criação e validação de um mecanismo executável específico.

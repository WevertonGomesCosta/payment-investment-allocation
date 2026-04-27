# ME-V238 — Auditoria diagnóstica da integração pagamentos + switching

```text
STATUS_DO_REGISTRO: AUDITORIA_DIAGNOSTICA_CONTROLADA_READ_ONLY
MICROETAPA: ME-V238
VERSAO_CANDIDATA: V238
BASELINE_DE_ENTRADA: V237
TIPO: DIAGNOSTICO / AUDITORIA
CLASSE_SEMANTICA_MMEF: AUDITA_INTEGRACAO_PAGAMENTOS_SWITCHING_SEM_ALTERAR_REGRA
```

---

## 1. Estado pós-V237

```text
ESTADO_POS_V237: CARREGADO
V237: DIAGNOSTICO_DE_RETOMADA_TECNICA_POS_FRAMEWORK
FRENTE_PRIORIZADA_V237: INTEGRACAO_PAGAMENTOS_SWITCHING
ME_V238: AUDITORIA_DIAGNOSTICA_DA_INTEGRACAO_PAGAMENTOS_SWITCHING
```

A ME-V238 foi executada em modo read-only.

Nenhum arquivo existente foi alterado.

Nenhum script foi executado.

Nenhuma simulação econômica foi executada.

Nenhuma implementação técnica foi iniciada.

---

## 2. Arquivos inspecionados em modo read-only

Foram inspecionados, sem edição, os seguintes arquivos e documentos:

```text
nucleo/motor_recomendacao_pagamentos_switching_v1.py
nucleo/alocador_pagamentos_terminal_v1.py
nucleo/simulador_central_eventos_v1.py
nucleo/saida_canonica.py
nucleo/aportes_futuros_planejados.py
nucleo/fiscal_lotes.py
nucleo/calendario_financeiro.py
nucleo/contexto_baseline.py
scripts/operacional/gerar_planilha_operacional.py
relatorios/atuais/BASELINE_FUNCIONAL_ESTAVEL_V225.md
relatorios/atuais/GATE_ECONOMICO_APORTES_PLANEJADOS_V220.md
relatorios/historico/auditorias_especificas/temporal/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md
```

Também foram feitas buscas read-only por nomes e responsabilidades aparentes dos módulos relacionados.

---

## 3. Linha funcional observada da integração

A linha funcional observada é:

```text
carregar_contexto_baseline
  -> dados_operacionais / fontes_elegiveis_pagamento / saldo_disponivel_geral
  -> decisao_local_v1
  -> recomputacao_sequencial_central_v1
  -> switching_economico_shadow
  -> motor_recomendacao_pagamentos_switching_v1
  -> saida_canonica
  -> gerar_planilha_operacional
```

Interpretação:

```text
A integração existe, mas é composta por camadas com responsabilidades diferentes:
- a recomputação central define uma referência sequencial sem necessariamente promover switching como decisão final;
- o motor de recomendação avalia estratégias por pagamento;
- a saída canônica materializa o extrato futuro e pode mesclar recomendação do motor com resumo financeiro central;
- a planilha operacional consome a saída canônica.
```

---

## 4. Motor de recomendação pagamentos + switching

Arquivo:

```text
nucleo/motor_recomendacao_pagamentos_switching_v1.py
```

Entradas funcionais observadas:

```text
dados_operacionais
fontes_elegiveis_pagamento
saldo_disponivel_geral
decisao_local_v1
recomputacao_sequencial_central_v1
switching_economico_shadow
data_referencia
```

Saídas principais observadas:

```text
PacoteMotorRecomendacaoPagamentosSwitchingV1
  - quadro_recomendacoes
  - auditoria
```

Campos relevantes em `quadro_recomendacoes`:

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
score_central_referencia
tipo_fonte_recomendada
materialidade_minima_switching
valor_residual_temporal_lote
fracao_residual_temporal_lote
consumo_residual_temporal_estimado
saldo_residual_temporal_pos_recomendacao
fallback_automatico_sem_switching
motivo_fallback_automatico
motivo_recomendacao
```

Estratégias comparadas:

```text
sem_switching
switching_simples
combinacao_minima
```

Diagnóstico:

```text
O motor já responde diretamente à pergunta operacional "qual lote/fonte usar por pagamento" considerando switching simples e combinação mínima. Também preserva referência central, saldo residual temporal e fallback automático para sem_switching.
```

Risco principal:

```text
O motor opera como recomendador por pagamento. A reconciliação com cenário conjunto final e com recomputação central ainda precisa ser auditada antes de promover qualquer alteração operacional.
```

---

## 5. Alocador de pagamentos terminal

Arquivo:

```text
nucleo/alocador_pagamentos_terminal_v1.py
```

Responsabilidade observada:

```text
Comparar fontes candidatas para um pagamento sob score terminal e heurísticas auxiliares, incluindo:
- saldo_disponivel;
- lote_nao_aportado;
- lote_aportado;
- combinacao_minima_fontes;
- cenario_switching_elegivel;
- sem_fonte_viavel.
```

Diagnóstico:

```text
O alocador é mais estrutural e econômico, enquanto o motor_recomendacao_pagamentos_switching_v1 atua como camada operacional de recomendação por pagamento. Há sobreposição conceitual em combinação mínima e cenário de switching, mas com funções distintas.
```

Achado:

```text
Há risco de divergência entre a recomendação operacional do motor e a decisão terminal do alocador se as duas camadas forem interpretadas como fonte única de verdade sem reconciliação explícita.
```

Classificação:

```text
RISCO: MODERADO
PRIORIDADE: ALTA
```

---

## 6. Simulador central de eventos

Arquivo:

```text
nucleo/simulador_central_eventos_v1.py
```

Responsabilidade observada:

```text
Construir estado global de recorte, planejar/aplicar eventos de switching, ativar recebidos futuros, normalizar pós-vencimento, executar eventos e avaliar cenários conjuntos.
```

Relação com pagamentos + switching:

```text
O simulador central usa alocar_pagamento_terminal_v1 e componentes de planejamento/avaliação de cenários. Ele modela a evolução temporal do estado, enquanto o motor de recomendação transforma resultados e sombras em recomendação operacional por pagamento.
```

Achado:

```text
A conexão entre recomendação local por pagamento e cenário conjunto final não deve ser assumida como resolvida apenas pela existência do motor. A V116 já havia registrado que a reconexão com cenário conjunto final permanecia pendente.
```

Classificação:

```text
RISCO: MODERADO_ALTO
PRIORIDADE: ALTA
```

---

## 7. Saída canônica e planilha operacional

Arquivos:

```text
nucleo/saida_canonica.py
scripts/operacional/gerar_planilha_operacional.py
```

Achado na saída canônica:

```text
_quadro_futuro_preferencial prioriza motor_recomendacao_pagamentos_switching_v1 quando existe.
```

Porém, no resumo futuro:

```text
_resumo_futuro usa primeiro mapa_central quando existe, retornando Lote sugerido e campos financeiros centrais.
```

Efeito provável:

```text
A linha do extrato futuro pode carregar estratégia do motor de recomendação e, simultaneamente, resumo financeiro/lote sugerido derivado da recomputação central.
```

Diagnóstico:

```text
Essa composição pode ser intencional como fallback/ancoragem central, mas precisa de auditoria específica porque pode ocultar divergência entre:
- lote recomendado pelo motor;
- lote final central;
- cobertura financeira exibida;
- indicação de necessidade de switching.
```

A planilha operacional consome `construir_saida_canonica` e materializa abas como Extrato Futuro e Switching.

Classificação:

```text
RISCO: ALTO PARA INTERPRETACAO OPERACIONAL
PRIORIDADE: MUITO_ALTA
```

---

## 8. Aportes planejados e gate econômico

Arquivo:

```text
nucleo/aportes_futuros_planejados.py
```

Relatório relacionado:

```text
relatorios/atuais/GATE_ECONOMICO_APORTES_PLANEJADOS_V220.md
```

Diagnóstico:

```text
O gate econômico de aportes planejados permanece regra de segurança separada. Ele bloqueia aportes planejados quando reduzem patrimônio terminal proxy, aumentam perda terminal total, aumentam penalidade estratégica total ou aumentam déficit total.
```

Relação com ME-V238:

```text
A auditoria de pagamentos + switching deve preservar o gate V225/V220 e não reabrir aportes planejados como primeira correção. Qualquer recombinação futura entre switching, pagamentos e aportes planejados exige microetapa própria e simulação posterior.
```

Classificação:

```text
RISCO: BAIXO SE PRESERVADO
RISCO: ALTO SE REABERTO SEM SIMULACAO
PRIORIDADE_IMEDIATA: PRESERVAR COMO TRAVA
```

---

## 9. Fiscalidade e calendário

Arquivos:

```text
nucleo/fiscal_lotes.py
nucleo/calendario_financeiro.py
```

Diagnóstico:

```text
A idade fiscal e a contagem de dias/rendimento estão centralizadas em módulos específicos. A V225 já consolidou esses pontos como estáveis.
```

Relação com ME-V238:

```text
A auditoria da integração pagamentos + switching não deve reabrir cálculo fiscal, dias corridos, dias úteis ou rendimento. Esses módulos devem ser tratados como dependências preservadas.
```

Classificação:

```text
RISCO: BAIXO SE PRESERVADO
PRIORIDADE_IMEDIATA: NAO_REABRIR
```

---

## 10. Auditoria histórica V116

Arquivo:

```text
relatorios/historico/auditorias_especificas/temporal/AUDITORIA_COMPARADOR_MOTOR_RECOMENDACAO_V116.md
```

Pontos relevantes:

```text
- A V115 inflava switching_simples por reaproveitar o mesmo lote em muitos pagamentos futuros.
- A V116 introduziu saldo residual temporal por lote.
- O ganho shadow passou a ser escalado pela fração residual temporal.
- O motor passou a registrar consumo temporal estimado.
- Quando o lote deixa de sustentar o pagamento, há fallback automático para sem_switching.
- switching_simples caiu de 137 para 56.
- sem_switching aumentou de 15 para 96.
- A V116 não resolveu a reconexão com o cenário conjunto final.
```

Diagnóstico:

```text
A principal pendência técnica não é simplesmente reduzir switching_simples novamente. A pendência é reconciliar a recomendação por pagamento, o saldo residual temporal e o cenário conjunto final observável nas saídas.
```

Classificação:

```text
RISCO: MODERADO_ALTO
PRIORIDADE: MUITO_ALTA
```

---

## 11. Lacunas de integração identificadas

### 11.1 Fonte de verdade operacional

```text
ACHADO:
Existem pelo menos três referências possíveis para a decisão futura:
- recomendação do motor_recomendacao_pagamentos_switching_v1;
- recomputação sequencial central;
- saída canônica/planilha operacional.
```

```text
RISCO:
Usuário pode interpretar lote sugerido, estratégia e cobertura como uma única decisão coesa, embora venham de camadas parcialmente distintas.
```

```text
PRIORIDADE: MUITO_ALTA
```

### 11.2 Recomendação local versus cenário conjunto final

```text
ACHADO:
O motor recomenda por pagamento, com controle temporal residual, mas a reconexão com cenário conjunto final permanece pendência histórica documentada desde V116.
```

```text
RISCO:
Uma recomendação local pode ser operacionalmente útil, mas não necessariamente ótima ou consistente no horizonte conjunto completo.
```

```text
PRIORIDADE: MUITO_ALTA
```

### 11.3 Mescla de motor e recomputação central na saída

```text
ACHADO:
A saída canônica prioriza quadro do motor para extrato futuro, mas usa mapa central para resumo financeiro quando disponível.
```

```text
RISCO:
O lote sugerido ou os valores financeiros exibidos podem refletir a recomputação central, enquanto a estratégia exibida vem do motor de recomendação.
```

```text
PRIORIDADE: ALTA
```

### 11.4 Duplicação parcial de lógica de combinação mínima

```text
ACHADO:
Há lógica de combinacao_minima tanto no alocador terminal quanto no motor de recomendação.
```

```text
RISCO:
Critérios diferentes podem gerar decisões diferentes sob o mesmo pagamento se não houver contrato explícito de precedência.
```

```text
PRIORIDADE: ALTA
```

### 11.5 Gate econômico preservado, mas não revalidado nessa integração

```text
ACHADO:
O gate econômico V220/V225 permanece preservado para aportes planejados, mas a auditoria de integração pagamentos + switching ainda precisa explicitar se e onde o gate limita decisões futuras.
```

```text
RISCO:
Baixo no estado atual se o gate permanecer preservado; alto se for reaberto junto com switching sem simulação.
```

```text
PRIORIDADE: MEDIA
```

---

## 12. Pontos que exigem simulação posterior

A ME-V238 não executou simulação econômica, mas identificou pontos que exigirão simulação em microetapa futura:

```text
SIMULACAO_FUTURA_01:
Comparar extrato futuro central versus extrato futuro com motor de recomendação para pagamentos relevantes.

SIMULACAO_FUTURA_02:
Medir quantos pagamentos exibem divergência entre lote_recomendado do motor e lote_final_central.

SIMULACAO_FUTURA_03:
Medir impacto de adotar recomendação do motor como fonte operacional principal nas saídas.

SIMULACAO_FUTURA_04:
Testar se switching_simples recomendado preserva cobertura integral, saldo residual temporal e patrimônio terminal.

SIMULACAO_FUTURA_05:
Testar se combinação mínima do motor e combinação mínima do alocador geram decisões equivalentes ou divergentes.
```

Essas simulações não devem ser iniciadas sem microetapa própria.

---

## 13. Classificação consolidada dos achados

```text
ACHADO_01_FONTE_VERDADE_OPERACIONAL:
RISCO: ALTO
PRIORIDADE: MUITO_ALTA
ACAO: auditar divergência motor versus central versus saída

ACHADO_02_RECONEXAO_CENARIO_CONJUNTO:
RISCO: MODERADO_ALTO
PRIORIDADE: MUITO_ALTA
ACAO: mapear contrato entre recomendação local e cenário conjunto final

ACHADO_03_MESCLA_SAIDA_CANONICA:
RISCO: ALTO
PRIORIDADE: ALTA
ACAO: criar auditoria comparativa de campos do extrato futuro

ACHADO_04_DUPLICACAO_COMBINACAO_MINIMA:
RISCO: MODERADO
PRIORIDADE: ALTA
ACAO: comparar regras do alocador e do motor

ACHADO_05_GATE_ECONOMICO:
RISCO: BAIXO_SE_PRESERVADO
PRIORIDADE: MEDIA
ACAO: manter gate preservado; não reabrir nesta frente
```

---

## 14. Decisão diagnóstica da ME-V238

```text
INTEGRACAO_PAGAMENTOS_SWITCHING: EXISTE_PARCIALMENTE
ESTADO: AUDITAVEL_MAS_NAO_PRONTO_PARA_PROMOCAO_DIRETA
PRINCIPAL_LACUNA: contrato de precedência/fonte de verdade entre motor, recomputação central e saída canônica
IMPLEMENTACAO_DIRETA: NAO_RECOMENDADA
SIMULACAO_IMEDIATA: NAO_EXECUTADA
```

A próxima etapa deve continuar diagnóstica, mas já pode ser mais específica: comparar o contrato de campos entre motor de recomendação, recomputação central e saída canônica, sem alterar código.

---

## 15. Recomendação única de próxima microetapa

```text
PROXIMA_MICROETAPA_RECOMENDADA: ME-V239
NOME_RECOMENDADO: Auditoria comparativa do contrato de saída pagamentos + switching
TIPO_RECOMENDADO: DIAGNOSTICO / AUDITORIA
CLASSE_RECOMENDADA: AUDITA_CONTRATO_SAIDA_PAGAMENTOS_SWITCHING_SEM_ALTERAR_REGRA
STATUS: RECOMENDACAO_APENAS
IMPLEMENTACAO_INICIADA: NAO
```

Objetivo recomendado para a ME-V239:

```text
Auditar, em modo read-only, o contrato de campos entre quadro_recomendacoes do motor_recomendacao_pagamentos_switching_v1, quadro_recomputacao_sequencial_central e extrato_futuro da saída canônica, identificando divergências de lote sugerido, estratégia, cobertura, saldo remanescente, necessidade de switching e fonte de verdade operacional, sem alterar código, sem executar simulação econômica e sem acionar Codex.
```

Escopo recomendado inicial:

```text
- mapear campos do quadro_recomendacoes;
- mapear campos da recomputação central usados pela saída;
- mapear campos do extrato_futuro;
- identificar campos com origem mista;
- definir se a próxima frente deve ser auditoria executável, ajuste de saída ou contrato de precedência;
- não alterar código;
- não executar simulação econômica inicialmente;
- não acionar Codex.
```

A ME-V239 não é iniciada por este documento.

---

## 16. Registros de não execução e não alteração

```text
CONTRATO_MESTRE: NAO_ALTERADO
MMEF_OFICIAL: NAO_ALTERADO
FRAMEWORK: NAO_ALTERADO
CHECKLIST_V234: NAO_ALTERADO
TEMPLATE_ITERACAO: NAO_ALTERADO
PROMPTS: NAO_ALTERADOS
REGISTROS_ANTERIORES_V226_V237: NAO_ALTERADOS
README: NAO_ALTERADO
INDICE_RELATORIOS: NAO_ALTERADO
RELATORIOS_ATUAIS: NAO_ALTERADOS
RELATORIOS_HISTORICOS: NAO_ALTERADOS
RELEASE_CHECKER: NAO_ALTERADO
RELEASE_CHECKER_EXECUTADO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUTADO: NAO
SCRIPT_DIAGNOSTICO_EXECUTADO: NAO
SCRIPT_NOVO_CRIADO: NAO
SCRIPTS: NAO_ALTERADOS
CODIGO_ECONOMICO: NAO_ALTERADO
MOTOR_DE_PAGAMENTOS: NAO_ALTERADO
MOTOR_DE_SWITCHING: NAO_ALTERADO
SIMULADOR_CENTRAL: NAO_ALTERADO
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

## 17. Estado final da ME-V238

```text
AUDITORIA_INTEGRACAO_PAGAMENTOS_SWITCHING: CONCLUIDA
INTEGRACAO_EXISTENTE: PARCIAL
PRONTA_PARA_PROMOCAO_DIRETA: NAO
FONTE_VERDADE_OPERACIONAL: NAO_CONSOLIDADA
PROXIMA_MICROETAPA_RECOMENDADA: ME-V239
VERSAO_CANDIDATA_ATUAL: V238
PROMOCAO_V238: NAO_REALIZADA
AUDITORIA_POS_IMPLEMENTACAO_DA_ME_V238: PENDENTE
```

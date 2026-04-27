# ME-V240 — Auditoria executável das divergências motor versus central versus extrato futuro

## 1. Identificação da microetapa

```text
MICROETAPA: ME-V240
TITULO: Auditoria executável das divergências motor versus central versus extrato futuro
TIPO: DIAGNOSTICO / AUDITORIA EXECUTAVEL CONTROLADA
CLASSE SEMANTICA: AUDITA_DIVERGENCIA_EXECUTAVEL_SEM_CORRIGIR_REGRA
BASELINE DE ENTRADA: V239
VERSAO CANDIDATA: V240
DECISAO PREVENTIVA: APROVAR_COM_RESSALVAS
NATUREZA DA ENTREGA: FORMALIZACAO DOCUMENTAL DO PROTOCOLO DE AUDITORIA FUTURA
STATUS DA EXECUCAO COMPARATIVA: NAO REALIZADA
STATUS DE SCRIPT DIAGNOSTICO: NAO CRIADO
STATUS DE FONTE DE VERDADE OPERACIONAL: NAO_CONSOLIDADA
```

Esta microetapa formaliza apenas o desenho da auditoria executável futura. A ME-V240 não realiza comparação entre camadas, não cria script diagnóstico, não altera código, não altera regras econômicas e não define precedência entre componentes do sistema.

---

## 2. Estado herdado da V239

A V239 está consolidada como microetapa de diagnóstico/auditoria, com decisão final `CONSOLIDAR_V239`.

Estado herdado obrigatório:

```text
BASELINE_DIAGNOSTICA_CONSOLIDADA: V239
DECISAO_FINAL_V239: CONSOLIDAR_V239
FONTE_DE_VERDADE_OPERACIONAL_ATUAL: NAO_CONSOLIDADA
ME_V240_STATUS_ANTES_DESTA_FORMALIZACAO: NAO_INICIADA
```

A V239 identificou divergência potencial no contrato de saída entre recomendações do motor, recomputação sequencial central e campos exibidos no `extrato_futuro` da saída canônica.

A fonte de verdade operacional permanece `NAO_CONSOLIDADA`. A V240 não altera esse estado.

---

## 3. Achado principal herdado da V239

Achado principal registrado pela V239:

```text
O extrato_futuro pode combinar estrategia do motor com Lote sugerido e campos financeiros da recomputacao central.
```

Esse achado permanece classificado como hipótese diagnóstica e necessita execução futura controlada para produção de evidência observável.

A ME-V240 registra apenas o protocolo necessário para que a divergência potencial seja avaliada posteriormente, com separação explícita entre:

```text
1. campos candidatos oriundos do motor_recomendacao_pagamentos_switching_v1;
2. campos candidatos oriundos da recomputacao_sequencial_central_v1;
3. campos candidatos exibidos no extrato_futuro da saida canonica;
4. hipoteses de origem da mistura;
5. criterios de classificacao de divergencia potencial.
```

---

## 4. Objetivo da auditoria futura

A auditoria executável futura deverá comparar, em microetapa própria e previamente aprovada, campos emitidos ou refletidos por três camadas:

```text
CAMADA_1: motor_recomendacao_pagamentos_switching_v1
CAMADA_2: recomputacao_sequencial_central_v1
CAMADA_3: extrato_futuro da saida canonica
```

Objetivo técnico da auditoria futura:

```text
Identificar se ha evidencia observavel de divergencia potencial entre estrategia recomendada, lote sugerido, lote financeiro efetivamente usado, valores financeiros recomputados e campos exibidos no extrato_futuro.
```

A auditoria futura deverá produzir evidência rastreável, sem alterar comportamento econômico, sem corrigir divergência e sem definir precedência entre as camadas.

---

## 5. Escopo da ME-V240

Escopo único desta microetapa:

```text
Criar o arquivo documental:
logs/iteracoes/ME-V240_AUDITORIA_EXECUTAVEL_DIVERGENCIAS_MOTOR_CENTRAL_EXTRATO.md
```

Esta microetapa somente formaliza:

```text
- estado herdado da V239;
- achado principal da V239;
- manutencao da fonte de verdade operacional como NAO_CONSOLIDADA;
- campos candidatos a comparacao futura;
- evidencias minimas esperadas para execucao futura;
- criterios de aprovacao da futura auditoria executavel;
- criterios de bloqueio da futura auditoria executavel;
- declaracoes negativas de execucao, criacao de script, simulacao e correcao;
- recomendacao de proxima microetapa unica.
```

---

## 6. Fora do escopo da ME-V240

Estão fora do escopo desta microetapa:

```text
- criar script diagnostico;
- executar script diagnostico;
- executar script operacional;
- executar simulacao economica;
- executar release checker;
- executar verificar_release_limpo.py;
- alterar codigo economico;
- alterar motor de pagamentos;
- alterar motor de switching;
- alterar recomputacao_sequencial_central_v1;
- alterar simulador central;
- alterar saida canonica;
- alterar planilha operacional;
- alterar dados financeiros;
- alterar cache BCB/CDI;
- alterar saidas oficiais;
- alterar planilhas de dados;
- alterar arquivos de resultado;
- corrigir divergencia;
- definir fonte de verdade operacional;
- promover V240;
- iniciar microetapa tecnica subsequente;
- executar correcao tecnica;
- executar refatoracao.
```

---

## 7. Campos candidatos à comparação futura

Os campos abaixo são candidatos à comparação em auditoria futura. A lista não implica existência simultânea desses campos em todas as camadas; a futura auditoria deverá classificar ausências como `CAMPO_AUSENTE` ou `NAO_COMPARAVEL`, quando aplicável.

### 7.1. Identificação do pagamento ou evento

```text
- pagamento_id
- data_pagamento
- data_evento
- descricao_pagamento
- categoria_pagamento
- valor_pagamento
- status_pagamento
- chave_rastreavel_evento
```

### 7.2. Campos candidatos do motor_recomendacao_pagamentos_switching_v1

```text
- estrategia_recomendada
- lote_sugerido
- lote_reserva
- necessidade_switching
- data_sugerida_switching
- produto_origem_switching
- produto_destino_switching
- ganho_liquido_estimado
- valor_coberto_estimado
- status_recomendacao
- justificativa_recomendacao
```

### 7.3. Campos candidatos da recomputacao_sequencial_central_v1

```text
- origem_pagamento_recomputada
- lote_utilizado_recomputado
- saldo_antes_recomputado
- valor_bruto_recomputado
- imposto_recomputado
- valor_liquido_recomputado
- saldo_remanescente_recomputado
- cobertura_integral_recomputada
- status_cobertura_recomputada
- justificativa_recomputacao
```

### 7.4. Campos candidatos do extrato_futuro da saída canônica

```text
- data_extrato
- tipo_evento_extrato
- descricao_extrato
- estrategia_exibida_extrato
- lote_exibido_extrato
- valor_bruto_extrato
- imposto_extrato
- valor_liquido_extrato
- saldo_remanescente_extrato
- observacao_extrato
```

### 7.5. Campos derivados candidatos para auditoria futura

```text
- status_divergencia_estrategia_motor_vs_extrato
- status_divergencia_lote_motor_vs_central
- status_divergencia_lote_central_vs_extrato
- status_divergencia_bruto_central_vs_extrato
- status_divergencia_liquido_central_vs_extrato
- status_divergencia_saldo_central_vs_extrato
- hipotese_origem_mistura
- severidade_operacional_potencial
- classificacao_divergencia_potencial
```

---

## 8. Classificações candidatas de divergência potencial

A auditoria futura deverá classificar cada linha comparável usando, no mínimo, as seguintes categorias:

```text
SEM_DIVERGENCIA_OBSERVAVEL
DIVERGENCIA_POTENCIAL_LOTE
DIVERGENCIA_POTENCIAL_ESTRATEGIA
DIVERGENCIA_POTENCIAL_VALOR_BRUTO
DIVERGENCIA_POTENCIAL_VALOR_LIQUIDO
DIVERGENCIA_POTENCIAL_SALDO_REMANESCENTE
DIVERGENCIA_POTENCIAL_ORIGEM_CAMPO
DIVERGENCIA_POTENCIAL_MISTA
CAMPO_AUSENTE
NAO_COMPARAVEL
```

A classificação deverá ser descritiva. Ela não deverá propor correção automática, nem estabelecer qual camada tem precedência operacional.

---

## 9. Hipóteses de origem da mistura

A auditoria futura poderá avaliar as seguintes hipóteses, sem tratá-las como conclusão antes da evidência observável:

```text
H1: estrategia exibida no extrato_futuro deriva do motor, enquanto campos financeiros derivam da recomputacao central.
H2: lote exibido no extrato_futuro deriva do motor, enquanto valores bruto/liquido derivam da recomputacao central.
H3: lote exibido no extrato_futuro deriva da recomputacao central, enquanto a estrategia textual deriva do motor.
H4: campos financeiros exibidos no extrato_futuro derivam de recomputacao central com granularidade diferente da recomendacao do motor.
H5: divergencia potencial decorre de campo ausente, transformacao textual ou perda de rastreabilidade entre camadas.
```

Essas hipóteses necessitam execução futura controlada e não definem responsabilidade técnica isolada nesta microetapa.

---

## 10. Evidências mínimas esperadas para execução futura

A execução futura da auditoria deverá produzir, no mínimo, as seguintes evidências:

```text
1. Lista de pagamentos/eventos candidatos à comparação.
2. Identificação rastreável de data, descrição, conta e valor.
3. Registro da estratégia recomendada pelo motor, quando disponível.
4. Registro do lote sugerido pelo motor, quando disponível.
5. Registro da origem/lote financeiro recomputado pela camada central, quando disponível.
6. Registro do lote exibido no extrato_futuro, quando disponível.
7. Registro de valores bruto, imposto, líquido e saldo remanescente por camada comparável.
8. Status de divergência campo a campo.
9. Classificação da divergência potencial.
10. Hipótese de origem da mistura, quando inferível de forma rastreável.
11. Severidade operacional potencial.
12. Lista de campos ausentes ou não comparáveis.
13. Sumário quantitativo por tipo de divergência potencial.
14. Amostra rastreável de casos críticos.
15. Declaração explícita de que a evidência produzida não altera regra econômica por si só.
```

As evidências futuras deverão ser suficientes para orientar microetapa posterior de decisão técnica, sem executar correção dentro da própria auditoria.

---

## 11. Critérios de aprovação da futura auditoria executável

A futura auditoria executável poderá ser aprovada se atender simultaneamente aos critérios abaixo:

```text
- permanecer estritamente diagnostica;
- preservar codigo economico;
- preservar motor de pagamentos;
- preservar motor de switching;
- preservar recomputacao_sequencial_central_v1;
- preservar simulador central;
- preservar saida canonica;
- preservar planilha operacional;
- preservar dados financeiros;
- preservar cache BCB/CDI;
- preservar saidas oficiais e arquivos de resultado permanentes;
- produzir evidencia rastreavel por pagamento/evento;
- classificar divergencias potenciais campo a campo;
- registrar campos ausentes ou nao comparaveis;
- registrar hipoteses de origem da mistura sem definir precedencia;
- manter a fonte de verdade operacional como NAO_CONSOLIDADA;
- recomendar microetapa posterior propria para eventual decisao tecnica.
```

A futura auditoria executável não poderá ser usada diretamente como promoção de baseline econômica ou como correção implícita da saída canônica.

---

## 12. Critérios de bloqueio da futura auditoria executável

A futura auditoria executável deverá ser bloqueada se qualquer condição abaixo ocorrer:

```text
- alterar regra economica;
- alterar motor de pagamentos;
- alterar motor de switching;
- alterar recomputacao_sequencial_central_v1;
- alterar simulador central;
- alterar saida canonica;
- alterar planilha operacional;
- alterar dados financeiros;
- alterar cache BCB/CDI;
- alterar saidas oficiais;
- alterar arquivos de resultado permanentes;
- criar correcao automatica de divergencia;
- definir precedencia entre motor, recomputacao central e extrato_futuro;
- promover fonte de verdade operacional;
- executar simulacao economica ampla;
- executar release checker fora do escopo aprovado;
- misturar auditoria com refatoracao;
- misturar auditoria com correcao tecnica;
- produzir evidencias sem rastreabilidade por pagamento/evento;
- omitir campos ausentes ou nao comparaveis;
- classificar divergencia potencial como decisao economica consolidada.
```

---

## 13. Declarações negativas obrigatórias

Para preservar o caráter documental da ME-V240, ficam registradas as seguintes declarações:

```text
AUDITORIA_COMPARATIVA_REALIZADA: NAO
SCRIPT_DIAGNOSTICO_CRIADO: NAO
SCRIPT_DIAGNOSTICO_EXECUCAO: NAO
SCRIPT_OPERACIONAL_EXECUCAO: NAO
SIMULACAO_ECONOMICA_EXECUCAO: NAO
PRECEDENCIA_ENTRE_CAMADAS_DEFINIDA: NAO
DIVERGENCIA_CORRIGIDA: NAO
REGRA_ECONOMICA_ALTERADA: NAO
SAIDA_CANONICA_ALTERADA: NAO
FONTE_DE_VERDADE_OPERACIONAL_DEFINIDA: NAO
MICROETAPA_TECNICA_SUBSEQUENTE_INICIADA: NAO
CODEX_ACIONADO: NAO
RELEASE_CHECKER_EXECUCAO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUCAO: NAO
```

Declaração complementar:

```text
A ME-V240 não contém resultado comparativo, não contém validação empírica em dados operacionais e não contém decisão sobre qual camada deve orientar a saída canônica.
```

---

## 14. Próxima etapa recomendada

Próxima microetapa única recomendada:

```text
ME-V241 — Criação controlada do artefato executável de auditoria motor versus central versus extrato futuro
```

Natureza recomendada:

```text
DIAGNOSTICO / AUDITORIA EXECUTAVEL CONTROLADA
```

Escopo recomendado para a ME-V241:

```text
Criar, em microetapa propria e previamente aprovada, um script diagnostico isolado ou artefato equivalente de auditoria que leia as estruturas ja existentes e produza evidencia comparativa rastreavel, sem alterar motor, recomputacao central, simulador central, saida canonica, planilha, dados, cache ou regra economica.
```

A ME-V241 deverá passar por auditoria preventiva antes de qualquer criação de script ou execução controlada.

---

## 15. Decisão da implementação documental da ME-V240

```text
IMPLEMENTACAO_DOCUMENTAL_CONTROLADA_CONCLUIDA
V240_STATUS: CANDIDATA_DOCUMENTAL_AGUARDANDO_AUDITORIA_POS_IMPLEMENTACAO
PROMOCAO_DE_BASELINE: NAO
FONTE_DE_VERDADE_OPERACIONAL_ATUAL: NAO_CONSOLIDADA
PROXIMA_ACAO: ENVIAR_PARA_AUDITORIA_POS_IMPLEMENTACAO
```

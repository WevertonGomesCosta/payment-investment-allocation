# ME-V17-F0-V37U — Fecha documentalmente a frente V3.7 e prepara abertura da V4A

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37U
- VERSAO_CANDIDATA: V17-F0-V.3.7U
- TIPO: DOCUMENTAL / FECHAMENTO DE FRENTE / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: FECHA_FRENTE_V37_PREPARA_ABERTURA_V4A
- BASELINE_DE_ENTRADA: V17-F0-V.3.7T
- BASELINE_COMMIT_ENTRADA: 12f1d5bd283f27e18f43d7ce7350f2d9a7be22cb
- ALTERA_CODIGO: não
- ALTERA_LEDGER: não
- ALTERA_REPLAY: não
- ALTERA_PACOTE_LEDGER_TEMPORAL: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Fechar documentalmente a frente V3.7, consolidando o que foi entregue desde a reorganização da fronteira Etapa 3 → ledger, registrando os resíduos remanescentes aceitos e preparando a abertura da V4A como auditoria completa da Etapa 4.

Esta microetapa não implementa código e não altera comportamento operacional.

---

## 3. Síntese da frente V3.7

A frente V3.7 teve como função retirar o projeto de uma sequência de contenções sintomáticas na saída e recolocar a arquitetura na rota normativa:

```text
Etapa 1 — entrada resolvida
Etapa 2 — validação pré-execução
Etapa 3 — canonização operacional
Etapa 4 — replay / ledger / estado temporal
Saída canônica / saída observável — consumo de pacotes e resultados
```

O foco prático foi fechar a principal fuga arquitetural identificada: o consumo da aba bruta `Switching` pelo ledger após a Etapa 3 já produzir `switching_canonico`.

---

## 4. Entregas consolidadas da frente V3.7

### 4.1. Registro das contenções e retorno à rota normativa

As microetapas V3.7A–V3.7D consolidaram que correções anteriores em saída canônica/observável foram contenções transitórias, necessárias para estabilizar o observável, mas insuficientes como arquitetura final.

Foram tratados:

```text
duplicidade POS na saída
origens migradas ainda ativas
duplicidade residual em lotes_exauridos
resumo patrimonial afetado por origens migradas duplicadas
```

Decisão consolidada:

```text
CORRECOES_SINTOMATICAS_NA_SAIDA=controladas
RETORNO_A_FRONTEIRA_NORMATIVA=sim
```

---

### 4.2. Auditoria operacional da Etapa 3

As microetapas V3.7E–V3.7F complementaram a auditoria operacional da Etapa 3, incluindo funções, scripts, entradas, saídas e fluxograma normativo no formato das Etapas 1 e 2.

Decisão consolidada:

```text
ETAPA3_DOCUMENTALMENTE_MAPEADA=sim
FLUXOGRAMA_ETAPA3_NORMATIVO=sim
```

---

### 4.3. Contratos mínimos entre Etapa 3, replay, ledger e saída

A V3.7G especificou os contratos mínimos entre:

```text
Etapa 3
replay
ledger
saída canônica
saída observável
```

A V3.7H auditou esses contratos contra o código atual, e a V3.7I detalhou dependências ainda existentes entre ledger, saída e contexto amplo.

Decisão consolidada:

```text
CONTRATOS_MINIMOS_ETAPA3_REPLAY_LEDGER_SAIDA=definidos
VIOLACOES_E_DEPENDENCIAS_MAPEADAS=sim
```

---

### 4.4. PacoteLedgerTemporal shadow

As microetapas V3.7J–V3.7L especificaram, implementaram e validaram o `PacoteLedgerTemporal` shadow.

Decisão consolidada:

```text
PACOTE_LEDGER_TEMPORAL_SHADOW_IMPLEMENTADO=sim
EQUIVALENCIA_LEDGER_LEGADO_VALIDADA=sim
SAIDA_CANONICA_NAO_ALTERADA=sim
```

---

### 4.5. Conexão da saída canônica ao ledger shadow

As microetapas V3.7M–V3.7M.1 conectaram o `PacoteLedgerTemporal` à saída canônica em modo shadow opcional e registraram equivalência runtime.

Decisão consolidada:

```text
SAIDA_CANONICA_COM_LEDGER_SHADOW_VALIDADA=sim
SEM_ALTERACAO_OBSERVAVEL=sim
```

---

### 4.6. Auditoria Etapas 1–3 e resíduo para entrada da Etapa 4

A V3.7N auditou a sequência Etapas 1–3 e identificou o problema central:

```text
ETAPA1_FUNCIONAL=sim
ETAPA1_COM_RESIDUO_LEGADO=sim
RESIDUO_ETAPA1_CONSUMIDO_APOS_ETAPA3=sim
ETAPA2_FUNCIONAL=sim
ETAPA3_FUNCIONAL=sim
ETAPA3_COERENTE_PARA_ETAPA4_ATUAL=sim
ETAPA3_SUFICIENTE_PARA_ETAPA4_ARQUITETURALMENTE_PURA=nao
```

O resíduo crítico era o consumo da aba bruta `Switching` pelo ledger.

---

### 4.7. Substituição do consumo bruto de Switching no ledger

A sequência V3.7O–V3.7S fechou a migração:

```text
V3.7O — especificou substituição de Switching bruto por switching_canonico
V3.7P — implementou adaptador switching_canonico_para_ledger_shadow
V3.7Q — conectou switching_canonico ao ledger em modo shadow opcional
V3.7R — validou switching_canonico como fonte primária controlada do ledger
V3.7S — substituiu internamente o consumo bruto de Switching por switching_canonico
V3.7S.1 — registrou equivalência runtime da substituição interna
V3.7T — auditou fechamento da fronteira Etapa 3 → ledger
```

Decisão consolidada:

```text
SWITCHING_CANONICO_FONTE_PRIMARIA_INTERNA_LEDGER=sim
FALLBACK_LEGADO_SWITCHING_AUDITAVEL=sim
CONSUMO_PRIMARIO_SWITCHING_BRUTO_REMOVIDO=sim
SAIDA_CANONICA_IDENTICA=sim
SAIDA_OBSERVAVEL_IDENTICA=sim
```

---

## 5. Estado arquitetural ao final da V3.7

### 5.1. Fronteira Etapa 3 → ledger para Switching

```text
FRONTEIRA_ETAPA3_LEDGER_SWITCHING_FECHADA=sim
```

O ledger deixou de usar a aba bruta `Switching` como fonte primária quando `switching_canonico` está disponível.

### 5.2. Fallback legado

```text
FALLBACK_LEGADO_SWITCHING_AUDITAVEL=sim
```

O caminho bruto ainda existe em funções legadas com sufixo V3.7S, mas apenas como fallback quando o canônico estiver vazio ou indisponível.

### 5.3. Saída observável

```text
SAIDA_OBSERVAVEL_PRESERVADA=sim
```

A V3.7S.1 registrou que eventos, FIFO, retorno do ledger, extrato futuro, saída canônica e saída observável permaneceram idênticos.

---

## 6. Resíduos remanescentes aceitos

### 6.1. Contexto amplo ainda existe

Ainda existem no projeto:

```text
pacote_planilha
quadros_brutos
caminho_planilha
```

Classificação:

```text
RESIDUO_CONTEXTO_AMPLO=sim
ACEITO_PARA_V4A=sim
```

Esses elementos ainda pertencem à transição arquitetural e devem ser mapeados na auditoria completa da Etapa 4.

---

### 6.2. Fallback legado do ledger

O fallback legado ainda pode ler:

```text
contexto.pacote_planilha.quadros_brutos['Switching']
pd.read_excel(..., sheet_name='Switching')
```

Classificação:

```text
RESIDUO_SWITCHING_BRUTO=fallback_auditavel
BLOQUEIA_V4A=nao
```

---

### 6.3. Metadados antigos no PacoteLedgerTemporal

`PacoteLedgerTemporal` ainda contém marcadores históricos da fase shadow, como:

```text
usa_planilha_bruta=True
uso_transitorio_de_planilha_bruta_pelo_ledger_legado
```

Classificação:

```text
RESIDUO_AUDITORIA_PACOTE_LEDGER=sim
NATUREZA=metadado_shadow_desatualizado/parcialmente_historico
BLOQUEIA_FUNCIONAMENTO=nao
BLOQUEIA_V4A=nao
TRATAR_EM_V4A_OU_MICROAJUSTE_POSTERIOR=sim
```

---

## 7. O que não deve ser reaberto antes da V4A

A frente V3.7 não deve ser reaberta para:

```text
refatorar todo o ledger
remover fallback legado de forma prematura
alterar saída canônica
alterar saída observável
reorganizar console/XLSX
corrigir metadados shadow antigos sem auditoria da Etapa 4
abrir novas contenções pontuais em saida_canonica.py
```

Esses pontos devem ser avaliados dentro da auditoria formal da Etapa 4.

---

## 8. Critérios de encerramento da frente V3.7

A frente V3.7 é considerada encerrável porque:

```text
1. Etapa 3 foi documentada operacionalmente.
2. Fluxograma final da Etapa 3 foi registrado.
3. Contratos mínimos Etapa 3 → replay → ledger → saída foram definidos.
4. PacoteLedgerTemporal shadow foi especificado, implementado e validado.
5. Saída canônica com ledger shadow foi validada sem alteração observável.
6. Consumo bruto de Switching pelo ledger foi substituído por switching_canonico.
7. Equivalência runtime foi registrada após a substituição interna.
8. Fronteira Etapa 3 → ledger para Switching foi auditada e considerada fechada.
```

Veredito:

```text
FRENTE_V37_ENCERRADA_DOCUMENTALMENTE=sim
```

---

## 9. Condição de entrada para V4A

A V4A deve partir do seguinte estado:

```text
BASELINE_RECOMENDADA=V17-F0-V.3.7U
ETAPA3_SWITCHING_CANONICO_FONTE_PRIMARIA_LEDGER=sim
FALLBACK_LEGADO_SWITCHING_AUDITAVEL=sim
PACOTE_LEDGER_TEMPORAL_SHADOW_EXISTE=sim
SAIDA_CANONICA_ESTAVEL=sim
```

A V4A não deve reabrir a frente V3.7 como correção de switching. Ela deve auditar a Etapa 4 como camada própria.

---

## 10. Escopo recomendado da V4A

A próxima frente deve ser:

```text
V17-F0-V.4A — Auditoria completa da Etapa 4: replay, ledger e estado temporal
```

Tipo sugerido:

```text
DOCUMENTAL / AUDITORIA OPERACIONAL / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Mapear a Etapa 4 como camada própria, separando replay passado, ledger temporal, estado temporal, saldos, vencimentos, fontes elegíveis, pagamentos futuros, resíduos de contexto amplo e responsabilidades ainda indevidamente concentradas em saída canônica ou ledger legado.
```

---

## 11. Questões que a V4A deve responder

A V4A deve responder, no mínimo:

```text
1. Quais são as entradas formais da Etapa 4?
2. Quais artefatos da Etapa 3 são consumidos pela Etapa 4?
3. Quais resíduos da Etapa 1 ainda chegam à Etapa 4?
4. Onde começa e termina o replay passado?
5. Onde começa e termina o ledger temporal futuro?
6. O que é estado temporal por data?
7. Como vencimentos, saldos, fontes elegíveis e pagamentos futuros são representados?
8. Quais funções ainda misturam replay, ledger, decisão econômica e saída?
9. Quais campos devem compor um PacoteReplayPassado?
10. Quais campos devem compor um PacoteLedgerTemporal operacional futuro?
11. Quais campos atuais do PacoteLedgerTemporal shadow são provisórios?
12. Quais metadados shadow devem ser corrigidos, removidos ou reinterpretados?
13. Quais invariantes econômicos precisam ser auditados na Etapa 4?
14. Quais saídas da Etapa 4 devem alimentar a saída canônica?
```

---

## 12. Decisão final

```text
V37U_STATUS=FECHAMENTO_DOCUMENTAL_APROVADO
FRENTE_V37_ENCERRADA=sim
ABRIR_V4A=sim
V4A_DEVE_SER_DOCUMENTAL_AUDITORIA_OPERACIONAL=sim
NAO_REABRIR_V37_ANTES_DA_V4A=sim
```

---

## 13. Conclusão

A frente V3.7 está documentalmente encerrada.

O projeto concluiu a reorganização da fronteira Etapa 3 → ledger para o caso crítico de `Switching`: `switching_canonico` agora é fonte primária interna do ledger, com fallback legado auditável e sem alteração observável.

A próxima etapa segura é abrir a V4A como auditoria completa da Etapa 4 — replay, ledger e estado temporal — sem iniciar ainda uma refatoração ampla.

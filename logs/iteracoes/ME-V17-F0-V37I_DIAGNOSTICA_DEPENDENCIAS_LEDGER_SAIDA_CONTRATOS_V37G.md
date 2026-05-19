# ME-V17-F0-V37I — Diagnostica dependências do ledger e da saída canônica contra os contratos V3.7G

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37I
- VERSAO_CANDIDATA: V17-F0-V.3.7I
- TIPO: DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: DIAGNOSTICA_DEPENDENCIAS_LEDGER_SAIDA_CONTRATOS_V37G
- BASELINE_DE_ENTRADA: V17-F0-V.3.7H
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_MOTOR: não
- ALTERA_REPLAY: não
- ALTERA_LEDGER: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Condição de entrada

A microetapa foi aberta após:

```text
14d9562 — V17-F0-V.3.7H: audita contratos minimos contra codigo atual
```

A V3.7H concluiu que os contratos da V3.7G são válidos, mas que o código atual ainda apresenta acoplamentos relevantes, principalmente em:

```text
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
```

A presente V3.7I aprofunda exclusivamente esses dois módulos e seus pontos de contato.

---

## 3. Objetivo

Mapear, com granularidade maior, chamadas e leituras diretas que ainda conectam:

- ledger temporal;
- saída canônica;
- contexto amplo;
- planilha bruta;
- switching shadow;
- POS;
- replay passado;
- dados operacionais;
- motores/decisões intermediárias.

A V3.7I não corrige esses pontos. Ela classifica dependências e define destino arquitetural de migração.

---

## 4. Veredito geral

```text
DIAGNOSTICO_GRANULAR_CONCLUIDO=sim
LEDGER_DEPENDE_DE_CONTEXTO_AMPLO=sim
LEDGER_LE_PLANILHA_OU_QUADROS_BRUTOS=sim
LEDGER_INJETA_POS_NO_ESTADO_TEMPORAL=sim
SAIDA_CANONICA_CHAMA_LEDGER_DIRETAMENTE=sim
SAIDA_CANONICA_COMPLEMENTA_POS_PASSADO=sim
CORRECAO_IMEDIATA_RECOMENDADA=nao
MIGRACAO_DEVE_SER_PRECEDIDA_POR_PACOTE_LEDGER_TEMPORAL=sim
```

A V3.7I confirma que a separação contratual não deve começar pela remoção direta de funções em `saida_canonica.py`. Antes disso, é necessário explicitar `PacoteLedgerTemporal` e preparar uma interface de ledger consumível pela saída.

---

## 5. Arquivos auditados

```text
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
```

Arquivos considerados indiretamente por dependência:

```text
nucleo/contexto_baseline.py
nucleo/dados_operacionais_canonicos.py
nucleo/replay_passado_controlado.py
nucleo/ledger_switching_estado_temporal_v17_f0_o2.py
```

---

## 6. Mapa granular — ledger temporal

### 6.1. Dependência L1 — leitura de `contexto.pacote_planilha`

Funções observadas:

```text
_mapa_switchings_aba_operacional(contexto)
_eventos_switching_aba_operacional(contexto)
```

Padrão observado:

```text
contexto -> pacote_planilha -> quadros_brutos -> aba Switching
```

Classificação:

```text
VIOLACAO_CONTRATO_V37G_LEDGER_CONSOME_PLANILHA_BRUTA
```

Contrato V3.7G esperado:

```text
Ledger consome PacoteDadosOperacionaisCanonicos, UniversoEconomicoCanonico e PacoteReplayPassado.
Ledger não consulta planilha nem quadros brutos.
```

Destino correto da dependência:

```text
Etapa 3 — switching_canonico / relacoes_origem_destino_switching
```

Ação futura:

```text
substituir leitura de contexto.pacote_planilha por consumo de switching_canonico já produzido na Etapa 3
```

---

### 6.2. Dependência L2 — fallback para `pd.read_excel(..., sheet_name='Switching')`

Função observada:

```text
_mapa_switchings_aba_operacional(contexto)
```

Padrão observado:

```text
se quadros_brutos não estiver disponível:
    pd.read_excel(caminho_planilha, sheet_name='Switching')
```

Classificação:

```text
VIOLACAO_FORTE_CONTRATO_V37G_LEDGER_REABRE_PLANILHA
```

Risco:

```text
ALTO
```

Motivo:

A reabertura de planilha dentro do ledger rompe a separação:

```text
Etapa 1 resolve entrada
Etapa 2 valida
Etapa 3 canoniza
Ledger consome artefatos canônicos
```

Destino correto:

```text
Etapa 1 / Etapa 3
```

Ação futura:

```text
remover fallback de leitura física após criação de interface canônica de switching para ledger
```

---

### 6.3. Dependência L3 — consumo de `contexto.switching_economico_shadow`

Função observada:

```text
_mapa_global_switchings_contexto(contexto)
```

Padrão observado:

```text
contexto.switching_economico_shadow.plano_shadow
```

Classificação:

```text
ACOPLAMENTO_LEDGER_COM_MOTOR_SHADOW
```

Contrato V3.7G esperado:

```text
Ledger processa eventos temporais já promovidos ou definidos por camada anterior.
Ledger não deve consumir plano shadow como fonte primária de switching canônico.
```

Destino correto:

```text
motor temporal / camada de decisão futura / PacoteLedgerTemporal como evento já promovido
```

Ação futura:

```text
classificar se cada uso de switching_economico_shadow é histórico, candidato, promovido ou apenas auditoria
```

---

### 6.4. Dependência L4 — injeção de POS no estado temporal local

Função observada:

```text
_injetar_lotes_pos_switching_em_estado_lotes(contexto, estado_lotes)
```

Padrão observado:

```text
materializar_eventos_switching_ledger_estado_temporal_v17_f0_o2(contexto)
injeta lotes POS em estado_lotes
marca origens migradas
```

Classificação:

```text
RESPONSABILIDADE_MISTA_ETAPA3_LEDGER
```

Interpretação:

A existência do POS e o vínculo origem-destino pertencem à Etapa 3.

A disponibilidade temporal do POS pertence ao ledger.

Estado atual mistura esses dois aspectos.

Destino correto:

```text
Etapa 3: identifica POS, origem migrada e vínculo origem-destino.
Ledger: calcula disponibilidade e saldo temporal de POS já canônico.
```

Ação futura:

```text
separar materialização canônica de POS da ativação temporal de POS
```

---

### 6.5. Dependência L5 — uso de fontes elegíveis e decisões locais dentro do ledger

Funções observadas:

```text
_mapa_recebidos_funcionais_por_pagamento(contexto)
_pagamentos_decisao_recebido_disponivel(contexto)
```

Padrão observado:

```text
contexto.fontes_elegiveis_pagamento
contexto.decisao_local_v1
```

Classificação:

```text
ACOPLAMENTO_LEDGER_COM_DECISAO_LOCAL_E_FONTES_FUNCIONAIS
```

Risco:

```text
MEDIO
```

Motivo:

Esses objetos são úteis para manter a operação atual, mas deveriam chegar ao ledger como eventos, fontes ou decisões já formalizadas, não como busca no contexto amplo.

Destino correto:

```text
PacoteLedgerTemporal / PacoteDecisoesTemporais / pacote de eventos promovidos
```

Ação futura:

```text
mapear quais campos desses pacotes são realmente necessários ao ledger
```

---

### 6.6. Dependência L6 — ausência de `PacoteLedgerTemporal`

Estado atual:

```text
construir_ledger_temporal_conjunto(...) retorna estrutura dict-like com eventos e auditorias operacionais
```

Contrato V3.7G esperado:

```text
PacoteLedgerTemporal
```

Campos mínimos esperados:

```text
eventos_temporais
estado_temporal_por_data
saldos_por_lote
saldos_disponiveis_por_data
vencimentos_processados
pagamentos_futuros_processados
fontes_elegiveis_por_data
alertas_temporais
auditoria_ledger_temporal
```

Classificação:

```text
LACUNA_DE_ENCAPSULAMENTO
```

Ação futura:

```text
criar envelope documental/técnico PacoteLedgerTemporal antes de alterar a saída canônica
```

---

## 7. Mapa granular — saída canônica

### 7.1. Dependência S1 — import direto do ledger

Padrão observado:

```text
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
```

Classificação:

```text
VIOLACAO_CONTRATO_V37G_SAIDA_IMPORTA_PRODUTOR_DE_LEDGER
```

Contrato V3.7G esperado:

```text
Saída canônica recebe PacoteLedgerTemporal pronto.
Saída canônica não chama o construtor do ledger.
```

Risco:

```text
ALTO
```

Ação futura:

```text
injetar PacoteLedgerTemporal na entrada da construção da saída canônica
```

---

### 7.2. Dependência S2 — chamada de ledger em `_construir_extrato_futuro(...)`

Função observada:

```text
_construir_extrato_futuro(contexto)
```

Padrão observado:

```text
ledger_result = construir_ledger_temporal_conjunto(quadro, mapa_central, contexto)
```

Classificação:

```text
VIOLACAO_FORTE_CONTRATO_V37G_SAIDA_DISPARA_LEDGER
```

Impacto:

A saída canônica ainda é responsável por acionar cálculo temporal futuro.

Destino correto:

```text
Ledger temporal deve rodar antes da saída canônica.
Saída canônica deve apenas consumir eventos e saldos já prontos.
```

Ação futura:

```text
criar uma versão de _construir_extrato_futuro que consuma PacoteLedgerTemporal
```

---

### 7.3. Dependência S3 — consumo direto de replay em `_construir_extrato_passado(...)`

Função observada:

```text
_construir_extrato_passado(contexto)
```

Padrão observado:

```text
contexto.replay_passado.log_passado
```

Classificação:

```text
ADERENTE_TRANSITORIO_COM_INTERFACE_NAO_ENCAPSULADA
```

Interpretação:

A saída canônica pode consumir replay. O problema não é consumir replay, mas consumir o objeto via contexto amplo e não via `PacoteReplayPassado` formal.

Destino correto:

```text
PacoteReplayPassado
```

Ação futura:

```text
formalizar PacoteReplayPassado como entrada da saída canônica
```

---

### 7.4. Dependência S4 — complemento de pagamentos passados POS ausentes

Função observada:

```text
_incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(...)
```

Padrão observado:

```text
dados_operacionais.gastos_canonicos
lotes POS inferidos em camada de saída
criação de novas linhas no extrato passado
```

Classificação:

```text
CONTENCAO_HISTORICA_FORA_DA_FRONTEIRA_FINAL
```

Interpretação:

A função foi útil como contenção para não omitir pagamentos POS no extrato, mas a criação/complementação de eventos passados não deve pertencer à saída canônica final.

Destino correto:

```text
Replay passado: pagamentos históricos processados.
Etapa 3: identificação canônica de POS e vínculos.
Saída canônica: apenas agrega resultado pronto.
```

Risco:

```text
ALTO se removida antes de replay/POS estarem completos
```

Ação futura:

```text
não remover agora; migrar após PacoteReplayPassado e PacoteLedgerTemporal estarem explícitos
```

---

### 7.5. Dependência S5 — inferência observável de POS em `_lotes_pos_switching_observaveis_q2(...)`

Função observada:

```text
_lotes_pos_switching_observaveis_q2(contexto)
```

Padrão observado:

```text
consulta Extrato Futuro
consulta switchings construídos
consulta gastos canônicos
aplica filtros conservadores de nomes POS
```

Classificação:

```text
CONTENCAO_OBSERVAVEL_DE_POS
```

Interpretação:

A função tenta inferir quais lotes são POS a partir de saídas e dados já renderizados.

Contrato final esperado:

```text
POS deve vir identificado da Etapa 3 e/ou Ledger.
Saída não deve inferir POS por leitura observável.
```

Destino correto:

```text
Etapa 3: ativo_pos_switching / migrado_por_switching / relação origem-destino.
Ledger: disponibilidade temporal e saldo POS.
```

---

### 7.6. Dependência S6 — normalização visual de fonte inválida futura

Função observada:

```text
_normalizar_sem_fonte_valida_extrato_futuro(...)
```

Padrão observado:

```text
se status = sem_saldo_temporal_auditavel
limpa lote sugerido, origem switching e valores operacionais
```

Classificação:

```text
FILTRO_DE_APRESENTACAO_COM_RISCO_DE_CORRECAO_CANONICA
```

Interpretação:

Pode permanecer temporariamente se for estritamente visual, mas a condição `sem_saldo_temporal_auditavel` deve ser decidida pelo ledger, não pela saída.

Destino correto:

```text
Ledger define status e motivo.
Saída apenas renderiza.
```

---

### 7.7. Dependência S7 — uso de ranking e cálculo de valor líquido em saída

Funções observáveis no módulo incluem uso de:

```text
ranking_carteira
valor_liquido_hoje(...)
calendario_financeiro
```

Classificação:

```text
RISCO_DE_LOGICA_ECONOMICA_RESIDUAL_NA_SAIDA
```

Interpretação:

Nem todo uso é necessariamente bloqueante, mas deve ser auditado antes de qualquer refatoração de saída.

Destino correto:

```text
ranking: UniversoEconomicoCanonico / motor
valor líquido temporal: replay ou ledger
saída: consumo de valores já calculados
```

---

## 8. Matriz de dependências por destino de migração

| Dependência | Local atual | Destino correto | Prioridade |
|---|---|---|---:|
| Leitura de aba `Switching` no ledger | `ledger_temporal_conjunto.py` | Etapa 3 / `switching_canonico` | Alta |
| `pd.read_excel` no ledger | `ledger_temporal_conjunto.py` | Etapa 1 / removido do ledger | Alta |
| `switching_economico_shadow` no ledger | `ledger_temporal_conjunto.py` | motor/decisão temporal promovida | Média-alta |
| Injeção de POS no estado temporal | `ledger_temporal_conjunto.py` | Etapa 3 + ledger temporal | Alta |
| `fontes_elegiveis_pagamento` no ledger | `ledger_temporal_conjunto.py` | pacote de eventos/fontes temporais | Média |
| `decisao_local_v1` no ledger | `ledger_temporal_conjunto.py` | pacote de decisões promovidas | Média |
| Import de ledger na saída | `saida_canonica.py` | remover após `PacoteLedgerTemporal` | Alta |
| Chamada de ledger no extrato futuro | `saida_canonica.py` | entrada `PacoteLedgerTemporal` | Alta |
| Complemento POS passado na saída | `saida_canonica.py` | replay + Etapa 3 | Alta |
| Inferência observável de POS | `saida_canonica.py` | Etapa 3 / ledger | Alta |
| Consumo de `replay_passado.log_passado` via contexto | `saida_canonica.py` | `PacoteReplayPassado` | Média |
| Normalização de sem fonte válida | `saida_canonica.py` | ledger define; saída renderiza | Média |

---

## 9. Matriz de bloqueio para refatoração

### 9.1. Não remover agora

Não remover diretamente:

```text
construir_ledger_temporal_conjunto(...) da saída
_incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(...)
_lotes_pos_switching_observaveis_q2(...)
_injetar_lotes_pos_switching_em_estado_lotes(...)
```

Motivo:

Essas funções ainda são pontes de compatibilidade que impedem regressões conhecidas em POS, extrato passado e extrato futuro.

### 9.2. Remover somente depois de substituir por pacote formal

A remoção só deve ocorrer depois de existir:

```text
PacoteReplayPassado formal
PacoteLedgerTemporal formal
POS canônico vindo da Etapa 3
origens migradas classificadas antes da saída
```

---

## 10. Ordem segura de migração pós-V3.7I

A ordem recomendada é:

```text
1. Especificar PacoteLedgerTemporal mínimo.
2. Especificar adaptador de ledger que embrulha o retorno atual de construir_ledger_temporal_conjunto(...).
3. Fazer saída canônica aceitar PacoteLedgerTemporal opcional em modo shadow.
4. Comparar saída atual vs saída via PacoteLedgerTemporal shadow.
5. Promover PacoteLedgerTemporal como entrada obrigatória da saída canônica.
6. Só então remover chamada direta de construir_ledger_temporal_conjunto(...) de saida_canonica.py.
7. Migrar complementos POS/passado para Etapa 3/replay/ledger conforme classificação.
```

---

## 11. Primeira microetapa executável futura sugerida

A primeira alteração de código futura não deve remover nada.

Deve criar um adaptador compatível:

```text
PacoteLedgerTemporal
construir_pacote_ledger_temporal_shadow(...)
```

Esse adaptador deve embrulhar a saída atual de:

```text
construir_ledger_temporal_conjunto(...)
```

sem alterar:

```text
extrato futuro
extrato passado
situação atual
resumos patrimoniais
console
XLSX
```

---

## 12. Próxima microetapa recomendada

Antes da primeira alteração de código, a próxima microetapa documental recomendada é:

```text
V17-F0-V.3.7J — Especifica PacoteLedgerTemporal mínimo e adaptador shadow do ledger atual
```

Tipo:

```text
DOCUMENTAL / CONTRATO INTERNO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Definir o envelope mínimo de PacoteLedgerTemporal e o contrato do adaptador shadow que deve embrulhar a execução atual de construir_ledger_temporal_conjunto(...) sem alterar saída.
```

---

## 13. Critérios de aprovação desta V3.7I

A V3.7I é aprovada se:

- não altera código;
- não altera dados;
- não altera saída;
- não altera ledger;
- mapeia dependências granulares de ledger;
- mapeia dependências granulares de saída canônica;
- classifica dependências por destino arquitetural;
- identifica pontos que não devem ser removidos imediatamente;
- define ordem segura para migração futura;
- preserva os contratos da V3.7G.

---

## 14. Conclusão

A V3.7I confirma que o principal ponto de risco não é a existência do ledger ou da saída canônica, mas o acoplamento operacional entre eles.

A saída canônica ainda constrói ledger; o ledger ainda lê contexto amplo, planilha bruta e fontes shadow.

A próxima ação segura é especificar um `PacoteLedgerTemporal` mínimo e um adaptador shadow que permita comparar comportamento antes de qualquer remoção de ponte histórica.

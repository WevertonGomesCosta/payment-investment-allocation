# ME-V17-F0-V37H — Audita contratos mínimos da V3.7G contra o estado atual do código

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37H
- VERSAO_CANDIDATA: V17-F0-V.3.7H
- TIPO: DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: AUDITA_CONTRATOS_MINIMOS_V37G_CONTRA_CODIGO_ATUAL
- BASELINE_DE_ENTRADA: V17-F0-V.3.7G
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
84ab793 — V17-F0-V.3.7G: especifica contratos minimos entre camadas
```

A V3.7G formalizou contratos mínimos entre Etapa 3, replay, ledger, saída canônica e saída observável.

A presente V3.7H audita o estado atual do código contra esses contratos.

Esta microetapa não corrige código. Ela identifica conformidades, lacunas e pontos de migração.

---

## 3. Escopo auditado

Foram auditados, no nível documental/diagnóstico:

```text
nucleo/contexto_baseline.py
nucleo/dados_operacionais_canonicos.py
nucleo/replay_passado_controlado.py
nucleo/ledger_temporal_conjunto.py
nucleo/saida_canonica.py
nucleo/saida_observavel.py
```

Também foi considerada a rota documental consolidada por:

```text
ME-V17-F0-V37F
ME-V17-F0-V37F.1
ME-V17-F0-V37G
```

---

## 4. Veredito geral

```text
CONTRATOS_V37G_DOCUMENTALMENTE_VALIDOS=sim
CODIGO_ATUAL_TOTALMENTE_ADERENTE_AOS_CONTRATOS=não
MIGRACAO_ARQUITETURAL_NECESSARIA=sim
CORRECAO_IMEDIATA_DE_MOTOR_OU_SAIDA=nao
PROXIMA_ACAO_DEVE_SER_MIGRACAO_CONTROLADA=sim
```

O código atual está em estado transitório: várias funções já executam partes das responsabilidades futuras, mas os limites entre pacotes ainda não estão fisicamente separados.

O diagnóstico não invalida a V3.7G. Ele confirma a necessidade de migração em microetapas.

---

## 5. Auditoria do orquestrador `ContextoBaseline`

### 5.1. Achado

O orquestrador ainda executa a canonização operacional antes de montar e validar formalmente o `PacoteEntradaResolvida`.

Fluxo real observado:

```text
carregar_config(...)
bootstrap_ambiente(...)
construir_calendario_financeiro(...)
carregar_planilha(...)
validar_pre_execucao(...) [legado shadow]
carregar_carteira_canonica(...)
carregar_dados_operacionais_canonicos(...)
materializar_recebidos_auditaveis(...)
carregar_cache_cdi_diario(...)
montar_pacote_entrada_resolvida(...)
auditar_pacote_entrada_resolvida(...)
validar_pre_execucao_pacote_entrada_resolvida(...)
```

### 5.2. Comparação com V3.7G

Contrato V3.7G:

```text
PacoteEntradaResolvida validado
PacoteValidacaoPreExecucao aprovado
        |
        v
Etapa 3 — Canonização operacional
```

Estado atual:

```text
PacotePlanilha + config
        |
        v
carregar_dados_operacionais_canonicos(...)
        |
        v
PacoteEntradaResolvida montado depois
```

### 5.3. Classificação

```text
DESALINHAMENTO_ESTRUTURAL_TRANSITORIO
```

### 5.4. Risco

Médio.

Motivo: a lógica já foi estabilizada por contenções e auditorias anteriores, mas a ordem operacional ainda não corresponde ao contrato final.

### 5.5. Ação futura recomendada

Criar microetapa específica para inverter a dependência da Etapa 3:

```text
carregar_dados_operacionais_canonicos_de_pacote_validado(...)
```

Essa função deve consumir:

```text
PacoteEntradaResolvida
PacoteValidacaoPreExecucao
```

sem depender primariamente de `PacotePlanilha` e `config` soltos.

---

## 6. Auditoria da Etapa 3 — `dados_operacionais_canonicos.py`

### 6.1. Conformidades

O módulo já contém uma camada clara de canonização inicial dos dados operacionais.

Ele já produz:

```text
PacoteDadosOperacionaisCanonicos
inventario_canonico
gastos_canonicos
salarios_canonicos
switching_canonico
inventario_lotes_expandido
lotes_pos_switching_normalizados
auditorias parciais
```

Ele também integra destinos POS ao inventário operacional por meio de:

```text
normalizar_lotes_pos_switching_para_schema_inventario(...)
construir_inventario_lotes_expandido(...)
```

### 6.2. Lacunas contra V3.7G

O contrato final exige:

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional
```

O código atual ainda não entrega esses três pacotes como fronteiras explícitas.

Lacunas:

1. `UniversoEconomicoCanonico` ainda não é dataclass/pacote explícito nessa camada.
2. `PacoteAuditoriaCanonizacaoOperacional` ainda não existe como pacote consolidado.
3. `recebidos_canonicos` ainda não aparece como campo explícito distinto de `salarios_canonicos`.
4. `inventario_canonico_base` e `inventario_canonico_completo` existem conceitualmente, mas a dataclass ainda expõe `inventario_canonico` e `inventario_lotes_expandido`.
5. A função agregadora atual ainda consome `PacotePlanilha`, `config`, `data_referencia` e `carteira_canonica`, não o pacote validado.
6. O módulo ainda possui resolvedores locais de aba/coluna para salários e switching.

### 6.3. Ponto de atenção sobre aliases

O contrato final estabelece que a Etapa 3 deve consumir quadros estruturais resolvidos, não redescobrir aliases físicos.

O código atual ainda contém:

```text
resolver_coluna(...)
_resolver_aba_por_alias(...)
_resolver_coluna_por_alias_local(...)
```

### 6.4. Classificação

```text
PARCIALMENTE_ADERENTE_COM_LACUNAS_DE_ENCAPSULAMENTO
```

### 6.5. Risco

Médio.

A Etapa 3 já contém lógica operacional relevante, mas precisa ser encapsulada e renomeada conforme o contrato final antes de ser tratada como camada normativa fechada.

### 6.6. Ação futura recomendada

Criar primeiro uma camada adaptadora sem alterar a lógica econômica:

```text
construir_pacote_canonizacao_operacional(...)
```

Essa camada deve devolver:

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional
```

Inicialmente, pode encapsular artefatos já existentes, sem refatoração profunda.

---

## 7. Auditoria do replay passado — `replay_passado_controlado.py`

### 7.1. Conformidades

O replay já existe como camada própria e possui pacote explícito:

```text
PacoteReplayPassadoControlado
```

Esse pacote contém:

```text
lotes_apos_replay
log_passado
estado_lotes_passado
auditoria
validacao
```

O escopo declarado do módulo é reprocessar contas pagas até a data de referência, consumir lotes explicitamente informados, atualizar saldos/remanescentes e gerar log técnico do replay.

### 7.2. Lacunas contra V3.7G

O contrato final usa o nome:

```text
PacoteReplayPassado
```

O código atual usa:

```text
PacoteReplayPassadoControlado
```

Além disso, o replay atual ainda consome diretamente:

```text
PacoteDadosOperacionaisCanonicos
nucleo_financeiro
calendario_financeiro
config
serie_cdi
```

mas ainda não recebe explicitamente:

```text
UniversoEconomicoCanonico
PacoteAuditoriaCanonizacaoOperacional aprovado
```

### 7.3. Classificação

```text
ADERENTE_EM_ESCOPO_MAS_NAO_EM_CONTRATO_DE_INTERFACE
```

### 7.4. Risco

Baixo a médio.

A camada replay já está relativamente separada, mas precisa alinhar nome, entrada e saída ao contrato V3.7G.

### 7.5. Ação futura recomendada

Criar adaptador ou alias documental/técnico:

```text
PacoteReplayPassado
```

preservando inicialmente `PacoteReplayPassadoControlado` como implementação interna, até a migração completa.

---

## 8. Auditoria do ledger temporal — `ledger_temporal_conjunto.py`

### 8.1. Conformidades

O módulo declara explicitamente que consolida eventos canônicos de pagamento e switching e que não deve recalcular resgates, impostos ou saldos na camada de saída.

Ele centraliza parte relevante do estado temporal que antes ficaria acoplado à saída.

### 8.2. Violações ou desalinhamentos contra V3.7G

O contrato V3.7G exige que o ledger consuma pacotes canônicos prontos:

```text
PacoteDadosOperacionaisCanonicos
UniversoEconomicoCanonico
PacoteReplayPassado
PacoteCacheCDIDiario
calendario_financeiro
data_referencia
config temporal mínima
```

O código atual ainda usa funções que consultam diretamente o contexto e, em alguns casos, a planilha bruta ou o arquivo físico.

Pontos observados:

1. `_mapa_switchings_aba_operacional(...)` acessa `contexto.pacote_planilha.quadros_brutos`.
2. A mesma função possui fallback para `pd.read_excel(..., sheet_name='Switching')`.
3. `_eventos_switching_aba_operacional(...)` também lê a aba `Switching` via `pacote_planilha`.
4. `_mapa_global_switchings_contexto(...)` consome `contexto.switching_economico_shadow`.
5. `_injetar_lotes_pos_switching_em_estado_lotes(...)` injeta POS no estado temporal local.
6. Não há `PacoteLedgerTemporal` como dataclass/pacote explícito consolidado.

### 8.3. Classificação

```text
PARCIALMENTE_ADERENTE_COM_ACOPLAMENTO_A_CONTEXTO_E_PLANILHA
```

### 8.4. Risco

Alto para a migração arquitetural.

Motivo: o ledger é uma camada crítica e ainda possui pontes para planilha bruta, contexto amplo, switching shadow e injeção de POS. Essas pontes podem dificultar a separação entre canonização, replay e estado temporal.

### 8.5. Ação futura recomendada

Antes de qualquer refatoração econômica, criar um diagnóstico específico do ledger:

```text
auditar_dependencias_ledger_temporal_contrato_v37g.py
```

Esse diagnóstico deve listar todas as leituras diretas de:

```text
contexto.pacote_planilha
pd.read_excel
switching_economico_shadow
saida_canonica
```

---

## 9. Auditoria da saída canônica — `saida_canonica.py`

### 9.1. Conformidades

A saída canônica já possui `PacoteSaidaCanonica` como dataclass explícita.

O pacote contém campos observáveis/canônicos relevantes:

```text
extrato_passado
extrato_futuro
switchings
ranking_amostra
lotes_ativos
lotes_exauridos
recebidos_atuais
fechamento_atual
resumo_recebidos
auditoria
```

### 9.2. Violações ou desalinhamentos contra V3.7G

O contrato V3.7G estabelece que a saída canônica deve receber `PacoteLedgerTemporal` pronto e não disparar ledger.

O código atual importa e chama:

```text
from nucleo.ledger_temporal_conjunto import construir_ledger_temporal_conjunto
```

Além disso, `_construir_extrato_futuro(...)` chama:

```text
ledger_result = construir_ledger_temporal_conjunto(quadro, mapa_central, contexto)
```

Esse comportamento viola a fronteira final:

```text
Saída canônica deve receber ledger pronto, não construir ledger.
```

Também foram observadas contenções ainda na saída canônica, como:

```text
_normalizar_sem_fonte_valida_extrato_futuro(...)
_lotes_pos_switching_observaveis_q2(...)
_incluir_pagamentos_passados_pos_switching_ausentes_extrato_passado(...)
```

Essas funções foram historicamente úteis para conter inconsistências, mas não pertencem à saída canônica final.

### 9.3. Classificação

```text
NAO_ADERENTE_A_FRONTEIRA_FINAL_DA_SAIDA_CANONICA
```

### 9.4. Risco

Alto.

Motivo: a saída canônica ainda reconstrói ou complementa parte do estado temporal e de POS, o que contraria o contrato V3.7G.

### 9.5. Ação futura recomendada

Não corrigir diretamente na saída ainda.

A ordem segura é:

1. consolidar `PacoteLedgerTemporal`;
2. fazer a saída canônica receber esse pacote;
3. remover chamada direta a `construir_ledger_temporal_conjunto(...)`;
4. transferir contenções POS/passado para Etapa 3, replay ou ledger, conforme o caso.

---

## 10. Auditoria da saída observável — `saida_observavel.py`

### 10.1. Conformidades

A saída observável está majoritariamente voltada à apresentação:

```text
seleção de colunas
formatação de datas
formatação de valores
construção de linhas curtas
resumo patrimonial observável
```

### 10.2. Pontos de atenção

Há funções observáveis que somam valores de replay e complementam dados usando `saida.extrato_passado` e `recebidos_atuais`.

Exemplo conceitual:

```text
somar_valores_sacados_por_lote(...)
```

Essa função é aceitável como leitura de apresentação apenas se não alterar totais canônicos nem estado patrimonial.

### 10.3. Classificação

```text
MAJORITARIAMENTE_ADERENTE_COM_RISCO_OBSERVAVEL_CONTROLADO
```

### 10.4. Risco

Baixo a médio.

A saída observável não deve ser a primeira camada a migrar. Ela deve ser revisada depois que saída canônica, ledger e replay estiverem contratualmente estabilizados.

---

## 11. Matriz resumida de aderência

| Camada | Aderência ao contrato V3.7G | Principais lacunas | Risco |
|---|---:|---|---:|
| ContextoBaseline | Parcial | Etapa 3 executada antes do pacote validado | Médio |
| Etapa 3 | Parcial | Sem pacotes finais explícitos; usa planilha/config; resolve aliases | Médio |
| Replay | Parcial alta | Nome/entrada não alinhados a `PacoteReplayPassado` final | Baixo-médio |
| Ledger | Parcial baixa | Lê planilha/contexto; sem `PacoteLedgerTemporal` explícito | Alto |
| Saída canônica | Parcial baixa | Dispara ledger; contém contenções temporais/POS | Alto |
| Saída observável | Parcial alta | Risco de complemento observável virar regra | Baixo-médio |

---

## 12. Ordem de migração recomendada

A ordem mais segura é:

```text
1. Criar adaptador final da Etapa 3 sem mudar lógica econômica.
2. Criar PacoteAuditoriaCanonizacaoOperacional consolidado.
3. Criar UniversoEconomicoCanonico como pacote explícito.
4. Criar PacoteReplayPassado como contrato externo do replay atual.
5. Criar diagnóstico específico das dependências do ledger.
6. Criar PacoteLedgerTemporal explícito.
7. Fazer saída canônica receber PacoteLedgerTemporal pronto.
8. Remover, em microetapas separadas, contenções de saída que pertencem a Etapa 3, replay ou ledger.
9. Revisar saída observável apenas ao final.
```

---

## 13. Decisão sobre próxima microetapa

A próxima microetapa não deve alterar saída canônica diretamente.

Motivo: a saída canônica está acoplada ao ledger e a POS; corrigir a saída antes de fechar os pacotes intermediários pode gerar regressões.

A próxima microetapa recomendada é:

```text
V17-F0-V.3.7I — Cria diagnóstico das dependências do ledger e da saída canônica contra os contratos V3.7G
```

Tipo:

```text
DOCUMENTAL / DIAGNÓSTICO / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo:

```text
Mapear, com maior granularidade, todas as chamadas e leituras diretas que ainda conectam ledger e saída canônica a contexto amplo, planilha bruta, switching shadow, POS e replay.
```

Alternativa, se a prioridade for começar pela Etapa 3:

```text
V17-F0-V.3.7I — Especifica adaptador final da Etapa 3 para PacoteDadosOperacionaisCanonicos, UniversoEconomicoCanonico e PacoteAuditoriaCanonizacaoOperacional
```

Essa alternativa também deve ser documental antes de qualquer código.

---

## 14. Critérios de aprovação desta V3.7H

A V3.7H é aprovada se:

- não altera código;
- não altera dados;
- não altera saída;
- compara contratos V3.7G contra módulos reais;
- identifica conformidades;
- identifica lacunas;
- classifica riscos;
- recomenda ordem segura de migração;
- não propõe correção econômica direta;
- preserva a rota Etapa 3 -> replay -> ledger -> saída canônica -> saída observável.

---

## 15. Conclusão

A V3.7H confirma que a arquitetura contratual da V3.7G está correta, mas o código atual ainda está em transição.

Os maiores riscos estão em:

```text
ledger_temporal_conjunto.py
saida_canonica.py
```

A Etapa 3 e o replay já possuem estrutura parcial mais próxima do contrato, mas ainda precisam de adaptadores/pacotes explícitos.

A próxima etapa deve manter caráter diagnóstico ou contratual antes da primeira refatoração executável.

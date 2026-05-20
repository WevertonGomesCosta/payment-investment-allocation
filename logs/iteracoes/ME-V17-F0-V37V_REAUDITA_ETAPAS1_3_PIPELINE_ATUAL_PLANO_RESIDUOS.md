# ME-V17-F0-V37V — Reaudita Etapas 1–3 contra pipeline atual e plano de remoção de resíduos

## 1. Identificação

- MICROETAPA: ME-V17-F0-V37V
- VERSAO_CANDIDATA: V17-F0-V.3.7V
- TIPO: DOCUMENTAL / AUDITORIA ARQUITETURAL / SEM ALTERAÇÃO DE CÓDIGO
- CLASSE: REAUDITA_ETAPAS1_3_PIPELINE_ATUAL_PLANO_REMOCAO_RESIDUOS
- BASELINE_DE_ENTRADA: V17-F0-V.3.7U
- BASELINE_COMMIT_ENTRADA: cc6fb9a52fa8db746717770ab7bd34610534f503
- ALTERA_CODIGO: não
- ALTERA_ETAPA_1: não
- ALTERA_ETAPA_2: não
- ALTERA_ETAPA_3: não
- ALTERA_ETAPA_4: não
- ALTERA_LEDGER: não
- ALTERA_REPLAY: não
- ALTERA_SAIDA_CANONICA: não
- ALTERA_SAIDA_OBSERVAVEL: não
- ALTERA_CONSOLE: não
- ALTERA_XLSX: não
- ALTERA_DADOS: não
- ALTERA_CACHE: não

---

## 2. Objetivo

Antes de abrir a auditoria completa da Etapa 4, reauditar as Etapas 1–3 contra o pipeline atualizado após a frente V3.7, verificando:

```text
1. se as Etapas 1–3 continuam coerentes com o pipeline atual;
2. quais resíduos ainda existem em cada etapa;
3. se algum resíduo ainda é consumido como fonte primária após a Etapa 3;
4. quais resíduos devem ser mantidos temporariamente;
5. quando e em que ordem esses resíduos devem ser removidos.
```

---

## 3. Mudança em relação à auditoria V3.7N

A V3.7N havia identificado como resíduo crítico:

```text
ledger_temporal_conjunto ainda lê aba Switching bruta
```

Depois da sequência V3.7O–V3.7S, esse ponto mudou de classificação:

```text
ANTES: consumo primário bruto de Switching pelo ledger
AGORA: fallback legado auditável, não fonte primária
```

A V3.7U registrou que a fronteira Etapa 3 → ledger para `Switching` foi fechada, com `switching_canonico` como fonte primária interna do ledger e fallback legado preservado apenas para contingência/auditoria.

---

## 4. Pipeline atual consolidado

O pipeline operacional atual, ainda com contexto amplo, é:

```text
carregar_config
bootstrap_ambiente
construir_calendario_financeiro
carregar_planilha
validar_pre_execucao legado shadow
carregar_carteira_canonica
carregar_dados_operacionais_canonicos
materializar_recebidos_auditaveis
carregar_cache_cdi_diario
montar_pacote_entrada_resolvida
auditar_pacote_entrada_resolvida
validar_pre_execucao_pacote_entrada_resolvida
carregar replay / módulos shadow / ledger / saída
```

Interpretação:

```text
PIPELINE_FUNCIONAL=sim
PIPELINE_NORMATIVO_TOTALMENTE_LINEAR=nao
```

A execução está estável, mas a ordem formal ainda não representa a arquitetura final ideal, porque a Etapa 3 ainda é montada antes do `PacoteEntradaResolvida` validado se tornar a entrada efetiva formal.

---

## 5. Auditoria da Etapa 1 — Entrada resolvida

### 5.1. Estado atual

A Etapa 1 possui o artefato formal:

```text
PacoteEntradaResolvida
```

O pacote agrega:

```text
pacote_config
contexto_execucao
pacote_planilha
mapa_abas_resolvidas
mapa_colunas_resolvidas
quadros_brutos
quadros_estruturais_resolvidos
janela_consulta_cdi
pacote_cache_cdi
auditoria_entrada_bruta
auditoria_resolucao_entrada
auditoria_cache_cdi
metadados
```

### 5.2. Coerência com o pipeline atual

```text
ETAPA1_FUNCIONAL=sim
ETAPA1_PRODUZ_PACOTE_FORMAL=sim
ETAPA1_ALIMENTA_GATE_ETAPA2=sim
ETAPA1_AINDA_ENCAPSULA_OBJETOS_LEGADOS=sim
```

A Etapa 1 está coerente para o pipeline atual, pois ela formaliza a entrada resolvida sem romper a compatibilidade com o leitor de planilha legado.

### 5.3. Resíduos da Etapa 1

| Resíduo | Natureza | Risco atual | Remoção recomendada |
|---|---|---:|---|
| `pacote_planilha` dentro do `PacoteEntradaResolvida` | envelope legado preservado | baixo/médio | após mapear consumidores na V4A |
| `quadros_brutos` | material bruto ainda preservado | médio | após todos consumidores usarem quadros resolvidos/canônicos |
| fallback para `quadros_canonicos` quando `quadros_estruturais_resolvidos` não existe | compatibilidade transitória | baixo | após estabilizar produtor único da Etapa 1 |
| `caminho_planilha` / rastros físicos | auditoria/fallback | baixo | manter como auditoria, remover de consumo operacional posterior |

### 5.4. Decisão da Etapa 1

```text
ETAPA1_DEVE_SER_MANTIDA_COM_RESIDUOS_AGORA=sim
REMOVER_RESIDUOS_ETAPA1_ANTES_DA_V4A=nao
```

Motivo: a V4A ainda precisa mapear todos os consumidores reais desses resíduos antes de remover campos do contexto.

---

## 6. Auditoria da Etapa 2 — Validação pré-execução

### 6.1. Estado atual

A Etapa 2 implementa gate puro por:

```text
validar_pre_execucao_pacote_entrada_resolvida(...)
```

O módulo declara que a validação:

```text
não baixa planilha
não carrega planilha
não abre workbook
não transforma dados
não decide pagamento
não decide switching
não gera saída
```

### 6.2. Coerência com o pipeline atual

```text
ETAPA2_FUNCIONAL=sim
ETAPA2_CONCEITUALMENTE_PURA=sim
ETAPA2_GATE_FORMAL_PACOTE_ENTRADA_RESOLVIDA=sim
```

### 6.3. Resíduos da Etapa 2

| Resíduo | Natureza | Risco atual | Remoção recomendada |
|---|---|---:|---|
| `validacao_pre_execucao_legada_shadow` no `ContextoBaseline` | compatibilidade com gate antigo | baixo | após V4A confirmar que nenhum diagnóstico depende do gate legado |
| `validacao_pre_execucao_pacote_entrada_resolvida_shadow` | marcador shadow redundante | baixo | após consolidar ContextoBaseline final |
| duplicidade entre gate legado e gate por pacote | transição arquitetural | baixo/médio | em frente posterior de limpeza do ContextoBaseline |

### 6.4. Decisão da Etapa 2

```text
ETAPA2_NAO_BLOQUEIA_V4A=sim
REMOVER_RESIDUOS_ETAPA2_ANTES_DA_V4A=nao
```

Motivo: os resíduos são de orquestração e compatibilidade, não de cálculo nem de saída. A remoção antes da V4A não aumenta a capacidade de auditar a Etapa 4.

---

## 7. Auditoria da Etapa 3 — Canonização operacional

### 7.1. Estado atual

A Etapa 3 produz:

```text
PacoteDadosOperacionaisCanonicos
```

com:

```text
inventario_canonico
gastos_canonicos
salarios_canonicos
switching_canonico
inventario_lotes_expandido
lotes_pos_switching_normalizados
auditorias de inventário, gastos, salários, switching e inventário expandido
```

### 7.2. Coerência com o pipeline atual

```text
ETAPA3_FUNCIONAL=sim
ETAPA3_PRODUZ_SWITCHING_CANONICO=sim
ETAPA3_PRODUZ_INVENTARIO_EXPANDIDO_POS_SWITCHING=sim
ETAPA3_ALIMENTA_LEDGER_COM_SWITCHING_CANONICO=sim
```

Após a V3.7S, o artefato `switching_canonico` deixou de ser apenas diagnóstico e passou a ser efetivamente fonte primária interna do ledger.

### 7.3. Resíduos da Etapa 3

| Resíduo | Natureza | Risco atual | Remoção recomendada |
|---|---|---:|---|
| `carregar_dados_operacionais_canonicos(...)` ainda recebe `PacotePlanilha` | entrada física legada | médio | após especificar adaptador `PacoteEntradaResolvida -> PacoteDadosOperacionaisCanonicos` |
| funções de canonização ainda usam `resolver_coluna` e `quadros_brutos` do pacote planilha | acoplamento ao leitor físico | médio | após criar camada de quadros estruturais resolvidos como entrada efetiva |
| auditorias POS ainda convivem com contenções de saída anteriores | histórico/transição | baixo | manter até V4A mapear replay/ledger/estado temporal |
| neutralização temporal de origens migradas não pertence à Etapa 3 | responsabilidade fora da Etapa 3 | baixo | manter fora da Etapa 3; tratar em Etapa 4 |

### 7.4. Decisão da Etapa 3

```text
ETAPA3_COERENTE_COM_PIPELINE_ATUAL=sim
ETAPA3_AINDA_NAO_PURA_COMO_CONSUMIDORA_DA_ETAPA1=sim
REMOVER_RESIDUOS_ETAPA3_ANTES_DA_V4A=nao
```

Motivo: a Etapa 3 está funcional e agora alimenta o ledger no ponto crítico de `Switching`. A purificação da entrada da Etapa 3 deve ocorrer depois de a V4A mapear exatamente quais estruturas a Etapa 4 consome.

---

## 8. Resíduos transversais no ContextoBaseline

### 8.1. Inversão transitória de ordem

O `ContextoBaseline` ainda monta `dados_operacionais` antes de montar e validar formalmente o `PacoteEntradaResolvida`.

Classificação:

```text
INVERSAO_TRANSITORIA_CONTEXTO_BASELINE=sim
BLOQUEIA_EXECUCAO=nao
BLOQUEIA_V4A=nao
BLOQUEIA_ARQUITETURA_FINAL=sim
```

### 8.2. Contexto amplo como depósito de módulos shadow

O `ContextoBaseline` ainda agrega muitos módulos shadow, diagnósticos e experimentais.

Classificação:

```text
CONTEXTO_BASELINE_AMPLO=sim
RISCO=medio
TRATAR_EM_FRENTE_PROPRIA_APOS_V4A=sim
```

### 8.3. Bug conhecido no benchmark agrupado/individual

A auditoria V3.7N registrou bug em chamada de `carregar_benchmark_agrupado_individual_shadow(...)` em contextos com defaults, contornado nos diagnósticos por:

```text
incluir_benchmark_agrupado_individual_shadow=False
```

Classificação atual:

```text
BUG_BENCHMARK_AGRUPADO_INDIVIDUAL=conhecido
BLOQUEIA_FLUXO_PRINCIPAL=nao
BLOQUEIA_V4A=nao_se_diagnosticos_desativarem_o_benchmark
TRATAR_COMO_MICROCORRECAO_POSTERIOR=sim
```

---

## 9. Matriz consolidada de resíduos e momento de remoção

| Camada | Resíduo | Manter agora? | Remover quando? |
|---|---|---:|---|
| Etapa 1 | `pacote_planilha` no pacote formal | sim | após V4A mapear consumidores e após adaptador formal Etapa1→Etapa3 |
| Etapa 1 | `quadros_brutos` | sim | após todos os consumidores usarem quadros resolvidos/canônicos |
| Etapa 1 | `caminho_planilha` | sim | manter como auditoria; remover de consumo operacional posterior |
| Etapa 2 | validação legada shadow | sim | após ContextoBaseline final não depender do gate antigo |
| Etapa 2 | duplicidade de validação | sim | em limpeza de orquestração pós-V4A |
| Etapa 3 | consumo de `PacotePlanilha` | sim | após criar entrada Etapa3 baseada em `PacoteEntradaResolvida` validado |
| Etapa 3 | uso de `resolver_coluna` sobre quadros físicos | sim | após promover `quadros_estruturais_resolvidos` como entrada efetiva |
| Etapa 3→ledger | fallback bruto de `Switching` | sim | após V4A ou V4B decidir se fallback ainda é necessário |
| PacoteLedgerTemporal | metadados shadow antigos | sim | durante auditoria/normalização da Etapa 4 |
| ContextoBaseline | ordem transitória de montagem | sim | após definir contratos finais da Etapa 4 |
| ContextoBaseline | muitos módulos shadow no contexto | sim | frente posterior de redução do contexto amplo |

---

## 10. Plano recomendado de remoção

### 10.1. Antes da V4A

Não remover resíduos estruturais agora.

Ação recomendada antes da V4A:

```text
apenas registrar esta auditoria e iniciar a V4A com os resíduos classificados
```

### 10.2. Durante a V4A

A V4A deve mapear:

```text
quais campos de Etapa 1–3 são realmente consumidos por replay
quais campos são consumidos pelo ledger
quais campos são consumidos pela saída canônica
quais campos são apenas shadow/auditoria
quais campos podem ser removidos sem alteração observável
```

### 10.3. Depois da V4A

A remoção deve ocorrer em microetapas específicas:

```text
V4B — Especifica contratos formais da Etapa 4 e pacotes mínimos
V4C — Separa PacoteReplayPassado mínimo
V4D — Normaliza PacoteLedgerTemporal operacional e metadados
V4E — Reduz dependências do ContextoBaseline amplo
V4F — Planeja purificação Etapa1→Etapa2→Etapa3
```

A purificação das Etapas 1–3 deve ser posterior à definição dos contratos da Etapa 4 para evitar remoção prematura de dados ainda necessários para replay/ledger/saída.

---

## 11. Decisão final

```text
ETAPAS1_3_COERENTES_COM_PIPELINE_ATUAL=sim
ETAPA1_COM_RESIDUOS=sim
ETAPA2_COM_RESIDUOS=sim
ETAPA3_COM_RESIDUOS=sim
RESIDUO_CRITICO_SWITCHING_BRUTO_LEDGER_REMOVIDO_COMO_FONTE_PRIMARIA=sim
RESIDUOS_REMANESCENTES_BLOQUEIAM_V4A=nao
REMOVER_RESIDUOS_ANTES_DA_V4A=nao
ABRIR_V4A_COM_RESIDUOS_CLASSIFICADOS=sim
```

---

## 12. Próxima microetapa recomendada

```text
V17-F0-V.4A — Auditoria completa da Etapa 4: replay, ledger e estado temporal
```

Tipo sugerido:

```text
DOCUMENTAL / AUDITORIA OPERACIONAL / SEM ALTERAÇÃO DE CÓDIGO
```

Objetivo sugerido:

```text
Mapear a Etapa 4 como camada própria, separando replay passado, ledger temporal, estado temporal, saldos, vencimentos, fontes elegíveis, pagamentos futuros, resíduos de contexto amplo e responsabilidades ainda indevidamente concentradas em saída canônica ou ledger legado.
```

---

## 13. Conclusão

As Etapas 1–3 estão coerentes com o pipeline atual, mas ainda preservam resíduos estruturais necessários para compatibilidade e auditoria.

O resíduo que bloqueava a fronteira Etapa 3 → ledger — consumo primário da aba bruta `Switching` — foi resolvido na frente V3.7.

Os resíduos restantes não devem ser removidos antes da V4A. Eles devem ser levados para a auditoria completa da Etapa 4, classificados por consumidor real e removidos depois, em microetapas específicas e testáveis.

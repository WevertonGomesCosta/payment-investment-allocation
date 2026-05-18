# ME-V17-F0-V34A — Planeja adaptação da Etapa 2 para consumir PacoteEntradaResolvida

## 1. Identificação

- MICROETAPA: V17-F0-V.3.4A
- TIPO: DOCUMENTAL / ARQUITETURAL / PLANEJAMENTO CONTROLADO
- CLASSE: PLANEJA_ETAPA2_CONSUMIR_PACOTE_ENTRADA_RESOLVIDA
- ALTERA CÓDIGO: NÃO
- ALTERA `nucleo/validacao_pre_execucao.py`: NÃO
- ALTERA CONTEXTO BASELINE: NÃO
- ALTERA ENTRADA RESOLVIDA: NÃO
- ALTERA CACHE CDI/BCB: NÃO
- ALTERA RENDIMENTO: NÃO
- ALTERA MOTOR: NÃO
- ALTERA ETAPA 3: NÃO
- ALTERA SAÍDA CANÔNICA: NÃO
- ALTERA CONSOLE: NÃO
- ALTERA XLSX: NÃO
- ALTERA DADOS: NÃO

---

## 2. Objetivo

Planejar como `nucleo/validacao_pre_execucao.py` deverá ser adaptado para consumir formalmente `PacoteEntradaResolvida`, preservando a Etapa 2 como validação pré-execução pura.

Esta microetapa não implementa a adaptação. Ela apenas registra a arquitetura-alvo, o escopo técnico e a sequência segura para implementação futura.

---

## 3. Contexto consolidado

A série V17-F0-V.3.3A–V17-F0-V.3.3H criou a base estrutural da Etapa 1:

```text
PacoteEntradaResolvida
├── pacote_config
├── contexto_execucao
├── pacote_planilha
├── mapa_abas_resolvidas
├── mapa_colunas_resolvidas
├── quadros_brutos
├── quadros_estruturais_resolvidos
├── janela_consulta_cdi
├── pacote_cache_cdi
├── auditoria_entrada_bruta
├── auditoria_resolucao_entrada
├── auditoria_cache_cdi
└── metadados
```

A V17-F0-V.3.3J integrou esse pacote ao `ContextoBaseline` em modo shadow.

A V17-F0-V.3.3K e a V17-F0-V.3.3K-fix validaram que a integração shadow preservou os atributos operacionais existentes e que o cache operacional permaneceu legado.

A V17-F0-V.3.3L encerrou documentalmente a frente de integração shadow da Etapa 1 ao contexto baseline.

---

## 4. Estado atual da Etapa 2

O arquivo `nucleo/validacao_pre_execucao.py` já declara a Etapa 2 como gate puro de validação pré-execução.

A função principal atual é:

```python
validar_pre_execucao(
    pacote_config: PacoteConfig,
    contexto_execucao: ContextoExecucao,
    pacote_planilha: PacotePlanilha,
) -> PacoteValidacaoPreExecucao
```

Ela valida atualmente:

- `PacoteConfig`;
- `ContextoExecucao`;
- `PacotePlanilha`.

Internamente, a Etapa 2 atual contém os principais blocos:

```text
_validar_pacote_config(...)
_validar_contexto_execucao(...)
_validar_pacote_planilha(...)
_validar_datas_minimas(...)
_validar_numeros_minimos(...)
```

A validação de colunas ainda usa `_mapear_colunas_por_alias(...)`, isto é, ainda existe uma lógica interna de redescoberta de colunas por aliases dentro da Etapa 2.

---

## 5. Problema arquitetural a resolver em etapas futuras

A Etapa 1 já passou a produzir:

- `MapaAbasResolvidas`;
- `MapaColunasResolvidas`;
- `quadros_estruturais_resolvidos`;
- `JanelaConsultaCDI`;
- auditorias estruturais da entrada;
- `PacoteEntradaResolvida`.

Portanto, a Etapa 2 não deve continuar dependendo conceitualmente de pacotes soltos nem redescobrir aliases/colunas quando o mapa resolvido já existe no pacote.

A adaptação futura deve fazer a Etapa 2 validar os artefatos já resolvidos pela Etapa 1, sem reconstruí-los.

---

## 6. Arquitetura-alvo da Etapa 2

A arquitetura-alvo é:

```text
Entrada:
PacoteEntradaResolvida

Processamento:
validar artefatos já resolvidos
registrar erros, avisos e evidências
não transformar dados
não reler planilha
não reconstruir mapas
não canonizar dados

Saída:
PacoteValidacaoPreExecucao
```

A Etapa 2 deve continuar retornando:

```text
PacoteValidacaoPreExecucao
├── ok
├── erros_bloqueantes
├── avisos
└── evidencias
```

A estrutura de saída não deve ser alterada nesta fase para preservar compatibilidade com o `ContextoBaseline` atual.

---

## 7. Estratégia de adaptação recomendada

A adaptação deve ser progressiva e compatível com o fluxo atual.

### 7.1. Preservar a função atual

A função existente deve continuar válida:

```python
validar_pre_execucao(pacote_config, contexto_execucao, pacote_planilha)
```

Ela pode ser mantida como interface legada temporária ou como wrapper.

### 7.2. Criar interface explícita para pacote resolvido

A etapa futura poderá criar uma função explícita:

```python
validar_pre_execucao_pacote_entrada_resolvida(
    pacote_entrada_resolvida: PacoteEntradaResolvida,
) -> PacoteValidacaoPreExecucao
```

Essa função deve extrair do pacote:

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
```

### 7.3. Manter compatibilidade durante transição

Durante a transição, `validar_pre_execucao(...)` poderá continuar recebendo os três argumentos legados e chamando internamente a lógica comum de validação.

A futura função por pacote deve ser adicionada sem substituir imediatamente o fluxo atual.

---

## 8. Mapeamento entre validação atual e validação por PacoteEntradaResolvida

| Validação atual | Origem futura no PacoteEntradaResolvida | Direção planejada |
|---|---|---|
| `pacote_config` | `pacote_entrada_resolvida.pacote_config` | preservar a função `_validar_pacote_config(...)` |
| `contexto_execucao` | `pacote_entrada_resolvida.contexto_execucao` | preservar a função `_validar_contexto_execucao(...)` |
| `pacote_planilha` | `pacote_entrada_resolvida.pacote_planilha` | adaptar `_validar_pacote_planilha(...)` para consumir mapas já resolvidos |
| nomes de abas | `mapa_abas_resolvidas` | validar mapa, não redescobrir |
| aliases de colunas | `mapa_colunas_resolvidas` | validar mapa, não reconstruir aliases |
| `quadros_brutos` | `quadros_brutos` | validar presença e shapes |
| `quadros_canonicos` legado | `quadros_estruturais_resolvidos` | migrar conceitualmente para o nome normativo |
| datas críticas | `quadros_estruturais_resolvidos` + `mapa_colunas_resolvidas` | validar interpretabilidade mínima |
| números críticos | `quadros_estruturais_resolvidos` + `mapa_colunas_resolvidas` | validar interpretabilidade mínima |
| cache ausente no gate atual | `pacote_cache_cdi` + `auditoria_cache_cdi` | adicionar validação estrutural do cache |
| janela CDI ausente no gate atual | `janela_consulta_cdi` | adicionar validação estrutural da janela |
| auditoria da planilha | `auditoria_entrada_bruta` | validar consistência com `pacote_planilha.auditoria` |
| auditoria dos mapas | `auditoria_resolucao_entrada` | validar ausências e evidências |

---

## 9. Funções futuras recomendadas

A implementação futura deve adicionar funções pequenas e específicas, sem misturar Etapa 2 com Etapa 3.

Funções planejadas:

```text
validar_pre_execucao_pacote_entrada_resolvida(...)
_validar_pacote_entrada_resolvida_estrutura(...)
_validar_mapa_abas_resolvidas(...)
_validar_mapa_colunas_resolvidas(...)
_validar_quadros_estruturais_resolvidos(...)
_validar_janela_consulta_cdi(...)
_validar_pacote_cache_cdi(...)
_validar_auditorias_etapa1(...)
```

A função `_mapear_colunas_por_alias(...)` deve ser preservada por compatibilidade temporária, mas não deve ser usada pela nova validação por `PacoteEntradaResolvida`.

---

## 10. Fronteiras preservadas

A adaptação futura da Etapa 2 deve preservar que a Etapa 2 não:

- baixa planilha;
- abre workbook;
- relê abas;
- resolve aliases;
- resolve colunas para uso operacional;
- canoniza colunas;
- cria quadros estruturais;
- carrega cache BCB;
- busca BCB online;
- salva cache;
- corrige dados;
- limpa dados;
- normaliza dados operacionalmente;
- cria carteira canônica;
- cria gastos canônicos;
- cria salários canônicos;
- cria switching canônico;
- cria inventário canônico;
- integra inventário com switching;
- calcula rendimento;
- executa replay;
- monta estado temporal;
- decide pagamento;
- decide switching;
- gera ledger;
- gera saída canônica;
- renderiza console;
- gera XLSX.

---

## 11. Sequência futura recomendada

### V17-F0-V.3.4B

```text
Implementar função validar_pre_execucao_pacote_entrada_resolvida(...) em modo paralelo
```

Escopo recomendado:

- alterar apenas `nucleo/validacao_pre_execucao.py`;
- preservar `validar_pre_execucao(...)` atual;
- não alterar `contexto_baseline.py`;
- não alterar Etapa 3;
- não alterar motor;
- não alterar saída.

### V17-F0-V.3.4C

```text
Criar script diagnóstico comparando validação legada vs validação por PacoteEntradaResolvida
```

Escopo recomendado:

- criar script em `scripts/diagnostico/`;
- não alterar pipeline principal;
- comparar `PacoteValidacaoPreExecucao` legado com o pacote gerado pela nova função.

### V17-F0-V.3.4D

```text
Integrar validação por PacoteEntradaResolvida ao ContextoBaseline em modo shadow
```

Escopo recomendado:

- anexar validação nova ao contexto como atributo shadow;
- preservar `validacao_pre_execucao` legado como atributo operacional;
- não alterar Etapa 3, motor, saída, console ou XLSX.

---

## 12. Resultado da microetapa

A V17-F0-V.3.4A registra que a próxima fase da frente V deve concentrar-se exclusivamente na adaptação da Etapa 2 para consumir `PacoteEntradaResolvida`.

A adaptação futura deve preservar a Etapa 2 como validação pré-execução pura, usando artefatos já resolvidos pela Etapa 1 e sem antecipar qualquer responsabilidade da Etapa 3.
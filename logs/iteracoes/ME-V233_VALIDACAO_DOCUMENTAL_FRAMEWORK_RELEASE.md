# ME-V233 — Validação documental complementar do framework no release

```text
STATUS_DO_REGISTRO: DEFINICAO_DOCUMENTAL_CONTROLADA
MICROETAPA: ME-V233
VERSAO_CANDIDATA: V233
BASELINE_DE_ENTRADA: V232
TIPO: DOCUMENTAL / ORGANIZACIONAL
CLASSE_SEMANTICA_MMEF: DOCUMENTA_REGRA_EXISTENTE / VALIDA_GOVERNANCA_DOCUMENTAL
```

---

## 1. Estado pós-V232

```text
ESTADO_POS_V232: CARREGADO
V226: BASELINE_DOCUMENTAL_ORGANIZACIONAL_DO_FRAMEWORK_OFICIAL_MINIMO
V227: REGISTRO_DOCUMENTAL_DA_PRIMEIRA_ITERACAO_GOVERNADA
V228: APLICACAO_DOCUMENTAL_CONTROLADA_DOS_PACOTES_V226_V227_NO_REPOSITORIO_PRINCIPAL
V229: REGISTRO_DOCUMENTAL_DA_CONSOLIDACAO_DA_APLICACAO_V228
V230: DIAGNOSTICO_AUDITORIA_DA_PRIMEIRA_FRENTE_POS_FRAMEWORK
V231: AUDITORIA_DO_ESTADO_REAL_DO_REPOSITORIO_POS_FRAMEWORK
V232: AUDITORIA_DE_RELEASE_POS_FRAMEWORK
ME_V233: DEFINICAO_DOCUMENTAL_DA_VALIDACAO_COMPLEMENTAR_DO_FRAMEWORK_NO_RELEASE
```

A ME-V233 foi executada como microetapa documental/organizacional controlada, com criação exclusiva deste arquivo de registro.

Nenhuma implementação técnica foi iniciada.

Nenhuma validação complementar foi implementada em código.

---

## 2. Lacuna documental identificada pela ME-V232

A ME-V232 concluiu que o release checker vigente permanece orientado à baseline funcional V225, enquanto a camada documental V226–V232 complementa a governança operacional sem substituir a baseline funcional.

```text
LACUNA_DOCUMENTAL_IDENTIFICADA:
O release checker V225 não valida explicitamente a presença, completude ou consistência mínima dos documentos e logs de governança introduzidos entre V226 e V232.
```

Interpretação formal:

```text
A lacuna não invalida a baseline funcional V225.
A lacuna indica necessidade de validação documental complementar da camada de governança pós-V225.
```

A ME-V233 não corrige essa lacuna em código. Ela apenas define documentalmente o que deve ser validado e qual deve ser a próxima decisão operacional.

---

## 3. Separação entre baseline funcional V225 e camada documental V226–V232

```text
BASELINE_FUNCIONAL_VIGENTE: V225
ESCOPO_DA_V225: validacao funcional/economica do pacote operacional vigente
CAMADA_DOCUMENTAL_POS_V225: V226–V232
ESCOPO_DA_CAMADA_DOCUMENTAL: governanca operacional, registros de microetapas, prompts e auditorias diagnosticas
```

A V225 permanece a baseline funcional estável.

A camada V226–V232 deve ser tratada como camada documental complementar de governança, sem efeito econômico direto e sem substituição da baseline funcional.

---

## 4. Arquivos obrigatórios da camada documental V226–V232

A validação documental complementar deve considerar, no mínimo, a presença dos seguintes arquivos.

### 4.1 Framework e template

```text
docs/governanca/FRAMEWORK_DESENVOLVIMENTO.md
logs/iteracoes/TEMPLATE_ITERACAO.md
```

### 4.2 Prompts operacionais

```text
prompts/abertura_chat/PROMPT_CORE.md
prompts/auditoria/PROMPT_AUDITORIA_PREVENTIVA.md
prompts/auditoria/PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md
prompts/simulacao/PROMPT_SIMULACAO.md
prompts/gemini/PROMPT_GEMINI_ADVERSARIAL.md
prompts/claude/PROMPT_CLAUDE_VALIDACAO.md
prompts/codex/PROMPT_CODEX_IMPLEMENTACAO.md
prompts/continuidade/PROMPT_CONTINUIDADE.md
```

### 4.3 Logs de iteração governada

```text
logs/iteracoes/ME-V226_REGISTRO_ITERACAO.md
logs/iteracoes/ME-V228_REGISTRO_APLICACAO_DOCUMENTAL.md
logs/iteracoes/ME-V230_DIAGNOSTICO_PRIMEIRA_FRENTE_POS_FRAMEWORK.md
logs/iteracoes/ME-V231_AUDITORIA_ESTADO_REAL_POS_FRAMEWORK.md
logs/iteracoes/ME-V232_AUDITORIA_RELEASE_POS_FRAMEWORK.md
logs/iteracoes/ME-V233_VALIDACAO_DOCUMENTAL_FRAMEWORK_RELEASE.md
```

Observação:

```text
A inclusão do próprio arquivo ME-V233 na lista representa a definição do contrato documental da validação complementar.
A implementação executável dessa validação, se existir, deve ocorrer apenas em microetapa posterior.
```

---

## 5. Critérios mínimos de presença dos arquivos

A validação documental complementar deve verificar:

```text
CRITERIO_PRESENCA_01:
Todos os arquivos obrigatórios listados na seção 4 existem nos caminhos esperados.

CRITERIO_PRESENCA_02:
Nenhum arquivo obrigatório está vazio.

CRITERIO_PRESENCA_03:
Os diretórios docs/governanca, logs/iteracoes e prompts existem.

CRITERIO_PRESENCA_04:
Os prompts operacionais mínimos existem nas subpastas esperadas.

CRITERIO_PRESENCA_05:
Os logs de iteração governada da trilha V226–V233 existem.
```

Esses critérios são documentais. Eles não validam comportamento econômico, não executam motor e não substituem o release checker funcional V225.

---

## 6. Critérios mínimos de consistência semântica

A validação documental complementar deve verificar, de forma mínima, que os arquivos obrigatórios preservam os seguintes marcadores semânticos.

### 6.1 Framework

```text
FRAMEWORK_DESENVOLVIMENTO.md deve conter:
- FRAMEWORK_OFICIAL_MINIMO_INSTALADO
- BASELINE_FORMAL_ENTRADA: V225
- DOCUMENTAL / ORGANIZACIONAL
- DOCUMENTA_REGRA_EXISTENTE
- AUDITORIA_PREVENTIVA
- AUDITORIA_POS_IMPLEMENTACAO
```

### 6.2 Template de iteração

```text
TEMPLATE_ITERACAO.md deve conter:
- ID_MICROETAPA
- BASELINE_FORMAL_ENTRADA
- VERSAO_CANDIDATA
- ESCOPO_PERMITIDO
- ESCOPO_PROIBIDO
- AUDITORIA_PREVENTIVA_STATUS
- AUDITORIA_POS_STATUS
- PROMOVER_VERSAO_CANDIDATA
```

### 6.3 Prompts operacionais

```text
PROMPT_CORE.md deve conter:
- CORE operacional determinístico
- auditoria preventiva
- escopo permitido
- escopo proibido

PROMPT_AUDITORIA_PREVENTIVA.md deve conter:
- APROVAR_AUDITORIA_PREVENTIVA
- CORRIGIR_MICROETAPA_ANTES_DE_IMPLEMENTAR
- BLOQUEAR_MICROETAPA

PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md deve conter:
- APROVAR_AUDITORIA_POS_IMPLEMENTACAO
- CORRIGIR_IMPLEMENTACAO
- BLOQUEAR_PROMOCAO

PROMPT_SIMULACAO.md deve conter:
- SIMULACAO_ECONOMICA_NAO_APLICAVEL

PROMPT_CODEX_IMPLEMENTACAO.md deve conter:
- alterar somente o escopo permitido
- não promover versão candidata

PROMPT_CONTINUIDADE.md deve conter:
- Última baseline formal aprovada
- Próxima ação pretendida
```

### 6.4 Logs de iteração

```text
Logs de iteração devem conter:
- identificação da microetapa;
- baseline de entrada;
- versão candidata ou consolidada;
- tipo da microetapa;
- classe semântica;
- decisão final ou status pendente;
- registro de não alteração de motor, dados e regra econômica quando aplicável.
```

---

## 7. Decisão recomendada: checklist documental versus função complementar no release checker

A ME-V233 recomenda a seguinte decisão operacional:

```text
DECISAO_RECOMENDADA:
Criar primeiro um checklist/documento de validação documental complementar, separado do release checker funcional V225.
```

Justificativa:

```text
1. O release checker V225 permanece coerente para validar a baseline funcional.
2. A camada V226–V232 é documental e não deve contaminar a validação funcional sem microetapa específica.
3. A criação de checklist separado reduz risco de alteração indevida de script.
4. Após validar o checklist, uma microetapa posterior pode decidir se a validação documental deve ser incorporada ao release checker.
```

Portanto, a próxima etapa não deve alterar diretamente `scripts/diagnostico/verificar_release_baseline.py`.

---

## 8. Recomendação única de próxima microetapa

```text
PROXIMA_MICROETAPA_RECOMENDADA: ME-V234
NOME_RECOMENDADO: Checklist documental complementar do framework
TIPO_RECOMENDADO: DOCUMENTAL / ORGANIZACIONAL
CLASSE_RECOMENDADA: DOCUMENTA_REGRA_EXISTENTE / MATERIALIZA_CHECKLIST_GOVERNANCA_DOCUMENTAL
STATUS: RECOMENDACAO_APENAS
IMPLEMENTACAO_INICIADA: NAO
```

Objetivo recomendado para a ME-V234:

```text
Criar um checklist documental complementar, separado do release checker funcional V225, para validar a presença e consistência mínima dos arquivos de governança V226–V233.
```

Escopo recomendado inicial:

```text
- criar documento/checklist de validação documental;
- listar arquivos obrigatórios;
- listar marcadores semânticos mínimos;
- definir como executar a conferência manual ou semiautomática sem alterar scripts;
- não alterar release checker;
- não alterar README;
- não alterar índice de relatórios;
- não alterar motor;
- não alterar dados;
- não executar simulação econômica.
```

A ME-V234 não foi iniciada nesta microetapa.

---

## 9. Registros de não execução e não alteração

```text
RELEASE_CHECKER: NAO_ALTERADO
RELEASE_CHECKER_EXECUTADO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUTADO: NAO
VALIDACAO_DOCUMENTAL_COMPLEMENTAR_EM_CODIGO: NAO_IMPLEMENTADA
SIMULACAO_ECONOMICA_EXECUTADA: NAO
CODEX: NAO_ACIONADO
IMPLEMENTACAO_TECNICA_INICIADA: NAO
CORRECAO_TECNICA_EXECUTADA: NAO
REFATORACAO_EXECUTADA: NAO
```

---

## 10. Restrições preservadas

```text
CONTRATO_MESTRE: NAO_ALTERADO
MMEF_OFICIAL: NAO_ALTERADO
FRAMEWORK: NAO_ALTERADO
TEMPLATE_ITERACAO: NAO_ALTERADO
PROMPTS: NAO_ALTERADOS
REGISTROS_ANTERIORES_V226_V232: NAO_ALTERADOS
README: NAO_ALTERADO
INDICE_RELATORIOS: NAO_ALTERADO
RELEASE_CHECKER: NAO_ALTERADO
SCRIPTS: NAO_ALTERADOS
CODIGO_ECONOMICO: NAO_ALTERADO
MOTOR_DE_PAGAMENTOS: NAO_ALTERADO
MOTOR_DE_SWITCHING: NAO_ALTERADO
SIMULADOR_CENTRAL: NAO_ALTERADO
DADOS_FINANCEIROS: NAO_ALTERADOS
CACHE_BCB_CDI: NAO_ALTERADO
SAIDAS_OFICIAIS: NAO_ALTERADAS
RELATORIOS_ECONOMICOS_EXISTENTES: NAO_ALTERADOS
PLANILHAS_DE_DADOS: NAO_ALTERADAS
ARQUIVOS_DE_RESULTADO: NAO_ALTERADOS
V184: NAO_USADA_COMO_VERSAO_OFICIAL
```

---

## 11. Estado final da ME-V233

```text
VALIDACAO_DOCUMENTAL_COMPLEMENTAR_DEFINIDA: SIM
VALIDACAO_DOCUMENTAL_IMPLEMENTADA_EM_CODIGO: NAO
VERSAO_CANDIDATA_ATUAL: V233
PROMOCAO_V233: NAO_REALIZADA
AUDITORIA_POS_IMPLEMENTACAO_DA_ME_V233: PENDENTE
PROXIMA_MICROETAPA: ME-V234_RECOMENDADA_APENAS
```

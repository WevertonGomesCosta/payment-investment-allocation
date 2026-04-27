# Checklist de validação documental do framework

```text
STATUS_DO_DOCUMENTO: CHECKLIST_DOCUMENTAL_COMPLEMENTAR
MICROETAPA_DE_ORIGEM: ME-V234
VERSAO_CANDIDATA: V234
BASELINE_DE_ENTRADA: V233
TIPO: DOCUMENTAL / ORGANIZACIONAL
CLASSE_SEMANTICA_MMEF: DOCUMENTA_REGRA_EXISTENTE / MATERIALIZA_CHECKLIST_GOVERNANCA_DOCUMENTAL
```

---

## 1. Objetivo do checklist

Este checklist define uma validação documental complementar para verificar a presença e a consistência mínima dos arquivos de governança introduzidos entre V226 e V233.

```text
OBJETIVO:
Validar documentalmente a camada de governança V226–V233, separada do release checker funcional V225, sem executar scripts, sem alterar release checker, sem alterar motor, sem alterar dados e sem executar simulação econômica.
```

O checklist serve como instrumento de conferência documental. Ele não implementa validação em código e não substitui qualquer auditoria preventiva ou pós-implementação.

---

## 2. Relação com a baseline funcional V225

```text
BASELINE_FUNCIONAL_VIGENTE: V225
ESCOPO_DA_V225: validação funcional/econômica do pacote operacional vigente
RELEASE_CHECKER_FUNCIONAL: scripts/diagnostico/verificar_release_baseline.py
```

A baseline funcional V225 permanece a referência operacional/econômica do projeto.

Este checklist não altera, amplia ou substitui a V225. Ele apenas verifica a camada documental criada depois da V225 para governança operacional do desenvolvimento.

---

## 3. Relação com a camada documental V226–V233

```text
CAMADA_DOCUMENTAL_VALIDADA: V226–V233
ESCOPO_DA_CAMADA: framework, template, prompts, registros de iteração, auditorias diagnósticas e definição da validação documental complementar
EFEITO_ECONOMICO: NENHUM
EFEITO_SOBRE_MOTOR: NENHUM
```

A camada V226–V233 complementa a governança do projeto sem modificar o motor, os dados financeiros, o release funcional ou a baseline econômica.

A função deste checklist é conferir se essa camada documental existe e preserva marcadores mínimos de coerência.

---

## 4. Arquivos obrigatórios da governança documental

### 4.1 Framework e template

```text
docs/governanca/FRAMEWORK_DESENVOLVIMENTO.md
logs/iteracoes/TEMPLATE_ITERACAO.md
```

### 4.2 Checklist documental

```text
docs/governanca/CHECKLIST_VALIDACAO_DOCUMENTAL_FRAMEWORK.md
```

### 4.3 Prompts operacionais mínimos

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

### 4.4 Logs de iteração governada

```text
logs/iteracoes/ME-V226_REGISTRO_ITERACAO.md
logs/iteracoes/ME-V228_REGISTRO_APLICACAO_DOCUMENTAL.md
logs/iteracoes/ME-V230_DIAGNOSTICO_PRIMEIRA_FRENTE_POS_FRAMEWORK.md
logs/iteracoes/ME-V231_AUDITORIA_ESTADO_REAL_POS_FRAMEWORK.md
logs/iteracoes/ME-V232_AUDITORIA_RELEASE_POS_FRAMEWORK.md
logs/iteracoes/ME-V233_VALIDACAO_DOCUMENTAL_FRAMEWORK_RELEASE.md
```

---

## 5. Critérios mínimos de presença

A validação documental deve marcar como falha se qualquer arquivo obrigatório estiver ausente.

```text
PRESENCA_01: todos os arquivos obrigatórios existem nos caminhos definidos.
PRESENCA_02: os diretórios docs/governanca, logs/iteracoes e prompts existem.
PRESENCA_03: as subpastas prompts/abertura_chat, prompts/auditoria, prompts/simulacao, prompts/gemini, prompts/claude, prompts/codex e prompts/continuidade existem.
PRESENCA_04: os registros documentais V226, V228, V230, V231, V232 e V233 existem.
PRESENCA_05: o checklist documental complementar existe em docs/governanca.
```

Resultado esperado:

```text
STATUS_PRESENCA: APROVADO
```

se todos os arquivos obrigatórios forem localizados.

---

## 6. Critérios mínimos de não esvaziamento

Cada arquivo obrigatório deve ter conteúdo textual não vazio.

```text
NAO_ESVAZIAMENTO_01: arquivo existe e possui tamanho maior que zero.
NAO_ESVAZIAMENTO_02: arquivo contém título ou bloco identificador inicial.
NAO_ESVAZIAMENTO_03: arquivo contém pelo menos um marcador de finalidade, status, tipo ou decisão.
```

Resultado esperado:

```text
STATUS_NAO_ESVAZIAMENTO: APROVADO
```

se nenhum arquivo obrigatório estiver vazio ou trivialmente incompleto.

---

## 7. Critérios mínimos de consistência semântica

### 7.1 Framework

`docs/governanca/FRAMEWORK_DESENVOLVIMENTO.md` deve conter marcadores compatíveis com:

```text
FRAMEWORK_OFICIAL_MINIMO_INSTALADO
BASELINE_FORMAL_ENTRADA: V225
DOCUMENTAL / ORGANIZACIONAL
DOCUMENTA_REGRA_EXISTENTE
AUDITORIA_PREVENTIVA
AUDITORIA_POS_IMPLEMENTACAO
```

### 7.2 Template de iteração

`logs/iteracoes/TEMPLATE_ITERACAO.md` deve conter marcadores compatíveis com:

```text
ID_MICROETAPA
BASELINE_FORMAL_ENTRADA
VERSAO_CANDIDATA
ESCOPO_PERMITIDO
ESCOPO_PROIBIDO
AUDITORIA_PREVENTIVA_STATUS
AUDITORIA_POS_STATUS
PROMOVER_VERSAO_CANDIDATA
```

### 7.3 Prompt CORE

`prompts/abertura_chat/PROMPT_CORE.md` deve conter marcadores compatíveis com:

```text
CORE operacional determinístico
auditoria preventiva
escopo permitido
escopo proibido
```

### 7.4 Prompt de auditoria preventiva

`prompts/auditoria/PROMPT_AUDITORIA_PREVENTIVA.md` deve conter:

```text
APROVAR_AUDITORIA_PREVENTIVA
CORRIGIR_MICROETAPA_ANTES_DE_IMPLEMENTAR
BLOQUEAR_MICROETAPA
```

### 7.5 Prompt de auditoria pós-implementação

`prompts/auditoria/PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md` deve conter:

```text
APROVAR_AUDITORIA_POS_IMPLEMENTACAO
CORRIGIR_IMPLEMENTACAO
BLOQUEAR_PROMOCAO
```

### 7.6 Prompt de simulação

`prompts/simulacao/PROMPT_SIMULACAO.md` deve conter:

```text
SIMULACAO_ECONOMICA_NAO_APLICAVEL
```

### 7.7 Prompt de implementação controlada

`prompts/codex/PROMPT_CODEX_IMPLEMENTACAO.md` deve conter marcadores compatíveis com:

```text
alterar somente o escopo permitido
não promover versão candidata
```

### 7.8 Prompt de continuidade

`prompts/continuidade/PROMPT_CONTINUIDADE.md` deve conter marcadores compatíveis com:

```text
Última baseline formal aprovada
Próxima ação pretendida
```

### 7.9 Logs de iteração

Cada log de iteração obrigatório deve conter, de forma explícita ou equivalente:

```text
identificação da microetapa
baseline de entrada
versão candidata ou consolidada
tipo da microetapa
classe semântica
auditoria preventiva ou estado equivalente
auditoria pós-implementação ou estado equivalente
decisão final ou status pendente
registro de não alteração de motor, dados e regra econômica quando aplicável
```

---

## 8. Procedimento manual de conferência

Procedimento recomendado:

```text
1. Abrir a raiz do repositório.
2. Confirmar que a baseline funcional vigente continua V225 nos documentos funcionais.
3. Confirmar a existência de todos os arquivos listados na seção 4.
4. Abrir cada arquivo obrigatório.
5. Verificar se o arquivo está vazio ou incompleto.
6. Procurar os marcadores semânticos mínimos definidos na seção 7.
7. Registrar cada item como APROVADO, FALHA_MENOR ou FALHA_CRITICA.
8. Não corrigir os arquivos durante a conferência.
9. Registrar falhas como pendência para microetapa própria.
```

O procedimento manual não autoriza alterações no repositório.

---

## 9. Procedimento semiautomático conceitual, sem código

A validação pode futuramente ser semiautomatizada por uma microetapa própria, mas este checklist não implementa código.

Conceitualmente, uma validação semiautomática poderia:

```text
1. Ler uma lista fixa de caminhos obrigatórios.
2. Verificar se cada caminho existe.
3. Verificar se cada arquivo possui conteúdo não vazio.
4. Verificar a presença de marcadores textuais mínimos.
5. Emitir resumo APROVADO ou BLOQUEADO_DOCUMENTALMENTE.
6. Não tocar no motor, dados, saídas ou release funcional.
```

Essa semiautomatização exigiria microetapa própria, auditoria preventiva própria e escopo explícito para alteração de script, se aplicável.

---

## 10. Resultado esperado da validação documental

Resultado aprovado:

```text
VALIDACAO_DOCUMENTAL_FRAMEWORK: APROVADA
ARQUIVOS_OBRIGATORIOS: PRESENTES
ARQUIVOS_VAZIOS: NAO
MARCADORES_MINIMOS: PRESENTES
BASELINE_FUNCIONAL_V225: PRESERVADA
RELEASE_CHECKER_V225: NAO_SUBSTITUIDO
```

Resultado com falha:

```text
VALIDACAO_DOCUMENTAL_FRAMEWORK: BLOQUEADA_OU_EXIGE_CORRECAO
MOTIVO: [DESCREVER_FALHA]
ACAO: abrir microetapa documental ou corretiva própria
```

---

## 11. Classificação de falhas documentais

```text
FALHA_MENOR:
- marcador textual secundário ausente;
- inconsistência de nomenclatura sem impacto sobre governança;
- redação ambígua mas rastreável.

FALHA_MODERADA:
- arquivo obrigatório existe, mas não contém marcadores mínimos suficientes;
- log de iteração sem decisão final clara;
- prompt operacional incompleto.

FALHA_CRITICA:
- arquivo obrigatório ausente;
- arquivo obrigatório vazio;
- ausência de auditoria preventiva em registro que deveria conter essa informação;
- ausência de auditoria pós-implementação em registro consolidado;
- referência indevida a versão não oficial como baseline;
- alteração documental que contradiga Contrato Mestre, MMEF Oficial ou baseline funcional V225.
```

Falhas não devem ser corrigidas dentro da conferência. Devem gerar microetapa própria.

---

## 12. Limites do checklist

```text
NAO_SUBSTITUI_RELEASE_CHECKER_V225: SIM
NAO_VALIDA_MOTOR: SIM
NAO_VALIDA_DADOS_FINANCEIROS: SIM
NAO_VALIDA_REGRAS_ECONOMICAS: SIM
NAO_VALIDA_SIMULACOES: SIM
NAO_EXECUTA_SCRIPT: SIM
NAO_AUTORIZA_CORRECAO: SIM
```

Este checklist não substitui o release checker funcional V225.

Este checklist não valida motor de pagamentos, motor de switching, simulador central, dados financeiros, cache, saídas, relatórios econômicos, planilhas ou resultados de simulação.

---

## 13. Recomendação única de próxima microetapa

```text
PROXIMA_MICROETAPA_RECOMENDADA: ME-V235
NOME_RECOMENDADO: Registro de aplicação do checklist documental complementar
TIPO_RECOMENDADO: DIAGNOSTICO / AUDITORIA
CLASSE_RECOMENDADA: APLICA_CHECKLIST_GOVERNANCA_DOCUMENTAL_SEM_ALTERAR_REGRA
STATUS: RECOMENDACAO_APENAS
IMPLEMENTACAO_INICIADA: NAO
```

Objetivo recomendado para a ME-V235:

```text
Aplicar o checklist documental complementar criado na V234 em modo diagnóstico/read-only, registrando se a camada de governança V226–V234 está presente e minimamente consistente, sem alterar arquivos e sem executar scripts operacionais.
```

A ME-V235 não é iniciada por este documento.

---

## 14. Registros de não execução e não alteração

```text
RELEASE_CHECKER: NAO_ALTERADO
RELEASE_CHECKER_EXECUTADO: NAO
VERIFICAR_RELEASE_LIMPO_EXECUTADO: NAO
FUNCAO_VALIDACAO_DOCUMENTAL_SCRIPT: NAO_CRIADA
SCRIPTS: NAO_ALTERADOS
SIMULACAO_ECONOMICA_EXECUTADA: NAO
CODEX: NAO_ACIONADO
IMPLEMENTACAO_TECNICA_INICIADA: NAO
CORRECAO_TECNICA_EXECUTADA: NAO
REFATORACAO_EXECUTADA: NAO
```

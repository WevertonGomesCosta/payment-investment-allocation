# FRAMEWORK DE DESENVOLVIMENTO CONTROLADO — GOVERNANÇA OPERACIONAL

```text
PROJETO: payment-investment-allocation
STATUS: FRAMEWORK_OFICIAL_MINIMO_INSTALADO
BASELINE_FORMAL_ENTRADA: V225
VERSAO_CANDIDATA_INICIAL: V226
MICROETAPA_DE_INSTALACAO: ME-V226
TIPO_MICROETAPA: DOCUMENTAL / ORGANIZACIONAL
CLASSE_SEMANTICA_MMEF: DOCUMENTA_REGRA_EXISTENTE
PROMOCAO_BASELINE: NAO_REALIZADA
```

## 1. Finalidade

Este arquivo instala a camada mínima de governança operacional do projeto. A finalidade é padronizar a abertura, auditoria, implementação, validação e continuidade de microetapas, sem alterar regras econômicas, motores, dados, saídas oficiais ou documentos normativos superiores.

A ME-V226 é exclusivamente documental e organizacional. Ela não muda comportamento do projeto, não executa simulação econômica e não promove nova baseline estável.

## 2. Hierarquia documental

A governança operacional instalada aqui é subordinada aos documentos oficiais superiores do projeto.

Ordem de precedência:

1. Contrato Mestre vigente.
2. MMEF Oficial vigente.
3. Baseline formal de entrada da microetapa.
4. Framework de Desenvolvimento Controlado.
5. Templates, prompts e logs operacionais.

Em caso de conflito, prevalecem Contrato Mestre e MMEF Oficial. Este framework não redefine regras econômicas, fiscais, financeiras, metodológicas ou algorítmicas.

## 3. Baseline e versionamento

```text
BASELINE_FORMAL_ENTRADA: V225
VERSAO_CANDIDATA_INICIAL: V226
STATUS_V226: CANDIDATA_DOCUMENTAL
PROMOCAO_AUTOMATICA: PROIBIDA
```

A versão candidata somente pode ser promovida após auditoria pós-implementação explícita. A criação dos arquivos desta microetapa não equivale a promoção de baseline.

## 4. Tipos de microetapa

Cada microetapa deve declarar um tipo operacional antes de qualquer implementação.

Tipos aceitos:

- DOCUMENTAL / ORGANIZACIONAL
- DIAGNOSTICO / AUDITORIA
- CORRECAO_CIRURGICA
- REFINAMENTO_OPERACIONAL
- IMPLEMENTACAO_ECONOMICA_CONTROLADA
- SIMULACAO / BENCHMARK
- PROMOCAO_CONTROLADA_DE_BASELINE

A ME-V226 usa o tipo:

```text
DOCUMENTAL / ORGANIZACIONAL
```

## 5. Classe semântica frente ao MMEF

Cada microetapa deve declarar sua relação semântica com o MMEF Oficial.

Classes operacionais:

- DOCUMENTA_REGRA_EXISTENTE
- APLICA_REGRA_EXISTENTE
- TESTA_REGRA_EXISTENTE
- CORRIGE_IMPLEMENTACAO_DE_REGRA_EXISTENTE
- PROPÕE_EXTENSAO_AINDA_NAO_OFICIAL
- BLOQUEADA_POR_CONFLITO_COM_MMEF

A ME-V226 usa a classe:

```text
DOCUMENTA_REGRA_EXISTENTE
```

Essa classe indica que a microetapa apenas formaliza fluxo, bloqueios, prompts e templates. Não cria regra econômica nova.

## 6. Fluxo obrigatório de governança

Fluxo mínimo para microetapas controladas:

```text
CORE_OPERACIONAL
  -> AUDITORIA_PREVENTIVA
  -> IMPLEMENTACAO_CONTROLADA
  -> VALIDACAO_ESTRUTURAL
  -> AUDITORIA_POS_IMPLEMENTACAO
  -> DECISAO_DE_PROMOCAO_OU_REJEICAO
```

A etapa de simulação econômica só entra no fluxo quando o tipo da microetapa exigir validação econômica. Microetapas documentais ou organizacionais não devem executar simulação econômica.

## 7. Papéis operacionais

### 7.1 CORE operacional

Responsável por:

- carregar estado;
- definir microetapa formal;
- separar escopo permitido e proibido;
- declarar critérios de sucesso e falha;
- preparar auditoria preventiva;
- bloquear implementação quando houver inconsistência.

### 7.2 Auditoria preventiva

Responsável por avaliar a microetapa antes da implementação.

Deve aprovar, corrigir ou bloquear.

### 7.3 Implementação controlada

Responsável por alterar somente os arquivos autorizados na microetapa.

Não pode ampliar escopo por conveniência.

### 7.4 Auditoria pós-implementação

Responsável por verificar se o resultado implementado respeitou o escopo aprovado.

### 7.5 Simulação

Só deve ser acionada quando a microetapa tiver efeito econômico, operacional ou algorítmico que exija validação por cenários.

### 7.6 Implementador externo

Só pode atuar depois da auditoria preventiva. Deve receber escopo fechado, arquivos permitidos, arquivos proibidos, critérios de validação e restrições explícitas.

## 8. Bloqueios permanentes do framework

Antes de qualquer implementação:

```text
AUDITORIA_PREVENTIVA: OBRIGATORIA
IMPLEMENTADOR_EXTERNO_SEM_AUDITORIA: BLOQUEADO
AMPLIACAO_DE_ESCOPO: BLOQUEADA
ALTERACAO_ECONOMICA_INDIRETA: BLOQUEADA
PROMOCAO_AUTOMATICA_DE_BASELINE: BLOQUEADA
```

Microetapas documentais devem bloquear:

- alteração de código econômico;
- alteração de motores;
- alteração do simulador central;
- alteração de dados financeiros;
- alteração de saídas oficiais;
- alteração de relatórios econômicos existentes;
- simulação econômica desnecessária.

## 9. Escopo permitido da ME-V226

A ME-V226 está limitada aos seguintes arquivos:

```text
docs/governanca/FRAMEWORK_DESENVOLVIMENTO.md
logs/iteracoes/TEMPLATE_ITERACAO.md
prompts/abertura_chat/PROMPT_CORE.md
prompts/auditoria/PROMPT_AUDITORIA_PREVENTIVA.md
prompts/auditoria/PROMPT_AUDITORIA_POS_IMPLEMENTACAO.md
prompts/simulacao/PROMPT_SIMULACAO.md
prompts/gemini/PROMPT_GEMINI_ADVERSARIAL.md
prompts/claude/PROMPT_CLAUDE_VALIDACAO.md
prompts/codex/PROMPT_CODEX_IMPLEMENTACAO.md
prompts/continuidade/PROMPT_CONTINUIDADE.md
```

## 10. Escopo proibido da ME-V226

A ME-V226 não pode alterar:

```text
Contrato Mestre
MMEF Oficial
codigo economico
motor de pagamentos
motor de switching
simulador central
dados financeiros
saidas oficiais
relatorios economicos existentes
scripts canonicos
cache financeiro
planilhas de dados
resultados versionados
```

## 11. Critérios mínimos de validação

Toda implementação controlada deve produzir, no mínimo:

1. Lista de arquivos criados ou alterados.
2. Verificação de que todos pertencem ao escopo permitido.
3. Resultado de `git diff --name-only`.
4. Resultado de `git diff --stat`.
5. Verificação de ausência de referência indevida a versão não oficial.
6. Prompt para auditoria pós-implementação.

Para microetapas documentais, a validação econômica deve ser registrada como não aplicável.

## 12. Critério de promoção

Uma versão candidata só pode ser promovida quando:

1. auditoria preventiva tiver sido aprovada;
2. implementação tiver respeitado o escopo;
3. auditoria pós-implementação tiver sido aprovada;
4. validações mínimas tiverem sido registradas;
5. não houver alteração fora do escopo;
6. não houver conflito com Contrato Mestre ou MMEF Oficial.

## 13. Estado final esperado da ME-V226

```text
FRAMEWORK_OFICIAL_MINIMO: INSTALADO
BASELINE_FORMAL_ENTRADA: V225
VERSAO_CANDIDATA: V226
PROMOCAO_BASELINE: PENDENTE_DE_AUDITORIA_POS_IMPLEMENTACAO
SIMULACAO_ECONOMICA: NAO_APLICAVEL
ALTERACAO_ECONOMICA: NENHUMA
```

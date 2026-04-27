# TEMPLATE DE ITERAÇÃO CONTROLADA

```text
PROJETO: payment-investment-allocation
TIPO_ARQUIVO: TEMPLATE_ITERACAO
USO: REGISTRO_OPERACIONAL_DE_MICROETAPA
```

## 1. Identificação

```text
ID_MICROETAPA:
NOME_MICROETAPA:
BASELINE_FORMAL_ENTRADA:
VERSAO_CANDIDATA:
DATA:
RESPONSAVEL_OPERACIONAL:
STATUS_ATUAL:
```

## 2. Classificação

```text
TIPO_MICROETAPA:
CLASSE_SEMANTICA_MMEF:
ALTERA_REGRA_ECONOMICA: SIM | NAO
ALTERA_CODIGO_ECONOMICO: SIM | NAO
ALTERA_DADOS_FINANCEIROS: SIM | NAO
ALTERA_SAIDAS_OFICIAIS: SIM | NAO
EXIGE_SIMULACAO_ECONOMICA: SIM | NAO
EXIGE_IMPLEMENTADOR_EXTERNO: SIM | NAO
```

## 3. Objetivo

Descrever o objetivo em uma frase operacional, verificável e sem ampliar o escopo.

```text
OBJETIVO:
```

## 4. Escopo permitido

Listar arquivos, diretórios ou componentes autorizados.

```text
ESCOPO_PERMITIDO:
- 
```

## 5. Escopo proibido

Listar explicitamente o que não pode ser alterado.

```text
ESCOPO_PROIBIDO:
- Contrato Mestre
- MMEF Oficial
- codigo economico
- motor de pagamentos
- motor de switching
- simulador central
- dados financeiros
- saidas oficiais
- relatorios economicos existentes
```

## 6. Critérios de sucesso

```text
CRITERIOS_SUCESSO:
1.
2.
3.
```

## 7. Critérios de falha

```text
CRITERIOS_FALHA:
1.
2.
3.
```

## 8. Auditoria preventiva

```text
AUDITORIA_PREVENTIVA_STATUS: PENDENTE | APROVADA | CORRIGIR | BLOQUEADA
DECISAO_PREVENTIVA:
OBSERVACOES_PREVENTIVAS:
```

## 9. Implementação

```text
IMPLEMENTACAO_STATUS: NAO_INICIADA | EM_EXECUCAO | CONCLUIDA | BLOQUEADA
ARQUIVOS_CRIADOS_OU_ALTERADOS:
- 
ARQUIVOS_REMOVIDOS:
- 
COMANDOS_EXECUTADOS:
- 
```

## 10. Validação estrutural

```text
GIT_DIFF_NAME_ONLY:

GIT_DIFF_STAT:

REFERENCIAS_INDEVIDAS:

VALIDACAO_ECONOMICA:
NAO_APLICAVEL | EXECUTADA | BLOQUEADA
```

## 11. Auditoria pós-implementação

```text
AUDITORIA_POS_STATUS: PENDENTE | APROVADA | CORRIGIR | BLOQUEADA
DECISAO_POS_IMPLEMENTACAO:
OBSERVACOES_POS_IMPLEMENTACAO:
```

## 12. Decisão de baseline

```text
PROMOVER_VERSAO_CANDIDATA: SIM | NAO
NOVA_BASELINE_FORMAL:
JUSTIFICATIVA:
PROXIMA_MICROETAPA_RECOMENDADA:
```

## 13. Continuidade

```text
PROMPT_DE_CONTINUIDADE:
```

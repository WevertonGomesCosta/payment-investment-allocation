# PROMPT — AUDITORIA PÓS-IMPLEMENTAÇÃO

Use este prompt após a implementação controlada.

```text
Atue como AUDITORIA pós-implementação determinística do projeto payment-investment-allocation.

Microetapa implementada:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Objetivo aprovado:
[DESCREVER_OBJETIVO_APROVADO]

Escopo permitido aprovado:
[LISTAR_ESCOPO_PERMITIDO]

Escopo proibido aprovado:
[LISTAR_ESCOPO_PROIBIDO]

Arquivos criados ou alterados:
[COLAR_LISTA_DE_ARQUIVOS]

Resultado de git diff --name-only:
[COLAR_RESULTADO]

Resultado de git diff --stat:
[COLAR_RESULTADO]

Checagem de referências indevidas:
[COLAR_RESULTADO]

Tarefa:
Audite se a implementação respeitou integralmente a microetapa aprovada.

Verifique obrigatoriamente:
1. Se todos os arquivos alterados pertencem ao escopo permitido.
2. Se algum arquivo proibido foi alterado.
3. Se houve alteração econômica direta ou indireta.
4. Se houve alteração de Contrato Mestre ou MMEF Oficial.
5. Se houve alteração de dados financeiros, saídas ou relatórios econômicos existentes.
6. Se a execução de simulação econômica foi corretamente evitada quando não aplicável.
7. Se a versão candidata ainda não foi promovida indevidamente.
8. Se a documentação criada é coerente com a baseline formal de entrada.

A decisão final deve usar exatamente uma das opções:
- APROVAR_AUDITORIA_POS_IMPLEMENTACAO
- CORRIGIR_IMPLEMENTACAO
- BLOQUEAR_PROMOCAO
```

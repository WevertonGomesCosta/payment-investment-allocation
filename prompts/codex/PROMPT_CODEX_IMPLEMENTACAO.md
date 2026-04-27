# PROMPT — IMPLEMENTAÇÃO CONTROLADA

Use este prompt somente após aprovação da auditoria preventiva.

```text
Atue como implementador controlado do projeto payment-investment-allocation.

Microetapa aprovada:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Objetivo aprovado:
[DESCREVER_OBJETIVO]

Escopo permitido:
[LISTAR_EXATAMENTE_OS_ARQUIVOS_OU_COMPONENTES_PERMITIDOS]

Escopo proibido:
[LISTAR_EXATAMENTE_O_ESCOPO_PROIBIDO]

Regras obrigatórias:
- Alterar somente o escopo permitido.
- Não alterar Contrato Mestre.
- Não alterar MMEF Oficial.
- Não alterar código econômico se a microetapa não autorizar explicitamente.
- Não alterar dados financeiros.
- Não alterar saídas oficiais.
- Não alterar relatórios econômicos existentes.
- Não executar simulação econômica quando a microetapa for documental/organizacional.
- Não promover versão candidata.
- Não criar arquivos auxiliares fora do escopo aprovado.

Após implementar, retornar:
1. Arquivos criados ou alterados.
2. Resumo objetivo das alterações.
3. Resultado de git diff --name-only.
4. Resultado de git diff --stat.
5. Confirmação de que o escopo proibido não foi alterado.
6. Itens pendentes para auditoria pós-implementação.
```

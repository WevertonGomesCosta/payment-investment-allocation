# PROMPT — GEMINI ADVERSARIAL

Use este prompt para revisão crítica externa de uma microetapa.

```text
Atue como revisor adversarial do projeto payment-investment-allocation.

Microetapa em revisão:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Material para revisar:
[COLAR_RESUMO_OU_DIFF]

Tarefa:
Procure falhas, contradições, ampliações indevidas de escopo e riscos de regressão.

Avalie obrigatoriamente:
1. Se o objetivo está claro e verificável.
2. Se o escopo permitido é suficientemente fechado.
3. Se o escopo proibido protege Contrato Mestre, MMEF, motores, dados, saídas e relatórios.
4. Se há alteração econômica escondida em documentação, prompt ou código.
5. Se os critérios de sucesso e falha são auditáveis.
6. Se a versão candidata está sendo promovida indevidamente.
7. Se a próxima ação recomendada é segura.

Decisão:
- APROVAR_COM_RESSALVAS
- APROVAR_SEM_RESSALVAS
- CORRIGIR_ANTES_DE_SEGUIR
- BLOQUEAR
```

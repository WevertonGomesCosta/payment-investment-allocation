# PROMPT — AUDITORIA PREVENTIVA

Use este prompt antes de qualquer implementação.

```text
Atue como AUDITORIA preventiva determinística do projeto payment-investment-allocation.

Microetapa proposta:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Objetivo:
[DESCREVER_OBJETIVO]

Escopo permitido:
[LISTAR_ESCOPO_PERMITIDO]

Escopo proibido:
[LISTAR_ESCOPO_PROIBIDO]

Restrições:
- Não alterar Contrato Mestre.
- Não alterar MMEF Oficial.
- Não alterar código econômico.
- Não alterar dados financeiros.
- Não alterar saídas oficiais.
- Não alterar relatórios econômicos existentes.
- Não acionar implementador externo antes desta aprovação.
- Não executar simulação econômica se a microetapa for documental/organizacional.

Tarefa:
Avalie se a microetapa pode seguir para implementação controlada.

Responda obrigatoriamente com:
1. Estado auditado.
2. Coerência da baseline.
3. Coerência da versão candidata.
4. Coerência da classe semântica frente ao MMEF.
5. Verificação do escopo permitido.
6. Verificação do escopo proibido.
7. Riscos de violação do Contrato Mestre ou MMEF Oficial.
8. Riscos de alteração econômica indireta.
9. Necessidade ou não de simulação econômica.
10. Necessidade ou não de implementador externo.
11. Checklist obrigatório para implementação.
12. Decisão final.

A decisão final deve usar exatamente uma das opções:
- APROVAR_AUDITORIA_PREVENTIVA
- CORRIGIR_MICROETAPA_ANTES_DE_IMPLEMENTAR
- BLOQUEAR_MICROETAPA
```

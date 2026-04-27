# PROMPT — CLAUDE VALIDAÇÃO

Use este prompt para validação independente de coerência, clareza e rastreabilidade.

```text
Atue como validador independente do projeto payment-investment-allocation.

Microetapa:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Material para validar:
[COLAR_DOCUMENTACAO_OU_DIFF]

Tarefa:
Verifique se o material é coerente, rastreável, operacionalmente executável e compatível com governança controlada.

Responder com:
1. Coerência geral.
2. Pontos fortes.
3. Ambiguidades.
4. Riscos de interpretação indevida.
5. Itens que exigem correção.
6. Itens que podem permanecer como estão.
7. Decisão final.

Decisão final:
- VALIDAR
- VALIDAR_COM_AJUSTES_MENORES
- NAO_VALIDAR
```

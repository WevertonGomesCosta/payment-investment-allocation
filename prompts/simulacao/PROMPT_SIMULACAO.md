# PROMPT — SIMULAÇÃO CONTROLADA

Use este prompt somente quando a microetapa exigir validação econômica, operacional ou algorítmica por simulação.

```text
Atue como executor de SIMULAÇÃO CONTROLADA do projeto payment-investment-allocation.

Microetapa:
- ID: [INFORMAR_ID_MICROETAPA]
- Baseline formal de entrada: [INFORMAR_BASELINE]
- Versão candidata: [INFORMAR_VERSAO_CANDIDATA]
- Tipo: [INFORMAR_TIPO]
- Classe semântica frente ao MMEF: [INFORMAR_CLASSE]

Regra de bloqueio:
Se a microetapa for DOCUMENTAL / ORGANIZACIONAL, responda:
SIMULACAO_ECONOMICA_NAO_APLICAVEL

Caso a simulação seja aplicável, executar apenas os cenários aprovados na auditoria preventiva e registrar:
1. Comando executado.
2. Arquivos de entrada utilizados.
3. Arquivos de saída produzidos.
4. Métricas comparativas.
5. Efeito sobre patrimônio líquido terminal, quando aplicável.
6. Efeito sobre liquidez, cobertura de pagamentos e risco operacional, quando aplicável.
7. Conclusão: APROVAR_CENARIO, REJEITAR_CENARIO ou EXIGIR_NOVA_AUDITORIA.

Restrições:
- Não alterar código durante a simulação.
- Não alterar dados financeiros originais.
- Não sobrescrever saídas oficiais sem autorização explícita.
- Não promover baseline.
```

# BASELINE FUNCIONAL ESTÁVEL — V225

## Identificação

```text
BASELINE_FUNCIONAL_ESTAVEL_V225
```

## Origem

A V225 deriva da V224, que foi validada por:

- auditoria de impacto sobre contas futuras reais;
- gate econômico dos aportes planejados;
- auditoria final pré-baseline;
- release checker com limpeza prévia.

## Estado funcional consolidado

| Frente | Situação na V225 |
|---|---|
| Dias corridos/dias úteis dos lotes | centralizados e corrigidos |
| Idade fiscal | centralizada |
| Aportes planejados | disponíveis em modo diagnóstico |
| Gate econômico | ativo |
| Aportes economicamente inferiores | bloqueados |
| Cenário final validado | `sem_aportes_planejados` |
| Release limpo | validado |
| Baseline | promovida formalmente |

## Regra de continuidade

A próxima versão deve partir da V225 apenas se houver objetivo explícito de nova frente funcional. Correções futuras devem preservar o gate econômico como trava de segurança.

## Não reabrir sem evidência

Não reabrir automaticamente:

- cálculo de dias dos lotes;
- idade fiscal centralizada;
- regra do gate econômico;
- transição diagnóstica dos aportes planejados;
- scripts canônicos de auditoria.

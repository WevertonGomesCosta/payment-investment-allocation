# MICRO-ETAPA8-AUDITORIA-03 — Audita integração runtime da SaidaCanonicaOficial

## Identificação

- **Microfrente:** MICRO-ETAPA8-AUDITORIA-03
- **Tipo:** documental / auditoria de integração
- **Baseline de entrada:** `d13113dce4700234061d59d32e9940052b5dbe85`
- **Branch:** `docs/etapa8-auditoria-03`
- **PR auditada:** PR #443 — MICRO-ETAPA8-FUNCIONAL-02
- **Arquivo auditado:** `aplicacao/principal.py`

## Objetivo

Auditar se a integração da `SaidaCanonicaOficial` no runtime respeita o contrato da Etapa 8 sem substituir console/XLSX e sem alterar motor, ledger ou gates.

## Resultado

```text
STATUS: APROVAR COM RESSALVAS TRANSITÓRIAS NÃO BLOQUEANTES
```

## Achados aprovados

1. `aplicacao/principal.py` importa `construir_saida_canonica_oficial(...)`.
2. A função `carregar_contexto_e_saida()` executa Etapas 1–7 antes da Etapa 8.
3. O bloqueio por `resultado_gates_validacao_nucleo.pronto_para_etapa8=False` ocorre antes de qualquer chamada posterior.
4. Quando os gates bloqueiam, o retorno preserva `saida_canonica=None` e `saida_canonica_oficial=None`.
5. `construir_saida_canonica_oficial(...)` é chamada somente depois dos gates aprovados.
6. As funções legadas de saída, matriz, console e XLSX continuam no fluxo existente.
7. Não há nova saída observável.
8. `main()` desempacota `saida_canonica_oficial` e a preserva apenas como artefato interno.

## Bloqueio preservado

Com `pronto_para_etapa8=False`, o runtime retorna antes de chamar:

```text
construir_saida_canonica_oficial(...)
construir_saida_canonica_com_switching_v17_c7(...)
construir_matriz_elegibilidade_fontes_s7b(...)
aplicar_matriz_elegibilidade_ao_fluxo_pagamentos_s7c(...)
render_console(...)
gerar_planilha_operacional(...)
```

## Ressalvas não bloqueantes

| ID | Tipo | Severidade | Descrição | Ação recomendada |
|---|---|---:|---|---|
| R1 | API transitória | P3 | `carregar_contexto_e_saida()` passou de seis para sete retornos. | Auditar consumidores externos antes de estabilizar API pública. |
| R2 | Arquitetura transitória | P2/P3 | Console/XLSX ainda consomem a saída legada, não `SaidaCanonicaOficial`. | Tratar em microfrente futura específica. |

## Conclusão

A integração runtime mínima da `SaidaCanonicaOficial` está aprovada. Ela é interna, pós-gates, não gera saída nova e não altera decisão econômica.

## Próxima microfrente recomendada

```text
MICRO-ETAPA8-CORRECAO-01 — Corrige metadado temporal de SaidaCanonicaOficial para timezone-aware UTC
```

Escopo:

- substituir `datetime.utcnow()` por `datetime.now(timezone.utc)` em `nucleo/saida_canonica_oficial.py`;
- alteração cirúrgica;
- sem alterar runtime;
- sem alterar console/XLSX;
- sem alterar lógica econômica.

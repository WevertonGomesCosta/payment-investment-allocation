# Baseline fixa V77

## Objetivo desta versão

Derivar a V76 de forma cirúrgica para abrir o **benchmark shadow do `resolver_hibrido_5p` legado**, adicionando uma camada diagnóstica auditável de alocação multifonte local por pagamento sem acoplamento ao fluxo principal.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório antes das próximas entregas;
- criação do módulo `nucleo/switching_economico_shadow.py`;
- inclusão de `switching_economico_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_switching_economico_shadow.py` e wrapper correspondente;
- sincronização do `README`, do contrato operacional, do backlog, do índice documental e dos relatórios vigentes com a realidade da V77;
- preservação explícita do `proxy econômico v3` como baseline monofonte vigente;
- preservação de `multifonte v1` como frente futura condicionada à evidência.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V77. O motor financeiro, a lógica de valuation, o replay histórico, a F1 materializada e o congelamento do `proxy econômico v3` continuam preservados; a correção desta versão atua apenas na abertura da camada shadow de switching econômico legado, na identidade da baseline, na documentação vigente, no diagnóstico novo e nos nomes de artefatos.

## Critério desta baseline

A V77 não executa switching no fluxo principal. Ela materializa uma camada **shadow** que:
- avalia lotes ativos pós-replay;
- compara `manter` vs `switch agora e carregar até o horizonte`;
- registra bloqueios auditáveis por mínimo, máximo, carência e mesmo produto;
- produz ranking por lote e plano shadow recomendado acima de limiar mínimo.


## Ajuste incremental adicional da V77

- criação do módulo `nucleo/resolver_hibrido_5p_shadow.py`;
- inclusão de `resolver_hibrido_5p_shadow` no `ContextoBaseline`;
- criação do diagnóstico `scripts/diagnostico/inspecionar_resolver_hibrido_5p_shadow.py` e wrapper correspondente;
- abertura do benchmark shadow do `resolver_hibrido_5p` legado, preservando o fluxo principal, o replay e o `proxy econômico v3`;


## Critério adicional desta baseline

A V77 não substitui a decisão local v1 vigente. Ela materializa um **benchmark shadow** que, para cada pagamento futuro/pendente, usa apenas lotes resgatáveis elegíveis e calcula uma alocação multifonte local com pesos legados de IOF, IR, idade, liquidez, cliff e VPL, apenas para comparação diagnóstica com a escolha monofonte vigente.

# Baseline fixa V80

## Objetivo desta versão

Derivar a V79 de forma cirúrgica para abrir uma **auditoria cirúrgica apenas dos 42 casos reaproveitáveis** identificados na auditoria residual entre o `proxy v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal, sem reabrir o `proxy v3` e sem acoplar o benchmark híbrido.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório;
- criação do diagnóstico `scripts/diagnostico/inspecionar_casos_reaproveitaveis_proxy_v3_vs_hibrido_shadow.py` e wrapper correspondente;
- abertura de uma auditoria cirúrgica apenas sobre os casos classificados como `potencial_reaproveitamento_proxy_v3`;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V80.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V80. O motor financeiro, o replay, a F1, o `proxy v3`, o switching shadow e o benchmark híbrido shadow continuam preservados; a correção desta versão atua apenas na auditoria diagnóstica adicional e na identidade/documentação da baseline.

## Critério desta baseline

A V80 não reabre o `proxy v3`. Ela materializa apenas uma auditoria cirúrgica dos **42 casos reaproveitáveis**, priorizando padrões, transições dominantes e buckets mais promissores para eventual auditoria fina futura.

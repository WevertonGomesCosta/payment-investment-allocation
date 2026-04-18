# Baseline fixa V83

## Objetivo desta versão

Derivar a V81 de forma cirúrgica para abrir uma **auditoria fina apenas da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`**, identificada a partir da auditoria cirúrgica dos 42 casos reaproveitáveis entre o `proxy v3` vigente e o benchmark shadow do `resolver_hibrido_5p`, sem alterar o fluxo principal, sem reabrir o `proxy v3` e sem acoplar o benchmark híbrido.

## Ajustes aplicados

- atualização da identidade da baseline em `nucleo/identidade_baseline.py`;
- manutenção da checagem mínima de release como gate obrigatório;
- criação do diagnóstico `scripts/diagnostico/inspecionar_transicao_dominante_proxy_v3_vs_hibrido_shadow.py` e wrapper correspondente;
- abertura de uma auditoria fina apenas sobre a transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`;
- sincronização do `README`, do contrato, do backlog, do índice documental e dos relatórios vigentes com a realidade da V83.

## Garantia de compatibilidade

Os comandos canônicos e antigos continuam executáveis na V83. O motor financeiro, o replay, a F1, o `proxy v3`, o switching shadow e o benchmark híbrido shadow continuam preservados; a correção desta versão atua apenas na auditoria diagnóstica adicional e na identidade/documentação da baseline.

## Critério desta baseline

A V83 não reabre o `proxy v3`. Ela materializa apenas uma auditoria fina da transição dominante `Lote 3000 mar. B -> Lote 8500 mar.`, priorizando descrições, buckets e janela temporal mais promissora para eventual hipótese de ajuste localizado futuro.

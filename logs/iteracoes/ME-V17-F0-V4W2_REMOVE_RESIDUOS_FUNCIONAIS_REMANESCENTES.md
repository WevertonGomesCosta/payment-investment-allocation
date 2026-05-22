# ME-V17-F0-V4W2 — Remove resíduos funcionais remanescentes

- Objetivo: remover resíduos funcionais reais em `nucleo/saida_observavel.py` e manter funções públicas como renderização orientada por pacote.
- Baseline: pós-V4W/V4X com bloqueio real por resíduos funcionais remanescentes.
- Resíduos removidos: helpers legados de mapas/replay, acessos diretos a replay/contexto e varreduras genéricas `__dict__/DataFrame`.
- Funções públicas preservadas: blocos/linhas/switchings/amostras/resumo operacional.
- Confirmação: `saida_observavel.py` sem acesso direto a replay e sem varredura genérica por `__dict__/iterrows/columns`.
- V4W ajustado para validar remoção explícita (`helpers_legados_removidos`, `saida_observavel_sem_acesso_direto_replay`, `saida_observavel_sem_varredura_dict_contexto`, `saida_observavel_sem_varredura_generica_dataframe`).
- Evidência lote 3120: permanece ativo na visão com pacote e mantém saldo final 50.52, bruto sacado 3093.76 e líquido sacado 3088.95.
- Etapa 5 permanece fechada nesta microetapa.
- Próxima microetapa recomendada: `V17-F0-V.4X-reexecucao`.

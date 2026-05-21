# ME-V17-F0-V4T — Limpeza controlada de resíduos pós-Etapa 4

- Limpeza controlada realizada sem alterar código funcional (`nucleo/`, `aplicacao/`, `dados/`).
- Diagnósticos históricos V4 movidos para `scripts/diagnostico/historico/etapa4/`.
- Diagnósticos preservados no namespace ativo: V4Q, V4P0A, V4P0B, V4S.
- Diagnósticos mantidos para investigação: V4O e V4O0A.
- Correção de ROOT aplicada aos scripts arquivados para execução fora do namespace ativo.
- Validação informativa da interface Etapa 4 → Etapa 5 adicionada em V4T.
- Decisão: Etapa 5 permanece fechada (`etapa5_pode_abrir_agora=False`).
- Próximos passos V4U/V4V/V4W/V4X permanecem no fechamento da Etapa 4.

- Nota curta (ajuste cirúrgico): bloco Etapa 4 → Etapa 5 corrigido para o padrão real da V4Q; imports inexistentes removidos; falhas de validação agora registradas em `erro_validacao_etapa4_etapa5`/`componentes_etapa4_etapa5_faltantes`; Etapa 5 permanece fechada; V4U/V4V/V4W/V4X seguem no fechamento arquitetural da Etapa 4.

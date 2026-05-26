# ME-PRE-ETAPA5-06 — Consolida EstadoTemporalInicial para consumo da Etapa 5

- EstadoTemporalInicial agora prioriza `recebidos_auditaveis.quadro_recebidos_auditaveis` como fonte de `recebidos_temporais`, preservando `recebido_id` canônico (`recebido::*`) e vínculos de pagamento quando disponíveis.
- Fallback para `salarios_canonicos` permanece apenas quando artefato auditável não estiver disponível, com normalização para `recebido::*` sem gerar `salario_auto_*`.
- `inventario_temporal` passou a derivar `status_temporal` por colunas canônicas existentes (`status_temporal`, `status_ciclo`, `situacao_investimento`, disponibilidade e flags reais), evitando classificar todos os lotes como ativos por ausência de flags legadas.
- Decisão de entrypoints standalone: `aplicacao/console/principal.py` permanece suportado e agora também constrói `EstadoTemporalInicial` na rota direta, usando a mesma cadeia canônica mínima da execução oficial.
- `nucleo/gerar_planilha_operacional.py` permanece suportado como renderizador sobre `ContextoOperacionalCanonico` + `SaidaCanonica` (injeção opcional), sem dependência de `ContextoBaseline`.
- Não houve uso de V4Z como gate, sem criação de sentinelas e sem scripts diagnósticos.

- Ajuste de correção PR #397: entrypoints standalone (console e planilha) passaram a construir a mesma saída canônica com switching materializado usada na rota oficial (`construir_saida_canonica_com_switching_v17_c7` + matriz S7B/S7C), eliminando divergência de switchings zerados no console standalone.

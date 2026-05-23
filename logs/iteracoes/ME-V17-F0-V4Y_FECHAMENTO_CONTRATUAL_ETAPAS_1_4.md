# V17-F0-V.4Y — Fechamento contratual estrito das Etapas 1–4 antes da Etapa 5

## Objetivo
Fechar contratualmente as Etapas 1–4 para garantir que a Etapa 5 consuma exclusivamente a saída saneada da Etapa 4.

## Decisões aplicadas
- Sentinelas específicas (Lote 3120 mai e Lote 8500 mar.) deixaram de ser gate normativo.
- Sentinelas permanecem apenas como regressão observável complementar.
- Gate de fechamento passa a depender de invariantes globais da Etapa 4 e dos contratos ativos V4W/V4X/V4Y.
- Mensagens semânticas legadas em V4U/V4V foram atualizadas para não contradizer o estado runtime atual.

## Fronteira formal da Etapa 5
A Etapa 5 só pode consumir:
- `PacoteSaidaObservavelTemporal` consolidado (ou sucessor explícito compatível);
- `saida_canonica` validada na Etapa 4, apenas quando encapsulada pelo pacote final;
- `relatorio_operacional_v225.xlsx` como artefato observável/exportado;
- V4X/V4Y como gates de validação (não como fonte de dados operacionais).

É proibido para Etapa 5:
- consumir planilha bruta;
- consumir contexto bruto;
- consumir `replay_passado`/`log_passado`;
- consumir helpers antigos;
- usar scripts diagnósticos como fonte operacional;
- recompor paralelamente lotes, pagamentos ou saldos;
- fallback para Etapas 1–3.

## Evidência contratual
- Auditor V4Y criado para validar cadeia estrita Etapas 1–4 e aptidão da Etapa 5.
- V4Y publica flags explícitas de resíduos funcionais/semânticos e consumo exclusivo da saída da Etapa 4.

## Revisão P1 semântico (PR #355)
- Corrigido o gate semântico do V4Y para usar flags atuais de V4U/V4V:
  - `compatibilidade_historica_preservada`
  - `helpers_legados_runtime_removidos`
  - `fallback_runtime_sem_pacote_bloqueado`
- Flags antigas (`helpers_legados_ainda_existentes`, `fallback_legado_preservado`, `helpers_legados_removidos`) permanecem apenas como detector de regressão contraditória; se reaparecerem em estado proibido, `residuos_semanticos_auditores=true` e a abertura da Etapa 5 é bloqueada.
- Sentinelas específicas (lote 3120/8500) permanecem somente como regressão/evidência auxiliar e não podem compor gates normativos (`validacao_v4w_ok`, `etapa4_saneada`, `etapa4_fechamento_saneado_ok`, `etapa5_pode_abrir`).
- A Etapa 5 permanece condicionada exclusivamente à saída saneada da Etapa 4.
- V4Y formalizado como gate contratual final antes da Etapa 5.

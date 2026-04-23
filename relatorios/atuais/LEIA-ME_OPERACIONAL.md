# LEIA-ME operacional — V176

## Baseline vigente
- Baseline vigente: **V179**
- Baseline anterior preservada: **V175**
- Marco de congelamento estrutural local do switching: **V174**
- Baseline central/contratual da frente principal: **V108**

## Leitura obrigatória inicial

### Contrato e direção metodológica
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V179.md`
- `CONTRATO_VALIDACAO_DIARIA_OBJETIVO_FINAL_V176.md`
- `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`
- `METRICA_CANONICA_MINIMA_CENTRAL.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

### Auditorias que governam esta etapa
- `AUDITORIA_REPOSITORIO_OBJETIVO_FINAL_V175.md`
- `AUDITORIA_ALINHAMENTO_CONTRATO_OBJETIVO_FINAL_V176.md`
- `AUDITORIA_CONGELAMENTO_APLICAR_SWITCHING_EVENTOS_V174.md`
- `VALIDACAO_DIARIA_OPERACIONAL_V175_2026-04-23_2026-05-23.md`
- `VALIDACAO_DIARIA_OPERACIONAL_V176_2026-04-23_2026-05-23.md`

## Regra operacional desta etapa
1. Não interpretar saídas user-facing apenas pelo contrato executável mínimo da baseline.
2. Validar pagamentos e switchings contra o **objetivo final do projeto**.
3. Exigir auditabilidade por lote/fonte nas saídas diárias.
4. Não aceitar runner diário que oculte componentes reais do pagamento vencedor.
5. Não aceitar runner diário que omita ações e cenários de switching do dia.

## Artefatos principais da V176
- `nucleo/runner_validacao_diaria_operacional_v176.py`
- `scripts/diagnostico/inspecionar_validacao_diaria_operacional_v176.py`
- `saidas/validacao_diaria_operacional_v176_2026-04-23_2026-05-23.json`
- `relatorios/atuais/VALIDACAO_DIARIA_OPERACIONAL_V176_2026-04-23_2026-05-23.md`

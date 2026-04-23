# LEIA-ME operacional — V139

## Baseline vigente
- Baseline de reorganização: **V139**
- Baseline de integração anterior preservada: **V138**
- Baseline central/contratual da frente principal: **V108**

## O que fica ativo em `relatorios/atuais`

### Contrato e direção metodológica
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `CONTRATO_V117_MOTOR_CONJUNTO_TEMPORAL.md`
- `CONTRATO_V117_ALOCADOR_PAGAMENTOS_TERMINAL_E_PLANEJADOR_SWITCHING_TEMPORAL.md`
- `CONTRATO_RANKING_CARTEIRA_V123.md`
- `METRICA_CANONICA_MINIMA_CENTRAL.md`
- `RECOMPUTACAO_SEQUENCIAL_CENTRAL_V108.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `F1_CONTRATO_MINIMO_CAIXA_RECEBIDOS.md`
- `MAPA_ABSORCAO_LEGADO_SCRIPTS_1_2.md`

### Frente temporal e pagamentos ainda vigentes
- `COMPARADOR_HIBRIDO_SWITCHING_V132.md`
- `GRADE_DIARIA_OFICIAL_HIBRIDA_V134.md`
- `AUDITORIA_ATIVACAO_LOTES_NAO_APORTADOS_FUTUROS_V136.md`
- `AUDITORIA_ATIVACAO_E_EXPANSAO_FUTUROS_V136.md`
- `AUDITORIA_FECHAMENTO_FRENTE_TEMPORAL_V135.md`
- `ALOCADOR_PAGAMENTOS_TERMINAL_V137.md`
- `FLUXO_PAGAMENTOS_TERMINAL_RECORTE_CURTO_V138.md`

### Reorganização vigente
- `BASELINE_FIXA_V139.md`
- `VALIDACAO_LOCAL_V139.md`
- `ESTRUTURA_REPOSITORIO_V139.md`
- `PREPARACAO_MODELOS_SCRIPT1_PAGAMENTOS_V139.md`
- `LEIA-ME_OPERACIONAL.md`

## Nova trilha de saídas
- `saidas/oficial/` → artefatos operacionais vigentes e saídas user-facing mais recentes
- `saidas/diagnostico/` → JSONs, chunks e relatórios técnicos usados para auditoria
- `saidas/historico/` → artefatos antigos preservados por rastreabilidade
- `saidas/operacional/` → camada de compatibilidade temporária durante a migração dos writers

## Próxima etapa após esta reorganização
1. absorver os modelos do Script 1 na camada `pagamentos`;
2. só depois ampliar o fluxo real de pagamentos para um bloco maior.

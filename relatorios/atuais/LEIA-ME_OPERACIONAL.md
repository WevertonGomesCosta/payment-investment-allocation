# LEIA-ME operacional — V201

## Baseline vigente da camada documental e de navegação
- Pacote operacional atual: **V201**
- Base funcional fixa de origem: **V200**
- Contrato mestre vigente: **CONTRATO_OPERACIONAL_PROJETO.md**
- Modelo oficial vigente: **MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md**
- Baseline contratual/metodológica preservada: **V183/V182**

## Leitura obrigatória inicial

### Núcleo normativo vigente
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `ESPECIFICACAO_SAIDA_OFICIAL.md`

### Documentos operacionais da V201
- `AUDITORIA_LIMPEZA_RESIDUAL_V201.md`
- `MAPA_SCRIPTS_V201.md`
- `CORRECAO_CIRURGICA_V200.md`

## Regra de leitura desta etapa
1. Interpretar o projeto pela V183 como contrato mestre vigente e pela V182 como modelo oficial vigente.
2. Tratar a V201 como baseline de limpeza residual segura, derivada da V200.
3. Tratar a V200 como base funcional fixa imediatamente anterior.
4. Não usar documentos históricos como base normativa principal para novas implementações.
5. Tratar `saidas/oficial/` como caminho canônico de artefatos oficiais ativos.
6. Tratar `relatorio_operacional_v200.xlsx` como saída operacional oficial ativa até nova geração formal.
7. Tratar `scripts/historico_raiz/` como acervo histórico sem autoridade operacional.
8. Exigir que a próxima etapa elimine recálculos paralelos entre console e planilha por meio de camada única de saída canônica.

## Onde encontrar o histórico rebaixado
- `relatorios/historico/limpeza_repositorio/`
- `relatorios/historico/contratos_intermediarios/`
- `relatorios/historico/validacoes_diarias/`
- `relatorios/historico/reorganizacao_local_switching/`
- `relatorios/historico/objetivo_final/`
- `relatorios/historico/documentacao_baseline/`
- `relatorios/historico/auditorias_especificas/`
- `relatorios/historico/baselines/`
- `relatorios/historico/estruturas/`
- `saidas/historico/`
- `scripts/historico_raiz/`

## Canonização de scripts e saídas
- use `scripts/diagnostico/` para inspeções, diagnósticos e checagem de release;
- use `scripts/operacional/` para geração de saídas operacionais;
- use `scripts/auditoria/` para auditorias formais;
- trate `scripts/historico_raiz/` como acervo histórico sem primazia operacional;
- trate wrappers da raiz de `scripts/` apenas como compatibilidade;
- trate `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- trate `saidas/diagnostico/` como apoio diagnóstico ativo;
- trate `saidas/operacional/` como compatibilidade residual de caminho;
- trate `saidas/historico/` como acervo histórico de artefatos, sem competição com os caminhos ativos.

## Próxima frente
Criar uma camada única de saída canônica para impedir divergência entre console, `.xlsx`, JSON/CSV e markdown. A frente de aportes/recebidos futuros em carteira deve ficar para depois dessa unificação.

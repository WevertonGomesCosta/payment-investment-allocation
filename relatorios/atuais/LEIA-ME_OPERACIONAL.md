# LEIA-ME operacional — V186

## Baseline vigente da camada documental e de navegação
- Pacote operacional atual: **V186**
- Contrato mestre vigente: **CONTRATO_OPERACIONAL_PROJETO.md**
- Modelo oficial vigente: **MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md**
- Baseline contratual/metodológica preservada: **V183/V182**

## Leitura obrigatória inicial

### Núcleo normativo vigente
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`

### Regra de leitura desta etapa
1. Interpretar o projeto pela V183 como contrato mestre vigente e pela V182 como modelo oficial vigente.
2. Tratar a V186 apenas como normalização final dos caminhos ativos de saída e do tooling diagnóstico/release.
3. Não usar documentos históricos como base normativa principal para novas implementações.
4. Exigir auditabilidade por lote, fonte, conta, pacote e destino nas saídas oficiais.
5. Tratar `saidas/oficial/` como caminho canônico de artefatos oficiais ativos.

## Onde encontrar o histórico rebaixado
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

## Referência normativa vigente
- Contrato mestre vigente: `CONTRATO_OPERACIONAL_PROJETO.md`
- Modelo metodológico vinculante: `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- Pacote operacional atual: V186

## Canonização de scripts e saídas
- use `scripts/diagnostico/` para inspeções, diagnósticos e checagem de release;
- use `scripts/operacional/` para geração de saídas operacionais;
- use `scripts/auditoria/` para auditorias formais;
- trate `scripts/historico_raiz/` como acervo histórico sem primazia operacional;
- trate `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- trate `saidas/diagnostico/` como apoio diagnóstico ativo;
- trate `saidas/operacional/` como compatibilidade residual de caminho;
- trate `saidas/historico/` como acervo histórico de artefatos, sem competição com os caminhos ativos.

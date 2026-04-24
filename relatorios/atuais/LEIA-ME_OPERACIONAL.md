# LEIA-ME operacional — V189

## Baseline vigente da camada documental e de navegação
- Pacote operacional atual: **V189**
- Contrato mestre vigente: **CONTRATO_OPERACIONAL_PROJETO.md**
- Modelo oficial vigente: **MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md**
- Baseline contratual/metodológica preservada: **V183/V182**

## Leitura obrigatória inicial

### Núcleo normativo vigente
- `CONTRATO_OPERACIONAL_PROJETO.md`
- `MODELO_MATEMATICO_ESTATISTICO_FINANCEIRO_OFICIAL_V182.md`
- `BACKLOG_CONTRATUAL_FASES_FUTURAS.md`
- `ESPECIFICACAO_SAIDA_OFICIAL.md`

### Regra de leitura desta etapa
1. Interpretar o projeto pela V183 como contrato mestre vigente e pela V182 como modelo oficial vigente.
2. Tratar a V189 como baseline de saída oficial observável, sem reabrir contrato, modelo ou núcleo econômico.
3. Não usar documentos históricos como base normativa principal para novas implementações.
4. Exigir auditabilidade por lote, fonte, conta, pacote e destino nas saídas oficiais.
5. Tratar `saidas/oficial/` como caminho canônico de artefatos oficiais ativos.
6. Tratar `ESPECIFICACAO_SAIDA_OFICIAL.md` como referência operacional da camada observável antes da derivação de `resolver_dia(t, E_t)`.

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
- Pacote operacional atual: V188

## Canonização de scripts e saídas
- use `scripts/diagnostico/` para inspeções, diagnósticos e checagem de release;
- use `scripts/operacional/` para geração de saídas operacionais;
- use `scripts/auditoria/` para auditorias formais;
- trate `scripts/historico_raiz/` como acervo histórico sem primazia operacional;
- trate `saidas/oficial/` como caminho canônico de artefatos oficiais ativos;
- trate `saidas/diagnostico/` como apoio diagnóstico ativo;
- trate `saidas/operacional/` como compatibilidade residual de caminho;
- trate `saidas/historico/` como acervo histórico de artefatos, sem competição com os caminhos ativos.


## Observação sobre a raiz de `scripts/`
Na raiz de `scripts/` permanecem apenas wrappers mínimos de compatibilidade e arquivos de suporte compartilhado. A leitura operacional canônica continua sendo: `scripts/diagnostico/`, `scripts/operacional/` e `scripts/auditoria/`.


## Observação operacional vigente

A saída oficial `.xlsx` deve manter as abas canônicas `Extrato Passado`, `Extrato Futuro`, `Switching`, `Carteira` e `Situação Atual`, além das abas do ranking estabilizado `Ranking_Completo`, `Top30`, `Destinos_Switch`, `Resumo` e `Validacao`, quando geradas pela trilha operacional oficial.
